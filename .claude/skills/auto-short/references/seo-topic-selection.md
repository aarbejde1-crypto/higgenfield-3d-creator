# SEO topic selection

How Stage 1 turns "make me a video" into one specific topic, with a trail you
can audit later when the analytics come in.

## Contents
- [The core idea](#the-core-idea)
- [Step 1 — Research](#step-1--research)
- [Step 2 — Write candidates as angles](#step-2--write-candidates-as-angles)
- [Step 3 — Score the eight signals](#step-3--score-the-eight-signals)
- [Step 4 — Rank and pick](#step-4--rank-and-pick)
- [Niche RPM reference](#niche-rpm-reference)
- [Failure modes](#failure-modes)

---

## The core idea

The metric that decides a Short's fate is retention, and the metric that
decides whether a topic is *winnable* is demand relative to competition. RPM
decides only how much a win is worth. So the ranking formula weights them in
that order: hook-ability first, gap second, money third.

The trap this avoids: every "best YouTube niches" list ranks by RPM alone,
which is why finance and AI-tools are the two most saturated categories on the
platform. A $4-RPM topic you can rank for beats a $25-RPM topic you cannot.
Profitability is `RPM × realistic ranking potential`, and the second term is
the one almost everybody drops.

## Step 1 — Research

Run 3–5 searches. Vary the shape — each one answers a different question:

| Search shape | What it tells you |
|---|---|
| `<niche> trends <current month/year>` | what has momentum right now |
| `<niche> questions people ask` / `<niche> reddit common questions` | real demand phrased the way viewers phrase it |
| `<niche> youtube shorts` | who's already covering it and how well |
| `<niche> mistakes` / `<niche> myths` | counterintuitive angles, which hook best |
| `<niche> <specific mechanism> explained` | whether a clear explanation already exists |

Two things to actually extract, rather than skimming:

- **The phrasing viewers use.** "Why is my listing not showing up" is a search
  query; "Airbnb search ranking factors" is how a marketer writes. Target the
  first — it's what gets typed, and it's what the hook should say out loud.
- **Where the existing coverage is thin or wrong.** A topic with high demand
  and three bad videos is worth more than one with high demand and thirty good
  ones. This is the `gap` signal and it's the hardest to fake.

Recency matters here. Short-form ranking mechanics and niche saturation both
move fast, so prefer sources from the last few months, and if the user's own
analytics contradict anything in this file, their data wins — say so and
adjust.

## Step 2 — Write candidates as angles

6–10 candidates. Each one is an **angle**, not a subject.

| Subject (too vague) | Angle (usable) |
|---|---|
| Airbnb pricing | Why your nightly rate drops the week after a cancellation |
| Short squeeze | How a stock rockets 300% with zero news behind it |
| AI tools | The one prompt pattern that stops ChatGPT inventing sources |

The test: can you state it as a bold claim or a curiosity gap in eight words or
fewer? If not, it's still a subject. Narrow it until you can — that sentence
becomes block 1's hook, and the first three seconds decide everything else.

Drop anything already in `channel.json`'s `published_topics`, or that shares a
core keyword with a recent one. Two videos on the same keyword split their own
impressions.

## Step 3 — Score the eight signals

Each 0–5, from the research — not from memory. Write a one-line justification
per signal; that note is what makes the pick reviewable in a month.

| Signal | 0 | 5 |
|---|---|---|
| `demand` | nobody searches this | high, sustained search volume |
| `gap` | thirty good videos already | real demand, thin or wrong coverage |
| `hook_3s` | needs setup before it lands | a bold claim in ≤8 words |
| `payoff` | resolves only after a long explanation | one line closes it, and can echo the hook |
| `rpm_band` | low-value advertiser category | premium category (see table below) |
| `evergreen` | stale in two weeks | still true and searched in a year |
| `fit` | off-niche for this channel | squarely what the audience subscribed for |
| `risk` | regulated advice, unverifiable claims | purely explanatory, fully sourceable |

`risk` is scored like the others — 5 is *safe* — and then subtracted, so a
risky topic has to be outstanding everywhere else to survive. That asymmetry is
deliberate: a compliance problem doesn't cost you a video, it can cost the
channel.

Note on `evergreen`: a spike topic can still be the right pick when `demand`
and `gap` are both high — riding a live trend is a legitimate play. The weight
just stops the channel being built entirely out of things that expire.

## Step 4 — Rank and pick

Run the script:

```bash
python3 scripts/pick_topic.py candidates.json --run-dir runs/
```

Weights, and why:

| Signal | Weight | Reasoning |
|---|---|---|
| `hook_3s` | 2.5 | Retention is the dominant ranking signal and most drop-off happens in the first three seconds. Nothing else in the video matters if this window is lost. |
| `gap` | 2.0 | The term everyone drops. Winnability, not raw demand. |
| `demand` | 1.5 | Necessary but not sufficient — high demand with no gap is just competition. |
| `fit` | 1.5 | Channel coherence is what trains the algorithm on who the audience is. |
| `payoff` | 1.5 | A clean one-line close drives loops, and replays count as watch time. |
| `rpm_band` | 1.0 | Decides what a win is worth, not whether you win. |
| `evergreen` | 1.0 | Compounding value, but not at the cost of a live trend. |
| `risk` | −2.0 | Inverted penalty. |

Announce the winner in one line with the deciding signal. Then save
`topic-selection.json` — every candidate, every score, every justification.
When a video over- or under-performs, that file is how you learn which signal
you're systematically misjudging.

## Niche RPM reference

Rough 2026 bands for `rpm_band` scoring. These move; re-check when the channel
is in an unlisted niche.

| Niche | RPM | Score |
|---|---|---|
| Personal finance, investing education | $15–40 | 5 |
| B2B software, SaaS, tech tutorials | $10–25 | 5 |
| AI tools / AI-assisted income | $10–25 | 4 |
| Luxury, wealth, real estate, short-term rental | $12–18 | 4 |
| Health and wellness | $10–18 | 4 |
| Motivation, self-improvement | $8–12 | 3 |
| General education, micro-learning | $5–10 | 2 |
| Entertainment, pranks, pets, gaming | $2–5 | 1 |

The last row is worth reading carefully: entertainment is the largest share of
Shorts viewership by a wide margin and the worst-paying. High views, low
revenue — fine as a growth play, bad as the whole strategy.

## Failure modes

- **Scoring from memory instead of research.** If every candidate scores 4 on
  `demand`, the searches didn't happen.
- **`gap` set by how the topic feels rather than what's on the platform.** It
  requires actually looking at what already ranks.
- **Picking the highest-RPM candidate regardless of rank.** The weights already
  price RPM in; overriding them is how a channel ends up in the most
  competitive niche on the platform with no differentiator.
- **Ten variations of one topic.** Candidates should span the niche, not
  rephrase a single idea ten ways — otherwise the ranking is meaningless.
- **Subjects that never got narrowed to angles.** Shows up later as a weak
  block-1 hook that no amount of production rescues.
