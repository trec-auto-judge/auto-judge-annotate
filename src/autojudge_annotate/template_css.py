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
.nugget-panel-header { font-size: 14px; color: #495057; margin-bottom: 10px; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.nugget-panel-header::before { content: ""; display: inline-block; width: 0; height: 0; border-left: 5px solid #495057; border-top: 4px solid transparent; border-bottom: 4px solid transparent; transition: transform 0.2s; }
.nugget-panel.collapsed .nugget-panel-header::before { transform: rotate(90deg); }
.nugget-panel.collapsed .nugget-list, .nugget-panel.collapsed .nugget-claims-section { display: none; }

.nugget-list { display: flex; flex-direction: column; gap: 2px; }
.nugget-item { display: flex; align-items: flex-start; gap: 8px; padding: 2px 4px; font-size: 12px; line-height: 1.4; }
.nugget-item.nugget-satisfied { background: #f8fff8; }
.nugget-item.nugget-partial { background: #fffdf5; }
.nugget-item.nugget-not-satisfied { background: #fff8f8; }
.nugget-item.nugget-unknown { background: #f8f9fa; }

.nugget-verdict { font-size: 12px; flex-shrink: 0; min-width: 16px; }
.nugget-satisfied .nugget-verdict { color: #28a745; }
.nugget-partial .nugget-verdict { color: #ffc107; }
.nugget-not-satisfied .nugget-verdict { color: #dc3545; }
.nugget-unknown .nugget-verdict { color: #6c757d; }

.nugget-text { flex: 1; }
.nugget-docs { font-size: 11px; color: #6c757d; flex-shrink: 0; cursor: help; }

.nugget-claims-section { margin-top: 12px; }
.nugget-claims-section h4 { font-size: 12px; color: #6c757d; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }

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
.criteria-nugget-item { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 4px; }
.criteria-nugget-item input[type="checkbox"] { margin-top: 3px; }
.criteria-nugget-item label { font-size: 13px; line-height: 1.4; color: #555; cursor: pointer; }
.criteria-nugget-item label:hover { color: #2c3e50; }

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

.doc-text { line-height: 1.7; white-space: pre-wrap; font-size: 13px; color: #333; max-height: 400px; overflow-y: auto; padding: 12px; background: #fafafa; border-radius: 4px; }
"""
