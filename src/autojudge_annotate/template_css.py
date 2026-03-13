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
.sync-syncing { background: #f39c12; animation: pulse 1s infinite; }
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
"""
