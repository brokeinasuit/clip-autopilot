#!/usr/bin/env python3
"""One-time setup for Clip Autopilot (macOS and Windows).

Creates a private Python environment in ~/.clip-autopilot/venv and installs what the engine needs:
yt-dlp (downloads), faster-whisper (transcripts on your own computer), Pillow (captions) and
imageio-ffmpeg (a working ffmpeg, so you don't have to install one). Safe to run again: it only
adds what is missing. Nothing is sent anywhere except the normal package downloads from PyPI.

    python3 setup.py          (Windows: py setup.py  or  python setup.py)
"""
import os, subprocess, sys, venv
from pathlib import Path

HOME = Path(os.environ.get("CLIP_AUTOPILOT_HOME", Path.home() / ".clip-autopilot"))
VENV = HOME / "venv"
REQ = ["yt-dlp", "faster-whisper", "pillow", "imageio-ffmpeg", "certifi"]


def vpy():
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def main():
    if sys.version_info < (3, 9):
        print(f"Python {sys.version.split()[0]} is too old: install Python 3.9+ from python.org and run this again.")
        return 1
    HOME.mkdir(parents=True, exist_ok=True)
    if not vpy().exists():
        print(f"creating environment in {VENV} ...")
        venv.EnvBuilder(with_pip=True, clear=False).create(VENV)
    print("installing / updating packages (first time takes a few minutes) ...")
    subprocess.run([str(vpy()), "-m", "pip", "install", "--quiet", "--upgrade", "pip"], check=False)
    r = subprocess.run([str(vpy()), "-m", "pip", "install", "--quiet", "--upgrade", *REQ])
    if r.returncode != 0:
        print("package install failed: see the error above. /clip-fix can help.")
        return 1
    here = Path(__file__).resolve().parent
    return subprocess.run([str(vpy()), str(here / "ca.py"), "doctor"]).returncode


if __name__ == "__main__":
    sys.exit(main())
