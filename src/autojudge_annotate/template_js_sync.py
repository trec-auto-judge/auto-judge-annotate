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

// Second manager: user nugget create/modify/delete -> nuggets_current (shares the same
// online/offline mode key via the identical storagePrefix, so one toggle drives both).
var nuggetSyncManager = createSyncManager({
  storagePrefix: "autojudge_annotate",
  dataset: DATA.dataset,
  tableName: "nuggets_current",
  keyColumn: "nugget_key",
  getRecordsFn: buildNuggetSyncRecords,
  getUsernameFn: function() { return usernameInput.value.trim(); }
  // No status/mode/controls element ids: it has no UI of its own and follows the shared
  // mode key; the annotation manager owns the single #sync-status / #sync-mode controls.
});

// Expose functions for backwards compatibility with existing code
function syncAnnotation(key, record) { return syncManager.syncAnnotation(key, record); }
function syncAll() { syncManager.syncAll(); return nuggetSyncManager.syncAll(); }
function syncCurrentAnnotationDebounced() { return syncManager.syncDebounced(); }
function syncDeleteAll() { syncManager.syncDeleteAll(); return nuggetSyncManager.syncDeleteAll(); }
function setSyncStatus(status) { return syncManager.setStatus(status); }

// Initialize UI (annotation manager owns the controls).
syncManager.initUI();

// The single mode toggle must flip BOTH managers. The annotation manager already bound its
// own listener in initUI; add a second listener so nuggets follow the same choice.
(function() {
  var modeEl = document.getElementById("sync-mode");
  if (modeEl) {
    modeEl.addEventListener("change", function() { nuggetSyncManager.setMode(modeEl.value); });
  }
})();
"""