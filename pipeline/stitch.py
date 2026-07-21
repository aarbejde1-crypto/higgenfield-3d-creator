#!/usr/bin/env python3
"""Stitch an ordered list of video clips into one video with crossfades.

Usage:
    python3 stitch.py --clips-dir DIR --manifest ORDER.txt --out OUT.mp4 \
        [--fade 0.5] [--width 1280] [--height 720] [--crf 18]

ORDER.txt: one clip filename (relative to --clips-dir) per line, in the
order they should appear. Clip durations are read per-file via ffprobe,
so clips don't need to be the same length.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips-dir", required=True)
    ap.add_argument("--manifest", required=True, help="text file, one clip filename per line, in order")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fade", type=float, default=0.5)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--crf", type=int, default=18)
    args = ap.parse_args()

    clips_dir = Path(args.clips_dir)
    names = [l.strip() for l in Path(args.manifest).read_text().splitlines() if l.strip()]
    if len(names) < 2:
        sys.exit("Need at least 2 clips to stitch")

    paths = [clips_dir / n for n in names]
    for p in paths:
        if not p.exists():
            sys.exit(f"Missing clip: {p}")

    durations = [probe_duration(p) for p in paths]

    inputs = []
    for p in paths:
        inputs += ["-i", str(p)]

    filters = []
    for i in range(len(paths)):
        filters.append(
            f"[{i}:v]scale={args.width}:{round(args.height*16/9)}:flags=lanczos,"
            f"crop={args.width}:{args.height},setsar=1,fps=24,format=yuv420p[v{i}]"
        )

    prev = "v0"
    cumulative = durations[0]
    for k in range(1, len(paths)):
        offset = round(cumulative - args.fade, 4)
        out_label = f"x{k}" if k < len(paths) - 1 else "vout"
        filters.append(
            f"[{prev}][v{k}]xfade=transition=fade:duration={args.fade}:offset={offset}[{out_label}]"
        )
        prev = out_label
        cumulative += durations[k] - args.fade

    filter_complex = ";".join(filters)

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", f"[{prev}]", "-an",
        "-c:v", "libx264", "-crf", str(args.crf), "-preset", "slow",
        "-movflags", "+faststart",
        args.out,
    ]
    subprocess.run(cmd, check=True)
    print(f"Wrote {args.out} ({round(cumulative, 2)}s)")


if __name__ == "__main__":
    main()
