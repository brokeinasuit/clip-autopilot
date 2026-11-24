"""Paths and tools. Works the same on macOS and Windows.

Workspace = the folder the user runs Claude Code in (or --root). Layout inside it:
  campaigns/<campaign>/RULES.md   the brief, turned into a checklist by /clip-rules
  work/<source-id>/               source video, words.json, transcript.txt, moments.json
  clips/<campaign>/<date>-<slug>/ finished 9:16 clips
"""
import os, re, shutil, subprocess, sys
from pathlib import Path

VERSION = "0.1.0"
HOME = Path(os.environ.get("CLIP_AUTOPILOT_HOME", Path.home() / ".clip-autopilot"))
PKG = Path(__file__).resolve().parent
FONT = PKG / "fonts" / "Anton.ttf"

# Shown at the end of setup and in the README. Filled in at launch.
PRO_URL = "https://brokeinasuitassets.gumroad.com/l/clip-autopilot-pro"
FREE_URL = "https://brokeinasuitassets.gumroad.com/l/clip-autopilot"


def root(arg=None):
    return Path(arg or os.environ.get("CLIP_ROOT") or os.getcwd()).resolve()


def die(msg, code=1):
    print(f"ERROR: {msg}")
    sys.exit(code)


def ffmpeg():
    """System ffmpeg if there is one, else the static build that ships with imageio-ffmpeg."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        die("ffmpeg not found. Run /clip-setup (or /clip-fix).")


def run(cmd, **kw):
    """subprocess.run that never opens a console window on Windows."""
    if os.name == "nt":
        kw.setdefault("creationflags", 0x08000000)  # CREATE_NO_WINDOW
    return subprocess.run(cmd, **kw)


def duration(path):
    """Media length in seconds, read from ffmpeg's banner (no ffprobe needed)."""
    err = run([ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True,
              encoding="utf-8", errors="replace").stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", err)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0


def video_size(path):
    err = run([ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True,
              encoding="utf-8", errors="replace").stderr
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", err)
    return (int(m.group(1)), int(m.group(2))) if m else (1920, 1080)


def fmt(t):
    return f"{int(t // 60):02d}:{t % 60:05.2f}"


STOP = {"the", "a", "an", "and", "or", "but", "so", "to", "of", "in", "on", "for", "is", "it",
        "you", "your", "i", "my", "we", "that", "this", "with", "are", "be", "was", "if", "just"}


def slugify(text, max_words=6):
    words = [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP]
    return "-".join(words[:max_words]) or "clip"


def rules(ws, campaign):
    """key: value block between the --- lines at the top of RULES.md."""
    path = ws / "campaigns" / campaign / "RULES.md"
    out = {}
    if path.exists():
        m = re.match(r"---\r?\n(.*?)\r?\n---", path.read_text(encoding="utf-8"), re.S)
        for line in (m.group(1).splitlines() if m else []):
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
    return out
