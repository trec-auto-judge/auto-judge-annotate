"""JS nugget clue capture: UI for creating and managing nugget clues from spans + comments."""

JS_CLUES = r"""
// --- Nugget Clue Capture ---

// State for clue creation mode
var clueCreationMode = false;
var pendingClueType = "must_have";

// Render the nugget clues section
function renderNuggetCluesSection(ann) {
  var html = '<div class="nugget-clues-section">';
  html += '<h3>Nugget Clues <span class="clue-count">(' + (ann.nugget_clues ? ann.nugget_clues.length : 0) + ')</span></h3>';

  // Add clue button and type selector (radio buttons)
  html += '<div class="clue-add-controls">';
  html += '<div class="clue-type-radios">';
  html += '<label class="clue-type-radio clue-type-must_have"><input type="radio" name="clue-type" value="must_have"' + (pendingClueType === "must_have" ? " checked" : "") + '><span>Must-have</span></label>';
  html += '<label class="clue-type-radio clue-type-should_have"><input type="radio" name="clue-type" value="should_have"' + (pendingClueType === "should_have" ? " checked" : "") + '><span>Should-have</span></label>';
  html += '<label class="clue-type-radio clue-type-avoid"><input type="radio" name="clue-type" value="avoid"' + (pendingClueType === "avoid" ? " checked" : "") + '><span>Avoid</span></label>';
  html += '</div>';
  html += '<button class="add-clue-btn" id="add-clue-btn">+ Add Nugget Clue</button>';
  html += '</div>';

  // Help text
  html += '<p class="clue-help">Select text spans above, enter a comment below, then click "Add Nugget Clue" to create a clue.</p>';

  // List existing clues
  if (ann.nugget_clues && ann.nugget_clues.length > 0) {
    html += '<div class="clue-list">';
    ann.nugget_clues.forEach(function(clue, idx) {
      html += renderClueItem(clue, idx);
    });
    html += '</div>';
  }

  html += '</div>';
  return html;
}

// Render a single clue item
function renderClueItem(clue, idx) {
  var typeLabel = {
    "must_have": "Must-have",
    "should_have": "Should-have",
    "avoid": "Avoid"
  }[clue.clue_type] || clue.clue_type;

  var typeClass = "clue-type-" + clue.clue_type;

  var html = '<div class="clue-item ' + typeClass + '" data-clue-idx="' + idx + '">';
  html += '<div class="clue-header">';
  html += '<span class="clue-type-badge">' + escapeHtml(typeLabel) + '</span>';
  html += '<button class="clue-delete-btn" data-clue-idx="' + idx + '" title="Delete clue">&times;</button>';
  html += '</div>';

  // Show spans if any
  if (clue.spans && clue.spans.length > 0) {
    html += '<div class="clue-spans">';
    clue.spans.forEach(function(sp) {
      var preview = sp.text.length > 60 ? sp.text.substring(0, 57) + "..." : sp.text;
      html += '<span class="clue-span-chip" title="' + escapeHtml(sp.text) + '">"' + escapeHtml(preview) + '"</span>';
    });
    html += '</div>';
  }

  // Show linked nugget if any
  if (clue.linked_nugget_id) {
    html += '<div class="clue-linked">Linked to: ' + escapeHtml(clue.linked_nugget_id) + '</div>';
  }

  // Show canonicalized nugget if present
  if (clue.canonicalized) {
    html += '<div class="clue-canonicalized canon-type-' + clue.clue_type + '">';
    html += '<div class="clue-canon-label">Canonicalized Nugget:</div>';
    html += '<div class="clue-canon-text">' + escapeHtml(clue.canonicalized.nugget_text) + '</div>';
    if (clue.canonicalized.explanation) {
      html += '<div class="clue-canon-explanation">' + escapeHtml(clue.canonicalized.explanation) + '</div>';
    }
    html += '</div>';
  }

  // Editable comment field and action buttons
  html += '<div class="clue-actions">';
  html += '<input type="text" class="clue-comment-input" data-clue-idx="' + idx + '" placeholder="Clarification comment for LLM..." value="' + escapeHtml(clue.comment || '') + '">';
  if (!clue.canonicalized) {
    html += '<button class="clue-canonicalize-btn" data-clue-idx="' + idx + '">Canonicalize</button>';
  } else {
    html += '<button class="clue-canonicalize-btn" data-clue-idx="' + idx + '">Re-canonicalize</button>';
  }
  html += '</div>';

  html += '</div>';
  return html;
}

// Add a new nugget clue from current spans and comment
function addNuggetClue() {
  var ann = currentAnnotation();
  if (!ann) return;

  var comment = document.getElementById("comment-input");
  var commentText = comment ? comment.value.trim() : "";

  // Get current spans (copy them)
  var spans = (ann.spans || []).map(function(s) {
    return { start: s.start, end: s.end, text: s.text };
  });

  // Require at least spans or comment
  if (spans.length === 0 && !commentText) {
    alert("Please select some text spans or enter a comment before adding a nugget clue.");
    return;
  }

  // Get selected clue type from radio buttons
  var selectedRadio = document.querySelector('input[name="clue-type"]:checked');
  var clueType = selectedRadio ? selectedRadio.value : "must_have";

  // Create the clue
  var newClue = {
    clue_type: clueType,
    comment: commentText,
    spans: spans,
    linked_nugget_id: null
  };

  // Add to annotation
  if (!ann.nugget_clues) ann.nugget_clues = [];
  ann.nugget_clues.push(newClue);

  // Clear the spans and comment after adding (so user can add more)
  ann.spans = [];
  if (comment) comment.value = "";
  ann.comment = "";

  autoSave();
  renderMain();
}

// Delete a nugget clue by index
function deleteNuggetClue(idx) {
  var ann = currentAnnotation();
  if (!ann || !ann.nugget_clues) return;

  if (idx >= 0 && idx < ann.nugget_clues.length) {
    ann.nugget_clues.splice(idx, 1);
    autoSave();
    renderMain();
  }
}

// Attach event handlers for nugget clues section
function attachClueHandlers() {
  var addBtn = document.getElementById("add-clue-btn");
  if (addBtn) {
    addBtn.addEventListener("click", addNuggetClue);
  }

  // Clue type radio buttons
  var typeRadios = document.querySelectorAll('input[name="clue-type"]');
  typeRadios.forEach(function(radio) {
    radio.addEventListener("change", function() {
      pendingClueType = this.value;
    });
  });

  // Delete buttons
  var deleteBtns = document.querySelectorAll(".clue-delete-btn");
  deleteBtns.forEach(function(btn) {
    btn.addEventListener("click", function(e) {
      e.stopPropagation();
      var idx = parseInt(this.getAttribute("data-clue-idx"));
      if (confirm("Delete this nugget clue?")) {
        deleteNuggetClue(idx);
      }
    });
  });

  // Clue comment input fields
  var commentInputs = document.querySelectorAll(".clue-comment-input");
  commentInputs.forEach(function(input) {
    input.addEventListener("change", function() {
      var idx = parseInt(this.getAttribute("data-clue-idx"));
      var ann = currentAnnotation();
      if (!ann || !ann.nugget_clues || idx >= ann.nugget_clues.length) return;
      ann.nugget_clues[idx].comment = this.value.trim();
      autoSave();
    });
  });

  // Canonicalize buttons
  var canonBtns = document.querySelectorAll(".clue-canonicalize-btn");
  canonBtns.forEach(function(btn) {
    btn.addEventListener("click", async function(e) {
      e.stopPropagation();
      var idx = parseInt(this.getAttribute("data-clue-idx"));
      var ann = currentAnnotation();
      if (!ann || !ann.nugget_clues || idx >= ann.nugget_clues.length) return;

      var clue = ann.nugget_clues[idx];

      // Update comment from input field before canonicalizing
      var commentInput = document.querySelector('.clue-comment-input[data-clue-idx="' + idx + '"]');
      if (commentInput) {
        clue.comment = commentInput.value.trim();
      }

      // Show loading state
      btn.disabled = true;
      btn.textContent = "Processing...";

      try {
        var result = await canonicalizeClue(clue, state.selectedTopic);
        if (result) {
          clue.canonicalized = result;
          autoSave();
          renderMain();
        }
      } finally {
        btn.disabled = false;
        btn.textContent = clue.canonicalized ? "Re-canonicalize" : "Canonicalize";
      }
    });
  });
}
"""
