"""JavaScript for the navigation panel (queries and reports sections)."""

JS_NAV = r"""
// ============================================================================
// Navigation Panel
// ============================================================================

function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// Count completed queries (has at least one annotated report)
function getCompletedQueryCount() {
    var count = 0;
    topicIds.forEach(function(topicId) {
        var runs = reportIndex[topicId] || {};
        var hasAnnotated = Object.keys(runs).some(function(runId) {
            return isAnnotated(topicId, runId);
        });
        if (hasAnnotated) count++;
    });
    return count;
}

// Check if a topic has any completed work
function isTopicComplete(topicId) {
    var runs = reportIndex[topicId] || {};
    return Object.keys(runs).some(function(runId) {
        return isAnnotated(topicId, runId);
    });
}

// Get nuggets count for a topic
function getNuggetCountForTopic(topicId) {
    var bank = DATA.nugget_banks && DATA.nugget_banks[topicId];
    if (!bank) return 0;
    var nuggets = bank.nuggets || [];
    var claims = bank.claims || [];
    return nuggets.length + claims.length;
}

// Render the navigation panel
function renderNavPanel() {
    var html = '';

    // Queries section (always visible)
    html += '<div class="nav-section queries-section">';
    html += '<div class="nav-section-header">';
    html += 'Queries';
    html += '<span class="nav-section-count">' + getCompletedQueryCount() + '/' + topicIds.length + '</span>';
    html += '</div>';
    html += '<div class="nav-list" id="queriesNav">';

    topicIds.forEach(function(topicId) {
        var request = requestMap[topicId];
        var isActive = state.selectedTopic === topicId;
        var isComplete = isTopicComplete(topicId);
        var nuggetCount = getNuggetCountForTopic(topicId);

        // Truncate query title
        var title = request ? (request.title || request.query || topicId) : topicId;
        if (title.length > 25) title = title.substring(0, 25) + '...';

        html += '<div class="nav-item' + (isActive ? ' active' : '') + '" data-topic="' + escapeHtml(topicId) + '">';
        html += '<span class="nav-item-status ' + (isComplete ? 'checked' : 'unchecked') + '"></span>';
        html += '<span class="nav-item-label">' + escapeHtml(topicId) + ': ' + escapeHtml(title) + '</span>';
        if (nuggetCount > 0) {
            html += '<span class="nav-item-badge">' + nuggetCount + '</span>';
        }
        html += '</div>';
    });

    html += '</div>';
    html += '</div>';

    // Reports section (only in Creation phase)
    if (state.phase === 'creation') {
        html += renderReportsSection();
    }

    navPanel.innerHTML = html;
    attachNavHandlers();
}

// Render reports section for current topic
function renderReportsSection() {
    if (!state.selectedTopic) {
        return '<div class="nav-section reports-section" id="reportsSection" style="display:none;"></div>';
    }

    var runs = reportIndex[state.selectedTopic] || {};
    var runIds = Object.keys(runs).sort();

    var html = '<div class="nav-section reports-section" id="reportsSection">';
    html += '<div class="nav-section-header">';
    html += 'Reports';
    html += '<span class="nav-section-count">' + runIds.length + '</span>';
    html += '</div>';
    html += '<div class="nav-list" id="reportsNav">';

    runIds.forEach(function(runId) {
        var isActive = state.selectedRun === runId;
        var isAnnotatedReport = isAnnotated(state.selectedTopic, runId);

        html += '<div class="nav-item' + (isActive ? ' active' : '') + '" data-run="' + escapeHtml(runId) + '">';
        html += '<span class="nav-item-status ' + (isAnnotatedReport ? 'checked' : 'unchecked') + '"></span>';
        html += '<span class="nav-item-label">' + escapeHtml(runId) + '</span>';
        html += '</div>';
    });

    html += '</div>';
    html += '</div>';

    return html;
}

// Attach click handlers to navigation items
function attachNavHandlers() {
    // Query items
    document.querySelectorAll('#queriesNav .nav-item').forEach(function(item) {
        item.addEventListener('click', function() {
            var topicId = item.dataset.topic;
            selectTopic(topicId);
        });
    });

    // Report items
    document.querySelectorAll('#reportsNav .nav-item').forEach(function(item) {
        item.addEventListener('click', function() {
            var runId = item.dataset.run;
            selectReport(runId);
        });
    });
}

// Select a topic
function selectTopic(topicId) {
    if (state.selectedTopic !== topicId) {
        pushNavHistory();
    }
    state.selectedTopic = topicId;
    state.selectedRun = null;

    // Auto-select first report if in Creation phase
    if (state.phase === 'creation') {
        var runs = reportIndex[topicId] || {};
        var runIds = Object.keys(runs).sort();
        if (runIds.length > 0) {
            state.selectedRun = runIds[0];
        }
    }

    renderAll();
    autoSave();
}

// Select a report (run)
function selectReport(runId) {
    if (state.selectedRun !== runId) {
        pushNavHistory();
    }
    state.selectedRun = runId;
    renderAll();
    autoSave();
}

// Update nav panel status indicators without full re-render
function updateNavCounts() {
    // Update query completion counts
    var countSpan = document.querySelector('.queries-section .nav-section-count');
    if (countSpan) {
        countSpan.textContent = getCompletedQueryCount() + '/' + topicIds.length;
    }

    // Update individual item statuses
    document.querySelectorAll('#queriesNav .nav-item').forEach(function(item) {
        var topicId = item.dataset.topic;
        var statusEl = item.querySelector('.nav-item-status');
        if (statusEl) {
            statusEl.classList.toggle('checked', isTopicComplete(topicId));
            statusEl.classList.toggle('unchecked', !isTopicComplete(topicId));
        }
    });

    document.querySelectorAll('#reportsNav .nav-item').forEach(function(item) {
        var runId = item.dataset.run;
        var statusEl = item.querySelector('.nav-item-status');
        if (statusEl && state.selectedTopic) {
            var annotated = isAnnotated(state.selectedTopic, runId);
            statusEl.classList.toggle('checked', annotated);
            statusEl.classList.toggle('unchecked', !annotated);
        }
    });
}

// Legacy alias for backwards compatibility
function updateSidebarCounts() {
    updateNavCounts();
}

// Legacy alias
function renderSidebar() {
    renderNavPanel();
}
"""
