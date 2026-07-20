# Task: Airbnb Listing → 3D Walkthrough Video (via Higgsfield)

## Goal
Turn the 12 attached photos of an Airbnb apartment into **one combined walkthrough video**, using the Higgsfield MCP connector (`https://mcp.higgsfield.ai/mcp`) to apply a 3D camera-move / parallax effect to each photo, then stitch the resulting clips together in order.

## Source listing
Copenhagen apartment ("Indre By" / city center), 4 bedrooms, 7 beds, 1 bathroom, ★4.78.
Airbnb link: https://www.airbnb.dk/rooms/1224585359222360054

## Photos (use in this order for the walkthrough)
1. `01-exterior.jpg` — street facade, establishing shot
2. `02-living-room.jpg` — living room, rattan chairs + sofa
3. `03-dining-table.jpg` — dining table set for a meal
4. `04-dining-room.jpg` — dining room, wide angle, curved wall
5. `05-bedroom-suite.jpg` — primary bedroom/sitting suite, wide
6. `06-bedroom-tv.jpg` — bedroom with TV cabinet
7. `07-bedroom-mirror.jpg` — bedroom with oval mirror + nightstand
8. `08-bedroom-desk.jpg` — bedroom with writing desk
9. `09-hallway.jpg` — hallway with exposed half-timber wall + art
10. `10-office-nook.jpg` — small home office corner
11. `11-reading-nook.jpg` — reading nook by balcony doors
12. `12-bunk-room.jpg` — kids' room with bunk beds

## What to do
1. For each photo, call the Higgsfield MCP's image-to-video tool, applying a smooth 3D camera-move / parallax effect (subtle dolly or pan works best for real-estate walkthroughs — avoid anything too aggressive that distorts the room).
2. Keep each clip short (2-4 seconds) so the combined video flows like a walkthrough rather than a slideshow.
3. Download/save all resulting clips.
4. Stitch the clips together **in the numbered order above** into a single combined video (add a simple crossfade or hard cut between clips — no need for music/titles unless you want to suggest one).
5. Output one final video file.

## Notes
- Photos are already resized/converted to JPG for compatibility.
- If Higgsfield's tools support batch/sequence generation directly, prefer that over generating one-by-one.
- This was prepped in a separate Claude session that couldn't reach the Higgsfield MCP connector directly — that's why this handoff file exists.
