# higgenfield-3d-creator

creating video to airbnb

## Skills

### `auto-short`

End-to-end faceless Short factory. Say "make me a video" and it picks the topic
from live SEO research, writes the manuscript with `manu-writer`, generates the
finished vertical video through the `faceless-video` workflow, and returns
upload-ready title/description/hashtags/tags.

```
.claude/skills/auto-short/
├── SKILL.md                            # the five-stage pipeline
├── references/seo-topic-selection.md   # scoring rubric and search recipe
├── references/pipeline-handoff.md      # parameter lock for video generation
└── scripts/pick_topic.py               # deterministic topic ranking
```

Channel settings (niche, style preset, voice, already-published topics) live in
`channel.json` at the repo root, created on the first run.
