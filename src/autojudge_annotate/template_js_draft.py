"""JavaScript for the draft card (new nugget creation workflow)."""

JS_DRAFT = r"""
// ============================================================================
// Draft Card (New Nugget Creation)
// ============================================================================

// Show the draft card
function showDraft() {
    state.draftState = {
        visible: true,
        spans: [],
        freetext: '',
        nuggetText: '',
        category: 'must_have',
        canonicalized: false,
        impactVisible: false,
        impactResults: []
    };
    renderDraftCard();
}

// Hide the draft card
function hideDraft() {
    state.draftState.visible = false;
    var container = document.getElementById('draftCardContainer');
    if (container) {
        container.innerHTML = '';
    }
}

// Render the draft card
function renderDraftCard() {
    var container = document.getElementById('draftCardContainer');
    if (!container) return;

    if (!state.draftState.visible) {
        container.innerHTML = '';
        return;
    }

    var ds = state.draftState;

    var html = '<div class="draft-card visible" id="draftCard">';

    // Header
    html += '<div class="draft-header">';
    html += '<span class="draft-title">New Nugget</span>';
    html += '<button class="draft-close" onclick="hideDraft()">&times;</button>';
    html += '</div>';

    // Step 1: Spans
    html += '<div class="draft-section">';
    html += '<div class="draft-label">1. Spans (select text in source)</div>';
    html += '<div class="draft-spans' + (ds.spans.length > 0 ? ' has-spans' : '') + '" id="draftSpans">';
    if (ds.spans.length === 0) {
        html += 'Select text from the report to add supporting quotes...';
    } else {
        ds.spans.forEach(function(span, idx) {
            var shortText = span.text.length > 40 ? span.text.substring(0, 40) + '...' : span.text;
            html += '<span class="span-chip">"' + escapeHtml(shortText) + '" ';
            html += '<span class="span-chip-remove" onclick="removeSpan(' + idx + ')">&times;</span></span>';
        });
    }
    html += '</div>';
    html += '</div>';

    // Freetext notes
    html += '<div class="draft-section">';
    html += '<div class="draft-label">Freetext Notes</div>';
    html += '<textarea class="draft-textarea draft-freetext" id="draftFreetext" ';
    html += 'placeholder="Notes about what this nugget should capture..." ';
    html += 'oninput="updateDraftFreetext(this.value)">' + escapeHtml(ds.freetext) + '</textarea>';
    html += '</div>';

    // Step 2: Canonicalize
    html += '<div class="draft-section">';
    html += '<div class="draft-label">2. Nugget Candidate</div>';
    html += '<div class="draft-canonicalize">';
    html += '<button class="canonicalize-btn progress-btn' + (ds.canonicalized ? ' done' : '') + '" ';
    html += 'id="canonicalizeBtn" onclick="canonicalize()">';
    html += '<span class="btn-text">' + (ds.canonicalized ? 'Re-canonicalize' : 'Canonicalize') + '</span>';
    html += '<span class="progress-indicator"></span>';
    html += '</button>';
    html += '<span class="canonicalize-hint">Generate nugget from spans + notes</span>';
    html += '</div>';
    html += '<textarea class="draft-textarea draft-nugget-text' + (ds.canonicalized ? ' populated' : '') + '" ';
    html += 'id="draftNuggetText" placeholder="Canonicalized nugget statement will appear here..." ';
    html += (ds.canonicalized ? '' : 'disabled ');
    html += 'oninput="updateDraftNuggetText(this.value)">' + escapeHtml(ds.nuggetText) + '</textarea>';
    html += '</div>';

    // Category selection
    html += '<div class="draft-section">';
    html += '<div class="draft-label">Category</div>';
    html += '<div class="draft-category">';
    html += '<button class="category-btn must' + (ds.category === 'must_have' ? ' active' : '') + '" ';
    html += 'onclick="setDraftCategory(\'must_have\')">Must Have</button>';
    html += '<button class="category-btn should' + (ds.category === 'should_have' ? ' active' : '') + '" ';
    html += 'onclick="setDraftCategory(\'should_have\')">Should Have</button>';
    html += '<button class="category-btn avoid' + (ds.category === 'avoid' ? ' active' : '') + '" ';
    html += 'onclick="setDraftCategory(\'avoid\')">Avoid</button>';
    html += '</div>';
    html += '</div>';

    // Impact preview - shows grades and quotes from LLM
    // Formatted as a section like "Category" or "2. Nugget Candidate"
    if (ds.impactVisible && ds.impactResults.length > 0) {
        // Count reports with positive grades
        var addressedCount = ds.impactResults.filter(function(r) { return r.grade >= 3; }).length;

        html += '<div class="draft-section">';
        html += '<div class="draft-label">3. Impact: ' + addressedCount + '/' + ds.impactResults.length + ' reports addressed</div>';
        html += '<div class="impact-quotes">';

        // Show all results with quotes prominently
        ds.impactResults.forEach(function(result, idx) {
            var isCurrent = result.runId === state.selectedRun;

            html += '<div class="impact-quote-item' + (isCurrent ? ' current' : '') + '" ';
            html += 'onclick="navigateToQuote(\'' + escapeHtml(result.runId) + '\')">';

            // Quote is the main content - show full text
            if (result.quote) {
                html += '<div class="impact-quote-text">"' + escapeHtml(result.quote) + '"</div>';
            } else if (result.reasoning) {
                html += '<div class="impact-quote-text impact-no-quote">' + escapeHtml(result.reasoning) + '</div>';
            }

            // System and grade as subtle metadata below
            html += '<div class="impact-meta">';
            html += '<span class="impact-meta-system">' + escapeHtml(result.runId);
            if (isCurrent) html += ' (current)';
            html += '</span>';
            html += '<span class="impact-meta-grade">grade ' + result.grade + '</span>';
            html += '</div>';

            html += '</div>';
        });

        html += '</div>';
        html += '</div>';
    }

    // Actions (directly in draft-card, not wrapped in draft-section)
    html += '<div class="draft-actions">';
    html += '<button class="cancel" onclick="hideDraft()">Cancel</button>';
    html += '<button class="impact progress-btn" id="impactBtn" onclick="checkImpact()"' + (ds.canonicalized ? '' : ' disabled') + '>';
    html += '<span class="btn-text">Check Impact</span>';
    html += '<span class="progress-indicator"></span>';
    html += '</button>';
    html += '<button class="commit" id="commitBtn" onclick="commitNugget()"' + (ds.canonicalized ? '' : ' disabled') + '>Commit</button>';
    html += '</div>';

    html += '</div>';

    container.innerHTML = html;
}

// Render just the spans area
function renderDraftSpans() {
    var spansEl = document.getElementById('draftSpans');
    if (!spansEl) return;

    var ds = state.draftState;
    if (ds.spans.length === 0) {
        spansEl.innerHTML = 'Select text from the report to add supporting quotes...';
        spansEl.classList.remove('has-spans');
    } else {
        var html = '';
        ds.spans.forEach(function(span, idx) {
            var shortText = span.text.length > 40 ? span.text.substring(0, 40) + '...' : span.text;
            html += '<span class="span-chip">"' + escapeHtml(shortText) + '" ';
            html += '<span class="span-chip-remove" onclick="removeSpan(' + idx + ')">&times;</span></span>';
        });
        spansEl.innerHTML = html;
        spansEl.classList.add('has-spans');
    }
}

// Remove a span from draft
function removeSpan(idx) {
    state.draftState.spans.splice(idx, 1);
    renderDraftSpans();
}

// Update freetext
function updateDraftFreetext(value) {
    state.draftState.freetext = value;
}

// Update nugget text
function updateDraftNuggetText(value) {
    state.draftState.nuggetText = value;
}

// Set draft category
function setDraftCategory(category) {
    state.draftState.category = category;
    document.querySelectorAll('.draft-category .category-btn').forEach(function(btn) {
        btn.classList.remove('active');
    });
    var activeBtn = document.querySelector('.draft-category .category-btn.' +
        (category === 'must_have' ? 'must' : (category === 'avoid' ? 'avoid' : 'should')));
    if (activeBtn) activeBtn.classList.add('active');
}

// Canonicalize: generate nugget from spans + freetext via LLM
// Uses the same prompt structure as canonicalizeClue from template_js_llm.py
async function canonicalize() {
    var ds = state.draftState;
    var canonBtn = document.getElementById('canonicalizeBtn');

    // Collect input
    var spanTexts = ds.spans.map(function(s) { return s.text; });
    var freetext = ds.freetext.trim();

    if (spanTexts.length === 0 && !freetext) {
        alert('Please add spans or notes to generate a nugget candidate.');
        return;
    }

    // Start progress
    if (typeof startProgressOperation === 'function') {
        startProgressOperation(canonBtn, 1);
    } else {
        canonBtn.classList.add('loading');
    }

    // Build query context
    var request = requestMap[state.selectedTopic];
    var queryContext = '';
    if (request) {
        if (request.title) queryContext += 'Title: ' + request.title + '\n';
        if (request.problem_statement) queryContext += 'Problem Statement: ' + request.problem_statement + '\n';
        if (request.background) queryContext += 'User Background: ' + request.background + '\n';
        if (request.query) queryContext += 'Query: ' + request.query + '\n';
        if (request.question) queryContext += 'Question: ' + request.question + '\n';
    }
    if (!queryContext) queryContext = 'Topic ID: ' + state.selectedTopic + '\n';

    // System prompt for nugget generation
    var systemPrompt = 'You are helping create evaluation criteria as open-ended question nuggets for RAG system responses. ' +
        'Generate brief, atomic questions that target query-essential information which a good response should answer well. ' +
        'Focus on relevance, correctness, and completeness. ' +
        'Avoid generic quality questions. Make questions self-contained (e.g., "What is the capital of France?" not "The capital?").';

    // Build user prompt
    var prompt = '## Query Context\n' + queryContext + '\n';
    prompt += '## Annotator\'s Clue\n';
    prompt += 'Clue type: ' + ds.category + '\n';

    if (ds.category === 'must_have') {
        prompt += '(This is essential information a good response MUST address)\n\n';
    } else if (ds.category === 'should_have') {
        prompt += '(This is helpful information a good response SHOULD include)\n\n';
    } else if (ds.category === 'avoid') {
        prompt += '(This is unhelpful information a good response MUST AVOID! If addressed, the response will be penalized.)\n\n';
    }

    if (spanTexts.length > 0) {
        prompt += 'Selected text spans from the response:\n';
        spanTexts.forEach(function(sp) {
            prompt += '- "' + sp + '"\n';
        });
        prompt += '\n';
    }

    if (freetext) {
        prompt += 'Annotator\'s comment: ' + freetext + '\n\n';
    }

    prompt += '## Task\n';
    if (ds.category === 'avoid') {
        prompt += 'Based on the query context and annotator\'s clue, create a brief, atomic question that:\n';
        prompt += '- Does not target query-essential information\n';
        prompt += '- An excellent RAG response would not address\n';
        prompt += '- Focuses on one fact\n';
        prompt += '- Is self-contained (can be understood without additional context)\n\n';
    } else {
        prompt += 'Based on the query context and annotator\'s clue, create a brief, atomic question that:\n';
        prompt += '- Targets query-essential information\n';
        prompt += '- A good RAG response should answer well\n';
        prompt += '- Focuses on one fact\n';
        prompt += '- Is self-contained (can be understood without additional context)\n\n';
    }

    prompt += 'Respond with JSON in this exact format:\n';
    prompt += '{\n';
    prompt += '  "nugget_question": "A clear, self-contained question",\n';
    prompt += '  "nugget_type": "' + ds.category + '",\n';
    prompt += '  "explanation": "Brief explanation of why this question matters"\n';
    prompt += '}\n\n';
    prompt += 'Only respond with the JSON, no other text.';

    // Call LLM
    if (typeof callLlm === 'function') {
        try {
            var result = await callLlm(prompt, systemPrompt);
            if (result) {
                // Parse JSON response
                var jsonStr = result.trim();
                if (jsonStr.startsWith('```')) {
                    jsonStr = jsonStr.replace(/```json?\n?/g, '').replace(/```/g, '').trim();
                }
                if (jsonStr.startsWith('{') && !jsonStr.endsWith('}')) {
                    jsonStr = jsonStr + '}';
                }
                var parsed = JSON.parse(jsonStr);
                ds.nuggetText = parsed.nugget_question || parsed.nugget_text || '';
                ds.explanation = parsed.explanation || '';
            } else {
                // Fallback if LLM returns null
                ds.nuggetText = freetext || ('Does the response address: ' + spanTexts.join(' ').substring(0, 100) + '?');
            }
            ds.canonicalized = true;
        } catch (err) {
            console.error('Canonicalize error:', err);
            // Fallback on error
            ds.nuggetText = freetext || ('Does the response address: ' + spanTexts.join(' ').substring(0, 100) + '?');
            ds.canonicalized = true;
        }
    } else {
        // No LLM available, use fallback
        ds.nuggetText = freetext ? ('Does the response ' + freetext.toLowerCase() + '?') :
                        ('Does the response mention: ' + spanTexts.join(' ').substring(0, 100) + '?');
        ds.canonicalized = true;
    }

    if (typeof endProgressOperation === 'function') {
        endProgressOperation();
    } else {
        canonBtn.classList.remove('loading');
    }
    renderDraftCard();
}

// Check impact: grade nugget against all reports and extract quotes
// Uses concurrent LLM calls with progress bar
async function checkImpact() {
    var ds = state.draftState;

    // Read current value from textarea (in case user edited without losing focus)
    var nuggetTextarea = document.getElementById('draftNuggetText');
    if (nuggetTextarea) {
        ds.nuggetText = nuggetTextarea.value.trim();
    }

    if (!ds.nuggetText) {
        alert('Please enter or generate a nugget text first.');
        return;
    }

    // Check API key first
    if (typeof getLlmApiKey === 'function' && !getLlmApiKey()) {
        alert('Please set your OpenRouter API key first (click LLM indicator in top bar).');
        return;
    }

    var impactBtn = document.getElementById('impactBtn');
    var runs = reportIndex[state.selectedTopic] || {};
    var runIds = Object.keys(runs);

    if (runIds.length === 0) {
        alert('No reports found for this topic.');
        return;
    }

    // Start progress - each report needs grade + possibly quote extraction
    if (typeof startProgressOperation === 'function') {
        startProgressOperation(impactBtn, runIds.length);
    } else {
        impactBtn.classList.add('loading');
    }

    var results = [];
    var isAvoidNugget = ds.category === 'avoid';

    // When editing an existing nugget, check for existing grades
    var editingNuggetId = ds.editingNuggetId;

    // Separate reports into those with existing grades and those needing LLM calls
    var reportsNeedingGrade = [];
    runIds.forEach(function(runId) {
        if (editingNuggetId && typeof getReportGrade === 'function') {
            var existingGrade = getReportGrade(state.selectedTopic, runId, editingNuggetId);
            if (existingGrade && typeof existingGrade.grade === 'number') {
                // Use existing grade
                results.push({
                    runId: runId,
                    grade: existingGrade.grade,
                    reasoning: existingGrade.reasoning || '',
                    confidence: existingGrade.confidence || 0.5,
                    quote: existingGrade.addressed_quote || null,
                    fromCache: true
                });
                return;
            }
        }
        reportsNeedingGrade.push(runId);
    });

    // Adjust progress count for only reports needing LLM calls
    if (reportsNeedingGrade.length < runIds.length) {
        console.log('Reusing ' + (runIds.length - reportsNeedingGrade.length) + ' existing grades');
    }

    // Update progress to reflect actual work needed
    if (reportsNeedingGrade.length === 0) {
        // All grades exist, no LLM calls needed
        if (typeof endProgressOperation === 'function') {
            endProgressOperation();
        } else {
            impactBtn.classList.remove('loading');
        }
        results.sort(function(a, b) { return b.grade - a.grade; });
        ds.impactResults = results;
        ds.impactVisible = true;
        renderDraftCard();
        return;
    }

    // Re-initialize progress for only the reports needing grades
    if (typeof startProgressOperation === 'function') {
        startProgressOperation(impactBtn, reportsNeedingGrade.length);
    }

    // Build grading system prompt
    var gradeSystemPrompt = 'Grade how well a passage answers a specific question.\n\n' +
        'Can the question be answered based on the available context? Choose one:\n' +
        '- 5: The answer is highly relevant, complete, and accurate.\n' +
        '- 4: The answer is mostly relevant and complete but may have minor gaps or inaccuracies.\n' +
        '- 3: The answer is partially relevant and complete, with noticeable gaps or inaccuracies.\n' +
        '- 2: The answer has limited relevance and completeness, with significant gaps or inaccuracies.\n' +
        '- 1: The answer is minimally relevant or complete, with substantial shortcomings.\n' +
        '- 0: The answer is not relevant or complete at all.';

    // Queue all grading tasks concurrently (only for reports needing grades)
    var gradePromises = reportsNeedingGrade.map(function(runId) {
        return (typeof queueLlmTask === 'function' ? queueLlmTask : function(fn) { return fn(); })(async function() {
            var report = runs[runId];
            // Use sentence.text (matches rendered text) for quote extraction
            var passage = '';
            if (report.sentences && report.sentences.length > 0) {
                passage = report.sentences.map(function(s) { return s.text || ''; }).join(' ');
            }
            if (!passage) passage = report.response_text || '';

            if (!passage) {
                if (typeof incrementProgress === 'function') incrementProgress();
                return null;
            }

            // Build grading prompt
            var prompt;
            if (isAvoidNugget) {
                prompt = '## Anti-Nugget (content to avoid)\n' + ds.nuggetText + '\n\n';
                prompt += '## Passage to evaluate\n' + passage.substring(0, 8000) + '\n\n';
                prompt += '## Task\n';
                prompt += 'Check if the passage contains the problematic content described in the anti-nugget.\n';
                prompt += 'Grade 0 = content is NOT present (good), Grade 5 = content IS clearly present (bad).\n\n';
            } else {
                prompt = '## Question\n' + ds.nuggetText + '\n\n';
                prompt += '## Passage\n' + passage.substring(0, 8000) + '\n\n';
                prompt += '## Task\n';
                prompt += 'Grade how well the passage answers the question.\n\n';
            }

            prompt += 'Respond with JSON in this exact format:\n';
            prompt += '{\n';
            prompt += '  "grade": "0-5",\n';
            prompt += '  "reasoning": "Brief explanation of the grade",\n';
            prompt += '  "confidence": 0.0-1.0\n';
            prompt += '}\n\n';
            prompt += 'Only respond with the JSON, no other text.';

            try {
                var result = await callLlm(prompt, gradeSystemPrompt);
                if (!result) {
                    if (typeof incrementProgress === 'function') incrementProgress();
                    return null;
                }

                var jsonStr = result.trim();
                if (jsonStr.startsWith('```')) {
                    jsonStr = jsonStr.replace(/```json?\n?/g, '').replace(/```/g, '').trim();
                }
                var parsed = JSON.parse(jsonStr);
                var grade = parseInt(parsed.grade, 10);
                if (isNaN(grade) || grade < 0 || grade > 5) grade = 0;

                var impactResult = {
                    runId: runId,
                    grade: grade,
                    reasoning: parsed.reasoning || '',
                    confidence: parseFloat(parsed.confidence) || 0.5,
                    quote: null
                };

                // For high grades, extract quote (with chunking for long passages)
                if (grade >= 3) {
                    var chunks = typeof chunkPassage === 'function' ? chunkPassage(passage) : [{ text: passage.substring(0, 8000), startOffset: 0 }];

                    // Try each chunk until we find a quote
                    for (var ci = 0; ci < chunks.length && !impactResult.quote; ci++) {
                        var chunk = chunks[ci];
                        var quotePrompt = '## Question\n' + ds.nuggetText + '\n\n';
                        quotePrompt += '## Passage\n' + chunk.text + '\n\n';
                        quotePrompt += '## Task\n';
                        quotePrompt += 'Find a SINGLE CONTIGUOUS text span that best supports the answer to the question.\n\n';
                        quotePrompt += 'CRITICAL REQUIREMENTS:\n';
                        quotePrompt += '- The quote MUST be a single contiguous span\n';
                        quotePrompt += '- Do NOT combine sentences from different parts\n';
                        quotePrompt += '- Copy the text character-for-character from the passage\n\n';
                        quotePrompt += 'Respond with JSON: {"extracted_quote": "the exact text", "confidence": 0.0-1.0}\n';
                        quotePrompt += 'Only respond with the JSON, no other text.';

                        var quoteResult = await callLlm(quotePrompt, 'Extract a contiguous verbatim quote from a passage that addresses a question.');
                        if (quoteResult) {
                            try {
                                var qJsonStr = quoteResult.trim();
                                if (qJsonStr.startsWith('```')) {
                                    qJsonStr = qJsonStr.replace(/```json?\n?/g, '').replace(/```/g, '').trim();
                                }
                                var qParsed = JSON.parse(qJsonStr);
                                var quote = qParsed.extracted_quote;
                                if (quote && quote.toLowerCase() !== 'none' && quote.toLowerCase() !== 'null') {
                                    // Scrub the quote to clean up LLM formatting
                                    quote = typeof scrubQuote === 'function' ? scrubQuote(quote) : quote.trim();
                                    // Validate quote exists in full passage (with Unicode normalization)
                                    var normalizeFunc = typeof normalizeForMatching === 'function' ? normalizeForMatching : function(t) {
                                        return t.replace(/\s+/g, ' ').toLowerCase();
                                    };
                                    if (normalizeFunc(passage).includes(normalizeFunc(quote))) {
                                        impactResult.quote = quote;
                                        // Stop at first found
                                        break;
                                    }
                                }
                            } catch (qErr) {
                                console.warn('Quote extraction parse error:', qErr);
                            }
                        }
                    }
                }

                results.push(impactResult);
                if (typeof incrementProgress === 'function') incrementProgress();
                return impactResult;

            } catch (err) {
                console.error('Grade error for', runId, err);
                if (typeof incrementProgress === 'function') incrementProgress();
                return null;
            }
        });
    });

    // Wait for all grades to complete
    await Promise.all(gradePromises);

    // Sort by grade descending
    results.sort(function(a, b) { return b.grade - a.grade; });

    ds.impactResults = results;
    ds.impactVisible = true;

    if (typeof endProgressOperation === 'function') {
        endProgressOperation();
    } else {
        impactBtn.classList.remove('loading');
    }

    renderDraftCard();
}

// Commit the nugget to the bank
function commitNugget() {
    var ds = state.draftState;

    // Read current values from textareas (in case user edited without losing focus)
    var nuggetTextarea = document.getElementById('draftNuggetText');
    if (nuggetTextarea) {
        ds.nuggetText = nuggetTextarea.value.trim();
    }
    var freetextArea = document.getElementById('draftFreetext');
    if (freetextArea) {
        ds.freetext = freetextArea.value.trim();
    }

    if (!ds.nuggetText) {
        alert('Please canonicalize the nugget first.');
        return;
    }

    var nuggetId;
    var isEditing = ds.editingNuggetId;

    if (isEditing) {
        // Editing existing nugget
        nuggetId = ds.editingNuggetId;
        var bank = DATA.nugget_banks && DATA.nugget_banks[state.selectedTopic];
        if (bank) {
            // Find and update the existing nugget
            var allNuggets = bank.nuggets || [];
            for (var i = 0; i < allNuggets.length; i++) {
                if (allNuggets[i].nugget_id === nuggetId) {
                    allNuggets[i].text = ds.nuggetText;
                    allNuggets[i].question = ds.nuggetText;
                    allNuggets[i].importance = ds.category;
                    allNuggets[i].quality = ds.category;
                    allNuggets[i].source_spans = ds.spans;
                    allNuggets[i].source_freetext = ds.freetext;
                    allNuggets[i].updated_at = new Date().toISOString();
                    allNuggets[i].updated_by = usernameInput.value.trim() || 'anonymous';
                    break;
                }
            }
        }
    } else {
        // Creating new nugget
        nuggetId = 'user-' + Date.now() + '-' + Math.random().toString(36).substring(2, 8);

        // Create nugget object
        var newNugget = {
            nugget_id: nuggetId,
            text: ds.nuggetText,
            question: ds.nuggetText,  // Compatibility
            importance: ds.category,
            quality: ds.category,  // Compatibility
            created_by: usernameInput.value.trim() || 'anonymous',
            created_at: new Date().toISOString(),
            source_spans: ds.spans,
            source_freetext: ds.freetext
        };

        // Add to local nugget bank
        if (!DATA.nugget_banks) DATA.nugget_banks = {};
        if (!DATA.nugget_banks[state.selectedTopic]) {
            DATA.nugget_banks[state.selectedTopic] = { nuggets: [], claims: [] };
        }
        DATA.nugget_banks[state.selectedTopic].nuggets.push(newNugget);

        // Enable by default
        state.enabledNuggets[nuggetId] = true;
    }

    // Save impact grades from the impact check (so we don't re-grade later)
    if (ds.impactResults && ds.impactResults.length > 0 && typeof storeUserGrade === 'function') {
        ds.impactResults.forEach(function(result) {
            if (result && result.runId && typeof result.grade === 'number') {
                storeUserGrade(state.selectedTopic, result.runId, nuggetId, {
                    grade: result.grade,
                    reasoning: result.reasoning || '',
                    addressed_quote: result.quote || ''
                });
            }
        });
    }

    // Hide draft and re-render
    hideDraft();
    renderNuggetsPanel();
    updateNavCounts();
    autoSave();

    // Show confirmation
    console.log('Nugget ' + (isEditing ? 'updated' : 'committed') + ':', nuggetId);
}
"""
