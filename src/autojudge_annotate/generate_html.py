"""Generate a self-contained HTML annotation interface for AutoJudge reports."""

import json
from pathlib import Path
from typing import Dict, List, Optional

import click

from autojudge_base.nugget_data import (
    NuggetBank,
    NuggetBanks,
    NuggetClaim,
    NuggetQuestion,
    load_nugget_banks_from_file,
)
from autojudge_base.report import Report, load_report
from autojudge_base.request import Request, load_requests_from_file

from autojudge_annotate.template import HTML_TEMPLATE


def _serialize_reports(reports: List[Report]) -> List[dict]:
    """Serialize reports to JSON-safe dicts with normalized sentences."""
    result = []
    for report in reports:
        sentences = report.get_sentences_with_citations()
        sentence_dicts = []
        for s in sentences:
            d = {"text": s.text}
            if s.citations:
                d["citations"] = s.citations
            sentence_dicts.append(d)

        doc_dict = {}
        if report.documents:
            for doc_id, doc in report.documents.items():
                doc_dict[doc_id] = {
                    "id": doc.id,
                    "text": doc.text,
                    "title": doc.title,
                    "url": doc.url,
                }

        result.append({
            "team_id": report.metadata.team_id,
            "run_id": report.metadata.run_id,
            "topic_id": report.metadata.topic_id,
            "sentences": sentence_dicts,
            "documents": doc_dict,
        })
    return result


def _serialize_requests(requests: List[Request]) -> List[dict]:
    """Serialize requests to JSON-safe dicts."""
    return [
        {
            "request_id": r.request_id,
            "title": r.title,
            "problem_statement": r.problem_statement,
            "background": r.background,
        }
        for r in requests
    ]


def _serialize_nugget_banks(nugget_banks: Optional[NuggetBanks]) -> Dict[str, dict]:
    """Serialize nugget banks to JSON-safe dict keyed by topic_id.

    Returns:
        Dict mapping topic_id -> {
            "nuggets": [{nugget_id, text, importance, quality, doc_ids}],
            "claims": [{claim_id, text, importance, quality, doc_ids}]
        }

    The doc_ids come from NuggetQuestion.references, indicating which
    documents satisfy the nugget (nugget-docs format).
    """
    if nugget_banks is None:
        return {}

    result: Dict[str, dict] = {}
    for topic_id, bank in nugget_banks.banks.items():
        nuggets = []
        claims = []

        # Serialize nugget questions
        if bank.nugget_bank:
            for question in bank.nugget_bank.values():
                doc_ids = []
                if question.references:
                    doc_ids = [ref.doc_id for ref in question.references]
                nuggets.append({
                    "nugget_id": question.question_id,
                    "text": question.question,
                    "importance": question.importance,
                    "quality": question.quality,
                    "doc_ids": doc_ids,
                })

        # Serialize nugget claims
        if bank.claim_bank:
            for claim in bank.claim_bank.values():
                doc_ids = []
                if claim.references:
                    doc_ids = [ref.doc_id for ref in claim.references]
                claims.append({
                    "claim_id": claim.claim_id,
                    "text": claim.claim,
                    "importance": claim.importance,
                    "quality": claim.quality,
                    "doc_ids": doc_ids,
                })

        result[topic_id] = {
            "nuggets": nuggets,
            "claims": claims,
        }

    return result


def _load_nugget_grades(path: Path) -> List[dict]:
    """Load nugget grades from JSONL file.

    Each line: {run_id, query_id, nugget_id, question, grade, reasoning, confidence, ...}
    """
    grades = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                grades.append(json.loads(line))
    return grades


def _serialize_nugget_grades(grades: List[dict]) -> Dict[str, Dict[str, Dict[str, dict]]]:
    """Serialize report-level nugget grades to nested dict.

    Input format (nugget-grades.jsonl for reports):
        {run_id, query_id, nugget_id, question, grade, reasoning, confidence}

    Returns:
        Dict[query_id][run_id][nugget_id] -> {grade, reasoning, confidence}
    """
    result: Dict[str, Dict[str, Dict[str, dict]]] = {}
    for g in grades:
        query_id = g.get("query_id", "")
        run_id = g.get("run_id", "")
        nugget_id = g.get("nugget_id", "")

        if not query_id or not run_id or not nugget_id:
            continue

        if query_id not in result:
            result[query_id] = {}
        if run_id not in result[query_id]:
            result[query_id][run_id] = {}

        result[query_id][run_id][nugget_id] = {
            "grade": g.get("grade", 0),
            "reasoning": g.get("reasoning", ""),
            "confidence": g.get("confidence", 0.0),
            "addressed_quote": g.get("addressed_quote"),
        }

    return result


