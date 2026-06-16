"""JS nuggets mode: criteria panel, report scoring/ranking, report viewer."""

JS_NUGGETS_MODE = r"""
// --- Nuggets Mode ---

// Count how many reports/documents satisfy a nugget
// Returns {reportsSatisfied, reportsPartial, reportsTotal, docsSatisfied, docsTotal}
function countNuggetCoverageStats(topicId, nuggetId, nugget) {
  var stats = {
    reportsSatisfied: 0,
    reportsPartial: 0,
    reportsTotal: 0,
    docsSatisfied: 0,
    docsTotal: 0
  };

  // Count reports
  if (reportIndex[topicId]) {
    var runs = Object.keys(reportIndex[topicId]);
    stats.reportsTotal = runs.length;
    runs.forEach(function(runId) {
      var grade = getReportGrade(topicId, runId, nuggetId);
      if (grade && grade.grade >= 4) {
        stats.reportsSatisfied++;
      } else if (grade && grade.grade >= 1) {
        stats.reportsPartial++;
      }
    });
  }

  // Count documents (if nugget has doc_ids)
  if (nugget && nugget.doc_ids) {
    // Get all unique documents across all reports for this topic
    var allDocs = {};
    if (reportIndex[topicId]) {
      Object.keys(reportIndex[topicId]).forEach(function(runId) {
        var report = reportIndex[topicId][runId];
        if (report && report.documents) {
          Object.keys(report.documents).forEach(function(docId) {
            allDocs[docId] = true;
          });
        }
      });
    }
    var allDocIds = Object.keys(allDocs);
    stats.docsTotal = allDocIds.length;

    allDocIds.forEach(function(docId) {
      if (nugget.doc_ids.indexOf(docId) !== -1) {
        stats.docsSatisfied++;
      }
    });
  }

  return stats;
}

// Format nugget coverage stats as a string (e.g., "3/8 (+2 partial)")
function formatNuggetCoverageStats(stats) {
  var parts = [];

  // Reports coverage
  if (stats.reportsTotal > 0) {
    var reportStr = stats.reportsSatisfied + "/" + stats.reportsTotal;
    if (stats.reportsPartial > 0) {
      reportStr += " (+" + stats.reportsPartial + ")";
    }
    parts.push(reportStr + " reports");
  }

  // Document coverage (only show if we have doc_ids data)
  if (stats.docsTotal > 0) {
    parts.push(stats.docsSatisfied + "/" + stats.docsTotal + " docs");
  }

  return parts.join(", ");
}

// Collect all canonicalized nuggets from clues for a topic
function getCanonicalizedNuggetsForTopic(topicId) {
  var result = [];
  var seen = {};

  Object.keys(state.annotations).forEach(function(key) {
    var ann = state.annotations[key];
    // Check if this annotation is for the given topic
    if (ann.topicId !== topicId) return;
    if (!ann.nugget_clues) return;

    ann.nugget_clues.forEach(function(clue, clueIdx) {
      if (clue.canonicalized && clue.canonicalized.nugget_text) {
        // Create a unique ID for this canonicalized nugget
        var nuggetId = "user_" + key + "_" + clueIdx;
        if (seen[nuggetId]) return;
        seen[nuggetId] = true;

        result.push({
          nugget_id: nuggetId,
          text: clue.canonicalized.nugget_text,
          nugget_type: clue.clue_type,
          explanation: clue.canonicalized.explanation,
          source: "user",  // Mark as user-created
          annotation_key: key,
          clue_idx: clueIdx
        });
      }
    });
  });

  return result;
}

// Compute score for a report based on current weights and enabled nuggets
function computeReportScore(topicId, runId) {
  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];

  if (nuggets.length === 0) return 0;

  var weight = state.nuggetWeights.must;
  if (weight === 0) return 0;

  var enabledNuggets = nuggets.filter(function(n) {
    return state.enabledNuggets[n.nugget_id] !== false; // default true
  });

  if (enabledNuggets.length === 0) return 0;

  var satisfied = 0;
  enabledNuggets.forEach(function(n) {
    var grade = getReportGrade(topicId, runId, n.nugget_id);
    if (grade && grade.grade >= 4) {
      satisfied += 1;
    } else if (grade && grade.grade >= 1) {
      satisfied += 0.5; // partial credit
    }
  });

  return weight * (satisfied / enabledNuggets.length);
}

// Rank reports for current topic
function rankReports(topicId) {
  var runs = reportIndex[topicId] ? Object.keys(reportIndex[topicId]).sort() : [];
  var scored = runs.map(function(runId) {
    return { runId: runId, score: computeReportScore(topicId, runId) };
  });
  scored.sort(function(a, b) { return b.score - a.score; });
  return scored;
}

// Get summary string for a report
function getReportSummary(topicId, runId) {
  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];

  var enabledNuggets = nuggets.filter(function(n) {
    return state.enabledNuggets[n.nugget_id] !== false;
  });

  if (enabledNuggets.length === 0) return "";

  var satisfied = 0;
  var partial = 0;
  enabledNuggets.forEach(function(n) {
    var grade = getReportGrade(topicId, runId, n.nugget_id);
    if (grade && grade.grade >= 4) {
      satisfied++;
    } else if (grade && grade.grade >= 1) {
      partial++;
    }
  });

  return satisfied + "/" + enabledNuggets.length + (partial > 0 ? " (+" + partial + " partial)" : "");
}

// Render criteria panel for nuggets mode
function renderCriteriaPanel(topicId) {
  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];
  var userNuggets = getCanonicalizedNuggetsForTopic(topicId);

  // Separate user nuggets by type
  var userMustHave = userNuggets.filter(function(n) { return n.nugget_type === "must_have"; });
  var userShouldHave = userNuggets.filter(function(n) { return n.nugget_type === "should_have"; });
  var userAvoid = userNuggets.filter(function(n) { return n.nugget_type === "avoid"; });

  if (nuggets.length === 0 && userNuggets.length === 0) {
    return '<div class="empty-state">No nuggets for this topic.</div>';
  }

  var html = '';

  // Must-have category
  html += '<div class="category-section">';
  html += '<div class="category-header">';
  html += '<span class="category-name">Must Have</span>';
  html += '<input type="number" class="category-weight" data-category="must" value="' + state.nuggetWeights.must + '" step="0.5" min="0" max="10">';
  html += '</div>';

  html += '<div class="nugget-list criteria-nugget-list">';
  nuggets.forEach(function(n) {
    var enabled = state.enabledNuggets[n.nugget_id] !== false;
    var checked = enabled ? "checked" : "";
    var stats = countNuggetCoverageStats(topicId, n.nugget_id, n);
    var coverageStr = formatNuggetCoverageStats(stats);

    html += '<div class="nugget-item criteria-nugget-item">';
    html += '<input type="checkbox" id="nug_' + n.nugget_id + '" data-nugget-id="' + n.nugget_id + '" ' + checked + '>';
    html += '<label for="nug_' + n.nugget_id + '">' + escapeHtml(n.text) + '</label>';
    if (coverageStr) {
      html += '<span class="nugget-coverage" title="Coverage across responses">' + escapeHtml(coverageStr) + '</span>';
    }
    html += '</div>';
  });

  // User-created must-have nuggets (shown with ? indicator)
  userMustHave.forEach(function(n) {
    html += '<div class="nugget-item criteria-nugget-item user-nugget">';
    html += '<span class="nugget-status-unknown" title="Not yet graded">?</span>';
    html += '<label title="' + escapeHtml(n.explanation || '') + '">' + escapeHtml(n.text) + '</label>';
    html += '</div>';
  });
  html += '</div>';
  html += '</div>';

  // Should-have category (if any user nuggets)
  if (userShouldHave.length > 0) {
    html += '<div class="category-section">';
    html += '<div class="category-header">';
    html += '<span class="category-name">Should Have</span>';
    html += '</div>';
    html += '<div class="nugget-list criteria-nugget-list">';
    userShouldHave.forEach(function(n) {
      html += '<div class="nugget-item criteria-nugget-item user-nugget">';
      html += '<span class="nugget-status-unknown" title="Not yet graded">?</span>';
      html += '<label title="' + escapeHtml(n.explanation || '') + '">' + escapeHtml(n.text) + '</label>';
      html += '</div>';
    });
    html += '</div>';
    html += '</div>';
  }

  // Avoid category (if any user nuggets)
  if (userAvoid.length > 0) {
    html += '<div class="category-section">';
    html += '<div class="category-header">';
    html += '<span class="category-name">Avoid</span>';
    html += '</div>';
    html += '<div class="nugget-list criteria-nugget-list">';
    userAvoid.forEach(function(n) {
      html += '<div class="nugget-item criteria-nugget-item user-nugget nugget-avoid">';
      html += '<span class="nugget-status-unknown" title="Not yet graded">?</span>';
      html += '<label title="' + escapeHtml(n.explanation || '') + '">' + escapeHtml(n.text) + '</label>';
      html += '</div>';
    });
    html += '</div>';
    html += '</div>';
  }

  return html;
}

// Render report list for nuggets mode
function renderReportList(topicId) {
  var ranked = rankReports(topicId);

  if (ranked.length === 0) {
    return '<div class="empty-state">No reports for this topic.</div>';
  }

  var html = '<div class="doc-list">';
  ranked.forEach(function(item, idx) {
    var score = item.score;
    var scoreClass = score >= 0.7 ? "score-high" : (score >= 0.3 ? "score-medium" : "score-low");
    var activeClass = state.selectedRun === item.runId ? " active" : "";

    html += '<div class="doc-item' + activeClass + '" data-run-id="' + escapeHtml(item.runId) + '">';
    html += '<span class="doc-rank">' + (idx + 1) + '.</span>';
    html += '<span class="doc-id">' + escapeHtml(item.runId) + '</span>';
    html += '<span class="doc-score ' + scoreClass + '">' + score.toFixed(2) + '</span>';
    html += '<span class="doc-summary">' + escapeHtml(getReportSummary(topicId, item.runId)) + '</span>';
    html += '<span class="doc-annotated">' + (isAnnotated(topicId, item.runId) ? '&#10003;' : '') + '</span>';
    html += '</div>';
  });
  html += '</div>';

  return html;
}

// Render report viewer for nuggets mode
function renderReportViewer(topicId, runId) {
  var report = reportIndex[topicId] && reportIndex[topicId][runId];
  if (!report) {
    return '<div class="empty-state">Report not found.</div>';
  }

  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];
  var userNuggets = getCanonicalizedNuggetsForTopic(topicId);

  var html = '<div class="doc-viewer">';

  // Verdicts
  html += '<div class="doc-verdicts">';
  html += '<h4>Verdict Breakdown</h4>';

  html += '<div class="verdict-category">';
  html += '<div class="verdict-category-name">Must Have</div>';

  nuggets.forEach(function(n) {
    if (state.enabledNuggets[n.nugget_id] === false) return;

    var grade = getReportGrade(topicId, runId, n.nugget_id);
    var icon, iconClass;

    if (grade && grade.grade >= 4) {
      icon = "&#10003;"; iconClass = "verdict-satisfied";
    } else if (grade && grade.grade >= 1) {
      icon = "~"; iconClass = "verdict-partial";
    } else if (!n.has_grades) {
      icon = "?"; iconClass = "verdict-unknown";
    } else {
      icon = "&#10007;"; iconClass = "verdict-not-satisfied";
    }

    html += '<div class="verdict-item">';
    html += '<span class="verdict-icon ' + iconClass + '">' + icon + '</span>';
    html += '<span class="verdict-text">' + escapeHtml(n.text) + '</span>';
    if (grade && grade.reasoning) {
      html += '<span class="verdict-reasoning" title="' + escapeHtml(grade.reasoning) + '">...</span>';
    }
    html += '</div>';
  });

  // User-created nuggets (not yet graded) - same style with "?" icon
  userNuggets.forEach(function(n) {
    html += '<div class="verdict-item">';
    html += '<span class="verdict-icon verdict-unknown">?</span>';
    html += '<span class="verdict-text">' + escapeHtml(n.text) + '</span>';
    html += '</div>';
  });

  html += '</div>'; // verdict-category
  html += '</div>'; // doc-verdicts

  // Report text - use report-text id for span selection compatibility
  html += '<div class="report-text" id="report-text"></div>';

  html += '</div>'; // doc-viewer

  return html;
}

// Attach event handlers for criteria panel in nuggets mode
function attachCriteriaHandlers() {
  // Weight inputs
  var weightInputs = document.querySelectorAll(".category-weight");
  weightInputs.forEach(function(input) {
    input.onchange = function() {
      var cat = input.getAttribute("data-category");
      state.nuggetWeights[cat] = parseFloat(input.value) || 0;
      renderMain();
    };
  });

  // Nugget checkboxes
  var checkboxes = document.querySelectorAll(".criteria-nugget-item input[type=checkbox]");
  checkboxes.forEach(function(cb) {
    cb.onchange = function() {
      var nuggetId = cb.getAttribute("data-nugget-id");
      state.enabledNuggets[nuggetId] = cb.checked;
      renderMain();
    };
  });
}

// Attach event handlers for report list in nuggets mode
function attachReportListHandlers() {
  var docItems = document.querySelectorAll(".doc-item");
  docItems.forEach(function(item) {
    item.onclick = function() {
      var runId = item.getAttribute("data-run-id");
      state.selectedRun = runId;
      state.selectedDoc = null;
      state.selectedSentenceIdx = null;
      state.selectedCitationIdx = null;
      // Auto-expand the run in sidebar
      state.expandedRuns[runExpandKey(state.selectedTopic, runId)] = true;
      renderSidebar();
      renderMain();
    };
  });
}

// Render main panel for nuggets mode
function renderMainNuggetsMode() {
  var html = renderRequestSection(state.selectedTopic);

  // Criteria panel
  html += '<div class="criteria-panel">';
  html += '<h3>Criteria Weights</h3>';
  html += renderCriteriaPanel(state.selectedTopic);
  html += '</div>';

  // Report list
  html += '<div class="doc-list-section">';
  html += '<h3>Reports (ranked by score)</h3>';
  html += renderReportList(state.selectedTopic);
  html += '</div>';

  // Report viewer with annotation controls
  if (state.selectedRun) {
    var ann = getReportAnnotation(state.selectedTopic, state.selectedRun);

    html += '<div class="doc-viewer-section">';
    html += '<h3>Selected Report: ' + escapeHtml(state.selectedRun) + '</h3>';
    html += renderReportViewer(state.selectedTopic, state.selectedRun);
    html += '</div>';

    // Annotation controls (spans, rating, comment, output)
    html += renderAnnotationControls(ann);
  }

  mainPanel.innerHTML = html;

  // Attach criteria and report list handlers
  attachCriteriaHandlers();
  attachReportListHandlers();

  // If a report is selected, set up span selection and annotation handlers
  if (state.selectedRun) {
    // Populate report text and apply highlights (uses currentAnnotation() internally)
    refreshReportHighlights();

    // Wire up annotation controls (rating, comment, download, sync)
    attachAnnotationHandlers();

    // Explicitly render spans and restore rating using the same annotation
    // This ensures consistency between what renderAnnotationControls generated
    // and what we display after all handlers are attached

    // Render spans
    var display = document.getElementById("spans-display");
    if (display && ann && ann.spans && ann.spans.length > 0) {
      display.innerHTML = "";
      ann.spans.forEach(function(sp) {
        var chip = document.createElement("span");
        chip.className = "span-chip";
        var sentLabel = (sp.sentence_idx !== undefined) ? "s" + sp.sentence_idx + " " : "";
        chip.textContent = sentLabel + "[" + sp.start + "-" + sp.end + "] " + sp.text;
        chip.title = sp.text;
        display.appendChild(chip);
      });
    } else if (display) {
      display.innerHTML = '<span style="color:#888;font-size:12px;">No spans selected. Highlight text above to add spans.</span>';
    }

    // Ensure rating radio is checked
    if (ann && ann.rating) {
      var ratingRadios = document.querySelectorAll('input[name="rating"]');
      ratingRadios.forEach(function(radio) {
        radio.checked = (radio.value === ann.rating);
      });
    }

    // Ensure comment is filled
    var commentInput = document.getElementById("comment-input");
    if (commentInput && ann && ann.comment) {
      commentInput.value = ann.comment;
    }
  }
}
"""
