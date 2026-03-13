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

modalClose.addEventListener("click", function() {
  modalOverlay.classList.remove("visible");
});
modalOverlay.addEventListener("click", function(e) {
  if (e.target === modalOverlay) modalOverlay.classList.remove("visible");
});

// --- Download ---

function handleDownload() {
  var lines = buildOutputLines();
  if (lines.length === 0) {
    alert("No annotations to download.");
    return;
  }
  var blob = new Blob([lines.join("\n") + "\n"], { type: "application/jsonl" });
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = DATA.dataset + "-annotations.jsonl";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Clear all annotations
document.getElementById("clear-all-btn").addEventListener("click", function() {
  if (!confirm("Clear ALL annotations for this dataset? This cannot be undone.")) return;
  state.annotations = {};
  localStorage.removeItem("autojudge_annotate_state_" + DATA.dataset);
  // Also delete from server if online and connected
  if (syncMode === "online" && typeof syncDeleteAll === "function") {
    syncDeleteAll().then(function(ok) {
      if (ok) setSyncStatus("success");
      else setSyncStatus("error");
    });
  }
  renderSidebar();
  renderMain();
});

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
renderSidebar();
renderMain();
"""
