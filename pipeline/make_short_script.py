#!/usr/bin/env python3
"""Build a timestamped manuscript for a vertical short from a listing.

Produces two files from the same beat plan:
  - <name>.json  machine-readable beats (drives clip generation)
  - <name>.md    the manuscript: timecode table + per-beat shot/caption/prompt

Usage:
    python3 make_short_script.py \
        --data listings/<slug>/report_data.json \
        --shots listings/<slug>/shot_plan.json \
        --out-json listings/<slug>/short_script.json \
        --out-md   listings/<slug>/short_script.md \
        [--duration 24] [--hook "..."] [--cta "..."]

Shorts are watched muted and thumb-scrolled, so the plan front-loads the
most striking space and carries the message in on-screen text; the
voiceover line per beat is optional and written to match the caption.
"""
import argparse
import json
from pathlib import Path

# Short-form pacing: a hard hook, quick middle beats, a closing card.
HOOK_SECONDS = 3.0
CTA_SECONDS = 3.0
MIN_BEAT_SECONDS = 2.0

# Camera moves per space type. Vertical framing favours moves that travel
# up/down or push in, since a 9:16 crop of a landscape photo loses the sides.
CAMERA_BY_KIND = {
    "exterior": "slow push in toward the entrance, slight tilt up",
    "outdoor": "low glide forward, gentle rise at the end",
    "living": "steady push in through the room",
    "kitchen": "glide forward along the counters",
    "dining": "push in over the table",
    "bedroom": "slow push in toward the bed",
    "bathroom": "gentle push in",
    "default": "slow push in, subtle parallax",
}

KIND_KEYWORDS = [
    ("exterior", ("exterior", "facade", "front", "entrance")),
    ("outdoor", ("patio", "backyard", "garden", "terrace", "balcony", "pool", "outdoor", "yard")),
    ("living", ("living", "lounge", "stue")),
    ("kitchen", ("kitchen", "køkken")),
    ("dining", ("dining", "spise")),
    ("bedroom", ("bedroom", "sove")),
    ("bathroom", ("bath", "bade", "shower")),
]


def classify(room_name):
    low = (room_name or "").lower()
    for kind, words in KIND_KEYWORDS:
        if any(w in low for w in words):
            return kind
    return "default"


def tc(seconds):
    """Format seconds as M:SS.s — fine-grained enough to cut against."""
    m, s = divmod(round(seconds, 1), 60)
    return f"{int(m)}:{s:04.1f}"


def default_hook(data):
    rating = str(data.get("rating") or "")
    beds = data.get("bedrooms")
    loc = (data.get("location") or "").split(",")[0].strip()
    if rating and rating.replace(".", "").isdigit() and float(rating) >= 4.9:
        return f"{rating}★ — and you can actually rent it"
    if beds and loc:
        return f"Inside a {beds}-bedroom stay in {loc}"
    return f"Inside this stay in {loc}" if loc else "Inside this stay"


def default_cta(data):
    loc = (data.get("location") or "").split(",")[0].strip()
    return f"{loc} · link in bio" if loc else "Link in bio"


def caption_for(room_name, kind, data, used):
    """Short on-screen label. Deliberately plain — the manuscript is a draft
    to edit, and a specific beat beats a clever-but-wrong line.

    Listings often have several spaces of one kind (two terraces, a patio and
    a backyard). Reusing one preset across them makes the short read like a
    template, so a repeat falls back to the space's own name.
    """
    guests = data.get("guests")
    baths = data.get("baths")
    presets = {
        "exterior": "It looks like this from the road",
        "outdoor": "…and there's outside space too",
        "living": "Living room",
        "kitchen": "Full kitchen — not a kitchenette",
        "dining": "Room to actually sit down and eat",
        "bedroom": f"Sleeps {guests}" if guests else "The bedroom",
        "bathroom": f"{baths} full bath" + ("s" if str(baths) not in ("1", None) else ""),
    }
    caption = presets.get(kind, room_name)
    if caption in used:
        caption = room_name
    used.add(caption)
    return caption


def vo_for(caption):
    """Captions are written to be read, not spoken — strip the typographic
    separators that a voice actor or TTS would stumble over."""
    spoken = caption.replace(" · ", ". ").replace("…", "").replace("★", " stars").strip()
    return spoken.rstrip(".") + "."


