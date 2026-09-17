---
name: auto-short
description: End-to-end faceless Short factory — researches live SEO/trend data and picks the topic itself, writes the full manuscript with the manu-writer skill, generates the finished vertical video, and hands back upload-ready title/description/hashtags/tags. Use this whenever someone wants a video made without choosing the topic themselves: "make me a short", "create a video for my channel", "best SEO video right now", "you pick the topic", "automatic video", "what should I post today", "generate today's video". Also use it when they only ask what to make next for a faceless channel, since the topic-selection stage stands alone. Not for rendering a script the user already wrote (go straight to the faceless-video workflow), and not for a manuscript with no video (manu-writer alone covers that).
---

# Auto Short

Turns "make me a video" into a finished, uploadable Short — topic chosen from
SEO evidence, manuscript written by `manu-writer`, video produced by the
`faceless-video` workflow, metadata ready to paste into the upload form.

## The autonomy contract

This skill exists because the user does *not* want to be asked. The whole
value is that they say "make one" and get a video back. So:

**Decide, state, proceed.** Every creative and technical parameter — topic,
angle, duration, style preset, voice, aspect, caption style — is yours to
choose. Announce each decision as a one-line statement with its reason, never
as a question. "Topic: why a stock can gap down 40% before the market opens —
highest demand-to-competition gap of the eight I scored." That is the whole
interaction.

Three things break the contract and are worth stopping for:

1. **No channel identity at all, first run ever.** You can't pick an SEO topic
   for a channel that doesn't exist yet. Ask one question — what the channel is
   about — then write `channel.json` and never ask again.
2. **Publishing.** Posting to YouTube/TikTok is public and hard to walk back.
   Always confirm before publishing, even in an otherwise hands-off run.
3. **A factual claim you can't source.** Drop the topic and take the next
   candidate rather than shipping something you'd have to retract.

Credit spend on generation is *not* on that list. The user asked for a video;
generating it in their own account is the thing they asked for. State the
estimate in the same line you announce the topic and keep going. If they want
the script without the spend, they'll say "just the script" — honour that by
stopping after Stage 2.

## Run layout

Everything for one video lives in one dated directory so a run is auditable
and a later run can see what's already been published:

```
runs/2026-09-17-premarket-gap-down/
├── topic-selection.json   # the candidates, their scores, why this one won
├── manuscript.md          # manu-writer output (A) + (B)
├── script_manifest.json   # manu-writer output (C) — the pipeline handoff
├── metadata.md            # title / description / hashtags / tags / CTA
└── video/                 # the finished file and any intermediates
```

`channel.json` sits at the repo root, not inside a run — it's the thing that
persists across videos.

---

## Stage 0 — Channel identity

Read `channel.json`. If it doesn't exist, build it: infer what you can from the
repo (README, prior runs, anything the user has said in this conversation), ask
the single niche question only if there is genuinely nothing to go on, then
write it.

```json
{
  "niche": "finance / investing education, faceless",
  "audience": "retail investors who know the words but not the mechanisms",
  "tone": "plain-language explainer, Wall Street register, no hype",
  "language": "en",
  "style_preset": "Editorial Motion Graphics",
  "voice_id": null,
  "aspect": "9:16",
  "duration_seconds": 40,
  "caption_preset": "Impact Bold",
  "compliance": "explanatory only — never buy/sell/hold, no price targets",
  "published_topics": []
}
```

`published_topics` is the one field that earns its keep over time: it stops
Stage 1 from re-picking a topic the channel already covered, which is the most
common way an automated channel starts cannibalising its own search results.

Pin `voice_id` after the first run. A faceless channel that changes narrator
between videos reads as a content farm to returning viewers, and returning
viewers are the audience the algorithm rewards most.

---

## Stage 1 — Pick the topic from evidence, not vibes

Read `references/seo-topic-selection.md` and follow it. In outline:

1. Run 3–5 web searches for the channel's niche — what's trending now, what
   people are searching, what the competing channels have *not* covered well.
2. Write down 6–10 candidate topics, each as a specific angle rather than a
   subject. "Short selling" is a subject; "why a short squeeze forces buyers
   to buy at any price" is a topic.
3. Score each candidate on the eight signals in the reference, then run
   `scripts/pick_topic.py` to rank them. Use the script rather than eyeballing
   the winner — writing the per-signal numbers down is what forces an honest
   comparison, and the same weights applied every run are what make the
   channel's topic mix coherent instead of drifting with your mood.
4. Announce the winner in one line with the reason. Save
   `topic-selection.json`.

