"""JavaScript for the ranking panel (QC and Observe phases)."""

JS_RANKING = r"""
// ============================================================================
// Ranking Panel (QC and Observe Phases)
// ============================================================================

// Compute score for a single report based on enabled nuggets
function computeReportScore(topicId, runId) {
    var bank = DATA.nugget_banks && DATA.nugget_banks[topicId];
    if (!bank) return { score: 0, satisfied: 0, partial: 0, total: 0 };

    var nuggets = bank.nuggets || [];
    var totalWeight = 0;
    var earnedWeight = 0;
    var satisfied = 0;
    var partial = 0;
    var total = 0;

    nuggets.forEach(function(nugget) {
        var nuggetId = nugget.nugget_id;

        // Skip disabled nuggets
        if (state.enabledNuggets[nuggetId] === false) return;

        // Solo mode: only count the soloed nugget
        if (state.soloNuggetId && state.soloNuggetId !== nuggetId) return;

        var category = nugget.importance || 'should_have';
        var weight = 1.0;
        if (category === 'must_have') weight = state.nuggetWeights.must;
        else if (category === 'should_have') weight = state.nuggetWeights.should;
        else if (category === 'avoid') weight = state.nuggetWeights.avoid;

        totalWeight += Math.abs(weight);
        total++;

        // Get grade
        var grade = getReportGrade(topicId, runId, nuggetId);
        var gradeValue = grade ? grade.grade : 0;

        if (category === 'avoid') {
            // For avoid: lower grade is better
            if (gradeValue === 0) {
                earnedWeight += Math.abs(weight);
                satisfied++;
            } else if (gradeValue <= 2) {
                earnedWeight += Math.abs(weight) * 0.5;
                partial++;
            }
        } else {
            // For must/should: higher grade is better
            if (gradeValue >= 4) {
                earnedWeight += weight;
                satisfied++;
            } else if (gradeValue >= 1) {
                earnedWeight += weight * 0.5;
                partial++;
            }
        }
    });

    var score = totalWeight > 0 ? earnedWeight / totalWeight : 0;
    return { score: score, satisfied: satisfied, partial: partial, total: total };
}

// Rank all reports for a topic
function rankReports(topicId) {
    var runs = reportIndex[topicId] || {};
    var results = [];

    Object.keys(runs).forEach(function(runId) {
        var scoreInfo = computeReportScore(topicId, runId);
        results.push({
            runId: runId,
            score: scoreInfo.score,
            satisfied: scoreInfo.satisfied,
            partial: scoreInfo.partial,
            total: scoreInfo.total
        });
    });

    // Sort by score descending
    results.sort(function(a, b) { return b.score - a.score; });
    return results;
}

// Compute metrics for Observe mode
function computeMetrics(rankedReports) {
    if (!rankedReports || rankedReports.length === 0) {
        return { avg: 0, max: 0, fullCoverage: 0 };
    }

    var sum = 0;
    var max = 0;
    var fullCount = 0;

    rankedReports.forEach(function(r) {
        sum += r.score;
        if (r.score > max) max = r.score;
        if (r.satisfied === r.total && r.total > 0) fullCount++;
    });

    return {
        avg: sum / rankedReports.length,
        max: max,
        fullCoverage: Math.round(fullCount / rankedReports.length * 100)
    };
}

// Get summary text for a report
function getReportSummary(topicId, runId) {
    var scoreInfo = computeReportScore(topicId, runId);
    var summary = scoreInfo.satisfied + '/' + scoreInfo.total;
    if (scoreInfo.partial > 0) {
        summary += ' (+' + scoreInfo.partial + ' partial)';
    }
    return summary;
}

// Render the ranking panel
function renderRankingPanel() {
    if (!state.selectedTopic) {
        rankingList.innerHTML = '<div class="empty-state">Select a query from the navigation.</div>';
        return;
    }

    var ranked = rankReports(state.selectedTopic);

    // Update metrics bar (Observe mode only)
    if (state.phase === 'observe') {
        var metrics = computeMetrics(ranked);
        var metricsBar = document.getElementById('metricsBar');
        if (metricsBar) {
            metricsBar.innerHTML =
                '<div class="metric-item"><div class="metric-value">' + metrics.avg.toFixed(2) + '</div><div class="metric-label">Avg</div></div>' +
                '<div class="metric-item"><div class="metric-value">' + metrics.max.toFixed(2) + '</div><div class="metric-label">Max</div></div>' +
                '<div class="metric-item"><div class="metric-value">' + metrics.fullCoverage + '%</div><div class="metric-label">Full</div></div>';
        }
    }

    // Render ranking list
    var html = '';
    ranked.forEach(function(item, idx) {
        var isSelected = state.selectedRun === item.runId;
        html += '<div class="ranking-item' + (isSelected ? ' selected' : '') + '" data-run-id="' + escapeHtml(item.runId) + '">';
        html += '<span class="ranking-position">' + (idx + 1) + '.</span>';
        html += '<div class="ranking-info">';
        html += '<div class="ranking-name">' + escapeHtml(item.runId) + '</div>';
        html += '<div class="ranking-summary">' + item.satisfied + '/' + item.total;
        if (item.partial > 0) html += ' (+' + item.partial + ' partial)';
        html += '</div>';
        html += '</div>';
        html += '<span class="ranking-score">' + item.score.toFixed(2) + '</span>';
        html += '</div>';
    });

    rankingList.innerHTML = html;
    attachRankingHandlers();
}

// Attach click handlers to ranking items
function attachRankingHandlers() {
    document.querySelectorAll('.ranking-item').forEach(function(item) {
        item.addEventListener('click', function() {
            var runId = item.dataset.runId;
            selectReportFromRanking(runId);
        });
    });
}

// Re-render ranking when nugget state changes
function updateRanking() {
    if (state.phase === 'qc' || state.phase === 'observe') {
        renderRankingPanel();
    }
}
"""