def _serialize_doc_grades(grades: List[dict]) -> Dict[str, Dict[str, Dict[str, dict]]]:
    """Serialize document-level nugget grades to nested dict.

    Input format (nugget-doc-grades.jsonl):
        {run_id, query_id, nugget_id, question, passage, doc_id, paragraph_idx, grade, reasoning, confidence}

    Returns:
        Dict[query_id][doc_id][nugget_id] -> {
            "paragraphs": {
                "0": {grade, reasoning, confidence, passage},
                "1": {...},
            },
            "max_grade": int,  # max across all paragraphs for this doc
        }

    Note: doc_grades are keyed by (query_id, doc_id, nugget_id), not by run_id,
    since document content is the same across runs.
    """
    # First pass: collect all grades per (query, doc, nugget)
    temp: Dict[str, Dict[str, Dict[str, list]]] = {}
    for g in grades:
        query_id = g.get("query_id", "")
        doc_id = g.get("doc_id", "")
        nugget_id = g.get("nugget_id", "")

        if not query_id or not doc_id or not nugget_id:
            continue

        if query_id not in temp:
            temp[query_id] = {}
        if doc_id not in temp[query_id]:
            temp[query_id][doc_id] = {}
        if nugget_id not in temp[query_id][doc_id]:
            temp[query_id][doc_id][nugget_id] = []

        temp[query_id][doc_id][nugget_id].append(g)

    # Second pass: structure with paragraph indices
    result: Dict[str, Dict[str, Dict[str, dict]]] = {}
    for query_id, docs in temp.items():
        result[query_id] = {}
        for doc_id, nuggets in docs.items():
            result[query_id][doc_id] = {}
            for nugget_id, grade_list in nuggets.items():
                paragraphs: Dict[str, dict] = {}
                max_grade = 0
                for g in grade_list:
                    paragraph_idx = str(g.get("paragraph_idx", 0))
                    grade = g.get("grade", 0)
                    paragraphs[paragraph_idx] = {
                        "grade": grade,
                        "reasoning": g.get("reasoning", ""),
                        "confidence": g.get("confidence", 0.0),
                        "passage": g.get("passage", ""),
                        "addressed_quote": g.get("addressed_quote"),
                    }
                    if grade > max_grade:
                        max_grade = grade

                result[query_id][doc_id][nugget_id] = {
                    "paragraphs": paragraphs,
                    "max_grade": max_grade,
                }

    return result


def _extract_nuggets_from_grades(grades: List[dict], is_doc_grades: bool = False) -> Dict[str, Dict[str, dict]]:
    """Extract unique nuggets from grades file to build a nugget bank.

    Args:
        grades: List of grade entries
        is_doc_grades: If True, marks nuggets as has_doc_info=True (from doc grades file)
                       If False, marks nuggets as has_grades=True (from report grades file)

    Returns:
        Dict mapping query_id -> nugget_id -> {nugget_id, text, ..., has_grades/has_doc_info}
    """
    result: Dict[str, Dict[str, dict]] = {}

    for g in grades:
        query_id = g.get("query_id", "")
        nugget_id = g.get("nugget_id", "")
        question = g.get("question", "")

        if not query_id or not nugget_id:
            continue

        if query_id not in result:
            result[query_id] = {}

        # Only store if we haven't seen this nugget yet
        if nugget_id not in result[query_id]:
            result[query_id][nugget_id] = {
                "nugget_id": nugget_id,
                "text": question,
                "importance": None,
                "quality": None,
                "doc_ids": [],
                "has_grades": not is_doc_grades,
                "has_doc_info": is_doc_grades,
            }

    return result