def build_beats(data, shots, total_seconds, hook_text, cta_text):
    middle_budget = total_seconds - HOOK_SECONDS - CTA_SECONDS
    if middle_budget <= 0:
        raise SystemExit(
            f"--duration {total_seconds}s leaves no room for content; "
            f"hook+CTA alone need {HOOK_SECONDS + CTA_SECONDS}s"
        )

    max_middle = int(middle_budget // MIN_BEAT_SECONDS)
    if max_middle < 1:
        raise SystemExit(f"--duration {total_seconds}s is too short for any room beat")

    # Beat 1 is the hook and reuses the first shot, so the middle draws from
    # the rest. Trim to what the runtime can hold rather than cramming.
    hero, rest = shots[0], shots[1:]
    middle = rest[:max_middle]
    beat_len = round(middle_budget / len(middle), 2) if middle else 0

    beats = []
    t = 0.0
    used_captions = {hook_text}

    hero_kind = classify(hero.get("room"))
    beats.append({
        "n": 1,
        "role": "hook",
        "start": 0.0,
        "end": HOOK_SECONDS,
        "duration": HOOK_SECONDS,
        "space": hero.get("room"),
        "camera": CAMERA_BY_KIND.get(hero_kind, CAMERA_BY_KIND["default"]),
        "caption": hook_text,
        "vo": vo_for(hook_text),
        "photo_url": hero.get("photo_url"),
    })
    t += HOOK_SECONDS

    for i, shot in enumerate(middle, start=2):
        kind = classify(shot.get("room"))
        cap = caption_for(shot.get("room"), kind, data, used_captions)
        beats.append({
            "n": i,
            "role": "body",
            "start": round(t, 2),
            "end": round(t + beat_len, 2),
            "duration": beat_len,
            "space": shot.get("room"),
            "camera": CAMERA_BY_KIND.get(kind, CAMERA_BY_KIND["default"]),
            "caption": cap,
            "vo": vo_for(cap),
            "photo_url": shot.get("photo_url"),
        })
        t += beat_len

    last = middle[-1] if middle else hero
    beats.append({
        "n": len(beats) + 1,
        "role": "cta",
        "start": round(t, 2),
        "end": round(t + CTA_SECONDS, 2),
        "duration": CTA_SECONDS,
        "space": last.get("room"),
        "camera": "hold, very slow drift",
        "caption": cta_text,
        "vo": vo_for(cta_text),
        "photo_url": last.get("photo_url"),
    })

    for b in beats:
        b["prompt"] = (
            f"Vertical short-form real-estate shot: {b['camera']}, "
            f"{b['space'].lower()}. Smooth continuous motion, no cuts. "
            "Scene completely static: no people, furniture and decor unchanged, "
            "no warping of walls or geometry."
        )
    return beats


def render_markdown(data, beats, total_seconds):
    title = data.get("title") or "Listing"
    loc = data.get("location") or ""
    lines = [
        f"# Short manuscript — {title}",
        "",
        f"**{loc}**  ",
        f"Format 9:16 vertical · Runtime {total_seconds:g}s · {len(beats)} beats",
        "",
        "| # | In | Out | Dur | Space | On-screen text |",
        "|---|----|-----|-----|-------|----------------|",
    ]
    for b in beats:
        lines.append(
            f"| {b['n']} | {tc(b['start'])} | {tc(b['end'])} | {b['duration']:g}s | "
            f"{b['space']} | {b['caption']} |"
        )

    lines += ["", "## Beats", ""]
    for b in beats:
        lines += [
            f"### {b['n']}. {tc(b['start'])}–{tc(b['end'])} · {b['role'].upper()} · {b['space']}",
            "",
            f"- **On-screen text:** {b['caption']}",
            f"- **Voiceover:** {b['vo']}",
            f"- **Camera:** {b['camera']}",
            f"- **Generation prompt:** {b['prompt']}",
            "",
        ]

    lines += [
        "## Production notes",
        "",
        "- Source photos are landscape; a 9:16 crop loses the sides, so frame",
        "  each shot on what sits in the centre and prefer push-in or tilt",
        "  moves over pans.",
        "- Captions carry the video — most viewers watch muted. Keep them",
        "  under ~40 characters so they clear the platform's UI overlays.",
        "- The hook beat has ~1.5s to earn the scroll; if the strongest space",
        "  is not the first one in the shot plan, reorder before generating.",
        "",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="report_data.json for the listing")
    ap.add_argument("--shots", required=True, help="shot_plan.json (ordered spaces + photos)")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--duration", type=float, default=24.0, help="total runtime in seconds")
    ap.add_argument("--hook", help="override the opening on-screen line")
    ap.add_argument("--cta", help="override the closing on-screen line")
    args = ap.parse_args()

    data = json.loads(Path(args.data).read_text())
    shots = json.loads(Path(args.shots).read_text()).get("shots") or []
    if not shots:
        raise SystemExit(f"No shots found in {args.shots}")

    hook_text = args.hook or default_hook(data)
    cta_text = args.cta or default_cta(data)
    beats = build_beats(data, shots, args.duration, hook_text, cta_text)

    Path(args.out_json).write_text(json.dumps({
        "title": data.get("title"),
        "location": data.get("location"),
        "listing_url": data.get("listing_url") or data.get("source_url"),
        "format": "9:16",
        "runtime_seconds": args.duration,
        "beats": beats,
    }, indent=2) + "\n")

    Path(args.out_md).write_text(render_markdown(data, beats, args.duration))
    print(f"Wrote {args.out_json} and {args.out_md} ({len(beats)} beats, {args.duration:g}s)")


if __name__ == "__main__":
    main()
