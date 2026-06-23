"""Self-contained HTML template for the annotation interface.

Assembled from fragment modules — see template_*.py for the individual pieces.

Nugget-Centric UI v12 modules:
- template_js_phase.py: Phase state machine (Creation/QC/Observe)
- template_js_nav.py: Navigation panel (queries/reports sections)
- template_js_source.py: Source panel (report text view)
- template_js_ranking.py: Ranking panel (QC/Observe phases)
- template_js_nuggets_panel.py: Nuggets panel (category sections)
- template_js_draft.py: Draft card (new nugget workflow)
"""

from .template_css import CSS_BLOCK
from .template_html import HTML_BLOCK
from .template_js_state import JS_STATE
from .template_js_sidebar import JS_SIDEBAR
from .template_js_nuggets import JS_NUGGETS
from .template_js_nuggets_mode import JS_NUGGETS_MODE
from .template_js_clues import JS_CLUES
from .template_js_llm import JS_LLM
from .template_js_main import JS_MAIN
from .template_js_spans import JS_SPANS
from .template_js_init import JS_INIT
from .template_js_sync import JS_SYNC

# Nugget-Centric UI v12 modules
from .template_js_phase import JS_PHASE
from .template_js_nav import JS_NAV
from .template_js_source import JS_SOURCE
from .template_js_ranking import JS_RANKING
from .template_js_nuggets_panel import JS_NUGGETS_PANEL
from .template_js_draft import JS_DRAFT

SUPABASE_CDN = '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>\n'

HTML_TEMPLATE = (
    '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
    '<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    '<title>AutoJudge Annotation Interface</title>\n'
    + SUPABASE_CDN
    + '<style>\n' + CSS_BLOCK + '\n</style>\n</head>\n<body>\n'
    + HTML_BLOCK
    + '\n<script>\n(function() {\n"use strict";\n'
    # Core state and data handling
    + JS_STATE + '\n'
    + JS_NUGGETS + '\n'
    + JS_NUGGETS_MODE + '\n'
    + JS_CLUES + '\n'
    + JS_LLM + '\n'
    # Legacy modules FIRST (so new UI can override)
    + JS_SIDEBAR + '\n'
    + JS_MAIN + '\n'
    + JS_SPANS + '\n'
    + JS_SYNC + '\n'
    # Nugget-Centric UI v12: Phase, Navigation, Panels (after legacy, so they override)
    + JS_PHASE + '\n'
    + JS_NAV + '\n'
    + JS_SOURCE + '\n'
    + JS_RANKING + '\n'
    + JS_NUGGETS_PANEL + '\n'
    + JS_DRAFT + '\n'
    # Initialization (always last)
    + JS_INIT + '\n'
    + '})();\n</script>\n</body>\n</html>'
)
