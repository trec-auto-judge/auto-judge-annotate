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

// Render the nugget panel for a topic
// In report mode: show which nuggets are satisfied by cited documents
// In document mode: show which nuggets the current doc satisfies
function renderNuggetPanel(topicId, currentDocIds) {
  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];
  var claims = bank.claims || [];

  if (nuggets.length === 0 && claims.length === 0) {
    return ''; // No nuggets for this topic
  }

  var html = '<div class="nugget-panel">';
  html += '<h3 class="nugget-panel-header">Nuggets (' + (nuggets.length + claims.length) + ')</h3>';

  // Render nugget questions
  if (nuggets.length > 0) {
    html += '<div class="nugget-list">';
    nuggets.forEach(function(n) {
      var satisfied = false;
      var satisfyingDocs = [];

      // Check if any of the current docs satisfy this nugget
      if (currentDocIds && currentDocIds.length > 0) {
        currentDocIds.forEach(function(docId) {
          if (docSatisfiesNugget(n, docId)) {
            satisfied = true;
            satisfyingDocs.push(docId);
          }
        });
      }

      var verdictClass = satisfied ? "nugget-satisfied" : "nugget-not-satisfied";
      var verdictIcon = satisfied ? "&#10003;" : "&#10007;";

      html += '<div class="nugget-item ' + verdictClass + '">';
      html += '<span class="nugget-verdict">' + verdictIcon + '</span>';
      html += '<span class="nugget-text">' + escapeHtml(n.text) + '</span>';
      if (satisfyingDocs.length > 0) {
        html += '<span class="nugget-docs" title="' + satisfyingDocs.join(', ') + '">';
        html += '(' + satisfyingDocs.length + ' doc' + (satisfyingDocs.length > 1 ? 's' : '') + ')';
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
      var satisfied = false;
      var satisfyingDocs = [];

      if (currentDocIds && currentDocIds.length > 0) {
        currentDocIds.forEach(function(docId) {
          if (docSatisfiesNugget(c, docId)) {
            satisfied = true;
            satisfyingDocs.push(docId);
          }
        });
      }

      var verdictClass = satisfied ? "nugget-satisfied" : "nugget-not-satisfied";
      var verdictIcon = satisfied ? "&#10003;" : "&#10007;";

      html += '<div class="nugget-item ' + verdictClass + '">';
      html += '<span class="nugget-verdict">' + verdictIcon + '</span>';
      html += '<span class="nugget-text">' + escapeHtml(c.text) + '</span>';
      if (satisfyingDocs.length > 0) {
        html += '<span class="nugget-docs">(' + satisfyingDocs.length + ' docs)</span>';
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
"""