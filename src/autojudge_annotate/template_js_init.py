"""JS initialization: showCitationModal, modal listeners, handleDownload, clear-all, initial render."""

JS_INIT = r"""
// --- Citation modal ---

function showCitationModal(report, citationId) {
  var doc = report.documents[citationId];
  if (!doc) {
    modalTitle.textContent = citationId;
    modalUrl.textContent = "";
    modalUrl.href = "#";
    modalText.textContent = "Document not available.";
  } else {
    modalTitle.textContent = doc.title || citationId;
    if (doc.url) {
      modalUrl.textContent = doc.url;
      modalUrl.href = doc.url;
    } else {
      modalUrl.textContent = "";
      modalUrl.href = "#";
    }
    modalText.textContent = doc.text || "";
  }
  modalOverlay.classList.add("visible");
}

if (modalClose) {
  modalClose.addEventListener("click", function() {
    modalOverlay.classList.remove("visible");
  });
}
if (modalOverlay) {
  modalOverlay.addEventListener("click", function(e) {
    if (e.target === modalOverlay) modalOverlay.classList.remove("visible");
  });
}

// --- Download ---

function downloadAnnotations() {
  handleDownload();
}

function handleDownload() {
  // Export NuggetBanks in JSONL format (one line per topic)
  var lines = buildNuggetBanksOutput();
  if (lines.length === 0) {
    alert("No nugget banks to download. Make sure there are nuggets for at least one topic.");
    return;
  }
  var blob = new Blob([lines.join("\n") + "\n"], { type: "application/jsonl" });
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = DATA.dataset + "-nuggets.jsonl";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Clear all annotations
var clearAllBtn = document.getElementById("clear-all-btn");
if (clearAllBtn) {
  clearAllBtn.addEventListener("click", function() {
    if (!confirm("Clear all your annotations for this dataset? This cannot be undone.")) return;

    // Use centralized reset function (defined in template_js_state.py)
    resetAllAnnotationState();

    // Also delete from server if online and connected
    if (syncMode === "online" && typeof syncDeleteAll === "function") {
      syncDeleteAll().then(function(ok) {
        if (ok) setSyncStatus("success");
        else setSyncStatus("error");
      });
    }
  });
}

// Initialize LLM indicator in topbar
if (typeof initLlmIndicator === "function") {
  initLlmIndicator();
}

// Initial render — auto-select first topic, first run, and mode-specific defaults
if (topicIds.length > 0) {
  state.selectedTopic = topicIds[0];
  var firstRuns = reportIndex[topicIds[0]] ? Object.keys(reportIndex[topicIds[0]]).sort() : [];
  if (firstRuns.length > 0) {
    state.selectedRun = firstRuns[0];
    if (state.mode === "documents" && runDocsIndex[topicIds[0]] && runDocsIndex[topicIds[0]][firstRuns[0]]) {
      var firstDocs = runDocsIndex[topicIds[0]][firstRuns[0]];
      if (firstDocs.length > 0) state.selectedDoc = firstDocs[0];
    }
    if (state.mode === "citations") {
      state.selectedSentenceIdx = 0;
      state.selectedCitationIdx = 0;
    }
  }
}
// Apply phase visibility before rendering
if (typeof applyPhaseVisibility === "function") {
  applyPhaseVisibility();
}

// Render using new UI if available, else fallback to legacy
if (typeof renderAll === "function") {
  renderAll();
} else {
  renderSidebar();
  renderMain();
}

// --- Global Exports ---
// Expose functions to window for onclick handlers in HTML
// (functions defined in IIFE are not accessible to inline onclick otherwise)

window.setPhase = typeof setPhase === "function" ? setPhase : function() {};
window.goBack = typeof goBack === "function" ? goBack : function() {};
window.setRankingScope = typeof setRankingScope === "function" ? setRankingScope : function() {};
window.downloadAnnotations = typeof downloadAnnotations === "function" ? downloadAnnotations : function() {};
window.gradeAllNuggets = typeof gradeAllNuggets === "function" ? gradeAllNuggets : function() {};
window.showDraft = typeof showDraft === "function" ? showDraft : function() {};
window.hideDraft = typeof hideDraft === "function" ? hideDraft : function() {};
window.canonicalize = typeof canonicalize === "function" ? canonicalize : function() {};
window.checkImpact = typeof checkImpact === "function" ? checkImpact : function() {};
window.commitNugget = typeof commitNugget === "function" ? commitNugget : function() {};
window.removeSpan = typeof removeSpan === "function" ? removeSpan : function() {};
window.updateDraftFreetext = typeof updateDraftFreetext === "function" ? updateDraftFreetext : function() {};
window.updateDraftNuggetText = typeof updateDraftNuggetText === "function" ? updateDraftNuggetText : function() {};
window.setDraftCategory = typeof setDraftCategory === "function" ? setDraftCategory : function() {};
window.navigateToQuote = typeof navigateToQuote === "function" ? navigateToQuote : function() {};
window.toggleSolo = typeof toggleSolo === "function" ? toggleSolo : function() {};
window.unsoloAll = typeof unsoloAll === "function" ? unsoloAll : function() {};
window.toggleNuggetEnabled = typeof toggleNuggetEnabled === "function" ? toggleNuggetEnabled : function() {};
window.toggleQuoteHighlight = typeof toggleQuoteHighlight === "function" ? toggleQuoteHighlight : function() {};
window.selectReportFromRanking = typeof selectReportFromRanking === "function" ? selectReportFromRanking : function() {};
"""
