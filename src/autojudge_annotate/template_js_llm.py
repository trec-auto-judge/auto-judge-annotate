"""JS LLM integration: OpenRouter API calls for nugget canonicalization."""

JS_LLM = r"""
// --- LLM Integration (OpenRouter) ---

var LLM_MODEL = "gpt-oss-120b";
var llmStatus = "none"; // "none", "ok", "error"

// Get/set API key from localStorage
function getLlmApiKey() {
  return localStorage.getItem("openrouter_api_key") || "";
}

function setLlmApiKey(key) {
  localStorage.setItem("openrouter_api_key", key);
  updateLlmIndicator();
}

// Update the topbar LLM indicator
function updateLlmIndicator() {
  var indicator = document.getElementById("llm-indicator");
  if (!indicator) return;

  var apiKey = getLlmApiKey();
  if (!apiKey) {
    indicator.textContent = "?";
    indicator.className = "llm-indicator llm-none";
    indicator.title = "Click to set OpenRouter API key";
  } else if (llmStatus === "error") {
    indicator.innerHTML = "&#10007;";
    indicator.className = "llm-indicator llm-error";
    indicator.title = "LLM error - click to change API key";
  } else {
    indicator.innerHTML = "&#10003;";
    indicator.className = "llm-indicator llm-ok";
    indicator.title = "LLM ready (" + LLM_MODEL + ") - click to change API key";
  }
}

// Attach click handler to LLM indicator
function attachLlmIndicatorHandler() {
  var indicator = document.getElementById("llm-indicator");
  if (indicator) {
    indicator.addEventListener("click", function() {
      var currentKey = getLlmApiKey();
      var msg = currentKey ? "Enter new OpenRouter API key (or cancel to keep current):" : "Enter your OpenRouter API key:";
      var key = prompt(msg);
      if (key !== null && key.trim()) {
        setLlmApiKey(key.trim());
        llmStatus = "none"; // Reset error state on new key
        updateLlmIndicator();
      }
    });
  }
}

// Call OpenRouter API
async function callLlm(prompt, systemPrompt) {
  var apiKey = getLlmApiKey();
  if (!apiKey) {
    alert("Please set your OpenRouter API key first (click LLM indicator in top bar).");
    return null;
  }

  var messages = [];
  if (systemPrompt) {
    messages.push({ role: "system", content: systemPrompt });
  }
  messages.push({ role: "user", content: prompt });

  try {
    var resp = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + apiKey,
        "Content-Type": "application/json",
        "HTTP-Referer": window.location.origin,
        "X-Title": "AutoJudge Annotate"
      },
      body: JSON.stringify({
        model: LLM_MODEL,
        messages: messages,
        temperature: 0.3
      })
    });

    if (!resp.ok) {
      var errText = await resp.text();
      console.error("LLM API error:", resp.status, errText);
      llmStatus = "error";
      updateLlmIndicator();
      alert("LLM API error: " + resp.status);
      return null;
    }

    var data = await resp.json();
    llmStatus = "ok";
    updateLlmIndicator();
    return data.choices[0].message.content;
  } catch (err) {
    console.error("LLM API call failed:", err);
    llmStatus = "error";
    updateLlmIndicator();
    alert("LLM API call failed: " + err.message);
    return null;
  }
}

// Canonicalize a nugget clue into a question-style nugget
async function canonicalizeClue(clue, topicId) {
  var request = DATA.requests.find(function(r) { return r.query_id === topicId; });

  // Build query context
  var queryContext = "";
  if (request) {
    if (request.title) queryContext += "Title: " + request.title + "\n";
    if (request.problem_statement) queryContext += "Problem Statement: " + request.problem_statement + "\n";
    if (request.background) queryContext += "User Background: " + request.background + "\n";
    if (request.query) queryContext += "Query: " + request.query + "\n";
    if (request.question) queryContext += "Question: " + request.question + "\n";
  }
  if (!queryContext) queryContext = "Topic ID: " + topicId + "\n";

  var systemPrompt = "You are helping create evaluation criteria as open-ended question nuggets for RAG system responses. " +
    "Generate brief, atomic questions that target query-essential information which a good response should answer well. " +
    "Focus on relevance, correctness, and completeness. " +
    "Avoid generic quality questions. Make questions self-contained (e.g., 'What is the capital of France?' not 'The capital?').";

  var prompt = "## Query Context\n" + queryContext + "\n";

  prompt += "## Annotator's Clue\n";
  prompt += "Clue type: " + clue.clue_type + "\n";
  if (clue.clue_type === "must_have") {
    prompt += "(This is essential information a good response MUST address)\n\n";
  } else if (clue.clue_type === "should_have") {
    prompt += "(This is helpful information a good response SHOULD include)\n\n";
  } else if (clue.clue_type === "avoid") {
    prompt += "(This is unhelpful information a good response MUST AVOID! If addressed, the response will be penalized.)\n\n";
  }

  if (clue.spans && clue.spans.length > 0) {
    prompt += "Selected text spans from the response:\n";
    clue.spans.forEach(function(sp) {
      prompt += '- "' + sp.text + '"\n';
    });
    prompt += "\n";
  }

  if (clue.comment) {
    prompt += "Annotator's comment: " + clue.comment + "\n\n";
  }

  prompt += "## Task\n";
  if (clue.clue_type === "avoid") {
    prompt += "Based on the query context and annotator's clue, create a brief, atomic question that:\n";
    prompt += "- Does not target query-essential information\n";
    prompt += "- An excellent RAG response would not address\n";
    prompt += "- Is self-contained (can be understood without additional context)\n\n";
    prompt += "Respond with JSON in this exact format:\n";
    prompt += "{\n";
    prompt += '  "nugget_question": "A clear, self-contained question",\n';
    prompt += '  "nugget_type": "' + clue.clue_type + '",\n';
    prompt += '  "explanation": "Brief explanation of why this question should be avoided for evaluating the response"\n';
    prompt += "}\n\n";
  } else {
    prompt += "Based on the query context and annotator's clue, create a brief, atomic question that:\n";
    prompt += "- Targets query-essential information\n";
    prompt += "- A good RAG response should answer well\n";
    prompt += "- Is self-contained (can be understood without additional context)\n\n";
    prompt += "Respond with JSON in this exact format:\n";
    prompt += "{\n";
    prompt += '  "nugget_question": "A clear, self-contained question",\n';
    prompt += '  "nugget_type": "' + clue.clue_type + '",\n';
    prompt += '  "explanation": "Brief explanation of why this question matters for evaluating the response"\n';
    prompt += "}\n\n";
  }
  prompt += "Only respond with the JSON, no other text.";

  var result = await callLlm(prompt, systemPrompt);
  if (!result) return null;

  try {
    // Try to parse JSON from response (may have markdown code blocks)
    var jsonStr = result.trim();
    if (jsonStr.startsWith("```")) {
      jsonStr = jsonStr.replace(/```json?\n?/g, "").replace(/```/g, "").trim();
    }
    // Fix common LLM JSON issues: missing closing brace
    if (jsonStr.startsWith("{") && !jsonStr.endsWith("}")) {
      jsonStr = jsonStr + "}";
    }
    var parsed = JSON.parse(jsonStr);
    // Normalize field names (support both nugget_question and nugget_text)
    return {
      nugget_text: parsed.nugget_question || parsed.nugget_text,
      nugget_type: parsed.nugget_type || clue.clue_type,
      explanation: parsed.explanation || ""
    };
  } catch (err) {
    console.error("Failed to parse LLM response as JSON:", result);
    alert("LLM response was not valid JSON. Check console for details.");
    return null;
  }
}

// Initialize LLM indicator on page load
function initLlmIndicator() {
  var apiKey = getLlmApiKey();
  if (apiKey) {
    llmStatus = "ok"; // Assume ok if key exists
  }
  updateLlmIndicator();
  attachLlmIndicatorHandler();
}

// --- Backpressure Queue for LLM Requests ---
// Limits concurrent requests to avoid rate limiting

var llmQueue = {
  maxConcurrent: 32,
  running: 0,
  queue: [],
  staggerMs: 50  // Small delay between starting requests
};

// Add a task to the queue and process
function queueLlmTask(taskFn) {
  return new Promise(function(resolve, reject) {
    llmQueue.queue.push({ taskFn: taskFn, resolve: resolve, reject: reject });
    processLlmQueue();
  });
}

// Process the queue
function processLlmQueue() {
  while (llmQueue.running < llmQueue.maxConcurrent && llmQueue.queue.length > 0) {
    var item = llmQueue.queue.shift();
    llmQueue.running++;

    // Stagger requests slightly
    setTimeout(function(taskItem) {
      taskItem.taskFn()
        .then(function(result) {
          llmQueue.running--;
          taskItem.resolve(result);
          processLlmQueue();
        })
        .catch(function(err) {
          llmQueue.running--;
          taskItem.reject(err);
          processLlmQueue();
        });
    }, llmQueue.staggerMs * llmQueue.running, item);
  }
}

// --- Nugget Grading ---

// Grading state for UI feedback
var gradingState = {
  activeNuggetId: null,  // Currently grading nugget
  completed: 0,
  total: 0,
  errors: 0
};

// Update grading progress display
function updateGradingProgress(nuggetId) {
  var progressEl = document.getElementById("grading-progress-" + nuggetId);
  if (progressEl) {
    if (gradingState.total === 0) {
      progressEl.textContent = "0/?";
    } else if (gradingState.completed >= gradingState.total) {
      progressEl.textContent = "Done!";
      progressEl.className = "grading-progress-inline grading-done";
    } else {
      progressEl.textContent = gradingState.completed + "/" + gradingState.total;
      if (gradingState.errors > 0) {
        progressEl.textContent += " (" + gradingState.errors + " err)";
      }
      progressEl.className = "grading-progress-inline grading-active";
    }
  }
}

// Grade a nugget against a single report
async function gradeNuggetForReport(topicId, runId, nuggetId, nuggetText, isAvoidNugget) {
  var report = reportIndex[topicId] && reportIndex[topicId][runId];
  if (!report) return null;

  var passage = report.response_text || "";
  if (!passage && report.sentences) {
    // Fallback: join sentences if response_text not available
    passage = report.sentences.map(function(s) { return s.text; }).join(" ");
  }

  if (!passage) {
    return null;
  }

  // Build the grading prompt based on GradeNuggetAnswer signature
  var systemPrompt = "Grade how well a passage answers a specific question.\n\n" +
    "Can the question be answered based on the available context? Choose one:\n" +
    "- 5: The answer is highly relevant, complete, and accurate.\n" +
    "- 4: The answer is mostly relevant and complete but may have minor gaps or inaccuracies.\n" +
    "- 3: The answer is partially relevant and complete, with noticeable gaps or inaccuracies.\n" +
    "- 2: The answer has limited relevance and completeness, with significant gaps or inaccuracies.\n" +
    "- 1: The answer is minimally relevant or complete, with substantial shortcomings.\n" +
    "- 0: The answer is not relevant or complete at all.";

  var prompt;
  if (isAvoidNugget) {
    prompt = "## Anti-Nugget (content to avoid)\n" + nuggetText + "\n\n";
    prompt += "## Passage to evaluate\n" + passage.substring(0, 8000) + "\n\n"; // Truncate for token limits
    prompt += "## Task\n";
    prompt += "Check if the passage contains the problematic content described in the anti-nugget.\n";
    prompt += "Grade 0 = content is NOT present (good), Grade 5 = content IS clearly present (bad).\n\n";
  } else {
    prompt = "## Question\n" + nuggetText + "\n\n";
    prompt += "## Passage\n" + passage.substring(0, 8000) + "\n\n"; // Truncate for token limits
    prompt += "## Task\n";
    prompt += "Grade how well the passage answers the question.\n\n";
  }

  prompt += "Respond with JSON in this exact format:\n";
  prompt += "{\n";
  prompt += '  "grade": "0-5",\n';
  prompt += '  "reasoning": "Brief explanation of the grade",\n';
  prompt += '  "confidence": 0.0-1.0\n';
  prompt += "}\n\n";
  prompt += "Only respond with the JSON, no other text.";

  var result = await callLlm(prompt, systemPrompt);
  if (!result) return null;

  try {
    var jsonStr = result.trim();
    if (jsonStr.startsWith("```")) {
      jsonStr = jsonStr.replace(/```json?\n?/g, "").replace(/```/g, "").trim();
    }
    var parsed = JSON.parse(jsonStr);

    var grade = parseInt(parsed.grade, 10);
    if (isNaN(grade) || grade < 0 || grade > 5) {
      console.warn("Invalid grade value:", parsed.grade);
      grade = 0;
    }

    // NOTE: We do NOT invert grades for avoid nuggets here.
    // The grade reflects PRESENCE (is this topic addressed?), not goodness.
    // The negative weight for ranking avoid nuggets is handled separately.
    // Motto: "Nuggets get a check mark whenever they are present."

    var gradeData = {
      grade: grade,
      reasoning: parsed.reasoning || "",
      confidence: parseFloat(parsed.confidence) || 0.5,
      addressed_quote: null
    };

    // For high grades (>= 4), extract the addressed quote
    if (grade >= 4) {
      // Increment total to account for the quote extraction prompt
      gradingState.total++;
      updateGradingProgress(gradingState.activeNuggetId);

      var quote = await extractAddressedQuote(nuggetText, passage);
      if (quote) {
        gradeData.addressed_quote = quote;
      }

      // Count quote extraction as completed
      gradingState.completed++;
      updateGradingProgress(gradingState.activeNuggetId);
    }

    return gradeData;
  } catch (err) {
    console.error("Failed to parse grade response:", result, err);
    return null;
  }
}

// Extract the contiguous quote from a passage that addresses a question
// Returns the quote string or null if not found/invalid
async function extractAddressedQuote(question, passage) {
  var systemPrompt = "Extract a contiguous verbatim quote from a passage that addresses a question.";

  var prompt = "## Question\n" + question + "\n\n";
  prompt += "## Passage\n" + passage.substring(0, 8000) + "\n\n";
  prompt += "## Task\n";
  prompt += "Find a SINGLE CONTIGUOUS text span that best supports the answer to the question.\n\n";
  prompt += "CRITICAL REQUIREMENTS:\n";
  prompt += "- The quote MUST be a single contiguous span - one unbroken sequence of characters that appears exactly as-is in the passage\n";
  prompt += "- Do NOT combine sentences from different parts of the passage\n";
  prompt += "- Do NOT rearrange or reorder text\n";
  prompt += "- Do NOT include quotation marks around the extracted text\n";
  prompt += "- Copy the text character-for-character from the passage\n\n";
  prompt += "If multiple relevant sections exist, choose the SINGLE BEST contiguous span. Do not try to combine them.\n\n";
  prompt += "Respond with JSON in this exact format:\n";
  prompt += "{\n";
  prompt += '  "extracted_quote": "the exact contiguous text from the passage, or null if none found",\n';
  prompt += '  "confidence": 0.0-1.0\n';
  prompt += "}\n\n";
  prompt += "Only respond with the JSON, no other text.";

  var result = await callLlm(prompt, systemPrompt);
  if (!result) return null;

  try {
    var jsonStr = result.trim();
    if (jsonStr.startsWith("```")) {
      jsonStr = jsonStr.replace(/```json?\n?/g, "").replace(/```/g, "").trim();
    }
    var parsed = JSON.parse(jsonStr);

    var quote = parsed.extracted_quote;
    var confidence = parseFloat(parsed.confidence) || 0.5;

    // Normalize empty/none values
    if (!quote || quote.toLowerCase() === "none" || quote.toLowerCase() === "null" || quote === "n/a") {
      console.warn("Quote extraction returned empty/none value");
      return null;
    }

    // Strip surrounding quotes if LLM added them anyway
    quote = quote.trim();
    while (quote.length >= 2 && (
      (quote.startsWith('"') && quote.endsWith('"')) ||
      (quote.startsWith("'") && quote.endsWith("'"))
    )) {
      quote = quote.slice(1, -1).trim();
    }

    // Validate: quote must actually exist in the passage (whitespace-normalized)
    var normPassage = passage.replace(/\s+/g, " ").toLowerCase();
    var normQuote = quote.replace(/\s+/g, " ").toLowerCase();
    if (!normPassage.includes(normQuote)) {
      console.warn("Extracted quote not found in passage, discarding:", quote.substring(0, 80) + "...");
      return null;
    }

    // Only accept if confidence is reasonable
    if (confidence < 0.2) {
      console.warn("Quote extraction confidence too low:", confidence);
      return null;
    }

    return quote;
  } catch (err) {
    console.error("Failed to parse quote extraction response:", result, err);
    return null;
  }
}

// Store a user-generated grade
function storeUserGrade(topicId, runId, nuggetId, gradeData) {
  if (!state.userNuggetGrades[topicId]) {
    state.userNuggetGrades[topicId] = {};
  }
  if (!state.userNuggetGrades[topicId][runId]) {
    state.userNuggetGrades[topicId][runId] = {};
  }
  state.userNuggetGrades[topicId][runId][nuggetId] = gradeData;
  saveUserNuggetGrades();
}

// Grade a user nugget across all reports for a topic
async function gradeUserNuggetAcrossReports(topicId, nuggetId, nuggetText, isAvoidNugget) {
  var runs = reportIndex[topicId] ? Object.keys(reportIndex[topicId]) : [];
  if (runs.length === 0) {
    alert("No reports found for this topic.");
    return;
  }

  // Initialize grading state
  gradingState.activeNuggetId = nuggetId;
  gradingState.completed = 0;
  gradingState.total = runs.length;
  gradingState.errors = 0;
  updateGradingProgress(nuggetId);

  // Queue all grading tasks
  var promises = runs.map(function(runId) {
    return queueLlmTask(async function() {
      var result = await gradeNuggetForReport(topicId, runId, nuggetId, nuggetText, isAvoidNugget);

      if (result) {
        storeUserGrade(topicId, runId, nuggetId, result);
      } else {
        gradingState.errors++;
      }

      gradingState.completed++;
      updateGradingProgress(nuggetId);

      // Refresh main panel to show updated verdicts
      renderMain();

      return result;
    });
  });

  // Wait for all to complete
  await Promise.all(promises);

  gradingState.activeNuggetId = null;
}

// Check if a nugget is currently being graded
function isNuggetGrading(nuggetId) {
  return gradingState.activeNuggetId === nuggetId;
}

// Check if a user nugget has any grades
function hasUserNuggetGrades(topicId, nuggetId) {
  if (!state.userNuggetGrades[topicId]) return false;
  var runs = Object.keys(state.userNuggetGrades[topicId]);
  for (var i = 0; i < runs.length; i++) {
    if (state.userNuggetGrades[topicId][runs[i]][nuggetId]) {
      return true;
    }
  }
  return false;
}

// --- Quote Extraction for Active Nuggets ---

var quoteExtractionState = {
  active: false,
  completed: 0,
  total: 0,
  errors: 0
};

function updateQuoteExtractionProgress() {
  var progressEl = document.getElementById("quote-extraction-progress");
  if (progressEl) {
    if (quoteExtractionState.total === 0) {
      progressEl.textContent = "";
      progressEl.className = "quote-progress-inline";
    } else if (quoteExtractionState.completed >= quoteExtractionState.total) {
      progressEl.textContent = "Done!";
      progressEl.className = "quote-progress-inline quote-done";
    } else {
      progressEl.textContent = quoteExtractionState.completed + "/" + quoteExtractionState.total;
      if (quoteExtractionState.errors > 0) {
        progressEl.textContent += " (" + quoteExtractionState.errors + " err)";
      }
      progressEl.className = "quote-progress-inline quote-active";
    }
  }
}

// Extract quotes for all active nuggets that have grades but no addressed_quote
async function extractQuotesForActiveNuggets() {
  var topicId = state.selectedTopic;
  var runId = state.selectedRun;
  var docId = state.selectedDoc;

  if (!topicId) return;

  // Determine passage source
  var passage = null;
  var isDocMode = !!docId;

  if (isDocMode) {
    // Document mode - get document text
    var doc = docIndex[topicId] && docIndex[topicId][docId];
    if (doc) {
      passage = doc.text || doc.body || "";
    }
  } else if (runId) {
    // Report mode - get report text
    var report = reportIndex[topicId] && reportIndex[topicId][runId];
    if (report) {
      passage = report.response_text || "";
      if (!passage && report.sentences) {
        passage = report.sentences.map(function(s) { return s.text; }).join(" ");
      }
    }
  }

  if (!passage) {
    console.warn("No passage text available for quote extraction");
    return;
  }

  // Get all active nuggets (pre-loaded + user-created)
  var bank = getNuggetsForTopic(topicId);
  var nuggets = bank.nuggets || [];
  var userNuggets = (typeof getCanonicalizedNuggetsForTopic === "function")
    ? getCanonicalizedNuggetsForTopic(topicId)
    : [];
  var allNuggets = nuggets.concat(userNuggets);

  // Filter to active nuggets that have grades but no quote
  var toProcess = [];
  allNuggets.forEach(function(n) {
    // Skip disabled nuggets
    if (typeof isNuggetEffectivelyEnabled === "function" && !isNuggetEffectivelyEnabled(n.nugget_id)) {
      return;
    }

    // Get grade for this nugget
    var gradeInfo = null;
    if (isDocMode) {
      gradeInfo = getDocGrade(topicId, docId, n.nugget_id);
      // For documents with paragraph-level grades (pre-loaded format)
      if (gradeInfo && gradeInfo.paragraphs) {
        var needsQuote = false;
        var bestPara = null;
        var bestGrade = 0;
        Object.keys(gradeInfo.paragraphs).forEach(function(pk) {
          var para = gradeInfo.paragraphs[pk];
          if (para.grade >= 1 && !para.addressed_quote) {
            needsQuote = true;
            // Track the highest-graded paragraph without a quote
            if (para.grade > bestGrade) {
              bestGrade = para.grade;
              bestPara = pk;
            }
          }
        });
        if (needsQuote && bestPara !== null) {
          toProcess.push({
            nugget: n,
            gradeInfo: gradeInfo,
            paragraphKey: bestPara,
            nuggetText: n.text || n.question || ""
          });
        }
      } else if (gradeInfo && gradeInfo.grade >= 1 && !gradeInfo.addressed_quote) {
        // For documents with flat grades (user-generated format)
        toProcess.push({
          nugget: n,
          gradeInfo: gradeInfo,
          paragraphKey: null,
          nuggetText: n.text || n.question || ""
        });
      }
    } else if (runId) {
      gradeInfo = getReportGrade(topicId, runId, n.nugget_id);
      // For reports, check top-level grade and quote
      if (gradeInfo && gradeInfo.grade >= 1 && !gradeInfo.addressed_quote) {
        toProcess.push({
          nugget: n,
          gradeInfo: gradeInfo,
          paragraphKey: null,
          nuggetText: n.text || n.question || ""
        });
      }
    }
  });

  if (toProcess.length === 0) {
    return;
  }

  // Initialize progress
  quoteExtractionState.active = true;
  quoteExtractionState.completed = 0;
  quoteExtractionState.total = toProcess.length;
  quoteExtractionState.errors = 0;
  updateQuoteExtractionProgress();

  // Process each nugget
  var promises = toProcess.map(function(item) {
    return queueLlmTask(async function() {
      var quote = await extractAddressedQuote(item.nuggetText, passage);

      if (quote) {

        if (isDocMode && item.paragraphKey !== null) {
          // Document mode with paragraph-level grades - store quote at paragraph level
          item.gradeInfo.paragraphs[item.paragraphKey].addressed_quote = quote;
          // Note: doc grades are stored in DATA.doc_grades, modification persists in memory
        } else if (isDocMode) {
          // Document mode with flat grades (user-generated) - store quote at top level
          item.gradeInfo.addressed_quote = quote;

          // Also store in userDocGrades (takes precedence over DATA.doc_grades)
          var updatedDocGrade = {
            grade: item.gradeInfo.grade,
            reasoning: item.gradeInfo.reasoning || "",
            confidence: item.gradeInfo.confidence || 0.5,
            addressed_quote: quote
          };
          storeUserDocGrade(topicId, docId, item.nugget.nugget_id, updatedDocGrade);
        } else {
          // Report mode - store quote at top level
          item.gradeInfo.addressed_quote = quote;

          // Also store in userNuggetGrades (takes precedence over DATA.nugget_grades)
          if (runId) {
            var updatedGrade = {
              grade: item.gradeInfo.grade,
              reasoning: item.gradeInfo.reasoning || "",
              confidence: item.gradeInfo.confidence || 0.5,
              addressed_quote: quote
            };
            storeUserGrade(topicId, runId, item.nugget.nugget_id, updatedGrade);
          }
        }
      } else {
        quoteExtractionState.errors++;
      }

      quoteExtractionState.completed++;
      updateQuoteExtractionProgress();

      // Refresh to show new highlights
      renderMain();

      return quote;
    });
  });

  await Promise.all(promises);

  quoteExtractionState.active = false;
}

// Check if quote extraction is currently running
function isQuoteExtractionActive() {
  return quoteExtractionState.active;
}

// --- Grade Documents for Current Report ---

var gradeDocsState = {
  active: false,
  completed: 0,
  total: 0,
  errors: 0
};

function updateGradeDocsProgress() {
  var progressEl = document.getElementById("grade-docs-progress");
  if (progressEl) {
    if (gradeDocsState.total === 0) {
      progressEl.textContent = "";
      progressEl.className = "grade-docs-progress-inline";
    } else if (gradeDocsState.completed >= gradeDocsState.total) {
      progressEl.textContent = "Done!";
      progressEl.className = "grade-docs-progress-inline grade-docs-done";
    } else {
      progressEl.textContent = gradeDocsState.completed + "/" + gradeDocsState.total;
      if (gradeDocsState.errors > 0) {
        progressEl.textContent += " (" + gradeDocsState.errors + " err)";
      }
      progressEl.className = "grade-docs-progress-inline grade-docs-active";
    }
  }
}

// Store a user-generated doc grade
function storeUserDocGrade(topicId, docId, nuggetId, gradeData) {
  if (!state.userDocGrades[topicId]) {
    state.userDocGrades[topicId] = {};
  }
  if (!state.userDocGrades[topicId][docId]) {
    state.userDocGrades[topicId][docId] = {};
  }
  state.userDocGrades[topicId][docId][nuggetId] = gradeData;
  saveUserDocGrades();
}

// Grade a nugget against a single document
async function gradeNuggetForDoc(topicId, docId, nuggetId, nuggetText, isAvoidNugget) {
  var doc = docIndex[topicId] && docIndex[topicId][docId];
  if (!doc) return null;

  var passage = doc.text || doc.body || "";
  if (!passage) {
    console.warn("No passage text for document:", docId);
    return null;
  }

  // Build the grading prompt (same as gradeNuggetForReport)
  var systemPrompt = "Grade how well a passage answers a specific question.\n\n" +
    "Can the question be answered based on the available context? Choose one:\n" +
    "- 5: The answer is highly relevant, complete, and accurate.\n" +
    "- 4: The answer is mostly relevant and complete but may have minor gaps or inaccuracies.\n" +
    "- 3: The answer is partially relevant and complete, with noticeable gaps or inaccuracies.\n" +
    "- 2: The answer has limited relevance and completeness, with significant gaps or inaccuracies.\n" +
    "- 1: The answer is minimally relevant or complete, with substantial shortcomings.\n" +
    "- 0: The answer is not relevant or complete at all.";

  var prompt;
  if (isAvoidNugget) {
    prompt = "## Anti-Nugget (content to avoid)\n" + nuggetText + "\n\n";
    prompt += "## Passage to evaluate\n" + passage.substring(0, 8000) + "\n\n";
    prompt += "## Task\n";
    prompt += "Check if the passage contains the problematic content described in the anti-nugget.\n";
    prompt += "Grade 0 = content is NOT present (good), Grade 5 = content IS clearly present (bad).\n\n";
  } else {
    prompt = "## Question\n" + nuggetText + "\n\n";
    prompt += "## Passage\n" + passage.substring(0, 8000) + "\n\n";
    prompt += "## Task\n";
    prompt += "Grade how well the passage answers the question.\n\n";
  }

  prompt += "Respond with JSON in this exact format:\n";
  prompt += "{\n";
  prompt += '  "grade": "0-5",\n';
  prompt += '  "reasoning": "Brief explanation of the grade",\n';
  prompt += '  "confidence": 0.0-1.0\n';
  prompt += "}\n\n";
  prompt += "Only respond with the JSON, no other text.";

  var result = await callLlm(prompt, systemPrompt);
  if (!result) return null;

  try {
    var jsonStr = result.trim();
    if (jsonStr.startsWith("```")) {
      jsonStr = jsonStr.replace(/```json?\n?/g, "").replace(/```/g, "").trim();
    }
    var parsed = JSON.parse(jsonStr);

    var grade = parseInt(parsed.grade, 10);
    if (isNaN(grade) || grade < 0 || grade > 5) {
      console.warn("Invalid grade value:", parsed.grade);
      grade = 0;
    }

    var gradeData = {
      grade: grade,
      reasoning: parsed.reasoning || "",
      confidence: parseFloat(parsed.confidence) || 0.5,
      addressed_quote: null
    };

    // For high grades (>= 4), extract the addressed quote
    if (grade >= 4) {
      gradeDocsState.total++;
      updateGradeDocsProgress();

      var quote = await extractAddressedQuote(nuggetText, passage);
      if (quote) {
        gradeData.addressed_quote = quote;
      }

      gradeDocsState.completed++;
      updateGradeDocsProgress();
    }

    return gradeData;
  } catch (err) {
    console.error("Failed to parse grade response:", result, err);
    return null;
  }
}

// Grade user nuggets against all documents cited by the current report
async function gradeDocsForReport() {
  var topicId = state.selectedTopic;
  var runId = state.selectedRun;

  if (!topicId || !runId) {
    alert("Please select a report first.");
    return;
  }

  // Get cited documents from the current report
  var report = reportIndex[topicId] && reportIndex[topicId][runId];
  if (!report) {
    alert("Report not found.");
    return;
  }

  var docIds = (typeof getReportDocIds === "function") ? getReportDocIds(report) : [];

  // Get active user nuggets (only user-created nuggets, not pre-loaded ones)
  var userNuggets = (typeof getCanonicalizedNuggetsForTopic === "function")
    ? getCanonicalizedNuggetsForTopic(topicId)
    : [];

  if (userNuggets.length === 0) {
    alert("No user-created nuggets for this topic. Create nuggets first by selecting spans and canonicalizing them.");
    return;
  }

  // Filter to enabled nuggets only
  var enabledNuggets = userNuggets.filter(function(n) {
    return typeof isNuggetEffectivelyEnabled !== "function" || isNuggetEffectivelyEnabled(n.nugget_id);
  });

  if (enabledNuggets.length === 0) {
    alert("No active user nuggets. Enable some nuggets using the checkboxes.");
    return;
  }

  // Build list of items that need grading (report + documents)
  var toProcessReport = [];
  var toProcessDocs = [];

  enabledNuggets.forEach(function(n) {
    var nuggetText = n.text || n.question || "";
    var isAvoidNugget = n.nugget_type === "avoid";

    // Check if report needs grading for this nugget
    var existingReportGrade = (typeof getReportGrade === "function") ? getReportGrade(topicId, runId, n.nugget_id) : null;
    if (!existingReportGrade || typeof existingReportGrade.grade !== "number") {
      toProcessReport.push({
        nugget: n,
        nuggetText: nuggetText,
        isAvoidNugget: isAvoidNugget
      });
    }

    // Check if documents need grading for this nugget
    docIds.forEach(function(docId) {
      var existingDocGrade = (typeof getDocGrade === "function") ? getDocGrade(topicId, docId, n.nugget_id) : null;
      if (!existingDocGrade || typeof existingDocGrade.grade !== "number") {
        toProcessDocs.push({
          nugget: n,
          docId: docId,
          nuggetText: nuggetText,
          isAvoidNugget: isAvoidNugget
        });
      }
    });
  });

  var totalToProcess = toProcessReport.length + toProcessDocs.length;
  if (totalToProcess === 0) {
    alert("All nuggets are already graded for this report and its documents.");
    return;
  }

  // Initialize progress
  gradeDocsState.active = true;
  gradeDocsState.completed = 0;
  gradeDocsState.total = totalToProcess;
  gradeDocsState.errors = 0;
  updateGradeDocsProgress();

  // Process report grades
  var reportPromises = toProcessReport.map(function(item) {
    return queueLlmTask(async function() {
      var result = await gradeNuggetForReport(topicId, runId, item.nugget.nugget_id, item.nuggetText, item.isAvoidNugget);

      if (result) {
        storeUserGrade(topicId, runId, item.nugget.nugget_id, result);
      } else {
        gradeDocsState.errors++;
      }

      gradeDocsState.completed++;
      updateGradeDocsProgress();
      renderMain();

      return result;
    });
  });

  // Process document grades
  var docPromises = toProcessDocs.map(function(item) {
    return queueLlmTask(async function() {
      var result = await gradeNuggetForDoc(topicId, item.docId, item.nugget.nugget_id, item.nuggetText, item.isAvoidNugget);

      if (result) {
        storeUserDocGrade(topicId, item.docId, item.nugget.nugget_id, result);
      } else {
        gradeDocsState.errors++;
      }

      gradeDocsState.completed++;
      updateGradeDocsProgress();
      renderMain();

      return result;
    });
  });

  await Promise.all(reportPromises.concat(docPromises));

  gradeDocsState.active = false;

  // Update sidebar to reflect new coverage counts
  if (typeof renderSidebar === "function") {
    renderSidebar();
  }
}

// Check if Grade Docs is currently running
function isGradeDocsActive() {
  return gradeDocsState.active;
}
"""