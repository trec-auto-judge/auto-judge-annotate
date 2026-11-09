#!/usr/bin/env python3
"""Turn crucible rubric judgments into the annotator's --nugget-grades file.

grade-rag26-nov.sh writes <out>/rubric.judgments.jsonl, one record per graded unit:
  {run_id, topic_id, nugget, question, grade, judgments: {prompt: {grade, reasoning,
   confidence, extract?}}}
The annotator's --nugget-grades wants one flat record per (run, topic, nugget):
  {run_id, query_id, nugget_id, question, grade, reasoning, confidence, addressed_quote?}

The judgment dump stores the question text but not the bank nugget's id, so nugget_id
here is md5(question). That is not necessarily the id the annotator cards carry (a bank's
question_id is md5(question) only when the source left it unset). The annotator's generate
step reconciles each grade's nugget_id to the matching card by question text, so the id
written here just has to travel alongside the question. See generate_html.py
(_reconcile_grade_nugget_ids).

usage: judgments_to_nugget_grades.py JUDGMENTS.jsonl --out GRADES.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict


def _rubric_judgment(judgments: Any) -> Dict[str, Any]:
    """The rubric prompt's judgment dict from a record's per-prompt judgments."""
    if not isinstance(judgments, dict) or not judgments:
        return {}
    for key, val in judgments.items():
        if "rubric" in str(key).lower() and isinstance(val, dict):
            return val
    # --variant rubric stores a single prompt; fall back to the only/first dict.
    for val in judgments.values():
        if isinstance(val, dict):
            return val
    return {}


def convert(src: Path, out: Path) -> int:
    # Guard against src == out: opening the output "w" truncates it before the read can
    # consume it, which silently wipes the judgments file. Fail loudly instead.
    if src.resolve() == out.resolve():
        raise SystemExit(
            f"refusing to flatten {src} onto itself: --out must be a different file "
            f"from the judgments (the raw judgments and the flattened grades have "
            f"different schemas and cannot share a path)")
    n = 0
    with open(src, "r", encoding="utf-8") as fh, open(out, "w", encoding="utf-8") as w:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            question = rec.get("question", "")
            if not question:
                continue
            j = _rubric_judgment(rec.get("judgments"))
            grade = rec.get("grade")
            if not isinstance(grade, int):
                grade = j.get("grade") if isinstance(j.get("grade"), int) else 0
            out_rec: Dict[str, Any] = {
                "run_id": rec.get("run_id", ""),
                "query_id": rec.get("topic_id", ""),
                "nugget_id": hashlib.md5(question.encode()).hexdigest(),
                "question": question,
                "grade": grade,
                "reasoning": j.get("reasoning", ""),
                "confidence": j.get("confidence", 0.0),
            }
            extract = j.get("extract")
            if extract:
                out_rec["addressed_quote"] = extract
            w.write(json.dumps(out_rec, ensure_ascii=False) + "\n")
            n += 1
    print("wrote %d nugget grades -> %s" % (n, out))
    return n


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("judgments", type=Path, help="rubric.judgments.jsonl from the grading run")
    ap.add_argument("--out", required=True, type=Path, help="annotator --nugget-grades output")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    convert(args.judgments, args.out)


if __name__ == "__main__":
    main()
