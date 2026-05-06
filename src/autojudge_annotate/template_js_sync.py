"""JS sync module: Supabase client init, sync functions, status indicator, mode toggle.

Uses createSyncManager from template_js_sync_core for the generic sync logic.
"""

from .template_js_sync_core import JS_SYNC_CORE

JS_SYNC = JS_SYNC_CORE + r"""
// --- autojudge-annotate specific sync configuration ---

var syncManager = createSyncManager({
  storagePrefix: "autojudge_annotate",
  dataset: DATA.dataset,
  getRecordsFn: buildOutputRecords,
  getUsernameFn: function() { return usernameInput.value.trim(); },
  statusElementId: "sync-status",
  modeElementId: "sync-mode",
  controlsElementId: "sync-controls"
});

// Expose functions for backwards compatibility with existing code
function syncAnnotation(key, record) { return syncManager.syncAnnotation(key, record); }
function syncAll() { return syncManager.syncAll(); }
function syncCurrentAnnotationDebounced() { return syncManager.syncDebounced(); }
function syncDeleteAll() { return syncManager.syncDeleteAll(); }
function setSyncStatus(status) { return syncManager.setStatus(status); }

// Initialize UI
syncManager.initUI();
"""