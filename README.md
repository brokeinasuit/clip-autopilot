# Clip Autopilot (Starter, free)

**Paste a clipping campaign brief. Give it a video. Get the best moments cut into vertical clips with captions.**
It does everything up to ready-to-post. You post the clips yourself (about 2 minutes a clip) and submit the links.

Made for paid clipping campaigns (Whop Content Rewards, Clipping.net and similar). The *campaign brief* is the text on
the campaign page that tells you the pay and the rules. Runs inside [Claude Code](https://claude.com/claude-code) on
**macOS and Windows**. Everything runs on your own computer: no social accounts to connect, nothing uploaded, it never
posts for you.

## What you need

- **Claude Code** with a Claude Pro plan or higher (the free Claude plan does not include Claude Code).
  Not installed yet? Get it at [claude.com/claude-code](https://claude.com/claude-code). Finding clips and cutting
  them uses some of your plan's usage.
- **Python**, a free program the clipper runs on. You don't need to do anything now: Claude checks it during setup
  and tells you exactly what to click if it's missing. (On Windows, restart Claude Code after installing Python.)
- About 3 GB of free disk space while you work on a video.

## Install (2 minutes)

1. Make a folder for your clips, for example `Documents/Clipping` (on Windows, a folder **outside OneDrive**, e.g.
   `C:\Clipping`). Open Claude Code in that folder.
2. Type these two lines into the Claude Code chat box, pressing Enter after each:
   ```
   /plugin marketplace add brokeinasuit/clip-autopilot
   /plugin install clip-autopilot@brokeinasuit
   ```
3. Type `/reload-plugins` (or close and reopen Claude Code) so the new skills load.
4. Say: **set up clip autopilot**

Claude installs the tools it needs to download and listen to videos and checks everything works. It asks your
permission before running commands: choose **Yes** (or always allow for this folder).

## Use it

Just talk to Claude:

1. **"Here's a new campaign: [paste the whole campaign page]"**: Claude writes down the pay, minimum views, clip
   length, required tags and the rules most likely to get you rejected.
2. **"Find clips in [YouTube link or video file]"**: Claude finds the 10 best moments, fixes where each one starts
   and ends, and writes the text that shows on screen. For a file, drag it into the Claude Code window to paste its
   path. YouTube sometimes blocks downloads: if it fails, download the video in your browser (only if the campaign
   allows it) and give Claude the file.
3. **"Cut them"**: vertical 1080x1920 clips with bold captions, the hook on screen for 3 seconds, and the volume
   evened out for TikTok, Reels and Shorts.
4. **Your clips are in the `clips` folder** inside your clipping folder, one dated folder per clip. Post them, then
   submit the links on the campaign page.

Something broken? Say **"fix clip autopilot"** or paste the error.

## Starter vs Pro

| | Starter (free) | Pro |
|---|---|---|
| Campaign brief -> rules checklist | yes | yes |
| Best-moment finder | yes | yes |
| Vertical clips with captions | plain look | 5 styled looks + your accent colour |
| One sentence does the whole run ("make clips from this link") | | yes |
| Hook rewrites, scored | | yes |
| Automatic quality check (framing, captions, length, volume) | | yes |
| Sound effects pass | | yes |
| Captions + titles per platform, ready to paste | | yes |
| Posting calendar + earnings tracker (opens in your browser) | | yes |
| Weekly "why did this flop" review | | yes |

**Pro:** https://brokeinasuitassets.gumroad.com/l/clip-autopilot-pro
**Tip jar / updates by email:** https://brokeinasuitassets.gumroad.com/l/clip-autopilot
**Help:** reply to your Gumroad receipt email (the free download sends one too).

## Good to know

- Clip only what the campaign gives or allows. The campaign's rules beat everything.
- Source videos are big. When you're happy with a batch, say **"clean up that video"** and Claude deletes the source
  (your clips stay).
- No income promises: views and payouts depend on the campaign, your accounts and your posting.

---
MIT licence. Font: Anton (SIL Open Font License, `engine/clipauto/fonts/OFL-Anton.txt`).
