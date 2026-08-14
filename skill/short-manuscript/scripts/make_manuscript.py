#!/usr/bin/env python3
"""Build a timestamped manuscript for a vertical short.

Handles the arithmetic — beat boundaries, timecodes, fitting the content to
the runtime — so the writing effort goes into the hook and the captions.

Two input shapes, auto-detected:

  1. Generic spec (preferred for new subjects):
       --spec spec.json
     {
       "title": "Wee Nook — a Hobbit Hole",
       "subject": "McEwen, Tennessee",         // context line, optional
       "facts": {"rating": "4.98", "guests": "2"},  // optional, free-form
       "shots": [
         {"name": "Exterior", "media": "...", "caption": "...", "camera": "..."},
         {"name": "Kitchen"}
       ]
     }
     Per-shot "caption" and "camera" are optional overrides; anything absent
     is filled with a sensible default that you are expected to rewrite.

  2. Listing pipeline pair (for the Airbnb walkthrough project):
       --data report_data.json --shots shot_plan.json

Usage:
    python3 make_manuscript.py --spec spec.json \
        --out-md short.md --out-json short.json \
        [--duration 24] [--hook "..."] [--cta "..."] \
        [--hook-seconds 3] [--cta-seconds 3]
"""
import argparse
import json
from pathlib import Path

MIN_BEAT_SECONDS = 2.0

# Vertical framing loses the sides of a landscape source, so moves that
# travel along the frame's short axis (push in, tilt) survive the crop far
# better than pans do.
CAMERA_BY_KIND = {
    "exterior": "slow push in toward the entrance, slight tilt up",
    "outdoor": "low glide forward, gentle rise at the end",
    "living": "steady push in through the room",
    "kitchen": "glide forward along the counters",
    "dining": "push in over the table",
    "bedroom": "slow push in toward the bed",
    "bathroom": "gentle push in",
    "product": "slow orbit, tight on the detail",
    "default": "slow push in, subtle parallax",
}

KIND_KEYWORDS = [
    ("exterior", ("exterior", "facade", "front", "entrance", "street")),
    ("outdoor", ("patio", "backyard", "garden", "terrace", "balcony", "pool",
                 "outdoor", "yard", "deck", "roof")),
    ("living", ("living", "lounge", "stue", "sitting")),
    ("kitchen", ("kitchen", "køkken")),
    ("dining", ("dining", "spise")),
    ("bedroom", ("bedroom", "sove", "suite")),
    ("bathroom", ("bath", "bade", "shower", "wc")),
    ("product", ("product", "close-up", "closeup", "detail")),
]


def classify(name):
    low = (name or "").lower()
    for kind, words in KIND_KEYWORDS:
        if any(w in low for w in words):
            return kind
    return "default"


def tc(seconds):
    """M:SS.S — fine enough to cut against in an editor."""
    m, s = divmod(round(seconds, 1), 60)
    return f"{int(m)}:{s:04.1f}"


def load_inputs(args):
    """Return (meta, shots) from either input shape."""
    if args.spec:
        spec = json.loads(Path(args.spec).read_text())
        meta = {
            "title": spec.get("title"),
            "subject": spec.get("subject") or "",
            "facts": spec.get("facts") or {},
            "url": spec.get("url"),
        }
        shots = [
            {
                "name": s.get("name") or s.get("room"),
                "media": s.get("media") or s.get("photo_url"),
                "caption": s.get("caption"),
                "camera": s.get("camera"),
            }
            for s in (spec.get("shots") or [])
        ]
        return meta, shots

    data = json.loads(Path(args.data).read_text())
    raw = json.loads(Path(args.shots).read_text()).get("shots") or []
    facts = {
        k: data.get(k)
        for k in ("rating", "bedrooms", "beds", "baths", "guests")
        if data.get(k)
    }
    meta = {
        "title": data.get("title"),
        "subject": data.get("location") or "",
        "facts": facts,
        "url": data.get("listing_url") or data.get("source_url"),
    }
    shots = [
        {"name": s.get("room"), "media": s.get("photo_url"),
         "caption": None, "camera": None}
        for s in raw
    ]
    return meta, shots


def default_hook(meta):
    facts = meta["facts"]
    rating = str(facts.get("rating") or "")
    place = (meta["subject"] or "").split(",")[0].strip()
    if rating.replace(".", "").isdigit() and float(rating) >= 4.9:
        return f"{rating}★ — and you can actually book it"
    if facts.get("bedrooms") and place:
        return f"Inside a {facts['bedrooms']}-bedroom stay in {place}"
    if place:
        return f"Inside this place in {place}"
    return f"Inside {meta['title']}" if meta.get("title") else "Watch this"


def default_cta(meta):
    place = (meta["subject"] or "").split(",")[0].strip()
    return f"{place} · link in bio" if place else "Link in bio"


def caption_for(shot, meta, used):
    """Default on-screen label.

    Subjects often repeat a kind of space (two terraces, a patio and a yard).
    Reusing one preset across them makes the short read like a template, so a
    repeat falls back to the shot's own name.
    """
    if shot.get("caption"):
        caption = shot["caption"]
    else:
        facts = meta["facts"]
        kind = classify(shot["name"])
        guests, baths = facts.get("guests"), facts.get("baths")
        presets = {
            "exterior": "It looks like this from the road",
            "outdoor": "…and there's outside space too",
            "living": "Living room",
            "kitchen": "Full kitchen — not a kitchenette",
            "dining": "Room to actually sit down and eat",
            "bedroom": f"Sleeps {guests}" if guests else "The bedroom",
            "bathroom": (f"{baths} full bath" + ("s" if str(baths) != "1" else ""))
                        if baths else "The bathroom",
        }
        caption = presets.get(kind, shot["name"])
        if caption in used:
            caption = shot["name"]
    used.add(caption)
    return caption


