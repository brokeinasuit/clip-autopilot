"""End-to-end test: setup -> new -> find -> (Claude's edit, simulated) -> cut -> check the output.
Runs on macOS and Windows (GitHub Actions). Usage: python tests/e2e.py [--skip-setup]
"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CA = REPO / "scripts" / "ca.py"
FIXTURE = REPO / "tests" / "fixtures" / "speech-40s.mp4"


def sh(*args, cwd=None):
    print("$", " ".join(str(a) for a in args), flush=True)
    r = subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print(r.stdout[-3000:], r.stderr[-3000:], sep="\n", flush=True)
    if r.returncode != 0:
        sys.exit(f"FAILED ({r.returncode}): {args}")
    return r.stdout


def main():
    if "--skip-setup" not in sys.argv:
        sh(REPO / "scripts" / "setup.py")
    out = sh(CA, "doctor")
    assert json.loads(out.strip().splitlines()[-1])["ok"], "doctor not ok"
    ws = Path(tempfile.mkdtemp(prefix="clipauto-e2e-"))
    try:
        sh(CA, "new", "e2e", cwd=ws)
        rules = ws / "campaigns" / "e2e" / "RULES.md"
        rules.write_text(rules.read_text(encoding="utf-8").replace("min_length_s: 15", "min_length_s: 8")
                         .replace("max_length_s: 60", "max_length_s: 25"), encoding="utf-8")
        sh(CA, "find", "e2e", FIXTURE, "--n", "3", "--model", "tiny.en", cwd=ws)
        wdirs = [d for d in (ws / "work").iterdir() if d.is_dir()]
        assert len(wdirs) == 1, wdirs
        wdir = wdirs[0]
        words = json.loads((wdir / "words.json").read_text(encoding="utf-8"))
        assert len(words) > 40, f"transcript too short: {len(words)} words"
        moments = json.loads((wdir / "moments.json").read_text(encoding="utf-8"))
        assert moments, "no moments found"
        # what Claude does in clip-find: hook + slug, keep one
        m = moments[0]
        m.update({"hook": "This is the test hook", "slug": "e2e-test-clip"})
        for o in moments[1:]:
            o["keep"] = False
        (wdir / "moments.json").write_text(json.dumps(moments, indent=2), encoding="utf-8")
        sh(CA, "cut", wdir.name, cwd=ws)
        clips = list((ws / "clips" / "e2e").rglob("e2e-test-clip.mp4"))
        assert len(clips) == 1, clips
        info = json.loads(sh(CA, "probe", clips[0]).strip().splitlines()[-1])
        size, dur = (info["width"], info["height"]), info["duration"]
        print(f"clip: {size} {dur:.1f} s")
        assert size == (1080, 1920), size
        assert abs(dur - (m["end"] - m["start"])) < 1.0, (dur, m)
        assert (clips[0].parent / "e2e-test-clip.txt").exists()
        print("E2E PASS")
    finally:
        shutil.rmtree(ws, ignore_errors=True)


if __name__ == "__main__":
    main()
