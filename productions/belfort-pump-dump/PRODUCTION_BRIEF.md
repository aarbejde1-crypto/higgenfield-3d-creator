# Production Brief — "How Jordan Belfort's Pump-and-Dump Scheme Worked"

Faceless YouTube Short · 40s · Finance / true-crime explainer
Framing: purely explanatory/historical. No investment advice, no instructions to replicate.

## Status

**BLOCKED at funding.** Higgsfield balance is 0.05 credits (plan: starter). The MCP free
trial is expired (`trial_status: expired`, `eligible: false`) and auto-refill is not
available for this workspace, so `use_unlim` is not a path here.

Confirmed against the backend, not assumed: the Phase 1 style-key submission was rejected
with `submission_failed — Out of credits on starter (monthly) plan in Private workspace`
(0 of 1 submitted). Nothing has been charged. Intake is complete and every parameter is
locked; the run resumes at Phase 1 the moment credits land.

Style formula (Stickman Cartoon, from `references/prompts.md §0`, used byte-identical
everywhere):

> flat 2D webcomic cartoon, extremely minimal — uniform thin even-weight black outlines,
> egg-shaped heads with tiny dot eyes and a single line mouth, plain noodle limbs, solid
> flat color fills with NO shading, NO gradients, NO texture, deadpan minimalist design,
> plain flat solid-color backgrounds.

## Locked intake (faceless-video workflow v2.4)

| Parameter | Value | Source |
|---|---|---|
| Channel type | Explainer | stated in brief |
| Motion mode | `stills` — narrated still pictures | picked |
| Duration | 40s | stated in brief |
| Aspect | 9:16 | implied by "YouTube Short" |
| Subtitles | Yes — burned, via the `subtitles` workflow | picked |
| Thumbnail | No | picked |
| Topic / script | User-supplied manuscript (below) | stated in brief |
| Style preset | Stickman Cartoon (`237dd06c…`), donor `f447d4d1…` | picked |
| Narrator voice | Archie (`bd072316…`, preset) | picked |

## Locked models (never substitute)

- Images: `seedream_v5_pro`, aspect `9:16`, 1080p-class
- Voice: `seed_audio` (stills mode uses the continuous read, not `text2speech_v2`)
- No `minimax_h3` — nothing is animated in this mode
- Assembly: `scripts/assemble_slides.sh` (never `assemble_final.sh`)

## Continuous narration (one unbroken read — 118 words)

> Jordan Belfort didn't trade stocks — he pumped and dumped them. At Stratton Oakmont, he
> built a machine that turned cheap penny stocks into millions of dollars almost overnight.
>
> First, his "rat holes" quietly bought shares before the public knew the stock existed.
> Then hundreds of brokers cold-called investors, pushing the price higher fast, block by block.
>
> Once the price peaked, Belfort quietly sold his shares while brokers pushed new buyers in.
> On the Steve Madden IPO alone, he pocketed twenty-three million dollars in under three minutes.
>
> That's the pump and dump: inflate the price, then dump it on investors left holding the loss.
> Stratton Oakmont collapsed, Belfort pleaded guilty to fraud, and served nearly two years in prison.

118 words over 40s ≈ 177 wpm — brisk but normal for a Short. If the measured read runs
long, trim Block 4 rather than speeding the delivery.

## Through-line: The Chart

A glowing candlestick/line stock chart: flat → steep climb → peak & crack → frozen red
flatline. It recurs as a prop reference in roughly every third framing and resolves against
the courthouse imagery in the payoff.

## Frame budget (stills mode is frame-count-gated)

- Assembler hard floor: `ceil(narration_sec / 1.5)` ≈ **27 frames** for a 40s read.
- Target cadence: one frame every ~1s → **~40 frames**.
- Split: ~20 KIND-A new framings (rendered from the asset roster) + ~20 KIND-B edits
  (previous frame + one visible change, chained at most twice before a new framing).
- The manuscript's 20 shots map 1:1 onto the 20 KIND-A framings; each spawns 1–2 edits.

