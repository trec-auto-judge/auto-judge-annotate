"""JS sync module: Supabase client init, sync functions, status indicator, mode toggle."""

JS_SYNC = r"""
// --- Supabase sync ---

var supabaseClient = null;
var syncMode = "offline";
var syncStatusEl = null;
var syncDebounceTimer = null;

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
  // status: "idle" | "syncing" | "success" | "error"
  if (!syncStatusEl) syncStatusEl = document.getElementById("sync-status");
  if (!syncStatusEl) return;
  syncStatusEl.className = "sync-status sync-" + status;
  syncStatusEl.title = status === "error" ? "Sync failed" :
                       status === "syncing" ? "Syncing..." :
                       status === "success" ? "Synced" : "Not synced";
}

// Upsert one annotation to annotations_current
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
  return !result.error;
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

// Bulk sync all annotations (offline "Sync to Server" button)
async function syncAll() {
  if (!supabaseClient) return;
  var username = usernameInput.value.trim();
  if (!username) {
    alert("Please enter a username before syncing.");
    return;
  }
  setSyncStatus("syncing");
  var records = buildOutputRecords();
  var success = true;
  for (var i = 0; i < records.length; i++) {
    if (!await syncAnnotation(records[i].key, records[i].record)) success = false;
  }
  setSyncStatus(success ? "success" : "error");
}

// Dirty-set sync: track which keys need syncing, flush after debounce
var syncInflight = false;
var syncDirtyKeys = {};  // key -> true for keys that need syncing

function syncCurrentAnnotationDebounced() {
  if (syncMode !== "online" || !supabaseClient) return;
  if (!usernameInput.value.trim()) return;
  var key = currentAnnotationKey();
  if (key) syncDirtyKeys[key] = true;
  clearTimeout(syncDebounceTimer);
  syncDebounceTimer = setTimeout(function() { triggerSync(); }, 5000);
}

async function triggerSync() {
  if (syncInflight) return;  // will be called again after current flush
  var keys = Object.keys(syncDirtyKeys);
  if (keys.length === 0) return;

  syncInflight = true;
  setSyncStatus("syncing");
  var records = buildOutputRecords();
  var recordMap = {};
  records.forEach(function(r) { recordMap[r.key] = r.record; });

  var ok = true;
  for (var i = 0; i < keys.length; i++) {
    if (recordMap[keys[i]]) {
      if (await syncAnnotation(keys[i], recordMap[keys[i]])) {
        delete syncDirtyKeys[keys[i]];  // only clear on confirmed upsert
      } else {
        ok = false;
      }
    } else {
      delete syncDirtyKeys[keys[i]];  // no record to sync, discard
    }
  }
  syncInflight = false;
  setSyncStatus(ok ? "success" : "error");

  // Retry failed keys or flush newly accumulated ones
  if (Object.keys(syncDirtyKeys).length > 0) {
    syncDebounceTimer = setTimeout(function() { triggerSync(); }, 5000);
  }
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
      setSyncStatus("idle");
    });
  }
}

initSyncUI();
"""
