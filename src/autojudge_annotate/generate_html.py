"""Generate a self-contained HTML annotation interface for AutoJudge reports."""

import json
from pathlib import Path
from typing import List

import click

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


@click.command("generate")
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
def generate(
    rag_responses: Path,
    rag_topics: Path,
    output: Path,
    dataset: str,
    show_documents: bool,
    topic: tuple,
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

    # Build data payload
    data = {
        "requests": _serialize_requests(requests),
        "reports": _serialize_reports(all_reports),
        "show_documents": show_documents,
        "dataset": dataset,
    }

    # Inject into template
    data_json = json.dumps(data, ensure_ascii=False, indent=None)
    html = HTML_TEMPLATE.replace("/* __DATA_PLACEHOLDER__ */ null", data_json)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    click.echo(f"Written annotation interface to {output}")


def main():
    generate()


if __name__ == "__main__":
    main()
