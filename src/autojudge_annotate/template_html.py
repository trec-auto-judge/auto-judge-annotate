"""HTML body content for the annotation interface."""

HTML_BLOCK = r"""
<div class="topbar">
  <label for="username-input">Username:</label>
  <input type="text" id="username-input" placeholder="Enter your name...">
  <label for="mode-select">Mode:</label>
  <select id="mode-select">
    <option value="reports">Reports</option>
    <option value="documents">Documents</option>
    <option value="citations">Citations</option>
  </select>
  <span class="dataset-label" id="dataset-label"></span>
</div>
<div class="username-banner" id="username-banner">Please enter a username above before annotating.</div>

<div class="container">
  <div class="sidebar" id="sidebar">
    <h3>Topics</h3>
    <div id="topic-list"></div>
    <h3 id="run-list-header">Runs</h3>
    <div id="run-list"></div>
    <h3 id="doc-list-header" style="display:none">Documents</h3>
    <div id="doc-list"></div>
    <h3 id="sent-list-header" style="display:none">Sentences</h3>
    <div id="sent-list"></div>
    <button class="clear-all-btn" id="clear-all-btn">Clear all annotations</button>
  </div>
  <div class="main-panel" id="main-panel">
    <div class="empty-state">Select a topic and run from the sidebar to begin annotating.</div>
  </div>
</div>

<div class="modal-overlay" id="modal-overlay">
  <div class="modal" id="modal">
    <h3 id="modal-title"></h3>
    <a class="doc-url" id="modal-url" target="_blank" rel="noopener"></a>
    <div class="doc-text" id="modal-text"></div>
    <button class="close-btn" id="modal-close">Close</button>
  </div>
</div>
"""
