---
name: clip-fix
description: Diagnose and fix Clip Autopilot problems on macOS or Windows - setup failing, "not set up", Python missing, pip errors, ffmpeg errors, downloads failing, Whisper slow or crashing, clips with bad framing or no audio, out of disk space. Use when any clip-* command errors, the user says "it doesn't work", "error", "broken", "help", "fix", or pastes an error message from Clip Autopilot.
---

# Clip Autopilot: fix

Work through this calmly. Run things yourself, explain in plain words, fix what you can, and only ask the user to do something you cannot (installing Python, freeing disk space).

## 1. Health check first
```
PY "${CLAUDE_PLUGIN_ROOT}/scripts/ca.py" doctor
```
(`PY` = `python3` on macOS, `py` or `python` on Windows.) "Not set up yet" -> run the clip-setup skill. Otherwise fix each `FIX` line with the table below, then run doctor again until everything is OK.

## 2. Common problems

| Symptom | Fix |
|---|---|
| `python3` / `py` / `python` not found | Install Python 3.9+ from python.org. Windows: tick "Add python.exe to PATH", then reopen Claude Code. |
| Windows: `python` opens the Microsoft Store | Use `py` instead, or install from python.org and turn off Settings > Apps > App execution aliases > python.exe. |
| pip install fails (SSL, proxy) | Retry once. Corporate/school network: try another network (phone hotspot). |
| pip fails building `av` / `ctranslate2` | Python version too new for prebuilt packages: install Python 3.11 or 3.12 from python.org, delete `~/.clip-autopilot/venv`, run setup again. |
| ffmpeg FIX / "no libx264" | Run setup again (installs imageio-ffmpeg). macOS with Homebrew: `brew install ffmpeg` also works. |
| Download fails: "Sign in to confirm you're not a bot" / 403 | Update the downloader: `PY "${CLAUDE_PLUGIN_ROOT}/scripts/setup.py"` (upgrades yt-dlp). Still failing: download the video in the browser (if the campaign allows it) and give the file path instead. |
| Google Drive / Dropbox link | Download the file in the browser and use the local path. |
| Whisper very slow | Normal on older laptops (CPU only). Use `--model base.en` for speed, or a YouTube link with captions. Close other heavy apps. |
| Whisper crash / out of memory | Use `--model base.en`; cut long sources into parts first. |
| Clip has no sound / "Stream map '0:a' matches no streams" | The source has no audio track. Check the source file plays with sound. |
| Speaker cut off at the side | Run `preview`, set a better `crop_x` (0 left ... 1 right) in moments.json, cut again with `--ids`. |
| Captions out of sync | YouTube auto-captions can drift: run find again with `--whisper`. |
| Disk full | Run `ca.py clean <work-id>` on finished work, empty the trash. Sources are 0.5-3 GB each. |
| Permission denied writing files | Open Claude Code in a folder you own (e.g. Documents/Clipping), not a system folder. |

## 3. Still stuck
Collect: the doctor output (last JSON line), the exact command and the last 20 lines of the error. Tell the user to post them in the Broke In A Suit Discord #help channel (link in the README), and never paste passwords or tokens there.
