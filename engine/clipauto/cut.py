"""Plain 9:16 cut: crop at crop_x, bold captions word groups, hook text on top for the first seconds,
loudness to -14 LUFS / true peak -1.5 dB. Captions are drawn with Pillow (works with any ffmpeg build).

The styled looks, hook rewrites, QA gate, SFX pass and post packs are in Clip Autopilot Pro.
"""
import datetime, json, re, shutil, tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .env import FONT, die, duration, ffmpeg, run, slugify, video_size

W, H = 1080, 1920
CAP_Y = 1240        # caption centre line (lower middle, clear of the platform buttons)
HOOK_Y = 300        # hook block top
HOOK_SECONDS = 3.0
MAX_GROUP = 3       # words per caption
QUOTES = r"[\"“”‘’]"


def _font(size):
    return ImageFont.truetype(str(FONT), size)


def _text_png(text, path, size, max_w=960, stroke=8):
    font = _font(size)
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if font.getlength(trial) + stroke * 2 > max_w and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines.append(cur)
    lh = int(size * 1.12)
    w = int(max(font.getlength(l) for l in lines)) + stroke * 2 + 8
    h = lh * len(lines) + stroke * 2 + 8
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        x = (w - font.getlength(line)) / 2
        d.text((x, stroke + 4 + i * lh), line, font=font, fill=(255, 255, 255, 255),
               stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    img.save(path)
    return w, h


def caption_groups(words, start, end):
    """Words inside the clip -> groups of up to 3, broken at punctuation and pauses. Times are clip-relative."""
    inside = [w for w in words if w["s"] >= start - 0.05 and w["e"] <= end + 0.3]
    groups, cur = [], []
    for i, w in enumerate(inside):
        cur.append(w)
        nxt = inside[i + 1] if i + 1 < len(inside) else None
        brk = (len(cur) >= MAX_GROUP or w["w"][-1:] in ".?!," or not nxt or nxt["s"] - w["e"] > 0.3)
        if brk:
            text = re.sub(QUOTES, "", " ".join(x["w"] for x in cur)).upper().strip()
            a = max(0.0, cur[0]["s"] - start)
            b = (nxt["s"] - start) if nxt and nxt["s"] - cur[-1]["e"] < 0.6 else cur[-1]["e"] - start + 0.15
            if text:
                groups.append((text, round(a, 3), round(min(b, end - start), 3)))
            cur = []
    return groups


def crop_filter(src, crop_x):
    iw, ih = video_size(src)
    if iw / ih > W / H:  # wider than 9:16: crop the sides
        cw = int(ih * W / H) // 2 * 2
        x = int((iw - cw) * min(1, max(0, crop_x)))
        return f"crop={cw}:{ih}:{x}:0,scale={W}:{H}:flags=lanczos,setsar=1,fps=30"
    ch = int(iw * H / W) // 2 * 2
    return f"crop={iw}:{min(ch, ih)}:0:(ih-{min(ch, ih)})/2,scale={W}:{H}:flags=lanczos,setsar=1,fps=30"


def cut_one(src, words, m, out):
    start, end = float(m["start"]), float(m["end"])
    dur = end - start
    tmp = Path(tempfile.mkdtemp(prefix="clipauto-"))
    try:
        layers = []  # (png, x, y, a, b)
        hook = re.sub(r"[*^]|" + QUOTES, "", m.get("hook") or "").strip()
        if hook:
            p = tmp / "hook.png"
            w, h = _text_png(hook.upper(), p, 78)
            layers.append((p, (W - w) // 2, HOOK_Y, 0, min(HOOK_SECONDS, dur)))
        for i, (text, a, b) in enumerate(caption_groups(words, start, end)):
            p = tmp / f"c{i:03d}.png"
            w, h = _text_png(text, p, 96)
            layers.append((p, (W - w) // 2, CAP_Y - h // 2, a, b))
        graph = [f"[0:v]{crop_filter(src, float(m.get('crop_x', 0.5)))}[v0]"]
        for k, (_, x, y, a, b) in enumerate(layers, 1):
            graph.append(f"[v{k - 1}][{k}:v]overlay=x={x}:y={y}:enable='between(t,{a},{b})'[v{k}]")
        graph.append(f"[v{len(layers)}]null[v]")
        graph.append("[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
        script = tmp / "graph.txt"
        script.write_text(";\n".join(graph), encoding="utf-8")
        cmd = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start}", "-t", f"{dur}", "-i", str(src)]
        for p, *_ in layers:
            cmd += ["-i", str(p)]
        cmd += ["-filter_complex_script", str(script), "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{dur}", str(out)]
        r = run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            die(f"ffmpeg failed on {out.name}:\n{r.stderr[-1500:]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def media_in(wdir):
    for f in sorted(Path(wdir).iterdir()):
        if f.name.startswith("source.") and f.suffix not in (".json3", ".vtt", ".part"):
            return f
    return None


def run_cut(ws, wid, ids=None):
    wdir = ws / "work" / wid
    if not wdir.is_dir():
        die(f"no work folder work/{wid}: run  find  first")
    meta = json.loads((wdir / "meta.json").read_text(encoding="utf-8"))
    src = media_in(wdir) or die("the source video is gone: run  find  again")
    words = json.loads((wdir / "words.json").read_text(encoding="utf-8"))
    moments = [m for m in json.loads((wdir / "moments.json").read_text(encoding="utf-8")) if m.get("keep")]
    if ids:
        moments = [m for m in moments if m["id"] in ids]
    from .env import rules
    r = rules(ws, meta["campaign"])
    lo = float(r.get("min_length_s") or 0)
    hi = float(r.get("max_length_s") or 1e9)
    today = datetime.date.today().isoformat()
    done = []
    for m in moments:
        slug = m.get("slug") or slugify(m.get("hook") or m["opening"])
        outdir = ws / "clips" / meta["campaign"] / f"{today}-{slug}"
        outdir.mkdir(parents=True, exist_ok=True)
        out = cut_one(src, words, m, outdir / f"{slug}.mp4")
        d = duration(out)
        warn = ""
        if not lo <= d <= hi:
            warn = f"  WARNING: {d:.1f} s is outside the campaign's {lo:g}-{hi:g} s"
        (outdir / f"{slug}.txt").write_text(
            f"{slug}.mp4  ({d:.1f} s)\nCampaign: {meta['campaign']}\nSource: {meta.get('title')}  {meta.get('url')}\n"
            f"Clip from {m['start']} s to {m['end']} s\nHook on screen: {m.get('hook') or '(none)'}\n\n"
            f"Before posting, check RULES.md: required tag ({r.get('required_tag') or 'none listed'}), "
            f"caption rules, and submit the post link on the campaign page.\n", encoding="utf-8")
        print(f"cut {out.relative_to(ws)}  {d:.1f} s{warn}")
        done.append(out)
    return done
