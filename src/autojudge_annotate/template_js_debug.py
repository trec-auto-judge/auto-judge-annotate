"""Debug / inspectability helpers for the generated annotator page.

The page's JS runs inside an IIFE, so `state`, `DATA`, and the lookup helpers are not
reachable from the browser console. This module (appended last, inside the IIFE) exposes
them on `window`, adds a `ajCheck()` self-check that reports which nugget cards fail to
resolve a grade, and adds a "Reset local data" button + `ajResetLocalData()` so a viewer
with stale localStorage can recover without the console. Safe to keep in production.
"""

JS_DEBUG = r"""
// === Debug / inspectability (safe in production) ===
try {
  window.DATA = DATA;
  window.state = state;
  if (typeof getReportGrade === "function") window.getReportGrade = getReportGrade;
  if (typeof getNuggetsForTopic === "function") window.getNuggetsForTopic = getNuggetsForTopic;
  if (typeof getDocGrade === "function") window.getDocGrade = getDocGrade;
  if (typeof hasUserNuggetGrades === "function") window.hasUserNuggetGrades = hasUserNuggetGrades;
  if (typeof nuggetBanksFingerprint === "function") window.nuggetBanksFingerprint = nuggetBanksFingerprint;
} catch (e) { console.warn("[debug] expose failed:", e); }

// Report, for a topic/run, the cards whose nugget_id does NOT resolve to a grade, and
// whether the grade nonetheless exists in DATA (-> an id mismatch / stale localStorage).
// Usage: ajCheck()  or  ajCheck("rag2026-2", "adela")
window.ajCheck = function (topicId, runId) {
  topicId = topicId || state.selectedTopic ||
            (DATA.nugget_grades && Object.keys(DATA.nugget_grades)[0]) ||
            (DATA.nugget_banks && Object.keys(DATA.nugget_banks)[0]);
  var bank = (DATA.nugget_banks && DATA.nugget_banks[topicId]) || {};
  var nuggets = (bank.nuggets || []).concat(bank.claims || []);
  if (!runId) {
    var runs = (DATA.nugget_grades && DATA.nugget_grades[topicId])
      ? Object.keys(DATA.nugget_grades[topicId]) : [];
    runId = state.selectedRun || runs[0];
  }
  var dataG = (DATA.nugget_grades && DATA.nugget_grades[topicId] &&
               DATA.nugget_grades[topicId][runId]) || {};
  var stateG = (state.userNuggetGrades && state.userNuggetGrades[topicId] &&
                state.userNuggetGrades[topicId][runId]) || {};
  var missing = [];
  nuggets.forEach(function (n) {
    var id = n.nugget_id;
    if (!stateG[id] && !dataG[id]) {
      missing.push({ id: id, inDATA: !!dataG[id], len: (n.text || n.question || "").length });
    }
  });
  console.log("[ajCheck] topic=" + topicId + " run=" + runId +
    " | cards=" + nuggets.length +
    " | DATA grade keys=" + Object.keys(dataG).length +
    " | state grade keys=" + Object.keys(stateG).length +
    " | cards without grade=" + missing.length);
  if (missing.length) {
    console.log("[ajCheck] unresolved card ids (inDATA=true would mean the grade exists " +
      "but the card id differs -> stale localStorage / id mismatch):", missing.slice(0, 15));
  }
  return { topicId: topicId, runId: runId, cards: nuggets.length, missing: missing };
};

// Clear this dataset's per-viewer localStorage (nuggets, grades, annotations) and reload.
window.ajResetLocalData = function () {
  var ds = DATA.dataset;
  ["user_nuggets", "user_nuggets_fp", "grades", "docgrades", "state", "mode", "phase"]
    .forEach(function (k) {
      try { localStorage.removeItem("autojudge_annotate_" + k + "_" + ds); } catch (e) {}
    });
  location.reload();
};

// Small unobtrusive reset button so a viewer with stale local data can recover.
try {
  var _ajBtn = document.createElement("button");
  _ajBtn.textContent = "Reset local data";
  _ajBtn.title = "Clear this browser's saved nuggets/grades/annotations for this dataset " +
                 "and reload from the built file";
  _ajBtn.style.cssText = "position:fixed;bottom:8px;right:8px;z-index:99999;" +
    "font-size:11px;padding:3px 8px;opacity:0.55;background:#fff;border:1px solid #999;" +
    "border-radius:4px;cursor:pointer;";
  _ajBtn.onmouseover = function () { _ajBtn.style.opacity = "1"; };
  _ajBtn.onmouseout = function () { _ajBtn.style.opacity = "0.55"; };
  _ajBtn.onclick = function () {
    if (confirm('Clear this browser\'s local nuggets/grades/annotations for "' +
                DATA.dataset + '" and reload from the built file? ' +
                'In-browser annotation work for this dataset will be lost.')) {
      window.ajResetLocalData();
    }
  };
  document.body.appendChild(_ajBtn);
} catch (e) { console.warn("[debug] reset button failed:", e); }

try {
  console.log("[debug] window.DATA / window.state exposed. Run ajCheck() to inspect grade " +
    "resolution; ajResetLocalData() to clear stale local data.");
  ajCheck();
} catch (e) { console.warn("[ajCheck] on-load run failed:", e); }
"""
