"""Word-timed transcript: words.json = [{"w": "word", "s": 1.23, "e": 1.56}, ...] in seconds.

YouTube auto-captions first (free, instant). If there are none, or --whisper is forced, local
faster-whisper with word timestamps (free, runs on your own computer, Mac or Windows).
"""
import json, os, re
from pathlib import Path

DEFAULT_MODEL = os.environ.get("CLIP_WHISPER_MODEL", "small.en")


def from_json3(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    words = []
    for ev in data.get("events", []):
        segs = ev.get("segs")
        if not segs or ev.get("aAppend"):
            continue
        t0, dur = ev.get("tStartMs", 0), ev.get("dDurationMs", 0)
        for seg in segs:
            txt = seg.get("utf8", "").strip()
            if txt:
                words.append({"w": txt, "s": (t0 + seg.get("tOffsetMs", 0)) / 1000, "e": (t0 + dur) / 1000})
    words.sort(key=lambda x: x["s"])
    for a, b in zip(words, words[1:]):  # a word ends where the next starts, capped so a pause stays a pause
        a["e"] = round(min(a["e"], b["s"], a["s"] + 1.2), 3)
    if words:
        words[-1]["e"] = round(min(words[-1]["e"], words[-1]["s"] + 1.2), 3)
    return [w for w in words if not re.fullmatch(r"\[.*\]", w["w"])]  # [Music], [Applause]


def load_audio(media, sr=16000):
    """Decode with ffmpeg to 16 kHz mono float32. Avoids PyAV, whose API changes break faster-whisper's own decoder."""
    import numpy as np
    from .env import ffmpeg, run
    r = run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-i", str(media), "-vn", "-ac", "1", "-ar", str(sr),
             "-f", "s16le", "-"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"could not read the audio of {media}: {r.stderr.decode(errors='replace')[-400:]}")
    return np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768.0


def from_whisper(media, model=DEFAULT_MODEL):
    from faster_whisper import WhisperModel
    print(f"transcribing with whisper ({model}) on this computer, first run downloads the model...")
    wm = WhisperModel(model, device="auto", compute_type="int8", cpu_threads=max(1, (os.cpu_count() or 4) - 1))
    segments, _ = wm.transcribe(load_audio(media), word_timestamps=True, vad_filter=True,
                                language="en" if model.endswith(".en") else None)
    words = []
    for seg in segments:
        for w in seg.words or []:
            txt = w.word.strip()
            if txt:
                words.append({"w": txt, "s": round(w.start, 3), "e": round(w.end, 3)})
    return words


def merge_numbers(words):
    """Glue "$10" ",000" and "1" "%" and hyphen splits back together."""
    out = []
    for w in words:
        if out and ((re.match(r"^[,.%]", w["w"]) and re.search(r"\d$", out[-1]["w"])) or w["w"].startswith("-")):
            out[-1] = {"w": out[-1]["w"] + w["w"], "s": out[-1]["s"], "e": w["e"]}
        else:
            out.append(dict(w))
    return out


def build(wdir, media, force_whisper=False, model=DEFAULT_MODEL):
    wdir = Path(wdir)
    subs = sorted(wdir.glob("*.json3"))
    words, source = [], None
    if subs and not force_whisper:
        words, source = from_json3(subs[0]), "youtube-captions"
    if len(words) < 50:
        words, source = from_whisper(media, model), "whisper"
    words = merge_numbers(words)
    (wdir / "words.json").write_text(json.dumps(words), encoding="utf-8")
    return words, source
