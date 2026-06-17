"""JS state management: data, state object, DOM refs, indexing, annotation helpers, auto-save, buildOutputLines."""

JS_STATE = r"""
// Data injected by generate_html.py
var DATA = /* __DATA_PLACEHOLDER__ */ null;

if (!DATA) { document.body.innerHTML = "<p>Error: No data embedded.</p>"; return; }

// State
var state = {
  selectedTopic: null,
  selectedRun: null,
  selectedDoc: null,
  selectedSentenceIdx: null,
  selectedCitationIdx: null,
  expandedRuns: {},  // "topicId|runId" -> boolean
  mode: "documents",   // "documents" or "citations" (controls fold-out content)
  annotations: {},   // key = "r|topicId|runId" or "d|topicId|docId" or "c|topicId|runId|sentIdx|docId" -> annotation
  // Nuggets mode state
  enabledNuggets: {},  // nugget_id -> boolean (default true)
  nuggetWeights: { must: 1.0, should: 1.0, avoid: -1.0 },  // category -> weight
  nuggetPanelCollapsed: {},  // "panel" | "must_have" | "should_have" | "avoid" | "claims" -> boolean
  soloNuggetId: null,  // nugget_id of currently soloed nugget (null = no solo)
  preSoloEnabledNuggets: null,  // snapshot of enabledNuggets before solo (to restore)
  preSoloNuggetIds: null,  // list of nugget IDs that existed before solo (to detect new nuggets)
  // User-generated nugget grades (from LLM grading)
  userNuggetGrades: {}  // topicId -> runId -> nuggetId -> {grade, reasoning, confidence}
};

// DOM refs
var usernameInput = document.getElementById("username-input");
var datasetLabel = document.getElementById("dataset-label");
var navTree = document.getElementById("nav-tree");
var mainPanel = document.getElementById("main-panel");
var modalOverlay = document.getElementById("modal-overlay");
var modalTitle = document.getElementById("modal-title");
var modalUrl = document.getElementById("modal-url");
var modalText = document.getElementById("modal-text");
var modalClose = document.getElementById("modal-close");
var modeSelect = document.getElementById("mode-select");

// Index data
var requestMap = {};  // request_id -> request
var reportIndex = {}; // topic_id -> {run_id -> report}
var topicIds = [];
var docIndex = {};    // topic_id -> {doc_id -> document obj} (union across all runs)
var runDocsIndex = {}; // topic_id -> {run_id -> [doc_id, ...]} (docs per run)

DATA.requests.forEach(function(r) { requestMap[r.request_id] = r; });
DATA.reports.forEach(function(r) {
  if (!reportIndex[r.topic_id]) reportIndex[r.topic_id] = {};
  reportIndex[r.topic_id][r.run_id] = r;
  // Build docIndex and runDocsIndex
  if (r.documents) {
    if (!docIndex[r.topic_id]) docIndex[r.topic_id] = {};
    if (!runDocsIndex[r.topic_id]) runDocsIndex[r.topic_id] = {};
    var runDocIds = [];
    Object.keys(r.documents).forEach(function(docId) {
      docIndex[r.topic_id][docId] = r.documents[docId];
      runDocIds.push(docId);
    });
    runDocsIndex[r.topic_id][r.run_id] = runDocIds.sort();
  }
});
topicIds = DATA.requests.map(function(r) { return r.request_id; });

// Init
datasetLabel.textContent = "Dataset: " + DATA.dataset;
var usernameBanner = document.getElementById("username-banner");
var savedUsername = localStorage.getItem("autojudge_annotate_username");
if (savedUsername) usernameInput.value = savedUsername;
function updateUsernameBanner() {
  if (usernameInput.value.trim()) {
    usernameBanner.classList.remove("visible");
  } else {
    usernameBanner.classList.add("visible");
  }
}
updateUsernameBanner();
usernameInput.addEventListener("input", function() {
  localStorage.setItem("autojudge_annotate_username", usernameInput.value);
  updateUsernameBanner();
});

// Load saved annotations from localStorage
var savedAnnotations = localStorage.getItem("autojudge_annotate_state_" + DATA.dataset);
if (savedAnnotations) {
  try {
    var loaded = JSON.parse(savedAnnotations);
    // Migrate old-format keys ("topicId|runId") to new format ("r|topicId|runId")
    Object.keys(loaded).forEach(function(key) {
      if (key.indexOf("r|") === 0 || key.indexOf("d|") === 0 || key.indexOf("c|") === 0) {
        // Already new format
        state.annotations[key] = loaded[key];
      } else {
        // Old format: "topicId|runId"
        var parts = key.split("|");
        var newKey = "r|" + key;
        var ann = loaded[key];
        ann.topicId = ann.topicId || parts[0];
        ann.runId = ann.runId || parts[1];
        state.annotations[newKey] = ann;
      }
    });
  } catch(e) { state.annotations = {}; }
}

// Load saved mode from localStorage
var savedMode = localStorage.getItem("autojudge_annotate_mode_" + DATA.dataset);
if (savedMode === "documents" || savedMode === "citations") {
  state.mode = savedMode;
} else if (savedMode === "reports" || savedMode === "nuggets") {
  // Migrate legacy modes to "documents"
  state.mode = "documents";
}
modeSelect.value = state.mode;

// Load saved user nugget grades from localStorage
var savedUserGrades = localStorage.getItem("autojudge_annotate_grades_" + DATA.dataset);
if (savedUserGrades) {
  try {
    state.userNuggetGrades = JSON.parse(savedUserGrades);
  } catch(e) { state.userNuggetGrades = {}; }
}

// Save user nugget grades to localStorage
function saveUserNuggetGrades() {
  localStorage.setItem("autojudge_annotate_grades_" + DATA.dataset, JSON.stringify(state.userNuggetGrades));
}

modeSelect.addEventListener("change", function() {
  state.mode = modeSelect.value;
  // Mode controls what appears in fold-out (documents or citations/sentences)
  // Clear sub-selections when switching
  state.selectedDoc = null;
  state.selectedSentenceIdx = null;
  state.selectedCitationIdx = null;
  localStorage.setItem("autojudge_annotate_mode_" + DATA.dataset, state.mode);
  renderSidebar();
  renderMain();
});

// --- Annotation helpers ---

function reportAnnotationKey(topicId, runId) { return "r|" + topicId + "|" + runId; }
function docAnnotationKey(topicId, docId) { return "d|" + topicId + "|" + docId; }

function getReportAnnotation(topicId, runId) {
  var key = reportAnnotationKey(topicId, runId);
  if (!state.annotations[key]) {
    state.annotations[key] = { topicId: topicId, runId: runId, rating: "Not rated", comment: "", spans: [], nugget_clues: [] };
  }
  // Migrate old annotations without nugget_clues
  if (!state.annotations[key].nugget_clues) state.annotations[key].nugget_clues = [];
  return state.annotations[key];
}

function getDocAnnotation(topicId, docId) {
  var key = docAnnotationKey(topicId, docId);
  if (!state.annotations[key]) {
    state.annotations[key] = { topicId: topicId, docId: docId, rating: "Not rated", comment: "", spans: [], nugget_clues: [] };
  }
  // Migrate old annotations without nugget_clues
  if (!state.annotations[key].nugget_clues) state.annotations[key].nugget_clues = [];
  return state.annotations[key];
}

function citationAnnotationKey(topicId, runId, sentIdx, docId) {
  if (docId) return "c|" + topicId + "|" + runId + "|" + sentIdx + "|" + docId;
  return "c|" + topicId + "|" + runId + "|" + sentIdx;
}

function getCitationAnnotation(topicId, runId, sentIdx, docId) {
  var key = citationAnnotationKey(topicId, runId, sentIdx, docId);
  if (!state.annotations[key]) {
    state.annotations[key] = { topicId: topicId, runId: runId, sentenceIdx: sentIdx, docId: docId || null, rating: "Not rated", comment: "", spans: [], reportSpans: [], nugget_clues: [] };
  }
  // Migrate old annotations without nugget_clues
  if (!state.annotations[key].nugget_clues) state.annotations[key].nugget_clues = [];
  return state.annotations[key];
}

function isCitationAnnotated(topicId, runId, sentIdx, docId) {
  var key = citationAnnotationKey(topicId, runId, sentIdx, docId);
  var ann = state.annotations[key];
  if (!ann) return false;
  return (ann.spans && ann.spans.length > 0) || (ann.reportSpans && ann.reportSpans.length > 0) || ann.rating !== "Not rated" || ann.comment !== "";
}

function isCitationSentenceComplete(topicId, runId, sentIdx) {
  var report = reportIndex[topicId] && reportIndex[topicId][runId];
  if (!report || !report.sentences || sentIdx >= report.sentences.length) return false;
  var sent = report.sentences[sentIdx];
  var citations = (sent.citations && sent.citations.length > 0) ? sent.citations : [null];
  return citations.every(function(docId) {
    return isCitationAnnotated(topicId, runId, sentIdx, docId);
  });
}

// Backwards compat: old annotations without topicId/runId fields
function getAnnotation(topicId, runId) { return getReportAnnotation(topicId, runId); }

function currentAnnotationKey() {
  // Annotation type is determined by what's selected, not by mode
  // Priority: citation > document > report
  if (state.selectedTopic && state.selectedRun && state.selectedSentenceIdx !== null) {
    // Citation annotation
    var report = reportIndex[state.selectedTopic] && reportIndex[state.selectedTopic][state.selectedRun];
    if (!report || !report.sentences || state.selectedSentenceIdx >= report.sentences.length) return null;
    var sent = report.sentences[state.selectedSentenceIdx];
    var citations = (sent.citations && sent.citations.length > 0) ? sent.citations : [null];
    var citIdx = state.selectedCitationIdx || 0;
    var docId = citations[citIdx] || null;
    return citationAnnotationKey(state.selectedTopic, state.selectedRun, state.selectedSentenceIdx, docId);
  }
  if (state.selectedTopic && state.selectedDoc) {
    // Document annotation
    return docAnnotationKey(state.selectedTopic, state.selectedDoc);
  }
  if (state.selectedTopic && state.selectedRun) {
    // Report annotation
    return reportAnnotationKey(state.selectedTopic, state.selectedRun);
  }
  return null;
}

function currentAnnotation() {
  // Annotation type is determined by what's selected, not by mode
  if (state.selectedTopic && state.selectedRun && state.selectedSentenceIdx !== null) {
    // Citation annotation
    var report = reportIndex[state.selectedTopic] && reportIndex[state.selectedTopic][state.selectedRun];
    if (!report || !report.sentences || state.selectedSentenceIdx >= report.sentences.length) return null;
    var sent = report.sentences[state.selectedSentenceIdx];
    var citations = (sent.citations && sent.citations.length > 0) ? sent.citations : [null];
    var citIdx = state.selectedCitationIdx || 0;
    var docId = citations[citIdx] || null;
    return getCitationAnnotation(state.selectedTopic, state.selectedRun, state.selectedSentenceIdx, docId);
  }
  if (state.selectedTopic && state.selectedDoc) {
    // Document annotation
    return getDocAnnotation(state.selectedTopic, state.selectedDoc);
  }
  if (state.selectedTopic && state.selectedRun) {
    // Report annotation
    return getReportAnnotation(state.selectedTopic, state.selectedRun);
  }
  return null;
}

function isAnnotated(topicId, runId) {
  var ann = state.annotations[reportAnnotationKey(topicId, runId)];
  if (!ann) return false;
  return ann.spans.length > 0 || ann.rating !== "Not rated" || ann.comment !== "" ||
         (ann.nugget_clues && ann.nugget_clues.length > 0);
}

function hasNuggetClues(topicId, runId) {
  var ann = state.annotations[reportAnnotationKey(topicId, runId)];
  if (!ann) return false;
  return ann.nugget_clues && ann.nugget_clues.length > 0;
}

function hasDocNuggetClues(topicId, docId) {
  var ann = state.annotations[docAnnotationKey(topicId, docId)];
  if (!ann) return false;
  return ann.nugget_clues && ann.nugget_clues.length > 0;
}

function isDocAnnotated(topicId, docId) {
  var ann = state.annotations[docAnnotationKey(topicId, docId)];
  if (!ann) return false;
  return ann.spans.length > 0 || ann.rating !== "Not rated" || ann.comment !== "";
}

// --- Auto-save: persist annotations + rebuild JSONL ---

function autoSave() {
  // Stamp current username onto the active annotation
  var ann = currentAnnotation();
  if (ann) ann.username = usernameInput.value.trim();
  // Persist annotation state
  localStorage.setItem("autojudge_annotate_state_" + DATA.dataset, JSON.stringify(state.annotations));
  // Update output textarea if visible
  var outputArea = document.getElementById("output-area");
  if (outputArea) {
    outputArea.value = buildOutputLines().join("\n");
  }
  // Update output count
  var outputHeader = document.getElementById("output-header");
  if (outputHeader) {
    var count = Object.keys(state.annotations).filter(function(k) {
      return isAnnotatedByKey(k);
    }).length;
    outputHeader.textContent = "JSONL Output (" + count + " annotations)";
  }
  // Update sidebar counts without full re-render (avoid losing focus)
  updateSidebarCounts();
  // Trigger debounced sync if online mode is active
  if (typeof syncCurrentAnnotationDebounced === "function") syncCurrentAnnotationDebounced();
}

function isAnnotatedByKey(key) {
  var ann = state.annotations[key];
  if (!ann) return false;
  var hasNuggetClues = ann.nugget_clues && ann.nugget_clues.length > 0;
  if (key.indexOf("c|") === 0) {
    return (ann.spans && ann.spans.length > 0) || (ann.reportSpans && ann.reportSpans.length > 0) || ann.rating !== "Not rated" || ann.comment !== "" || hasNuggetClues;
  }
  return ann.spans.length > 0 || ann.rating !== "Not rated" || ann.comment !== "" || hasNuggetClues;
}

function buildOutputRecords(includeAll) {
  var records = [];
  var fallbackUsername = usernameInput.value.trim();
  Object.keys(state.annotations).forEach(function(key) {
    var ann = state.annotations[key];
    var username = ann.username || fallbackUsername;
    if (!includeAll && !isAnnotatedByKey(key)) return;

    // Determine annotation type via key prefix
    if (key.indexOf("c|") === 0) {
      // Citation annotation
      var topicId = ann.topicId;
      var runId = ann.runId;
      var sentIdx = ann.sentenceIdx;
      var docId = ann.docId;
      var report = reportIndex[topicId] && reportIndex[topicId][runId];
      if (!report || !report.sentences || sentIdx >= report.sentences.length) return;
      var sent = report.sentences[sentIdx];
      var doc = null;
      if (docId) {
        doc = (report.documents && report.documents[docId]) || (docIndex[topicId] && docIndex[topicId][docId]) || null;
      }
      var obj = {
        dataset: DATA.dataset,
        request_id: topicId,
        topic_id: topicId,
        username: username || "",
        rating: ann.rating,
        comment: ann.comment,
        spans: (ann.spans || []).map(function(s) {
          return { start: s.start, end: s.end, text: s.text };
        }),
        report_spans: (ann.reportSpans || []).map(function(s) {
          return { start: s.start, end: s.end, text: s.text };
        }),
        nugget_clues: (ann.nugget_clues || []).map(function(clue) {
          return {
            clue_type: clue.clue_type,
            comment: clue.comment || "",
            spans: (clue.spans || []).map(function(s) {
              return { start: s.start, end: s.end, text: s.text };
            }),
            linked_nugget_id: clue.linked_nugget_id || null
          };
        }),
        citation: {
          report: report,
          sentence_idx: sentIdx,
          sentence: { text: sent.text, citations: sent.citations || [] },
          docid: docId || null,
          document: doc
        }
      };
      records.push({key: key, record: obj});
    } else if (ann.docId !== undefined && key.indexOf("d|") === 0) {
      // Document annotation
      var topicId = ann.topicId;
      var docId = ann.docId;
      var doc = docIndex[topicId] && docIndex[topicId][docId];
      if (!doc) return;
      var obj = {
        dataset: DATA.dataset,
        request_id: topicId,
        docid: docId,
        topic_id: topicId,
        username: username || "",
        rating: ann.rating,
        comment: ann.comment,
        spans: ann.spans.map(function(s) {
          return { start: s.start, end: s.end, text: s.text };
        }),
        nugget_clues: (ann.nugget_clues || []).map(function(clue) {
          return {
            clue_type: clue.clue_type,
            comment: clue.comment || "",
            spans: (clue.spans || []).map(function(s) {
              return { start: s.start, end: s.end, text: s.text };
            }),
            linked_nugget_id: clue.linked_nugget_id || null
          };
        }),
        document: doc
      };
      records.push({key: key, record: obj});
    } else {
      // Report annotation
      var topicId = ann.topicId;
      var runId = ann.runId;
      // Backwards compat: old annotations may not have topicId/runId fields
      if (!topicId || !runId) {
        var parts = key.split("|");
        topicId = topicId || parts[1] || parts[0];
        runId = runId || parts[2] || parts[1];
      }
      var report = reportIndex[topicId] && reportIndex[topicId][runId];
      if (!report) return;
      var obj = {
        dataset: DATA.dataset,
        request_id: topicId,
        run_id: runId,
        team_id: report.team_id,
        topic_id: topicId,
        username: username || "",
        rating: ann.rating,
        comment: ann.comment,
        spans: ann.spans.map(function(s) {
          var o = { start: s.start, end: s.end, text: s.text };
          if (s.sentence_idx !== undefined) o.sentence_idx = s.sentence_idx;
          return o;
        }),
        nugget_clues: (ann.nugget_clues || []).map(function(clue) {
          return {
            clue_type: clue.clue_type,
            comment: clue.comment || "",
            spans: (clue.spans || []).map(function(s) {
              return { start: s.start, end: s.end, text: s.text };
            }),
            linked_nugget_id: clue.linked_nugget_id || null
          };
        }),
        report: report
      };
      records.push({key: key, record: obj});
    }
  });
  return records;
}

function buildOutputLines() {
  return buildOutputRecords().map(function(r) { return JSON.stringify(r.record); });
}

// --- Centralized Reset Function ---
// Call this when clearing all annotations to ensure all UI state is reset.
// Add new UI state variables here when adding new features.

function resetAllAnnotationState() {
  // 1. Clear annotation data
  state.annotations = {};
  localStorage.removeItem("autojudge_annotate_state_" + DATA.dataset);

  // 2. Reset nugget clue UI state
  if (typeof pendingClueType !== "undefined") {
    pendingClueType = "must_have";
  }
  if (typeof clueCreationMode !== "undefined") {
    clueCreationMode = false;
  }

  // 3. Reset nugget mode state (weights, enabled nuggets, user grades, collapsed state, solo)
  state.enabledNuggets = {};
  state.nuggetWeights = { must: 1.0, should: 1.0, avoid: -1.0 };
  state.nuggetPanelCollapsed = {};
  state.soloNuggetId = null;
  state.preSoloEnabledNuggets = null;
  state.preSoloNuggetIds = null;
  state.userNuggetGrades = {};
  localStorage.removeItem("autojudge_annotate_grades_" + DATA.dataset);

  // 4. Force fresh annotation objects by clearing and restoring selection
  // This ensures no stale references persist
  var savedTopic = state.selectedTopic;
  var savedRun = state.selectedRun;
  var savedDoc = state.selectedDoc;
  var savedSentenceIdx = state.selectedSentenceIdx;
  var savedCitationIdx = state.selectedCitationIdx;

  // Temporarily clear selections
  state.selectedTopic = null;
  state.selectedRun = null;
  state.selectedDoc = null;
  state.selectedSentenceIdx = null;
  state.selectedCitationIdx = null;

  // Render empty state (no form fields shown)
  renderSidebar();
  renderMain();

  // Restore selections - this creates FRESH annotation objects
  state.selectedTopic = savedTopic;
  state.selectedRun = savedRun;
  state.selectedDoc = savedDoc;
  state.selectedSentenceIdx = savedSentenceIdx;
  state.selectedCitationIdx = savedCitationIdx;

  // Final render with clean state
  renderSidebar();
  renderMain();
}
"""
