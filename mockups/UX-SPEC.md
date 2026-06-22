# Nugget Annotator UX Specification

Reference mockup: `nugget-centric-v12.html`

## Three Phases

### Phase 1: Creation
Build nuggets from sources (reports/documents).

**Middle Panel**: Source panel showing report text with query
**Nuggets Panel**:
- Nugget bank with categories (Must Have, Should Have, Avoid)
- "+ Nugget" button for creating new nuggets
- Verdicts shown inline when report is selected (check/tilde/cross + source citations)
- Quote button to toggle quote highlighting in source

**Navigation**: Queries + Reports sections visible

### Phase 2: QC (Quality Control)
Review and refine nuggets before finalizing.

**Middle Panel**: System Ranking panel (click to drill into report)
**Nuggets Panel**:
- Solo button (dot) - view ranking with single nugget active
- Enable/disable checkboxes for each nugget
- Category weight inputs (editable)
- Edit button for each nugget
- "+ Nugget" button available

**Navigation**: Queries section only (reports hidden)

### Phase 3: Observe
Frozen nugget bank, final rankings.

**Middle Panel**: System Ranking panel with:
- Toggle: "All Queries" / "Q3 Only"
- Metrics bar: Avg, Max, Full coverage stats

**Nuggets Panel**:
- Category weights visible but read-only (slightly dimmed)
- No edit buttons
- No "+ Nugget" button
- No solo/checkbox controls

**Navigation**: Queries section only

## Panel Layout

```
[Nav Panel] | [Middle Panel] | [Nuggets Panel]
   180px    |     flex       |     380px
```

- **Nav Panel**: Query list, Report list (Creation only)
- **Middle Panel**: Source (Creation) or System Ranking (QC/Observe)
- **Nuggets Panel**: Single panel that adapts based on phase

## Nugget Row Structure

```
[QC Controls] [Nugget Content]
              [Text]
              [Global: Coverage Bar + Label] [Edit] [Report: Verdict + Source + Quote]
```

- **QC Controls**: Solo button + checkbox (QC mode only)
- **Coverage Bar**: Neutral gray, shows X/Y reports
- **Edit**: Hidden in Observe mode
- **Report section**: Visible in Creation mode when report selected

## New Nugget Flow

1. Click "+ Nugget" to open draft card
2. **Step 1**: Select text from source (adds as span chip)
3. **Freetext Notes**: Optional description of what nugget should capture
4. **Step 2**: Click "Canonicalize" button
   - Shows progress bar during LLM call (~1.5s)
   - Generates canonical nugget statement in textarea
   - Button changes to "Re-canonicalize" (green)
   - Enables Impact and Commit buttons
5. Select category: Must Have / Should Have / Avoid
6. Click "Check Impact"
   - Shows progress bar during LLM call (~1.2s)
   - Shows matching quotes across reports
   - Click quote to navigate to that report
7. Click "Commit" to add nugget to bank

## Progress Bar Behavior

All LLM-calling buttons replace their text with a progress bar during operation:
- Button text becomes transparent (or replaced with progress indicator)
- Blue gradient fills from left to right based on actual progress
- Pointer events disabled during operation

**Real implementation (not mockup animation):**
- Progress bar starts when LLM request is initiated
- Fills as streaming responses arrive
- Denominator can grow if follow-up requests are queued
  - E.g., "Check Impact" may batch requests across 50 reports
  - If more batches are needed, total work increases
- Completes when all responses are received
- On error: bar turns red, button becomes re-clickable

Buttons with progress bar:
- Canonicalize (single LLM call)
- Check Impact (may batch across multiple reports)
- Grade All (many LLM calls, shows overall progress)

## Navigation

**Back Button**: Appears when navigation history exists
- Tracks phase + selected report
- Returns to previous state without pushing to history

**Cross-phase navigation**:
- Click ranking item in QC/Observe → jumps to Creation with that report
- Click quote in impact preview → jumps to Creation with that report

## Color Scheme

**Minimal color usage**:
- Coverage bars: Neutral gray (#888)
- Ranking scores: Neutral gray (#555)
- Category colors only on category headers and quote highlights:
  - Must Have: Green (#28a745)
  - Should Have: Yellow (#ffc107 / #856404)
  - Avoid: Red (#dc3545)

**Quote highlights** in source text:
- Colored underline + light tint background
- Toggle via Quote button in nugget row
- `.inactive` class removes styling temporarily

## Key Interactions

| Action | Result |
|--------|--------|
| Click report in nav | Load report in source panel |
| Click ranking item | Switch to Creation with that report |
| Click Quote button | Toggle quote highlight in source |
| Click Solo button | Show ranking with only that nugget |
| Click Unsolo | Restore all nuggets |
| Toggle checkbox | Enable/disable nugget in QC |
| Click phase tab | Switch phases with history push |
| Click Back | Return to previous state |