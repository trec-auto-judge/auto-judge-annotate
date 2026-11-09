# Nugget Annotator User Guide

*Version 1.1 — 2026-11-09*

A guide for creating and managing nuggets to evaluate RAG system outputs.

> **Maintainer note**: This file is the single source of truth for user documentation.
> When updating, also sync changes to the Quick Start Guide and Full Guide in `template_html.py`.
> See `CLAUDE.md` for the full checklist.

## Getting Started

### 1. Configure Your LLM API Key

Before creating nuggets, you need an OpenRouter API key for LLM-powered features.

1. Look for the **?** indicator in the top-right corner
2. Click it to open the API key prompt
3. Enter your OpenRouter API key
4. The indicator changes to **green checkmark** when ready

The key is stored in your browser's localStorage and persists across sessions.

### 2. Enter Your Username

Enter your name in the **Username** field (top-right). This is recorded as the creator of any nuggets you create.

---

## Navigation

### Queries Panel (Left Sidebar)

- Lists all evaluation queries/topics
- Shows **completion status** (checkmark if annotated)
- Shows **nugget count** badge for each query
- Click a query to select it

### Reports Panel (Creation Phase)

- Shows all system reports for the selected query
- Click a report to view its content in the middle panel
- In Creation phase, the first report auto-selects when you choose a query

---

## Creating Your First Nugget

### Step 1: Select Text Spans

In **Creation** phase:

1. Select text in the report with your mouse
2. The draft dialog opens automatically with your selection as a "span"
3. Select additional spans if needed - each appears as a chip in the draft card
4. Remove unwanted spans by clicking the **x** on their chip

You can also select text from the **Query** box at the top.

### Step 2: Add Notes (Optional)

Use the **Freetext notes** area to describe what this nugget should capture. This helps the LLM generate a better nugget question.

### Step 3: Canonicalize

Click **Canonicalize** to have the LLM generate a formal nugget question from your spans and notes.

- The button shows progress while working
- Once complete, the generated question appears
- Click **Re-canonicalize** to regenerate if unsatisfied

### Step 4: Choose Category

Select the nugget's importance:

| Category | Meaning |
|----------|---------|
| **Must Have** | Critical information - reports lacking this are poor |
| **Should Have** | Important but not critical |
| **Avoid** | Information that should NOT appear (e.g., hallucinations) |

### Step 5: Check Impact (Recommended)

Click **Check Impact** to preview how this nugget grades across all reports:

- Progress bar shows completion (e.g., "5/8")
- Results show each report with its grade and supporting quote
- Click a quote to navigate to that report while keeping the draft open
- This helps you verify the nugget is discriminative before committing

### Step 6: Commit

Click **Commit** to save the nugget permanently. It appears in the Nuggets panel on the right.

---

## Editing and Deleting Nuggets

### Edit a Nugget

1. Find the nugget in the right panel
2. Click the **Edit** button (pencil icon)
3. Modify spans, notes, or category
4. Click **Re-canonicalize** if you changed the notes or directly change the text
5. Click **Commit** to save changes

### Delete a Nugget

Click the **Delete** button on a nugget card to remove it. This works for both nuggets you
created and preloaded ones. The removal is saved to your browser and (if server sync is on)
recorded on the server as a tombstone. If you only want to keep a nugget out of the ranking,
**disable** it in QC phase instead of deleting it.

> Editing a nugget's **question text** is treated as a delete of the old nugget plus a new one,
> because nuggets are identified by a hash of their text.

---

## Viewing Nugget Quotes

Quotes show where in the report the nugget is addressed.

### Find Quote

Next to each nugget, the quote button shows:

| State | Action |
|-------|--------|
| **Find Quote** (green) | Click to extract quote from current report |
| **Show Quote** (blue) | Click to highlight the quote in the source |
| **Hide Quote** (blue) | Click to remove highlight |
| **No Quote** (gray) | No supporting quote found |

### Quote Highlighting

When you click **Show Quote**, the matching text is highlighted in the report view with a colored background.

---

## Grade All

The **Grade All** button (top-right) grades all enabled nuggets against all reports for the current query.

1. Click **Grade All**
2. Watch progress (e.g., "12/32")
3. When complete, shows brief "Done!" confirmation
4. Grades appear next to each nugget in the right panel

Only nuggets without existing grades are processed (cached grades are reused).

---

## QC Phase: Quality Control

Switch to **QC** phase using the tab at the top.

### Adjust Category Weights

Each category has an adjustable weight:

| Category | Range | Default | Effect |
|----------|-------|---------|--------|
| Must Have | 0-10 | 1.0 | Higher = more important in ranking |
| Should Have | 0-10 | 1.0 | Higher = more important in ranking |
| Avoid | -10-0 | -1.0 | Negative = penalizes reports containing this |

