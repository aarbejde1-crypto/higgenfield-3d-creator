#!/usr/bin/env python3
"""Fill outreach_message_template.txt with listing + report details.

Usage:
    python3 render_outreach.py --data listing.json --report-url URL \
        --whatsapp "+4512345678" --your-name "Alex" --detail "..." --out message.txt
"""
import argparse
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-title", required=True, help="listing title")
    ap.add_argument("--location", default="")
    ap.add_argument("--detail", required=True, help="one specific, genuine detail about the listing")
    ap.add_argument("--report-url", required=True)
    ap.add_argument("--whatsapp", required=True, help="wa.me link or number")
    ap.add_argument("--your-name", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument(
        "--template",
        default=str(Path(__file__).parent / "outreach_message_template.txt"),
    )
    args = ap.parse_args()

    template = Path(args.template).read_text()
    message = template.split("\n---\n")[0].strip()

    whatsapp = args.whatsapp
    if not whatsapp.startswith("http"):
        digits = "".join(c for c in whatsapp if c.isdigit())
        whatsapp = f"https://wa.me/{digits}"

    message = (
        message.replace("{{TITLE}}", args.data_title)
        .replace("{{LOCATION}}", args.location)
        .replace("{{DETAIL}}", args.detail)
        .replace("{{REPORT_URL}}", args.report_url)
        .replace("{{WHATSAPP_LINK}}", whatsapp)
        .replace("{{YOUR_NAME}}", args.your_name)
    )

    Path(args.out).write_text(message + "\n")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
