"""Human-readable renderings of a run: ``report.md``, terminal summary, RUNS table.

Everything here is pure text built from ``RunReport`` and ``OutputRecord`` values.
What is shown is limited on purpose (CONTRACT §12, A24):

* posting IDs, titles and locations (public board data), rule labels and failed gates,
  judgment status and label, and counts;
* Claude's label is always tagged as an opinion; Claude's free text (``summary``,
  evidence ``reason``) and every résumé value are never shown.

A seeded run starts with the PLAN §4 banner in both ``report.md`` and the terminal.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from job_search_agent.models import OutputRecord, RunReport

OPINION_TAG = "Claude opinion"


def seeded_banner(report: RunReport) -> str | None:
    """Returns the seeded-run banner line, or ``None`` for a live run.

    Args:
        report: The run report.

    Returns:
        ``> SEEDED RUN — replayed from saved file <path> (sha256 <hex>, originally
        fetched <ts>). No network request was made.``
    """
    if not report.seeded:
        return None
    ref = report.raw_evidence
    path = ref.path if ref else "<unknown>"
    digest = ref.sha256 if ref else "<unknown>"
    fetched = (
        report.original_fetched_at_utc.isoformat()
        if report.original_fetched_at_utc
        else "<unknown>"
    )
    return (
        f"> SEEDED RUN — replayed from saved file {path} (sha256 {digest}, "
        f"originally fetched {fetched}). No network request was made."
    )


def _count(value: int | None) -> str:
    return "n/a" if value is None else str(value)


def _judgment_text(record: OutputRecord) -> str:
    judgment = record.model_judgment
    if judgment.label is None:
        return f"{OPINION_TAG}: {judgment.status.value}"
    return f"{OPINION_TAG}: {judgment.status.value} {judgment.label}"


def _gates_text(record: OutputRecord) -> str:
    gates = record.rule_verdict.failed_gates
    return ",".join(g.value for g in gates) if gates else "-"


def _md_cell(text: str | None) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ")


def _record_rows(records: Sequence[OutputRecord]) -> list[str]:
    rows = [
        "| posting_id | title | location | rule | failed gates | "
        f"{OPINION_TAG} | rule evidence ok |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in records:
        rows.append(
            f"| {r.posting_id} | {_md_cell(r.title)} | {_md_cell(r.location)} | "
            f"{r.rule_verdict.label.value} | {_gates_text(r)} | "
            f"{_judgment_text(r).removeprefix(OPINION_TAG + ': ')} | "
            f"{'yes' if not r.rule_evidence_errors else 'NO'} |"
        )
    return rows


def render_markdown(
    report: RunReport,
    records: Sequence[OutputRecord],
    retried: Sequence[OutputRecord],
) -> str:
    """Renders ``report.md``.

    Args:
        report: The run report.
        records: Records for new postings.
        retried: Records for retried pending postings.

    Returns:
        Markdown text ending in a newline; for a seeded run the first line is the
        seeded banner.
    """
    lines: list[str] = []
    banner = seeded_banner(report)
    if banner:
        lines += [banner, ""]
    lines += [
        f"# Run {report.run_id}",
        "",
        f"- Status: **{report.status.value}**",
        f"- Mode: {report.mode.value} (seeded: {str(report.seeded).lower()})",
        f"- Board: {report.provider}/{report.board}",
        f"- Started (UTC): {report.started_at_utc.isoformat()}",
        f"- Started (ET): {report.started_at_et.isoformat()}",
        f"- Finished (UTC): {report.finished_at_utc.isoformat()}",
        f"- Fetched postings: {_count(report.fetched_count)}",
        f"- Unique valid IDs: {_count(report.unique_valid_ids)}",
        f"- New postings: {report.new_count}",
        f"- Retried pending: {len(report.retried_pending_ids)}",
        f"- Still pending: {len(report.unresolved_pending_ids)}",
        f"- Records saved: {str(report.records_saved).lower()}",
        f"- State saved: {str(report.state_saved).lower()}",
        f"- Code: {report.code_commit or 'unknown'}"
        f" (dirty: {'unknown' if report.code_dirty is None else report.code_dirty})",
        f"- Model backend: {report.model_backend}"
        + (f" ({report.model_id})" if report.model_id else ""),
    ]
    if report.raw_evidence:
        lines.append(
            f"- Raw evidence: {report.raw_evidence.path} "
            f"(sha256 {report.raw_evidence.sha256})"
        )
    if report.fetch_error:
        status = f", HTTP {report.http_status}" if report.http_status else ""
        lines.append(f"- Fetch error: {report.fetch_error.value}{status}")
    if report.judgment_counts:
        counts = ", ".join(
            f"{k.value}={v}" for k, v in sorted(report.judgment_counts.items())
        )
        lines.append(f"- Judgments ({OPINION_TAG}): {counts}")
    if report.data_quality_issues:
        lines.append(f"- Data-quality issues: {len(report.data_quality_issues)}")
    if report.notes:
        lines.append(f"- Notes: {', '.join(report.notes)}")
    if report.status.value == "BASELINE":
        lines += [
            "",
            "Baseline: every valid ID was stored as seen; no posting was judged "
            "(new_count is 0 by definition).",
        ]
    for heading, recs in (("New postings", records), ("Retried pending", retried)):
        if recs:
            lines += ["", f"## {heading}", "", *_record_rows(recs)]
    lines += [
        "",
        f"The {OPINION_TAG} column is Claude's judgment: an opinion based on the "
        "supplied text, not a fact or an employer decision.",
    ]
    return "\n".join(lines) + "\n"


def render_terminal(
    report: RunReport,
    records: Sequence[OutputRecord],
    retried: Sequence[OutputRecord],
) -> str:
    """Renders the privacy-safe terminal summary.

    Args:
        report: The run report.
        records: Records for new postings.
        retried: Records for retried pending postings.

    Returns:
        Plain text; the seeded banner comes first for a seeded run.
    """
    lines: list[str] = []
    banner = seeded_banner(report)
    if banner:
        lines.append(banner)
    lines.append(f"jsa run {report.run_id}: {report.status.value}")
    lines.append(
        f"  fetched={_count(report.fetched_count)} "
        f"unique_valid_ids={_count(report.unique_valid_ids)} "
        f"new={report.new_count} retried={len(report.retried_pending_ids)} "
        f"pending={len(report.unresolved_pending_ids)} "
        f"state_saved={str(report.state_saved).lower()}"
    )
    if report.fetch_error:
        lines.append(f"  fetch_error={report.fetch_error.value}")
    if report.notes:
        lines.append(f"  notes={','.join(report.notes)}")
    for tag, recs in (("new", records), ("retried", retried)):
        for r in recs:
            lines.append(
                f"  [{tag}] {r.posting_id} {r.title!r} "
                f"rule={r.rule_verdict.label.value} failed={_gates_text(r)} "
                f"| {_judgment_text(r)}"
            )
    return "\n".join(lines) + "\n"


def render_runs_markdown(reports: Iterable[RunReport]) -> str:
    """Renders ``docs/RUNS.md`` with separate live and seeded tables (PLAN §4).

    Args:
        reports: Every ``report.json`` found, in any order.

    Returns:
        Markdown text.
    """
    ordered = sorted(reports, key=lambda r: r.started_at_utc)
    header = [
        "| run_id | started (ET) | status | fetched | unique IDs | new | "
        "state saved | code |",
        "|---|---|---|---|---|---|---|---|",
    ]

    def rows(seeded: bool) -> list[str]:
        out = list(header)
        for r in ordered:
            if r.seeded is seeded:
                out.append(
                    f"| {r.run_id} | {r.started_at_et.isoformat()} | "
                    f"{r.status.value} | {_count(r.fetched_count)} | "
                    f"{_count(r.unique_valid_ids)} | {r.new_count} | "
                    f"{str(r.state_saved).lower()} | "
                    f"{(r.code_commit or 'unknown')[:12]}"
                    f"{'+dirty' if r.code_dirty else ''} |"
                )
        if len(out) == len(header):
            out.append("| (none) | | | | | | | |")
        return out

    lines = [
        "# Runs",
        "",
        "Generated from `report.json` files by `jsa docs render`.",
        "",
        "## Live runs",
        "",
        *rows(False),
        "",
        "## Seeded runs (replayed from saved files; no network request)",
        "",
        *rows(True),
    ]
    return "\n".join(lines) + "\n"
