"""JavaScript for the nuggets panel (all phases)."""

JS_NUGGETS_PANEL = r"""
// ============================================================================
// Nuggets Panel
// ============================================================================

// Group nuggets by category
function groupNuggetsByCategory(nuggets) {
    var grouped = {
        must_have: [],
        should_have: [],
        avoid: []
    };

    nuggets.forEach(function(n) {
        var category = n.importance || n.quality || 'should_have';
        if (category === 'must_have' || category === 'must') {
            grouped.must_have.push(n);
        } else if (category === 'avoid') {
            grouped.avoid.push(n);
        } else {
            grouped.should_have.push(n);
        }
    });

    return grouped;
}

// Check if a nugget is effectively enabled (considering solo mode)
function isNuggetEffectivelyEnabled(nuggetId) {
    if (state.soloNuggetId) {
        return state.soloNuggetId === nuggetId;
    }
    return state.enabledNuggets[nuggetId] !== false;
}

// Count coverage stats for a nugget
function countNuggetCoverageStats(topicId, nuggetId, nugget) {
    var runs = reportIndex[topicId] || {};
    var runIds = Object.keys(runs);
    var satisfied = 0;
    var partial = 0;

    runIds.forEach(function(runId) {
        var grade = getReportGrade(topicId, runId, nuggetId);
        if (grade) {
            if (grade.grade >= 4) satisfied++;
            else if (grade.grade >= 1) partial++;
        }
    });

    return {
        reportsSatisfied: satisfied,
        reportsPartial: partial,
        reportsTotal: runIds.length
    };
}

// Convert grade to verdict display
function gradeToVerdict(grade) {
    if (grade === null || grade === undefined || typeof grade !== 'number') {
        return { cls: 'unknown', icon: '?', label: 'unknown' };
    }
    if (grade >= 4) {
        return { cls: 'satisfied', icon: '\u2713', label: 'satisfied' };
    } else if (grade >= 1) {
        return { cls: 'partial', icon: '~', label: 'partial' };
    } else {
        return { cls: 'not-satisfied', icon: '\u2717', label: 'not-satisfied' };
    }
}

// Build source description (R, R+docs, etc.)
function buildSourceDesc(grade, docGrades) {
    if (!grade) return '';
    var desc = 'R';
    var docCount = docGrades ? Object.keys(docGrades).length : 0;
    if (docCount > 0) {
        desc += '+' + docCount;
    }
    return desc;
}

// Render the nuggets panel
function renderNuggetsPanel() {
    if (!state.selectedTopic) {
        nuggetsPanel.innerHTML = '<div class="nuggets-header"><span class="nuggets-title">Nuggets</span></div><div class="empty-state">Select a query first.</div>';
        return;
    }

    var bank = DATA.nugget_banks && DATA.nugget_banks[state.selectedTopic];
    var nuggets = bank ? (bank.nuggets || []) : [];
    var claims = bank ? (bank.claims || []) : [];
    var allNuggets = nuggets.concat(claims);
    var isCreation = state.phase === 'creation';
    var isQC = state.phase === 'qc';
    var isObserve = state.phase === 'observe';

    var html = '';

    // Header
    html += '<div class="nuggets-header">';
    html += '<div>';
    html += '<span class="nuggets-title">Nuggets (' + allNuggets.length + ')</span>';
    if (isCreation && state.selectedRun) {
        html += '<span class="nuggets-context"> — ' + escapeHtml(state.selectedRun) + '</span>';
    }
    html += '</div>';
    if (!isObserve) {
        html += '<button class="new-nugget-btn" id="newNuggetBtn" onclick="showDraft()">+ Nugget</button>';
    }
    html += '</div>';

    // Solo mode bar
    if (state.soloNuggetId) {
        html += '<div class="solo-mode-bar visible">';
        html += '<span>Solo mode active</span>';
        html += '<button class="unsolo-btn" onclick="unsoloAll()">Unsolo</button>';
        html += '</div>';
    }

    html += '<div class="nuggets-list">';

    // Draft card placeholder (rendered separately)
    html += '<div id="draftCardContainer"></div>';

    // Group nuggets by category
    var grouped = groupNuggetsByCategory(allNuggets);

    // Must Have section
    if (grouped.must_have.length > 0 || isQC || isObserve) {
        html += renderCategorySection('must', 'Must Have', grouped.must_have);
    }

    // Should Have section
    if (grouped.should_have.length > 0 || isQC || isObserve) {
        html += renderCategorySection('should', 'Should Have', grouped.should_have);
    }

    // Avoid section
    if (grouped.avoid.length > 0 || isQC || isObserve) {
        html += renderCategorySection('avoid', 'Avoid', grouped.avoid);
    }

    html += '</div>';

    nuggetsPanel.innerHTML = html;
    attachNuggetsPanelHandlers();

    // Render draft card if visible
    if (state.draftState.visible) {
        renderDraftCard();
    }
}

// Render a category section
function renderCategorySection(categoryKey, categoryName, nuggets) {
    var isQC = state.phase === 'qc';
    var isObserve = state.phase === 'observe';
    var isCreation = state.phase === 'creation';

    var categoryClass = categoryKey;  // 'must', 'should', 'avoid'

    var html = '<div class="category-section">';

    // Category header with weight
    html += '<div class="category-header">';
    html += '<span class="category-name ' + categoryClass + '">' + categoryName + '</span>';
    html += '<span class="category-spacer"></span>';

    // Weight input (visible in QC and Observe)
    if (isQC || isObserve) {
        var weightKey = categoryKey === 'must' ? 'must' : (categoryKey === 'avoid' ? 'avoid' : 'should');
        var weight = state.nuggetWeights[weightKey];
        var min = categoryKey === 'avoid' ? '-10' : '0';
        var max = categoryKey === 'avoid' ? '0' : '10';

        html += '<div class="category-weight-group visible">';
        html += '<span class="category-weight-label">Weight:</span>';
        html += '<input type="number" class="category-weight" data-category="' + weightKey + '" ';
        html += 'value="' + weight + '" step="0.5" min="' + min + '" max="' + max + '"';
        if (isObserve) html += ' disabled style="opacity: 0.7;"';
        html += '>';
        html += '</div>';
    }

    html += '</div>';

    // Nugget rows
    html += '<div class="category-nuggets">';
    nuggets.forEach(function(n) {
        html += renderNuggetRow(n, categoryKey);
    });
    html += '</div>';

    html += '</div>';
    return html;
}

// Render a single nugget row
function renderNuggetRow(nugget, categoryKey) {
    var nuggetId = nugget.nugget_id;
    var isCreation = state.phase === 'creation';
    var isQC = state.phase === 'qc';
    var isObserve = state.phase === 'observe';

    var enabled = isNuggetEffectivelyEnabled(nuggetId);
    var soloed = state.soloNuggetId === nuggetId;

    var rowClass = 'nugget-row';
    if (!enabled && !soloed) rowClass += ' disabled';
    if (soloed) rowClass += ' soloed';

    var html = '<div class="' + rowClass + '" id="nugget-' + escapeHtml(nuggetId) + '">';

    // QC controls (solo + checkbox) - only in QC phase
    if (isQC) {
        html += '<div class="qc-controls visible">';
        html += '<button class="solo-btn' + (soloed ? ' active' : '') + '" data-nugget-id="' + escapeHtml(nuggetId) + '">&middot;</button>';
        html += '<input type="checkbox" class="nugget-checkbox" data-nugget-id="' + escapeHtml(nuggetId) + '"' + (enabled ? ' checked' : '') + '>';
        html += '</div>';
    }

    // Nugget content
    html += '<div class="nugget-content">';
    html += '<div class="nugget-text">' + escapeHtml(nugget.text || nugget.question || '') + '</div>';

    // Global info row
    html += '<div class="nugget-global">';

    // Coverage bar
    var stats = countNuggetCoverageStats(state.selectedTopic, nuggetId, nugget);
    var pct = stats.reportsTotal > 0 ? (stats.reportsSatisfied / stats.reportsTotal * 100) : 0;
    html += '<div class="coverage-bar-container">';
    html += '<div class="coverage-bar"><div class="coverage-bar-fill" style="width: ' + pct + '%"></div></div>';
    html += '<span class="coverage-label">' + stats.reportsSatisfied + '/' + stats.reportsTotal + '</span>';
    html += '</div>';

    // Edit button (not in Observe)
    if (!isObserve) {
        html += '<button class="edit-btn" data-nugget-id="' + escapeHtml(nuggetId) + '">Edit</button>';
    }

    // Report verdict (only in Creation with report selected)
    if (isCreation && state.selectedRun) {
        var grade = getReportGrade(state.selectedTopic, state.selectedRun, nuggetId);
        var verdict = grade ? gradeToVerdict(grade.grade) : gradeToVerdict(null);
        var source = grade ? buildSourceDesc(grade, null) : '';

        // Quote button states:
        // - No grade yet: "Find Quote" (triggers LLM)
        // - Grade exists, addressed_quote is null: "Find Quote" (not yet attempted)
        // - Grade exists, addressed_quote is "": "No Quote" (attempted, not found) - disabled
        // - Grade exists, addressed_quote has text: "Show Quote" / "Hide Quote" (toggle)
        var quoteState = 'find';  // default: can try to find
        var quoteLabel = 'Find Quote';
        var isActive = state.heavyHighlightNuggetId === nuggetId;

        if (grade) {
            if (grade.addressed_quote === '') {
                // Explicitly empty = attempted but not found
                quoteState = 'none';
                quoteLabel = 'No Quote';
            } else if (grade.addressed_quote) {
                // Has quote text
                quoteState = 'has';
                quoteLabel = isActive ? 'Hide Quote' : 'Show Quote';
            } else {
                // Debug: grade exists but addressed_quote is null (unexpected after Check Impact)
                console.warn('QUOTE MISSING: grade exists but addressed_quote is null', {
                    nuggetId: nuggetId,
                    runId: state.selectedRun,
                    grade: grade.grade,
                    addressedQuote: grade.addressed_quote
                });
            }
        }

        html += '<div class="nugget-report visible">';
        html += '<span class="verdict-icon ' + verdict.label + '">' + verdict.icon + '</span>';
        html += '<span class="verdict-source">' + source + '</span>';
        html += '<button class="quote-btn quote-' + quoteState + (isActive ? ' active' : '') + '" ';
        html += 'data-nugget-id="' + escapeHtml(nuggetId) + '" data-quote-state="' + quoteState + '">';
        html += quoteLabel + '</button>';
        html += '</div>';
    }

    html += '</div>';  // nugget-global
    html += '</div>';  // nugget-content
    html += '</div>';  // nugget-row

    return html;
}

// Attach handlers for nuggets panel
function attachNuggetsPanelHandlers() {
    // Solo buttons
    document.querySelectorAll('.solo-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var nuggetId = btn.dataset.nuggetId;
            toggleSolo(nuggetId);
        });
    });

    // Checkboxes
    document.querySelectorAll('.nugget-checkbox').forEach(function(cb) {
        cb.addEventListener('change', function() {
            var nuggetId = cb.dataset.nuggetId;
            toggleNuggetEnabled(nuggetId, cb.checked);
        });
    });

    // Weight inputs
    document.querySelectorAll('.category-weight').forEach(function(input) {
        input.addEventListener('change', function() {
            var category = input.dataset.category;
            var value = parseFloat(input.value) || 0;
            state.nuggetWeights[category] = value;
            updateRanking();
            autoSave();
        });
    });

    // Quote buttons
    document.querySelectorAll('.quote-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var nuggetId = btn.dataset.nuggetId;
            toggleQuoteHighlight(nuggetId);
        });
    });

    // Edit buttons
    document.querySelectorAll('.edit-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var nuggetId = btn.dataset.nuggetId;
            editNugget(nuggetId);
        });
    });
}

// Edit an existing nugget - opens draft card with nugget data pre-filled
function editNugget(nuggetId) {
    // Find the nugget in the bank
    var bank = DATA.nugget_banks && DATA.nugget_banks[state.selectedTopic];
    if (!bank) return;

    var allNuggets = (bank.nuggets || []).concat(bank.claims || []);
    var nugget = allNuggets.find(function(n) { return n.nugget_id === nuggetId; });
    if (!nugget) return;

    var nuggetText = nugget.text || nugget.question || '';

    // Initialize draft state with nugget data
    // originalNuggetId: ID in DATA.nugget_banks (for finding nugget to update on commit)
    // editingNuggetId: hash of current text (for looking up/storing grades)
    state.draftState = {
        visible: true,
        originalNuggetId: nuggetId,  // ID in DATA.nugget_banks
        editingNuggetId: hashNuggetText(nuggetText),  // Hash-based ID for grades
        spans: nugget.source_spans || [],
        freetext: nugget.source_freetext || '',
        nuggetText: nuggetText,
        category: nugget.importance || nugget.quality || 'should_have',
        canonicalized: true,  // Already has nugget text
        impactVisible: false,
        impactResults: []
    };

    renderDraftCard();
}

// Toggle solo mode for a nugget
function toggleSolo(nuggetId) {
    if (state.soloNuggetId === nuggetId) {
        // Exit solo mode
        state.soloNuggetId = null;
        // Restore previous enabled state if saved
        if (state.preSoloEnabledNuggets) {
            state.enabledNuggets = state.preSoloEnabledNuggets;
            state.preSoloEnabledNuggets = null;
        }
    } else {
        // Enter solo mode
        if (!state.preSoloEnabledNuggets) {
            state.preSoloEnabledNuggets = Object.assign({}, state.enabledNuggets);
        }
        state.soloNuggetId = nuggetId;
    }

    renderNuggetsPanel();
    updateRanking();
    autoSave();
}

// Exit solo mode
function unsoloAll() {
    state.soloNuggetId = null;
    if (state.preSoloEnabledNuggets) {
        state.enabledNuggets = state.preSoloEnabledNuggets;
        state.preSoloEnabledNuggets = null;
    }
    renderNuggetsPanel();
    updateRanking();
    autoSave();
}

// Toggle nugget enabled state
function toggleNuggetEnabled(nuggetId, enabled) {
    state.enabledNuggets[nuggetId] = enabled;

    // Update row visual
    var row = document.getElementById('nugget-' + nuggetId);
    if (row) {
        row.classList.toggle('disabled', !enabled);
    }

    updateRanking();
    autoSave();
}

// Handle quote button click based on state
function toggleQuoteHighlight(nuggetId) {
    var btn = document.querySelector('.quote-btn[data-nugget-id="' + nuggetId + '"]');
    if (!btn) return;

    var quoteState = btn.dataset.quoteState;

    if (quoteState === 'none') {
        // Disabled - do nothing
        return;
    }

    if (quoteState === 'find') {
        // Trigger LLM call to find quote
        findQuoteForNugget(nuggetId);
        return;
    }

    // quoteState === 'has' - toggle show/hide
    // Clear active state from ALL quote buttons first
    document.querySelectorAll('.quote-btn.active').forEach(function(b) {
        b.classList.remove('active');
        b.textContent = 'Show Quote';
    });

    // Toggle heavy highlight state
    if (state.heavyHighlightNuggetId === nuggetId) {
        // Clicking same button again - hide
        state.heavyHighlightNuggetId = null;
        btn.textContent = 'Show Quote';
    } else {
        // Show this quote
        state.heavyHighlightNuggetId = nuggetId;
        btn.classList.add('active');
        btn.textContent = 'Hide Quote';
    }

    // Re-render source to apply highlight
    if (state.phase === 'creation') {
        applyQuoteHighlights();

        // Try to scroll to the quote
        if (state.heavyHighlightNuggetId === nuggetId) {
            var highlighted = document.querySelector('.has-quote-highlight[data-highlight-nugget="' + nuggetId + '"]');
            if (highlighted) {
                highlighted.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                // Quote not found - show what the quote actually is
                var grade = typeof getReportGrade === 'function'
                    ? getReportGrade(state.selectedTopic, state.selectedRun, nuggetId)
                    : null;
                var quoteText = grade && grade.addressed_quote ? grade.addressed_quote : '(empty)';
                var truncated = quoteText.length > 80 ? quoteText.substring(0, 80) + '...' : quoteText;
                showToast('Quote not found: "' + truncated + '"');
                console.warn('Full quote that could not be matched:', quoteText);
                // Reset button state
                btn.classList.remove('active');
                btn.textContent = 'Show Quote';
                state.heavyHighlightNuggetId = null;
            }
        }
    }
}

// Find quote for a nugget using LLM
async function findQuoteForNugget(nuggetId) {
    var btn = document.querySelector('.quote-btn[data-nugget-id="' + nuggetId + '"]');
    if (!btn) return;

    // Check API key
    if (typeof getLlmApiKey === 'function' && !getLlmApiKey()) {
        showToast('Please set your OpenRouter API key first.');
        return;
    }

    // Get nugget text
    var bank = DATA.nugget_banks && DATA.nugget_banks[state.selectedTopic];
    var allNuggets = bank ? (bank.nuggets || []).concat(bank.claims || []) : [];
    var nugget = allNuggets.find(function(n) { return n.nugget_id === nuggetId; });
    if (!nugget) return;

    var nuggetText = nugget.text || nugget.question || '';
    if (!nuggetText) return;

    // Get report text - use sentence.text (matches rendered text) for quote extraction
    var report = reportIndex[state.selectedTopic] && reportIndex[state.selectedTopic][state.selectedRun];
    if (!report) return;

    var passage = '';
    if (report.sentences && report.sentences.length > 0) {
        passage = report.sentences.map(function(s) { return s.text || ''; }).join(' ');
    }
    if (!passage) passage = report.response_text || '';
    if (!passage) return;

    // Show loading state
    btn.textContent = 'Finding...';
    btn.classList.add('loading');

    try {
        // Split passage into chunks for long documents
        var chunks = typeof chunkPassage === 'function'
            ? chunkPassage(passage, 6000, 1000)
            : [{ text: passage.substring(0, 8000), startOffset: 0 }];

        var quote = '';
        var normalizeFunc = typeof normalizeForMatching === 'function' ? normalizeForMatching : function(t) {
            return t.replace(/\s+/g, ' ').toLowerCase();
        };

        // Try each chunk until we find a valid quote
        for (var ci = 0; ci < chunks.length && !quote; ci++) {
            var chunkText = chunks[ci].text;

            // Build quote extraction prompt
            var prompt = '## Question\n' + nuggetText + '\n\n';
            prompt += '## Passage\n' + chunkText + '\n\n';
            prompt += '## Task\n';
            prompt += 'Find a SINGLE CONTIGUOUS text span that best supports the answer to the question.\n\n';
            prompt += 'CRITICAL REQUIREMENTS:\n';
            prompt += '- The quote MUST be a single contiguous span\n';
            prompt += '- Do NOT combine sentences from different parts\n';
            prompt += '- Copy the text character-for-character from the passage\n';
            prompt += '- If no relevant quote exists, respond with {"extracted_quote": "", "confidence": 0.0}\n\n';
            prompt += 'Respond with JSON: {"extracted_quote": "the exact text", "confidence": 0.0-1.0}\n';
            prompt += 'Only respond with the JSON, no other text.';

            var result = await callLlm(prompt, 'Extract a contiguous verbatim quote from a passage that addresses a question.');

            if (result) {
                try {
                    var jsonStr = result.trim();
                    if (jsonStr.startsWith('```')) {
                        jsonStr = jsonStr.replace(/```json?\n?/g, '').replace(/```/g, '').trim();
                    }
                    var parsed = JSON.parse(jsonStr);
                    var candidateQuote = scrubQuote(parsed.extracted_quote || '');

                    // Validate quote exists in full passage (with Unicode normalization)
                    if (candidateQuote && candidateQuote.toLowerCase() !== 'none' && candidateQuote.toLowerCase() !== 'null') {
                        if (normalizeFunc(passage).includes(normalizeFunc(candidateQuote))) {
                            quote = candidateQuote;  // Found valid quote, will exit loop
                            console.log('Found quote in chunk ' + (ci + 1) + '/' + chunks.length);
                        } else {
                            console.warn('Quote from chunk ' + (ci + 1) + ' not found in full passage:', candidateQuote.substring(0, 100));
                        }
                    }
                } catch (e) {
                    console.error('Quote parse error in chunk ' + (ci + 1) + ':', e);
                }
            }
        }

        // Store the result (empty string means "attempted, not found")
        var existingGrade = typeof getReportGrade === 'function'
            ? getReportGrade(state.selectedTopic, state.selectedRun, nuggetId)
            : null;

        if (existingGrade) {
            existingGrade.addressed_quote = quote;
        } else {
            // Create a minimal grade entry just for the quote
            existingGrade = {
                grade: null,
                reasoning: '',
                addressed_quote: quote
            };
        }

        if (typeof storeUserGrade === 'function') {
            storeUserGrade(state.selectedTopic, state.selectedRun, nuggetId, existingGrade);
        }

        // Re-render to update button state
        renderNuggetsPanel();

        if (quote) {
            // Auto-show the quote
            state.heavyHighlightNuggetId = nuggetId;
            applyQuoteHighlights();
            scrollToQuoteInSource(nuggetId);
            showToast('Quote found and highlighted.');
        } else {
            showToast('No matching quote found in this report.');
        }

    } catch (err) {
        console.error('Find quote error:', err);
        showToast('Error finding quote. Please try again.');
        btn.textContent = 'Find Quote';
        btn.classList.remove('loading');
    }
}

// Scroll to highlighted quote in source panel
function scrollToQuoteInSource(nuggetId) {
    var sourceText = document.getElementById('sourceText');
    if (!sourceText) return;

    // Find the highlighted paragraph
    var highlighted = sourceText.querySelector('.has-quote-highlight[data-highlight-nugget="' + nuggetId + '"]');
    if (highlighted) {
        highlighted.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Show a temporary toast message
function showToast(message) {
    var existing = document.getElementById('toast-message');
    if (existing) existing.remove();

    var toast = document.createElement('div');
    toast.id = 'toast-message';
    toast.className = 'toast-message';
    toast.textContent = message;
    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(function() { toast.classList.add('visible'); }, 10);

    // Remove after 3 seconds
    setTimeout(function() {
        toast.classList.remove('visible');
        setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
}

"""
