"""JS span/highlight logic: buildReportText, buildPlainText, buildSentenceBoundaries,
splitIntoSentenceSpans, collectTextNodes, applyHighlights, wrapRange,
handleSelection, handleDocSelection, computeOffset, renderSpans,
refreshReportHighlights, refreshDocHighlights."""

JS_SPANS = r"""
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
        var displayId = cid.length > 10 ? cid.substring(0, 4) + "\u2026" : cid;
        span.textContent = "[" + displayId + "]";
        span.setAttribute("data-citation-id", cid);
        span.title = cid;
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

function applyHighlights(container, spans, onRemove) {
  if (!spans || spans.length === 0) return;

  // Apply spans in reverse order to avoid invalidating offsets
  var sorted = spans.slice().sort(function(a, b) { return b.start - a.start; });
  sorted.forEach(function(sp) {
    var spanIndex = spans.indexOf(sp);
    var info = collectTextNodes(container);
    wrapRange(info.textNodes, info.nodeStarts, sp, spanIndex, onRemove);
  });
}

function wrapRange(textNodes, nodeStarts, span, spanIndex, onRemove) {
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
        onRemove(idx);
      });
      mark.appendChild(removeBtn);
      isFirst = false;
    }
  }
}

// --- Refresh helpers (rebuild text + highlights with explicit onRemove) ---

function refreshReportHighlights() {
  var reportTextEl = document.getElementById("report-text");
  var ann = currentAnnotation();
  var report = reportIndex[state.selectedTopic][state.selectedRun];
  buildReportText(reportTextEl, report);
  applyHighlights(reportTextEl, ann.spans, function(idx) {
    ann.spans.splice(idx, 1);
    autoSave();
    refreshReportHighlights();
    renderSpans();
  });
  reportTextEl.addEventListener("mouseup", handleSelection);
}

function refreshDocHighlights() {
  var reportTextEl = document.getElementById("report-text");
  var ann = currentAnnotation();
  var doc = docIndex[state.selectedTopic] && docIndex[state.selectedTopic][state.selectedDoc];
  var docText = (doc.title ? doc.title + "\n\n" : "") + (doc.text || "");
  reportTextEl.textContent = docText;
  applyHighlights(reportTextEl, ann.spans, function(idx) {
    ann.spans.splice(idx, 1);
    autoSave();
    refreshDocHighlights();
    renderSpans();
  });
  reportTextEl.addEventListener("mouseup", handleDocSelection);
}

// --- Selection handlers ---

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
  refreshReportHighlights();
  renderSpans();
}

function handleDocSelection() {
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

  // No sentence splitting for documents
  var doc = docIndex[state.selectedTopic] && docIndex[state.selectedTopic][state.selectedDoc];
  if (!doc) return;

  var docText = "";
  if (doc.title) docText = doc.title + "\n\n";
  docText += doc.text || "";

  var spanText = docText.substring(offset.start, offset.end).trim();
  if (!spanText) { sel.removeAllRanges(); return; }

  // Avoid exact duplicates
  var isDuplicate = ann.spans.some(function(s) { return s.start === offset.start && s.end === offset.end; });
  if (isDuplicate) { sel.removeAllRanges(); return; }

  ann.spans.push({ start: offset.start, end: offset.end, text: spanText });
  ann.spans.sort(function(a, b) { return a.start - b.start; });

  sel.removeAllRanges();
  autoSave();

  // Re-render highlights
  refreshDocHighlights();
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
"""
