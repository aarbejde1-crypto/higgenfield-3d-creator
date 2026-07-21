# higgenfield-3d-creator

Turns an Airbnb listing URL into a drone-style flythrough video + a
shareable sales report, for pitching a "video tour" upgrade to the
listing's homeowner. Built around the Higgsfield MCP connector
(`https://mcp.higgsfield.ai/mcp`), driven from inside a Claude session.

## What it produces, per listing

- **A flythrough video** — one short AI-generated camera-move clip per
  room/space, stitched with crossfades into a single walkthrough.
- **A watermarked preview** of that video, for sending to a homeowner
  who hasn't paid/engaged yet.
- **A one-page sales report** (`report.html` / `report_preview.html`) —
  listing stats, the embedded video, a pitch, the original photos, and
  either a self-share button or a "Chat on WhatsApp" CTA.
- **An outreach message** — first-contact copy that leads with the free
  video (no ask up front) and invites the homeowner to continue on
  WhatsApp.

## How it works

Everything under `pipeline/` is a script Claude runs step by step inside
a session (there's no standalone backend — Higgsfield generation is an
MCP tool call, which only exists inside a Claude session):

1. `scrape_listing.js` — fetches the Airbnb page and reads Airbnb's own
   server-rendered listing JSON (title, stats, photos grouped by room).
   No public Airbnb API exists, so this is best-effort and may need
   updates if Airbnb changes its markup.
2. Photos get imported into Higgsfield and turned into short
   drone-style clips (`generate_video`, `kling3_0_turbo`).
3. `stitch.py` — crossfades the clips into one video, in listing order.
4. `watermark.py` — burns a center + four-corner mark into a copy of the
   video, for the free preview stage.
5. `render_report.py` — fills `report_template.html` with the listing
   data, the video, and (optionally) a WhatsApp deep link + preview
   banner.
6. `render_outreach.py` — fills `outreach_message_template.txt` with the
   listing detail, report link, and WhatsApp contact.

Full details, including known gotchas (Airbnb's headless-browser bot
detection, this environment's network egress policy, and a GitHub raw
`.html`-serves-as-plain-text quirk), are in `pipeline/README.md`.

## Output layout

Each listing gets its own folder under `listings/<slug>/`: the scraped
data, the clean video, the watermarked preview, both report variants,
and the outreach message.

## Sharing a report link

`raw.githubusercontent.com` serves `.html` as `text/plain` (a
GitHub security measure), so that link shows source code instead of
rendering. Use `rawcdn.githack.com/<owner>/<repo>/<branch>/<path>`
instead for a link that renders correctly — or set up GitHub Pages for
a permanent first-party link (not yet configured for this repo).

## Credits

Video generation costs Higgsfield credits (a few credits per clip).
Check balance before running a new listing.
