#!/usr/bin/env python3
"""Overlay a preview watermark onto a video: a large centered mark plus a
small mark in each corner, so a cropped screen-recording still carries a
visible mark. Meant for the free/preview copy sent to a homeowner before
they engage — the clean master stays unwatermarked for after.

Usage:
    python3 watermark.py --in walkthrough.mp4 --out walkthrough_preview.mp4 \
        --text "PREVIEW - WhatsApp +45 12 34 56 78"
"""
import argparse
import subprocess

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def escape_text(text):
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--crf", type=int, default=20,
                    help="x264 quality; raise it for a smaller file (heavy "
                         "foliage/detail footage encodes large at low crf)")
    args = ap.parse_args()

    t = escape_text(args.text)
    common = f"fontfile={FONT}:fontcolor=white@0.55:shadowcolor=black@0.6:shadowx=2:shadowy=2"

    filters = [
        f"drawtext=text='{t}':{common}:fontsize=34:x=(w-text_w)/2:y=(h-text_h)/2",
        f"drawtext=text='{t}':{common}:fontsize=16:x=16:y=16",
        f"drawtext=text='{t}':{common}:fontsize=16:x=w-text_w-16:y=16",
        f"drawtext=text='{t}':{common}:fontsize=16:x=16:y=h-text_h-16",
        f"drawtext=text='{t}':{common}:fontsize=16:x=w-text_w-16:y=h-text_h-16",
    ]
    filter_complex = ",".join(filters)

    cmd = [
        "ffmpeg", "-y", "-i", args.inp,
        "-vf", filter_complex,
        "-c:v", "libx264", "-crf", str(args.crf), "-preset", "slow",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        args.out,
    ]
    subprocess.run(cmd, check=True)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
