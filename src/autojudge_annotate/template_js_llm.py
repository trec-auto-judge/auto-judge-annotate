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
    console.warn("No passage text for report:", runId);
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

    return {
      grade: grade,
      reasoning: parsed.reasoning || "",
      confidence: parseFloat(parsed.confidence) || 0.5
    };
  } catch (err) {
    console.error("Failed to parse grade response:", result, err);
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
  console.log("Grading complete for nugget:", nuggetId, "Completed:", gradingState.completed, "Errors:", gradingState.errors);
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
"""