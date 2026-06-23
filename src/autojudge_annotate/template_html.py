"""HTML body content for the annotation interface.

New nugget-centric layout with three phases (Creation, QC, Observe)
and three-column layout: Nav | Middle | Nuggets
"""

HTML_BLOCK = r"""
<!-- Top Bar with Phase Tabs -->
<div class="top-bar">
  <button class="back-btn" id="backBtn" onclick="goBack()">&larr; Back</button>
  <span class="logo">Nugget Annotator</span>

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
          <div class="ranking-toggle" id="rankingToggle">
            <button class="active" onclick="setRankingScope('all')">All Queries</button>
            <button onclick="setRankingScope('single')">This Query</button>
          </div>
        </div>
        <div class="metrics-bar" id="metricsBar">
          <!-- Rendered by JS -->
        </div>
      </div>
      <div class="ranking-list" id="rankingList">
        <!-- Rendered by JS -->
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
"""
