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
function getReportGrade(topicId, runId, nuggetId) {
  if (!DATA.nugget_grades) {
    console.log("No nugget_grades in DATA");
    return null;
  }
  var topicGrades = DATA.nugget_grades[topicId];
  if (!topicGrades) {
    console.log("No grades for topic:", topicId, "Available topics:", Object.keys(DATA.nugget_grades));
    return null;
  }
  var runGrades = topicGrades[runId];
  if (!runGrades) {
    console.log("No grades for run:", runId, "Available runs:", Object.keys(topicGrades));
    return null;
  }
  var grade = runGrades[nuggetId];
  if (!grade) {
    console.log("No grade for nugget:", nuggetId, "Available nuggets:", Object.keys(runGrades).slice(0, 5));
  }
  return grade || null;
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

// Render the nugget panel for a topic
// In report mode: show report grades + doc satisfaction
// In document mode: show which nuggets the current doc satisfies
function renderNuggetPanel(topicId, currentDocIds) {
  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];
  var claims = bank.claims || [];

  if (nuggets.length === 0 && claims.length === 0) {
    return ''; // No nuggets for this topic
  }

  // Get current run for report mode grades
  var currentRunId = state.selectedRun || null;
  var isReportMode = state.mode === "reports";

  var html = '<div class="nugget-panel">';
  html += '<h3 class="nugget-panel-header">Nuggets (' + (nuggets.length + claims.length) + ')</h3>';

  // Render nugget questions
  if (nuggets.length > 0) {
    html += '<div class="nugget-list">';
    nuggets.forEach(function(n) {
      var satisfyingDocs = [];

      // Check if any of the current docs satisfy this nugget
      if (currentDocIds && currentDocIds.length > 0) {
        currentDocIds.forEach(function(docId) {
          if (docSatisfiesNugget(n, docId)) {
            satisfyingDocs.push(docId);
          }
        });
      }

      // Get report grade if in report mode
      var reportGrade = null;
      if (isReportMode && currentRunId) {
        reportGrade = getReportGrade(topicId, currentRunId, n.nugget_id);
      }

      // Determine verdict: use report grade if available, else doc satisfaction
      // Use "unknown" state when we don't have relevant evaluation data
      var verdict;
      if (reportGrade) {
        verdict = gradeToVerdict(reportGrade.grade);
      } else if (satisfyingDocs.length > 0) {
        verdict = { cls: "nugget-satisfied", icon: "&#10003;", label: "satisfied" };
      } else if (isReportMode && !n.has_grades) {
        // In report mode but no grade data exists for this nugget
        verdict = unknownVerdict();
      } else if (!isReportMode && !n.has_doc_info) {
        // In document mode but no doc_ids data exists for this nugget
        verdict = unknownVerdict();
      } else {
        verdict = { cls: "nugget-not-satisfied", icon: "&#10007;", label: "not satisfied" };
      }

      // Build source description
      var sourceDesc = buildSourceDesc(reportGrade, satisfyingDocs);

      html += '<div class="nugget-item ' + verdict.cls + '">';
      html += '<span class="nugget-verdict">' + verdict.icon + '</span>';
      html += '<span class="nugget-text">' + escapeHtml(n.text) + '</span>';
      if (sourceDesc) {
        var tooltip = satisfyingDocs.length > 0 ? satisfyingDocs.join(', ') : '';
        if (reportGrade && reportGrade.reasoning) {
          tooltip = (tooltip ? tooltip + '\\n\\n' : '') + 'Reasoning: ' + reportGrade.reasoning;
        }
        html += '<span class="nugget-docs" title="' + escapeHtml(tooltip) + '">';
        html += '(' + sourceDesc + ')';
        html += '</span>';
      }
      html += '</div>';
    });
    html += '</div>';
  }

  // Render claims (if any)
  if (claims.length > 0) {
    html += '<div class="nugget-claims-section">';
    html += '<h4>Claims</h4>';
    html += '<div class="nugget-list">';
    claims.forEach(function(c) {
      var satisfyingDocs = [];

      if (currentDocIds && currentDocIds.length > 0) {
        currentDocIds.forEach(function(docId) {
          if (docSatisfiesNugget(c, docId)) {
            satisfyingDocs.push(docId);
          }
        });
      }

      // Get report grade for claims (using claim_id)
      var reportGrade = null;
      if (isReportMode && currentRunId) {
        reportGrade = getReportGrade(topicId, currentRunId, c.claim_id);
      }

      var verdict;
      if (reportGrade) {
        verdict = gradeToVerdict(reportGrade.grade);
      } else if (satisfyingDocs.length > 0) {
        verdict = { cls: "nugget-satisfied", icon: "&#10003;", label: "satisfied" };
      } else if (isReportMode && !c.has_grades) {
        verdict = unknownVerdict();
      } else if (!isReportMode && !c.has_doc_info) {
        verdict = unknownVerdict();
      } else {
        verdict = { cls: "nugget-not-satisfied", icon: "&#10007;", label: "not satisfied" };
      }

      var sourceDesc = buildSourceDesc(reportGrade, satisfyingDocs);

      html += '<div class="nugget-item ' + verdict.cls + '">';
      html += '<span class="nugget-verdict">' + verdict.icon + '</span>';
      html += '<span class="nugget-text">' + escapeHtml(c.text) + '</span>';
      if (sourceDesc) {
        html += '<span class="nugget-docs">(' + sourceDesc + ')</span>';
      }
      html += '</div>';
    });
    html += '</div>';
    html += '</div>';
  }

  html += '</div>';
  return html;
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
"""