"""Self-contained HTML template for the annotation interface."""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AutoJudge Annotation Interface</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; color: #222; }

/* Top bar */
.topbar { background: #2c3e50; color: #fff; padding: 8px 16px; display: flex; align-items: center; gap: 16px; }
.topbar label { font-weight: 600; }
.topbar input[type=text] { padding: 4px 8px; border: 1px solid #555; border-radius: 4px; background: #3d5166; color: #fff; width: 200px; }
.topbar input[type=text]::placeholder { color: #aaa; }
.username-banner { display: none; background: #e74c3c; color: #fff; text-align: center; padding: 8px; font-weight: 600; font-size: 13px; }
.username-banner.visible { display: block; }
.topbar .dataset-label { margin-left: auto; font-size: 12px; opacity: 0.7; }

/* Layout */
.container { display: flex; height: calc(100vh - 40px); }
.sidebar { width: 260px; min-width: 260px; background: #f5f6fa; border-right: 1px solid #ddd; overflow-y: auto; padding: 12px; }
.main-panel { flex: 1; overflow-y: auto; padding: 24px 32px; }

/* Sidebar */
.sidebar h3 { font-size: 13px; text-transform: uppercase; color: #888; margin: 12px 0 6px 0; letter-spacing: 0.5px; }
.sidebar h3:first-child { margin-top: 0; }
.topic-item, .run-item { padding: 6px 10px; cursor: pointer; border-radius: 4px; margin-bottom: 2px; display: flex; align-items: center; gap: 6px; }
.topic-item:hover, .run-item:hover { background: #e0e4ed; }
.topic-item.active { background: #3498db; color: #fff; }
.run-item.active { background: #3498db; color: #fff; }
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
.report-text mark { background: #ffeaa7; border-radius: 2px; position: relative; cursor: pointer; }
.report-text mark .remove-span { display: none; position: absolute; top: -8px; right: -6px; width: 16px; height: 16px; background: #e74c3c; color: #fff; border-radius: 50%; font-size: 10px; line-height: 16px; text-align: center; cursor: pointer; z-index: 10; }
.report-text mark:hover .remove-span { display: block; }
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
</style>
</head>
<body>

<div class="topbar">
  <label for="username-input">Username:</label>
  <input type="text" id="username-input" placeholder="Enter your name...">
  <span class="dataset-label" id="dataset-label"></span>
</div>
<div class="username-banner" id="username-banner">Please enter a username above before annotating.</div>

<div class="container">
  <div class="sidebar" id="sidebar">
    <h3>Topics</h3>
    <div id="topic-list"></div>
    <h3>Runs</h3>
    <div id="run-list"></div>
    <button class="clear-all-btn" id="clear-all-btn">Clear all annotations</button>
  </div>
  <div class="main-panel" id="main-panel">
    <div class="empty-state">Select a topic and run from the sidebar to begin annotating.</div>
  </div>
</div>

<div class="modal-overlay" id="modal-overlay">
  <div class="modal" id="modal">
    <h3 id="modal-title"></h3>
    <a class="doc-url" id="modal-url" target="_blank" rel="noopener"></a>
    <div class="doc-text" id="modal-text"></div>
    <button class="close-btn" id="modal-close">Close</button>
  </div>
</div>

<script>
(function() {
"use strict";

// Data injected by generate_html.py
var DATA = /* __DATA_PLACEHOLDER__ */ null;

if (!DATA) { document.body.innerHTML = "<p>Error: No data embedded.</p>"; return; }

// State
var state = {
  selectedTopic: null,
  selectedRun: null,
  annotations: {}   // key = "topicId|runId" -> {rating, comment, spans: [{start,end,text}]}
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

// Index data
var requestMap = {};  // request_id -> request
var reportIndex = {}; // topic_id -> {run_id -> report}
var topicIds = [];

DATA.requests.forEach(function(r) { requestMap[r.request_id] = r; });
DATA.reports.forEach(function(r) {
  if (!reportIndex[r.topic_id]) reportIndex[r.topic_id] = {};
  reportIndex[r.topic_id][r.run_id] = r;
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
  try { state.annotations = JSON.parse(savedAnnotations); } catch(e) { state.annotations = {}; }
}

// --- Annotation helpers ---

function annotationKey(topicId, runId) { return topicId + "|" + runId; }

function getAnnotation(topicId, runId) {
  var key = annotationKey(topicId, runId);
  if (!state.annotations[key]) {
    state.annotations[key] = { rating: "Not rated", comment: "", spans: [] };
  }
  return state.annotations[key];
}

function currentAnnotation() {
  if (!state.selectedTopic || !state.selectedRun) return null;
  return getAnnotation(state.selectedTopic, state.selectedRun);
}

function isAnnotated(topicId, runId) {
  var ann = state.annotations[annotationKey(topicId, runId)];
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
  return ann.spans.length > 0 || ann.rating !== "Not rated" || ann.comment !== "";
}

function buildOutputLines() {
  var lines = [];
  var username = usernameInput.value.trim();
  Object.keys(state.annotations).forEach(function(key) {
    var ann = state.annotations[key];
    if (!isAnnotatedByKey(key)) return;
    var parts = key.split("|");
    var topicId = parts[0];
    var runId = parts[1];
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
  });
  return lines;
}

// --- Sidebar ---

function escapeHtml(str) {
  var div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

function updateSidebarCounts() {
  // Update topic progress counts and run checkmarks without full re-render
  topicIds.forEach(function(tid) {
    var countEl = document.getElementById("topic-count-" + tid);
    if (countEl) {
      var runs = reportIndex[tid] ? Object.keys(reportIndex[tid]) : [];
      var done = runs.filter(function(rid) { return isAnnotated(tid, rid); }).length;
      countEl.textContent = "(" + done + "/" + runs.length + ")";
    }
  });
  if (state.selectedTopic && reportIndex[state.selectedTopic]) {
    Object.keys(reportIndex[state.selectedTopic]).forEach(function(rid) {
      var checkEl = document.getElementById("run-check-" + rid);
      if (checkEl) {
        checkEl.innerHTML = isAnnotated(state.selectedTopic, rid) ? "&#10003;" : "";
      }
    });
  }
}

function renderSidebar() {
  topicList.innerHTML = "";
  topicIds.forEach(function(tid) {
    var runs = reportIndex[tid] ? Object.keys(reportIndex[tid]).sort() : [];
    var done = runs.filter(function(rid) { return isAnnotated(tid, rid); }).length;

    var el = document.createElement("div");
    el.className = "topic-item" + (state.selectedTopic === tid ? " active" : "");
    el.innerHTML = escapeHtml(tid) + '<span class="progress" id="topic-count-' + escapeHtml(tid) + '">(' + done + "/" + runs.length + ")</span>";
    el.addEventListener("click", function() {
      state.selectedTopic = tid;
      // Keep current run if it exists for the new topic, otherwise fall back to first
      var availableRuns = reportIndex[tid] ? Object.keys(reportIndex[tid]).sort() : [];
      if (state.selectedRun && availableRuns.indexOf(state.selectedRun) === -1) {
        state.selectedRun = availableRuns.length > 0 ? availableRuns[0] : null;
      } else if (!state.selectedRun && availableRuns.length > 0) {
        state.selectedRun = availableRuns[0];
      }
      renderSidebar();
      renderMain();
    });
    topicList.appendChild(el);
  });

  runList.innerHTML = "";
  if (state.selectedTopic && reportIndex[state.selectedTopic]) {
    var runs = Object.keys(reportIndex[state.selectedTopic]).sort();
    runs.forEach(function(rid) {
      var report = reportIndex[state.selectedTopic][rid];
      var el = document.createElement("div");
      el.className = "run-item" + (state.selectedRun === rid ? " active" : "");
      var label = escapeHtml(rid) + " (" + escapeHtml(report.team_id) + ")";
      var checkContent = isAnnotated(state.selectedTopic, rid) ? "&#10003;" : "";
      el.innerHTML = label + '<span class="checkmark" id="run-check-' + escapeHtml(rid) + '">' + checkContent + '</span>';
      el.addEventListener("click", function() {
        state.selectedRun = rid;
        renderSidebar();
        renderMain();
      });
      runList.appendChild(el);
    });
  }
}

// --- Main panel ---

function renderMain() {
  if (!state.selectedTopic) {
    mainPanel.innerHTML = '<div class="empty-state">Select a topic from the sidebar to begin.</div>';
    return;
  }

  var request = requestMap[state.selectedTopic];
  var html = '<div class="request-section">';
  html += "<h2>Request: " + escapeHtml(state.selectedTopic) + "</h2>";
  if (request) {
    html += '<div class="field-label">Title</div>';
    html += '<div class="field-value">' + escapeHtml(request.title || "") + "</div>";
    if (request.problem_statement) {
      html += '<div class="field-label">Problem Statement</div>';
      html += '<div class="field-value">' + escapeHtml(request.problem_statement) + "</div>";
    }
    if (request.background) {
      html += '<div class="field-label">Background</div>';
      html += '<div class="field-value">' + escapeHtml(request.background) + "</div>";
    }
  }
  html += "</div>";

  if (!state.selectedRun) {
    html += '<div class="empty-state">Select a run from the sidebar.</div>';
    mainPanel.innerHTML = html;
    return;
  }

  var report = reportIndex[state.selectedTopic][state.selectedRun];
  if (!report) {
    html += '<div class="empty-state">Report not found.</div>';
    mainPanel.innerHTML = html;
    return;
  }

  var ann = getAnnotation(state.selectedTopic, state.selectedRun);

  html += '<div class="report-section">';
  html += "<h2>Report: " + escapeHtml(report.run_id) + " by " + escapeHtml(report.team_id) + "</h2>";
  html += '<div class="report-text" id="report-text"></div>';
  html += "</div>";

  // Spans list
  html += '<div class="spans-section"><h3>Selected Spans</h3><div id="spans-display"></div></div>';

  // Rating
  html += '<div class="rating-section"><h3>Rating</h3><div class="rating-options">';
  ["Not rated", "Perfect", "Mostly Good", "So-so", "Bad"].forEach(function(r) {
    var checked = (ann.rating === r) ? " checked" : "";
    html += '<label><input type="radio" name="rating" value="' + escapeHtml(r) + '"' + checked + '><span>' + escapeHtml(r) + "</span></label>";
  });
  html += "</div></div>";

  // Comment
  html += '<div class="comment-section"><h3>Comments</h3>';
  html += '<textarea id="comment-input" placeholder="Optional comments...">' + escapeHtml(ann.comment) + '</textarea></div>';

  // Output section
  var annotatedCount = Object.keys(state.annotations).filter(function(k) { return isAnnotatedByKey(k); }).length;
  html += '<div class="output-section"><h3 id="output-header">JSONL Output (' + annotatedCount + ' annotations)</h3>';
  html += '<textarea id="output-area" readonly></textarea>';
  html += '<button class="download-btn" id="download-btn">Download JSONL</button></div>';

  mainPanel.innerHTML = html;

  // Populate output area
  var outputArea = document.getElementById("output-area");
  outputArea.value = buildOutputLines().join("\n");

  // Build report text safely using DOM manipulation
  var reportTextEl = document.getElementById("report-text");
  buildReportText(reportTextEl, report);
  applyHighlights(reportTextEl, ann.spans);

  // Attach event handlers
  reportTextEl.addEventListener("mouseup", handleSelection);
  document.getElementById("download-btn").addEventListener("click", handleDownload);

  // Auto-save on rating change
  document.querySelectorAll('input[name="rating"]').forEach(function(radio) {
    radio.addEventListener("change", function() {
      var ann = currentAnnotation();
      if (ann) { ann.rating = this.value; autoSave(); }
    });
  });

  // Auto-save on comment change
  document.getElementById("comment-input").addEventListener("input", function() {
    var ann = currentAnnotation();
    if (ann) { ann.comment = this.value.trim(); autoSave(); }
  });

  renderSpans();
}

// --- Report text rendering ---

function buildReportText(container, report) {
  container.innerHTML = "";
  report.sentences.forEach(function(sent, idx) {
    if (idx > 0) container.appendChild(document.createTextNode(" "));
    var textNode = document.createTextNode(sent.text);
    container.appendChild(textNode);

    if (sent.citations && sent.citations.length > 0) {
      sent.citations.forEach(function(cid) {
        var span = document.createElement("span");
        span.className = "citation-marker";
        span.textContent = "[" + cid + "]";
        span.setAttribute("data-citation-id", cid);
        if (DATA.show_documents) {
          span.addEventListener("click", function(e) {
            e.stopPropagation();
            showCitationModal(report, cid);
          });
        }
        container.appendChild(span);
      });
    }
  });
}

// Build the plain text from report sentences (no citation markers)
function buildPlainText(report) {
  return report.sentences.map(function(s) { return s.text; }).join(" ");
}

// Build sentence boundary map: [{start, end, sentence_idx}]
// The plain text is: "sent0 sent1 sent2" with single-space separators
function buildSentenceBoundaries(report) {
  var boundaries = [];
  var pos = 0;
  report.sentences.forEach(function(sent, idx) {
    if (idx > 0) pos += 1; // space separator
    var start = pos;
    pos += sent.text.length;
    boundaries.push({ start: start, end: pos, sentence_idx: idx });
  });
  return boundaries;
}

// Split a raw selection into per-sentence subspans
// Uses plain text (not sel.toString()) to extract subspan text
function splitIntoSentenceSpans(start, end, report) {
  var plainText = buildPlainText(report);
  var boundaries = buildSentenceBoundaries(report);
  var subspans = [];
  boundaries.forEach(function(b) {
    var overlapStart = Math.max(start, b.start);
    var overlapEnd = Math.min(end, b.end);
    if (overlapStart < overlapEnd) {
      var text = plainText.substring(overlapStart, overlapEnd).trim();
      if (text) {
        subspans.push({
          start: overlapStart,
          end: overlapEnd,
          text: text,
          sentence_idx: b.sentence_idx
        });
      }
    }
  });
  return subspans;
}

// --- Highlight / span logic ---

function collectTextNodes(container) {
  var textNodes = [];
  var nodeStarts = [];
  var pos = 0;
  function walk(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      textNodes.push(node);
      nodeStarts.push(pos);
      pos += node.textContent.length;
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      if (node.classList && node.classList.contains("citation-marker")) return;
      if (node.classList && node.classList.contains("remove-span")) return;
      for (var i = 0; i < node.childNodes.length; i++) {
        walk(node.childNodes[i]);
      }
    }
  }
  walk(container);
  return { textNodes: textNodes, nodeStarts: nodeStarts };
}

function applyHighlights(reportTextEl, spans) {
  if (!spans || spans.length === 0) return;

  // Apply spans in reverse order to avoid invalidating offsets
  var sorted = spans.slice().sort(function(a, b) { return b.start - a.start; });
  sorted.forEach(function(sp) {
    var spanIndex = spans.indexOf(sp);
    var info = collectTextNodes(reportTextEl);
    wrapRange(info.textNodes, info.nodeStarts, sp, spanIndex);
  });
}

function wrapRange(textNodes, nodeStarts, span, spanIndex) {
  var isFirst = true;
  for (var i = 0; i < textNodes.length; i++) {
    var nodeStart = nodeStarts[i];
    var nodeEnd = nodeStart + textNodes[i].textContent.length;

    if (span.start >= nodeEnd) continue;
    if (span.end <= nodeStart) break;

    var localStart = Math.max(0, span.start - nodeStart);
    var localEnd = Math.min(textNodes[i].textContent.length, span.end - nodeStart);

    var range = document.createRange();
    range.setStart(textNodes[i], localStart);
    range.setEnd(textNodes[i], localEnd);

    var mark = document.createElement("mark");
    range.surroundContents(mark);

    // Only show remove button on first fragment of the span
    if (isFirst) {
      var removeBtn = document.createElement("span");
      removeBtn.className = "remove-span";
      removeBtn.textContent = "x";
      removeBtn.setAttribute("data-span-index", spanIndex);
      removeBtn.addEventListener("click", function(e) {
        e.stopPropagation();
        e.preventDefault();
        var idx = parseInt(this.getAttribute("data-span-index"));
        var ann = currentAnnotation();
        if (ann) {
          ann.spans.splice(idx, 1);
          autoSave();
          var reportTextEl = document.getElementById("report-text");
          var report = reportIndex[state.selectedTopic][state.selectedRun];
          buildReportText(reportTextEl, report);
          applyHighlights(reportTextEl, ann.spans);
          reportTextEl.addEventListener("mouseup", handleSelection);
          renderSpans();
        }
      });
      mark.appendChild(removeBtn);
      isFirst = false;
    }
  }
}

function handleSelection() {
  var sel = window.getSelection();
  if (!sel || sel.isCollapsed || sel.rangeCount === 0) return;

  var reportTextEl = document.getElementById("report-text");
  if (!reportTextEl) return;

  var range = sel.getRangeAt(0);
  if (!reportTextEl.contains(range.startContainer) || !reportTextEl.contains(range.endContainer)) return;

  var selectedText = sel.toString().trim();
  if (!selectedText) return;

  var offset = computeOffset(reportTextEl, range);
  if (offset === null) return;

  var ann = currentAnnotation();
  if (!ann) return;

  // Split into per-sentence subspans (text derived from plain text, not selection)
  var report = reportIndex[state.selectedTopic][state.selectedRun];
  var subspans = splitIntoSentenceSpans(offset.start, offset.end, report);

  if (subspans.length === 0) { sel.removeAllRanges(); return; }

  // Avoid exact duplicates
  subspans = subspans.filter(function(sp) {
    return !ann.spans.some(function(s) { return s.start === sp.start && s.end === sp.end; });
  });
  if (subspans.length === 0) { sel.removeAllRanges(); return; }

  subspans.forEach(function(sp) { ann.spans.push(sp); });
  ann.spans.sort(function(a, b) { return a.start - b.start; });

  sel.removeAllRanges();
  autoSave();

  // Re-render highlights
  buildReportText(reportTextEl, report);
  applyHighlights(reportTextEl, ann.spans);
  reportTextEl.addEventListener("mouseup", handleSelection);
  renderSpans();
}

function computeOffset(container, range) {
  var startOff = 0;
  var endOff = 0;
  var foundStart = false;
  var foundEnd = false;
  var charPos = 0;

  function walk(node) {
    if (foundEnd) return;
    if (node.nodeType === Node.TEXT_NODE) {
      var len = node.textContent.length;
      if (!foundStart && node === range.startContainer) {
        startOff = charPos + range.startOffset;
        foundStart = true;
      }
      if (!foundEnd && node === range.endContainer) {
        endOff = charPos + range.endOffset;
        foundEnd = true;
      }
      charPos += len;
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      if (node.classList && node.classList.contains("citation-marker")) {
        if (!foundStart && node.contains(range.startContainer)) {
          startOff = charPos;
          foundStart = true;
        }
        if (!foundEnd && node.contains(range.endContainer)) {
          endOff = charPos;
          foundEnd = true;
        }
        return;
      }
      if (node.classList && node.classList.contains("remove-span")) return;
      for (var i = 0; i < node.childNodes.length; i++) {
        walk(node.childNodes[i]);
      }
    }
  }
  walk(container);
  if (!foundStart || !foundEnd || startOff >= endOff) return null;
  return { start: startOff, end: endOff };
}

function renderSpans() {
  var display = document.getElementById("spans-display");
  if (!display) return;
  var ann = currentAnnotation();
  var spans = ann ? ann.spans : [];
  if (spans.length === 0) {
    display.innerHTML = '<span style="color:#888;font-size:12px;">No spans selected. Highlight text above to add spans.</span>';
    return;
  }
  display.innerHTML = "";
  spans.forEach(function(sp) {
    var chip = document.createElement("span");
    chip.className = "span-chip";
    var sentLabel = (sp.sentence_idx !== undefined) ? "s" + sp.sentence_idx + " " : "";
    chip.textContent = sentLabel + "[" + sp.start + "-" + sp.end + "] " + sp.text;
    chip.title = sp.text;
    display.appendChild(chip);
  });
}

// --- Citation modal ---

function showCitationModal(report, citationId) {
  var doc = report.documents[citationId];
  if (!doc) {
    modalTitle.textContent = citationId;
    modalUrl.textContent = "";
    modalUrl.href = "#";
    modalText.textContent = "Document not available.";
  } else {
    modalTitle.textContent = doc.title || citationId;
    if (doc.url) {
      modalUrl.textContent = doc.url;
      modalUrl.href = doc.url;
    } else {
      modalUrl.textContent = "";
      modalUrl.href = "#";
    }
    modalText.textContent = doc.text || "";
  }
  modalOverlay.classList.add("visible");
}

modalClose.addEventListener("click", function() {
  modalOverlay.classList.remove("visible");
});
modalOverlay.addEventListener("click", function(e) {
  if (e.target === modalOverlay) modalOverlay.classList.remove("visible");
});

// --- Download ---

function handleDownload() {
  var lines = buildOutputLines();
  if (lines.length === 0) {
    alert("No annotations to download.");
    return;
  }
  var blob = new Blob([lines.join("\n") + "\n"], { type: "application/jsonl" });
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = DATA.dataset + "-annotations.jsonl";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Clear all annotations
document.getElementById("clear-all-btn").addEventListener("click", function() {
  if (!confirm("Clear ALL annotations for this dataset? This cannot be undone.")) return;
  state.annotations = {};
  localStorage.removeItem("autojudge_annotate_state_" + DATA.dataset);
  renderSidebar();
  renderMain();
});

// Initial render — auto-select first topic and first run
if (topicIds.length > 0) {
  state.selectedTopic = topicIds[0];
  var firstRuns = reportIndex[topicIds[0]] ? Object.keys(reportIndex[topicIds[0]]).sort() : [];
  if (firstRuns.length > 0) state.selectedRun = firstRuns[0];
}
renderSidebar();
renderMain();

})();
</script>
</body>
</html>
"""
