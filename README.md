# Clip Autopilot (Starter, free)

**Paste a clipping campaign brief. Give it a video. Get the best moments cut into 9:16 clips with captions.**
It does everything up to ready-to-post. You post the clips yourself (about 2 minutes a clip) and submit the links.

Made for paid clipping campaigns (Whop Content Rewards, Clipping.net and similar), runs inside
[Claude Code](https://claude.com/claude-code) on **macOS and Windows**. Everything runs on your own computer:
no accounts to connect, nothing uploaded, it never posts for you.

## Install (2 minutes)

You need Claude Code (a paid Claude plan) and Python 3.9+ ([python.org](https://www.python.org/downloads/),
on Windows tick *Add python.exe to PATH*).

In Claude Code, run:

```
/plugin marketplace add brokeinasuit/clip-autopilot
/plugin install clip-autopilot@brokeinasuit
```

Then open Claude Code in a folder for your clips (for example `Documents/Clipping`) and say:

```
set up clip autopilot
```

Claude installs the rest (downloader, local transcriber, ffmpeg) and checks everything works.

## Use it

Just talk to Claude:

1. **"Here's a new campaign: [paste the whole campaign page]"**: becomes `campaigns/<name>/RULES.md` with pay,
   minimum views, clip length, required tags and the rules most likely to get you rejected.
2. **"Find clips in [YouTube link or video file]"**: transcript + the 10 best moments, then Claude fixes the start
   and end of each and writes the on-screen hook.
3. **"Cut them"**: 1080x1920 clips with bold captions, the hook on screen for 3 seconds, loudness set to -14 LUFS,
   saved in `clips/<campaign>/`.
4. Post them yourself, submit the links on the campaign page.

Something broken? Say **"fix clip autopilot"** or paste the error.

## What's in Starter vs Pro

| | Starter (free) | Pro |
|---|---|---|
| Campaign brief -> rules checklist | yes | yes |
| Transcript + best-moment finder | yes | yes |
| 9:16 cuts with captions | plain look | 5 styled looks + your accent colour |
| Hook rewrites, scored | | yes |
| Automatic QA (framing, captions, length, loudness) | | yes |
| Sound effects pass | | yes |
| Captions + titles per platform, ready to paste | | yes |
| Posting calendar + earnings tracker app | | yes |
| New campaign in 2 minutes, weekly analytics | | yes |

**Pro:** https://brokeinasuit.gumroad.com/l/clip-autopilot-pro
**Tip jar / updates by email:** https://brokeinasuit.gumroad.com/l/clip-autopilot

## Good to know

- Clip only what the campaign gives or allows. The campaign's rules beat everything.
- No income promises: views and payouts depend on the campaign, your accounts and your posting.
- Help and wins: Broke In A Suit Discord (link on the Gumroad page).

MIT licence. Fonts: Anton (SIL Open Font License, see `engine/clipauto/fonts/OFL-Anton.txt`).