def _serialize_nugget_banks_as_dict(nugget_banks: Optional[NuggetBanks]) -> Dict[str, Dict[str, dict]]:
    """Serialize nugget banks to nested dict keyed by topic_id -> nugget_id.

    Returns:
        Dict mapping topic_id -> nugget_id -> {nugget_id, text, ..., has_doc_info: bool}
    """
    if nugget_banks is None:
        return {}

    result: Dict[str, Dict[str, dict]] = {}
    for topic_id, bank in nugget_banks.banks.items():
        result[topic_id] = {}

        if bank.nugget_bank:
            for question in bank.nugget_bank.values():
                doc_ids = []
                if question.references:
                    doc_ids = [ref.doc_id for ref in question.references]
                # has_doc_info is True if we have doc_ids (nugget-docs format)
                has_doc_info = len(doc_ids) > 0
                result[topic_id][question.question_id] = {
                    "nugget_id": question.question_id,
                    "text": question.question,
                    "importance": question.importance,
                    "quality": question.quality,
                    "doc_ids": doc_ids,
                    "has_grades": False,
                    "has_doc_info": has_doc_info,
                }

        # Also add claims with claim_id as the key
        if bank.claim_bank:
            for claim in bank.claim_bank.values():
                doc_ids = []
                if claim.references:
                    doc_ids = [ref.doc_id for ref in claim.references]
                has_doc_info = len(doc_ids) > 0
                result[topic_id][claim.claim_id] = {
                    "nugget_id": claim.claim_id,  # Use nugget_id field for consistency
                    "text": claim.claim,
                    "importance": claim.importance,
                    "quality": claim.quality,
                    "doc_ids": doc_ids,
                    "has_grades": False,
                    "has_doc_info": has_doc_info,
                    "is_claim": True,
                }

    return result


def _convert_nugget_dict_to_list_format(nugget_dict: Dict[str, Dict[str, dict]]) -> Dict[str, dict]:
    """Convert dict-keyed nuggets back to list format for JS consumption.

    Returns:
        Dict mapping topic_id -> {"nuggets": [...], "claims": [...]}
    """
    result: Dict[str, dict] = {}
    for topic_id, nuggets in nugget_dict.items():
        nugget_list = []
        claim_list = []
        for nugget in nuggets.values():
            if nugget.get("is_claim"):
                # Remove the is_claim flag and rename nugget_id to claim_id
                claim = {k: v for k, v in nugget.items() if k != "is_claim"}
                claim["claim_id"] = claim.pop("nugget_id")
                claim_list.append(claim)
            else:
                nugget_list.append(nugget)
        result[topic_id] = {"nuggets": nugget_list, "claims": claim_list}
    return result


@click.group()
def cli():
    """AutoJudge annotation tools."""
    pass


