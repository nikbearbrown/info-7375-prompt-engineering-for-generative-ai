"""Sampling report (Chapter 1): the five §13 postings, n fresh calls each (PLAN §6.1).

* Prompt v1, the same file and digest as the pipeline.
* Calls go round-robin (posting 1..5, then again) so no posting's calls cluster in
  time. Each is a separate CLI process with ``--no-session-persistence``; there are
  no retries, so every reply scored is a first reply.
* One sampling study: outputs live at fixed paths under
  ``data/experiments/sampling/`` and ``run`` refuses if it has already started. The
  manifest is rewritten after every call with ``"complete": false`` (``true`` only
  at the end), so a crash keeps the calls made and ``table`` reports them, marked
  as an incomplete study.
* ``table`` refuses to report if two calls share a session ID, the evidence that
  each conversation was fresh. Calls without a session ID (failed spawns) are counted
  and reported.

Headline phrasing: repeatable is not correct. A unanimous wrong label is called out;
a posting whose every reply was INVALID is a format or outage case, not a wrong label.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict

from job_search_agent.experiments._calls import CallRecord, JudgeCall
from job_search_agent.experiments._io import (
    STUDENT_MARKER,
    ExperimentContext,
    ExperimentError,
    is_complete,
    read_json,
    record_calls,
)
from job_search_agent.experiments.metrics import INVALID, Rate, outcome, rate
from job_search_agent.experiments.selection import HANDCHECK_IDS
from job_search_agent.judge.prompt import PromptContract
from job_search_agent.models import Posting, VerdictLabel

OUT = "experiments/sampling"
MANIFEST = f"{OUT}/manifest.json"
SPREAD = f"{OUT}/spread.json"
TABLES = f"{OUT}/SAMPLING.tables.md"
HAND_LABELS_REL = "experiments/sampling/hand_labels.json"


class _Out(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SampledCall(_Out):
    """One manifest entry."""

    k: int
    call: CallRecord


def call_order(n: int, ids: Sequence[str] = HANDCHECK_IDS) -> list[tuple[int, str]]:
    """Returns the round-robin call order ``[(k, posting_id), ...]``.

    Args:
        n: Calls per posting (``k`` runs from 1 to ``n``).
        ids: Postings in contract order.

    Returns:
        ``n * len(ids)`` pairs: all postings for k=1, then k=2, ...

    Raises:
        ExperimentError: If ``n < 1``.
    """
    if n < 1:
        raise ExperimentError("--n must be at least 1")
    return [(k, pid) for k in range(1, n + 1) for pid in ids]


def cmd_sampling_run(
    ctx: ExperimentContext,
    *,
    n: int,
    postings: Mapping[str, Posting],
    prompt: PromptContract,
    judge_call: JudgeCall,
    model_requested: str | None,
) -> dict[str, Any]:
    """Makes ``n`` fresh first-reply calls for each §13 posting.

    Args:
        ctx: Shared dependencies.
        n: Calls per posting.
        postings: Postings of the hand-check raw file by ID.
        prompt: Prompt v1.
        judge_call: One call with ``retry_once=False``.
        model_requested: The pinned model ID.

    Returns:
        The manifest.

    Raises:
        ExperimentError: If sampling has already started, the prompt is not v1, or a
            §13 posting is missing.
    """
    if ctx.data_exists(MANIFEST):
        raise ExperimentError("sampling has already run; it runs once only")
    if prompt.version != "v1":
        raise ExperimentError("sampling uses prompt v1 only")
    missing = [pid for pid in HANDCHECK_IDS if pid not in postings]
    if missing:
        raise ExperimentError("§13 postings missing from source: " + ", ".join(missing))
    started = {
        "prompt_id": prompt.prompt_id,
        "prompt_sha256": prompt.sha256,
        "model_requested": model_requested,
        "n_per_posting": n,
        "posting_ids": list(HANDCHECK_IDS),
        "started_at_utc": ctx.clock.now_utc().isoformat(),
        "code_commit": ctx.git.head(),
        "code_dirty": ctx.git.is_dirty(),
    }

    def call(k: int, pid: str) -> Callable[[], dict[str, Any]]:
        def make() -> dict[str, Any]:
            record = judge_call(postings[pid], prompt, f"{OUT}/calls/{pid}/{k}")
            return SampledCall(k=k, call=record).model_dump(mode="json")

        return make

    return record_calls(
        ctx, MANIFEST, started, (call(k, pid) for k, pid in call_order(n))
    )


def check_distinct_sessions(calls: Sequence[CallRecord]) -> int:
    """Verifies that no two calls share a session ID.

    Args:
        calls: Every sampled call.

    Returns:
        How many calls have no session ID at all.

    Raises:
        ExperimentError: If a session ID repeats (conversations were not fresh).
    """
    ids = [c.session_id for c in calls if c.session_id is not None]
    repeated = sorted(s for s, count in Counter(ids).items() if count > 1)
    if repeated:
        raise ExperimentError(
            f"{len(repeated)} session ID(s) repeat; refusing to report"
        )
    return sum(1 for c in calls if c.session_id is None)


class PostingSpread(_Out):
    """One row of the spread table."""

    posting_id: str
    hand_label: VerdictLabel
    n: int
    relevant: int
    not_relevant: int
    invalid: int
    modal_outcome: str
    unanimous: bool
    agreement_with_hand: Rate
    """k/n where an invalid reply counts as a disagreement."""
    unanimous_and_wrong: bool
    """Every reply gave the same label and it disagrees with the hand label."""
    all_invalid: bool
    """Every reply was INVALID: a format or outage case, not a wrong label."""
    distinct_evidence_path_sets: int
    """Distinct sets of ``(resume_path, posting_path)`` pairs among valid replies."""
    format_acceptance: Rate


def spread_table(
    calls: Sequence[CallRecord], hand: Mapping[str, VerdictLabel]
) -> list[PostingSpread]:
    """Builds the per-posting spread rows (pure).

    Args:
        calls: Every sampled call.
        hand: Hand label per posting ID (the §13 verdicts).

    Returns:
        One row per posting in ``HANDCHECK_IDS`` order (only postings with calls).
    """
    rows: list[PostingSpread] = []
    for pid in HANDCHECK_IDS:
        mine = [c for c in calls if c.posting_id == pid]
        if not mine:
            continue
        outcomes = [outcome(c) for c in mine]
        counts = Counter(outcomes)
        top = max(counts.values())
        modal = sorted(o for o, c in counts.items() if c == top)
        unanimous = len(counts) == 1
        all_invalid = set(counts) == {INVALID}
        agree = sum(1 for o in outcomes if o == hand[pid].value)
        path_sets = {
            frozenset((p[0], p[1]) for p in c.evidence_paths)
            for c in mine
            if c.first_reply_valid
        }
        rows.append(
            PostingSpread(
                posting_id=pid,
                hand_label=hand[pid],
                n=len(mine),
                relevant=counts.get("MATCH", 0),
                not_relevant=counts.get("NO_MATCH", 0),
                invalid=counts.get(INVALID, 0),
                modal_outcome="/".join(modal),
                unanimous=unanimous,
                agreement_with_hand=rate(agree, len(mine)),
                unanimous_and_wrong=unanimous and agree == 0 and not all_invalid,
                all_invalid=all_invalid,
                distinct_evidence_path_sets=len(path_sets),
                format_acceptance=rate(
                    sum(1 for c in mine if c.first_reply_valid), len(mine)
                ),
            )
        )
    return rows


def load_hand_labels(ctx: ExperimentContext) -> tuple[dict[str, VerdictLabel], Any]:
    """Reads ``experiments/sampling/hand_labels.json``.

    Returns:
        ``(labels by ID, confirmed_by_student value)``.

    Raises:
        ExperimentError: If the file is malformed or lacks a §13 posting.
    """
    doc = read_json(ctx.reader, HAND_LABELS_REL)
    try:
        labels = {
            pid: VerdictLabel(doc["labels"][pid]["hand_label"]) for pid in HANDCHECK_IDS
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ExperimentError(f"{HAND_LABELS_REL} is malformed") from exc
    return labels, doc.get("confirmed_by_student")


def cmd_sampling_table(ctx: ExperimentContext) -> dict[str, Any]:
    """Writes ``spread.json`` and ``SAMPLING.tables.md`` from the manifest.

    An incomplete manifest (the run stopped early) is reported, marked
    ``"complete": false`` with the planned and made call counts.

    Args:
        ctx: Shared dependencies.

    Returns:
        The spread document.

    Raises:
        ExperimentError: If there is no manifest or session IDs repeat.
    """
    if not ctx.data_exists(MANIFEST):
        raise ExperimentError("no sampling manifest; run `jsa exp sampling run` first")
    manifest = ctx.read_data_json(MANIFEST)
    calls = [SampledCall.model_validate(c).call for c in manifest["calls"]]
    no_session = check_distinct_sessions(calls)
    hand, confirmed = load_hand_labels(ctx)
    rows = spread_table(calls, hand)
    doc = {
        "generated_at_utc": ctx.clock.now_utc().isoformat(),
        "prompt_id": manifest["prompt_id"],
        "prompt_sha256": manifest["prompt_sha256"],
        "model_requested": manifest["model_requested"],
        "models_served": sorted({m for c in calls for m in c.model_served}),
        "n_per_posting": manifest["n_per_posting"],
        "complete": is_complete(manifest),
        "calls_planned": manifest["n_per_posting"] * len(manifest["posting_ids"]),
        "calls_total": len(calls),
        "calls_without_session_id": no_session,
        "session_ids_distinct": True,
        "hand_labels_confirmed_by_student": confirmed,
        "rows": [r.model_dump(mode="json") for r in rows],
    }
    ctx.writer.write_json_atomic(SPREAD, doc)
    ctx.writer.write_bytes_atomic(TABLES, render_tables(doc).encode("utf-8"))
    return doc


def render_tables(doc: Mapping[str, Any]) -> str:
    """Renders the generated tables for ``docs/experiments/SAMPLING.md``.

    Args:
        doc: The ``spread.json`` content.

    Returns:
        Markdown; the conclusion is left to the student.
    """
    confirmed = doc["hand_labels_confirmed_by_student"]
    incomplete = (
        []
        if doc["complete"]
        else [
            f"**INCOMPLETE STUDY:** the run stopped after {doc['calls_total']} of "
            f"{doc['calls_planned']} planned calls; these tables describe only the "
            "calls made.",
            "",
        ]
    )
    lines = [
        "# Sampling report: generated tables",
        "",
        *incomplete,
        "**Repeatable is not correct.** A label Claude gives every time can still "
        "disagree with the hand label; such rows are marked *unanimous and wrong*.",
        "",
        f"Prompt `{doc['prompt_id']}` (sha256 `{doc['prompt_sha256'][:16]}…`), model "
        f"requested `{doc['model_requested']}`, served "
        f"{', '.join(f'`{m}`' for m in doc['models_served']) or '(none)'}. "
        f"{doc['calls_total']} calls, {doc['n_per_posting']} per posting, first reply "
        "only, every session ID distinct "
        f"({doc['calls_without_session_id']} call(s) had no session ID).",
        "",
        "Hand labels are the CONTRACT.md §13 verdicts"
        + (
            "; not yet confirmed by the student."
            if confirmed is None
            else f"; confirmed by the student: {confirmed}."
        ),
        "",
        "| Posting | Hand | n | RELEVANT | NOT_RELEVANT | INVALID | Modal | "
        "Unanimous | Agreement k/n | Distinct evidence-path sets | "
        "First-reply format acceptance |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    wrong: list[str] = []
    all_invalid: list[str] = []
    for row in doc["rows"]:
        agreement = row["agreement_with_hand"]
        accepted = row["format_acceptance"]
        unanimous = "yes" if row["unanimous"] else "no"
        if row["unanimous_and_wrong"]:
            unanimous = "yes (unanimous and wrong)"
            wrong.append(row["posting_id"])
        if row["all_invalid"]:
            unanimous = "yes (all INVALID: format or outage)"
            all_invalid.append(row["posting_id"])
        lines.append(
            f"| {row['posting_id']} | {row['hand_label']} | {row['n']} | "
            f"{row['relevant']} | {row['not_relevant']} | {row['invalid']} | "
            f"{row['modal_outcome']} | {unanimous} | "
            f"{agreement['k']}/{agreement['n']} | "
            f"{row['distinct_evidence_path_sets']} | "
            f"{accepted['k']}/{accepted['n']} |"
        )
    lines += [
        "",
        "Unanimous and wrong: " + (", ".join(wrong) if wrong else "none") + ".",
        "",
        "All replies INVALID (a format or outage case, not a wrong label): "
        + (", ".join(all_invalid) if all_invalid else "none")
        + ".",
        "",
        "## Conclusion",
        "",
        STUDENT_MARKER,
        "",
    ]
    return "\n".join(lines)
