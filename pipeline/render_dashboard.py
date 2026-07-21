#!/usr/bin/env python3
"""Render the private lead-pipeline dashboard from leads/leads.json.

Usage:
    python3 render_dashboard.py --leads leads/leads.json --out dashboard.html

Re-run and republish (via the Artifact tool, same file path) any time
leads.json changes -- this is a static snapshot, not a live-updating page.
"""
import argparse
import html
import json
from pathlib import Path

STATUS_META = {
    "new":          {"label": "New",             "class": "st-new"},
    "generating":   {"label": "Generating",       "class": "st-generating"},
    "video_only":   {"label": "Video only",       "class": "st-video-only"},
    "ready_to_send":{"label": "Ready to send",    "class": "st-ready"},
    "sent":         {"label": "Sent",             "class": "st-sent"},
    "replied":      {"label": "Replied",          "class": "st-replied"},
    "closed":       {"label": "Closed",           "class": "st-closed"},
}

RAW_BASE = "https://raw.githubusercontent.com/{repo}/{branch}/{path}"
PAGE_BASE = "https://rawcdn.githack.com/{repo}/{branch}/{path}"


def esc(v):
    return html.escape(str(v)) if v is not None else ""


def asset_url(repo, branch, path, is_page):
    base = PAGE_BASE if is_page else RAW_BASE
    return base.format(repo=repo, branch=branch, path=path)


def stat_chip(label, value):
    if not value:
        return ""
    return f'<span class="chip"><b>{esc(value)}</b> {esc(label)}</span>'


def asset_link(label, url):
    if not url:
        return f'<span class="link disabled">{esc(label)}</span>'
    return f'<a class="link" href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>'


