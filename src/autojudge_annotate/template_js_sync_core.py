"""Generic Supabase sync utilities - configurable via config object.

These functions can be reused by any annotation tool that needs Supabase sync.
"""

JS_SYNC_CORE = r"""
// --- Generic Supabase sync utilities ---

/**
 * Create a sync manager for Supabase integration.
 * @param {Object} config - Configuration object
 * @param {string} config.storagePrefix - Prefix for localStorage keys (e.g., "autojudge_annotate")
 * @param {string} config.dataset - Dataset identifier
 * @param {function(boolean): Array<{key: string, record: Object}>} config.getRecordsFn - Returns annotation records
 * @param {function(): string} config.getUsernameFn - Returns current username
 * @param {string} config.statusElementId - ID of sync status element (optional)
 * @param {string} config.modeElementId - ID of sync mode select element (optional)
 * @param {string} config.controlsElementId - ID of sync controls container (optional)
 * @returns {Object} - Sync manager with methods
 */
function createSyncManager(config) {
  var client = null;
  var mode = "offline";
  var debounceTimer = null;
  var inflight = false;
  var lastError = null;
  var errorDialogShown = false;

  // Initialize Supabase client if credentials provided
  if (DATA.supabase_url && DATA.supabase_anon_key) {
    client = supabase.createClient(DATA.supabase_url, DATA.supabase_anon_key);
  }

  // Load saved sync mode preference
  var savedMode = localStorage.getItem(config.storagePrefix + "_sync_mode_" + config.dataset);
  if (savedMode === "online" || savedMode === "offline") {
    mode = savedMode;
  } else if (client) {
    mode = "online";
  }

  function setStatus(status) {
    if (!config.statusElementId) return;
    var el = document.getElementById(config.statusElementId);
    if (!el) return;
    el.className = "sync-status sync-" + status;
    el.title = status === "error" ? "Sync failed" :
               status === "syncing" ? "Uploading..." :
               status === "pending" ? "Change noted, sync pending" :
               status === "success" ? "Synced" : "Not synced";
  }

  function showErrorDialog(errorMsg) {
    if (errorDialogShown) return;
    errorDialogShown = true;
    var msg = "Sync to Supabase failed.\n\n"
            + "Error: " + (errorMsg || "Unknown error") + "\n\n"
            + "Your annotations are safe in localStorage.\n\n"
            + "Click OK to switch to offline mode, or Cancel to keep retrying.";
    if (confirm(msg)) {
      mode = "offline";
      clearTimeout(debounceTimer);
      debounceTimer = null;
      localStorage.setItem(config.storagePrefix + "_sync_mode_" + config.dataset, mode);
      if (config.modeElementId) {
        var modeEl = document.getElementById(config.modeElementId);
        if (modeEl) modeEl.value = "offline";
      }
      setStatus("idle");
    }
  }

  async function syncAnnotation(key, record) {
    if (!client) return false;
    var username = record.username;
    if (!username) return false;
    var row = {
      annotation_key: key,
      dataset: config.dataset,
      username: username,
      payload: record
    };
    var result = await client
      .from("annotations_current")
      .upsert(row, { onConflict: "dataset,username,annotation_key" });
    if (result.error) {
      lastError = result.error.message || JSON.stringify(result.error);
      return false;
    }
    return true;
  }

  async function syncDeleteAll() {
    if (!client) return false;
    var username = config.getUsernameFn();
    if (!username) return false;
    var result = await client
      .from("annotations_current")
      .delete()
      .eq("dataset", config.dataset)
      .eq("username", username);
    return !result.error;
  }

  async function syncAll() {
    if (!client) return;
    var username = config.getUsernameFn();
    if (!username) {
      alert("Please enter a username before syncing.");
      return;
    }
    if (inflight) return;
    inflight = true;
    clearTimeout(debounceTimer);
    debounceTimer = null;
    errorDialogShown = false;
    setStatus("syncing");
    var records = config.getRecordsFn(true);
    var success = true;
    for (var i = 0; i < records.length; i++) {
      if (!await syncAnnotation(records[i].key, records[i].record)) success = false;
    }
    inflight = false;
    setStatus(success ? "success" : "error");
    if (!success) showErrorDialog(lastError);
  }

  function syncDebounced() {
    if (mode !== "online" || !client) return;
    if (!config.getUsernameFn()) return;
    if (debounceTimer) return;  // timer already running
    setStatus("pending");
    debounceTimer = setTimeout(function() {
      debounceTimer = null;
      syncAll();
    }, 5000);
  }

  function setMode(newMode) {
    mode = newMode;
    localStorage.setItem(config.storagePrefix + "_sync_mode_" + config.dataset, mode);
    if (mode === "offline") {
      clearTimeout(debounceTimer);
      debounceTimer = null;
      setStatus("idle");
    } else if (mode === "online") {
      syncAll();
    }
  }

  function initUI() {
    // Hide controls if no client
    if (!client && config.controlsElementId) {
      var controls = document.getElementById(config.controlsElementId);
      if (controls) controls.style.display = "none";
      return;
    }

    // Set initial mode in select element
    if (config.modeElementId) {
      var modeEl = document.getElementById(config.modeElementId);
      if (modeEl) {
        modeEl.value = mode;
        modeEl.addEventListener("change", function() {
          setMode(modeEl.value);
        });
      }
    }
  }

  return {
    syncAnnotation: syncAnnotation,
    syncAll: syncAll,
    syncDebounced: syncDebounced,
    syncDeleteAll: syncDeleteAll,
    setMode: setMode,
    getMode: function() { return mode; },
    hasClient: function() { return !!client; },
    initUI: initUI,
    setStatus: setStatus
  };
}
"""