"""JavaScript for the ranking panel (QC and Observe phases)."""

JS_RANKING = r"""
// ============================================================================
// Ranking Panel (QC and Observe Phases)
// ============================================================================

// Compute score for a single report based on enabled nuggets (legacy, used by QC)
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

// ============================================================================
// Multi-Metric Scoring (Observe Mode)
// ============================================================================

// Compute detailed metrics for a single report
// Returns: { avg, max, percent, score }
function computeDetailedMetrics(topicId, runId) {
    var bank = DATA.nugget_banks && DATA.nugget_banks[topicId];
    if (!bank) return { avg: 0, max: 0, percent: 0, score: 0, total: 0 };

    var nuggets = bank.nuggets || [];
    var grades = [];
    var mustShouldTotal = 0;
    var mustShouldCovered = 0;
    var weightedScore = 0;
    var totalWeight = 0;

    nuggets.forEach(function(nugget) {
        var nuggetId = nugget.nugget_id;

        // Skip disabled nuggets
        if (state.enabledNuggets[nuggetId] === false) return;

        // Solo mode: only count the soloed nugget
        if (state.soloNuggetId && state.soloNuggetId !== nuggetId) return;

        var importance = nugget.importance || 'should_have';
        var weight = 1.0;
        if (importance === 'must_have') weight = state.nuggetWeights.must;
        else if (importance === 'should_have') weight = state.nuggetWeights.should;
        else if (importance === 'avoid') weight = state.nuggetWeights.avoid;

        var grade = getReportGrade(topicId, runId, nuggetId);
        var g = grade ? grade.grade : 0;
        grades.push(g);

        // Percent: count must/should covered at grade >= 4
        if (importance !== 'avoid') {
            mustShouldTotal++;
            if (g >= 4) mustShouldCovered++;
        }

        // Weighted score
        if (importance === 'avoid') {
            // 0 = good (full weight), 5 = bad (no weight)
            weightedScore += Math.abs(weight) * (g === 0 ? 1 : g <= 2 ? 0.5 : 0);
        } else {
            weightedScore += weight * (g >= 4 ? 1 : g >= 1 ? 0.5 : 0);
        }
        totalWeight += Math.abs(weight);
    });

    return {
        avg: grades.length ? grades.reduce(function(a, b) { return a + b; }, 0) / grades.length : 0,
        max: grades.length ? Math.max.apply(null, grades) : 0,
        percent: mustShouldTotal ? (mustShouldCovered / mustShouldTotal * 100) : 0,
        score: totalWeight ? (weightedScore / totalWeight) : 0,
        total: grades.length
    };
}

// Helper: compute mean of an array
function mean(arr) {
    if (!arr || arr.length === 0) return 0;
    return arr.reduce(function(a, b) { return a + b; }, 0) / arr.length;
}

// Compute macro-averaged metrics across all topics for a run
function computeMacroAveragedMetrics(runId) {
    var perTopicMetrics = [];

    topicIds.forEach(function(topicId) {
        // Skip topics where this run has no report
        if (!reportIndex[topicId] || !reportIndex[topicId][runId]) return;
        perTopicMetrics.push(computeDetailedMetrics(topicId, runId));
    });

    if (perTopicMetrics.length === 0) return null;

    // Macro-average each metric
    return {
        avg: mean(perTopicMetrics.map(function(m) { return m.avg; })),
        max: mean(perTopicMetrics.map(function(m) { return m.max; })),
        percent: mean(perTopicMetrics.map(function(m) { return m.percent; })),
        score: mean(perTopicMetrics.map(function(m) { return m.score; })),
        topicCount: perTopicMetrics.length,
        total: perTopicMetrics.reduce(function(sum, m) { return sum + m.total; }, 0)
    };
}

// Get all unique run IDs across all topics
function getAllRunIds() {
    var runIds = {};
    topicIds.forEach(function(topicId) {
        var runs = reportIndex[topicId] || {};
        Object.keys(runs).forEach(function(runId) {
            runIds[runId] = true;
        });
    });
    return Object.keys(runIds);
}

// Compute aggregated ranking across all topics (for "All Queries" mode)
function computeAggregatedRanking() {
    var allRunIds = getAllRunIds();
    var results = [];

    allRunIds.forEach(function(runId) {
        var metrics = computeMacroAveragedMetrics(runId);
        if (metrics) {
            results.push({
                runId: runId,
                avg: metrics.avg,
                max: metrics.max,
                percent: metrics.percent,
                score: metrics.score,
                topicCount: metrics.topicCount,
                total: metrics.total,
                // Legacy fields for compatibility
                satisfied: Math.round(metrics.percent / 100 * metrics.total),
                partial: 0
            });
        }
    });

    // Sort by score descending
    results.sort(function(a, b) { return b.score - a.score; });
    return results;
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
    var isObserve = state.phase === 'observe';
    var isQC = state.phase === 'qc';
    var isAllQueries = state.rankingScope === 'all' && isObserve;

    // Render controls (toggle in Observe, nothing in QC)
    renderRankingControls();

    // Hide metricsBar (we put header in the table now)
    var metricsBar = document.getElementById('metricsBar');
    if (metricsBar) metricsBar.style.display = 'none';

    // For "All Queries" mode, we don't need a selected topic
    if (!isAllQueries && !state.selectedTopic) {
        rankingList.innerHTML = '<div class="empty-state">Select a query from the navigation.</div>';
        return;
    }

    // Get ranked reports based on mode
    var ranked;
    if (isAllQueries) {
        ranked = computeAggregatedRanking();
    } else {
        // Single topic mode - use detailed metrics for both QC and Observe
        ranked = rankReportsWithMetrics(state.selectedTopic);
    }

    // Build table with header row included for proper alignment
    var html = '<div class="ranking-table">';

    // Header row
    html += '<div class="ranking-header-row">';
    html += '<span class="col-rank">#</span>';
    html += '<span class="col-name">System</span>';
    html += '<span class="col-count">Nug</span>';
    html += '<span class="col-avg">Avg</span>';
    html += '<span class="col-cov">Cov</span>';
    html += '<span class="col-score">Score</span>';
    if (isAllQueries) {
        html += '<span class="col-topics">Qry</span>';
    }
    html += '</div>';

    // Data rows
    ranked.forEach(function(item, idx) {
        var isSelected = state.selectedRun === item.runId;
        html += '<div class="ranking-row' + (isSelected ? ' selected' : '') + '" data-run-id="' + escapeHtml(item.runId) + '">';

        // Rank
        html += '<span class="col-rank">' + (idx + 1) + '</span>';

        // System name
        html += '<span class="col-name" title="' + escapeHtml(item.runId) + '">' + escapeHtml(truncateName(item.runId, 14)) + '</span>';

        // Nugget counts (X/Y)
        var countStr = item.satisfied + '/' + item.total;
        html += '<span class="col-count" title="Satisfied/Total">' + countStr + '</span>';

        // Avg grade
        var avgVal = (item.avg !== undefined) ? item.avg.toFixed(1) : '-';
        html += '<span class="col-avg" title="Average grade">' + avgVal + '</span>';

        // Coverage %
        var covVal = (item.percent !== undefined) ? Math.round(item.percent) + '%' : '-';
        html += '<span class="col-cov" title="Coverage at grade 4+">' + covVal + '</span>';

        // Score
        html += '<span class="col-score" title="Weighted score">' + item.score.toFixed(2) + '</span>';

        // Topics (only in All Queries mode)
        if (isAllQueries) {
            html += '<span class="col-topics" title="Number of queries">' + (item.topicCount || '-') + '</span>';
        }

        html += '</div>';
    });
    html += '</div>';

    rankingList.innerHTML = html;
    attachRankingHandlers();
}

// Truncate name for display
function truncateName(name, maxLen) {
    if (!name) return '';
    if (name.length <= maxLen) return name;
    return name.substring(0, maxLen - 1) + '…';
}

// Render controls based on phase
function renderRankingControls() {
    var controlsEl = document.getElementById('rankingControls');
    if (!controlsEl) return;

    var isObserve = state.phase === 'observe';

    if (!isObserve) {
        // QC phase: no controls, single query is implied
        controlsEl.innerHTML = '';
        return;
    }

    // Observe phase: simple "All Queries" toggle button
    var isAll = state.rankingScope === 'all';
    var html = '<button class="all-queries-toggle' + (isAll ? ' active' : '') + '" onclick="toggleAllQueries()">';
    html += isAll ? 'All Queries' : 'This Query';
    html += '</button>';
    controlsEl.innerHTML = html;
}

// Toggle between all queries and current query
function toggleAllQueries() {
    if (state.rankingScope === 'all') {
        state.rankingScope = 'single';
        // Keep selectedTopic as-is (from nav selection)
    } else {
        state.rankingScope = 'all';
    }
    renderRankingPanel();
    renderNuggetsPanel();  // Update overview panel
}

// Rank reports for a single topic with detailed metrics (Observe mode)
function rankReportsWithMetrics(topicId) {
    var runs = reportIndex[topicId] || {};
    var results = [];

    Object.keys(runs).forEach(function(runId) {
        var metrics = computeDetailedMetrics(topicId, runId);
        results.push({
            runId: runId,
            avg: metrics.avg,
            max: metrics.max,
            percent: metrics.percent,
            score: metrics.score,
            total: metrics.total,
            satisfied: Math.round(metrics.percent / 100 * metrics.total),
            partial: 0
        });
    });

    // Sort by score descending
    results.sort(function(a, b) { return b.score - a.score; });
    return results;
}

// Attach click handlers to ranking items
function attachRankingHandlers() {
    document.querySelectorAll('.ranking-row').forEach(function(item) {
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
