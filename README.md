# Autojudge Annotate

A tool for human annotation of RAG report quality. Generates a self-contained HTML file that annotators open in a browser — no server required.

Annotators highlight relevant passages, rate report quality, and add comments. All work is auto-saved to the browser's localStorage and can be exported as JSONL.

## Installation

```bash
uv pip install ./auto-judge-annotate
```

Requires `autojudge-base` and `click`.

## Usage

```bash
autojudge-annotate \
    --rag-responses path/to/runs/ \
    --rag-topics path/to/topics.jsonl \
    --output annotator.html \
    --dataset my-dataset \
    --show-documents
```

Then open `annotator.html` in a browser.

### Options

| Flag | Description |
|------|-------------|
| `--rag-responses` | Directory containing report files (any extension, JSONL format) |
| `--rag-topics` | JSONL file with evaluation topics/requests |
| `--output` | Output HTML file path |
| `--dataset` | Freetext label included in annotation output |
| `--show-documents` | Enable citation document popups (increases file size) |
| `--topic ID` | Filter to specific topics (repeatable) |

### Filtering topics

For large datasets, pass only the topics you need:

```bash
autojudge-annotate \
    --rag-responses runs/ \
    --rag-topics topics.jsonl \
    --output annotator.html \
    --dataset my-dataset \
    --topic 1101 --topic 1102 --topic 1103
```

## Annotation workflow

1. Enter your username (persists across sessions)
2. Select a topic from the sidebar, then a run
3. Read the request (title, problem statement, background) and the report
4. Highlight relevant passages by selecting text with the mouse
5. Choose a rating: Perfect, Mostly Good, So-so, Bad, or Not rated
6. Add optional comments
7. Navigate between topics/runs freely — all state is preserved
8. Click **Download JSONL** to export annotations

### Features

- **Auto-save**: every change is saved to localStorage immediately
- **Span splitting**: selections crossing sentence boundaries are split into per-sentence subspans with `sentence_idx`
- **Citation popups**: click `[DocId]` markers to view source documents (when `--show-documents` is enabled)
- **Progress tracking**: sidebar shows checkmarks on annotated runs and completion counts per topic
- **Clear all**: small button at the bottom of the sidebar to reset all annotations (with confirmation)

## Output format

Each annotation is a JSON line:

```json
{
  "dataset": "my-dataset",
  "request_id": "1101",
  "run_id": "run1",
  "team_id": "teamA",
  "topic_id": "1101",
  "username": "alice",
  "rating": "Mostly Good",
  "comment": "Good coverage but missing key detail",
  "spans": [
    {"start": 0, "end": 45, "text": "First relevant passage text here", "sentence_idx": 0},
    {"start": 46, "end": 120, "text": "Second passage from next sentence", "sentence_idx": 1}
  ],
  "report": { ... }
}
```