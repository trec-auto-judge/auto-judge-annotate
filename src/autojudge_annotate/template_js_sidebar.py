"""JS sidebar: unified hierarchical navigation (Topics → Reports → Documents/Sentences)."""

JS_SIDEBAR = r"""
// --- Sidebar ---

function escapeHtml(str) {
  var div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

function abbreviateDocId(docId) {
  if (docId.length > 25) return docId.substring(0, 22) + "\u2026";
  return docId;
}

function runExpandKey(topicId, runId) {
  return topicId + "|" + runId;
}

function isRunExpanded(topicId, runId) {
  return !!state.expandedRuns[runExpandKey(topicId, runId)];
}

function toggleRunExpanded(topicId, runId) {
  var key = runExpandKey(topicId, runId);
  state.expandedRuns[key] = !state.expandedRuns[key];
}

function countCitationSentences(topicId, runId) {
  var report = reportIndex[topicId] && reportIndex[topicId][runId];
  if (!report || !report.sentences) return { done: 0, total: 0 };
  var total = report.sentences.length;
  var done = 0;
  for (var i = 0; i < total; i++) {
    if (isCitationSentenceComplete(topicId, runId, i)) done++;
  }
  return { done: done, total: total };
}

// Determine CSS class for topic row based on selection state
function getTopicClass(topicId) {
  if (state.selectedTopic !== topicId) return "topic-row";
  // Topic is selected - check if viewing topic (ranking) or something under it
  if (!state.selectedRun) return "topic-row active";
  // A report or doc under this topic is selected
  return "topic-row parent-active";
}

// Determine CSS class for report row based on selection state
function getReportClass(topicId, runId) {
  if (state.selectedTopic !== topicId || state.selectedRun !== runId) return "report-row";
  // This report is selected - check if viewing report or a doc/sentence under it
  if (!state.selectedDoc && state.selectedSentenceIdx === null) return "report-row active";
  // A doc or sentence under this report is selected
  return "report-row parent-active";
}

function updateSidebarCounts() {
  // Update checkmarks and counts without full re-render
  // This is called after autoSave to update visual state
  topicIds.forEach(function(tid) {
    var runs = reportIndex[tid] ? Object.keys(reportIndex[tid]) : [];
    runs.forEach(function(rid) {
      // Report clues indicator
      var reportClues = document.getElementById("report-clues-" + CSS.escape(tid) + "-" + CSS.escape(rid));
      if (reportClues) {
        reportClues.innerHTML = hasNuggetClues(tid, rid) ? "&#9776;" : "";
      }
      // Report checkmark
      var reportCheck = document.getElementById("report-check-" + CSS.escape(tid) + "-" + CSS.escape(rid));
      if (reportCheck) {
        reportCheck.innerHTML = isAnnotated(tid, rid) ? "&#10003;" : "";
      }
      // Document clues indicators and checkmarks
      var docs = (runDocsIndex[tid] && runDocsIndex[tid][rid]) || [];
      docs.forEach(function(did) {
        var docClues = document.getElementById("doc-clues-" + CSS.escape(tid) + "-" + CSS.escape(did));
        if (docClues) {
          docClues.innerHTML = hasDocNuggetClues(tid, did) ? "&#9776;" : "";
        }
        var docCheck = document.getElementById("doc-check-" + CSS.escape(tid) + "-" + CSS.escape(did));
        if (docCheck) {
          docCheck.innerHTML = isDocAnnotated(tid, did) ? "&#10003;" : "";
        }
      });
      // Sentence checkmarks (citations mode)
      var report = reportIndex[tid][rid];
      if (report && report.sentences) {
        report.sentences.forEach(function(sent, idx) {
          var sentCheck = document.getElementById("sent-check-" + CSS.escape(tid) + "-" + CSS.escape(rid) + "-" + idx);
          if (sentCheck) {
            sentCheck.innerHTML = isCitationSentenceComplete(tid, rid, idx) ? "&#10003;" : "";
          }
        });
      }
    });
  });
}

function renderSidebar() {
  navTree.innerHTML = "";

  topicIds.forEach(function(tid) {
    // --- Topic row ---
    var topicEl = document.createElement("div");
    topicEl.className = getTopicClass(tid);
    topicEl.textContent = tid;
    topicEl.addEventListener("click", function() {
      state.selectedTopic = tid;
      state.selectedRun = null;
      state.selectedDoc = null;
      state.selectedSentenceIdx = null;
      state.selectedCitationIdx = null;
      if (typeof clearHeavyHighlight === "function") clearHeavyHighlight();
      renderSidebar();
      renderMain();
    });
    navTree.appendChild(topicEl);

    // --- Reports under this topic ---
    var runs = reportIndex[tid] ? Object.keys(reportIndex[tid]).sort() : [];
    runs.forEach(function(rid) {
      var report = reportIndex[tid][rid];
      var isExpanded = isRunExpanded(tid, rid);

      // Report row
      var reportEl = document.createElement("div");
      reportEl.className = getReportClass(tid, rid);

      // Fold arrow
      var arrow = document.createElement("span");
      arrow.className = "fold-arrow";
      arrow.textContent = isExpanded ? "\u25BE" : "\u25B8";
      arrow.addEventListener("click", function(e) {
        e.stopPropagation();
        toggleRunExpanded(tid, rid);
        renderSidebar();
      });
      reportEl.appendChild(arrow);

      // Report name
      var nameSpan = document.createElement("span");
      nameSpan.className = "report-name";
      nameSpan.textContent = rid;
      nameSpan.title = rid + " (" + report.team_id + ")";
      reportEl.appendChild(nameSpan);

      // Nugget coverage badge
      if (typeof countNuggetCoverage === "function") {
        var cov = countNuggetCoverage(tid, rid);
        if (cov.total > 0) {
          var covBadge = document.createElement("span");
          covBadge.className = "nugget-coverage";
          covBadge.textContent = cov.satisfied + "/" + cov.total;
          reportEl.appendChild(covBadge);
        }
      }

      // Clues indicator (hamburger icon)
      var cluesEl = document.createElement("span");
      cluesEl.className = "clues-indicator";
      cluesEl.id = "report-clues-" + CSS.escape(tid) + "-" + CSS.escape(rid);
      cluesEl.innerHTML = hasNuggetClues(tid, rid) ? "&#9776;" : "";
      cluesEl.title = "Has nugget clues";
      reportEl.appendChild(cluesEl);

      // Checkmark for annotated
      var checkEl = document.createElement("span");
      checkEl.className = "checkmark";
      checkEl.id = "report-check-" + CSS.escape(tid) + "-" + CSS.escape(rid);
      checkEl.innerHTML = isAnnotated(tid, rid) ? "&#10003;" : "";
      reportEl.appendChild(checkEl);

      // Click to select report
      reportEl.addEventListener("click", function() {
        state.selectedTopic = tid;
        state.selectedRun = rid;
        state.selectedDoc = null;
        state.selectedSentenceIdx = null;
        state.selectedCitationIdx = null;
        // Auto-expand when selecting
        state.expandedRuns[runExpandKey(tid, rid)] = true;
        if (typeof clearHeavyHighlight === "function") clearHeavyHighlight();
        renderSidebar();
        renderMain();
      });
      navTree.appendChild(reportEl);

      // --- Fold-out content (documents or sentences) ---
      if (isExpanded) {
        var foldout = document.createElement("div");
        foldout.className = "foldout-list";

        if (state.mode === "citations") {
          // Show sentences
          if (report.sentences) {
            report.sentences.forEach(function(sent, idx) {
              var sentEl = document.createElement("div");
              var isActive = state.selectedTopic === tid && state.selectedRun === rid && state.selectedSentenceIdx === idx;
              sentEl.className = "foldout-item" + (isActive ? " active" : "");

              var preview = sent.text.length > 20 ? sent.text.substring(0, 20) + "\u2026" : sent.text;
              var citeCount = (sent.citations && sent.citations.length > 0) ? sent.citations.length : 0;

              var idSpan = document.createElement("span");
              idSpan.className = "foldout-id";
              idSpan.textContent = "s" + idx;
              sentEl.appendChild(idSpan);

              var previewSpan = document.createElement("span");
              previewSpan.className = "foldout-preview";
              previewSpan.textContent = preview;
              previewSpan.title = sent.text;
              sentEl.appendChild(previewSpan);

              if (citeCount > 0) {
                var citeBadge = document.createElement("span");
                citeBadge.className = "cite-count";
                citeBadge.textContent = "[" + citeCount + "]";
                sentEl.appendChild(citeBadge);
              }

              var sentCheck = document.createElement("span");
              sentCheck.className = "checkmark";
              sentCheck.id = "sent-check-" + CSS.escape(tid) + "-" + CSS.escape(rid) + "-" + idx;
              sentCheck.innerHTML = isCitationSentenceComplete(tid, rid, idx) ? "&#10003;" : "";
              sentEl.appendChild(sentCheck);

              sentEl.addEventListener("click", function() {
                state.selectedTopic = tid;
                state.selectedRun = rid;
                state.selectedDoc = null;
                state.selectedSentenceIdx = idx;
                state.selectedCitationIdx = 0;
                if (typeof clearHeavyHighlight === "function") clearHeavyHighlight();
                renderSidebar();
                renderMain();
              });
              foldout.appendChild(sentEl);
            });
          }
        } else {
          // Show documents (default)
          var docs = (runDocsIndex[tid] && runDocsIndex[tid][rid]) || [];
          docs.forEach(function(did) {
            var docEl = document.createElement("div");
            var isActive = state.selectedTopic === tid && state.selectedRun === rid && state.selectedDoc === did;
            docEl.className = "foldout-item" + (isActive ? " active" : "");

            var idSpan = document.createElement("span");
            idSpan.className = "foldout-id";
            idSpan.textContent = abbreviateDocId(did);
            idSpan.title = did;
            docEl.appendChild(idSpan);

            // Document nugget coverage
            if (typeof countDocNuggetCoverage === "function") {
              var docCov = countDocNuggetCoverage(tid, did);
              if (docCov.total > 0) {
                var docCovBadge = document.createElement("span");
                docCovBadge.className = "nugget-coverage";
                docCovBadge.textContent = docCov.satisfied + "/" + docCov.total;
                docEl.appendChild(docCovBadge);
              }
            }

            // Document clues indicator (hamburger icon)
            var docCluesEl = document.createElement("span");
            docCluesEl.className = "clues-indicator";
            docCluesEl.id = "doc-clues-" + CSS.escape(tid) + "-" + CSS.escape(did);
            docCluesEl.innerHTML = hasDocNuggetClues(tid, did) ? "&#9776;" : "";
            docCluesEl.title = "Has nugget clues";
            docEl.appendChild(docCluesEl);

            var docCheck = document.createElement("span");
            docCheck.className = "checkmark";
            docCheck.id = "doc-check-" + CSS.escape(tid) + "-" + CSS.escape(did);
            docCheck.innerHTML = isDocAnnotated(tid, did) ? "&#10003;" : "";
            docEl.appendChild(docCheck);

            docEl.addEventListener("click", function() {
              state.selectedTopic = tid;
              state.selectedRun = rid;
              state.selectedDoc = did;
              state.selectedSentenceIdx = null;
              state.selectedCitationIdx = null;
              if (typeof clearHeavyHighlight === "function") clearHeavyHighlight();
              renderSidebar();
              renderMain();
            });
            foldout.appendChild(docEl);
          });
        }
        navTree.appendChild(foldout);
      }
    });
  });
}
"""