def vo_for(caption):
    """Captions are written to be read, not spoken — strip the typographic
    shorthand a voice actor or TTS would stumble over."""
    spoken = (caption.replace(" · ", ". ").replace("…", "")
              .replace("★", " stars").replace("—", "—").strip())
    return spoken.rstrip(".") + "."


def build_beats(meta, shots, total, hook_text, cta_text, hook_s, cta_s):
    middle_budget = total - hook_s - cta_s
    if middle_budget <= 0:
        raise SystemExit(
            f"--duration {total:g}s leaves no room for content; "
            f"hook + CTA alone need {hook_s + cta_s:g}s"
        )
    max_middle = int(middle_budget // MIN_BEAT_SECONDS)
    if max_middle < 1:
        raise SystemExit(f"--duration {total:g}s is too short for any body beat")

    # The hook reuses the strongest shot, so the body draws from the rest.
    # Trim to what the runtime can actually hold rather than cramming.
    hero, rest = shots[0], shots[1:]
    middle = rest[:max_middle]
    beat_len = round(middle_budget / len(middle), 2) if middle else 0

    used = {hook_text}
    beats = []
    t = 0.0

    def add(role, shot, dur, caption):
        nonlocal t
        camera = shot.get("camera") or CAMERA_BY_KIND.get(
            classify(shot["name"]), CAMERA_BY_KIND["default"])
        beats.append({
            "n": len(beats) + 1,
            "role": role,
            "start": round(t, 2),
            "end": round(t + dur, 2),
            "duration": dur,
            "shot": shot["name"],
            "camera": camera if role != "cta" else "hold, very slow drift",
            "caption": caption,
            "vo": vo_for(caption),
            "media": shot.get("media"),
        })
        t += dur

    add("hook", hero, hook_s, hook_text)
    for shot in middle:
        add("body", shot, beat_len, caption_for(shot, meta, used))
    add("cta", middle[-1] if middle else hero, cta_s, cta_text)

    for b in beats:
        b["prompt"] = (
            f"Vertical 9:16 short-form shot: {b['camera']}, {b['shot'].lower()}. "
            "Smooth continuous motion, no cuts. Scene completely static: no "
            "people, nothing rearranged, no warping of geometry."
        )
    return beats


def render_markdown(meta, beats, total):
    title = meta.get("title") or "Untitled"
    lines = [
        f"# Short manuscript — {title}",
        "",
        f"**{meta['subject']}**  " if meta.get("subject") else "",
        f"Format 9:16 vertical · Runtime {total:g}s · {len(beats)} beats",
        "",
        "| # | In | Out | Dur | Shot | On-screen text |",
        "|---|----|-----|-----|------|----------------|",
    ]
    for b in beats:
        lines.append(
            f"| {b['n']} | {tc(b['start'])} | {tc(b['end'])} | {b['duration']:g}s "
            f"| {b['shot']} | {b['caption']} |"
        )

    lines += ["", "## Beats", ""]
    for b in beats:
        lines += [
            f"### {b['n']}. {tc(b['start'])}–{tc(b['end'])} · {b['role'].upper()} · {b['shot']}",
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
        "- Landscape sources lose their sides in a 9:16 crop — frame on what",
        "  sits centre and prefer push-in or tilt moves over pans.",
        "- Captions carry the video; most viewers watch muted. Keep them under",
        "  ~40 characters so they clear the platform's UI overlays.",
        "- The hook has roughly 1.5s to earn the scroll. If the strongest shot",
        "  is not first in the list, reorder before generating.",
        "",
    ]
    return "\n".join(l for l in lines if l is not None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", help="generic spec JSON (title/subject/facts/shots)")
    ap.add_argument("--data", help="listing report_data.json (with --shots)")
    ap.add_argument("--shots", help="listing shot_plan.json (with --data)")
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--duration", type=float, default=24.0)
    ap.add_argument("--hook-seconds", type=float, default=3.0)
    ap.add_argument("--cta-seconds", type=float, default=3.0)
    ap.add_argument("--hook", help="override the opening on-screen line")
    ap.add_argument("--cta", help="override the closing on-screen line")
    args = ap.parse_args()

    if not args.spec and not (args.data and args.shots):
        raise SystemExit("Provide --spec, or both --data and --shots")

    meta, shots = load_inputs(args)
    if not shots:
        raise SystemExit("No shots found in the input")
    if not all(s.get("name") for s in shots):
        raise SystemExit("Every shot needs a name")

    hook_text = args.hook or default_hook(meta)
    cta_text = args.cta or default_cta(meta)
    beats = build_beats(meta, shots, args.duration, hook_text, cta_text,
                        args.hook_seconds, args.cta_seconds)

    Path(args.out_json).write_text(json.dumps({
        "title": meta.get("title"),
        "subject": meta.get("subject"),
        "url": meta.get("url"),
        "format": "9:16",
        "runtime_seconds": args.duration,
        "beats": beats,
    }, indent=2) + "\n")
    Path(args.out_md).write_text(render_markdown(meta, beats, args.duration))
    print(f"Wrote {args.out_md} and {args.out_json} "
          f"({len(beats)} beats, {args.duration:g}s)")


if __name__ == "__main__":
    main()
