---
name: clip-rules
description: Turn a clipping campaign brief (Whop Content Rewards, Clipping.net, ClipHaus or any paid clipping campaign page the user pastes) into a campaign folder with a RULES.md checklist the clipping engine reads - pay per 1K views, minimum views, clip length, platforms, required tags and caption text, banned content, allowed sources. Use when the user pastes a campaign brief or link, says "new campaign", "set up this campaign", "read these rules", or before finding clips for a campaign that has no RULES.md yet.
---

# Clip Autopilot: campaign rules

Goal: one folder per campaign at `campaigns/<campaign-slug>/` in the workspace, with a filled `RULES.md`. The engine reads its top block; the user reads the checklist before every post.

## Steps

1. **Get the brief.** If the user gave a link you cannot open (most campaign pages need a login), ask them to copy the whole campaign page text and paste it. Never guess rules you were not given.

2. **Pick the slug**: lowercase, hyphens, from the creator or campaign name (`caleb-hammer`, `ring-drone`). Create the folder:
   ```
   PY "${CLAUDE_PLUGIN_ROOT}/scripts/ca.py" new <campaign-slug>
   ```
   (`PY` = the Python command that worked in clip-setup: `python3` on macOS, `py` or `python` on Windows.)

3. **Fill the block at the top of `campaigns/<slug>/RULES.md`**, one `key: value` per line, only from the brief:
   - `name`, `campaign_url`, `platform_site` (Whop, Clipping.net...), `creator`
   - `pay_per_1k_views_usd`, `min_views_for_payout`, `max_payout_per_post_usd`, `budget_left_usd`, `audience_geo`
   - `min_length_s` / `max_length_s`: the brief's limits. If it gives none, keep 15 / 60 and say so.
   - `platforms`: comma list from tiktok, instagram, youtube
   - `required_tag` (the @handles), `required_caption_text` (word for word, keep capitals and emojis), `hashtags`, `submit_within`
   Leave a field empty when the brief does not say. Never invent a number.

4. **Fill the notes below the block** (allowed sources, allowed edits, banned things, caption rules, account requirements, review time) in short bullets from the brief, quoting exact wording where wording matters.

5. **Write the source links** the campaign allows into `campaigns/<slug>/sources.txt`, one per line.

6. **Report back in under 8 lines**: pay, minimum views, length window, platforms, the exact caption/tag requirement, the 1-2 rules most likely to get a clip rejected. Flag anything risky (for example: "requires 40%+ US audience", "no reposting of full clips", "submit within 30 minutes").

7. Offer the next step: "Send me the first video (link or file) and I'll find the best moments."

## Rules
- The campaign's rules always beat anything else, including these skills.
- Only clip what the campaign provides or allows. If the user wants to use footage the brief does not allow, say so plainly.
