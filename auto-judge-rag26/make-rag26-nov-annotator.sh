#!/bin/sh
# Build the rag26-nov classroom annotator: merge every judge's rag26 nugget bank for the
# four topics, then generate the annotation web UI. If a grading run has produced rubric
# judgments (grade-rag26-nov.sh), flatten them and attach them as pre-computed grades.
# All inputs' overridable paths and all outputs live beside this script.
#
#   usage: EXPORT_CLEAN=<release>/clean/evalbase/runs/autojudge ./make-rag26-nov-annotator.sh
#   needs: pip install -e . in the auto-judge-annotate venv (autojudge-annotate + autojudge_base)
#
# The dataset and the export are gated; run this yourself against the real data.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/../.."                              # auto-judge-code-test

DATA="${DATA:-$ROOT/datasets/rag26}"
REPORTS="${REPORTS:-$DATA/runs/generation/}"
TOPICS="${TOPICS:-$DATA/topics/trec_rag_2026_queries.jsonl}"
OUT="${OUT:-$HERE/rag26-nov-annotate.html}"
DATASET="${DATASET:-rag26-nov}"
NUGGETS="${NUGGETS:-$HERE/rag26-nov-nuggets.jsonl}"
# The release clean tree (gated); rag26 banks at <runtag>/rag26/<llm>/<runtag>.nuggets.jsonl.
EXPORT_CLEAN="${EXPORT_CLEAN:-$ROOT/../trec2026-auto-judge-release/clean/evalbase/runs/autojudge}"
# Pre-computed grades. JUDGMENTS is the judge's own per-unit dump from grade-rag26-nov.sh
# (its real, persistent output). GRADES is a GENERATED TEMP INTERMEDIATE: we flatten the
# judge dump into the annotator's flat --nugget-grades schema and attach it if present
# (absent -> no grades, no error). GRADES must stay a DIFFERENT path from JUDGMENTS -- the
# flatten opens --out for writing, which would truncate the judgments if they were the
# same file (the flatten now refuses that outright). The temp intermediate is gitignored.
GRADES="${GRADES:-$HERE/rag26-nov-nugget-grades.jsonl}"          # temp intermediate (generated)
JUDGMENTS="${JUDGMENTS:-$HERE/rag26-nov-grades/rubric.judgments.jsonl}"  # judge's own output
# Binaries from this project's own venv (uv sync), falling back to PATH.
PY="${PY:-$HERE/.venv/bin/python}"; [ -x "$PY" ] || PY="python"
ANNOTATE="${ANNOTATE:-$HERE/.venv/bin/autojudge-annotate}"; [ -x "$ANNOTATE" ] || ANNOTATE="autojudge-annotate"
TOPIC_SEL="--topic rag2026-11 --topic rag2026-13 --topic rag2026-2 --topic rag2026-4"

# nltk >= 3.10 refuses a group/other-writable data dir and no longer has an env opt-out,
# so make the existing data private (owner-only); no re-download needed.
NLTK_HOME="${NLTK_DATA:-$HOME/nltk_data}"
[ -d "$NLTK_HOME" ] && chmod -R go-w "$NLTK_HOME"

# 1. Merge every judge's rag26 nugget bank in the export into one file (four topics,
#    union per topic deduped by question). -W silences a benign runpy warning.
# shellcheck disable=SC2046
$PY -W "ignore::RuntimeWarning" -m autojudge_base.nugget_data.merge \
  $(find "$EXPORT_CLEAN" -path '*/rag26/*' -name '*nuggets.jsonl' | sort) \
  --out "$NUGGETS" \
  $TOPIC_SEL

# 2. Flatten the rubric judgments into the annotator's flat grade schema, if grading has
#    run. nugget_id in the flattened file is md5(question); the annotator keys both cards
#    and grades by md5(question text), so they line up by content with no reconciliation.
if [ -f "$JUDGMENTS" ]; then
  $PY "$HERE/judgments_to_nugget_grades.py" "$JUDGMENTS" --out "$GRADES"
fi
grades_arg=""
[ -f "$GRADES" ] && grades_arg="--nugget-grades $GRADES"

# 3. Build the annotator HTML: four topics, the merged bank, and (if present) the grades.
#    --grading-prompt picks the in-browser "Grade All" prompt (embedded at compile time);
#    "rubric" matches the crucible rubric used for the pre-grades.
GRADING_PROMPT="${GRADING_PROMPT:-rubric}"
# shellcheck disable=SC2086
"$ANNOTATE" generate \
  --rag-responses "$REPORTS" \
  --rag-topics "$TOPICS" \
  --output "$OUT" \
  --dataset "$DATASET" \
  --show-documents \
  $TOPIC_SEL \
  --nugget-banks "$NUGGETS" \
  --grading-prompt "$GRADING_PROMPT" \
  $grades_arg

echo "wrote $OUT"