def render_card(lead, repo, branch):
    meta = STATUS_META.get(lead["status"], {"label": lead["status"], "class": "st-new"})
    stats = lead.get("stats", {})
    assets = lead.get("assets", {})

    chips = "".join([
        stat_chip("bd", stats.get("bedrooms")),
        stat_chip("ba", stats.get("baths")),
        stat_chip("beds", stats.get("beds")),
        stat_chip("guests", stats.get("guests")),
    ])
    rating = stats.get("rating")
    rating_chip = f'<span class="chip rating">{esc(rating)}{"" if rating == "New" else " ★"}</span>' if rating else ""

    hero = lead.get("hero_image")
    thumb = f'<div class="thumb" style="background-image:url(\'{esc(hero)}\')"></div>' if hero else '<div class="thumb thumb-empty">No photo</div>'

    links = []
    if assets.get("video_preview"):
        links.append(asset_link("Preview video", asset_url(repo, branch, assets["video_preview"], False)))
    elif assets.get("video"):
        links.append(asset_link("Video", asset_url(repo, branch, assets["video"], False)))
    if assets.get("video") and assets.get("video_preview"):
        links.append(asset_link("Clean video", asset_url(repo, branch, assets["video"], False)))
    if assets.get("report_preview"):
        links.append(asset_link("Report", asset_url(repo, branch, assets["report_preview"], True)))
    elif assets.get("report"):
        links.append(asset_link("Report", asset_url(repo, branch, assets["report"], True)))
    if assets.get("outreach_message"):
        links.append(asset_link("Message", asset_url(repo, branch, assets["outreach_message"], False)))
    links_html = "".join(links) or '<span class="link disabled">No assets yet</span>'

    return f"""
    <article class="card">
      {thumb}
      <div class="card-body">
        <div class="card-top">
          <div>
            <h2>{esc(lead["title"])}</h2>
            <p class="loc">{esc(lead["location"])}</p>
          </div>
          <span class="pill {meta['class']}">{esc(meta['label'])}</span>
        </div>
        <div class="chips">{chips}{rating_chip}</div>
        <p class="note">{esc(lead.get("status_note") or "")}</p>
        <div class="links">{links_html}</div>
        <p class="updated">Updated {esc(lead.get("updated_at") or "—")} &middot; <a class="source" href="{esc(lead["source_url"])}" target="_blank" rel="noopener">original listing ↗</a></p>
      </div>
    </article>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leads", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.loads(Path(args.leads).read_text())
    repo, branch = data["repo"], data["branch"]
    leads = data["leads"]

    counts = {}
    for lead in leads:
        counts[lead["status"]] = counts.get(lead["status"], 0) + 1
    summary_html = "".join(
        f'<div class="summary-item"><span class="summary-count">{counts.get(key, 0)}</span><span class="summary-label">{meta["label"]}</span></div>'
        for key, meta in STATUS_META.items()
        if counts.get(key)
    )

    cards_html = "".join(render_card(lead, repo, branch) for lead in leads)

    html_out = TEMPLATE.replace("<!--SUMMARY-->", summary_html).replace("<!--CARDS-->", cards_html).replace(
        "<!--COUNT-->", str(len(leads))
    )
    Path(args.out).write_text(html_out)
    print(f"Wrote {args.out} ({len(leads)} leads)")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lead Pipeline</title>
<style>
  :root {
    --ink: #1b211f;
    --paper: #f1efe7;
    --paper-raised: #ffffff;
    --border: rgba(27,33,31,0.12);
    --muted: #6b7269;
    --accent: #0e6e63;
    --accent-soft: #dbeeea;
    --st-new: #5b6b8c;         --st-new-bg: rgba(91,107,140,0.14);
    --st-generating: #b8892b;  --st-generating-bg: rgba(184,137,43,0.16);
    --st-video-only: #8a7f5a;  --st-video-only-bg: rgba(138,127,90,0.16);
    --st-ready: #0e6e63;       --st-ready-bg: rgba(14,110,99,0.14);
    --st-sent: #7a5cb0;        --st-sent-bg: rgba(122,92,176,0.14);
    --st-replied: #3f8f5f;     --st-replied-bg: rgba(63,143,95,0.14);
    --st-closed: #8a8577;      --st-closed-bg: rgba(138,133,119,0.16);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --ink: #eceae3;
      --paper: #14171a;
      --paper-raised: #1c2023;
      --border: rgba(236,234,227,0.12);
      --muted: #9aa39c;
      --accent: #35a896;
      --accent-soft: rgba(53,168,150,0.16);
    }
  }
  :root[data-theme="dark"] {
    --ink: #eceae3; --paper: #14171a; --paper-raised: #1c2023;
    --border: rgba(236,234,227,0.12); --muted: #9aa39c;
    --accent: #35a896; --accent-soft: rgba(53,168,150,0.16);
  }
  :root[data-theme="light"] {
    --ink: #1b211f; --paper: #f1efe7; --paper-raised: #ffffff;
    --border: rgba(27,33,31,0.12); --muted: #6b7269;
    --accent: #0e6e63; --accent-soft: #dbeeea;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--paper); color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.5;
  }
  .mono { font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; font-variant-numeric: tabular-nums; }
  .wrap { max-width: 880px; margin: 0 auto; padding: 32px 20px 64px; }
  header { margin-bottom: 20px; }
  .eyebrow { text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.72rem; color: var(--muted); font-weight: 600; }
  h1 { font-size: 1.6rem; margin: 4px 0 0; text-wrap: balance; }
  .summary {
    display: flex; gap: 10px; flex-wrap: wrap; margin: 20px 0 28px;
  }
  .summary-item {
    background: var(--paper-raised); border: 1px solid var(--border); border-radius: 10px;
    padding: 10px 14px; min-width: 84px;
  }
  .summary-count { display: block; font-size: 1.3rem; font-weight: 700; font-family: ui-monospace, Menlo, Consolas, monospace; }
  .summary-label { display: block; font-size: 0.72rem; color: var(--muted); margin-top: 2px; }
  .cards { display: flex; flex-direction: column; gap: 14px; }
  .card {
    display: flex; gap: 16px; background: var(--paper-raised); border: 1px solid var(--border);
    border-radius: 14px; padding: 16px; overflow: hidden;
  }
  .thumb {
    flex: 0 0 120px; height: 120px; border-radius: 10px; background-size: cover; background-position: center;
    background-color: var(--accent-soft);
  }
  .thumb-empty { display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: var(--muted); }
  .card-body { flex: 1; min-width: 0; }
  .card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
  .card-top h2 { font-size: 1.05rem; margin: 0; text-wrap: balance; }
  .loc { margin: 2px 0 0; font-size: 0.85rem; color: var(--muted); }
  .pill {
    font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 999px; white-space: nowrap;
  }
  .st-new { color: var(--st-new); background: var(--st-new-bg); }
  .st-generating { color: var(--st-generating); background: var(--st-generating-bg); }
  .st-video-only { color: var(--st-video-only); background: var(--st-video-only-bg); }
  .st-ready { color: var(--st-ready); background: var(--st-ready-bg); }
  .st-sent { color: var(--st-sent); background: var(--st-sent-bg); }
  .st-replied { color: var(--st-replied); background: var(--st-replied-bg); }
  .st-closed { color: var(--st-closed); background: var(--st-closed-bg); }
  .chips { display: flex; gap: 6px; flex-wrap: wrap; margin: 10px 0 0; }
  .chip {
    font-size: 0.78rem; background: var(--paper); border: 1px solid var(--border); border-radius: 7px;
    padding: 3px 8px; font-family: ui-monospace, Menlo, Consolas, monospace;
  }
  .chip b { font-weight: 700; }
  .chip.rating { color: var(--accent); border-color: var(--accent-soft); }
  .note { font-size: 0.85rem; color: var(--muted); margin: 10px 0 0; }
  .links { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0 0; }
  .link {
    font-size: 0.8rem; font-weight: 600; color: var(--accent); text-decoration: none;
    border: 1px solid var(--accent-soft); background: var(--accent-soft); border-radius: 7px; padding: 5px 10px;
  }
  .link:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .link.disabled { color: var(--muted); background: transparent; border-style: dashed; }
  .updated { font-size: 0.75rem; color: var(--muted); margin: 12px 0 0; }
  .source { color: var(--muted); }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="eyebrow">Private &middot; <!--COUNT--> listings tracked</div>
    <h1>Lead Pipeline</h1>
  </header>
  <div class="summary"><!--SUMMARY--></div>
  <div class="cards"><!--CARDS--></div>
</div>
</body>
</html>
"""

if __name__ == "__main__":
    main()