The reference explains why the weights sit where they do; the short version is
that hook-ability and the demand-to-competition gap outrank RPM, because a
$4-RPM topic you can actually rank for beats a $25-RPM topic you'll drown in.

---

## Stage 2 — Manuscript

Invoke the `manu-writer` skill with:

- **TOPIC** — the winning angle, worded as the angle, not the subject
- **DURATION_SECONDS** — `channel.json`'s `duration_seconds` (default 40)
- **CHANNEL** — the niche, audience, tone and compliance line from
  `channel.json`, so the voiceover lands in the channel's register rather than
  manu-writer's finance default

Take all three of its outputs. Save (A)+(B) as `manuscript.md`, (C) as
`script_manifest.json`, and the SEO block also as `metadata.md` on its own so
it's one copy-paste at upload time.

Before moving on, check two things the video stage can't fix later:

- **The hook says the keyword out loud.** Block 1's VO must contain the exact
  keyword phrase the title targets. Platforms transcribe audio and index it
  alongside the text metadata, so a hook that talks *around* the term throws
  away half the ranking signal the title is chasing.
- **The payoff reuses a phrase from the hook**, not just its idea. That echo
  is what makes the Short loop, and replays count as real watch time.

Fix either by asking manu-writer to revise that block — cheaper now than after
the clips are generated.

---

## Stage 3 — Generate the video

Read `references/pipeline-handoff.md` before the first generation call. It
carries the exact parameter lock, the fallback pipeline, and the traps in the
handoff.

The essential move: the `faceless-video` workflow asks only for parameters you
*haven't* already stated, so state all of them in the message that loads it.
A run that states type, motion mode, style, duration, aspect, subtitles,
thumbnail and topic up front asks zero questions and goes straight through to
delivery — which is the entire point of this skill. Leave one out and the user
gets an intake screen they didn't want.

Hand over `script_manifest.json` as an authored script, not as a topic to
re-write. The blocks are already timed, arced and shot-listed; letting the
video stage re-derive them throws away Stage 2 and usually loses the hook.

---

## Stage 4 — QC before you call it done

Six checks, in the order they're cheapest to fix:

| Check | Why it matters |
|---|---|
| First frame is legible and high-contrast as a still | Shorts auto-select the opening frame as the thumbnail; a strong one is worth ~85% more click-through than a random grab |
| Burned captions start at true 0.0s | Most short-form is watched muted; a caption that starts a beat late loses the hook entirely |
| Runtime lands in the 30–45s band | The band that maximises completion rate and recommendation rate at once |
| Payoff echoes the hook's wording | Drives replays, which count as watch time |
| No shot holds past ~2.5s | A longer hold reads as a slideshow and shows up as a retention dip |
| Compliance line holds across every VO line | One prescriptive sentence can cost the whole video |

If the run produced a real narration track, measure its actual pace. manu-writer
budgets words at an assumed 2.9 words/second and real voices vary a lot — if
block 1 came back more than ~15% off, rewrite the *remaining* blocks' lines to
fit rather than time-stretching audio. Stretched audio is audible; a rewritten
line isn't.

Optionally run the virality predictor on the finished file. Treat its score as
a second opinion on the hook, not a gate — if it flags weak early retention,
the fix is block 1, never the whole script.

---

## Stage 5 — Deliver

Post, in this order:

1. The finished video file.
2. The metadata block — title, description, hashtags, tags, CTA, cover-frame
   note — formatted for copy-paste, not as JSON.
3. One line on what was decided and why, so the next run has context.

Then append the topic to `published_topics` in `channel.json`.

Publishing to a platform is a separate, confirmed step. Ask first, every time.

---

## Running a batch

For several videos at once, run Stage 1 once and take the top N candidates
rather than running the whole skill N times — one research pass, N manuscripts.
Check they don't compete: two Shorts targeting the same keyword split their own
impressions, so if the top two candidates share a core keyword, take the third
instead. Space them out on the calendar; a steady weekly cadence outperforms a
burst, and the algorithm needs a consistent signal to learn who the channel is
for.

## Bundled files

- `references/seo-topic-selection.md` — the scoring rubric, the signals, the
  search recipe, and the reasoning behind the weights. Read it in Stage 1.
- `references/pipeline-handoff.md` — parameter lock for `faceless-video`, the
  Everygen fallback, and the handoff traps. Read it in Stage 3.
- `scripts/pick_topic.py` — deterministic scoring and run scaffolding.
  `python3 scripts/pick_topic.py candidates.json` prints the ranking and writes
  `topic-selection.json`. Run `--help` for the input shape.