## Shot outline (KIND-A framings, in spoken order)

Block 1 — HOOK · location `trading_floor_stage`
1. WIDE low — trading-floor stage, neon STRATTON OAKMONT sign glowing
2. MEDIUM eye — chart ticking upward on a screen behind a silhouetted broker
3. CLOSE-UP high — hand on a phone receiver against the desk
4. CLOSE-UP low — the Chart's line spiking sharply upward
5. MEDIUM eye — the rising chart filling the frame

Block 2 — BUILD · location `boiler_room_desks`
6. WIDE high — rows of brokers at phone desks
7. CLOSE-UP eye — a hand on a phone dial
8. MEDIUM low — a stamp coming down on a stock-certificate prop
9. MEDIUM high — the Chart climbing faster
10. WIDE eye — the boiler room erupting, fists in the air

Block 3 — TURN · location `ipo_bell_stage`
11. WIDE low — a hand at the IPO bell
12. CLOSE-UP eye — the Chart at its peak
13. MEDIUM high — a briefcase snapping shut over stacked cash
14. CLOSE-UP low — the Chart cracking and plunging
15. WIDE eye — confetti over the floor turning to red warning light

Block 4 — PAYOFF · location `courthouse_steps`
16. WIDE low — exterior of a federal courthouse
17. CLOSE-UP eye — a gavel coming down
18. MEDIUM high — handcuffs closing around wrists
19. CLOSE-UP low — the Chart frozen flat and red
20. MEDIUM eye — the frozen chart, final held frame

Shot-mix law: two CLOSE-UPs never run back to back. Micro-variation frames keep their
base's shot size.

## Asset roster (Phase 2 — generated before any frame)

Locations (9:16): `trading_floor_stage`, `boiler_room_desks`, `ipo_bell_stage`, `courthouse_steps`
Props (1:1): `the_chart`, `neon_sign`, `phone_prop`, `stock_certificate`, `briefcase_and_cash`, `gavel`, `handcuffs`
Characters (2:3): generic silhouetted broker figures — no real-person likeness of Jordan Belfort
or any other named individual; the story is told through the floor, the props and the Chart.

## Known conflicts with the source manuscript

1. **Title cards will not be generated as in-frame text.** Stills mode bans on-screen text in
   generated frames. "PUMP & DUMP" (Block 1, Shot 5) and "PUMP. DUMP. COLLAPSE." (Block 4,
   Shot 5) cannot be rendered by the image model. The burned subtitles still carry the words
   of the narration. If the cards matter, they need a post step outside this pipeline.
2. **Camera moves and impact beats do not apply.** Push-ins, whips, drifts and slams are motion-
   mode grammar; in stills they are replaced by the frame-burst cadence described above.
3. **No real-person likeness.** Belfort is named in narration but not depicted.

## SEO & discovery metadata

- **Title:** How Jordan Belfort's Pump-and-Dump Scheme Actually Worked
- **Description:** The real Wolf of Wall Street scam, explained in 40 seconds. Jordan Belfort
  didn't get rich trading — he built a pump-and-dump machine at Stratton Oakmont, inflating
  penny stocks and cashing out before investors caught on. Here's how it worked, and how it
  all fell apart. #Shorts #WolfOfWallStreet #StockMarket #FinanceExplained
- **Hashtags:** #Shorts #WolfOfWallStreet #StockMarket #FinanceExplained
- **Tags:** Jordan Belfort, Wolf of Wall Street, pump and dump scheme, Stratton Oakmont,
  stock market fraud, securities fraud, finance explainer, true crime finance, penny stocks,
  Steve Madden IPO, boiler room stocks
- **CTA overlay** (top of Block 4, ~75% mark): "More true-crime finance breakdowns like this
  — follow along."
- **Cover frame:** framing 1 — the trading floor with the glowing STRATTON OAKMONT sign.

## Sources

- https://www.crimemuseum.org/crime-library/white-collar-crime/jordan-belfort/
- https://allthatsinteresting.com/stratton-oakmont
