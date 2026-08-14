---
name: short-manuscript
description: Write a timestamped manuscript (shot-by-shot script with timecodes, on-screen captions, voiceover lines, and per-shot generation prompts) for a vertical short-form video — TikTok, Reels, YouTube Shorts. Use this whenever the user wants a script, storyboard, shot list, beat sheet, or manuscript for a short/reel/TikTok, wants to turn photos or a product/property/place into a short video, asks how to structure or time a short, or asks to plan a video before generating clips — even if they don't say "manuscript" or "timestamp". Also use it when they have footage or images and need to decide what goes where and for how long.
---

# Timestamped manuscripts for vertical shorts

A short lives or dies in its first second and a half, and most people watch
it muted. Those two facts drive everything here: the strongest shot goes
first, the message rides in on-screen text rather than narration, and every
beat has a hard in/out so the edit can be cut against it.

The bundled script does the arithmetic — beat boundaries, timecodes,
fitting content to runtime. That frees you to spend your effort where it
actually matters, which is the writing.

## Workflow

1. **Establish the subject and the shot order.** You need an ordered list of
   shots and a little metadata. Order matters more than people expect:
   beat one is the hook, so the most striking shot belongs first, not the
   chronological or spatial first. If the user hands you a walkthrough order
   ("front door, hallway, kitchen…"), ask whether the best shot is really the
   opener before accepting it.

2. **Generate the manuscript** with `scripts/make_manuscript.py`.

3. **Rewrite the copy.** The script fills captions with sound defaults, not
   final lines. This is the part that needs a person or a model thinking
   about *this* subject — see "Writing the copy" below.

4. **Hand back the `.md`** as the thing to read and edit. The `.json` is for
   machines: each beat carries a `prompt` field ready for a 9:16 video
   generator, plus its source media reference.

## Running the script

Generic subject — a product, a place, a recipe, a car:

```bash
python3 scripts/make_manuscript.py --spec spec.json \
  --out-md short.md --out-json short.json --duration 24
```

```json
{
  "title": "Wee Nook — a Hobbit Hole",
  "subject": "McEwen, Tennessee",
  "facts": {"rating": "4.98", "guests": "2"},
  "shots": [
    {"name": "Exterior", "media": "01.jpg"},
    {"name": "Kitchen", "caption": "A real kitchen, underground"}
  ]
}
```

`facts` is free-form and feeds the default hook and a few captions. Per-shot
`caption` and `camera` are optional overrides — set them when you already
know the line and want the script to stop guessing.

Useful flags: `--hook` and `--cta` to set the opening and closing lines
directly, `--duration` for total runtime, `--hook-seconds` / `--cta-seconds`
to re-balance the ends.

## How runtime shapes the cut

Runtime is the real constraint, and the script resolves it rather than
letting beats drift out of sync:

- **Too many shots for the time** — it trims to what fits, holding a 2s
  floor per beat. Below about 2s a viewer registers movement but not the
  room, so cramming twelve shots into twenty seconds produces a blur, not a
  tour.
- **Time to spare** — it stretches the remaining beats to fill.
- **Runtime that can't fit hook + CTA** — it stops with an explanation
  instead of emitting a broken plan.

For reference: 20–30s suits a property or product tour. Under 15s you have
room for maybe three body beats, so pick the three that sell it.

## Writing the copy

The defaults are scaffolding. What separates a short that works:

- **The hook is the whole ballgame.** "Living room" is not a hook. A number
  that surprises, a contradiction, or a promise works: *"4.98 stars — and
  you can actually book it"*, *"This is underground"*. If the subject has a
  genuinely unusual fact, that is the first line.
- **Captions are read, not spoken.** Keep them under ~40 characters or the
  platform's own interface covers them. One idea per beat.
- **Say something, don't label.** "Full kitchen — not a kitchenette" earns
  its beat; "Kitchen" does not. Every caption should add a fact the picture
  alone doesn't carry.
- **Don't repeat a line across similar shots.** The script falls back to the
  shot's own name when a default would repeat, but that fallback is a plain
  label — usually worth replacing by hand.
- **Voiceover is derived from the caption** and strips typographic
  shorthand (`·`, `…`, `★`) that a narrator or TTS would trip over. If the
  short is silent, ignore the `vo` field.

## Vertical framing

Most source material is landscape; a 9:16 crop throws away the sides. Two
consequences worth stating to the user rather than discovering in the edit:

- Compose on what sits in the centre of the frame.
- Prefer push-in, tilt, and rise moves over pans. A pan across a landscape
  photo cropped to vertical mostly shows wall.

The per-beat `prompt` in the JSON already specifies 9:16 and a static scene
(no people, nothing rearranged, no warped geometry) — reliably the failure
modes that make a generated property or product shot unusable.

## Output shape

The `.md` opens with a timecode table so the whole cut is legible at a
glance, then expands each beat with its caption, voiceover, camera move, and
generation prompt, and closes with production notes. The `.json` mirrors it
with `beats[]` carrying `start`, `end`, `duration`, `caption`, `vo`,
`camera`, `media`, and `prompt`.

Keep both. People edit the manuscript; pipelines read the JSON.
