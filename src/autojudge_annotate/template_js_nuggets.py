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
// Structure: DATA.doc_grades[query_id][doc_id][nugget_id] -> {paragraphs: {...}, max_grade: int}
function getDocGrade(topicId, docId, nuggetId) {
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

  // Check doc grades or doc_ids for current docs (not applicable for user nuggets)
  if (!isUserNugget && currentDocIds && currentDocIds.length > 0) {
    currentDocIds.forEach(function(docId) {
      // First try doc_grades (new format)
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
      } else if (docSatisfiesNugget(n, docId)) {
        // Fall back to doc_ids check (old format)
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
    html += '<span class="nugget-docs" title="' + escapeHtml(tooltip) + '">';
    if (sourceDesc) {
      html += '(' + sourceDesc + ')';
    } else if (gradeForVerdict) {
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
  html += '<h3 class="nugget-panel-header" data-panel="nuggets">';
  html += '<span class="nugget-panel-toggle">&#9656;</span>';
  html += 'Nuggets (' + enabledCount + (enabledCount < totalCount ? '/' + totalCount : '') + ')';
  html += '</h3>';
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
  var total = nuggets.length + claims.length;

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

  return { satisfied: satisfied, total: total };
}
"""