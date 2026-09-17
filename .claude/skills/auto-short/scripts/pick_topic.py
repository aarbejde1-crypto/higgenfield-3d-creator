#!/usr/bin/env python3
"""Rank candidate Short topics by weighted SEO signals and scaffold the run.

Input is a JSON file: either a bare list of candidates, or an object with a
"candidates" key (and optionally "niche" / "published_topics").

Each candidate:

    {
      "angle": "Why a stock can gap down 40% before the market opens",
      "keyword": "premarket gap down",
      "scores": {
        "demand": 4, "gap": 5, "hook_3s": 5, "payoff": 4,
        "rpm_band": 4, "evergreen": 4, "fit": 5, "risk": 5
      },
      "notes": {"gap": "three thin videos, none explains the mechanism"},
      "sources": ["https://..."]
    }

Every signal is 0-5.  "risk" is scored so that 5 means SAFE; it is subtracted,
so a risky topic must be outstanding everywhere else to survive.

Usage:
    python3 pick_topic.py candidates.json
    python3 pick_topic.py candidates.json --run-dir runs/
    python3 pick_topic.py candidates.json --top 3          # batch mode
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

# Weights are ordered on the premise that retention decides a Short's fate and
# winnability decides whether a topic is worth entering at all.  RPM only
# decides what a win is worth.  See references/seo-topic-selection.md.
WEIGHTS = {
    "hook_3s": 2.5,
    "gap": 2.0,
    "demand": 1.5,
    "fit": 1.5,
    "payoff": 1.5,
    "rpm_band": 1.0,
    "evergreen": 1.0,
    "risk": -2.0,
}

MAX_SCORE = 5
# The best possible total: every positive signal at 5, risk at 5 (fully safe,
# so its -2.0 * (5 - 5) penalty is zero).
BEST = sum(w * MAX_SCORE for k, w in WEIGHTS.items() if w > 0)


def slugify(text, maxlen=48):
    """Directory-safe slug, truncated on a word boundary so it stays readable."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(slug) > maxlen:
        slug = slug[:maxlen].rsplit("-", 1)[0]
    return slug.strip("-") or "untitled"


def validate(candidate, index):
    where = f"candidate {index}"
    angle = candidate.get("angle")
    if not angle:
        sys.exit(f"{where}: missing 'angle'")
    scores = candidate.get("scores")
    if not isinstance(scores, dict):
        sys.exit(f"{where} ({angle}): missing 'scores' object")
    missing = sorted(set(WEIGHTS) - set(scores))
    if missing:
        sys.exit(f"{where} ({angle}): missing signals {', '.join(missing)}")
    for signal, value in scores.items():
        if signal not in WEIGHTS:
            sys.exit(f"{where} ({angle}): unknown signal '{signal}'")
        if not isinstance(value, (int, float)) or not 0 <= value <= MAX_SCORE:
            sys.exit(f"{where} ({angle}): '{signal}' must be 0-{MAX_SCORE}, got {value!r}")


def score(candidate):
    """Weighted total, normalised to 0-100.

    Positive signals contribute weight * value.  'risk' contributes a penalty
    proportional to how far from safe it is, so a fully safe topic pays nothing
    and a maximally risky one loses 10 raw points.
    """
    scores = candidate["scores"]
    raw = sum(w * scores[k] for k, w in WEIGHTS.items() if w > 0)
    raw += WEIGHTS["risk"] * (MAX_SCORE - scores["risk"])
    return round(100 * raw / BEST, 1)


def deciding_signal(candidate, runner_up):
    """Which signal separated the winner from the next candidate.

    Useful because the one-line announcement should say *why* this topic won,
    and the honest answer is whichever weighted signal moved the most.
    """
    if runner_up is None:
        return None
    best = None
    for signal, weight in WEIGHTS.items():
        delta = weight * (candidate["scores"][signal] - runner_up["scores"][signal])
        if best is None or delta > best[1]:
            best = (signal, delta)
    return best[0] if best and best[1] > 0 else None


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("candidates", help="JSON file of candidate topics")
    parser.add_argument("--run-dir", help="create runs/<date>-<slug>/ under this directory")
    parser.add_argument("--top", type=int, default=1, help="how many winners to scaffold")
    parser.add_argument("--json", action="store_true", help="print the ranking as JSON")
    args = parser.parse_args()

    data = json.loads(Path(args.candidates).read_text())
    if isinstance(data, list):
        data = {"candidates": data}
    candidates = data.get("candidates") or []
    if not candidates:
        sys.exit("no candidates found — expected a list, or an object with a 'candidates' key")

    for i, candidate in enumerate(candidates, 1):
        validate(candidate, i)

    # Drop anything the channel has already covered.  Two Shorts on one keyword
    # split their own impressions, so a near-duplicate is worse than nothing.
    published = {slugify(t) for t in data.get("published_topics", [])}
    skipped = [c for c in candidates if slugify(c["angle"]) in published]
    candidates = [c for c in candidates if slugify(c["angle"]) not in published]
    if not candidates:
        sys.exit("every candidate duplicates an already-published topic")

    for candidate in candidates:
        candidate["total"] = score(candidate)
    ranked = sorted(candidates, key=lambda c: c["total"], reverse=True)

    winner = ranked[0]
    winner["deciding_signal"] = deciding_signal(winner, ranked[1] if len(ranked) > 1 else None)

    result = {
        "generated": dt.date.today().isoformat(),
        "niche": data.get("niche"),
        "weights": WEIGHTS,
        "skipped_as_published": [c["angle"] for c in skipped],
        "ranking": ranked,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{'#':>2}  {'score':>5}  angle")
        print("-" * 72)
        for i, c in enumerate(ranked, 1):
            print(f"{i:>2}  {c['total']:>5}  {c['angle']}")
        if skipped:
            print(f"\nskipped (already published): {', '.join(c['angle'] for c in skipped)}")
        print(f"\nWinner: {winner['angle']}")
        if winner.get("deciding_signal"):
            signal = winner["deciding_signal"]
            note = (winner.get("notes") or {}).get(signal)
            print(f"Decided on: {signal}" + (f" — {note}" if note else ""))

    for candidate in ranked[: args.top]:
        slug = slugify(candidate["angle"])
        if args.run_dir:
            run = Path(args.run_dir) / f"{dt.date.today().isoformat()}-{slug}"
            (run / "video").mkdir(parents=True, exist_ok=True)
            payload = dict(result, selected=candidate)
            (run / "topic-selection.json").write_text(json.dumps(payload, indent=2))
            print(f"\nRun directory: {run}")


if __name__ == "__main__":
    main()
