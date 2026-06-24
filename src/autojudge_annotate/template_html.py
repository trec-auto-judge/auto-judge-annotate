"""HTML body content for the annotation interface.

New nugget-centric layout with three phases (Creation, QC, Observe)
and three-column layout: Nav | Middle | Nuggets

DOCUMENTATION SYNC REMINDER
===========================
When adding or changing user-facing features, update documentation in this order:

1. USER_GUIDE.md           -- The single source of truth (standalone markdown)
2. Quick Start Guide below -- Condensed version in help-modal (lines ~110-165)
3. Full Guide below        -- Rendered HTML version in guide-modal (lines ~175+)

The Quick Start and Full Guide should reflect USER_GUIDE.md content.
See also: CLAUDE.md in auto-judge-annotate/ for the full checklist.
"""

HTML_BLOCK = r"""
<!-- Top Bar with Phase Tabs -->
<div class="top-bar">
  <button class="back-btn" id="backBtn" onclick="goBack()">&larr; Back</button>
  <span class="logo">Nugget Annotator</span>
  <button class="help-btn" onclick="showHelp()" title="Help">?</button>

  <div class="phase-tabs">
    <button class="phase-tab active" id="tab-creation" onclick="setPhase('creation')">Creation</button>
    <button class="phase-tab" id="tab-qc" onclick="setPhase('qc')">QC</button>
    <button class="phase-tab" id="tab-observe" onclick="setPhase('observe')">Observe</button>
  </div>

  <div class="spacer"></div>

  <div class="top-actions">
    <input type="text" id="username-input" class="username-input" placeholder="Username...">
    <span id="sync-controls" class="sync-controls">
      <select id="sync-mode" class="sync-select">
        <option value="offline">Offline</option>
        <option value="online">Online</option>
      </select>
      <span class="sync-status sync-idle" id="sync-status"></span>
    </span>
    <span id="llm-controls" class="llm-controls">
      <span class="llm-indicator" id="llm-indicator" title="Click to set API key">?</span>
    </span>
    <button id="export-btn" onclick="downloadAnnotations()">Export</button>
    <button class="primary progress-btn" id="grade-all-btn" onclick="gradeAllNuggets()">
      <span class="btn-text">Grade All</span>
      <span class="progress-indicator"></span>
    </button>
  </div>
</div>

<!-- Username Banner (shown when no username) -->
<div class="username-banner" id="username-banner">Please enter a username above before annotating.</div>

<!-- Main Three-Column Layout -->
<div class="main-container">
  <!-- Navigation Panel -->
  <div class="nav-panel" id="navPanel">
    <!-- Rendered by JS: queries section + reports section -->
  </div>

  <!-- Middle Panel -->
  <div class="middle-panel">
    <!-- Source Panel (Creation phase) -->
    <div class="source-panel" id="sourcePanel">
      <div class="source-header">
        <div class="source-title-area">
          <div class="source-title" id="sourceTitle">Select a report</div>
          <div class="source-subtitle" id="sourceSubtitle"></div>
        </div>
      </div>
      <div class="source-content" id="sourceContent">
        <div class="empty-state">Select a query and report from the navigation to begin.</div>
      </div>
    </div>

    <!-- Ranking Panel (QC/Observe phases) -->
    <div class="ranking-panel" id="rankingPanel">
      <div class="ranking-header">
        <div class="ranking-header-top">
          <span class="ranking-title">System Ranking</span>
          <div class="ranking-controls" id="rankingControls">
            <!-- Rendered by JS: query selector in Observe, nothing in QC -->
          </div>
        </div>
        <div class="metrics-bar" id="metricsBar">
          <!-- Rendered by JS: column headers -->
        </div>
      </div>
      <div class="ranking-list" id="rankingList">
        <!-- Rendered by JS: tabular ranking -->
      </div>
    </div>
  </div>

  <!-- Nuggets Panel -->
  <div class="nuggets-panel" id="nuggetsPanel">
    <!-- Rendered by JS: header, solo bar, draft card, category sections -->
  </div>
</div>

<!-- Selection Prompt (appears on text selection) -->
<div class="selection-prompt" id="selectionPrompt">+ Add as span</div>

<!-- Citation Document Modal -->
<div class="modal-overlay" id="modal-overlay">
  <div class="modal" id="modal">
    <h3 id="modal-title"></h3>
    <a class="doc-url" id="modal-url" target="_blank" rel="noopener"></a>
    <div class="doc-text" id="modal-text"></div>
    <button class="close-btn" id="modal-close">Close</button>
  </div>
</div>

<!-- Help Modal -->
<div class="modal-overlay" id="help-modal-overlay">
  <div class="modal help-modal" id="help-modal">
    <button class="modal-close" onclick="hideHelp()">&times;</button>
    <h2>Quick Start Guide</h2>

    <div class="help-section">
      <h3>1. Setup</h3>
      <ul>
        <li><b>API Key:</b> Click the <code>?</code> indicator (top-right) to set your OpenRouter API key</li>
        <li><b>Username:</b> Enter your name in the username field</li>
      </ul>
    </div>

    <div class="help-section">
      <h3>2. Create Nuggets (Creation Phase)</h3>
      <ul>
        <li>Select a <b>query</b> from the left panel, then a <b>report</b></li>
        <li><b>Select text</b> in the report &rarr; draft dialog opens automatically</li>
        <li>Add notes (optional), then click <b>Canonicalize</b></li>
        <li>Choose category: <b>Must Have</b> / <b>Should Have</b> / <b>Avoid</b></li>
        <li>Click <b>Check Impact</b> to preview grades across all reports</li>
        <li>Click <b>Commit</b> to save the nugget</li>
      </ul>
    </div>

    <div class="help-section">
      <h3>3. Grade &amp; Review</h3>
      <ul>
        <li><b>Grade All:</b> Grades all nuggets against all reports</li>
        <li><b>Find Quote:</b> Extracts supporting text from the report</li>
        <li><b>Edit:</b> Click the edit button next to any nugget to modify it</li>
      </ul>
    </div>

    <div class="help-section">
      <h3>4. QC Phase</h3>
      <ul>
        <li><b>Weights:</b> Adjust category weights (0-10) to tune ranking</li>
        <li><b>Enable/Disable:</b> Toggle nuggets on/off with checkboxes</li>
        <li><b>Solo:</b> Click the dot to isolate a single nugget for testing</li>
      </ul>
    </div>

    <div class="help-section">
      <h3>5. Observe Phase</h3>
      <ul>
        <li>Toggle <b>All Queries</b> for cross-query rankings</li>
        <li>Overview panel shows nugget quality indicators</li>
        <li><b>Discriminative</b> nuggets (10-80% coverage) are ideal</li>
      </ul>
    </div>

    <div class="help-section">
      <h3>6. Export</h3>
      <ul>
        <li>Click <b>Export</b> to download nuggets as JSONL</li>
        <li>Use exported file with nugget-based judges</li>
      </ul>
    </div>

    <p class="help-footer">
      <button class="help-full-btn" onclick="hideHelp(); showFullGuide();">Full Guide &rarr;</button>
      <span class="help-version">v1.0 &mdash; 2026-06-24</span>
    </p>
  </div>
</div>

<!-- Full Documentation Modal -->
<div class="modal-overlay" id="guide-modal-overlay">
  <div class="modal guide-modal" id="guide-modal">
    <button class="modal-close" onclick="hideFullGuide()">&times;</button>
    <div class="guide-content">
      <h1>Nugget Annotator User Guide</h1>

      <h2>Getting Started</h2>

      <h3>1. Configure Your LLM API Key</h3>
      <p>Before creating nuggets, you need an OpenRouter API key for LLM-powered features.</p>
      <ol>
        <li>Look for the <code>?</code> indicator in the top-right corner</li>
        <li>Click it to open the API key prompt</li>
        <li>Enter your OpenRouter API key</li>
        <li>The indicator changes to <b>green checkmark</b> when ready</li>
      </ol>
      <p>The key is stored in your browser's localStorage and persists across sessions.</p>

      <h3>2. Enter Your Username</h3>
      <p>Enter your name in the <b>Username</b> field (top-right). This is recorded as the creator of any nuggets you create.</p>

      <hr>

      <h2>Navigation</h2>

      <h3>Queries Panel (Left Sidebar)</h3>
      <ul>
        <li>Lists all evaluation queries/topics</li>
        <li>Shows <b>completion status</b> (checkmark if annotated)</li>
        <li>Shows <b>nugget count</b> badge for each query</li>
        <li>Click a query to select it</li>
      </ul>

      <h3>Reports Panel (Creation Phase)</h3>
      <ul>
        <li>Shows all system reports for the selected query</li>
        <li>Click a report to view its content in the middle panel</li>
        <li>In Creation phase, the first report auto-selects when you choose a query</li>
      </ul>

      <hr>

      <h2>Creating Your First Nugget</h2>

      <h3>Step 1: Select Text Spans</h3>
      <p>In <b>Creation</b> phase:</p>
      <ol>
        <li>Select text in the report with your mouse</li>
        <li>The draft dialog opens automatically with your selection as a "span"</li>
        <li>Select additional spans if needed - each appears as a chip in the draft card</li>
        <li>Remove unwanted spans by clicking the <b>x</b> on their chip</li>
      </ol>
      <p>You can also select text from the <b>Query</b> box at the top.</p>

      <h3>Step 2: Add Notes (Optional)</h3>
      <p>Use the <b>Freetext notes</b> area to describe what this nugget should capture. This helps the LLM generate a better nugget question.</p>

      <h3>Step 3: Canonicalize</h3>
      <p>Click <b>Canonicalize</b> to have the LLM generate a formal nugget question from your spans and notes.</p>
      <ul>
        <li>The button shows progress while working</li>
        <li>Once complete, the generated question appears</li>
        <li>Click <b>Re-canonicalize</b> to regenerate if unsatisfied</li>
      </ul>

      <h3>Step 4: Choose Category</h3>
      <table>
        <tr><th>Category</th><th>Meaning</th></tr>
        <tr><td><b>Must Have</b></td><td>Critical information - reports lacking this are poor</td></tr>
        <tr><td><b>Should Have</b></td><td>Important but not critical</td></tr>
        <tr><td><b>Avoid</b></td><td>Information that should NOT appear (e.g., hallucinations)</td></tr>
      </table>

      <h3>Step 5: Check Impact (Recommended)</h3>
      <p>Click <b>Check Impact</b> to preview how this nugget grades across all reports:</p>
      <ul>
        <li>Progress bar shows completion (e.g., "5/8")</li>
        <li>Results show each report with its grade and supporting quote</li>
        <li>Click a quote to navigate to that report while keeping the draft open</li>
        <li>This helps you verify the nugget is discriminative before committing</li>
      </ul>

      <h3>Step 6: Commit</h3>
      <p>Click <b>Commit</b> to save the nugget permanently. It appears in the Nuggets panel on the right.</p>

      <hr>

      <h2>Editing and Deleting Nuggets</h2>

      <h3>Edit a Nugget</h3>
      <ol>
        <li>Find the nugget in the right panel</li>
        <li>Click the <b>Edit</b> button (pencil icon)</li>
        <li>Modify spans, notes, or category</li>
        <li>Click <b>Re-canonicalize</b> if you changed the text</li>
        <li>Click <b>Commit</b> to save changes</li>
      </ol>

      <hr>

      <h2>Viewing Nugget Quotes</h2>

      <h3>Find Quote Button States</h3>
      <table>
        <tr><th>State</th><th>Action</th></tr>
        <tr><td><b>Find Quote</b> (green)</td><td>Click to extract quote from current report</td></tr>
        <tr><td><b>Show Quote</b> (blue)</td><td>Click to highlight the quote in the source</td></tr>
        <tr><td><b>Hide Quote</b> (blue)</td><td>Click to remove highlight</td></tr>
        <tr><td><b>No Quote</b> (gray)</td><td>No supporting quote found</td></tr>
      </table>

      <hr>

      <h2>Grade All</h2>
      <p>The <b>Grade All</b> button (top-right) grades all enabled nuggets against all reports for the current query.</p>
      <ol>
        <li>Click <b>Grade All</b></li>
        <li>Watch progress (e.g., "12/32")</li>
        <li>When complete, shows brief "Done!" confirmation</li>
        <li>Grades appear next to each nugget in the right panel</li>
      </ol>

      <hr>

      <h2>QC Phase: Quality Control</h2>
      <p>Switch to <b>QC</b> phase using the tab at the top.</p>

      <h3>Adjust Category Weights</h3>
      <table>
        <tr><th>Category</th><th>Range</th><th>Default</th><th>Effect</th></tr>
        <tr><td>Must Have</td><td>0-10</td><td>1.0</td><td>Higher = more important in ranking</td></tr>
        <tr><td>Should Have</td><td>0-10</td><td>1.0</td><td>Higher = more important in ranking</td></tr>
        <tr><td>Avoid</td><td>-10-0</td><td>-1.0</td><td>Negative = penalizes reports containing this</td></tr>
      </table>

      <h3>Enable/Disable Nuggets</h3>
      <p>Use the <b>checkbox</b> next to each nugget to include or exclude it from ranking calculations.</p>

      <h3>Solo Mode</h3>
      <p>Click the <b>dot button</b> next to a nugget to "solo" it:</p>
      <ul>
        <li>Only that nugget is used for ranking</li>
        <li>Useful for testing individual nugget discriminativeness</li>
        <li>Click again or click <b>Unsolo</b> to exit solo mode</li>
      </ul>

      <h3>Ranking Table Columns</h3>
      <table>
        <tr><th>Column</th><th>Meaning</th></tr>
        <tr><td><b>#</b></td><td>Rank position</td></tr>
        <tr><td><b>System</b></td><td>Report/system name</td></tr>
        <tr><td><b>Nug</b></td><td>Satisfied/Total nuggets</td></tr>
        <tr><td><b>Avg</b></td><td>Average grade (0-5)</td></tr>
        <tr><td><b>Cov</b></td><td>Coverage % (grade 4+ count)</td></tr>
        <tr><td><b>Score</b></td><td>Weighted score</td></tr>
      </table>

      <hr>

      <h2>Observe Phase: Analysis</h2>
      <p>Switch to <b>Observe</b> phase for read-only analysis.</p>

      <h3>Toggle All Queries</h3>
      <p>Click <b>All Queries</b> / <b>This Query</b> button to switch between single-query and cross-query rankings.</p>

      <h3>Overview Panel Metrics</h3>
      <table>
        <tr><th>Metric</th><th>Meaning</th><th>Ideal</th></tr>
        <tr><td><b>Discriminative</b></td><td>Covered by 10-80% of systems</td><td>High count</td></tr>
        <tr><td><b>Universal</b></td><td>Covered by &gt;80% of systems</td><td>May be too easy</td></tr>
        <tr><td><b>Hard</b></td><td>Covered by &lt;10% of systems</td><td>May need refinement</td></tr>
      </table>
      <p><b>Good nugget bank:</b> Mostly discriminative nuggets, few universal/hard extremes.</p>

      <hr>

      <h2>Exporting Your Work</h2>
      <p>Click <b>Export</b> to download a JSONL file containing all nuggets, grades, and metadata.</p>
      <p>The exported file integrates with nugget-based judges and other evaluation tooling.</p>

      <hr>

      <h2>Tips for Effective Annotation</h2>
      <ol>
        <li><b>Start with obvious nuggets</b> - Key facts that good reports should cover</li>
        <li><b>Use Check Impact</b> - Verify nuggets discriminate before committing</li>
        <li><b>Mix categories</b> - Include Must Have, Should Have, and Avoid nuggets</li>
        <li><b>Iterate in QC</b> - Adjust weights to see ranking changes</li>
        <li><b>Watch for extremes</b> - Too many universal or hard nuggets indicates problems</li>
        <li><b>Export regularly</b> - Save your work to avoid browser data loss</li>
      </ol>
    </div>
  </div>
</div>
"""
