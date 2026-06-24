"""CSS styles for the annotation interface."""

CSS_BLOCK = r"""
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; color: #222; }

/* Top bar */
.topbar { background: #2c3e50; color: #fff; padding: 8px 16px; display: flex; align-items: center; gap: 16px; }
.topbar label { font-weight: 600; }
.topbar input[type=text] { padding: 4px 8px; border: 1px solid #555; border-radius: 4px; background: #3d5166; color: #fff; width: 200px; }
.topbar input[type=text]::placeholder { color: #aaa; }
.username-banner { display: none; background: #e74c3c; color: #fff; text-align: center; padding: 8px; font-weight: 600; font-size: 13px; }
.username-banner.visible { display: block; }
.topbar select { padding: 4px 8px; border: 1px solid #555; border-radius: 4px; background: #3d5166; color: #fff; font-size: 13px; }
.topbar .sync-controls { display: flex; align-items: center; gap: 8px; }
.sync-status { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
.sync-idle { background: #888; }
.sync-pending { background: #8cbf3f; }
.sync-syncing { background: #f1c40f; animation: pulse 1s infinite; }
.sync-success { background: #27ae60; }
.sync-error { background: #e74c3c; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

/* LLM indicator in topbar */
.llm-controls { display: flex; align-items: center; gap: 6px; }
.llm-indicator { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; cursor: pointer; font-size: 12px; font-weight: bold; }
.llm-indicator.llm-none { background: #666; color: #aaa; }
.llm-indicator.llm-ok { background: #27ae60; color: #fff; }
.llm-indicator.llm-error { background: #e74c3c; color: #fff; }
.llm-indicator:hover { opacity: 0.8; }

.topbar .dataset-label { margin-left: auto; font-size: 12px; opacity: 0.7; }

/* Layout */
.container { display: flex; height: calc(100vh - 40px); }
.sidebar { width: 260px; min-width: 260px; background: #f5f6fa; border-right: 1px solid #ddd; overflow-y: auto; padding: 12px; }
.main-panel { flex: 1; overflow-y: auto; padding: 24px 32px; }

/* Sidebar */
.sidebar h3 { font-size: 13px; text-transform: uppercase; color: #888; margin: 12px 0 6px 0; letter-spacing: 0.5px; }
.sidebar h3:first-child { margin-top: 0; }
.topic-item, .run-item, .doc-item { padding: 6px 10px; cursor: pointer; border-radius: 4px; margin-bottom: 2px; display: flex; align-items: center; gap: 6px; }
.topic-item:hover, .run-item:hover, .doc-item:hover { background: #e0e4ed; }
.topic-item.active { background: #3498db; color: #fff; }
.run-item.active { background: #3498db; color: #fff; }
.doc-item.active { background: #3498db; color: #fff; }
.doc-item .checkmark { margin-left: auto; color: #27ae60; font-weight: bold; }
.run-item .progress { font-size: 11px; opacity: 0.7; margin-left: auto; }
.topic-item .progress { font-size: 11px; opacity: 0.7; margin-left: auto; }
.run-item .checkmark { margin-left: auto; color: #27ae60; font-weight: bold; }
.run-item .nugget-coverage { font-size: 11px; color: #6c757d; background: #e9ecef; padding: 1px 5px; border-radius: 10px; margin-left: 6px; }

/* Hierarchical sidebar - Topics → Reports → Documents/Sentences */
.topic-row {
  padding: 8px 10px;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 2px;
  font-weight: 600;
  color: #2c3e50;
}
.topic-row:hover { background: #e0e4ed; }
.topic-row.active { background: #3498db; color: #fff; }
.topic-row.parent-active { background: #aed6f1; }

.report-row {
  display: flex;
  align-items: center;
  padding: 6px 10px 6px 20px;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 2px;
  gap: 6px;
}
.report-row:hover { background: #e0e4ed; }
.report-row.active { background: #3498db; color: #fff; }
.report-row.parent-active { background: #aed6f1; }

.fold-arrow {
  width: 16px;
  font-size: 10px;
  color: #666;
  flex-shrink: 0;
  user-select: none;
}
.report-row.active .fold-arrow { color: #fff; }
.fold-arrow:hover { color: #3498db; }
.report-row.active .fold-arrow:hover { color: #cce5ff; }

.report-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.nugget-coverage {
  font-size: 11px;
  color: #6c757d;
  background: #e9ecef;
  padding: 1px 6px;
  border-radius: 10px;
  flex-shrink: 0;
}
.report-row.active .nugget-coverage { background: rgba(255,255,255,0.3); color: #fff; }
.report-row.parent-active .nugget-coverage { background: rgba(255,255,255,0.6); color: #2c3e50; }
.topic-row.parent-active .nugget-coverage { background: rgba(255,255,255,0.6); color: #2c3e50; }

.checkmark { color: #27ae60; font-weight: bold; flex-shrink: 0; margin-left: 4px; min-width: 14px; text-align: center; }
.report-row.active .checkmark { color: #90EE90; }
.report-row.parent-active .checkmark { color: #1e8449; }

/* Clues indicator (hamburger icon) */
.clues-indicator { color: #6c757d; font-size: 12px; flex-shrink: 0; min-width: 14px; text-align: center; }
.clues-indicator:not(:empty) { color: #007bff; }
.report-row.active .clues-indicator { color: #a0cfff; }
.report-row.parent-active .clues-indicator { color: #0056b3; }

/* Foldout list (documents or sentences) */
.foldout-list { margin-left: 20px; }
.foldout-item {
  display: flex;
  align-items: center;
  padding: 4px 10px 4px 16px;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 1px;
  gap: 6px;
  font-size: 12px;
  color: #555;
}
.foldout-item:hover { background: #e0e4ed; }
.foldout-item.active { background: #5dade2; color: #fff; }

.foldout-id { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.foldout-preview { flex: 2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #888; }
.foldout-item.active .foldout-preview { color: #dbeafe; }
.foldout-item .nugget-coverage { font-size: 10px; padding: 1px 5px; }
.foldout-item.active .nugget-coverage { background: rgba(255,255,255,0.3); color: #fff; }
.foldout-item .checkmark { font-size: 12px; }
.foldout-item.active .checkmark { color: #90EE90; }

.cite-count { font-size: 10px; color: #888; flex-shrink: 0; }
.foldout-item.active .cite-count { color: #dbeafe; }

/* Request section */
.request-section { margin-bottom: 24px; padding: 16px; background: #f0f4f8; border-radius: 8px; border-left: 4px solid #3498db; }
.request-section h2 { font-size: 16px; margin-bottom: 8px; color: #2c3e50; }
.request-section .field-label { font-weight: 600; color: #555; font-size: 12px; text-transform: uppercase; margin-top: 8px; }
.request-section .field-value { margin-top: 2px; line-height: 1.5; }

/* Report section */
.report-section { margin-bottom: 24px; }
.report-section h2 { font-size: 16px; margin-bottom: 12px; color: #2c3e50; }
.report-text { line-height: 1.8; padding: 12px; background: #fff; border: 1px solid #ddd; border-radius: 6px; position: relative; user-select: text; white-space: pre-wrap; }
.report-text mark { background: #87ceeb; border-radius: 2px; cursor: pointer; }
.report-text mark .remove-span { display: none; width: 14px; height: 14px; background: #e74c3c; color: #fff; border-radius: 50%; font-size: 9px; line-height: 14px; text-align: center; cursor: pointer; vertical-align: top; margin-left: 1px; }
.report-text mark:hover .remove-span { display: inline-block; }
.citation-marker { color: #2980b9; font-size: 12px; cursor: pointer; vertical-align: super; font-weight: 600; }
.citation-marker:hover { text-decoration: underline; }

/* Spans list */
.spans-section { margin: 16px 0; }
.spans-section h3 { font-size: 14px; margin-bottom: 8px; color: #555; }
.span-chip { display: inline-block; background: #87ceeb; padding: 2px 8px; border-radius: 4px; margin: 2px 4px 2px 0; font-size: 12px; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Rating */
.rating-section { margin: 16px 0; }
.rating-section h3 { font-size: 14px; margin-bottom: 8px; color: #555; }
.rating-options { display: flex; gap: 12px; flex-wrap: wrap; }
.rating-options label { display: flex; align-items: center; gap: 4px; cursor: pointer; padding: 4px 8px; border: 1px solid #ddd; border-radius: 4px; }
.rating-options label:hover { background: #f0f4f8; }
.rating-options input[type=radio]:checked + span { font-weight: 600; }

/* Comment */
.comment-section { margin: 16px 0; }
.comment-section h3 { font-size: 14px; margin-bottom: 8px; color: #555; }
.comment-section textarea { width: 100%; height: 60px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; font-size: 13px; resize: vertical; }

/* Output section */
.output-section { margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px; }
.output-section h3 { font-size: 14px; margin-bottom: 8px; color: #555; }
.output-section textarea { width: 100%; height: 120px; font-family: monospace; font-size: 12px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; resize: vertical; }
.download-btn { margin-top: 8px; padding: 8px 16px; background: #2c3e50; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }
.download-btn:hover { background: #1a252f; }

/* Citation modal */
.modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); z-index: 1000; align-items: center; justify-content: center; }
.modal-overlay.visible { display: flex; }
.modal { background: #fff; border-radius: 8px; padding: 24px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; box-shadow: 0 4px 24px rgba(0,0,0,0.2); }
.modal h3 { margin-bottom: 8px; }
.modal .doc-url { color: #2980b9; font-size: 12px; margin-bottom: 12px; display: block; }
.modal .doc-text { line-height: 1.6; white-space: pre-wrap; }
.modal .close-btn { margin-top: 16px; padding: 6px 16px; background: #e74c3c; color: #fff; border: none; border-radius: 4px; cursor: pointer; }

/* Clear all button */
.clear-all-btn { display: block; margin-top: 24px; padding: 4px 8px; background: none; border: 1px solid #ccc; border-radius: 3px; color: #999; font-size: 11px; cursor: pointer; }
.clear-all-btn:hover { color: #e74c3c; border-color: #e74c3c; }

/* Empty state */
.empty-state { color: #888; text-align: center; padding: 48px; }

/* Sentence stepper */
.sentence-stepper { margin-bottom: 20px; }
.stepper-nav { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.stepper-nav button { padding: 6px 14px; background: #3498db; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
.stepper-nav button:disabled { background: #bdc3c7; cursor: not-allowed; }

.sentence-display { line-height: 1.8; padding: 12px; background: #fffbe6; border: 2px solid #f1c40f; border-radius: 6px; user-select: text; white-space: pre-wrap; }
.sentence-display mark { background: #87ceeb; border-radius: 2px; cursor: pointer; }
.sentence-display mark .remove-span { display: none; width: 14px; height: 14px; background: #e74c3c; color: #fff; border-radius: 50%; font-size: 9px; line-height: 14px; text-align: center; cursor: pointer; vertical-align: top; margin-left: 1px; }
.sentence-display mark:hover .remove-span { display: inline-block; }

/* Citation tabs + doc display */
.citation-tabs { display: flex; gap: 4px; margin-bottom: 8px; flex-wrap: wrap; }
.citation-tab { padding: 4px 12px; border: 1px solid #ddd; border-radius: 4px 4px 0 0; background: #f5f6fa; cursor: pointer; font-size: 12px; }
.citation-tab.active { background: #fff; border-bottom-color: #fff; font-weight: 600; }
.no-citation-msg { color: #888; font-style: italic; padding: 12px; }
.document-display { line-height: 1.8; padding: 12px; background: #f0f8ff; border: 1px solid #b0c4de; border-radius: 6px; user-select: text; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
.document-display mark { background: #87ceeb; border-radius: 2px; cursor: pointer; }
.document-display mark .remove-span { display: none; width: 14px; height: 14px; background: #e74c3c; color: #fff; border-radius: 50%; font-size: 9px; line-height: 14px; text-align: center; cursor: pointer; vertical-align: top; margin-left: 1px; }
.document-display mark:hover .remove-span { display: inline-block; }

/* Sentence sidebar items + dual span chips */
.sent-item { padding: 4px 8px; cursor: pointer; border-radius: 4px; margin-bottom: 2px; display: flex; align-items: center; gap: 6px; font-size: 12px; }
.sent-item:hover { background: #e0e4ed; }
.sent-item.active { background: #3498db; color: #fff; }
.sent-item .checkmark { margin-left: auto; color: #27ae60; font-weight: bold; }
.sent-item .sent-preview { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 160px; }
.sent-item .cite-count { font-size: 10px; opacity: 0.7; }
.report-span-chip { display: inline-block; background: #87ceeb; padding: 2px 8px; border-radius: 4px; margin: 2px 4px 2px 0; font-size: 12px; }
.document-span-chip { display: inline-block; background: #b8e6ff; padding: 2px 8px; border-radius: 4px; margin: 2px 4px 2px 0; font-size: 12px; }

/* Nugget panel */
.nugget-panel { margin: 16px 0; padding: 12px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; }
.nugget-panel-header { font-size: 14px; color: #495057; margin-bottom: 10px; cursor: pointer; display: flex; align-items: center; gap: 4px; user-select: none; }
.nugget-panel-toggle { display: inline-block; transition: transform 0.2s; font-size: 10px; transform: rotate(90deg); }
.nugget-panel.collapsed .nugget-panel-toggle { transform: rotate(0deg); }
.nugget-panel.collapsed .nugget-panel-content { display: none; }
.nugget-panel-title { font-weight: 600; }
.nugget-panel-spacer { flex: 1; }
.nugget-panel-content { }
.quote-all-btn { padding: 2px 8px; background: #6c757d; color: #fff; border: none; border-radius: 3px; font-size: 10px; cursor: pointer; }
.quote-all-btn:hover { background: #5a6268; }
.quote-all-btn:disabled { background: #adb5bd; cursor: not-allowed; }
.quote-progress-inline { display: inline-flex; align-items: center; justify-content: center; min-width: 36px; height: 16px; background: #e3f2fd; color: #1976d2; border-radius: 8px; font-size: 9px; font-weight: 600; }
.quote-progress-inline.quote-active { background: #e3f2fd; color: #1976d2; }
.quote-progress-inline.quote-done { background: #e8f5e9; color: #2e7d32; }

/* Grade Docs button - same color as Quote button */
.grade-docs-btn { padding: 2px 8px; background: #6c757d; color: #fff; border: none; border-radius: 3px; font-size: 10px; cursor: pointer; margin-right: 4px; }
.grade-docs-btn:hover { background: #5a6268; }
.grade-docs-btn:disabled { background: #adb5bd; cursor: not-allowed; }
.grade-docs-progress-inline { display: inline-flex; align-items: center; justify-content: center; min-width: 36px; height: 16px; background: #e3f2fd; color: #1976d2; border-radius: 8px; font-size: 9px; font-weight: 600; margin-right: 4px; }
.grade-docs-progress-inline.grade-docs-active { background: #e3f2fd; color: #1976d2; }
.grade-docs-progress-inline.grade-docs-done { background: #e8f5e9; color: #2e7d32; }

/* Nugget categories */
.nugget-category { margin-bottom: 12px; }
.nugget-category:last-child { margin-bottom: 0; }
.nugget-category-header { display: flex; align-items: center; gap: 4px; cursor: pointer; padding: 4px 0; user-select: none; }
.nugget-category-toggle { display: inline-block; transition: transform 0.2s; font-size: 10px; color: #6c757d; transform: rotate(90deg); }
.nugget-category.collapsed .nugget-category-toggle { transform: rotate(0deg); }
.nugget-category.collapsed .nugget-category-content { display: none; }
.nugget-category-name { font-size: 12px; font-weight: 600; color: #495057; text-transform: uppercase; letter-spacing: 0.5px; }
.nugget-category-count { font-size: 11px; color: #6c757d; }
.nugget-category-content { padding-left: 8px; margin-top: 4px; }

/* Category-specific styling - all same color for consistency */
.cat-must-have .nugget-category-name,
.cat-should-have .nugget-category-name,
.cat-avoid .nugget-category-name,
.cat-claims .nugget-category-name { color: #2c3e50; }

.nugget-list { display: flex; flex-direction: column; gap: 0; }
.nugget-item { display: flex; align-items: flex-start; gap: 8px; padding: 4px 4px; font-size: 12px; line-height: 1.4; border-bottom: 1px solid #e9ecef; }
.nugget-item:last-child { border-bottom: none; }
/* No background colors for verdict states - avoids confusion with quote highlight colors */
/* Verdict is indicated by the icon color only */
/* User-created nuggets: subtle left border indicator */
.nugget-item.user-nugget-item { border-left: 3px solid #3498db; padding-left: 6px; }

.nugget-verdict { font-size: 12px; flex-shrink: 0; min-width: 16px; }
.nugget-satisfied .nugget-verdict { color: #28a745; }
.nugget-partial .nugget-verdict { color: #ffc107; }
.nugget-not-satisfied .nugget-verdict { color: #dc3545; }
.nugget-unknown .nugget-verdict { color: #6c757d; }

.nugget-text { flex: 1; }
.nugget-docs { font-size: 11px; color: #6c757d; flex-shrink: 0; cursor: help; }

/* Nuggets mode - criteria panel */
.criteria-panel { margin-bottom: 24px; padding: 16px; background: #fff; border: 1px solid #ddd; border-radius: 8px; }
.criteria-panel h3 { font-size: 14px; margin-bottom: 12px; color: #2c3e50; }

.category-section { margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #eee; }
.category-section:last-child { margin-bottom: 0; border-bottom: none; padding-bottom: 0; }

.category-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.category-name { font-weight: 600; color: #2c3e50; min-width: 100px; }
.category-weight { width: 60px; padding: 4px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; text-align: center; }
.category-weight:focus { outline: none; border-color: #3498db; }

.criteria-nugget-list { margin-left: 20px; }
.criteria-nugget-item { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 4px; flex-wrap: wrap; }
.criteria-nugget-item input[type="checkbox"] { margin-top: 3px; flex-shrink: 0; accent-color: #0d6efd; }
.criteria-nugget-item label { font-size: 13px; line-height: 1.4; color: #555; cursor: pointer; flex: 1; }
.criteria-nugget-item label:hover { color: #2c3e50; }
.nugget-coverage { font-size: 11px; color: #6c757d; background: #f1f3f4; padding: 2px 6px; border-radius: 10px; white-space: nowrap; margin-left: auto; }

/* User-created nuggets - blue left border indicator, verdict backgrounds preserved */
.user-nugget { border-left: 3px solid #3498db; }
.nugget-text-span { font-size: 13px; line-height: 1.4; color: #555; flex: 1; }

/* Grade button */
.grade-btn { padding: 2px 8px; font-size: 10px; background: #6c757d; color: #fff; border: none; border-radius: 3px; cursor: pointer; white-space: nowrap; flex-shrink: 0; margin-right: 4px; }
.grade-btn:hover { background: #5a6268; }

/* Solo button - matches checkbox accent color */
.solo-btn { display: inline-flex; align-items: center; justify-content: center; width: 16px; height: 16px; background: #fff; color: #6c757d; border: 1px solid #ced4da; border-radius: 50%; font-size: 14px; font-weight: bold; line-height: 1; cursor: pointer; flex-shrink: 0; margin-right: 4px; padding: 0; }
.solo-btn:hover { border-color: #86b7fe; }
.solo-btn.soloed { background: #0d6efd; border-color: #0d6efd; color: #fff; }

/* Solo mode bar */
.solo-mode-bar { display: flex; align-items: center; gap: 12px; padding: 6px 12px; margin-bottom: 12px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; }
.solo-mode-label { font-size: 12px; color: #495057; }
.unsolo-btn { padding: 3px 8px; font-size: 11px; background: #fff; color: #495057; border: 1px solid #ced4da; border-radius: 3px; cursor: pointer; }
.unsolo-btn:hover { background: #e9ecef; }

/* Inline progress indicator (replaces ? during grading) */
.grading-progress-inline { display: inline-flex; align-items: center; justify-content: center; min-width: 40px; height: 18px; background: #e3f2fd; color: #1976d2; border-radius: 9px; font-size: 10px; font-weight: 600; flex-shrink: 0; margin-right: 4px; }
.grading-progress-inline.grading-active { background: #e3f2fd; color: #1976d2; }
.grading-progress-inline.grading-done { background: #e8f5e9; color: #2e7d32; }

/* Nuggets mode - document list */
.doc-list-section { margin-bottom: 24px; }
.doc-list-section h3 { font-size: 14px; margin-bottom: 12px; color: #2c3e50; }

.doc-list { max-height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 6px; }
.doc-item { padding: 10px 12px; border-bottom: 1px solid #eee; cursor: pointer; display: flex; align-items: center; gap: 12px; }
.doc-item:last-child { border-bottom: none; }
.doc-item:hover { background: #f5f6fa; }
.doc-item.active { background: #e8f4fc; border-left: 3px solid #3498db; }

.doc-rank { font-weight: 600; color: #888; min-width: 24px; }
.doc-id { flex: 1; font-weight: 500; color: #2c3e50; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.doc-score { font-weight: 600; min-width: 50px; text-align: right; }
.doc-summary { font-size: 11px; color: #888; min-width: 120px; text-align: right; }
.doc-annotated { color: #27ae60; font-weight: bold; font-size: 14px; flex-shrink: 0; min-width: 18px; text-align: center; }
.doc-item.active .doc-annotated { color: #1e8449; }

.score-high { color: #27ae60; }
.score-medium { color: #f39c12; }
.score-low { color: #e74c3c; }

/* Nuggets mode - document viewer */
.doc-viewer-section { margin-bottom: 24px; }
.doc-viewer-section h3 { font-size: 14px; margin-bottom: 12px; color: #2c3e50; }

.doc-viewer { padding: 16px; background: #fff; border: 1px solid #ddd; border-radius: 6px; }

.doc-verdicts { margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #eee; }
.doc-verdicts h4 { font-size: 13px; color: #888; margin-bottom: 8px; text-transform: uppercase; }

.verdict-category { margin-bottom: 12px; }
.verdict-category-name { font-weight: 600; font-size: 12px; color: #555; margin-bottom: 4px; }
.verdict-item { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 4px; padding-left: 12px; }
.verdict-icon { font-size: 12px; min-width: 16px; }
.verdict-text { font-size: 12px; color: #666; line-height: 1.4; flex: 1; }
.verdict-reasoning { font-size: 11px; color: #999; cursor: help; }

.verdict-satisfied { color: #27ae60; }
.verdict-partial { color: #f39c12; }
.verdict-not-satisfied { color: #e74c3c; }
.verdict-unknown { color: #6c757d; }

.user-verdict { background: #f0f8ff; border-left: 2px solid #007bff; padding-left: 6px; margin-left: -6px; }
.user-verdict.verdict-avoid { background: #fff5f5; border-left-color: #dc3545; }

.doc-text { line-height: 1.7; white-space: pre-wrap; font-size: 13px; color: #333; max-height: 400px; overflow-y: auto; padding: 12px; background: #fafafa; border-radius: 4px; }

/* Nugget Clues Section */
.nugget-clues-section { margin: 16px 0; padding: 16px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; }
.nugget-clues-section h3 { font-size: 14px; margin-bottom: 12px; color: #495057; }
.nugget-clues-section .clue-count { font-weight: normal; color: #6c757d; }

.clue-add-controls { display: flex; gap: 12px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }
.add-clue-btn { padding: 6px 12px; background: #28a745; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 500; }
.add-clue-btn:hover { background: #218838; }

.clue-type-radios { display: flex; gap: 4px; }
.clue-type-radio { display: flex; align-items: center; gap: 4px; padding: 4px 10px; border: 1px solid #ced4da; border-radius: 4px; cursor: pointer; font-size: 12px; background: #fff; transition: all 0.15s; }
.clue-type-radio:hover { background: #f8f9fa; }
.clue-type-radio input { margin: 0; }
.clue-type-radio input:checked + span { font-weight: 600; }
.clue-type-radio.clue-type-must_have input:checked + span { color: #155724; }
.clue-type-radio.clue-type-should_have input:checked + span { color: #856404; }
.clue-type-radio.clue-type-avoid input:checked + span { color: #721c24; }
.clue-type-radio.clue-type-must_have:has(input:checked) { background: #d4edda; border-color: #28a745; }
.clue-type-radio.clue-type-should_have:has(input:checked) { background: #fff3cd; border-color: #ffc107; }
.clue-type-radio.clue-type-avoid:has(input:checked) { background: #f8d7da; border-color: #dc3545; }

.clue-help { font-size: 12px; color: #6c757d; margin-bottom: 12px; font-style: italic; }

.clue-list { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }

.clue-item { padding: 10px 12px; border-radius: 6px; background: #fff; border: 1px solid #dee2e6; }
.clue-item.clue-type-must_have { border-left: 4px solid #28a745; }
.clue-item.clue-type-should_have { border-left: 4px solid #ffc107; }
.clue-item.clue-type-avoid { border-left: 4px solid #dc3545; }

.clue-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.clue-type-badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; text-transform: uppercase; }
.clue-type-must_have .clue-type-badge { background: #d4edda; color: #155724; }
.clue-type-should_have .clue-type-badge { background: #fff3cd; color: #856404; }
.clue-type-avoid .clue-type-badge { background: #f8d7da; color: #721c24; }

.clue-delete-btn { background: none; border: none; color: #dc3545; font-size: 18px; cursor: pointer; padding: 0 4px; line-height: 1; }
.clue-delete-btn:hover { color: #a71d2a; }

.clue-spans { margin-bottom: 6px; }
.clue-span-chip { display: inline-block; background: #e9ecef; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin: 2px 4px 2px 0; color: #495057; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.clue-comment { font-size: 13px; color: #495057; line-height: 1.4; padding: 6px 0; border-top: 1px solid #eee; margin-top: 6px; }

.clue-linked { font-size: 11px; color: #6c757d; margin-top: 4px; }

/* Clue actions */
.clue-actions { margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee; display: flex; gap: 8px; align-items: center; }
.clue-comment-input { flex: 1; padding: 6px 10px; border: 1px solid #ced4da; border-radius: 4px; font-size: 12px; }
.clue-comment-input:focus { outline: none; border-color: #007bff; }
.clue-canonicalize-btn { background: #007bff; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; white-space: nowrap; }
.clue-canonicalize-btn:hover { background: #0056b3; }
.clue-canonicalize-btn:disabled { background: #6c757d; cursor: wait; }

/* Canonicalized nugget display */
.clue-canonicalized { margin-top: 10px; padding: 10px; border-radius: 6px; }
.clue-canon-label { font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
.clue-canon-text { font-size: 14px; font-weight: 500; line-height: 1.4; }
.clue-canon-explanation { font-size: 12px; margin-top: 6px; font-style: italic; }

/* Canonicalized nugget type-specific colors */
.canon-type-must_have { background: #e8f5e9; border: 1px solid #a5d6a7; }
.canon-type-must_have .clue-canon-label { color: #388e3c; }
.canon-type-must_have .clue-canon-text { color: #1b5e20; }
.canon-type-must_have .clue-canon-explanation { color: #558b2f; }

.canon-type-should_have { background: #fff8e1; border: 1px solid #ffe082; }
.canon-type-should_have .clue-canon-label { color: #f57f17; }
.canon-type-should_have .clue-canon-text { color: #e65100; }
.canon-type-should_have .clue-canon-explanation { color: #ff8f00; }

.canon-type-avoid { background: #ffebee; border: 1px solid #ef9a9a; }
.canon-type-avoid .clue-canon-label { color: #c62828; }
.canon-type-avoid .clue-canon-text { color: #b71c1c; }
.canon-type-avoid .clue-canon-explanation { color: #d32f2f; }

/* LLM Settings */
.llm-settings { margin: 16px 0; padding: 12px 16px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; }
.llm-settings h4 { margin: 0 0 10px 0; font-size: 13px; color: #495057; }
.llm-key-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.llm-key-row label { font-size: 13px; color: #555; }
.llm-key-masked { font-family: monospace; font-size: 12px; background: #e9ecef; padding: 4px 8px; border-radius: 4px; color: #495057; }
.llm-key-btn { background: #6c757d; color: #fff; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; }
.llm-key-btn:hover { background: #5a6268; }
.llm-key-clear { background: #dc3545; }
.llm-key-clear:hover { background: #c82333; }
.llm-model-info { font-size: 11px; color: #6c757d; margin-top: 8px; }

/* Addressed quote highlights (from nugget grades) */
/* Light highlights - subtle background indicating quote location */
.quote-highlight { border-radius: 2px; padding: 0 1px; }
.quote-highlight-must_have { background: rgba(40, 167, 69, 0.15); }
.quote-highlight-should_have { background: rgba(255, 193, 7, 0.2); }
.quote-highlight-avoid { background: rgba(220, 53, 69, 0.15); }

/* Heavy highlights - stronger styling when toggled via click */
.quote-highlight-heavy { font-weight: 500; }
.quote-highlight-heavy.quote-highlight-must_have { background: rgba(40, 167, 69, 0.4); box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.3); }
.quote-highlight-heavy.quote-highlight-should_have { background: rgba(255, 193, 7, 0.5); box-shadow: 0 0 0 2px rgba(255, 193, 7, 0.3); }
.quote-highlight-heavy.quote-highlight-avoid { background: rgba(220, 53, 69, 0.4); box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.3); }

/* Nugget source clickable indicator */
.nugget-source-clickable { cursor: pointer; text-decoration: underline; text-decoration-style: dotted; }
.nugget-source-clickable:hover { text-decoration-style: solid; }

/* ============================================================================
   Nugget-Centric UI v12 - Three-Column Layout
   ============================================================================ */

/* Top Bar */
.top-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    background: #2c3e50;
    color: #fff;
    padding: 8px 16px;
    height: 48px;
}

.top-bar .logo {
    font-weight: 600;
    font-size: 15px;
}

.back-btn {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.3);
    color: #fff;
    padding: 4px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    display: none;
}
.back-btn.visible { display: inline-block; }
.back-btn:hover { background: rgba(255,255,255,0.1); }

/* Phase Tabs */
.phase-tabs {
    display: flex;
    gap: 4px;
    margin-left: 24px;
}

.phase-tab {
    padding: 6px 16px;
    background: rgba(255,255,255,0.1);
    border: none;
    border-radius: 4px;
    color: rgba(255,255,255,0.7);
    cursor: pointer;
    font-size: 13px;
    transition: all 0.15s;
}
.phase-tab:hover { background: rgba(255,255,255,0.2); color: #fff; }
.phase-tab.active { background: #3498db; color: #fff; }

/* Spacer to push actions to right */
.top-bar .spacer { flex: 1; }

/* Top actions area */
.top-bar .top-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.top-bar .top-actions button {
    padding: 6px 12px;
    border: 1px solid rgba(255,255,255,0.3);
    background: rgba(255,255,255,0.1);
    color: #fff;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}
.top-bar .top-actions button:hover { background: rgba(255,255,255,0.2); }
.top-bar .top-actions button.primary { background: #27ae60; border-color: #27ae60; }
.top-bar .top-actions button.primary:hover { background: #219a52; }

.top-bar .sync-select {
    padding: 4px 8px;
    border: 1px solid rgba(255,255,255,0.3);
    background: rgba(255,255,255,0.1);
    color: #fff;
    border-radius: 4px;
    font-size: 12px;
}

/* User controls in top bar */
.top-bar .user-controls {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 12px;
}

.top-bar .username-input {
    padding: 4px 10px;
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 4px;
    background: rgba(255,255,255,0.1);
    color: #fff;
    font-size: 13px;
    width: 140px;
}
.top-bar .username-input::placeholder { color: rgba(255,255,255,0.5); }

/* Main Container - Three Column Layout */
.main-container {
    display: flex;
    height: calc(100vh - 48px);
}

/* Nav Panel (Left Column) */
.nav-panel {
    width: 200px;
    min-width: 200px;
    background: #f5f6fa;
    border-right: 1px solid #ddd;
    overflow-y: auto;
    padding: 8px;
}

.nav-section {
    margin-bottom: 12px;
}

.nav-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 8px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #888;
    font-weight: 600;
}

.nav-section-count {
    font-size: 10px;
    color: #aaa;
}

.nav-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    color: #333;
}
.nav-item:hover { background: #e0e4ed; }
.nav-item.active { background: #3498db; color: #fff; }

.nav-item-status {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.nav-item-status.unchecked { background: #ddd; }
.nav-item-status.checked { background: #27ae60; }

.nav-item-label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.nav-item-badge {
    font-size: 10px;
    background: #e9ecef;
    padding: 1px 5px;
    border-radius: 8px;
    color: #666;
}
.nav-item.active .nav-item-badge { background: rgba(255,255,255,0.3); color: #fff; }

/* Middle Panel */
.middle-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Source Panel (Creation phase) */
.source-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.source-panel.hidden { display: none; }

.source-header {
    padding: 12px 16px;
    border-bottom: 1px solid #eee;
    background: #fafafa;
}

.source-title {
    font-size: 15px;
    font-weight: 600;
    color: #2c3e50;
}

.source-subtitle {
    font-size: 12px;
    color: #888;
    margin-top: 2px;
}

.source-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
}

.query-box {
    background: #f0f4f8;
    border-left: 4px solid #3498db;
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    margin-bottom: 16px;
    user-select: text;
}

.query-box-label {
    font-size: 11px;
    text-transform: uppercase;
    color: #888;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.query-box-content {
    font-size: 14px;
    line-height: 1.5;
    color: #2c3e50;
}

.query-title {
    font-weight: 600;
    font-size: 15px;
    color: #2c3e50;
    margin-bottom: 12px;
}

.query-section {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #ddd;
}

.query-section-label {
    font-size: 11px;
    text-transform: uppercase;
    color: #888;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.query-section-text {
    font-size: 14px;
    line-height: 1.6;
    color: #444;
    white-space: pre-wrap;
}

/* Legacy - kept for backward compatibility */
.query-box-text {
    font-size: 14px;
    line-height: 1.5;
    color: #2c3e50;
}

.source-text-area {
    line-height: 1.8;
    font-size: 14px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 16px;
    user-select: text;
}

.source-text-area p {
    margin-bottom: 12px;
}
.source-text-area p:last-child { margin-bottom: 0; }

/* Quote highlights in source text */
/* Quote highlights - light by default */
.source-text-area .has-quote-highlight {
    background: rgba(52, 152, 219, 0.1);
    border-left: 2px solid rgba(52, 152, 219, 0.3);
    padding-left: 8px;
    margin-left: -10px;
    transition: background 0.2s, border-color 0.2s;
}

/* Category-specific light highlights */
.source-text-area .has-quote-highlight[data-highlight-category="must"] {
    background: rgba(39, 174, 96, 0.1);
    border-left-color: rgba(39, 174, 96, 0.3);
}
.source-text-area .has-quote-highlight[data-highlight-category="avoid"] {
    background: rgba(231, 76, 60, 0.1);
    border-left-color: rgba(231, 76, 60, 0.3);
}
.source-text-area .has-quote-highlight[data-highlight-category="should"] {
    background: rgba(243, 156, 18, 0.1);
    border-left-color: rgba(243, 156, 18, 0.3);
}

/* Heavy highlight when Quote button is active */
.source-text-area .has-quote-highlight.heavy-highlight {
    background: rgba(52, 152, 219, 0.25);
    border-left: 3px solid #3498db;
    box-shadow: inset 0 0 0 1px rgba(52, 152, 219, 0.2);
}
.source-text-area .has-quote-highlight.heavy-highlight[data-highlight-category="must"] {
    background: rgba(39, 174, 96, 0.25);
    border-left-color: #27ae60;
    box-shadow: inset 0 0 0 1px rgba(39, 174, 96, 0.2);
}
.source-text-area .has-quote-highlight.heavy-highlight[data-highlight-category="avoid"] {
    background: rgba(231, 76, 60, 0.25);
    border-left-color: #e74c3c;
    box-shadow: inset 0 0 0 1px rgba(231, 76, 60, 0.2);
}
.source-text-area .has-quote-highlight.heavy-highlight[data-highlight-category="should"] {
    background: rgba(243, 156, 18, 0.25);
    border-left-color: #f39c12;
    box-shadow: inset 0 0 0 1px rgba(243, 156, 18, 0.2);
}

/* Class-based highlight colors (used with precedence) */
.source-text-area .has-quote-highlight.highlight-must {
    background: rgba(39, 174, 96, 0.1);
    border-left-color: rgba(39, 174, 96, 0.3);
}
.source-text-area .has-quote-highlight.highlight-avoid {
    background: rgba(231, 76, 60, 0.1);
    border-left-color: rgba(231, 76, 60, 0.3);
}
.source-text-area .has-quote-highlight.highlight-should {
    background: rgba(243, 156, 18, 0.1);
    border-left-color: rgba(243, 156, 18, 0.3);
}

/* Heavy versions of class-based highlights */
.source-text-area .has-quote-highlight.heavy-highlight.highlight-must {
    background: rgba(39, 174, 96, 0.25);
    border-left-color: #27ae60;
}
.source-text-area .has-quote-highlight.heavy-highlight.highlight-avoid {
    background: rgba(231, 76, 60, 0.25);
    border-left-color: #e74c3c;
}
.source-text-area .has-quote-highlight.heavy-highlight.highlight-should {
    background: rgba(243, 156, 18, 0.25);
    border-left-color: #f39c12;
}

/* Nugget badge on highlighted paragraphs */
.nugget-badge {
    display: inline-block;
    background: #34495e;
    color: #fff;
    font-size: 10px;
    font-weight: 600;
    padding: 1px 4px;
    border-radius: 3px;
    margin-right: 6px;
    cursor: pointer;
    vertical-align: middle;
    user-select: none;
}
.nugget-badge:hover {
    background: #2c3e50;
}

/* Nugget popup */
.nugget-popup {
    position: absolute;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    z-index: 1000;
    min-width: 280px;
    max-width: 400px;
    max-height: 300px;
    overflow: hidden;
}
.nugget-popup-header {
    padding: 8px 12px;
    background: #f8f9fa;
    border-bottom: 1px solid #eee;
    font-weight: 600;
    font-size: 12px;
    color: #666;
}
.nugget-popup-list {
    max-height: 250px;
    overflow-y: auto;
}
.nugget-popup-item {
    padding: 8px 12px;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    font-size: 13px;
}
.nugget-popup-item:last-child {
    border-bottom: none;
}
.nugget-popup-item:hover {
    background: #f8f9fa;
}
.nugget-popup-category {
    display: inline-block;
    font-size: 9px;
    font-weight: 600;
    padding: 2px 5px;
    border-radius: 3px;
    margin-right: 6px;
}
.nugget-popup-category.must {
    background: rgba(39, 174, 96, 0.15);
    color: #27ae60;
}
.nugget-popup-category.should {
    background: rgba(243, 156, 18, 0.15);
    color: #f39c12;
}
.nugget-popup-category.avoid {
    background: rgba(231, 76, 60, 0.15);
    color: #e74c3c;
}
.nugget-popup-text {
    color: #333;
}

/* Flash highlight for nugget rows when navigating from badge */
.nugget-row.flash-highlight {
    animation: flash-pulse 1.5s ease-out;
}
@keyframes flash-pulse {
    0% { background-color: rgba(52, 152, 219, 0.4); }
    100% { background-color: transparent; }
}

/* Selection prompt */
.selection-prompt {
    position: fixed;
    background: #2c3e50;
    color: #fff;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    z-index: 100;
    display: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.selection-prompt.visible { display: block; }
.selection-prompt:hover { background: #34495e; }

/* Ranking Panel (QC/Observe phases) */
.ranking-panel {
    flex: 1;
    display: none;
    flex-direction: column;
    overflow: hidden;
}
.ranking-panel.visible { display: flex; }

.ranking-header {
    padding: 12px 16px;
    border-bottom: 1px solid #eee;
    background: #fafafa;
}

.ranking-title {
    font-size: 15px;
    font-weight: 600;
    color: #2c3e50;
}

.ranking-scope {
    display: flex;
    gap: 4px;
    margin-top: 8px;
}

.scope-btn {
    padding: 4px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #fff;
    cursor: pointer;
    font-size: 12px;
}
.scope-btn:hover { background: #f5f6fa; }
.scope-btn.active { background: #3498db; color: #fff; border-color: #3498db; }

/* Metrics Bar (Observe only) */
.metrics-bar {
    display: none;
    padding: 12px 16px;
    background: #f8f9fa;
    border-bottom: 1px solid #eee;
    gap: 24px;
}
.metrics-bar.visible { display: flex; }

.metric-item {
    text-align: center;
}

.metric-value {
    font-size: 20px;
    font-weight: 600;
    color: #2c3e50;
}

.metric-label {
    font-size: 11px;
    color: #888;
    text-transform: uppercase;
}

.ranking-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
}

.ranking-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 4px;
}
.ranking-item:hover { background: #f5f6fa; }
.ranking-item.selected { background: #e8f4fc; border: 1px solid #3498db; }

.ranking-position {
    font-weight: 600;
    color: #888;
    min-width: 24px;
}

.ranking-info {
    flex: 1;
    overflow: hidden;
}

.ranking-name {
    font-weight: 500;
    color: #2c3e50;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.ranking-summary {
    font-size: 11px;
    color: #888;
}

.ranking-score {
    font-weight: 600;
    font-size: 14px;
    min-width: 40px;
    text-align: right;
}

/* Tabular Ranking Layout */
.ranking-header-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    border-bottom: 1px solid #eee;
}

.ranking-title {
    font-size: 14px;
    font-weight: 600;
    color: #2c3e50;
}

.ranking-controls {
    display: flex;
    align-items: center;
    gap: 8px;
}

.all-queries-toggle {
    padding: 4px 10px;
    font-size: 11px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #fff;
    cursor: pointer;
}
.all-queries-toggle:hover { border-color: #3498db; background: #f8f9fa; }
.all-queries-toggle.active {
    background: #3498db;
    color: #fff;
    border-color: #3498db;
}

/* Table structure */
.ranking-table {
    display: table;
    table-layout: auto;
    border-collapse: collapse;
    margin: 0 auto;
}

.ranking-header-row {
    display: table-row;
    background: #f8f9fa;
    font-size: 10px;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.ranking-row {
    display: table-row;
    cursor: pointer;
}
.ranking-row:hover { background: #f5f6fa; }
.ranking-row.selected { background: #e8f4fc; }

/* Column definitions using table-cell */
.ranking-header-row > span,
.ranking-row > span {
    display: table-cell;
    padding: 6px 4px;
    vertical-align: middle;
    border-bottom: 1px solid #f0f0f0;
}

.ranking-header-row > span {
    border-bottom: 1px solid #e5e7eb;
}

.col-rank {
    text-align: center;
    font-weight: 600;
    color: #888;
    padding-left: 8px !important;
    padding-right: 4px !important;
}
.col-name {
    text-align: left;
    font-weight: 500;
    color: #2c3e50;
    padding-right: 12px !important;
}
.col-count {
    text-align: center;
    font-size: 11px;
    color: #666;
}
.col-avg {
    text-align: center;
    font-size: 11px;
}
.col-cov {
    text-align: center;
    font-size: 11px;
}
.col-score {
    text-align: right;
    font-weight: 600;
    color: #2c3e50;
    padding-right: 8px !important;
}
.col-topics {
    text-align: center;
    font-size: 11px;
    color: #888;
}

/* Nuggets Panel (Right Column) */
.nuggets-panel {
    width: 380px;
    min-width: 380px;
    background: #fff;
    border-left: 1px solid #ddd;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.nuggets-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid #eee;
}

.nuggets-title {
    font-size: 14px;
    font-weight: 600;
    color: #2c3e50;
}

.nuggets-context {
    font-size: 12px;
    color: #888;
}

.new-nugget-btn {
    padding: 4px 12px;
    background: #27ae60;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}
.new-nugget-btn:hover { background: #219a52; }

/* Overview Panel (Observe Mode) */
.overview-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
}

.overview-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid #eee;
}

.overview-title {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
}

.overview-scope {
    font-size: 12px;
    color: #6b7280;
    background: #f3f4f6;
    padding: 4px 8px;
    border-radius: 4px;
}

.overview-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
}

.overview-summary {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e5e7eb;
}

.summary-stat {
    text-align: center;
}

.summary-value {
    font-size: 24px;
    font-weight: 700;
    color: #2563eb;
}

.summary-label {
    font-size: 11px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.overview-section {
    margin-bottom: 20px;
}

.section-title {
    font-size: 12px;
    font-weight: 600;
    color: #374151;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}

.metric-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    border-left: 3px solid #e5e7eb;
}

.metric-card.good { border-left-color: #10b981; }
.metric-card.neutral { border-left-color: #6b7280; }
.metric-card.warning { border-left-color: #f59e0b; }
.metric-card.bad { border-left-color: #ef4444; }

.metric-card-header {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 4px;
}

.metric-card-value {
    font-size: 22px;
    font-weight: 700;
    color: #1f2937;
}

.metric-card-label {
    font-size: 13px;
    font-weight: 500;
    color: #374151;
}

.metric-card-desc {
    font-size: 11px;
    color: #6b7280;
    margin-bottom: 8px;
}

.metric-bar {
    height: 6px;
    background: #e5e7eb;
    border-radius: 3px;
    overflow: hidden;
}

.metric-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
}

.metric-bar-fill.good { background: #10b981; }
.metric-bar-fill.neutral { background: #6b7280; }
.metric-bar-fill.warning { background: #f59e0b; }
.metric-bar-fill.bad { background: #ef4444; }

/* Ranking Metrics Tags */
.ranking-metrics {
    display: flex;
    gap: 6px;
    margin-top: 4px;
}

.metric-tag {
    font-size: 10px;
    color: #6b7280;
    background: #f3f4f6;
    padding: 2px 6px;
    border-radius: 3px;
}

/* Solo Mode Bar */
.solo-mode-bar {
    display: none;
    padding: 8px 16px;
    background: #fff3cd;
    border-bottom: 1px solid #ffc107;
    align-items: center;
    justify-content: space-between;
    font-size: 12px;
}
.solo-mode-bar.visible { display: flex; }

.unsolo-btn {
    padding: 3px 10px;
    background: #fff;
    border: 1px solid #ffc107;
    border-radius: 4px;
    cursor: pointer;
    font-size: 11px;
}
.unsolo-btn:hover { background: #ffc107; }

.nuggets-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px 16px;
}

/* Category Section */
.category-section {
    margin-bottom: 16px;
}

.category-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.category-name {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.category-name.must { color: #27ae60; }
.category-name.should { color: #f39c12; }
.category-name.avoid { color: #e74c3c; }

.category-spacer { flex: 1; }

.category-weight-group {
    display: none;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: #888;
}
.category-weight-group.visible { display: flex; }

.category-weight-label {
    color: #888;
}

.category-weight {
    width: 50px;
    padding: 2px 6px;
    border: 1px solid #ddd;
    border-radius: 3px;
    font-size: 12px;
    text-align: center;
}
.category-weight:focus { outline: none; border-color: #3498db; }

.category-nuggets {
    padding-top: 4px;
}

/* Nugget Row */
.nugget-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 4px;
    border-bottom: 1px solid #f0f0f0;
    transition: opacity 0.15s;
}
.nugget-row:last-child { border-bottom: none; }
.nugget-row.disabled { opacity: 0.4; }
.nugget-row.soloed { background: #fffde7; }

/* QC Controls (solo + checkbox) */
.qc-controls {
    display: none;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;
}
.qc-controls.visible { display: flex; }

.qc-controls .solo-btn {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 1px solid #ddd;
    background: #fff;
    cursor: pointer;
    font-size: 16px;
    line-height: 16px;
    text-align: center;
    color: #999;
}
.qc-controls .solo-btn:hover { border-color: #3498db; color: #3498db; }
.qc-controls .solo-btn.active { background: #3498db; color: #fff; border-color: #3498db; }

.qc-controls .nugget-checkbox {
    width: 16px;
    height: 16px;
    cursor: pointer;
}

/* Nugget Content */
.nugget-content {
    flex: 1;
    min-width: 0;
}

.nugget-text {
    font-size: 13px;
    line-height: 1.4;
    color: #333;
    margin-bottom: 6px;
}

.nugget-global {
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Coverage Bar */
.coverage-bar-container {
    display: flex;
    align-items: center;
    gap: 6px;
}

.coverage-bar {
    width: 60px;
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
    overflow: hidden;
}

.coverage-bar-fill {
    height: 100%;
    background: #6c757d;
    border-radius: 3px;
    transition: width 0.2s;
}

.coverage-label {
    font-size: 10px;
    color: #888;
    min-width: 30px;
}

/* Edit button */
.edit-btn {
    padding: 2px 8px;
    border: 1px solid #ddd;
    background: #fff;
    border-radius: 3px;
    font-size: 10px;
    cursor: pointer;
    color: #666;
}
.edit-btn:hover { background: #f5f6fa; }

/* Report Verdict (Creation phase with report selected) */
.nugget-report {
    display: none;
    align-items: center;
    gap: 6px;
    margin-left: auto;
}
.nugget-report.visible { display: flex; }

.verdict-icon {
    font-size: 14px;
    font-weight: bold;
}
.verdict-icon.satisfied { color: #27ae60; }
.verdict-icon.partial { color: #f39c12; }
.verdict-icon.not-satisfied { color: #e74c3c; }
.verdict-icon.unknown { color: #aaa; }

.verdict-source {
    font-size: 10px;
    color: #888;
}

.quote-btn {
    padding: 2px 8px;
    border: 1px solid #ddd;
    background: #fff;
    border-radius: 3px;
    font-size: 10px;
    cursor: pointer;
    color: #666;
    min-width: 70px;
    text-align: center;
}
.quote-btn:hover { background: #f5f6fa; }
.quote-btn.active { background: #3498db; color: #fff; border-color: #3498db; }

/* Find Quote state - clickable, triggers LLM */
.quote-btn.quote-find {
    color: #3498db;
    border-color: #3498db;
    border-style: dashed;
}
.quote-btn.quote-find:hover {
    background: #ebf5fb;
}
.quote-btn.quote-find.loading {
    opacity: 0.7;
    cursor: wait;
}

/* No Quote state - disabled, grayed out */
.quote-btn.quote-none {
    opacity: 0.4;
    cursor: not-allowed;
    color: #999;
    border-color: #ddd;
}
.quote-btn.quote-none:hover {
    background: #fff;
}

/* Has Quote state - normal toggle button */
.quote-btn.quote-has {
    color: #27ae60;
    border-color: #27ae60;
}
.quote-btn.quote-has:hover {
    background: #e8f8f0;
}
.quote-btn.quote-has.active {
    background: #27ae60;
    color: #fff;
}

/* Toast message for feedback */
.toast-message {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%) translateY(20px);
    background: #2c3e50;
    color: #fff;
    padding: 12px 24px;
    border-radius: 6px;
    font-size: 13px;
    opacity: 0;
    transition: opacity 0.3s, transform 0.3s;
    z-index: 10000;
    max-width: 400px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.toast-message.visible {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}

/* Draft Card - matches mockup v12 structure */
.draft-card {
    display: none;
    flex-direction: column;
    background: #fff;
    border: 2px solid #3498db;
    border-radius: 6px;
    margin: 8px 0;
    padding: 10px;
}
.draft-card.visible { display: flex; }

.draft-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}

.draft-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    color: #3498db;
}

.draft-close {
    background: none;
    border: none;
    font-size: 16px;
    color: #888;
    cursor: pointer;
}
.draft-close:hover { color: #333; }

.draft-section {
    margin-bottom: 10px;
}
.draft-section:last-child { margin-bottom: 0; }

.draft-label {
    font-size: 11px;
    font-weight: 600;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.draft-spans {
    min-height: 32px;
    padding: 6px;
    background: #f8f9fa;
    border-radius: 4px;
    font-size: 12px;
    color: #888;
}
.draft-spans.has-spans { color: #333; }

.span-chip {
    display: inline-block;
    background: #87ceeb;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    margin: 2px;
}

.span-chip-remove {
    cursor: pointer;
    color: #c0392b;
    margin-left: 4px;
}
.span-chip-remove:hover { color: #e74c3c; }

.draft-textarea {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 13px;
    font-family: inherit;
    resize: vertical;
    min-height: 60px;
}
.draft-textarea:focus { outline: none; border-color: #3498db; }
.draft-textarea:disabled { background: #f5f6fa; color: #888; }
.draft-textarea.populated { background: #f0fff4; border-color: #27ae60; }

/* Canonicalize button and area */
.draft-canonicalize {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.canonicalize-btn {
    padding: 6px 14px;
    background: #6c757d;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}
.canonicalize-btn:hover { background: #5a6268; }
.canonicalize-btn.done { background: #27ae60; }

.canonicalize-hint {
    font-size: 11px;
    color: #888;
}

/* Category selector in draft */
.draft-category {
    display: flex;
    gap: 4px;
}

.draft-category .category-btn {
    flex: 1;
    padding: 8px;
    border: 1px solid #ddd;
    background: #fff;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    text-align: center;
}
.draft-category .category-btn:hover { background: #f5f6fa; }
.draft-category .category-btn.active { color: #fff; }
.draft-category .category-btn.must.active { background: #27ae60; border-color: #27ae60; }
.draft-category .category-btn.should.active { background: #f39c12; border-color: #f39c12; }
.draft-category .category-btn.avoid.active { background: #e74c3c; border-color: #e74c3c; }

/* Impact Preview - quote-focused layout */
.impact-quotes {
    max-height: 200px;
    overflow-y: auto;
}

.impact-quote-item {
    padding: 8px;
    background: #fff;
    border: 1px solid #eee;
    border-radius: 4px;
    margin-bottom: 6px;
    cursor: pointer;
}
.impact-quote-item:hover { background: #f8f9fa; }
.impact-quote-item.current { background: #e8f4fc; border-color: #3498db; }

/* Quote text is the main content - prominent display */
.impact-quote-text {
    font-size: 12px;
    line-height: 1.4;
    color: #2c3e50;
}
.impact-quote-text.impact-no-quote {
    color: #888;
    font-style: italic;
}

/* Metadata (system, grade) - subtle, below quote */
.impact-meta {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
    font-size: 10px;
    color: #999;
}

.impact-meta-system {
    font-weight: 500;
}

.impact-meta-grade {
    color: #aaa;
}

/* Draft Actions - matches mockup */
.draft-actions {
    display: flex;
    gap: 6px;
    padding-top: 8px;
    border-top: 1px solid #eee;
}

.draft-actions button {
    flex: 1;
    padding: 6px;
    border-radius: 4px;
    border: 1px solid #ddd;
    background: #fff;
    cursor: pointer;
    font-size: 11px;
}

.draft-actions .cancel { color: #888; }
.draft-actions .cancel:hover { background: #f5f5f5; }

.draft-actions .impact { color: #3498db; border-color: #3498db; }
.draft-actions .impact:hover { background: #e8f4fc; }
.draft-actions .impact:disabled { color: #aaa; border-color: #ddd; cursor: not-allowed; }

.draft-actions .commit { background: #28a745; border-color: #28a745; color: #fff; }
.draft-actions .commit:hover { background: #218838; }
.draft-actions .commit:disabled { background: #ccc; border-color: #ccc; cursor: not-allowed; }

/* Progress Bar Buttons */
.progress-btn {
    position: relative;
    overflow: hidden;
}

.progress-btn .btn-text {
    position: relative;
    z-index: 1;
}

.progress-btn .progress-indicator {
    display: none;
    position: relative;
    z-index: 1;
}

.progress-btn.loading .btn-text { display: none; }
.progress-btn.loading .progress-indicator { display: inline; }

.progress-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: var(--progress-width, 0%);
    background: rgba(255,255,255,0.3);
    transition: width 0.2s;
}

.progress-btn.loading {
    cursor: wait;
}

.progress-btn.done::before {
    width: 100%;
    background: rgba(39, 174, 96, 0.3);
}

/* Citation marker styling */
.source-text-area .citation-marker {
    color: #2980b9;
    font-size: 11px;
    cursor: pointer;
    vertical-align: super;
    font-weight: 600;
}
.source-text-area .citation-marker:hover { text-decoration: underline; }

/* Modal Overlay */
.modal-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 1000;
    align-items: center;
    justify-content: center;
}
.modal-overlay.visible { display: flex; }

.modal-content {
    background: #fff;
    border-radius: 8px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}

.modal-header {
    padding: 16px;
    border-bottom: 1px solid #eee;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.modal-header h3 {
    margin: 0;
    font-size: 16px;
}

.modal-body {
    padding: 16px;
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #888;
}
.modal-close:hover { color: #333; }

/* Empty State */
.empty-state {
    padding: 32px;
    text-align: center;
    color: #888;
    font-size: 14px;
}

/* Utility classes */
.hidden { display: none !important; }
.visible { display: flex !important; }

/* Help Button */
.help-btn {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 1px solid #ccc;
    background: #fff;
    color: #666;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    margin-left: 8px;
}
.help-btn:hover {
    background: #f0f0f0;
    border-color: #999;
}

/* Help Modal */
.help-modal {
    max-width: 520px;
    max-height: 80vh;
    overflow-y: auto;
    padding: 24px;
    position: relative;
}

.help-modal h2 {
    margin: 0 0 16px 0;
    font-size: 20px;
    color: #2c3e50;
}

.help-modal .modal-close {
    position: absolute;
    top: 12px;
    right: 12px;
}

.help-section {
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #eee;
}

.help-section:last-of-type {
    border-bottom: none;
}

.help-section h3 {
    margin: 0 0 8px 0;
    font-size: 14px;
    color: #3498db;
}

.help-section ul {
    margin: 0;
    padding-left: 20px;
}

.help-section li {
    margin-bottom: 4px;
    font-size: 13px;
    line-height: 1.4;
    color: #444;
}

.help-section code {
    background: #f5f5f5;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 12px;
}

.help-footer {
    margin: 16px 0 0 0;
    text-align: center;
    font-size: 13px;
}

.help-footer a {
    color: #3498db;
    text-decoration: none;
}
.help-footer a:hover {
    text-decoration: underline;
}

.help-full-btn {
    background: #3498db;
    color: #fff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
}
.help-full-btn:hover {
    background: #2980b9;
}
.help-version {
    display: block;
    margin-top: 12px;
    font-size: 11px;
    color: #999;
}

/* Full Guide Modal */
.guide-modal {
    max-width: 700px;
    width: 90%;
    max-height: 85vh;
    overflow-y: auto;
    padding: 32px;
    position: relative;
}

.guide-modal .modal-close {
    position: absolute;
    top: 16px;
    right: 16px;
}

.guide-content {
    line-height: 1.6;
    color: #333;
}

.guide-content h1 {
    font-size: 24px;
    color: #2c3e50;
    margin: 0 0 24px 0;
    padding-bottom: 12px;
    border-bottom: 2px solid #3498db;
}

.guide-content h2 {
    font-size: 18px;
    color: #2c3e50;
    margin: 24px 0 12px 0;
}

.guide-content h3 {
    font-size: 14px;
    color: #3498db;
    margin: 16px 0 8px 0;
}

.guide-content p {
    margin: 8px 0;
    font-size: 13px;
}

.guide-content ul, .guide-content ol {
    margin: 8px 0;
    padding-left: 24px;
}

.guide-content li {
    margin: 4px 0;
    font-size: 13px;
}

.guide-content hr {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 20px 0;
}

.guide-content table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 12px;
}

.guide-content th, .guide-content td {
    border: 1px solid #e5e7eb;
    padding: 8px 12px;
    text-align: left;
}

.guide-content th {
    background: #f8f9fa;
    font-weight: 600;
    color: #374151;
}

.guide-content code {
    background: #f5f5f5;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 12px;
}
"""
