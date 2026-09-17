# Pipeline handoff

Stage 3: turning `script_manifest.json` into a finished file without the user
being asked anything.

## Contents
- [Which pipeline](#which-pipeline)
- [The parameter lock](#the-parameter-lock)
- [Handing over the script](#handing-over-the-script)
- [Traps](#traps)
- [Fallback — Everygen](#fallback--everygen)
- [Publishing](#publishing)

---

## Which pipeline

**Higgsfield `faceless-video` (v2.4) is the default.** It's the only pipeline
that takes a locked script, a locked style, one narrator voice and burned
subtitles through to a single finished file in one run — which is exactly the
shape of a manu-writer manuscript. Its Animated mode is built on 10-second
blocks of hard-cut shots, the same unit manu-writer writes in, so the manifest
maps block-for-block with nothing to translate.

Load it with `get_workflow_instructions({ workflow: "faceless-video" })`
*before* any generation call. Use Everygen only if Higgsfield isn't connected.

## The parameter lock

`faceless-video`'s intake asks only for parameters that are still missing, and
skips any round the user's message already answered. That's the mechanism this
skill runs on: **state every parameter in the message that loads the workflow,
and the intake disappears entirely.**

State all nine, as flat statements:

| Parameter | Value | Source |
|---|---|---|
| Channel type | Explainer | the default for a niche explainer channel; History / Kids / Fairy Tale only if the niche actually is one |
| Motion mode | Animated | matches manu-writer's 5-shots-per-10s-block structure; Still pictures throws the shot list away |
| Style | name it verbatim | `channel.json.style_preset`, e.g. "Editorial Motion Graphics" |
| Duration | the manuscript's real runtime | e.g. 40 seconds — see the duration trap below |
| Aspect | 9:16 | Shorts are vertical; the model supports only 9:16 and 16:9 |
| Subtitles | yes | captions roughly double watch time and most short-form is watched muted |
| Thumbnail | no | Shorts don't accept a custom thumbnail — the opening frame is the thumbnail |
| Topic | the winning angle | Stage 1 |
| Script | the manuscript | authored text, see below |

Naming the style is what keeps the run hands-off. The workflow opens its preset
card gallery unless the user named a style, so if `channel.json` has one, say
it by name. On the very first run for a channel, opening the gallery once is
correct — record whatever gets picked into `channel.json` so every later run is
silent. Style drift between videos is worse than a slightly wrong style: a
faceless channel's look *is* its brand.

Set the voice once and pin it in `channel.json` for the same reason.

## Handing over the script

Pass the manuscript as an **authored script**, not as a topic to write from.
The workflow treats a pasted script as the user's own words and doesn't rewrite
it — which is what you want, because the blocks are already timed, arced,
shot-listed and keyword-placed.

Give it the VO lines as the script, and use the manifest's `shots`,
`location`, `through_line` and `assets_used` for the visual plan. Two fields
carry more weight than they look:

- **`through_line`** — the recurring object that changes state block to block.
  It's what makes four separately generated 10-second clips read as one video
  instead of four unrelated ones. Keep its progression intact across blocks.
- **`location`** — a stable handle. Blocks sharing a handle share a location,
  and only the *first* block at a location opens on an establishing wide; later
  ones open on a fresh close or medium. Re-establishing the same picture reads
  as padding.

`style` is deliberately blank in the manifest — manu-writer leaves the look to
this stage. Fill it from `channel.json`.

## Traps

**Duration.** The workflow's duration round offers 1 / 2 / 3 minutes; a 40s
Short needs the "Other" path. State the real number explicitly ("40 seconds")
so the round never opens. Don't let a Short get rounded up to a minute — the
30–45s band is where completion rate and recommendation rate peak together, and
that band is the reason manu-writer defaults to 40.

**Caption start.** Burned captions must start at true 0.0s, not a beat in. The
hook's words on screen from frame one is most of the readable-first-frame
benefit, and it's the one caption detail that's expensive to fix after render.
Say it explicitly at the caption step.

**Re-derivation.** If the video stage starts writing its own script, the
handover didn't land as authored text. Stop and re-hand it — a re-derived
script loses the hook wording, and the hook is the whole video.

**Cover frame.** There is no separate thumbnail step for a Short. Block 1 shot
1 *is* the thumbnail, so it has to be legible and high-contrast as a single
still. The manifest's `seo.cover_frame_note` says what it should contain — pass
it through rather than letting the generator choose.

## Fallback — Everygen

If Higgsfield isn't available, assemble manually:

1. Generate one clip per block from the manifest's shots.
2. Generate the voiceover as one continuous track, not per-block — per-block
   audio leaves seams at every join.
3. `compose_video` in two passes: glue the clips first with no `audioUrl` on
   any clip, then a single-clip pass carrying the one voiceover over the glued
   result. Putting `audioUrl` on a multi-clip payload ends the narration with
   the first clip.
4. `add_captions` on the composed result, `position: "bottom"` (above the app
   UI safe area), preset from `channel.json` — "Impact Bold" is the punchy
   default that suits an explainer.

More moving parts and more places to lose sync, which is why it's the fallback.

## Publishing

Not part of the automatic run. Publishing is public and hard to undo, so
confirm every time, even when the rest of the run was hands-off — show the
title, description and hashtags, and post only on a clear yes.
