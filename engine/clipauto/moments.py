"""Transcript -> ranked candidate clips (moments.json) + transcript.txt.

First pass only. Claude then reads moments.json and transcript.txt, fixes the start and end so each
clip starts on a strong line and ends on a payoff, writes the on-screen hook and drops weak ones.
Scoring: the opening line's hook score, a length that fits the campaign, and dead air (kills retention).
"""
import json
from pathlib import Path

from . import hookscore
from .env import fmt

GAP_SENTENCE = 0.55  # a pause this long counts as a sentence break when captions have no punctuation


def sentences(words):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["s"] - w["e"]) if nxt else 9
        if w["w"][-1:] in ".?!" or gap >= GAP_SENTENCE or not nxt:
            out.append({"s": cur[0]["s"], "e": cur[-1]["e"], "text": " ".join(x["w"] for x in cur),
                        "gap_after": round(gap, 2)})
            cur = []
    return out


def write_transcript(sents, path):
    Path(path).write_text("".join(f"[{fmt(s['s'])} - {fmt(s['e'])}] {s['text']}\n" for s in sents), encoding="utf-8")


def length_score(d, lo, hi):
    if lo <= d <= hi:
        return 100
    return max(0, 100 - abs(d - (lo if d < lo else hi)) * 6)


def candidates(sents, min_len, max_len, sweet):
    cands = []
    for i in range(len(sents)):
        for j in range(i, len(sents)):
            d = sents[j]["e"] - sents[i]["s"]
            if d > max_len:
                break
            if d < min_len:
                continue
            opening = " ".join(" ".join(s["text"] for s in sents[i:i + 2]).split()[:24])
            _, hook, _, _ = hookscore.score(opening)
            dead = sum(max(0, s["gap_after"] - 0.8) for s in sents[i:j])
            score = round(0.6 * hook + 0.4 * length_score(d, *sweet) - dead * 8, 1)
            cands.append({"start": round(max(0, sents[i]["s"] - 0.15), 2), "end": round(sents[j]["e"] + 0.25, 2),
                          "score": score, "opening": opening,
                          "text": " ".join(s["text"] for s in sents[i:j + 1])})
    return cands


def pick(cands, n):
    chosen = []
    for c in sorted(cands, key=lambda c: -c["score"]):
        if all(c["end"] <= k["start"] or c["start"] >= k["end"] for k in chosen):
            chosen.append(c)
        if len(chosen) >= n:
            break
    chosen.sort(key=lambda c: c["start"])
    for k, c in enumerate(chosen, 1):
        c.update({"id": k, "keep": True, "slug": "", "hook": "", "crop_x": 0.5})
    return chosen


def run(wdir, n=10, min_len=15, max_len=60):
    wdir = Path(wdir)
    words = json.loads((wdir / "words.json").read_text(encoding="utf-8"))
    sents = sentences(words)
    write_transcript(sents, wdir / "transcript.txt")
    span = max_len - min_len
    sweet = (min_len + span * 0.15, min_len + span * 0.6)
    moments = pick(candidates(sents, min_len, max_len, sweet), n)
    (wdir / "moments.json").write_text(json.dumps(moments, indent=2), encoding="utf-8")
    return moments
