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
  mode: "reports",   // "reports", "documents", or "citations"
  annotations: {}   // key = "r|topicId|runId" or "d|topicId|docId" or "c|topicId|runId|sentIdx|docId" -> annotation
};

// DOM refs
var usernameInput = document.getElementById("username-input");
var datasetLabel = document.getElementById("dataset-label");
var topicList = document.getElementById("topic-list");
var runList = document.getElementById("run-list");
var mainPanel = document.getElementById("main-panel");
var modalOverlay = document.getElementById("modal-overlay");
var modalTitle = document.getElementById("modal-title");
var modalUrl = document.getElementById("modal-url");
var modalText = document.getElementById("modal-text");
var modalClose = document.getElementById("modal-close");
var modeSelect = document.getElementById("mode-select");
var docListHeader = document.getElementById("doc-list-header");
var docList = document.getElementById("doc-list");
var runListHeader = document.getElementById("run-list-header");
var sentListHeader = document.getElementById("sent-list-header");
var sentList = document.getElementById("sent-list");

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
  autoSave();
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
if (savedMode === "reports" || savedMode === "documents" || savedMode === "citations") {
  state.mode = savedMode;
}
modeSelect.value = state.mode;

modeSelect.addEventListener("change", function() {
  state.mode = modeSelect.value;
  if (state.mode === "documents") {
    // Ensure a run is selected (keep current or pick first)
    if (state.selectedTopic) {
      var availableRuns = reportIndex[state.selectedTopic] ? Object.keys(reportIndex[state.selectedTopic]).sort() : [];
      if (!state.selectedRun || availableRuns.indexOf(state.selectedRun) === -1) {
        state.selectedRun = availableRuns.length > 0 ? availableRuns[0] : null;
      }
      // Auto-select first document of the run
      if (state.selectedRun && runDocsIndex[state.selectedTopic] && runDocsIndex[state.selectedTopic][state.selectedRun]) {
        var docs = runDocsIndex[state.selectedTopic][state.selectedRun];
        state.selectedDoc = docs.length > 0 ? docs[0] : null;
      } else {
        state.selectedDoc = null;
      }
    }
    state.selectedSentenceIdx = null;
    state.selectedCitationIdx = null;
  } else if (state.mode === "citations") {
    // Ensure a run is selected
    if (state.selectedTopic) {
      var availableRuns = reportIndex[state.selectedTopic] ? Object.keys(reportIndex[state.selectedTopic]).sort() : [];
      if (!state.selectedRun || availableRuns.indexOf(state.selectedRun) === -1) {
        state.selectedRun = availableRuns.length > 0 ? availableRuns[0] : null;
      }
    }
    state.selectedSentenceIdx = 0;
    state.selectedCitationIdx = 0;
    state.selectedDoc = null;
  } else {
    state.selectedDoc = null;
    state.selectedSentenceIdx = null;
    state.selectedCitationIdx = null;
  }
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
    state.annotations[key] = { topicId: topicId, runId: runId, rating: "Not rated", comment: "", spans: [] };
  }
  return state.annotations[key];
}

function getDocAnnotation(topicId, docId) {
  var key = docAnnotationKey(topicId, docId);
  if (!state.annotations[key]) {
    state.annotations[key] = { topicId: topicId, docId: docId, rating: "Not rated", comment: "", spans: [] };
  }
  return state.annotations[key];
}

function citationAnnotationKey(topicId, runId, sentIdx, docId) {
  if (docId) return "c|" + topicId + "|" + runId + "|" + sentIdx + "|" + docId;
  return "c|" + topicId + "|" + runId + "|" + sentIdx;
}

function getCitationAnnotation(topicId, runId, sentIdx, docId) {
  var key = citationAnnotationKey(topicId, runId, sentIdx, docId);
  if (!state.annotations[key]) {
    state.annotations[key] = { topicId: topicId, runId: runId, sentenceIdx: sentIdx, docId: docId || null, rating: "Not rated", comment: "", spans: [], reportSpans: [] };
  }
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

function currentAnnotation() {
  if (state.mode === "documents") {
    if (!state.selectedTopic || !state.selectedDoc) return null;
    return getDocAnnotation(state.selectedTopic, state.selectedDoc);
  }
  if (state.mode === "citations") {
    if (!state.selectedTopic || !state.selectedRun || state.selectedSentenceIdx === null) return null;
    var report = reportIndex[state.selectedTopic] && reportIndex[state.selectedTopic][state.selectedRun];
    if (!report || !report.sentences || state.selectedSentenceIdx >= report.sentences.length) return null;
    var sent = report.sentences[state.selectedSentenceIdx];
    var citations = (sent.citations && sent.citations.length > 0) ? sent.citations : [null];
    var citIdx = state.selectedCitationIdx || 0;
    var docId = citations[citIdx] || null;
    return getCitationAnnotation(state.selectedTopic, state.selectedRun, state.selectedSentenceIdx, docId);
  }
  if (!state.selectedTopic || !state.selectedRun) return null;
  return getReportAnnotation(state.selectedTopic, state.selectedRun);
}

function isAnnotated(topicId, runId) {
  var ann = state.annotations[reportAnnotationKey(topicId, runId)];
  if (!ann) return false;
  return ann.spans.length > 0 || ann.rating !== "Not rated" || ann.comment !== "";
}

function isDocAnnotated(topicId, docId) {
  var ann = state.annotations[docAnnotationKey(topicId, docId)];
  if (!ann) return false;
  return ann.spans.length > 0 || ann.rating !== "Not rated" || ann.comment !== "";
}

// --- Auto-save: persist annotations + rebuild JSONL ---

function autoSave() {
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
}

function isAnnotatedByKey(key) {
  var ann = state.annotations[key];
  if (!ann) return false;
  if (key.indexOf("c|") === 0) {
    return (ann.spans && ann.spans.length > 0) || (ann.reportSpans && ann.reportSpans.length > 0) || ann.rating !== "Not rated" || ann.comment !== "";
  }
  return ann.spans.length > 0 || ann.rating !== "Not rated" || ann.comment !== "";
}

function buildOutputLines() {
  var lines = [];
  var username = usernameInput.value.trim();
  Object.keys(state.annotations).forEach(function(key) {
    var ann = state.annotations[key];
    if (!isAnnotatedByKey(key)) return;

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
        citation: {
          report: report,
          sentence_idx: sentIdx,
          sentence: { text: sent.text, citations: sent.citations || [] },
          docid: docId || null,
          document: doc
        }
      };
      lines.push(JSON.stringify(obj));
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
        document: doc
      };
      lines.push(JSON.stringify(obj));
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
        report: report
      };
      lines.push(JSON.stringify(obj));
    }
  });
  return lines;
}
"""
