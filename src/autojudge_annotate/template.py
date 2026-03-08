"""Self-contained HTML template for the annotation interface.

Assembled from fragment modules — see template_*.py for the individual pieces.
"""

from .template_css import CSS_BLOCK
from .template_html import HTML_BLOCK
from .template_js_state import JS_STATE
from .template_js_sidebar import JS_SIDEBAR
from .template_js_main import JS_MAIN
from .template_js_spans import JS_SPANS
from .template_js_init import JS_INIT

HTML_TEMPLATE = (
    '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
    '<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    '<title>AutoJudge Annotation Interface</title>\n'
    '<style>\n' + CSS_BLOCK + '\n</style>\n</head>\n<body>\n'
    + HTML_BLOCK
    + '\n<script>\n(function() {\n"use strict";\n'
    + JS_STATE + '\n'
    + JS_SIDEBAR + '\n'
    + JS_MAIN + '\n'
    + JS_SPANS + '\n'
    + JS_INIT + '\n'
    + '})();\n</script>\n</body>\n</html>'
)
