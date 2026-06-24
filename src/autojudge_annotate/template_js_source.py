"""JavaScript for the source panel (report text view in Creation phase)."""

JS_SOURCE = r"""
// ============================================================================
// Source Panel (Creation Phase)
// ============================================================================

// Render the source panel with query and report text
function renderSourcePanel() {
    if (!state.selectedTopic) {
        sourceContent.innerHTML = '<div class="empty-state">Select a query from the navigation to begin.</div>';
        document.getElementById('sourceTitle').textContent = 'Select a report';
        document.getElementById('sourceSubtitle').textContent = '';
        return;
    }

    if (!state.selectedRun) {
        sourceContent.innerHTML = '<div class="empty-state">Select a report from the navigation.</div>';
        document.getElementById('sourceTitle').textContent = 'Select a report';
        document.getElementById('sourceSubtitle').textContent = 'Query: ' + state.selectedTopic;
        return;
    }

    var request = requestMap[state.selectedTopic];
    var report = reportIndex[state.selectedTopic] && reportIndex[state.selectedTopic][state.selectedRun];

    if (!report) {
        sourceContent.innerHTML = '<div class="empty-state">Report not found.</div>';
        return;
    }

    // Update header
    document.getElementById('sourceTitle').textContent = report.run_id || state.selectedRun;
    document.getElementById('sourceSubtitle').textContent = 'Response for ' + state.selectedTopic;

    // Build content
    var html = '';

    // Query box with full details (title, problem_statement, background)
    html += '<div class="query-box" id="queryBox">';
    html += '<div class="query-box-label">Query</div>';
    html += '<div class="query-box-content">';

    if (request) {
        // Title/query line
        var title = request.title || request.query || '';
        if (title) {
            html += '<div class="query-title">' + escapeHtml(title) + '</div>';
        }

        // Problem statement (if different from title)
        var problemStatement = request.problem_statement || '';
        if (problemStatement && problemStatement !== title) {
            html += '<div class="query-section">';
            html += '<div class="query-section-label">Problem Statement</div>';
            html += '<div class="query-section-text">' + escapeHtml(problemStatement) + '</div>';
            html += '</div>';
        }

        // Background (if available)
        var background = request.background || '';
        if (background) {
            html += '<div class="query-section">';
            html += '<div class="query-section-label">Background</div>';
            html += '<div class="query-section-text">' + escapeHtml(background) + '</div>';
            html += '</div>';
        }
    }

    html += '</div>';  // query-box-content
    html += '</div>';  // query-box

    // Report text area
    html += '<div class="source-text-area" id="sourceText">';
    html += renderReportText(report);
    html += '</div>';

    sourceContent.innerHTML = html;

    // Attach selection handler
    attachSourceSelectionHandler();

    // Apply quote highlights
    applyQuoteHighlights();
}

// Render report text with sentence structure
function renderReportText(report) {
    if (!report || !report.sentences) {
        return '<p>' + escapeHtml(report ? (report.text || '') : '') + '</p>';
    }

    var html = '';
    report.sentences.forEach(function(sentence, idx) {
        html += '<p data-sentence-idx="' + idx + '">';
        html += escapeHtml(sentence.text || '');

        // Add citation markers if present
        if (sentence.citations && sentence.citations.length > 0) {
            sentence.citations.forEach(function(docId) {
                html += ' <span class="citation-marker" data-doc-id="' + escapeHtml(docId) + '">[' + escapeHtml(docId.substring(0, 8)) + ']</span>';
            });
        }

        html += '</p>';
    });

    return html;
}

// Category precedence for highlights: avoid (highest) > must > should (lowest)
var categoryPrecedence = { 'avoid': 3, 'must': 2, 'should': 1 };

// Apply quote highlights based on nugget grades
function applyQuoteHighlights() {
    if (!state.selectedTopic || !state.selectedRun) return;

    var sourceText = document.getElementById('sourceText');
    if (!sourceText) return;

    // First, clear any existing highlights and badges
    sourceText.querySelectorAll('.has-quote-highlight').forEach(function(el) {
        el.classList.remove('has-quote-highlight', 'heavy-highlight', 'highlight-avoid', 'highlight-must', 'highlight-should');
        delete el.dataset.highlightNuggets;  // Now stores JSON array
        delete el.dataset.highlightCategory;
    });
    sourceText.querySelectorAll('.nugget-badge').forEach(function(el) {
        el.remove();
    });

    // Get all nuggets for this topic (both nuggets and claims)
    var bank = DATA.nugget_banks && DATA.nugget_banks[state.selectedTopic];
    if (!bank) return;

    var allNuggets = (bank.nuggets || []).concat(bank.claims || []);

    allNuggets.forEach(function(nugget) {
        var nuggetId = nugget.nugget_id;

        // Get grade for this report
        var grade = getReportGrade(state.selectedTopic, state.selectedRun, nuggetId);
        if (!grade || !grade.addressed_quote) return;

        // Check if this nugget should be heavily highlighted (Quote button active)
        var isHeavy = state.heavyHighlightNuggetId === nuggetId;

        // Debug: show what quote is being used for highlighting
        if (isHeavy) {
            console.log('=== applyQuoteHighlights ===');
            console.log('nuggetId:', nuggetId);
            console.log('nuggetText:', (nugget.text || nugget.question || '').substring(0, 50) + '...');
            console.log('runId:', state.selectedRun);
            console.log('grade.addressed_quote:', grade.addressed_quote.substring(0, 80) + '...');
        }

        // Find and highlight the quote
        var quote = grade.addressed_quote;
        var found = highlightQuoteInSource(sourceText, quote, nugget.importance || 'should_have', nuggetId, isHeavy);

        // Debug: log if quote wasn't found when it should have been highlighted
        if (isHeavy && !found) {
            console.warn('Quote not found in source text for nugget:', nuggetId);
            console.warn('Quote text:', quote.substring(0, 100) + '...');
        }
    });

    // After all highlights applied, add nugget count badges
    addNuggetBadges(sourceText);
}

// Add [Xn] badges to highlighted paragraphs
function addNuggetBadges(container) {
    container.querySelectorAll('.has-quote-highlight').forEach(function(el) {
        var nuggetIds = [];
        try {
            nuggetIds = JSON.parse(el.dataset.highlightNuggets || '[]');
        } catch (e) {
            nuggetIds = el.dataset.highlightNuggets ? [el.dataset.highlightNuggets] : [];
        }

        if (nuggetIds.length === 0) return;

        // Create badge
        var badge = document.createElement('span');
        badge.className = 'nugget-badge';
        badge.textContent = '[' + nuggetIds.length + 'n]';
        badge.dataset.nuggetIds = JSON.stringify(nuggetIds);
        badge.title = 'Click to see ' + nuggetIds.length + ' nugget(s) referencing this section';
        badge.onclick = function(e) {
            e.stopPropagation();
            showNuggetPopup(e, nuggetIds);
        };

        // Insert at start of paragraph
        el.insertBefore(badge, el.firstChild);
    });
}

// Show popup with nuggets that reference this section
function showNuggetPopup(event, nuggetIds) {
    // Remove any existing popup
    var existingPopup = document.querySelector('.nugget-popup');
    if (existingPopup) existingPopup.remove();

    // Get nugget details
    var bank = DATA.nugget_banks && DATA.nugget_banks[state.selectedTopic];
    if (!bank) return;

    var allNuggets = (bank.nuggets || []).concat(bank.claims || []);
    var matchingNuggets = nuggetIds.map(function(id) {
        return allNuggets.find(function(n) { return n.nugget_id === id; });
    }).filter(Boolean);

    if (matchingNuggets.length === 0) return;

    // Create popup
    var popup = document.createElement('div');
    popup.className = 'nugget-popup';

    var html = '<div class="nugget-popup-header">Nuggets (' + matchingNuggets.length + ')</div>';
    html += '<div class="nugget-popup-list">';

    matchingNuggets.forEach(function(nugget) {
        var category = nugget.importance || nugget.quality || 'should_have';
        var categoryClass = category === 'must_have' ? 'must' : (category === 'avoid' ? 'avoid' : 'should');
        var text = nugget.text || nugget.question || '';
        var preview = text.length > 400 ? text.substring(0, 400) + '...' : text;

        html += '<div class="nugget-popup-item" data-nugget-id="' + escapeHtml(nugget.nugget_id) + '">';
        html += '<span class="nugget-popup-category ' + categoryClass + '">' + categoryClass.toUpperCase() + '</span> ';
        html += '<span class="nugget-popup-text">' + escapeHtml(preview) + '</span>';
        html += '</div>';
    });

    html += '</div>';
    popup.innerHTML = html;

    // Position near click
    popup.style.left = event.pageX + 'px';
    popup.style.top = event.pageY + 'px';

    document.body.appendChild(popup);

    // Adjust if off-screen
    var rect = popup.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
        popup.style.left = (window.innerWidth - rect.width - 10) + 'px';
    }
    if (rect.bottom > window.innerHeight) {
        popup.style.top = (event.pageY - rect.height - 10) + 'px';
    }

    // Click on item to scroll to nugget
    popup.querySelectorAll('.nugget-popup-item').forEach(function(item) {
        item.onclick = function() {
            var nuggetId = item.dataset.nuggetId;
            scrollToNuggetInPanel(nuggetId);
            popup.remove();
        };
    });

    // Click outside to close
    setTimeout(function() {
        document.addEventListener('click', function closePopup(e) {
            if (!popup.contains(e.target)) {
                popup.remove();
                document.removeEventListener('click', closePopup);
            }
        });
    }, 0);
}

// Scroll to a nugget in the nuggets panel and highlight it
function scrollToNuggetInPanel(nuggetId) {
    var nuggetRow = document.querySelector('.nugget-row[data-nugget-id="' + nuggetId + '"]');
    if (nuggetRow) {
        nuggetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
        nuggetRow.classList.add('flash-highlight');
        setTimeout(function() {
            nuggetRow.classList.remove('flash-highlight');
        }, 1500);
    }
}

// Highlight a specific quote in the source text
// Returns true if quote was found and highlighted, false otherwise
function highlightQuoteInSource(container, quoteText, category, nuggetId, isHeavy) {
    if (!quoteText || !container) return false;

    // Scrub the quote first (in case it was stored with formatting issues)
    var scrubbedQuote = typeof scrubQuote === 'function' ? scrubQuote(quoteText) : quoteText;

    // Normalize for matching - handles Unicode variations (curly quotes, dashes, etc.)
    var normalizeFunc = typeof normalizeForMatching === 'function' ? normalizeForMatching : function(t) {
        return t.replace(/\s+/g, ' ').trim().toLowerCase();
    };

    var normalizedQuote = normalizeFunc(scrubbedQuote);
    if (normalizedQuote.length < 5) return false;  // Skip very short quotes

    // Walk through text nodes looking for match
    // Skip citation markers since LLM doesn't see them (they're rendered separately)
    var walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
        acceptNode: function(node) {
            // Skip text inside citation markers
            var parent = node.parentElement;
            while (parent && parent !== container) {
                if (parent.classList && parent.classList.contains('citation-marker')) {
                    return NodeFilter.FILTER_REJECT;
                }
                parent = parent.parentElement;
            }
            return NodeFilter.FILTER_ACCEPT;
        }
    }, false);
    var node;
    var fullText = '';
    var nodeMap = [];  // {node, start, end}

    while (node = walker.nextNode()) {
        // Add space between text nodes (paragraphs) to match how LLM sees joined text
        if (fullText.length > 0) fullText += ' ';
        // Record start AFTER adding space, so nodeMap positions match actual node content
        var start = fullText.length;
        fullText += node.textContent;
        nodeMap.push({ node: node, start: start, end: fullText.length });
    }

    // Try to find match in UNNORMALIZED text first (preserves positions)
    var lowerFullText = fullText.toLowerCase();
    var lowerQuote = scrubbedQuote.toLowerCase();
    var matchIdx = lowerFullText.indexOf(lowerQuote);

    // If not found, try normalized matching but then re-locate in unnormalized
    var usedNormalized = false;
    if (matchIdx === -1) {
        var normalizedFull = normalizeFunc(fullText);
        var normalizedMatchIdx = normalizedFull.indexOf(normalizedQuote);

        // Try partial matching if full quote not found
        if (normalizedMatchIdx === -1 && normalizedQuote.length > 100) {
            var shortQuote = normalizedQuote.substring(0, 100);
            normalizedMatchIdx = normalizedFull.indexOf(shortQuote);
            if (normalizedMatchIdx !== -1) {
                console.log('Matched partial quote (first 100 chars) in normalized');
            }
        }

        if (normalizedMatchIdx === -1 && normalizedQuote.length > 50) {
            var firstSentenceEnd = normalizedQuote.search(/[.!?]\s/);
            if (firstSentenceEnd > 20) {
                var firstSentence = normalizedQuote.substring(0, firstSentenceEnd + 1);
                normalizedMatchIdx = normalizedFull.indexOf(firstSentence);
                if (normalizedMatchIdx !== -1) {
                    console.log('Matched first sentence in normalized');
                }
            }
        }

        // If found in normalized, try to find same text in unnormalized using first N words
        if (normalizedMatchIdx !== -1) {
            usedNormalized = true;
            // Extract first few words from matched position
            var matchedNormText = normalizedFull.substring(normalizedMatchIdx, normalizedMatchIdx + 60);
            var firstWords = matchedNormText.split(/\s+/).slice(0, 5).join(' ');
            if (firstWords.length > 10) {
                // Search for these words in lowercased unnormalized text
                matchIdx = lowerFullText.indexOf(firstWords);
                if (matchIdx !== -1 && isHeavy) {
                    console.log('Re-located in unnormalized using first words:', firstWords);
                }
            }
        }
    }

    // Debug logging
    if (matchIdx === -1 && isHeavy) {
        console.log('=== Quote Match Debug ===');
        console.log('Quote length:', quoteText.length);
        console.log('Original quote (first 200):', quoteText.substring(0, 200));
        console.log('Lower quote (first 200):', lowerQuote.substring(0, 200));
        console.log('Source text length:', fullText.length);
        console.log('Source text (first 500):', fullText.substring(0, 500));
    }

    if (matchIdx === -1) return false;  // Quote not found

    // Debug: show what was matched and where
    if (isHeavy) {
        console.log('=== Quote Match SUCCESS ===');
        console.log('Match index (unnormalized):', matchIdx);
        console.log('Used normalized matching:', usedNormalized);
        console.log('Quote preview:', lowerQuote.substring(0, 80) + '...');
        console.log('Matched text in source:', fullText.substring(matchIdx, matchIdx + 80) + '...');
    }

    // Map back to original character positions
    var categoryClass = category === 'must_have' ? 'must' : (category === 'avoid' ? 'avoid' : 'should');

    // Find which node contains the start of the match
    for (var i = 0; i < nodeMap.length; i++) {
        var nodeInfo = nodeMap[i];
        if (nodeInfo.end > matchIdx) {
            // This node contains part of the match
            var parent = nodeInfo.node.parentElement;
            while (parent && parent !== container) {
                if (parent.tagName === 'P') {
                    parent.classList.add('has-quote-highlight');
                    if (isHeavy) {
                        parent.classList.add('heavy-highlight');
                    }

                    // Track multiple nuggets per paragraph
                    var existingNuggets = [];
                    try {
                        existingNuggets = JSON.parse(parent.dataset.highlightNuggets || '[]');
                    } catch (e) {
                        existingNuggets = [];
                    }
                    if (existingNuggets.indexOf(nuggetId) === -1) {
                        existingNuggets.push(nuggetId);
                    }
                    parent.dataset.highlightNuggets = JSON.stringify(existingNuggets);

                    // Apply category with precedence: avoid > must > should
                    var existingCategory = parent.dataset.highlightCategory || '';
                    var existingPrecedence = categoryPrecedence[existingCategory] || 0;
                    var newPrecedence = categoryPrecedence[categoryClass] || 0;

                    if (newPrecedence > existingPrecedence) {
                        // Remove old category class, add new one
                        parent.classList.remove('highlight-avoid', 'highlight-must', 'highlight-should');
                        parent.classList.add('highlight-' + categoryClass);
                        parent.dataset.highlightCategory = categoryClass;
                    } else if (!existingCategory) {
                        // No existing category, set this one
                        parent.classList.add('highlight-' + categoryClass);
                        parent.dataset.highlightCategory = categoryClass;
                    }

                    return true;  // Found and highlighted
                }
                parent = parent.parentElement;
            }
            break;
        }
    }
    return false;
}

// Store pending text selection for span adding
var pendingSpanText = '';
var pendingSpanSourceType = 'report';  // "report" | "document" | "query"

// Handle text selection for span adding (works on both source text and query box)
// sourceType parameter indicates where the selection came from
function handleTextSelection(e, sourceType) {
    var selection = window.getSelection();
    var text = selection.toString().trim();

    if (text.length > 0 && state.phase === 'creation') {
        if (!state.draftState.visible) {
            // Auto-open draft dialog and add the span directly
            showDraft();
            addSpanToDraft(text, sourceType || 'report');
            window.getSelection().removeAllRanges();
            selectionPrompt.classList.remove('visible');
        } else {
            // Draft is open - show prompt to let user click to add
            pendingSpanText = text;
            pendingSpanSourceType = sourceType || 'report';
            var range = selection.getRangeAt(0);
            var rect = range.getBoundingClientRect();
            selectionPrompt.style.left = (rect.left + rect.width / 2 - 50) + 'px';
            selectionPrompt.style.top = (rect.bottom + 8) + 'px';
            selectionPrompt.classList.add('visible');
        }
    } else {
        selectionPrompt.classList.remove('visible');
        pendingSpanText = '';
        pendingSpanSourceType = 'report';
    }
}

// Attach selection handler for adding spans to draft
function attachSourceSelectionHandler() {
    var sourceText = document.getElementById('sourceText');
    var queryBox = document.getElementById('queryBox');

    // Attach to source text (report content)
    if (sourceText) {
        sourceText.addEventListener('mouseup', function(e) {
            handleTextSelection(e, 'report');
        });

        // Citation marker click handler
        sourceText.addEventListener('click', function(e) {
            if (e.target.classList.contains('citation-marker')) {
                var docId = e.target.dataset.docId;
                showCitationModal(docId);
            }
        });
    }

    // Attach to query box (allows selecting from query/problem_statement/background)
    if (queryBox) {
        queryBox.addEventListener('mouseup', function(e) {
            handleTextSelection(e, 'query');
        });
    }
}

// Selection prompt click handler (uses stored pendingSpanText and pendingSpanSourceType)
if (selectionPrompt) {
    selectionPrompt.addEventListener('mousedown', function(e) {
        // Use mousedown to capture before selection is cleared
        e.preventDefault();
        e.stopPropagation();

        if (pendingSpanText && state.draftState.visible) {
            addSpanToDraft(pendingSpanText, pendingSpanSourceType);
            window.getSelection().removeAllRanges();
            selectionPrompt.classList.remove('visible');
            pendingSpanText = '';
            pendingSpanSourceType = 'report';
        }
    });
}

// Add a span to the draft card with source type tracking
// sourceType: "report" | "document" | "query"
function addSpanToDraft(text, sourceType) {
    state.draftState.spans.push({
        text: text,
        start: 0,  // TODO: compute actual offsets if needed
        end: text.length,
        sourceType: sourceType || 'report'
    });
    renderDraftSpans();
}

// Show citation document modal
function showCitationModal(docId) {
    if (!state.selectedTopic) return;

    var doc = docIndex[state.selectedTopic] && docIndex[state.selectedTopic][docId];
    if (!doc) {
        modalTitle.textContent = 'Document: ' + docId;
        modalText.textContent = 'Document not found.';
        modalUrl.href = '';
        modalUrl.textContent = '';
    } else {
        modalTitle.textContent = doc.title || docId;
        modalText.textContent = doc.text || '';
        if (doc.url) {
            modalUrl.href = doc.url;
            modalUrl.textContent = doc.url;
        } else {
            modalUrl.href = '';
            modalUrl.textContent = '';
        }
    }

    modalOverlay.classList.add('visible');
}

// Close modal
if (modalClose) {
    modalClose.addEventListener('click', function() {
        modalOverlay.classList.remove('visible');
    });
}
if (modalOverlay) {
    modalOverlay.addEventListener('click', function(e) {
        if (e.target === modalOverlay) {
            modalOverlay.classList.remove('visible');
        }
    });
}

// Legacy alias for backwards compatibility
function renderMain() {
    if (state.phase === 'creation') {
        renderSourcePanel();
    } else {
        renderRankingPanel();
    }
}
"""
