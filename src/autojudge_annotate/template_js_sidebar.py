"""JS sidebar: escapeHtml, abbreviateDocId, countCitationSentences, updateSidebarCounts, renderSidebarCitationsMode, renderSidebar."""

JS_SIDEBAR = r"""
// --- Sidebar ---

function escapeHtml(str) {
  var div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
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

function updateSidebarCounts() {
  if (state.mode === "citations") {
    // Topic counters: done-sentences / total-sentences across all runs
    topicIds.forEach(function(tid) {
      var countEl = document.getElementById("topic-count-" + tid);
      if (countEl) {
        var runs = reportIndex[tid] ? Object.keys(reportIndex[tid]) : [];
        var totalDone = 0, totalAll = 0;
        runs.forEach(function(rid) {
          var c = countCitationSentences(tid, rid);
          totalDone += c.done; totalAll += c.total;
        });
        countEl.textContent = "(" + totalDone + "/" + totalAll + ")";
      }
    });
    // Run counters
    if (state.selectedTopic && reportIndex[state.selectedTopic]) {
      Object.keys(reportIndex[state.selectedTopic]).forEach(function(rid) {
        var countEl = document.getElementById("run-count-" + CSS.escape(rid));
        if (countEl) {
          var c = countCitationSentences(state.selectedTopic, rid);
          countEl.textContent = "(" + c.done + "/" + c.total + ")";
        }
      });
    }
    // Sentence checkmarks
    if (state.selectedTopic && state.selectedRun) {
      var report = reportIndex[state.selectedTopic] && reportIndex[state.selectedTopic][state.selectedRun];
      if (report && report.sentences) {
        report.sentences.forEach(function(sent, idx) {
          var checkEl = document.getElementById("sent-check-" + idx);
          if (checkEl) {
            checkEl.innerHTML = isCitationSentenceComplete(state.selectedTopic, state.selectedRun, idx) ? "&#10003;" : "";
          }
        });
      }
    }
    return;
  }
  if (state.mode === "documents") {
    // Document mode: topic counter = unique annotated docs / total unique docs
    topicIds.forEach(function(tid) {
      var countEl = document.getElementById("topic-count-" + tid);
      if (countEl) {
        var allDocs = docIndex[tid] ? Object.keys(docIndex[tid]) : [];
        var done = allDocs.filter(function(did) { return isDocAnnotated(tid, did); }).length;
        countEl.textContent = "(" + done + "/" + allDocs.length + ")";
      }
    });
    // Run counter = annotated docs / total docs for that run
    if (state.selectedTopic && runDocsIndex[state.selectedTopic]) {
      Object.keys(runDocsIndex[state.selectedTopic]).forEach(function(rid) {
        var countEl = document.getElementById("run-count-" + CSS.escape(rid));
        if (countEl) {
          var docs = runDocsIndex[state.selectedTopic][rid] || [];
          var done = docs.filter(function(did) { return isDocAnnotated(state.selectedTopic, did); }).length;
          countEl.textContent = "(" + done + "/" + docs.length + ")";
        }
      });
    }
    // Doc checkmarks
    if (state.selectedTopic && state.selectedRun && runDocsIndex[state.selectedTopic]) {
      var docs = runDocsIndex[state.selectedTopic][state.selectedRun] || [];
      docs.forEach(function(did) {
        var checkEl = document.getElementById("doc-check-" + CSS.escape(did));
        if (checkEl) {
          checkEl.innerHTML = isDocAnnotated(state.selectedTopic, did) ? "&#10003;" : "";
        }
      });
    }
  } else {
    // Report mode: topic counter = annotated runs / total runs
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
        var checkEl = document.getElementById("run-check-" + CSS.escape(rid));
        if (checkEl) {
          checkEl.innerHTML = isAnnotated(state.selectedTopic, rid) ? "&#10003;" : "";
        }
      });
    }
  }
}

function abbreviateDocId(docId) {
  if (docId.length > 30) return docId.substring(0, 27) + "\u2026";
  return docId;
}

function renderSidebarCitationsMode() {
  runListHeader.textContent = "Runs";
  docListHeader.style.display = "none";
  sentListHeader.style.display = "";

  // Topics
  topicIds.forEach(function(tid) {
    var runs = reportIndex[tid] ? Object.keys(reportIndex[tid]) : [];
    var totalDone = 0, totalAll = 0;
    runs.forEach(function(rid) {
      var c = countCitationSentences(tid, rid);
      totalDone += c.done; totalAll += c.total;
    });

    var el = document.createElement("div");
    el.className = "topic-item" + (state.selectedTopic === tid ? " active" : "");
    el.innerHTML = escapeHtml(tid) + '<span class="progress" id="topic-count-' + escapeHtml(tid) + '">(' + totalDone + "/" + totalAll + ")</span>";
    el.addEventListener("click", function() {
      state.selectedTopic = tid;
      var availableRuns = reportIndex[tid] ? Object.keys(reportIndex[tid]).sort() : [];
      if (!state.selectedRun || availableRuns.indexOf(state.selectedRun) === -1) {
        state.selectedRun = availableRuns.length > 0 ? availableRuns[0] : null;
      }
      state.selectedSentenceIdx = 0;
      state.selectedCitationIdx = 0;
      renderSidebar();
      renderMain();
    });
    topicList.appendChild(el);
  });

  // Runs
  if (state.selectedTopic && reportIndex[state.selectedTopic]) {
    var runs = Object.keys(reportIndex[state.selectedTopic]).sort();
    runs.forEach(function(rid) {
      var report = reportIndex[state.selectedTopic][rid];
      var c = countCitationSentences(state.selectedTopic, rid);

      var el = document.createElement("div");
      el.className = "run-item" + (state.selectedRun === rid ? " active" : "");
      var label = escapeHtml(rid) + " (" + escapeHtml(report.team_id) + ")";
      el.innerHTML = label + '<span class="progress" id="run-count-' + CSS.escape(rid) + '">(' + c.done + "/" + c.total + ")</span>";
      el.addEventListener("click", function() {
        state.selectedRun = rid;
        state.selectedSentenceIdx = 0;
        state.selectedCitationIdx = 0;
        renderSidebar();
        renderMain();
      });
      runList.appendChild(el);
    });
  }

  // Sentences
  if (state.selectedTopic && state.selectedRun) {
    var report = reportIndex[state.selectedTopic] && reportIndex[state.selectedTopic][state.selectedRun];
    if (report && report.sentences) {
      report.sentences.forEach(function(sent, idx) {
        var el = document.createElement("div");
        el.className = "sent-item" + (state.selectedSentenceIdx === idx ? " active" : "");
        var preview = sent.text.length > 30 ? sent.text.substring(0, 30) + "\u2026" : sent.text;
        var citeCount = (sent.citations && sent.citations.length > 0) ? sent.citations.length : 0;
        var citeBadge = citeCount > 0 ? ' <span class="cite-count">[' + citeCount + "]</span>" : "";
        var checkContent = isCitationSentenceComplete(state.selectedTopic, state.selectedRun, idx) ? "&#10003;" : "";
        el.innerHTML = '<span class="sent-preview">s' + idx + " " + escapeHtml(preview) + "</span>" + citeBadge + '<span class="checkmark" id="sent-check-' + idx + '">' + checkContent + "</span>";
        el.addEventListener("click", function() {
          state.selectedSentenceIdx = idx;
          state.selectedCitationIdx = 0;
          renderSidebar();
          renderMain();
        });
        sentList.appendChild(el);
      });
    }
  }
}

function renderSidebar() {
  topicList.innerHTML = "";
  runList.innerHTML = "";
  docList.innerHTML = "";
  sentList.innerHTML = "";

  if (state.mode === "citations") {
    renderSidebarCitationsMode();
    return;
  }

  if (state.mode === "documents") {
    runListHeader.textContent = "Runs";
    docListHeader.style.display = "";
    sentListHeader.style.display = "none";

    // Topics: counter = unique annotated docs / total unique docs
    topicIds.forEach(function(tid) {
      var allDocs = docIndex[tid] ? Object.keys(docIndex[tid]) : [];
      var done = allDocs.filter(function(did) { return isDocAnnotated(tid, did); }).length;

      var el = document.createElement("div");
      el.className = "topic-item" + (state.selectedTopic === tid ? " active" : "");
      el.innerHTML = escapeHtml(tid) + '<span class="progress" id="topic-count-' + escapeHtml(tid) + '">(' + done + "/" + allDocs.length + ")</span>";
      el.addEventListener("click", function() {
        state.selectedTopic = tid;
        var availableRuns = reportIndex[tid] ? Object.keys(reportIndex[tid]).sort() : [];
        if (state.selectedRun && availableRuns.indexOf(state.selectedRun) === -1) {
          state.selectedRun = availableRuns.length > 0 ? availableRuns[0] : null;
        } else if (!state.selectedRun && availableRuns.length > 0) {
          state.selectedRun = availableRuns[0];
        }
        // Auto-select first doc for the run
        if (state.selectedRun && runDocsIndex[tid] && runDocsIndex[tid][state.selectedRun]) {
          state.selectedDoc = runDocsIndex[tid][state.selectedRun][0] || null;
        } else {
          state.selectedDoc = null;
        }
        renderSidebar();
        renderMain();
      });
      topicList.appendChild(el);
    });

    // Runs: counter = annotated docs / total docs for this run
    if (state.selectedTopic && reportIndex[state.selectedTopic]) {
      var runs = Object.keys(reportIndex[state.selectedTopic]).sort();
      runs.forEach(function(rid) {
        var report = reportIndex[state.selectedTopic][rid];
        var docs = (runDocsIndex[state.selectedTopic] && runDocsIndex[state.selectedTopic][rid]) || [];
        var done = docs.filter(function(did) { return isDocAnnotated(state.selectedTopic, did); }).length;

        var el = document.createElement("div");
        el.className = "run-item" + (state.selectedRun === rid ? " active" : "");
        var label = escapeHtml(rid) + " (" + escapeHtml(report.team_id) + ")";
        el.innerHTML = label + '<span class="progress" id="run-count-' + CSS.escape(rid) + '">(' + done + "/" + docs.length + ")</span>";
        el.addEventListener("click", function() {
          state.selectedRun = rid;
          // Auto-select first doc
          var rdocs = (runDocsIndex[state.selectedTopic] && runDocsIndex[state.selectedTopic][rid]) || [];
          state.selectedDoc = rdocs.length > 0 ? rdocs[0] : null;
          renderSidebar();
          renderMain();
        });
        runList.appendChild(el);
      });
    }

    // Documents: checkmark per doc
    if (state.selectedTopic && state.selectedRun && runDocsIndex[state.selectedTopic] && runDocsIndex[state.selectedTopic][state.selectedRun]) {
      var docs = runDocsIndex[state.selectedTopic][state.selectedRun];
      docs.forEach(function(did) {
        var el = document.createElement("div");
        el.className = "doc-item" + (state.selectedDoc === did ? " active" : "");
        var displayId = abbreviateDocId(did);
        var checkContent = isDocAnnotated(state.selectedTopic, did) ? "&#10003;" : "";
        el.innerHTML = escapeHtml(displayId) + '<span class="checkmark" id="doc-check-' + CSS.escape(did) + '">' + checkContent + '</span>';
        el.title = did;
        el.addEventListener("click", function() {
          state.selectedDoc = did;
          renderSidebar();
          renderMain();
        });
        docList.appendChild(el);
      });
    }

  } else {
    // Report mode (unchanged logic)
    runListHeader.textContent = "Runs";
    docListHeader.style.display = "none";
    sentListHeader.style.display = "none";

    topicIds.forEach(function(tid) {
      var runs = reportIndex[tid] ? Object.keys(reportIndex[tid]).sort() : [];
      var done = runs.filter(function(rid) { return isAnnotated(tid, rid); }).length;

      var el = document.createElement("div");
      el.className = "topic-item" + (state.selectedTopic === tid ? " active" : "");
      el.innerHTML = escapeHtml(tid) + '<span class="progress" id="topic-count-' + escapeHtml(tid) + '">(' + done + "/" + runs.length + ")</span>";
      el.addEventListener("click", function() {
        state.selectedTopic = tid;
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

    if (state.selectedTopic && reportIndex[state.selectedTopic]) {
      var runs = Object.keys(reportIndex[state.selectedTopic]).sort();
      runs.forEach(function(rid) {
        var report = reportIndex[state.selectedTopic][rid];
        var el = document.createElement("div");
        el.className = "run-item" + (state.selectedRun === rid ? " active" : "");
        var label = escapeHtml(rid) + " (" + escapeHtml(report.team_id) + ")";
        var checkContent = isAnnotated(state.selectedTopic, rid) ? "&#10003;" : "";
        el.innerHTML = label + '<span class="checkmark" id="run-check-' + CSS.escape(rid) + '">' + checkContent + '</span>';
        el.addEventListener("click", function() {
          state.selectedRun = rid;
          renderSidebar();
          renderMain();
        });
        runList.appendChild(el);
      });
    }
  }
}
"""
