"""JS sync module: Supabase client init, sync functions, status indicator, mode toggle."""

JS_SYNC = r"""
// --- Supabase sync ---

var supabaseClient = null;
var syncMode = "offline";
var syncStatusEl = null;
var syncDebounceTimer = null;
var syncInflight = false;

// Init Supabase client (only if credentials provided)
if (DATA.supabase_url && DATA.supabase_anon_key) {
  supabaseClient = supabase.createClient(DATA.supabase_url, DATA.supabase_anon_key);
}

// Load saved sync mode preference
var savedSyncMode = localStorage.getItem("autojudge_annotate_sync_mode_" + DATA.dataset);
if (savedSyncMode === "online" || savedSyncMode === "offline") {
  syncMode = savedSyncMode;
} else if (supabaseClient) {
  // Default to online when credentials are provided
  syncMode = "online";
}

function setSyncStatus(status) {
  // status: "idle" | "pending" | "syncing" | "success" | "error"
  if (!syncStatusEl) syncStatusEl = document.getElementById("sync-status");
  if (!syncStatusEl) return;
  syncStatusEl.className = "sync-status sync-" + status;
  syncStatusEl.title = status === "error" ? "Sync failed" :
                       status === "syncing" ? "Uploading..." :
                       status === "pending" ? "Change noted, sync pending" :
                       status === "success" ? "Synced" : "Not synced";
}

var syncErrorDialogShown = false;

function showSyncErrorDialog(errorMsg) {
  if (syncErrorDialogShown) return;
  syncErrorDialogShown = true;
  var msg = "Sync to Supabase failed.\n\n"
          + "Error: " + (errorMsg || "Unknown error") + "\n\n"
          + "Your annotations are safe in localStorage.\n\n"
          + "Click OK to switch to offline mode, or Cancel to keep retrying.";
  if (confirm(msg)) {
    syncMode = "offline";
    clearTimeout(syncDebounceTimer);
    localStorage.setItem("autojudge_annotate_sync_mode_" + DATA.dataset, syncMode);
    var syncModeEl = document.getElementById("sync-mode");
    if (syncModeEl) syncModeEl.value = "offline";
    setSyncStatus("idle");
  }
}

// Upsert one annotation to annotations_current
var lastSyncError = null;

async function syncAnnotation(key, record) {
  if (!supabaseClient) return false;
  var username = record.username;
  if (!username) return false;
  var row = {
    annotation_key: key,
    dataset: DATA.dataset,
    username: username,
    payload: record
  };
  var result = await supabaseClient
    .from("annotations_current")
    .upsert(row, { onConflict: "dataset,username,annotation_key" });
  if (result.error) {
    lastSyncError = result.error.message || JSON.stringify(result.error);
    return false;
  }
  return true;
}

// Delete annotations for this user+dataset from the server
async function syncDeleteAll() {
  if (!supabaseClient) return false;
  var username = usernameInput.value.trim();
  if (!username) return false;
  var result = await supabaseClient
    .from("annotations_current")
    .delete()
    .eq("dataset", DATA.dataset)
    .eq("username", username);
  return !result.error;
}

// Sync all annotations to server
async function syncAll() {
  if (!supabaseClient) return;
  var username = usernameInput.value.trim();
  if (!username) {
    alert("Please enter a username before syncing.");
    return;
  }
  if (syncInflight) return;
  syncInflight = true;
  // Clear timer so edits during sync start a new timer
  clearTimeout(syncDebounceTimer);
  syncDebounceTimer = null;
  syncErrorDialogShown = false;
  setSyncStatus("syncing");
  var records = buildOutputRecords(true);
  var success = true;
  for (var i = 0; i < records.length; i++) {
    if (!await syncAnnotation(records[i].key, records[i].record)) success = false;
  }
  syncInflight = false;
  setSyncStatus(success ? "success" : "error");
  if (!success) showSyncErrorDialog(lastSyncError);
}

// Throttled sync: first edit starts a 5s timer, subsequent edits don't reset it
function syncCurrentAnnotationDebounced() {
  if (syncMode !== "online" || !supabaseClient) return;
  if (!usernameInput.value.trim()) return;
  if (syncDebounceTimer) return;  // timer already running, syncAll will pick up all changes
  setSyncStatus("pending");
  syncDebounceTimer = setTimeout(function() {
    syncDebounceTimer = null;
    syncAll();
  }, 5000);
}

// --- Sync UI initialization ---

function initSyncUI() {
  var syncModeEl = document.getElementById("sync-mode");
  var syncControls = document.getElementById("sync-controls");

  if (!supabaseClient) {
    // No credentials: hide sync controls in topbar
    if (syncControls) syncControls.style.display = "none";
    return;
  }

  // Set initial mode from saved preference
  if (syncModeEl) {
    syncModeEl.value = syncMode;
    syncModeEl.addEventListener("change", function() {
      syncMode = syncModeEl.value;
      localStorage.setItem("autojudge_annotate_sync_mode_" + DATA.dataset, syncMode);
      if (syncMode === "offline") {
        clearTimeout(syncDebounceTimer);
        setSyncStatus("idle");
      } else if (syncMode === "online") {
        syncAll();
      }
    });
  }
}

initSyncUI();
"""