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
.report-text mark { background: #ffeaa7; border-radius: 2px; cursor: pointer; }
.report-text mark .remove-span { display: none; width: 14px; height: 14px; background: #e74c3c; color: #fff; border-radius: 50%; font-size: 9px; line-height: 14px; text-align: center; cursor: pointer; vertical-align: top; margin-left: 1px; }
.report-text mark:hover .remove-span { display: inline-block; }
.citation-marker { color: #2980b9; font-size: 12px; cursor: pointer; vertical-align: super; font-weight: 600; }
.citation-marker:hover { text-decoration: underline; }

/* Spans list */
.spans-section { margin: 16px 0; }
.spans-section h3 { font-size: 14px; margin-bottom: 8px; color: #555; }
.span-chip { display: inline-block; background: #ffeaa7; padding: 2px 8px; border-radius: 4px; margin: 2px 4px 2px 0; font-size: 12px; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

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
.sentence-display mark { background: #ffd700; border-radius: 2px; cursor: pointer; }
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
.report-span-chip { display: inline-block; background: #ffeaa7; padding: 2px 8px; border-radius: 4px; margin: 2px 4px 2px 0; font-size: 12px; }
.document-span-chip { display: inline-block; background: #b8e6ff; padding: 2px 8px; border-radius: 4px; margin: 2px 4px 2px 0; font-size: 12px; }

/* Nugget panel */
.nugget-panel { margin: 16px 0; padding: 12px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; }
.nugget-panel-header { font-size: 14px; color: #495057; margin-bottom: 10px; cursor: pointer; display: flex; align-items: center; gap: 4px; user-select: none; }
.nugget-panel-toggle { display: inline-block; transition: transform 0.2s; font-size: 10px; transform: rotate(90deg); }
.nugget-panel.collapsed .nugget-panel-toggle { transform: rotate(0deg); }
.nugget-panel.collapsed .nugget-panel-content { display: none; }
.nugget-panel-content { }

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

.nugget-list { display: flex; flex-direction: column; gap: 2px; }
.nugget-item { display: flex; align-items: flex-start; gap: 8px; padding: 2px 4px; font-size: 12px; line-height: 1.4; }
.nugget-item.nugget-satisfied { background: #f8fff8; }
.nugget-item.nugget-partial { background: #fffdf5; }
.nugget-item.nugget-not-satisfied { background: #fff8f8; }
.nugget-item.nugget-unknown { background: #f8f9fa; }
.nugget-item.user-nugget-item { background: #f0f8ff; }

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

/* User-created nuggets */
.user-nugget { background: #f0f8ff; }
.user-nugget.nugget-avoid { background: #fff5f5; }
.nugget-text-span { font-size: 13px; line-height: 1.4; color: #555; flex: 1; }

/* Grade button for ungraded nuggets */
.grade-btn { padding: 2px 8px; font-size: 10px; background: #6c757d; color: #fff; border: none; border-radius: 3px; cursor: pointer; white-space: nowrap; flex-shrink: 0; margin-right: 4px; }
.grade-btn:hover { background: #5a6268; }

/* Re-grade button (after grading complete) */
.regrade-nugget-btn { padding: 2px 8px; font-size: 10px; background: #e9ecef; color: #495057; border: 1px solid #ced4da; border-radius: 3px; cursor: pointer; white-space: nowrap; flex-shrink: 0; margin-right: 8px; }
.regrade-nugget-btn:hover { background: #dee2e6; }
.regrade-nugget-btn:disabled { opacity: 0.6; cursor: not-allowed; }

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
"""