@cli.command()
@click.option(
    "--rag-responses",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Directory containing report JSONL files",
)
@click.option(
    "--rag-topics",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="JSONL file with evaluation topics/requests",
)
@click.option(
    "--output",
    required=True,
    type=click.Path(path_type=Path),
    help="Output HTML file path",
)
@click.option(
    "--dataset",
    required=True,
    type=str,
    help="Freetext dataset label, included as-is in JSONL output",
)
@click.option(
    "--show-documents",
    is_flag=True,
    default=False,
    help="Enable citation document popups",
)
@click.option(
    "--topic",
    multiple=True,
    type=str,
    help="Filter to specific topic IDs (repeatable, e.g. --topic 1101 --topic 1102)",
)
@click.option(
    "--supabase-url",
    type=str,
    default=None,
    help="Supabase project URL for server sync",
)
@click.option(
    "--supabase-anon-key",
    type=str,
    default=None,
    help="Supabase anon key for server sync",
)
@click.option(
    "--nugget-banks",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Nugget banks file (JSONL) with nugget questions and doc references",
)
@click.option(
    "--nugget-grades",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Nugget grades file (JSONL) with per-report nugget grading results",
)
@click.option(
    "--doc-grades",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Document grades file (JSONL) with per-doc/paragraph nugget grading results",
)
def generate(
    rag_responses: Path,
    rag_topics: Path,
    output: Path,
    dataset: str,
    show_documents: bool,
    topic: tuple,
    supabase_url: str,
    supabase_anon_key: str,
    nugget_banks: Optional[Path],
    nugget_grades: Optional[Path],
    doc_grades: Optional[Path],
) -> None:
    """Generate an HTML annotation interface from reports and topics."""
    # Load requests
    requests = load_requests_from_file(rag_topics)
    if topic:
        topic_set = set(topic)
        requests = [r for r in requests if r.request_id in topic_set]
        click.echo(f"Filtered to {len(requests)} topics: {', '.join(sorted(topic_set))}")
    click.echo(f"Loaded {len(requests)} topics from {rag_topics}")

    # Load reports from all files in the directory (any extension, JSONL format)
    all_reports: List[Report] = []
    if rag_responses.is_dir():
        report_files = sorted(
            f for f in rag_responses.iterdir() if f.is_file()
        )
        for report_file in report_files:
            try:
                reports = load_report(report_file)
                all_reports.extend(reports)
                click.echo(f"  Loaded {len(reports)} reports from {report_file.name}")
            except Exception as e:
                click.echo(f"  Skipping {report_file.name}: {e}", err=True)
    else:
        all_reports = load_report(rag_responses)
        click.echo(f"  Loaded {len(all_reports)} reports from {rag_responses}")

    if topic:
        all_reports = [r for r in all_reports if r.metadata.topic_id in topic_set]
    click.echo(f"Total: {len(all_reports)} reports")

    # Validation: require at least one topic and one report
    if len(requests) == 0:
        raise click.ClickException("No topics loaded. Check --rag-topics path.")
    if len(all_reports) == 0:
        raise click.ClickException("No reports loaded. Check --rag-responses path.")

    # Count documents for warning
    total_docs = sum(
        len(r.documents) if r.documents else 0 for r in all_reports
    )
    if total_docs == 0:
        click.echo("Warning: No cited documents found in any report.", err=True)

    # Load nugget banks if provided
    loaded_nugget_banks: Optional[NuggetBanks] = None
    if nugget_banks:
        loaded_nugget_banks = load_nugget_banks_from_file(nugget_banks)
        total_nuggets = sum(
            len(b.nuggets_as_list()) for b in loaded_nugget_banks.banks.values()
        )
        click.echo(f"Loaded {total_nuggets} nuggets across {len(loaded_nugget_banks.banks)} topics from {nugget_banks}")

    # Load nugget grades if provided (report-level)
    serialized_grades: Dict[str, Dict[str, Dict[str, dict]]] = {}
    nuggets_from_grades: Dict[str, Dict[str, dict]] = {}
    if nugget_grades:
        raw_grades = _load_nugget_grades(nugget_grades)
        serialized_grades = _serialize_nugget_grades(raw_grades)
        nuggets_from_grades = _extract_nuggets_from_grades(raw_grades)
        total_grades = len(raw_grades)
        num_runs = sum(len(runs) for runs in serialized_grades.values())
        click.echo(f"Loaded {total_grades} nugget grades across {num_runs} run/topic combinations from {nugget_grades}")

    # Load doc grades if provided (document-level)
    serialized_doc_grades: Dict[str, Dict[str, Dict[str, dict]]] = {}
    nuggets_from_doc_grades: Dict[str, Dict[str, dict]] = {}
    if doc_grades:
        raw_doc_grades = _load_nugget_grades(doc_grades)  # same JSONL loading
        serialized_doc_grades = _serialize_doc_grades(raw_doc_grades)
        nuggets_from_doc_grades = _extract_nuggets_from_grades(raw_doc_grades, is_doc_grades=True)
        total_doc_grades = len(raw_doc_grades)
        num_docs = sum(len(docs) for docs in serialized_doc_grades.values())
        click.echo(f"Loaded {total_doc_grades} doc grades across {num_docs} doc/topic combinations from {doc_grades}")

    # Merge nugget banks: union of nuggets from all sources (dict-based merge)
    # Priority: nugget_banks > report grades > doc grades (last one sets flags correctly)
    merged_nuggets: Dict[str, Dict[str, dict]] = {}
    # 1. Start with doc grades nuggets (has_doc_info=True)
    for topic_id, nuggets in nuggets_from_doc_grades.items():
        merged_nuggets.setdefault(topic_id, {}).update(nuggets)
    # 2. Merge report grades nuggets (has_grades=True, overwrites doc grades flags)
    for topic_id, nuggets in nuggets_from_grades.items():
        for nid, nugget in nuggets.items():
            if topic_id in merged_nuggets and nid in merged_nuggets[topic_id]:
                # Merge flags: keep has_doc_info if already set
                nugget["has_doc_info"] = merged_nuggets[topic_id][nid].get("has_doc_info", False)
            merged_nuggets.setdefault(topic_id, {})[nid] = nugget
    # 3. Merge nugget banks (highest priority, may have additional metadata)
    bank_nuggets = _serialize_nugget_banks_as_dict(loaded_nugget_banks)
    for topic_id, nuggets in bank_nuggets.items():
        merged_nuggets.setdefault(topic_id, {}).update(nuggets)

    # Convert to list format for JS
    final_nugget_banks = _convert_nugget_dict_to_list_format(merged_nuggets)
    total_final = sum(len(b["nuggets"]) + len(b["claims"]) for b in final_nugget_banks.values())
    if total_final > 0:
        click.echo(f"Final nugget bank: {total_final} nuggets across {len(final_nugget_banks)} topics")

    # Build data payload
    data = {
        "requests": _serialize_requests(requests),
        "reports": _serialize_reports(all_reports),
        "nugget_banks": final_nugget_banks,
        "nugget_grades": serialized_grades,
        "doc_grades": serialized_doc_grades,
        "show_documents": show_documents,
        "dataset": dataset,
        "supabase_url": supabase_url or "",
        "supabase_anon_key": supabase_anon_key or "",
    }

    # Inject into template
    data_json = json.dumps(data, ensure_ascii=False, indent=None)
    html = HTML_TEMPLATE.replace("/* __DATA_PLACEHOLDER__ */ null", data_json)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    click.echo(f"Written annotation interface to {output}")



