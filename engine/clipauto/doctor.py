"""Health check. Prints one line per check (OK / FIX) and a JSON summary on the last line.
/clip-setup and /clip-fix read it. Exit code 0 = all good."""
import json, os, platform, shutil, sys

from .env import FONT, HOME, VERSION, run


def check():
    res = []

    def add(name, ok, detail, fix=""):
        res.append({"check": name, "ok": bool(ok), "detail": detail, "fix": fix})

    add("python", sys.version_info >= (3, 9), platform.python_version(), "Install Python 3.9 or newer")
    add("os", True, f"{platform.system()} {platform.release()} {platform.machine()}")
    add("venv", str(HOME) in sys.prefix, sys.prefix, "Run scripts/setup.py (or /clip-setup)")
    for mod, pip in (("yt_dlp", "yt-dlp"), ("faster_whisper", "faster-whisper"), ("PIL", "pillow"),
                     ("imageio_ffmpeg", "imageio-ffmpeg")):
        try:
            m = __import__(mod)
            add(pip, True, getattr(m, "__version__", "installed"))
        except Exception as e:
            add(pip, False, str(e)[:120], f"Run scripts/setup.py again (installs {pip})")
    exe = shutil.which("ffmpeg")
    if not exe:
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            exe = None
    ok = False
    detail = "not found"
    if exe:
        r = run([exe, "-hide_banner", "-encoders"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        ok = "libx264" in r.stdout
        detail = exe + ("" if ok else " (no libx264 encoder)")
    add("ffmpeg", ok, detail, "Run scripts/setup.py again; it installs a working ffmpeg")
    add("font", FONT.exists(), FONT.name, "Reinstall the plugin (font file missing)")
    try:
        free = shutil.disk_usage(os.getcwd()).free / 1e9
        add("disk", free > 3, f"{free:.1f} GB free here", "Free up disk space: a source video + clips can take 2-3 GB")
    except Exception:
        pass
    return res


def main():
    res = check()
    for r in res:
        print(f"{'OK ' if r['ok'] else 'FIX'}  {r['check']:15s} {r['detail']}" + ("" if r["ok"] else f"\n     -> {r['fix']}"))
    print(json.dumps({"version": VERSION, "ok": all(r["ok"] for r in res), "checks": res}))
    return 0 if all(r["ok"] for r in res) else 1
