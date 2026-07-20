# higgenfield-3d-creator

Turn Airbnb listing photos into a combined 3D walkthrough video via the
Higgsfield MCP connector (`https://mcp.higgsfield.ai/mcp`).

## Source listing
Copenhagen apartment ("Indre By" / city center), 4 bedrooms, 7 beds, 1 bathroom, ★4.78.
Airbnb link: https://www.airbnb.dk/rooms/1224585359222360054

## Photos
See `photos/` — 12 images, numbered in walkthrough order (`01-exterior.jpg` … `12-bunk-room.jpg`).

## Task
1. For each photo, call Higgsfield's image-to-video tool with a smooth 3D
   camera-move / parallax effect (subtle dolly or pan — avoid distortion).
2. Keep each clip 2-4 seconds.
3. Download/save all resulting clips.
4. Stitch the clips together in numbered order into a single combined video
   (crossfade or hard cut between clips).
5. Output one final video file.

See `TASK.md` for the full handoff notes.