_INIT_DB_SQL = """\
CREATE TABLE IF NOT EXISTS annotations_current (
    dataset TEXT NOT NULL,
    username TEXT NOT NULL,
    annotation_key TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (dataset, username, annotation_key)
);

ALTER TABLE annotations_current ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'annotations_current' AND policyname = 'Allow all for anon'
    ) THEN
        CREATE POLICY "Allow all for anon"
            ON annotations_current FOR ALL
            USING (true) WITH CHECK (true);
    END IF;
END $$;

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_updated_at ON annotations_current;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON annotations_current
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
"""


@cli.command("init-db")
def init_db() -> None:
    """Print instructions for creating the annotations table in Supabase."""
    click.echo("To set up the annotations database, run the following SQL in the")
    click.echo("Supabase dashboard (SQL Editor > New query > paste > Run):\n")
    click.echo("------------------------------\n")
    click.echo(_INIT_DB_SQL)
    click.echo("------------------------------\n")
    click.echo("After running the SQL, verify by checking Table Editor > annotations_current.")


@cli.command("export-db")
@click.option("--supabase-url", required=True, type=str,
              help="Supabase project URL (e.g. https://xyz.supabase.co)")
@click.option("--supabase-anon-key", required=True, type=str,
              help="Supabase anon key")
@click.option("--dataset", type=str, default=None,
              help="Filter by dataset name (exports all datasets if omitted)")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output JSONL file (default: stdout)")
def export_db(supabase_url: str, supabase_anon_key: str,
              dataset: str | None, output: str | None) -> None:
    """Export annotations from Supabase as JSONL."""
    import urllib.error
    import urllib.parse
    import urllib.request

    base = f"{supabase_url.rstrip('/')}/rest/v1/annotations_current"
    params = {"select": "*", "order": "created_at.asc"}
    if dataset:
        params["dataset"] = f"eq.{dataset}"
    url = f"{base}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={
        "apikey": supabase_anon_key,
        "Authorization": f"Bearer {supabase_anon_key}",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            rows = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        click.echo(f"HTTP {e.code} {e.reason}", err=True)
        raise SystemExit(1)

    if not rows:
        click.echo("No annotations found.", err=True)
        return

    lines = []
    for row in rows:
        # Merge payload fields into top-level, keep metadata
        record = row.get("payload", {})
        record["dataset"] = row["dataset"]
        record["username"] = row["username"]
        record["annotation_key"] = row["annotation_key"]
        record["created_at"] = row.get("created_at")
        record["updated_at"] = row.get("updated_at")
        lines.append(json.dumps(record, ensure_ascii=False))

    text = "\n".join(lines) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
        click.echo(f"Exported {len(rows)} annotations to {output}", err=True)
    else:
        click.echo(text, nl=False)


def main():
    cli()


if __name__ == "__main__":
    main()
