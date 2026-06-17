"""JS nugget panel: renderNuggetPanel, getNuggetsForTopic, getVerdictForDoc."""

JS_NUGGETS = r"""
// --- Nugget Panel ---

// Get nuggets for a topic from DATA.nugget_banks
function getNuggetsForTopic(topicId) {
  if (!DATA.nugget_banks || !DATA.nugget_banks[topicId]) {
    return { nuggets: [], claims: [] };
  }
  return DATA.nugget_banks[topicId];
}

// Check if a document satisfies a nugget (appears in doc_ids)
function docSatisfiesNugget(nugget, docId) {
  if (!nugget.doc_ids || nugget.doc_ids.length === 0) return false;
  return nugget.doc_ids.indexOf(docId) !== -1;
}

// Get all doc_ids from the current report that satisfy any nugget
function getReportDocIds(report) {
  if (!report || !report.documents) return [];
  return Object.keys(report.documents);
}

// Get report grade for a nugget
// Returns: {grade, reasoning, confidence} or null if no grade
// Checks both DATA.nugget_grades (pre-loaded) and state.userNuggetGrades (user-generated)
function getReportGrade(topicId, runId, nuggetId) {
  // First check user-generated grades (these take precedence)
  if (state.userNuggetGrades[topicId] &&
      state.userNuggetGrades[topicId][runId] &&
      state.userNuggetGrades[topicId][runId][nuggetId]) {
    return state.userNuggetGrades[topicId][runId][nuggetId];
  }

  // Then check pre-loaded grades from DATA
  if (!DATA.nugget_grades) {
    return null;
  }
  var topicGrades = DATA.nugget_grades[topicId];
  if (!topicGrades) {
    return null;
  }
  var runGrades = topicGrades[runId];
  if (!runGrades) {
    return null;
  }
  return runGrades[nuggetId] || null;
}

// Get document-level grade for a nugget
// Returns: {grade, reasoning, confidence, paragraphs} or null if no grade
// Checks both state.userDocGrades (user-generated) and DATA.doc_grades (pre-loaded)
function getDocGrade(topicId, docId, nuggetId) {
  // First check user-generated doc grades (these take precedence)
  if (state.userDocGrades &&
      state.userDocGrades[topicId] &&
      state.userDocGrades[topicId][docId] &&
      state.userDocGrades[topicId][docId][nuggetId]) {
    return state.userDocGrades[topicId][docId][nuggetId];
  }

  // Then check pre-loaded grades from DATA
  if (!DATA.doc_grades) {
    return null;
  }
  var topicGrades = DATA.doc_grades[topicId];
  if (!topicGrades) {
    return null;
  }
  var docGrades = topicGrades[docId];
  if (!docGrades) {
    return null;
  }
  var nuggetGrade = docGrades[nuggetId];
  if (!nuggetGrade) {
    return null;
  }
  // Return in same format as report grades for consistency
  return {
    grade: nuggetGrade.max_grade || 0,
    reasoning: "", // aggregated - individual reasoning in paragraphs
    confidence: 0,
    paragraphs: nuggetGrade.paragraphs || {}
  };
}

// Determine verdict class and icon based on grade
// Grade 4-5: satisfied (checkmark), 1-3: partial (tilde), 0: not satisfied (X)
function gradeToVerdict(grade) {
  if (grade >= 4) {
    return { cls: "nugget-satisfied", icon: "&#10003;", label: "satisfied" };
  } else if (grade >= 1) {
    return { cls: "nugget-partial", icon: "&#126;", label: "partial" };
  } else {
    return { cls: "nugget-not-satisfied", icon: "&#10007;", label: "not satisfied" };
  }
}

// Unknown verdict (no evaluation data available)
function unknownVerdict() {
  return { cls: "nugget-unknown", icon: "&#63;", label: "unknown" };
}

// Build source description for nugget (e.g., "report + 3 docs", "report", "3 docs")
function buildSourceDesc(reportGrade, satisfyingDocs) {
  var parts = [];
  if (reportGrade && reportGrade.grade >= 1) {
    parts.push("report");
  }
  if (satisfyingDocs.length > 0) {
    parts.push(satisfyingDocs.length + " doc" + (satisfyingDocs.length > 1 ? "s" : ""));
  }
  return parts.join(" + ");
}

// Render a single nugget item
function renderNuggetItem(n, topicId, currentRunId, isReportMode, currentDocIds, isUserNugget) {
  var satisfyingDocs = [];
  var docGrade = null;
  var hasDocGradeData = false;  // True if we have explicit grade data for this doc/nugget

  // Check doc grades or doc_ids for current docs
  if (currentDocIds && currentDocIds.length > 0) {
    currentDocIds.forEach(function(docId) {
      // First try doc_grades (new format) - works for both pre-loaded and user nuggets
      var dg = getDocGrade(topicId, docId, n.nugget_id);
      if (dg) {
        hasDocGradeData = true;
        // Keep the best doc grade for display
        if (!docGrade || dg.grade > docGrade.grade) {
          docGrade = dg;
        }
        if (dg.grade >= 1) {
          satisfyingDocs.push(docId);
        }
      } else if (!isUserNugget && docSatisfiesNugget(n, docId)) {
        // Fall back to doc_ids check (old format) - only for pre-loaded nuggets
        satisfyingDocs.push(docId);
      }
    });
  }

  // Get report grade if in report mode
  var reportGrade = null;
  if (isReportMode && currentRunId) {
    reportGrade = getReportGrade(topicId, currentRunId, n.nugget_id);
  }

  // Determine verdict
  var verdict;
  var gradeForVerdict = null;
  if (reportGrade) {
    gradeForVerdict = reportGrade;
    verdict = gradeToVerdict(reportGrade.grade);
  } else if (docGrade) {
    // Document mode with doc_grades (including grade=0)
    gradeForVerdict = docGrade;
    verdict = gradeToVerdict(docGrade.grade);
  } else if (satisfyingDocs.length > 0) {
    verdict = { cls: "nugget-satisfied", icon: "&#10003;", label: "satisfied" };
  } else if (isUserNugget) {
    verdict = unknownVerdict();
  } else if (isReportMode && !n.has_grades) {
    verdict = unknownVerdict();
  } else if (!isReportMode && !n.has_doc_info && !hasDocGradeData) {
    verdict = unknownVerdict();
  } else {
    verdict = { cls: "nugget-not-satisfied", icon: "&#10007;", label: "not satisfied" };
  }

  // Build source description
  var sourceDesc = buildSourceDesc(reportGrade, satisfyingDocs);

  var html = '<div class="nugget-item ' + verdict.cls + (isUserNugget ? ' user-nugget-item' : '') + '">';
  html += '<span class="nugget-verdict">' + verdict.icon + '</span>';
  html += '<span class="nugget-text">' + escapeHtml(n.text) + '</span>';
  if (sourceDesc || gradeForVerdict) {
    var tooltip = satisfyingDocs.length > 0 ? satisfyingDocs.join(', ') : '';
    if (gradeForVerdict && gradeForVerdict.reasoning) {
      tooltip = (tooltip ? tooltip + '\\n\\n' : '') + 'Reasoning: ' + gradeForVerdict.reasoning;
    }
    // Show paragraph-level reasoning from doc grades
    if (docGrade && docGrade.paragraphs) {
      var paraKeys = Object.keys(docGrade.paragraphs);
      paraKeys.forEach(function(pk) {
        var para = docGrade.paragraphs[pk];
        if (para.reasoning) {
          tooltip = (tooltip ? tooltip + '\\n\\n' : '') + 'P' + pk + ' (grade ' + para.grade + '): ' + para.reasoning;
        }
      });
    }
    // Check if this nugget has an addressed_quote that can be highlighted
    // In report mode: only report-level quotes (paragraph quotes are from source docs, not report)
    // In document mode: paragraph-level quotes
    // Show for any grade that has a quote (not just grade >= 4)
    var hasQuote = false;
    if (isReportMode) {
      // Report mode: check report-level addressed_quote
      if (gradeForVerdict && gradeForVerdict.addressed_quote) {
        hasQuote = true;
      }
    } else {
      // Document mode: check paragraph-level quotes (pre-loaded) or top-level quotes (user-generated)
      if (docGrade && docGrade.paragraphs) {
        Object.keys(docGrade.paragraphs).forEach(function(pk) {
          var para = docGrade.paragraphs[pk];
          if (para.addressed_quote) {
            hasQuote = true;
          }
        });
      } else if (docGrade && docGrade.addressed_quote) {
        // Flat doc grade (user-generated format)
        hasQuote = true;
      }
    }

    var clickableClass = hasQuote ? ' nugget-source-clickable' : '';
    var dataAttr = hasQuote ? ' data-nugget-id="' + escapeHtml(n.nugget_id) + '"' : '';
    html += '<span class="nugget-docs' + clickableClass + '" title="' + escapeHtml(tooltip) + '"' + dataAttr + '>';
    if (sourceDesc) {
      html += '(' + sourceDesc + ')';
    } else if (gradeForVerdict && gradeForVerdict.grade > 0) {
      // Only show grade if > 0 (present); grade 0 means not present, show nothing
      html += '(grade: ' + gradeForVerdict.grade + ')';
    }
    html += '</span>';
  }
  html += '</div>';
  return html;
}

// Render a category section with header
function renderNuggetCategory(categoryName, categoryClass, nuggetItems, collapsed) {
  if (nuggetItems.length === 0) return '';

  var collapseClass = collapsed ? ' collapsed' : '';
  var html = '<div class="nugget-category ' + categoryClass + collapseClass + '">';
  html += '<div class="nugget-category-header" data-category="' + categoryClass + '">';
  html += '<span class="nugget-category-toggle">&#9656;</span>';
  html += '<span class="nugget-category-name">' + categoryName + '</span>';
  html += '<span class="nugget-category-count">(' + nuggetItems.length + ')</span>';
  html += '</div>';
  html += '<div class="nugget-category-content">';
  html += '<div class="nugget-list">';
  nuggetItems.forEach(function(item) {
    html += item;
  });
  html += '</div>';
  html += '</div>';
  html += '</div>';
  return html;
}

// Render the nugget panel for a topic
// In report mode: show report grades + doc satisfaction
// In document mode: show which nuggets the current doc satisfies
function renderNuggetPanel(topicId, currentDocIds) {
  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];
  var claims = bank.claims || [];

  // Get user-created nuggets from canonicalized clues
  var userNuggets = [];
  if (typeof getCanonicalizedNuggetsForTopic === "function") {
    userNuggets = getCanonicalizedNuggetsForTopic(topicId);
  }

  var totalCount = nuggets.length + claims.length + userNuggets.length;

  if (totalCount === 0) {
    return ''; // No nuggets for this topic
  }

  // Get current run for report mode grades
  var currentRunId = state.selectedRun || null;
  var isReportMode = (currentRunId !== null && state.selectedDoc === null && state.selectedSentenceIdx === null);

  // Initialize collapsed state if not set
  if (!state.nuggetPanelCollapsed) {
    state.nuggetPanelCollapsed = {};
  }

  // Group all nuggets by type (only show enabled nuggets)
  var mustHaveItems = [];
  var shouldHaveItems = [];
  var avoidItems = [];
  var claimItems = [];
  var enabledCount = 0;

  // Pre-loaded nuggets (default to must_have if no type specified)
  nuggets.forEach(function(n) {
    // Skip disabled nuggets
    if (state.enabledNuggets[n.nugget_id] === false) return;
    enabledCount++;
    var itemHtml = renderNuggetItem(n, topicId, currentRunId, isReportMode, currentDocIds, false);
    var nuggetType = n.nugget_type || "must_have";
    if (nuggetType === "should_have") {
      shouldHaveItems.push(itemHtml);
    } else if (nuggetType === "avoid") {
      avoidItems.push(itemHtml);
    } else {
      mustHaveItems.push(itemHtml);
    }
  });

  // User-created nuggets
  userNuggets.forEach(function(n) {
    // Skip disabled nuggets
    if (state.enabledNuggets[n.nugget_id] === false) return;
    enabledCount++;
    var itemHtml = renderNuggetItem(n, topicId, currentRunId, isReportMode, currentDocIds, true);
    if (n.nugget_type === "should_have") {
      shouldHaveItems.push(itemHtml);
    } else if (n.nugget_type === "avoid") {
      avoidItems.push(itemHtml);
    } else {
      mustHaveItems.push(itemHtml);
    }
  });

  // Claims
  claims.forEach(function(c) {
    // Skip disabled claims
    if (state.enabledNuggets[c.claim_id] === false) return;
    enabledCount++;
    // Claims use claim_id instead of nugget_id
    var cAsNugget = { nugget_id: c.claim_id, text: c.text, doc_ids: c.doc_ids, has_grades: c.has_grades, has_doc_info: c.has_doc_info };
    var itemHtml = renderNuggetItem(cAsNugget, topicId, currentRunId, isReportMode, currentDocIds, false);
    claimItems.push(itemHtml);
  });

  // If no enabled nuggets, don't show the panel
  if (enabledCount === 0) {
    return '';
  }

  // Build panel HTML
  var panelCollapsed = state.nuggetPanelCollapsed["panel"] === true;
  var html = '<div class="nugget-panel' + (panelCollapsed ? ' collapsed' : '') + '">';
  html += '<div class="nugget-panel-header" data-panel="nuggets">';
  html += '<span class="nugget-panel-toggle">&#9656;</span>';
  html += '<span class="nugget-panel-title">Nuggets (' + enabledCount + (enabledCount < totalCount ? '/' + totalCount : '') + ')</span>';
  html += '<span class="nugget-panel-spacer"></span>';
  if (isReportMode) {
    html += '<button id="grade-docs-btn" class="grade-docs-btn" title="Grade user nuggets against cited documents">Grade Docs</button>';
    html += '<span id="grade-docs-progress" class="grade-docs-progress-inline"></span>';
  }
  html += '<button id="quote-all-btn" class="quote-all-btn" title="Extract quotes for all graded nuggets without quotes">Quote</button>';
  html += '<span id="quote-extraction-progress" class="quote-progress-inline"></span>';
  html += '</div>';
  html += '<div class="nugget-panel-content">';

  // Render each category
  html += renderNuggetCategory('Must Have', 'cat-must-have', mustHaveItems, state.nuggetPanelCollapsed["must_have"]);
  html += renderNuggetCategory('Should Have', 'cat-should-have', shouldHaveItems, state.nuggetPanelCollapsed["should_have"]);
  html += renderNuggetCategory('Avoid', 'cat-avoid', avoidItems, state.nuggetPanelCollapsed["avoid"]);
  html += renderNuggetCategory('Claims', 'cat-claims', claimItems, state.nuggetPanelCollapsed["claims"]);

  html += '</div>';
  html += '</div>';
  return html;
}

// Attach nugget panel toggle handlers
function attachNuggetPanelHandlers() {
  // Main panel toggle
  var panelHeader = document.querySelector('.nugget-panel-header[data-panel="nuggets"]');
  if (panelHeader) {
    panelHeader.onclick = function() {
      if (!state.nuggetPanelCollapsed) state.nuggetPanelCollapsed = {};
      state.nuggetPanelCollapsed["panel"] = !state.nuggetPanelCollapsed["panel"];
      var panel = panelHeader.closest('.nugget-panel');
      if (panel) {
        panel.classList.toggle('collapsed', state.nuggetPanelCollapsed["panel"]);
      }
    };
  }

  // Category toggles
  var categoryHeaders = document.querySelectorAll('.nugget-category-header');
  categoryHeaders.forEach(function(header) {
    header.onclick = function(e) {
      e.stopPropagation();
      var catClass = header.getAttribute('data-category');
      var catKey = catClass.replace('cat-', '').replace('-', '_');
      if (!state.nuggetPanelCollapsed) state.nuggetPanelCollapsed = {};
      state.nuggetPanelCollapsed[catKey] = !state.nuggetPanelCollapsed[catKey];
      var category = header.closest('.nugget-category');
      if (category) {
        category.classList.toggle('collapsed', state.nuggetPanelCollapsed[catKey]);
      }
    };
  });

  // Heavy highlight toggle on clickable source descriptions
  var clickableSources = document.querySelectorAll('.nugget-source-clickable');
  clickableSources.forEach(function(el) {
    el.onclick = function(e) {
      e.stopPropagation();
      var nuggetId = el.getAttribute('data-nugget-id');
      if (nuggetId) {
        toggleHeavyHighlight(nuggetId);
      }
    };
  });

  // Quote all button
  var quoteAllBtn = document.getElementById('quote-all-btn');
  if (quoteAllBtn) {
    quoteAllBtn.onclick = function(e) {
      e.stopPropagation();
      if (typeof extractQuotesForActiveNuggets === "function" && !isQuoteExtractionActive()) {
        extractQuotesForActiveNuggets();
      }
    };
  }

  // Grade Docs button (only in report mode)
  var gradeDocsBtn = document.getElementById('grade-docs-btn');
  if (gradeDocsBtn) {
    gradeDocsBtn.onclick = function(e) {
      e.stopPropagation();
      if (typeof gradeDocsForReport === "function" && !isGradeDocsActive()) {
        gradeDocsForReport();
      }
    };
  }
}

// Get current document IDs based on mode
function getCurrentDocIds() {
  if (state.mode === "documents" && state.selectedDoc) {
    return [state.selectedDoc];
  }
  if (state.mode === "reports" && state.selectedRun && state.selectedTopic) {
    var report = reportIndex[state.selectedTopic] && reportIndex[state.selectedTopic][state.selectedRun];
    return getReportDocIds(report);
  }
  if (state.mode === "citations" && state.selectedRun && state.selectedTopic) {
    var report = reportIndex[state.selectedTopic] && reportIndex[state.selectedTopic][state.selectedRun];
    return getReportDocIds(report);
  }
  return [];
}

// Count nugget coverage for a run
// Returns {satisfied: N, total: M} where satisfied means grade >= 1 or doc satisfies
function countNuggetCoverage(topicId, runId) {
  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];
  var claims = bank.claims || [];
  var total = nuggets.length + claims.length;

  if (total === 0) {
    return { satisfied: 0, total: 0 };
  }

  // Get doc_ids for this run
  var report = reportIndex[topicId] && reportIndex[topicId][runId];
  var docIds = getReportDocIds(report);

  var satisfied = 0;

  // Check nugget questions
  nuggets.forEach(function(n) {
    // Check report grade
    var grade = getReportGrade(topicId, runId, n.nugget_id);
    if (grade && grade.grade >= 1) {
      satisfied++;
      return;
    }
    // Check doc satisfaction
    for (var i = 0; i < docIds.length; i++) {
      if (docSatisfiesNugget(n, docIds[i])) {
        satisfied++;
        break;
      }
    }
  });

  // Check claims
  claims.forEach(function(c) {
    var grade = getReportGrade(topicId, runId, c.claim_id);
    if (grade && grade.grade >= 1) {
      satisfied++;
      return;
    }
    for (var i = 0; i < docIds.length; i++) {
      if (docSatisfiesNugget(c, docIds[i])) {
        satisfied++;
        break;
      }
    }
  });

  return { satisfied: satisfied, total: total };
}

// Count nugget coverage for a single document
// Returns {satisfied: N, total: M} where satisfied means grade >= 1 from doc_grades
// Falls back to doc_ids check only if no doc_grades entry exists for this nugget
function countDocNuggetCoverage(topicId, docId) {
  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];
  var claims = bank.claims || [];

  // Include user-created nuggets
  var userNuggets = (typeof getCanonicalizedNuggetsForTopic === "function")
    ? getCanonicalizedNuggetsForTopic(topicId)
    : [];

  var total = nuggets.length + claims.length + userNuggets.length;

  if (total === 0) {
    return { satisfied: 0, total: 0 };
  }

  var satisfied = 0;

  // Check nugget questions
  nuggets.forEach(function(n) {
    // First try doc_grades (new format)
    var docGrade = getDocGrade(topicId, docId, n.nugget_id);
    if (docGrade) {
      // Have explicit grade data - use it (grade=0 means not satisfied)
      if (docGrade.grade >= 1) {
        satisfied++;
      }
      return;
    }
    // Fall back to doc_ids check (old format) only if no doc_grades entry
    if (docSatisfiesNugget(n, docId)) {
      satisfied++;
    }
  });

  // Check claims
  claims.forEach(function(c) {
    var docGrade = getDocGrade(topicId, docId, c.claim_id);
    if (docGrade) {
      if (docGrade.grade >= 1) {
        satisfied++;
      }
      return;
    }
    if (docSatisfiesNugget(c, docId)) {
      satisfied++;
    }
  });

  // Check user-created nuggets
  userNuggets.forEach(function(n) {
    var docGrade = getDocGrade(topicId, docId, n.nugget_id);
    if (docGrade && docGrade.grade >= 1) {
      satisfied++;
    }
  });

  return { satisfied: satisfied, total: total };
}

// --- Addressed Quote Highlighting ---

// Get quote highlights for the current view (report or document)
// Returns: [{quote, nuggetId, nuggetType, isHeavy}]
function getQuoteHighlights(topicId, runId, docId) {
  var highlights = [];
  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];

  // Include user-created nuggets from canonicalized clues
  var userNuggets = (typeof getCanonicalizedNuggetsForTopic === "function")
    ? getCanonicalizedNuggetsForTopic(topicId)
    : [];
  var allNuggets = nuggets.concat(userNuggets);

  allNuggets.forEach(function(n) {
    var nuggetType = n.nugget_type || "must_have";
    var nuggetId = n.nugget_id;

    // Only show highlights for enabled/selected nuggets
    if (typeof isNuggetEffectivelyEnabled === "function" && !isNuggetEffectivelyEnabled(nuggetId)) {
      return;
    }

    var gradeInfo = null;

    if (docId) {
      // Document mode - check doc_grades
      gradeInfo = getDocGrade(topicId, docId, nuggetId);
      if (gradeInfo && gradeInfo.paragraphs) {
        // Look for addressed_quote in paragraphs (pre-loaded format)
        Object.keys(gradeInfo.paragraphs).forEach(function(pk) {
          var para = gradeInfo.paragraphs[pk];
          if (para.addressed_quote) {
            highlights.push({
              quote: para.addressed_quote,
              nuggetId: nuggetId,
              nuggetType: nuggetType,
              isHeavy: state.heavyHighlightNuggetId === nuggetId
            });
          }
        });
      } else if (gradeInfo && gradeInfo.addressed_quote) {
        // Flat doc grade (user-generated format)
        highlights.push({
          quote: gradeInfo.addressed_quote,
          nuggetId: nuggetId,
          nuggetType: nuggetType,
          isHeavy: state.heavyHighlightNuggetId === nuggetId
        });
      }
    } else if (runId) {
      // Report mode - check report grades (any grade with a quote)
      gradeInfo = getReportGrade(topicId, runId, nuggetId);
      if (gradeInfo && gradeInfo.addressed_quote) {
        highlights.push({
          quote: gradeInfo.addressed_quote,
          nuggetId: nuggetId,
          nuggetType: nuggetType,
          isHeavy: state.heavyHighlightNuggetId === nuggetId
        });
      }
    }
  });

  return highlights;
}

// Strip surrounding quotes from a string (handles \"...\", '...', etc.)
function stripSurroundingQuotes(s) {
  if (!s) return s;
  s = s.trim();
  // Strip escaped quotes at start/end
  while (s.length >= 2 &&
         ((s.startsWith('\\"') && s.endsWith('\\"')) ||
          (s.startsWith('"') && s.endsWith('"')) ||
          (s.startsWith("'") && s.endsWith("'")))) {
    if (s.startsWith('\\"')) {
      s = s.slice(2, -2);
    } else {
      s = s.slice(1, -1);
    }
    s = s.trim();
  }
  return s;
}

// Find substring in text (case-insensitive, whitespace-normalized)
function findQuoteInText(text, quote) {
  if (!text || !quote) return null;

  // Strip surrounding quotes that LLM may have added
  quote = stripSurroundingQuotes(quote);
  if (!quote) return null;

  // Normalize whitespace for comparison
  var normalizedText = text.replace(/\s+/g, ' ');
  var normalizedQuote = quote.trim().replace(/\s+/g, ' ');

  // Try exact match first
  var idx = normalizedText.indexOf(normalizedQuote);
  if (idx !== -1) {
    // Map back to original positions
    var origStart = mapNormalizedToOriginal(text, idx);
    var origEnd = mapNormalizedToOriginal(text, idx + normalizedQuote.length);
    return { start: origStart, end: origEnd };
  }

  // Try case-insensitive match
  idx = normalizedText.toLowerCase().indexOf(normalizedQuote.toLowerCase());
  if (idx !== -1) {
    var origStart = mapNormalizedToOriginal(text, idx);
    var origEnd = mapNormalizedToOriginal(text, idx + normalizedQuote.length);
    return { start: origStart, end: origEnd };
  }

  return null;
}

// Map position in normalized text (single spaces) back to original text
function mapNormalizedToOriginal(original, normalizedPos) {
  var origIdx = 0;
  var normIdx = 0;
  var inWhitespace = false;

  while (normIdx < normalizedPos && origIdx < original.length) {
    var ch = original[origIdx];
    if (/\s/.test(ch)) {
      if (!inWhitespace) {
        normIdx++;
        inWhitespace = true;
      }
      origIdx++;
    } else {
      normIdx++;
      origIdx++;
      inWhitespace = false;
    }
  }

  return origIdx;
}

// Collect text nodes for quote highlighting
// Skips citation-marker and remove-span to match SKIP_CLASSES used by user span selection
// Descends into MARK (user highlights) and quote-highlight to find nested text nodes
// Returns: {textNodes: [], nodeStarts: [], plainText: string}
// NOTE: Named differently from collectTextNodes in JS_SPANS_CORE to avoid shadowing
function collectQuoteTextNodes(container) {
  var textNodes = [];
  var nodeStarts = [];
  var pos = 0;
  function walk(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      textNodes.push(node);
      nodeStarts.push(pos);
      pos += node.textContent.length;
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      // Skip citation-marker and remove-span (matches SKIP_CLASSES used by user span selection)
      if (node.classList.contains('citation-marker') || node.classList.contains('remove-span')) {
        return;
      }
      for (var i = 0; i < node.childNodes.length; i++) {
        walk(node.childNodes[i]);
      }
    }
  }
  walk(container);

  var plainText = textNodes.map(function(n) { return n.textContent; }).join('');
  return { textNodes: textNodes, nodeStarts: nodeStarts, plainText: plainText };
}

// Apply quote highlights to a container element
// Call AFTER applyHighlights (user spans) to layer quote highlights
function applyQuoteHighlights(container, highlights) {
  if (!highlights || highlights.length === 0) return;

  // Apply each highlight separately, re-collecting text nodes after each wrap
  // This handles DOM mutations from previous wraps
  highlights.forEach(function(h) {
    // Re-collect text nodes fresh for each highlight (uses quote-specific function)
    var info = collectQuoteTextNodes(container);

    var pos = findQuoteInText(info.plainText, h.quote);
    if (pos) {
      wrapQuoteRange(info.textNodes, info.nodeStarts, {
        start: pos.start,
        end: pos.end,
        nuggetType: h.nuggetType,
        nuggetId: h.nuggetId,
        isHeavy: h.isHeavy
      });
    }
  });
}

// Wrap a quote range with highlight span
function wrapQuoteRange(textNodes, nodeStarts, highlight) {
  for (var i = 0; i < textNodes.length; i++) {
    var nodeStart = nodeStarts[i];
    var nodeEnd = nodeStart + textNodes[i].textContent.length;

    if (highlight.start >= nodeEnd) continue;
    if (highlight.end <= nodeStart) break;

    var localStart = Math.max(0, highlight.start - nodeStart);
    var localEnd = Math.min(textNodes[i].textContent.length, highlight.end - nodeStart);

    var range = document.createRange();
    range.setStart(textNodes[i], localStart);
    range.setEnd(textNodes[i], localEnd);

    var span = document.createElement("span");
    span.className = "quote-highlight quote-highlight-" + highlight.nuggetType;
    if (highlight.isHeavy) {
      span.classList.add("quote-highlight-heavy");
    }
    span.setAttribute("data-nugget-id", highlight.nuggetId);

    try {
      range.surroundContents(span);
    } catch (e) {
      // Range may cross element boundaries - skip this highlight
    }
  }
}

// Toggle heavy highlight for a nugget
function toggleHeavyHighlight(nuggetId) {
  if (state.heavyHighlightNuggetId === nuggetId) {
    state.heavyHighlightNuggetId = null;
  } else {
    state.heavyHighlightNuggetId = nuggetId;
  }
  // Re-render to apply highlight changes
  renderMain();
}

// Clear heavy highlight (called on navigation)
function clearHeavyHighlight() {
  state.heavyHighlightNuggetId = null;
}
"""