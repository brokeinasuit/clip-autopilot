---
name: clip-find
description: Find the best clip-worthy moments in a long video (podcast, stream, interview, trailer) for a clipping campaign - downloads the video or takes a local file, makes a word-timed transcript (YouTube captions or local Whisper), ranks candidate moments by hook strength, length and dead air, then Claude fixes start/end points and writes the on-screen hook for each. Use when the user gives a video link or file to clip, says "find clips", "find the best moments", "what should I clip from this", or after clip-rules is done.
---

# Clip Autopilot: find moments

> `PY` below = the Python command that worked in clip-setup (`python3` on macOS; `py`, else `python`, on Windows). `${CLAUDE_PLUGIN_ROOT}` is this plugin's folder; if it comes out empty, use the folder that contains `scripts/ca.py` under `~/.claude/plugins`. On Windows PowerShell, start the command with `& ` when the first word is quoted.

## Steps

1. **Campaign check.** The video must belong to a campaign folder (`campaigns/<slug>/RULES.md`). If there is none, run the clip-rules skill first (or, if the user has no campaign, create one called `practice`). Read RULES.md: length window, allowed sources, banned content.

2. **Run the finder** (`PY` = the Python command from clip-setup):
   ```
   PY "${CLAUDE_PLUGIN_ROOT}/scripts/ca.py" find <campaign-slug> "<url-or-file>" --n 10
   ```
   - YouTube links with captions take seconds. Without captions (or local files) Whisper runs on this computer: about 1-3x the video's length on a normal laptop, the first run also downloads the model. Tell the user it is working, do not abort it.
   - Time: a 1-hour podcast can take 20-60 minutes with the default model. For a first try use a short video or `--model base.en` (faster, a few more mistakes). `tiny.en` is for tests only: its captions contain mistakes that get burned into the clip.
   - `--whisper` forces Whisper (use it when the YouTube captions are bad). `--model base.en` is faster and a bit less accurate; `--model small.en` is the default.
   - The last lines print the work id (`work/<id>/`) and the ranked moments.

3. **Judge the moments yourself. This is the important part.** Read `work/<id>/moments.json` and `work/<id>/transcript.txt`. For each moment:
   - Start on a line that makes a scroller stop: a bold claim, a number, a question, conflict. Move `start` earlier or later to the beginning of that sentence (use transcript times).
   - End on the payoff (the punchline, the answer, the number), not mid-thought. Move `end`.
   - Keep the length inside the campaign's `min_length_s`-`max_length_s`.
   - Drop weak ones: set `"keep": false` (filler, inside jokes, needs context, breaks a campaign rule).
   - If RULES.md bans on-screen text, overlays or edits, leave `"hook"` empty (`""`) and tell the user.
   - Write `"hook"`: the on-screen text for the first 3 seconds, max 8 words, in the creator's meaning, no clickbait the campaign bans, no quotes or emojis.
   - Write `"slug"`: 3-6 lowercase words with hyphens, from the hook (becomes the file name).
   - Leave `crop_x` at 0.5 unless step 4 says otherwise.
   Save moments.json (valid JSON, same fields).

4. **Framing (do this for EVERY wide 16:9 source; the default centre crop often cuts people or on-screen text off):**
   ```
   PY "${CLAUDE_PLUGIN_ROOT}/scripts/ca.py" preview <work-id>
   ```
   Open and look at each `work/<id>/preview/mNN.jpg`. Set `crop_x` per moment: 0 = keep the left edge, 0.5 = centre, 1 = right edge, so the speaker's face sits in the middle of a 9:16 slice.

5. **Show the user a short table**: id, time, length, hook, one-line reason it works. Ask which to cut, or say "I'll cut all kept ones" and go to clip-cut.

## Tips
- 5-8 strong clips beat 10 average ones. Campaigns pay on views; weak clips also hurt the account.
- Never change what the creator said. The hook is your words; the clip is theirs.
