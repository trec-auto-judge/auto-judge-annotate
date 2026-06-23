"""JS state management: data, state object, DOM refs, indexing, annotation helpers, auto-save, buildOutputLines."""

JS_STATE = r"""
// Data injected by generate_html.py
var DATA = /* __DATA_PLACEHOLDER__ */ null;

if (!DATA) { document.body.innerHTML = "<p>Error: No data embedded.</p>"; return; }

// State
var state = {
  // Phase management (new nugget-centric UI)
  phase: "creation",  // "creation" | "qc" | "observe"
  navHistory: [],  // [{phase, topicId, runId}] for back button
  rankingScope: "all",  // "all" | "single" for observe mode toggle

  // Selection state
  selectedTopic: null,
  selectedRun: null,
  selectedDoc: null,
  selectedSentenceIdx: null,
  selectedCitationIdx: null,
  expandedRuns: {},  // "topicId|runId" -> boolean
  mode: "documents",   // "documents" or "citations" (controls fold-out content)
  annotations: {},   // key = "r|topicId|runId" or "d|topicId|docId" or "c|topicId|runId|sentIdx|docId" -> annotation

  // Draft card state (new nugget creation)
  draftState: {
    visible: false,
    spans: [],  // [{start, end, text}]
    freetext: "",
    nuggetText: "",
    category: "must_have",  // "must_have" | "should_have" | "avoid"
    canonicalized: false,
    impactVisible: false,
    impactResults: []  // [{runId, quote, confidence}]
  },

  // Nuggets mode state
  enabledNuggets: {},  // nugget_id -> boolean (default true)
  nuggetWeights: { must: 1.0, should: 1.0, avoid: -1.0 },  // category -> weight
  nuggetPanelCollapsed: {},  // "panel" | "must_have" | "should_have" | "avoid" | "claims" -> boolean
  soloNuggetId: null,  // nugget_id of currently soloed nugget (null = no solo)
  preSoloEnabledNuggets: null,  // snapshot of enabledNuggets before solo (to restore)
  preSoloNuggetIds: null,  // list of nugget IDs that existed before solo (to detect new nuggets)
  // User-generated nugget grades (from LLM grading)
  userNuggetGrades: {},  // topicId -> runId -> nuggetId -> {grade, reasoning, confidence, addressed_quote}
  // User-generated document grades (from "Grade Docs" button)
  userDocGrades: {},  // topicId -> docId -> nuggetId -> {grade, reasoning, confidence, addressed_quote, paragraphs}
  // Heavy highlight for addressed_quote (toggle via clicking "(report)")
  heavyHighlightNuggetId: null  // nugget_id to show with heavy highlight (null = none)
};

// DOM refs
var usernameInput = document.getElementById("username-input");
var navPanel = document.getElementById("navPanel");
var sourcePanel = document.getElementById("sourcePanel");
var sourceContent = document.getElementById("sourceContent");
var rankingPanel = document.getElementById("rankingPanel");
var rankingList = document.getElementById("rankingList");
var nuggetsPanel = document.getElementById("nuggetsPanel");
var modalOverlay = document.getElementById("modal-overlay");
var modalTitle = document.getElementById("modal-title");
var modalUrl = document.getElementById("modal-url");
var modalText = document.getElementById("modal-text");
var modalClose = document.getElementById("modal-close");
var selectionPrompt = document.getElementById("selectionPrompt");

// Legacy refs (for backwards compatibility with existing modules)
var mainPanel = sourcePanel;  // Alias for existing code
var modeSelect = null;  // No longer used in new UI
var datasetLabel = null;  // Moved to a different location
var navTree = navPanel;  // Alias for existing code

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
// Dataset label is shown in top bar via title (set in HTML generation)
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

// Load saved mode from localStorage (legacy, kept for backwards compatibility)
var savedMode = localStorage.getItem("autojudge_annotate_mode_" + DATA.dataset);
if (savedMode === "documents" || savedMode === "citations") {
  state.mode = savedMode;
} else if (savedMode === "reports" || savedMode === "nuggets") {
  // Migrate legacy modes to "documents"
  state.mode = "documents";
}

// Load saved phase from localStorage
var savedPhase = localStorage.getItem("autojudge_annotate_phase_" + DATA.dataset);
if (savedPhase === "creation" || savedPhase === "qc" || savedPhase === "observe") {
  state.phase = savedPhase;
}

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

// Load saved user doc grades from localStorage
var savedUserDocGrades = localStorage.getItem("autojudge_annotate_docgrades_" + DATA.dataset);
if (savedUserDocGrades) {
  try {
    state.userDocGrades = JSON.parse(savedUserDocGrades);
  } catch(e) { state.userDocGrades = {}; }
}

// Save user doc grades to localStorage
function saveUserDocGrades() {
  localStorage.setItem("autojudge_annotate_docgrades_" + DATA.dataset, JSON.stringify(state.userDocGrades));
}

// Save phase to localStorage (called from setPhase in template_js_phase.py)
function savePhase() {
  localStorage.setItem("autojudge_annotate_phase_" + DATA.dataset, state.phase);
}

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

  // 3. Reset nugget mode state (weights, enabled nuggets, user grades, collapsed state, solo, heavy highlight)
  state.enabledNuggets = {};
  state.nuggetWeights = { must: 1.0, should: 1.0, avoid: -1.0 };
  state.nuggetPanelCollapsed = {};
  state.soloNuggetId = null;
  state.preSoloEnabledNuggets = null;
  state.preSoloNuggetIds = null;
  state.userNuggetGrades = {};
  state.heavyHighlightNuggetId = null;
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

// Scrub quote text from LLM output - clean up common formatting issues
// This is defined early so it's available to all modules
function scrubQuote(quote) {
    if (!quote) return '';

    var scrubbed = quote;

    // Remove surrounding quotes (single, double, escaped)
    scrubbed = scrubbed.replace(/^["'`]+|["'`]+$/g, '');
    scrubbed = scrubbed.replace(/^\\"|\\"$/g, '');
    scrubbed = scrubbed.replace(/^\\'|\\'$/g, '');

    // Remove markdown formatting
    scrubbed = scrubbed.replace(/^\*+|\*+$/g, '');
    scrubbed = scrubbed.replace(/^_+|_+$/g, '');

    // Handle escaped newlines
    scrubbed = scrubbed.replace(/\\n/g, ' ');

    // Handle HTML entities
    scrubbed = scrubbed.replace(/&quot;/g, '"');
    scrubbed = scrubbed.replace(/&apos;/g, "'");
    scrubbed = scrubbed.replace(/&amp;/g, '&');
    scrubbed = scrubbed.replace(/&lt;/g, '<');
    scrubbed = scrubbed.replace(/&gt;/g, '>');

    // Normalize whitespace
    scrubbed = scrubbed.replace(/\s+/g, ' ').trim();

    // Handle ellipsis variations
    scrubbed = scrubbed.replace(/\.{3,}/g, '...');
    scrubbed = scrubbed.replace(/…/g, '...');

    // Remove [sic] annotations
    scrubbed = scrubbed.replace(/\s*\[sic\]\s*/gi, ' ');

    // Remove leading/trailing punctuation that might have been added
    scrubbed = scrubbed.replace(/^[,;:\s]+|[,;:\s]+$/g, '');

    return scrubbed;
}

// Normalize text for fuzzy matching - handles Unicode variations
// Used for both source text and quote text before comparison
function normalizeForMatching(text) {
    if (!text) return '';

    var norm = text;

    // Normalize curly/smart quotes to straight quotes
    norm = norm.replace(/[\u2018\u2019\u201A\u201B]/g, "'");  // Single quotes
    norm = norm.replace(/[\u201C\u201D\u201E\u201F]/g, '"');  // Double quotes
    norm = norm.replace(/[\u00AB\u00BB]/g, '"');              // Guillemets

    // Normalize dashes
    norm = norm.replace(/[\u2010\u2011\u2012\u2013\u2014\u2015]/g, '-');  // Various dashes to hyphen

    // Normalize special whitespace
    norm = norm.replace(/[\u00A0\u2000-\u200B\u202F\u205F\u3000]/g, ' ');  // Various spaces to regular space

    // Normalize ellipsis
    norm = norm.replace(/\u2026/g, '...');

    // Remove zero-width characters
    norm = norm.replace(/[\u200B-\u200D\uFEFF]/g, '');

    // Collapse whitespace and lowercase
    norm = norm.replace(/\s+/g, ' ').trim().toLowerCase();

    return norm;
}

// Split a long passage into chunks with overlap for processing
// Returns array of {text, startOffset} objects
// chunkSize: target size of each chunk (default 6000)
// overlap: overlap between chunks (default 1000)
function chunkPassage(passage, chunkSize, overlap) {
    chunkSize = chunkSize || 6000;
    overlap = overlap || 1000;

    if (!passage || passage.length <= chunkSize) {
        return [{ text: passage || '', startOffset: 0 }];
    }

    var chunks = [];
    var pos = 0;

    while (pos < passage.length) {
        var end = Math.min(pos + chunkSize, passage.length);

        // Try to end at a sentence boundary if possible
        if (end < passage.length) {
            var lastPeriod = passage.lastIndexOf('. ', end);
            var lastNewline = passage.lastIndexOf('\n', end);
            var boundary = Math.max(lastPeriod, lastNewline);

            // Only use boundary if it's reasonably close to target end
            if (boundary > pos + chunkSize * 0.7) {
                end = boundary + 1;
            }
        }

        chunks.push({
            text: passage.substring(pos, end),
            startOffset: pos
        });

        // Move position, accounting for overlap
        pos = end - overlap;

        // Avoid infinite loop if overlap >= chunk size
        if (pos <= chunks[chunks.length - 1].startOffset) {
            pos = end;
        }
    }

    return chunks;
}
"""
