"""JS main panel: renderRequestSection, renderAnnotationControls, attachAnnotationHandlers,
renderMainCitationsMode (with sub-functions), citation handlers, renderCitationSpans,
renderMain, renderMainReportMode, renderMainDocMode."""

JS_MAIN = r"""
// --- Main panel ---

function renderRequestSection(topicId) {
  var request = requestMap[topicId];
  var html = '<div class="request-section">';
  html += "<h2>Request: " + escapeHtml(topicId) + "</h2>";
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
  return html;
}

function renderAnnotationControls(ann, skipSpans) {
  var html = '';

  // Spans list (skipped in citations mode which handles spans separately)
  if (!skipSpans) {
    html += '<div class="spans-section"><h3>Selected Spans</h3><div id="spans-display"></div></div>';
  }

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

  return html;
}

function attachAnnotationHandlers() {
  document.getElementById("download-btn").addEventListener("click", handleDownload);

  document.querySelectorAll('input[name="rating"]').forEach(function(radio) {
    radio.addEventListener("change", function() {
      var ann = currentAnnotation();
      if (ann) { ann.rating = this.value; autoSave(); }
    });
  });

  document.getElementById("comment-input").addEventListener("input", function() {
    var ann = currentAnnotation();
    if (ann) { ann.comment = this.value.trim(); autoSave(); }
  });

  var outputArea = document.getElementById("output-area");
  outputArea.value = buildOutputLines().join("\n");
}

// --- Citations mode sub-functions ---

function buildCitationStepperHtml(sentIdx, totalSents) {
  var html = '<div class="sentence-stepper">';
  html += '<div class="stepper-nav">';
  html += '<button id="prev-sent-btn"' + (sentIdx === 0 ? " disabled" : "") + '>&lt; Prev</button>';
  html += '<strong>Sentence ' + (sentIdx + 1) + ' of ' + totalSents + '</strong>';
  html += '<button id="next-sent-btn"' + (sentIdx >= totalSents - 1 ? " disabled" : "") + '>Next &gt;</button>';
  html += '</div>';
  html += '<div class="sentence-display" id="sentence-text"></div>';
  html += '</div>';
  return html;
}

function buildCitationTabsHtml(citations, citIdx, docId) {
  var html = '';
  if (docId !== null) {
    if (citations.length > 1) {
      html += '<div class="citation-tabs" id="citation-tabs">';
      citations.forEach(function(cid, i) {
        var activeClass = (i === citIdx) ? " active" : "";
        var displayId = cid ? (cid.length > 15 ? cid.substring(0, 12) + "\u2026" : cid) : "none";
        html += '<div class="citation-tab' + activeClass + '" data-cit-idx="' + i + '">' + escapeHtml(displayId) + '</div>';
      });
      html += '</div>';
    }
    html += '<h3 style="margin: 8px 0 4px 0; font-size: 14px; color: #555;">Document: ' + escapeHtml(docId) + '</h3>';
    html += '<div class="document-display" id="document-text"></div>';
  } else {
    if (citations.length > 1) {
      html += '<div class="citation-tabs" id="citation-tabs"></div>';
    }
    html += '<div class="no-citation-msg">No citations for this sentence.</div>';
  }
  return html;
}

function wireCitationStepper(sentIdx, report) {
  document.getElementById("prev-sent-btn").addEventListener("click", function() {
    if (sentIdx > 0) {
      state.selectedSentenceIdx = sentIdx - 1;
      state.selectedCitationIdx = 0;
      renderSidebar();
      renderMain();
    }
  });
  document.getElementById("next-sent-btn").addEventListener("click", function() {
    if (sentIdx < report.sentences.length - 1) {
      state.selectedSentenceIdx = sentIdx + 1;
      state.selectedCitationIdx = 0;
      renderSidebar();
      renderMain();
    }
  });
}

function wireCitationTabs() {
  var tabsEl = document.getElementById("citation-tabs");
  if (tabsEl) {
    tabsEl.querySelectorAll(".citation-tab").forEach(function(tab) {
      tab.addEventListener("click", function() {
        state.selectedCitationIdx = parseInt(this.getAttribute("data-cit-idx"));
        renderMain();
      });
    });
  }
}

function renderMainCitationsMode() {
  var html = renderRequestSection(state.selectedTopic);

  if (!state.selectedRun) {
    html += '<div class="empty-state">Select a run from the sidebar.</div>';
    mainPanel.innerHTML = html;
    return;
  }

  var report = reportIndex[state.selectedTopic] && reportIndex[state.selectedTopic][state.selectedRun];
  if (!report || !report.sentences || report.sentences.length === 0) {
    html += '<div class="empty-state">No sentences in this report.</div>';
    mainPanel.innerHTML = html;
    return;
  }

  var sentIdx = state.selectedSentenceIdx || 0;
  if (sentIdx >= report.sentences.length) sentIdx = 0;
  var sent = report.sentences[sentIdx];
  var citations = (sent.citations && sent.citations.length > 0) ? sent.citations : [null];
  var citIdx = state.selectedCitationIdx || 0;
  if (citIdx >= citations.length) citIdx = 0;
  var docId = citations[citIdx];

  var ann = getCitationAnnotation(state.selectedTopic, state.selectedRun, sentIdx, docId);

  // Build HTML
  html += buildCitationStepperHtml(sentIdx, report.sentences.length);
  html += buildCitationTabsHtml(citations, citIdx, docId);
  html += '<div class="spans-section" id="citation-spans-display"></div>';
  html += renderAnnotationControls(ann, true);
  mainPanel.innerHTML = html;

  // Populate sentence text
  var sentenceTextEl = document.getElementById("sentence-text");
  sentenceTextEl.textContent = sent.text;
  applyHighlights(sentenceTextEl, ann.reportSpans, function(idx) {
    ann.reportSpans.splice(idx, 1);
    autoSave();
    renderMain();
  });
  sentenceTextEl.addEventListener("mouseup", function() {
    handleCitationSentenceSelection(sentenceTextEl, ann);
  });

  // Populate document text
  if (docId !== null) {
    var docTextEl = document.getElementById("document-text");
    var doc = (report.documents && report.documents[docId]) || (docIndex[state.selectedTopic] && docIndex[state.selectedTopic][docId]);
    if (doc) {
      var fullDocText = "";
      if (doc.title) fullDocText = doc.title + "\n\n";
      fullDocText += doc.text || "";
      docTextEl.textContent = fullDocText;
      applyHighlights(docTextEl, ann.spans, function(idx) {
        ann.spans.splice(idx, 1);
        autoSave();
        renderMain();
      });
      docTextEl.addEventListener("mouseup", function() {
        handleCitationDocSelection(docTextEl, ann, doc);
      });
    } else {
      docTextEl.textContent = "Document not available.";
    }
  }

  // Render dual span chips
  renderCitationSpans(ann, docId !== null);

  // Wire stepper and tabs
  wireCitationStepper(sentIdx, report);
  wireCitationTabs();

  attachAnnotationHandlers();
}

function handleCitationSentenceSelection(container, ann) {
  var sel = window.getSelection();
  if (!sel || sel.isCollapsed || sel.rangeCount === 0) return;

  var range = sel.getRangeAt(0);
  if (!container.contains(range.startContainer) || !container.contains(range.endContainer)) return;

  var selectedText = sel.toString().trim();
  if (!selectedText) return;

  var offset = computeOffset(container, range);
  if (offset === null) return;

  var spanText = container.textContent.substring(offset.start, offset.end).trim();
  if (!spanText) { sel.removeAllRanges(); return; }

  var isDuplicate = ann.reportSpans.some(function(s) { return s.start === offset.start && s.end === offset.end; });
  if (isDuplicate) { sel.removeAllRanges(); return; }

  ann.reportSpans.push({ start: offset.start, end: offset.end, text: spanText });
  ann.reportSpans.sort(function(a, b) { return a.start - b.start; });

  sel.removeAllRanges();
  autoSave();
  renderMain();
}

function handleCitationDocSelection(container, ann, doc) {
  var sel = window.getSelection();
  if (!sel || sel.isCollapsed || sel.rangeCount === 0) return;

  var range = sel.getRangeAt(0);
  if (!container.contains(range.startContainer) || !container.contains(range.endContainer)) return;

  var selectedText = sel.toString().trim();
  if (!selectedText) return;

  var offset = computeOffset(container, range);
  if (offset === null) return;

  var fullDocText = "";
  if (doc.title) fullDocText = doc.title + "\n\n";
  fullDocText += doc.text || "";

  var spanText = fullDocText.substring(offset.start, offset.end).trim();
  if (!spanText) { sel.removeAllRanges(); return; }

  var isDuplicate = ann.spans.some(function(s) { return s.start === offset.start && s.end === offset.end; });
  if (isDuplicate) { sel.removeAllRanges(); return; }

  ann.spans.push({ start: offset.start, end: offset.end, text: spanText });
  ann.spans.sort(function(a, b) { return a.start - b.start; });

  sel.removeAllRanges();
  autoSave();
  renderMain();
}

function renderCitationSpans(ann, hasCitations) {
  var container = document.getElementById("citation-spans-display");
  if (!container) return;
  var html = '';

  // Report spans (sentence side)
  html += '<h3 style="font-size:14px;color:#555;margin-bottom:4px;">Report Spans</h3>';
  if (ann.reportSpans && ann.reportSpans.length > 0) {
    ann.reportSpans.forEach(function(sp) {
      html += '<span class="report-span-chip">[' + sp.start + '-' + sp.end + '] ' + escapeHtml(sp.text) + '</span>';
    });
  } else {
    html += '<span style="color:#888;font-size:12px;">No report spans selected.</span>';
  }

  // Document spans
  if (hasCitations) {
    html += '<h3 style="font-size:14px;color:#555;margin:8px 0 4px 0;">Document Spans</h3>';
    if (ann.spans && ann.spans.length > 0) {
      ann.spans.forEach(function(sp) {
        html += '<span class="document-span-chip">[' + sp.start + '-' + sp.end + '] ' + escapeHtml(sp.text) + '</span>';
      });
    } else {
      html += '<span style="color:#888;font-size:12px;">No document spans selected.</span>';
    }
  }

  container.innerHTML = html;
}

function renderMain() {
  if (!state.selectedTopic) {
    mainPanel.innerHTML = '<div class="empty-state">Select a topic from the sidebar to begin.</div>';
    return;
  }

  if (state.mode === "citations") {
    renderMainCitationsMode();
  } else if (state.mode === "documents") {
    renderMainDocMode();
  } else {
    renderMainReportMode();
  }
}

function renderMainReportMode() {
  var html = renderRequestSection(state.selectedTopic);

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

  var ann = getReportAnnotation(state.selectedTopic, state.selectedRun);

  html += '<div class="report-section">';
  html += "<h2>Report: " + escapeHtml(report.run_id) + " by " + escapeHtml(report.team_id) + "</h2>";
  html += '<div class="report-text" id="report-text"></div>';
  html += "</div>";

  html += renderAnnotationControls(ann);
  mainPanel.innerHTML = html;

  // Build report text and apply highlights with explicit onRemove
  refreshReportHighlights();

  attachAnnotationHandlers();
  renderSpans();
}

function renderMainDocMode() {
  var html = renderRequestSection(state.selectedTopic);

  if (!state.selectedRun) {
    html += '<div class="empty-state">Select a run from the sidebar.</div>';
    mainPanel.innerHTML = html;
    return;
  }

  if (!state.selectedDoc) {
    html += '<div class="empty-state">Select a document from the sidebar.</div>';
    mainPanel.innerHTML = html;
    return;
  }

  var doc = docIndex[state.selectedTopic] && docIndex[state.selectedTopic][state.selectedDoc];
  if (!doc) {
    html += '<div class="empty-state">Document not found.</div>';
    mainPanel.innerHTML = html;
    return;
  }

  var ann = getDocAnnotation(state.selectedTopic, state.selectedDoc);

  html += '<div class="report-section">';
  html += "<h2>Document: " + escapeHtml(state.selectedDoc) + "</h2>";
  html += '<div class="report-text" id="report-text"></div>';
  html += "</div>";

  html += renderAnnotationControls(ann);
  mainPanel.innerHTML = html;

  // Build document text and apply highlights with explicit onRemove
  refreshDocHighlights();

  attachAnnotationHandlers();
  renderSpans();
}
"""
