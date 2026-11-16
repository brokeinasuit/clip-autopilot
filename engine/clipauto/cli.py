"""Clip Autopilot Starter engine. Claude runs it through scripts/ca.py; you normally never type these.

  doctor                                  check everything is installed (used by /clip-setup and /clip-fix)
  new <campaign>                          campaigns/<campaign>/RULES.md from the template
  find <campaign> <url|file> [--whisper] [--n 10] [--model small.en]
                                          download, transcript, top moments -> work/<id>/moments.json
  preview <work-id>                       one frame per moment in work/<id>/preview/ (to set crop_x)
  cut <work-id> [--ids 1,4]               plain 9:16 clips with captions -> clips/<campaign>/
  list                                    work folders and their state
  clean <work-id>                         delete the source video (keeps transcript + moments)

Workspace = current folder, or --root <folder>.
"""
import datetime, json, re, shutil, sys
from pathlib import Path

from . import moments as M
from . import transcript
from .env import PKG, VERSION, die, ffmpeg, fmt, root, rules, run


def cmd_new(ws, campaign):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", campaign):
        die("campaign name: lowercase letters, numbers and hyphens, e.g. caleb-hammer")
    dest = ws / "campaigns" / campaign
    if dest.exists():
        print(f"exists: {dest}")
        return
    dest.mkdir(parents=True)
    shutil.copy(PKG.parent.parent / "templates" / "RULES.md", dest / "RULES.md")
    (dest / "sources.txt").write_text("# one source URL or file path per line\n", encoding="utf-8")
    print(f"created {dest.relative_to(ws)}: fill RULES.md from the campaign page (/clip-rules does this)")


def ytdlp(*args):
    return [sys.executable, "-m", "yt_dlp", "--ffmpeg-location", ffmpeg(), *args]


def cmd_find(ws, campaign, src, force_whisper, n, model):
    if not (ws / "campaigns" / campaign).is_dir():
        die(f"no campaign '{campaign}': run  new {campaign}  (or /clip-rules) first")
    r = rules(ws, campaign)
    lo = float(r.get("min_length_s") or 15)
    hi = float(r.get("max_length_s") or 60)
    p = Path(src).expanduser()
    if p.exists():
        wid = re.sub(r"[^a-z0-9]+", "-", p.stem.lower()).strip("-") or "source"
        wdir = ws / "work" / wid
        wdir.mkdir(parents=True, exist_ok=True)
        media = wdir / ("source" + p.suffix.lower())
        if not media.exists():
            shutil.copy(p, media)
        meta = {"title": p.name, "uploader": "", "url": str(p)}
    else:
        res = run(ytdlp("-J", "--no-playlist", src), capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode != 0:
            die(f"could not read that link:\n{res.stderr[-800:]}")
        info = json.loads(res.stdout)
        wid = re.sub(r"[^A-Za-z0-9_-]+", "-", info["id"])
        wdir = ws / "work" / wid
        wdir.mkdir(parents=True, exist_ok=True)
        print(f"downloading: {info.get('title')}")
        run(ytdlp("--no-playlist", "--no-progress", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b",
                  "--merge-output-format", "mp4", "--write-auto-subs", "--sub-langs", "en", "--sub-format", "json3",
                  "--ignore-errors", "-o", str(wdir / "source.%(ext)s"), src))
        media = wdir / "source.mp4"
        if not media.exists():
            die(f"download failed: {src}")
        meta = {"title": info.get("title"), "uploader": info.get("uploader"), "url": src,
                "duration": info.get("duration")}
    meta.update({"campaign": campaign, "id": wid, "fetched": datetime.date.today().isoformat()})
    (wdir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    words, how = transcript.build(wdir, media, force_whisper, model)
    found = M.run(wdir, n, lo, hi)
    print(f"\n{wid}: {len(words)} words ({how}), {len(found)} moments -> work/{wid}/moments.json")
    for m in found:
        print(f"{m['id']:2d}  {fmt(m['start'])}-{fmt(m['end'])}  score {m['score']:5.1f}  {m['opening'][:70]}")


def cmd_preview(ws, wid):
    from .cut import media_in
    wdir = ws / "work" / wid
    src = media_in(wdir) or die("source already deleted")
    pdir = wdir / "preview"
    pdir.mkdir(exist_ok=True)
    for m in json.loads((wdir / "moments.json").read_text(encoding="utf-8")):
        t = m["start"] + min(3, (m["end"] - m["start"]) / 2)
        run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1",
             "-vf", "scale=960:-2", str(pdir / f"m{m['id']:02d}.jpg")], check=True)
    print(f"frames in work/{wid}/preview/")


def cmd_list(ws):
    from .cut import media_in
    base = ws / "work"
    for wdir in sorted(base.iterdir()) if base.is_dir() else []:
        if wdir.is_dir():
            mp = wdir / "meta.json"
            meta = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
            print(f"{wdir.name:20s} {meta.get('campaign', '?'):20s} source={'yes' if media_in(wdir) else 'deleted'}"
                  f"  {meta.get('title', '')}")


def cmd_clean(ws, wid):
    from .cut import media_in
    src = media_in(ws / "work" / wid)
    if src:
        src.unlink()
        print(f"deleted {src.relative_to(ws)}")


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)

    def flag(f):
        return f in a and (a.remove(f) or True)

    def opt(f, default=None):
        if f in a:
            i = a.index(f)
            v = a[i + 1]
            del a[i:i + 2]
            return v
        return default

    if flag("--version"):
        print(VERSION)
        return
    ws = root(opt("--root"))
    whisper = flag("--whisper")
    n = int(opt("--n", 10))
    model = opt("--model", transcript.DEFAULT_MODEL)
    ids = [int(x) for x in opt("--ids", "").split(",") if x]
    if not a:
        die(__doc__)
    cmd = a[0]
    if cmd == "doctor":
        from .doctor import main as doctor
        sys.exit(doctor())
    elif cmd == "new" and len(a) == 2:
        cmd_new(ws, a[1])
    elif cmd == "find" and len(a) == 3:
        cmd_find(ws, a[1], a[2], whisper, n, model)
    elif cmd == "preview" and len(a) == 2:
        cmd_preview(ws, a[1])
    elif cmd == "cut" and len(a) == 2:
        from .cut import run_cut
        run_cut(ws, a[1], ids)
    elif cmd == "list":
        cmd_list(ws)
    elif cmd == "clean" and len(a) == 2:
        cmd_clean(ws, a[1])
    else:
        die(__doc__)


if __name__ == "__main__":
    main()
