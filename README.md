# Autojudge Annotate

A tool for human annotation of RAG report quality. Generates a self-contained HTML file that annotators open in a browser — no server required.

Annotators highlight relevant passages, rate report quality, and add comments. All work is auto-saved to the browser's localStorage and can be exported as JSONL. 

Optional Supabase integration enables real-time cloud sync across annotators.

## Installation

```bash
uv pip install ./auto-judge-annotate
```

Requires `autojudge-base` and `click`.

## Usage

```bash
autojudge-annotate generate \
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
| `--supabase-url` | Supabase project URL for cloud sync (optional) |
| `--supabase-anon-key` | Supabase anon key for cloud sync (optional) |

### Filtering topics

For large datasets, pass only the topics you need:

```bash
autojudge-annotate generate \
    --rag-responses runs/ \
    --rag-topics topics.jsonl \
    --output annotator.html \
    --dataset my-dataset \
    --topic 1101 --topic 1102 --topic 1103
```

## Supabase setup (optional)

Supabase enables cloud sync so multiple annotators can work on the same dataset and annotations are persisted server-side.

### 1. Create the database table

Run `autojudge-annotate init-db` to print the SQL, then paste it into the Supabase dashboard (SQL Editor > New query > Run):

```bash
autojudge-annotate init-db
```

Verify by checking Table Editor > `annotations_current` in the Supabase dashboard.

### 2. Generate HTML with Supabase credentials

Find your project URL and anon key in the Supabase dashboard under Settings > API.

```bash
autojudge-annotate generate \
    --rag-responses runs/ \
    --rag-topics topics.jsonl \
    --output annotator.html \
    --dataset my-dataset \
    --supabase-url https://yourproject.supabase.co \
    --supabase-anon-key your-anon-key
```

### 3. Sync modes

The annotation interface has a sync mode toggle in the top bar:

- **Online**: annotations are automatically uploaded to Supabase after each edit (5s throttle). A status indicator shows sync state: grey (idle), yellowish-green (pending), yellow (uploading), green (synced), red (error).
- **Offline**: annotations are saved to localStorage only. Use the "Sync to Server" button to upload manually when ready.

Switching from offline to online immediately uploads all annotations. On sync errors, a dialog offers to switch to offline mode.

### 4. Export annotations

Download all annotations from Supabase as JSONL:

```bash
# All datasets
autojudge-annotate export-db \
    --supabase-url https://yourproject.supabase.co \
    --supabase-anon-key your-anon-key \
    -o annotations.jsonl

# Single dataset
autojudge-annotate export-db \
    --supabase-url https://yourproject.supabase.co \
    --supabase-anon-key your-anon-key \
    --dataset my-dataset \
    -o annotations.jsonl
```

## Annotation workflow

Before you begin, enter your username, which persists across sessions and is stored per annotation.

The topbar **Mode** selector switches between three annotation modes:

### Reports mode

Annotate full report text per topic/run.

1. Select a topic from the sidebar, then a run
2. Read the request (title, problem statement, background) and the report
3. Highlight relevant passages by selecting text — selections crossing sentence boundaries are automatically split into per-sentence subspans with `sentence_idx`
4. Click `[DocId]` citation markers to view source documents in a popup (when `--show-documents` is enabled)
5. Choose a rating and add optional comments

### Documents mode

Annotate individual source documents per topic.

1. Select a topic, then a run, then a document from the sidebar
2. Read the document text (title + body)
3. Highlight relevant passages
4. Choose a rating and add optional comments

### Citations mode

Step through report sentences and annotate the relationship between each sentence and its cited documents with **dual spans** (report spans + document spans).

1. Select a topic, then a run from the sidebar; sentences appear in the sidebar
2. Use the **sentence stepper** (Prev/Next buttons) or click a sentence in the sidebar
3. The current sentence is displayed in a yellow box; highlight text to create **report spans**
4. If the sentence has citations, the cited document appears below; highlight text to create **document spans**
5. For sentences with multiple citations, use the **citation tabs** to switch between documents
6. Choose a rating and add optional comments
7. The sidebar shows checkmarks on fully annotated sentences (all citations rated)

## Common features

- **Auto-save**: every change is saved to localStorage immediately
- **Progress tracking**: sidebar shows checkmarks on annotated items and completion counts per topic
- **Ratings**: Perfect, Mostly Good, So-so, Bad, or Not rated
- **Download**: click **Download JSONL** to export all annotations
- **Clear**: button at the bottom of the sidebar to reset your annotations for this dataset (with confirmation; also deletes from server if online)
- **Username**: stored per annotation at edit time, persists across sessions

## Output format

Each annotation is a JSON line. The format varies by mode:

### Report annotation

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
    {"start": 0, "end": 45, "text": "First relevant passage", "sentence_idx": 0},
    {"start": 46, "end": 120, "text": "Second passage from next sentence", "sentence_idx": 1}
  ],
  "report": { ... }
}
```

### Document annotation

```json
{
  "dataset": "my-dataset",
  "request_id": "1101",
  "docid": "doc-abc-123",
  "topic_id": "1101",
  "username": "alice",
  "rating": "So-so",
  "comment": "",
  "spans": [
    {"start": 10, "end": 85, "text": "Relevant passage from document"}
  ],
  "document": { ... }
}
```

### Citation annotation

```json
{
  "dataset": "my-dataset",
  "request_id": "1101",
  "topic_id": "1101",
  "username": "alice",
  "rating": "Perfect",
  "comment": "Sentence accurately reflects source",
  "spans": [
    {"start": 0, "end": 50, "text": "Document passage supporting the claim"}
  ],
  "report_spans": [
    {"start": 0, "end": 30, "text": "Sentence text being verified"}
  ],
  "citation": {
    "report": { ... },
    "sentence_idx": 2,
    "sentence": {"text": "The full sentence text.", "citations": ["doc-abc-123"]},
    "docid": "doc-abc-123",
    "document": { ... }
  }
}
```