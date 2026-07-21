#!/usr/bin/env python3
"""Fill report_template.html with listing data + generated video into a
single shareable one-pager.

Usage:
    python3 render_report.py --data listing.json --video VIDEO_URL \
        --out report.html [--template report_template.html]

listing.json is the scrape_listing.js output, optionally augmented with:
  - "pitch_bullets": [str, ...]   (defaults provided if omitted)
  - "listing_url": str            (defaults to source_url)
"""
import argparse
import html
import json
import urllib.parse
from pathlib import Path

DEFAULT_PITCH = [
    "See the whole home in motion, not just static photos — bookers picture themselves there faster.",
    "Video listings stand out in Airbnb search results and share better on social media.",
    "Built directly from your existing listing photos — no reshoot needed.",
]


def esc(v):
    return html.escape(str(v)) if v is not None else ""


def first_number(text, fallback="—"):
    if not text:
        return fallback
    digits = "".join(c for c in text if c.isdigit() or c == ".")
    return digits or fallback


def rating_display(text, fallback="—"):
    """Ratings are usually numeric ("4.78") but a brand-new listing may pass
    a label like "New" instead — pass those through as-is rather than
    stripping them down to nothing."""
    if not text:
        return fallback
    if str(text).replace(".", "").isdigit():
        return first_number(text, fallback)
    return str(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--video", required=True, help="URL or relative path to the final video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default=str(Path(__file__).parent / "report_template.html"))
    ap.add_argument("--max-photos", type=int, default=12)
    args = ap.parse_args()

    data = json.loads(Path(args.data).read_text())
    template = Path(args.template).read_text()

    title = data.get("title") or "Listing walkthrough"
    listing_url = data.get("listing_url") or data.get("source_url") or ""
    hero = data.get("heroImage") or (data.get("photos") or [None])[0] or ""

    share_body = f"Check out the new video tour for {title}: {args.video}"
    share_text_encoded = urllib.parse.quote(share_body)

    replacements = {
        "[[TITLE]]": esc(title),
        "[[LOCATION]]": esc(data.get("location") or ""),
        "[[RATING]]": esc(rating_display(data.get("rating"))),
        "[[RATING_LABEL]]": "listing" if rating_display(data.get("rating")) == "New" else "★ rating",
        "[[BEDROOMS]]": esc(first_number(data.get("bedrooms"))),
        "[[BEDS]]": esc(first_number(data.get("beds"))),
        "[[BATHS]]": esc(first_number(data.get("baths"))),
        "[[GUESTS]]": esc(first_number(data.get("guests"))),
        "[[HERO_IMAGE]]": esc(hero),
        "[[VIDEO_URL]]": esc(args.video),
        "[[LISTING_URL]]": esc(listing_url),
        "[[SHARE_TEXT]]": share_text_encoded,
    }

    out_html = template
    for token, value in replacements.items():
        out_html = out_html.replace(token, value)

    bullets = data.get("pitch_bullets") or DEFAULT_PITCH
    bullets_html = "\n".join(f"        <li>{esc(b)}</li>" for b in bullets)
    out_html = out_html.replace("<!--PITCH_BULLETS-->", bullets_html)

    photos = (data.get("photos") or [])[: args.max_photos]
    photos_html = "\n".join(
        f'      <img src="{esc(p)}" alt="listing photo" loading="lazy">' for p in photos
    )
    out_html = out_html.replace("<!--PHOTOS-->", photos_html)

    Path(args.out).write_text(out_html)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
