"""Generic span highlighting utilities - no app-specific dependencies.

These functions can be reused by any annotation tool. They take parameters
instead of accessing global state.
"""

JS_SPANS_CORE = r"""
// --- Generic DOM utilities for span highlighting ---

/**
 * Collect all text nodes within a container, computing their character offsets.
 * @param {Element} container - The container element
 * @param {string[]} skipClasses - Array of class names to skip (e.g., ["citation-marker"])
 * @returns {{textNodes: Text[], nodeStarts: number[]}}
 */
function collectTextNodes(container, skipClasses) {
  var textNodes = [];
  var nodeStarts = [];
  var pos = 0;
  skipClasses = skipClasses || [];
  function walk(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      textNodes.push(node);
      nodeStarts.push(pos);
      pos += node.textContent.length;
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      if (node.classList) {
        for (var i = 0; i < skipClasses.length; i++) {
          if (node.classList.contains(skipClasses[i])) return;
        }
      }
      for (var i = 0; i < node.childNodes.length; i++) {
        walk(node.childNodes[i]);
      }
    }
  }
  walk(container);
  return { textNodes: textNodes, nodeStarts: nodeStarts };
}

/**
 * Compute character offsets from a DOM Range within a container.
 * @param {Element} container - The container element
 * @param {Range} range - The DOM selection range
 * @param {string[]} skipClasses - Array of class names to skip
 * @returns {{start: number, end: number}|null} - Character offsets or null if invalid
 */
function computeOffset(container, range, skipClasses) {
  var startOff = 0;
  var endOff = 0;
  var foundStart = false;
  var foundEnd = false;
  var charPos = 0;
  skipClasses = skipClasses || [];

  function shouldSkip(node) {
    if (!node.classList) return false;
    for (var i = 0; i < skipClasses.length; i++) {
      if (node.classList.contains(skipClasses[i])) return true;
    }
    return false;
  }

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
      if (shouldSkip(node)) {
        // If selection starts/ends inside a skipped element, snap to boundary
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
      for (var i = 0; i < node.childNodes.length; i++) {
        walk(node.childNodes[i]);
      }
    }
  }
  walk(container);
  if (!foundStart || !foundEnd || startOff >= endOff) return null;
  return { start: startOff, end: endOff };
}

/**
 * Apply highlight marks to a container based on span offsets.
 * @param {Element} container - The container element
 * @param {Array<{start: number, end: number}>} spans - Array of span objects
 * @param {function(number): void} onRemove - Callback when span is removed (receives span index)
 * @param {string[]} skipClasses - Array of class names to skip when collecting text nodes
 */
function applyHighlights(container, spans, onRemove, skipClasses) {
  if (!spans || spans.length === 0) return;

  // Apply spans in reverse order to avoid invalidating offsets
  var sorted = spans.slice().sort(function(a, b) { return b.start - a.start; });
  sorted.forEach(function(sp) {
    var spanIndex = spans.indexOf(sp);
    var info = collectTextNodes(container, skipClasses);
    wrapRange(info.textNodes, info.nodeStarts, sp, spanIndex, onRemove);
  });
}

/**
 * Wrap a character range with <mark> elements.
 * @param {Text[]} textNodes - Array of text nodes
 * @param {number[]} nodeStarts - Character offset where each text node starts
 * @param {{start: number, end: number}} span - The span to wrap
 * @param {number} spanIndex - Index of this span (for removal callback)
 * @param {function(number): void} onRemove - Callback when remove button clicked
 */
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

/**
 * Create a simple selection handler for text containers.
 * @param {Object} config - Configuration object
 * @param {string} config.containerId - ID of the text container element
 * @param {function(): Object} config.getAnnotation - Returns current annotation object with spans array
 * @param {function(): string} config.getPlainText - Returns plain text for span text extraction
 * @param {function(): void} config.onSpanAdded - Callback after span is added
 * @param {string[]} config.skipClasses - Classes to skip in offset computation
 * @returns {function(): void} - Selection handler function to attach to mouseup
 */
function createSelectionHandler(config) {
  return function handleSelection() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || sel.rangeCount === 0) return;

    var container = document.getElementById(config.containerId);
    if (!container) return;

    var range = sel.getRangeAt(0);
    if (!container.contains(range.startContainer) || !container.contains(range.endContainer)) return;

    var selectedText = sel.toString().trim();
    if (!selectedText) return;

    var offset = computeOffset(container, range, config.skipClasses || []);
    if (offset === null) return;

    var ann = config.getAnnotation();
    if (!ann) return;

    // Extract text from plain text (more reliable than selection) and
    // shrink offsets to the trimmed boundaries — otherwise a trailing
    // newline pushes the inline-block remove-x onto a new visual line
    // where the mark's hover region doesn't reach.
    var plainText = config.getPlainText ? config.getPlainText() : null;
    var raw = plainText ? plainText.substring(offset.start, offset.end) : selectedText;
    var leftTrim = raw.length - raw.replace(/^\s+/, "").length;
    var rightTrim = raw.length - raw.replace(/\s+$/, "").length;
    var startAdj = offset.start + leftTrim;
    var endAdj = offset.end - rightTrim;
    var spanText = raw.trim();
    if (!spanText || endAdj <= startAdj) { sel.removeAllRanges(); return; }

    // Avoid exact duplicates
    var isDuplicate = ann.spans.some(function(s) {
      return s.start === startAdj && s.end === endAdj;
    });
    if (isDuplicate) { sel.removeAllRanges(); return; }

    ann.spans.push({ start: startAdj, end: endAdj, text: spanText });
    ann.spans.sort(function(a, b) { return a.start - b.start; });

    sel.removeAllRanges();
    if (config.onSpanAdded) config.onSpanAdded();
  };
}
"""