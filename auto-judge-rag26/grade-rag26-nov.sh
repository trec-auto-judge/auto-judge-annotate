#!/usr/bin/env bash
# =============================================================================
# Pre-grade all rag26 systems for the rag26-nov annotator.
# Documented before launch per the rule.
#
#   setup     uv sync   (in this directory, once) -- builds .venv with autojudge-annotate
#             + trec2026-unh and their local deps; no other project's venv is borrowed.
#   what      grade every rag26 generation run against the MERGED rag26-nov nugget bank
#             (the per-topic union of all judges' banks, four topics), with our
#             submission's RUBRIC prompt only. Uses our judge-only workflow
#             (rag26-nov-judge.workflow.yml), which reuses the production CrucibleJudge;
#             bank_label there is "merged" (the union bank has no used/should/vital cut).
#   topics    restricted implicitly to the four topics in the merged bank (the judge
#             only grades topics the bank contains). Build the bank first with
#             make-rag26-nov-annotator.sh (the merge step) in this directory.
#   endpoint  the fresh-cache minima proxy on :2026 (OpenRouter upstream, gpt-oss-120b,
#             a brand-new cache for this run); override OPENAI_BASE_URL/OPENAI_MODEL to
#             change it. No CACHE_DIR on the client -- the proxy owns the cache.
#   outputs   $OUT/rubric.judgments.jsonl (+ rubric.eval.txt, rubric.run.log), beside
#             this script; make-rag26-nov-annotator.sh flattens the judgments for the UI.
#   volume    all runs x 4 topics x (union nuggets/topic) rubric calls -- the merged bank
#             is a union across judges, so this can be large. Check it before launching.
# =============================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/../.."                            # auto-judge-code-test

# Binaries from this project's own venv (uv sync), falling back to PATH.
PY="${PY:-$HERE/.venv/bin/python}"; [ -x "$PY" ] || PY="python"
AUTOJUDGE="${AUTOJUDGE:-$HERE/.venv/bin/auto-judge}"; [ -x "$AUTOJUDGE" ] || AUTOJUDGE="auto-judge"
# Our judge-only workflow (reuses the production CrucibleJudge class; grading only). It
# still needs trec2026 importable for that class, which `uv sync` provides.
WORKFLOW="${WORKFLOW:-$HERE/rag26-nov-judge.workflow.yml}"
echo "WORKFLOW for grading: $WORKFLOW"

NUGGETS="${NUGGETS:-$HERE/rag26-nov-nuggets.jsonl}"
DATA="${DATA:-$ROOT/datasets/rag26}"
REPORTS="${REPORTS:-$DATA/runs/generation/}"
TOPICS="${TOPICS:-$DATA/topics/trec_rag_2026_queries.jsonl}"
OUT="${OUT:-$HERE/rag26-nov-grades}"

export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://localhost:2026/v1}"
export OPENAI_MODEL="${OPENAI_MODEL:-openai/gpt-oss-120b}"
export PYTHONUNBUFFERED=1
export MAX_ATTEMPTS="${MAX_ATTEMPTS:-0}"      # retry forever (self-heals an endpoint stall)
# Flow control: modest concurrency, polite to the live endpoint. Raise only if the
# proxy / OpenRouter can take it.
export BATCH_NUM_WORKERS="${BATCH_NUM_WORKERS:-64}"
export MAX_OUTSTANDING="${MAX_OUTSTANDING:-64}"
export TIMEOUT_S="${TIMEOUT_S:-1200}"
unset MINIMA_DEBUG MINIMA_TRACE_FILE CACHE_DIR CACHE_FORCE_REFRESH || true
# nltk >= 3.10 refuses a group/other-writable data dir (the env flag no longer helps);
# make the existing data private so the judge's text chunker can load punkt/stopwords.
[ -d "$HOME/nltk_data" ] && chmod -R go-w "$HOME/nltk_data"

[ -f "$NUGGETS" ] || { echo "merged bank not found: $NUGGETS (run make-rag26-nov-annotator.sh first)" >&2; exit 1; }
mkdir -p "$OUT"
echo "=== rag26-nov GRADE START $(date -Is)  endpoint=$OPENAI_BASE_URL ==="
# tee so minima-llm's batch progress (done=/sent=/recv=/eta=/tok=, printed by default)
# streams to the terminal and is still captured in the log. pipefail keeps auto-judge's
# exit status as the pipeline's, so the if below still catches a failed run.
if "$AUTOJUDGE" run --workflow "$WORKFLOW" \
    --variant rubric \
    --rag-responses "$REPORTS" --rag-topics "$TOPICS" \
    --nugget-banks "$NUGGETS" \
    --out-dir "$OUT/" 2>&1 | tee "$OUT/rubric.run.log"; then
  echo "=== rag26-nov GRADE DONE $(date -Is) -> $OUT/rubric.judgments.jsonl ==="
else
  echo "=== rag26-nov GRADE FAILED $(date -Is) (see $OUT/rubric.run.log) ===" >&2
  exit 1
fi
