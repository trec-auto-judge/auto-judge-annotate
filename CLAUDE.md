# CLAUDE.md - Nugget Annotator

## Project Overview

Browser-based annotation interface for creating and quality-checking nuggets to evaluate RAG system outputs. Generates standalone HTML files with embedded data and JavaScript.

## Documentation Sync Checklist

**When adding or changing user-facing features, update these in order:**

1. [ ] **USER_GUIDE.md** - The single source of truth (standalone markdown)
2. [ ] **template_html.py** - Quick Start Guide in help-modal (~lines 120-175)
3. [ ] **template_html.py** - Full Guide in guide-modal (~lines 185+)
4. [ ] **template_html.py** - Update version marker in help-footer (e.g., `v1.1 — 2026-07-01`)

The Quick Start Guide is a condensed summary. The Full Guide should mirror USER_GUIDE.md content rendered as HTML.

### Why This Matters

Documentation drift is inevitable without explicit reminders. This checklist ensures:
- Users always see current feature documentation
- The version marker signals when docs were last updated
- Both Claude and human developers have a clear update path

## Key Files

| File | Purpose |
|------|---------|
| `src/autojudge_annotate/template.py` | Main template assembly |
| `src/autojudge_annotate/template_html.py` | HTML structure, help modals, guide content |
| `src/autojudge_annotate/template_css.py` | All CSS styling |
| `src/autojudge_annotate/template_js_*.py` | JavaScript modules (state, rendering, LLM, etc.) |
| `USER_GUIDE.md` | Standalone user documentation |

## Development Commands

```bash
# Install
pip install -e .

# Generate HTML from test data
python -m autojudge_annotate generate --input data.jsonl --output output.html

# Run tests
pytest tests/
```

## UI Architecture

Three-phase workflow:
- **Creation**: Select text spans, canonicalize into nuggets, check impact
- **QC**: Adjust weights, enable/disable nuggets, solo mode
- **Observe**: Cross-query rankings, overview metrics

Three-column layout:
- **Nav Panel** (left): Query/report selection
- **Middle Panel**: Source text (Creation) or Ranking table (QC/Observe)
- **Nuggets Panel** (right): Draft card, nugget list, or overview stats