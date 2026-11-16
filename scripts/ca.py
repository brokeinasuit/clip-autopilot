#!/usr/bin/env python3
"""Launcher: runs the engine inside ~/.clip-autopilot/venv, from any Python, on macOS or Windows.

    python3 ca.py <command> ...     (Windows: py ca.py ... or python ca.py ...)
"""
import os, subprocess, sys
from pathlib import Path

HOME = Path(os.environ.get("CLIP_AUTOPILOT_HOME", Path.home() / ".clip-autopilot"))
VENV = HOME / "venv"
ENGINE = Path(__file__).resolve().parent.parent / "engine"
VPY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def main():
    if not VPY.exists():
        print("Clip Autopilot is not set up yet: run /clip-setup (or: python3 scripts/setup.py).")
        return 2
    if Path(sys.prefix).resolve() != VENV.resolve():
        env = dict(os.environ, PYTHONPATH=str(ENGINE), PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        return subprocess.run([str(VPY), str(Path(__file__).resolve()), *sys.argv[1:]], env=env).returncode
    sys.path.insert(0, str(ENGINE))
    from clipauto.cli import main as cli
    cli(sys.argv[1:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
