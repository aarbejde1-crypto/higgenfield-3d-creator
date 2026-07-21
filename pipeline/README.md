# Listing → Video Kit pipeline

Repeatable process for turning an Airbnb listing URL into a shareable
video + one-page sales report. This is a playbook Claude follows inside a
session (there is no standalone server — the steps that call Higgsfield
run as MCP tool calls, which only exist inside a Claude session).

## Steps

1. **Scrape the listing**
   ```
   node pipeline/scrape_listing.js "<airbnb-url>" > listing.json
   ```
   Airbnb has no public listing API, so this reads the rendered page
   (title, description, rating, bed/bath/guest counts, and photo URLs
   from Airbnb's media CDN). Best-effort — Airbnb's markup changes over
   time, so spot-check `listing.json` before continuing, especially
   `photos` (dedupe/quality) and the regex-scraped stats.

2. **Import photos into Higgsfield**
   For each URL in `listing.json.photos`, call the `media_import_url`
   MCP tool (type: image) to get a `media_id`.

3. **Generate a "flying through" clip per room**
   Call `generate_video` with `kling3_0_turbo`, one `start_image` per
   photo, ~3s duration, 16:9. Prompt pattern for the flythrough feel:

   > Smooth cinematic drone-style camera flying forward into the room
   > [toward the doorway / across the space], gentle continuous motion,
   > low subtle altitude, real-estate drone footage aesthetic. Scene
   > completely static: no people, furniture and decor unchanged, no
   > distortion of room geometry.

   For rooms with a visible doorway/hallway in frame, bias the prompt
   toward flying *through* that opening — it's what sells the
   continuous-flight illusion once clips are crossfaded.

4. **Fetch the generated clips**
   Higgsfield's CDN is blocked by this environment's egress proxy, so
   direct `curl`/download of `rawUrl` fails with a 403 CONNECT tunnel
   error. Use the GitHub Actions relay instead:
   - Write each clip's `rawUrl` (one per line, `name url`) to
     `clips/urls.txt`.
   - Push to the branch — `.github/workflows/fetch-clips.yml` runs on
     push, downloads each URL with a runner (which has open network),
     and commits the files to `clips/`.
   - `git pull` to bring the clips back into the session's checkout.

5. **Stitch the clips in listing order**
   ```
   python3 pipeline/stitch.py --clips-dir clips \
     --manifest clips/order.txt --out walkthrough.mp4 --fade 0.4
   ```
   `clips/order.txt` lists clip filenames in flythrough order, one per
   line. Use a shorter fade (~0.3-0.4s) than a slideshow-style video —
   tighter cuts read as continuous flight instead of a dissolve between
   photos.

6. **(Optional) Upscale**
   `upscale_video` (provider `bytedance`, resolution `2k` or `4k`) on
   the stitched result if higher resolution is wanted. Cheaper than
   regenerating all clips at higher resolution.

7. **Render the sales report**
   ```
   python3 pipeline/render_report.py --data listing.json \
     --video <hosted-video-url-or-path> --out report.html
   ```
   Fill in `pitch_bullets` in `listing.json` for a custom pitch, or rely
   on the built-in defaults. The report is a single static HTML file:
   hero photo, stats, embedded video, pitch copy, a photo grid, and a
   "Text me this" button (an `sms:` link — opens the reader's own
   Messages app pre-filled; there's no automated SMS-sending service
   wired in).

8. **Deliver**
   Send `walkthrough.mp4` (or the upscaled version) and `report.html`
   to the user, and/or publish `report.html` as an Artifact if a
   shareable link is wanted.

## Known limitations

- This simulates a flythrough via per-room clips + crossfades. It is
  not a true continuous 3D reconstruction — there's no shared camera
  path or geometry across rooms, just consistent motion direction and
  tight transitions timed at doorways.
- The scraper depends on Airbnb's current DOM/CDN conventions and may
  need selector updates over time.
- No outreach/sending is automated — the report's share button and any
  pitch copy are for the operator to send themselves.