The system ranking updates in real-time as you adjust weights.

### Enable/Disable Nuggets

Use the **checkbox** next to each nugget to include or exclude it from ranking calculations. Disabled nuggets are ignored when computing system scores.

### Solo Mode

Click the **dot button** next to a nugget to "solo" it:

- Only that nugget is used for ranking
- Useful for testing individual nugget discriminativeness
- Click again or click **Unsolo** to exit solo mode

### Interpreting Rankings

The ranking table shows:

| Column | Meaning |
|--------|---------|
| **#** | Rank position |
| **System** | Report/system name |
| **Nug** | Satisfied/Total nuggets |
| **Avg** | Average grade (0-5) |
| **Cov** | Coverage % (grade 4+ count) |
| **Score** | Weighted score |

**Strong systems at top** = Your nuggets may be too easy (everyone gets them)
**Weak systems dominate** = Consider if nuggets are too strict or missing key points

---

## Observe Phase: Analysis

Switch to **Observe** phase for read-only analysis.

### Toggle All Queries

Click **All Queries** / **This Query** button to switch between:

- **This Query**: Rankings for currently selected query
- **All Queries**: Macro-averaged rankings across all queries

### Overview Panel

The right panel shows quality indicators:

| Metric | Meaning | Ideal |
|--------|---------|-------|
| **Discriminative Nuggets** | Covered by 10-80% of systems | High count |
| **Universal Nuggets** | Covered by >80% of systems | May be too easy |
| **Hard Nuggets** | Covered by <10% of systems | May need refinement |
| **Good Systems** | Cover 50%+ nuggets | Varies |
| **Poor Systems** | Cover <2% nuggets | Low count |

**Good nugget bank**: Mostly discriminative nuggets, few universal/hard extremes.

---

## Exporting Your Work

### Download Nugget Bank

Click **Export** to download a JSONL file containing:

- All nuggets with text and IDs
- Category assignments
- Creator metadata (username, timestamp, source spans)
- All grades for all reports
- Weight settings

**File format**: One JSON line per query's nugget bank.

**File name**: `{dataset}-nuggets.jsonl`

### Using Exported Data

The exported JSONL integrates with:

- Nugget-based judges for automated evaluation
- Other evaluation tooling in the TREC ecosystem
- Version control for annotation snapshots

---

## Server Sync (Supabase)

If the annotator was built with Supabase credentials, a **sync control** appears in the
top bar: an **online / offline** selector, a **status dot**, and a **Sync to Server** button.
Sync is a **backup**: your work is pushed to the server, so you can recover it if the browser's
local data is lost. (It is one-way for now — reopening on a fresh browser does *not* pull your
work back down; use **Export** or keep the same browser to continue.)

- **Online** mode pushes changes automatically a few seconds after you make them; the status
  dot shows syncing / synced / error. **Offline** mode keeps everything local until you switch
  back or click **Sync to Server**.
- You must enter a **username** before anything syncs (your rows are keyed by it).
- **What is backed up:** your document/report judgments, and every nugget you **create,
  modify, delete, or enable/disable** — including changes to preloaded nuggets. Deletes are
  stored as tombstones so the deletion itself is preserved.
- **What is not backed up:** the global category **weights** and transient **solo** mode.
- If a sync fails, your work stays safe in the browser; the app offers to switch to offline
  mode so you can keep working, and you can retry later.

If the sync control is absent, this build has no server configured and everything is
local-only (see **Data Lost** under Troubleshooting).

---

## Tips for Effective Annotation

1. **Start with obvious nuggets** - Key facts that good reports should cover
2. **Use Check Impact** - Verify nuggets discriminate before committing
3. **Mix categories** - Include Must Have, Should Have, and Avoid nuggets
4. **Iterate in QC** - Adjust weights to see ranking changes
5. **Watch for extremes** - Too many universal or hard nuggets indicates problems
6. **Export regularly** - Save your work to avoid browser data loss

---

## Keyboard Shortcuts

| Action | Method |
|--------|--------|
| Select text | Mouse drag in report |
| Add span | Auto-opens draft, or click "+ Add as span" prompt |
| Cancel draft | Click X on draft card or Cancel button |
| Navigate back | Click **Back** button (top-left) |

---

## Troubleshooting

### LLM Not Working

- Check the indicator shows green checkmark
- Verify your OpenRouter API key is valid
- Check browser console for errors

### Grades Not Updating

- Click **Grade All** to force re-grading
- Grades are cached by nugget text hash - editing text creates new cache entry

### Data Lost

- Data is stored in browser localStorage
- Use **Export** regularly to backup
- Clearing browser data will erase all local annotations