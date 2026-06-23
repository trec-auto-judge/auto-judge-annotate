"""JavaScript for phase management (Creation, QC, Observe).

Handles phase transitions, navigation history, and visibility toggling.
"""

JS_PHASE = r"""
// ============================================================================
// Phase Management
// ============================================================================

// Push current state to navigation history (including draft state)
function pushNavHistory() {
    // Deep copy the draft state so it's preserved
    var draftCopy = null;
    if (state.draftState && state.draftState.visible) {
        draftCopy = JSON.parse(JSON.stringify(state.draftState));
    }

    state.navHistory.push({
        phase: state.phase,
        topicId: state.selectedTopic,
        runId: state.selectedRun,
        draftState: draftCopy
    });
    updateBackButton();
}

// Update back button visibility
function updateBackButton() {
    var btn = document.getElementById('backBtn');
    if (btn) {
        btn.classList.toggle('visible', state.navHistory.length > 0);
    }
}

// Go back to previous state (restoring draft if it was open)
function goBack() {
    if (state.navHistory.length === 0) return;
    var prev = state.navHistory.pop();
    updateBackButton();

    // Restore previous state without pushing to history
    state.phase = prev.phase;
    state.selectedTopic = prev.topicId;
    state.selectedRun = prev.runId;

    // Restore draft state if it was open
    if (prev.draftState) {
        state.draftState = prev.draftState;
    }

    // Update phase tab visual
    document.querySelectorAll('.phase-tab').forEach(function(t) {
        t.classList.remove('active');
    });
    var activeTab = document.getElementById('tab-' + state.phase);
    if (activeTab) activeTab.classList.add('active');

    applyPhaseVisibility();
    renderAll();

    // Re-render draft card if it was open
    if (prev.draftState && prev.draftState.visible && typeof renderDraftCard === 'function') {
        renderDraftCard();
    }
}

// Set the current phase
function setPhase(phase) {
    if (phase !== state.phase) {
        pushNavHistory();
    }
    state.phase = phase;

    // Update phase tab visuals
    document.querySelectorAll('.phase-tab').forEach(function(t) {
        t.classList.remove('active');
    });
    var activeTab = document.getElementById('tab-' + phase);
    if (activeTab) activeTab.classList.add('active');

    applyPhaseVisibility();
    renderAll();
    savePhase();
    autoSave();
}

// Apply visibility based on current phase
function applyPhaseVisibility() {
    var isCreation = state.phase === 'creation';
    var isQC = state.phase === 'qc';
    var isObserve = state.phase === 'observe';

    // Source panel visible only in Creation
    var sourcePanel = document.getElementById('sourcePanel');
    if (sourcePanel) {
        sourcePanel.classList.toggle('hidden', !isCreation);
    }

    // Ranking panel visible in QC and Observe
    var rankingPanel = document.getElementById('rankingPanel');
    if (rankingPanel) {
        rankingPanel.classList.toggle('visible', isQC || isObserve);
    }

    // Reports section visible only in Creation
    var reportsSection = document.getElementById('reportsSection');
    if (reportsSection) {
        reportsSection.classList.toggle('hidden', !isCreation);
    }

    // QC controls (solo/checkbox) visible only in QC
    document.querySelectorAll('.qc-controls').forEach(function(el) {
        el.classList.toggle('visible', isQC);
    });

    // Category weights: visible in QC and Observe, read-only in Observe
    document.querySelectorAll('.category-weight-group').forEach(function(el) {
        el.classList.toggle('visible', isQC || isObserve);
    });
    document.querySelectorAll('.category-weight').forEach(function(el) {
        el.disabled = isObserve;
        el.style.opacity = isObserve ? '0.7' : '1';
    });

    // Report-specific nugget info visible in Creation with report selected
    document.querySelectorAll('.nugget-report').forEach(function(el) {
        el.classList.toggle('visible', isCreation && state.selectedRun);
    });

    // Edit buttons hidden in Observe
    document.querySelectorAll('.edit-btn').forEach(function(el) {
        el.classList.toggle('hidden', isObserve);
    });

    // + Nugget button hidden in Observe
    var newNuggetBtn = document.getElementById('newNuggetBtn');
    if (newNuggetBtn) {
        newNuggetBtn.classList.toggle('hidden', isObserve);
    }

    // Ranking toggle visible only in Observe
    var rankingToggle = document.getElementById('rankingToggle');
    if (rankingToggle) {
        rankingToggle.classList.toggle('visible', isObserve);
    }

    // Metrics bar visible only in Observe
    var metricsBar = document.getElementById('metricsBar');
    if (metricsBar) {
        metricsBar.classList.toggle('visible', isObserve);
    }
}

// Set ranking scope (all queries vs single query) - Observe mode only
function setRankingScope(scope) {
    state.rankingScope = scope;

    // Update toggle buttons
    var toggleBtns = document.querySelectorAll('#rankingToggle button');
    toggleBtns.forEach(function(btn) {
        btn.classList.remove('active');
    });
    var activeBtn = document.querySelector('#rankingToggle button[onclick*="' + scope + '"]');
    if (activeBtn) activeBtn.classList.add('active');

    renderRankingPanel();
}

// Cross-phase navigation: from ranking to report in Creation
function selectReportFromRanking(runId) {
    pushNavHistory();
    state.selectedRun = runId;
    state.phase = 'creation';

    document.querySelectorAll('.phase-tab').forEach(function(t) {
        t.classList.remove('active');
    });
    document.getElementById('tab-creation').classList.add('active');

    applyPhaseVisibility();
    renderAll();
}

// Navigate to a quote from impact preview
// Preserves the draft state so user can see the quote in context
function navigateToQuote(runId) {
    // Push history before changing state (includes draft)
    pushNavHistory();

    // Just change the selected run - don't hide draft or change phase
    state.selectedRun = runId;

    // Ensure we're in creation mode to see the report
    if (state.phase !== 'creation') {
        state.phase = 'creation';
        document.querySelectorAll('.phase-tab').forEach(function(t) {
            t.classList.remove('active');
        });
        document.getElementById('tab-creation').classList.add('active');
        applyPhaseVisibility();
    }

    // Re-render to show new report
    renderAll();

    // Keep draft visible - re-render it
    if (state.draftState && state.draftState.visible && typeof renderDraftCard === 'function') {
        renderDraftCard();
    }
}

// Render all panels based on current state
function renderAll() {
    renderNavPanel();

    if (state.phase === 'creation') {
        renderSourcePanel();
    } else {
        renderRankingPanel();
    }

    renderNuggetsPanel();
}
"""
