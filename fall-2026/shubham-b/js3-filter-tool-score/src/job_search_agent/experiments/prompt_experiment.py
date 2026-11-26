"""Prompt experiment (Chapter 2): select, seal, run, freeze, score (PLAN §6.2).

Command order, each step checked against git through ``GitInspector``:

1. ``select`` — refuses if a selection exists or ``PROCEDURE.md`` is not committed.
2. The student fills ``experiments/prompt/labels/{dev,heldout}.labels.json``.
3. ``seal`` — validates all labels and writes ``SEAL.json``. The student commits the
   labels and SEAL before any model call.
4. ``run --prompt v1 --set dev`` — refuses unless SEAL is committed and its hashes
   match. Each (prompt, set) cell runs once only; its ``results.json`` is rewritten
   after every call with ``"complete": false`` (``true`` only at the end).
5. The student writes ``prompts/judge.v2.md`` (one section changed).
6. ``freeze`` — needs the v1 dev results and a one-section diff; writes
   ``FREEZE.json``, which must be committed.
7. ``run --prompt v2 --set dev`` — refuses unless FREEZE is committed.
8. ``run --prompt v1|v2 --set heldout`` — refuses unless FREEZE is committed, the
   prompt hashes equal FREEZE, both dev cells exist, and this cell has not run.
9. ``score`` — re-verifies SEAL, reveals the strata, writes ``metrics.json`` and the
   tables. A cell that stopped early is scored on the calls it made and marked
   incomplete.

Outputs live under ``data/experiments/prompt/`` (data-relative
``experiments/prompt/``); the human-authored inputs live under ``experiments/prompt/``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from job_search_agent.experiments._calls import CallRecord, JudgeCall
from job_search_agent.experiments._io import (
    STUDENT_MARKER,
    ExperimentContext,
    ExperimentError,
    file_sha256,
    is_complete,
    read_json,
    record_calls,
)
from job_search_agent.experiments.metrics import (
    discordant,
    rule_vs_hand_audit,
    score_cell,
)
from job_search_agent.experiments.selection import (
    QUOTAS,
    SEED,
    SETS,
    STRATUM_DEFINITIONS,
    Evaluate,
    LabelFile,
    label_template,
    render_worksheet,
    select_postings,
    validate_label_file,
)
from job_search_agent.judge.prompt import PromptContract, changed_sections
from job_search_agent.models import Posting, VerdictLabel
from job_search_agent.sources import meta_path_for, sha256_hex

OUT = "experiments/prompt"
"""Data-relative output directory."""

PROCEDURE_REL = "experiments/prompt/PROCEDURE.md"
HANDCHECK_RAW_REL = "evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.json"
HANDCHECK_META_REL = meta_path_for(Path(HANDCHECK_RAW_REL)).as_posix()
"""The committed meta file whose ``sha256`` pins the hand-check raw bytes."""

PROMPTS: tuple[str, ...] = ("v1", "v2")
SAMPLING_MANIFEST = "experiments/sampling/manifest.json"

SELECTION = f"{OUT}/selection.json"
STRATA_FILE = f"{OUT}/strata.json"
SEAL = f"{OUT}/SEAL.json"
FREEZE = f"{OUT}/FREEZE.json"
METRICS = f"{OUT}/metrics.json"
TABLES = f"{OUT}/PROMPT_EXPERIMENT.tables.md"

LoadPrompt = Callable[[str], PromptContract]
"""``load_prompt(version) -> PromptContract``."""


def labels_rel(set_name: str) -> str:
    """Repo-relative path of a hand-label file."""
    return f"experiments/prompt/labels/{set_name}.labels.json"


def cell_dir(prompt: str, set_name: str) -> str:
    """Data-relative directory of one (prompt, set) cell."""
    return f"{OUT}/results/{prompt}-{set_name}"


def _started(prompt: str, set_name: str) -> str:
    """The run-once marker PROCEDURE.md names, written before the first call."""
    return f"{cell_dir(prompt, set_name)}/STARTED.json"


def _results(prompt: str, set_name: str) -> str:
    return f"{cell_dir(prompt, set_name)}/results.json"


def _now(ctx: ExperimentContext) -> str:
    return ctx.clock.now_utc().isoformat()


# --- select ----------------------------------------------------------------------


def pinned_handcheck_sha256(ctx: ExperimentContext) -> str:
    """Returns the hand-check raw file's sha256 as pinned in its committed meta.

    Raises:
        ExperimentError: If the meta file is missing, not JSON or has no digest.
    """
    meta = read_json(ctx.reader, HANDCHECK_META_REL)
    pinned = meta.get("sha256") if isinstance(meta, dict) else None
    if not isinstance(pinned, str):
        raise ExperimentError(f"no sha256 in {HANDCHECK_META_REL}")
    return pinned


def cmd_select(
    ctx: ExperimentContext,
    *,
    postings: Sequence[Posting],
    evaluate: Evaluate,
) -> dict[str, Any]:
    """Draws the sets and writes selection, strata, worksheets and label templates.

    Args:
        ctx: Shared dependencies.
        postings: Every posting of the hand-check raw file (parsed by the provider).
        evaluate: The rule (``rule.verdict.evaluate`` with the verified résumé bound).

    Returns:
        The written ``selection.json`` content.

    Raises:
        ExperimentError: If a selection exists, PROCEDURE.md is not committed, the
            raw file's digest is not the one pinned in its meta, or a stratum is
            short.
    """
    if ctx.data_exists(SELECTION):
        raise ExperimentError("selection already exists; select runs once only")
    if not ctx.git.is_tracked_and_clean(Path(PROCEDURE_REL)):
        raise ExperimentError(f"commit {PROCEDURE_REL} before running select")
    raw_sha = file_sha256(ctx.reader, HANDCHECK_RAW_REL)
    if raw_sha != pinned_handcheck_sha256(ctx):
        raise ExperimentError("hand-check raw file digest differs from the pinned one")
    selection = select_postings(postings, evaluate)
    by_id = {p.posting_id: p for p in postings}

    strata_doc = {
        "seed": SEED,
        "quotas": dict(QUOTAS),
        "definitions": dict(STRATUM_DEFINITIONS),
        "pool_sizes": dict(selection.pool_sizes),
        "postings": {
            pid: {
                "stratum": f.stratum,
                "rule_label": f.label.value,
                "failed_gates": list(f.failed_gates),
            }
            for pid, f in sorted(selection.facts.items(), key=lambda kv: int(kv[0]))
        },
        "notice": "Do not open this file until `jsa exp prompt score`.",
    }
    ctx.writer.write_json_atomic(STRATA_FILE, strata_doc)
    strata_sha = file_sha256(ctx.reader, ctx.repo_rel(STRATA_FILE))
    doc: dict[str, Any] = {
        "seed": SEED,
        "created_at_utc": _now(ctx),
        "procedure_path": PROCEDURE_REL,
        "procedure_sha256": file_sha256(ctx.reader, PROCEDURE_REL),
        "raw_path": HANDCHECK_RAW_REL,
        "raw_sha256": raw_sha,
        "code_commit": ctx.git.head(),
        "code_dirty": ctx.git.is_dirty(),
        "strata_path": ctx.repo_rel(STRATA_FILE),
        "strata_sha256": strata_sha,
        "sets": {"dev": list(selection.dev), "heldout": list(selection.heldout)},
    }
    ctx.writer.write_json_atomic(SELECTION, doc)
    for set_name in SETS:
        ids = selection.ids(set_name)
        text = render_worksheet(set_name, ids, by_id)
        ctx.writer.write_bytes_atomic(
            f"{OUT}/worksheets/{set_name}.md", text.encode("utf-8")
        )
        ctx.writer.write_json_atomic(
            f"{OUT}/label-templates/{set_name}.labels.json",
            label_template(set_name, ids),
        )
    return doc


# --- seal ------------------------------------------------------------------------


def _selection(ctx: ExperimentContext) -> dict[str, Any]:
    if not ctx.data_exists(SELECTION):
        raise ExperimentError("no selection yet; run `jsa exp prompt select` first")
    doc: dict[str, Any] = ctx.read_data_json(SELECTION)
    return doc


def _labels(
    ctx: ExperimentContext, selection: Mapping[str, Any]
) -> dict[str, LabelFile]:
    return {
        set_name: validate_label_file(
            read_json(ctx.reader, labels_rel(set_name)),
            expected_set=set_name,
            expected_ids=selection["sets"][set_name],
        )
        for set_name in SETS
    }


def _seal_hashes(ctx: ExperimentContext) -> dict[str, str]:
    return {
        ctx.repo_rel(SELECTION): file_sha256(ctx.reader, ctx.repo_rel(SELECTION)),
        **{labels_rel(s): file_sha256(ctx.reader, labels_rel(s)) for s in SETS},
    }


def cmd_seal(ctx: ExperimentContext) -> dict[str, Any]:
    """Validates all hand labels and writes ``SEAL.json``.

    Args:
        ctx: Shared dependencies.

    Returns:
        The SEAL content.

    Raises:
        ExperimentError: If SEAL exists, there is no selection, or any label is
            invalid.
    """
    if ctx.data_exists(SEAL):
        raise ExperimentError("SEAL.json already exists; labels are sealed once")
    selection = _selection(ctx)
    labels = _labels(ctx, selection)
    doc = {
        "sealed_at_utc": _now(ctx),
        "code_commit": ctx.git.head(),
        "label_counts": {s: len(labels[s].labels) for s in SETS},
        "sha256": _seal_hashes(ctx),
        "instruction": (
            "Commit the two label files and this SEAL.json before any model call; "
            "the commit timestamp is the seal."
        ),
    }
    ctx.writer.write_json_atomic(SEAL, doc)
    return doc


def _verify_seal(ctx: ExperimentContext) -> None:
    if not ctx.data_exists(SEAL):
        raise ExperimentError("not sealed; run `jsa exp prompt seal` and commit it")
    if not ctx.committed(SEAL):
        raise ExperimentError("SEAL.json is not committed (tracked and clean)")
    for rel in [labels_rel(s) for s in SETS]:
        if not ctx.git.is_tracked_and_clean(Path(rel)):
            raise ExperimentError(f"{rel} is not committed (tracked and clean)")
    sealed: dict[str, str] = ctx.read_data_json(SEAL)["sha256"]
    current = _seal_hashes(ctx)
    changed = sorted(rel for rel in current if sealed.get(rel) != current[rel])
    if changed or set(sealed) != set(current):
        raise ExperimentError("sealed files changed since seal: " + ", ".join(changed))


# --- run -------------------------------------------------------------------------


def _freeze(ctx: ExperimentContext) -> dict[str, Any]:
    if not ctx.data_exists(FREEZE):
        raise ExperimentError("not frozen; run `jsa exp prompt freeze` and commit it")
    if not ctx.committed(FREEZE):
        raise ExperimentError("FREEZE.json is not committed (tracked and clean)")
    doc: dict[str, Any] = ctx.read_data_json(FREEZE)
    return doc


def _check_prompts_match_freeze(
    freeze: Mapping[str, Any], load_prompt: LoadPrompt
) -> None:
    for version in PROMPTS:
        if load_prompt(version).sha256 != freeze[f"{version}_sha256"]:
            raise ExperimentError(f"prompt {version} changed after freeze")


def cmd_run(
    ctx: ExperimentContext,
    *,
    prompt_version: str,
    set_name: str,
    postings: Mapping[str, Posting],
    load_prompt: LoadPrompt,
    judge_call: JudgeCall,
) -> dict[str, Any]:
    """Runs one (prompt, set) cell: one first-reply call per posting.

    Args:
        ctx: Shared dependencies.
        prompt_version: ``"v1"`` or ``"v2"``.
        set_name: ``"dev"`` or ``"heldout"``.
        postings: Postings of the hand-check raw file by ID.
        load_prompt: Loads ``prompts/judge.<version>.md``.
        judge_call: Makes one call with ``retry_once=False``.

    Returns:
        The written ``results.json`` content.

    Raises:
        ExperimentError: If any ordering gate refuses (see module docstring).
    """
    if prompt_version not in PROMPTS or set_name not in SETS:
        raise ExperimentError("prompt must be v1 or v2 and set must be dev or heldout")
    _verify_seal(ctx)
    if ctx.data_exists(_started(prompt_version, set_name)):
        raise ExperimentError(
            f"{prompt_version}/{set_name} has already run; each cell runs once only"
        )
    if (prompt_version, set_name) != ("v1", "dev"):
        freeze = _freeze(ctx)
        _check_prompts_match_freeze(freeze, load_prompt)
        if set_name == "heldout":
            for version in PROMPTS:
                if not ctx.data_exists(_results(version, "dev")):
                    raise ExperimentError(f"{version} dev results missing")
    prompt = load_prompt(prompt_version)
    ids: list[str] = _selection(ctx)["sets"][set_name]
    missing = [pid for pid in ids if pid not in postings]
    if missing:
        raise ExperimentError(
            "selected postings missing from source: " + ", ".join(missing)
        )
    started = {
        "prompt_id": prompt.prompt_id,
        "prompt_sha256": prompt.sha256,
        "set": set_name,
        "started_at_utc": _now(ctx),
        "code_commit": ctx.git.head(),
        "code_dirty": ctx.git.is_dirty(),
    }
    ctx.writer.write_json_atomic(_started(prompt_version, set_name), started)

    def call(pid: str) -> Callable[[], dict[str, Any]]:
        log_dir = f"{cell_dir(prompt_version, set_name)}/calls/{pid}"
        return lambda: judge_call(postings[pid], prompt, log_dir).model_dump(
            mode="json"
        )

    return record_calls(
        ctx, _results(prompt_version, set_name), started, (call(p) for p in ids)
    )


# --- freeze ----------------------------------------------------------------------


def cmd_freeze(ctx: ExperimentContext, *, load_prompt: LoadPrompt) -> dict[str, Any]:
    """Freezes v1 and v2 after checking the one-section rule.

    Args:
        ctx: Shared dependencies.
        load_prompt: Loads ``prompts/judge.<version>.md``.

    Returns:
        The FREEZE content.

    Raises:
        ExperimentError: If FREEZE exists, the v1 dev results are missing, v2 is
            missing or malformed, v1 changed since the dev run or the sampling run,
            or v2 differs from v1 in other than exactly one section.
    """
    if ctx.data_exists(FREEZE):
        raise ExperimentError("FREEZE.json already exists; there is no v2 iteration")
    if not ctx.data_exists(_results("v1", "dev")):
        raise ExperimentError("v1 dev results missing; run v1 on dev first")
    v1 = load_prompt("v1")
    v2 = load_prompt("v2")
    dev_sha = ctx.read_data_json(_results("v1", "dev"))["prompt_sha256"]
    if dev_sha != v1.sha256:
        raise ExperimentError("prompt v1 changed since the v1 dev run")
    if not ctx.data_exists(SAMPLING_MANIFEST):
        raise ExperimentError("sampling manifest missing; v1 must match sampling's v1")
    sampling_sha = ctx.read_data_json(SAMPLING_MANIFEST)["prompt_sha256"]
    if sampling_sha != v1.sha256:
        raise ExperimentError("prompt v1 differs from the v1 used for sampling")
    changed = changed_sections(v1, v2)
    if len(changed) != 1:
        raise ExperimentError(
            f"v2 must differ from v1 in exactly one section; changed: {changed}"
        )
    doc = {
        "frozen_at_utc": _now(ctx),
        "code_commit": ctx.git.head(),
        "v1_sha256": v1.sha256,
        "v2_sha256": v2.sha256,
        "changed_section": changed[0],
        "v1_matches_dev_run": True,
        "v1_matches_sampling": True,
        "instruction": "Commit this FREEZE.json before any v2 call.",
    }
    ctx.writer.write_json_atomic(FREEZE, doc)
    return doc


# --- score -----------------------------------------------------------------------


def _scores(
    ctx: ExperimentContext, prompt: str, set_name: str
) -> tuple[list[CallRecord], bool]:
    doc = ctx.read_data_json(_results(prompt, set_name))
    calls = [CallRecord.model_validate(c) for c in doc["calls"]]
    return calls, is_complete(doc)


def cmd_score(ctx: ExperimentContext) -> dict[str, Any]:
    """Scores all four cells after re-verifying the seal; reveals the strata.

    A cell that stopped early is scored on the calls it made and marked
    ``"complete": false`` (as is the whole document).

    Args:
        ctx: Shared dependencies.

    Returns:
        The written ``metrics.json`` content.

    Raises:
        ExperimentError: If SEAL or FREEZE fail their checks, a cell is missing, or
            the strata file changed since selection.
    """
    _verify_seal(ctx)
    freeze = _freeze(ctx)
    for prompt in PROMPTS:
        for set_name in SETS:
            if not ctx.data_exists(_results(prompt, set_name)):
                raise ExperimentError(f"results missing for {prompt}/{set_name}")
    selection = _selection(ctx)
    strata_raw = ctx.reader.read_bytes(ctx.repo_rel(STRATA_FILE))
    if sha256_hex(strata_raw) != selection["strata_sha256"]:
        raise ExperimentError("strata.json changed since selection")
    strata_doc = ctx.read_data_json(STRATA_FILE)["postings"]
    strata = {pid: v["stratum"] for pid, v in strata_doc.items()}
    rule = {pid: VerdictLabel(v["rule_label"]) for pid, v in strata_doc.items()}
    gates = {pid: v["failed_gates"] for pid, v in strata_doc.items()}
    labels = _labels(ctx, selection)
    cells: dict[str, Any] = {}
    discord: dict[str, Any] = {}
    audit: dict[str, Any] = {}
    for set_name in SETS:
        hand = labels[set_name].by_id()
        loaded = {p: _scores(ctx, p, set_name) for p in PROMPTS}
        per_prompt = {p: scores for p, (scores, _) in loaded.items()}
        for prompt, (scores, complete) in loaded.items():
            cells[f"{prompt}-{set_name}"] = {
                **score_cell(scores, hand).model_dump(mode="json"),
                "complete": complete,
            }
        discord[set_name] = [
            d.model_dump(mode="json")
            for d in discordant(per_prompt["v1"], per_prompt["v2"], strata, hand)
        ]
        audit[set_name] = [
            a.model_dump(mode="json") for a in rule_vs_hand_audit(hand, rule, gates)
        ]
    doc = {
        "scored_at_utc": _now(ctx),
        "code_commit": ctx.git.head(),
        "changed_section": freeze["changed_section"],
        "first_reply_only": True,
        "complete": all(cell["complete"] for cell in cells.values()),
        "cells": cells,
        "v1_v2_discordant": discord,
        "rule_vs_hand_audit": audit,
        "strata": strata,
        "pool_sizes": ctx.read_data_json(STRATA_FILE)["pool_sizes"],
    }
    ctx.writer.write_json_atomic(METRICS, doc)
    ctx.writer.write_bytes_atomic(TABLES, render_tables(doc).encode("utf-8"))
    return doc


def _fmt_rate(r: Mapping[str, Any]) -> str:
    if r["value"] is None:
        return f"{r['k']}/{r['n']} (n/a)"
    return f"{r['k']}/{r['n']} [{r['wilson_low']:.2f}, {r['wilson_high']:.2f}]"


def render_tables(doc: Mapping[str, Any]) -> str:
    """Renders the generated tables for ``docs/experiments/PROMPT_EXPERIMENT.md``.

    Args:
        doc: The ``metrics.json`` content.

    Returns:
        Markdown with generated tables and student-only sections left blank.
    """
    stopped = [name for name, cell in doc["cells"].items() if not cell["complete"]]
    incomplete = (
        [
            "**INCOMPLETE STUDY:** these cells stopped before every call was made "
            "and are scored on the calls made only: " + ", ".join(stopped) + ".",
            "",
        ]
        if stopped
        else []
    )
    lines = [
        "# Prompt experiment: generated tables",
        "",
        *incomplete,
        f"Changed section (v1 to v2): `{doc['changed_section']}`. First reply only; "
        "no retries. Format acceptance is the validator pass rate, not accuracy. "
        "Brackets are Wilson 95% intervals.",
        "",
        "| Cell | Format acceptance | Agreement (invalid = disagree) | "
        "Agreement among valid | Evidence entries valid | Replies with a bad path |",
        "|---|---|---|---|---|---|",
    ]
    for name, cell in doc["cells"].items():
        paths = cell["evidence_paths"]
        mark = "" if cell["complete"] else " (INCOMPLETE)"
        lines.append(
            f"| {name}{mark} | {_fmt_rate(cell['format_acceptance'])} | "
            f"{_fmt_rate(cell['agreement_invalid_as_disagreement'])} | "
            f"{_fmt_rate(cell['agreement_among_valid'])} | "
            f"{paths['valid_entries']}/{paths['entries']} | "
            f"{paths['replies_with_bad_path']} |"
        )
    lines += ["", "## Confusion matrices (rows: hand label; columns: Claude)", ""]
    for name, cell in doc["cells"].items():
        lines += [
            f"### {name}",
            "",
            "| hand \\ Claude | MATCH | NO_MATCH | INVALID |",
            "|---|---|---|---|",
        ]
        for hand_label, row in cell["confusion"].items():
            counts = " | ".join(str(row[k]) for k in ("MATCH", "NO_MATCH", "INVALID"))
            lines.append(f"| {hand_label} | {counts} |")
        lines.append("")
    lines += ["## v1 vs v2 discordant postings", ""]
    for set_name, rows in doc["v1_v2_discordant"].items():
        items = [
            f"{r['posting_id']} ({r['stratum']}; v1 {r['v1']}, v2 {r['v2']})"
            for r in rows
        ]
        lines.append(f"- {set_name}: " + (", ".join(items) or "none"))
    lines += ["", "## Rule vs hand audit", ""]
    for set_name, rows in doc["rule_vs_hand_audit"].items():
        items = [
            f"{r['posting_id']} (hand {r['hand_label']}, rule {r['rule_label']})"
            for r in rows
        ]
        lines.append(f"- {set_name}: " + (", ".join(items) or "none"))
    lines += [
        "",
        "## Limits",
        "",
        "- n = 10 per cell: one posting moves a rate by 10 points.",
        "- One call per cell ignores the sampling variance measured in the sampling "
        "report.",
        "- Both sets come from one board on one day.",
        "- The stratified mix is not the board's base rate.",
        "",
        "## Rule-vs-hand decisions (labeling slip or rule bug)",
        "",
        STUDENT_MARKER,
        "",
        "## Conclusion",
        "",
        STUDENT_MARKER,
        "",
    ]
    return "\n".join(lines)
