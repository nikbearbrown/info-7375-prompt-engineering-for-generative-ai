"""Prompt experiment command order and gates (PLAN §6.2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from job_search_agent.experiments import prompt_experiment as pe
from job_search_agent.experiments._io import ExperimentError
from job_search_agent.experiments.selection import SETS
from tests.conftest import RawHandcheck
from tests.experiments.helpers import (
    DEFAULT_COUNTS,
    Board,
    Repo,
    first_reply_judge,
    make_board,
    make_repo,
    reply_text,
    write_labels,
)

SAMPLING_V1 = "experiments/sampling/manifest.json"


def _select(repo: Repo, board: Board) -> dict[str, Any]:
    repo.commit(pe.PROCEDURE_REL)
    return pe.cmd_select(repo.ctx, postings=board.postings, evaluate=board.evaluate)


def _hand(board: Board) -> dict[str, str]:
    """Hand labels equal to the synthetic rule verdicts."""
    return {
        pid: ("MATCH" if s == "M" else "NO_MATCH") for pid, s in board.strata.items()
    }


def _sealed(tmp_path: Path) -> tuple[Repo, Board]:
    repo = make_repo(tmp_path)
    board = make_board(DEFAULT_COUNTS)
    _select(repo, board)
    write_labels(repo, _hand(board))
    pe.cmd_seal(repo.ctx)
    repo.commit(
        "data/experiments/prompt/SEAL.json",
        "experiments/prompt/labels/dev.labels.json",
        "experiments/prompt/labels/heldout.labels.json",
    )
    return repo, board


def _run(
    repo: Repo, board: Board, prompt: str, set_name: str, label: str = "RELEVANT"
) -> Any:
    judge, backend = first_reply_judge(repo, [reply_text(label)] * 10)
    doc = pe.cmd_run(
        repo.ctx,
        prompt_version=prompt,
        set_name=set_name,
        postings=board.by_id(),
        load_prompt=repo.load_prompt,
        judge_call=judge,
    )
    assert backend.calls == 10
    return doc


def _write_v2(repo: Repo, *, sections: tuple[str, ...] = ("label_definition",)) -> None:
    text = (repo.root / "prompts/judge.v1.md").read_text(encoding="utf-8")
    for name in sections:
        start = text.index(f"<!-- section:{name} -->\n") + len(
            f"<!-- section:{name} -->\n"
        )
        end = text.index("<!-- /section -->", start)
        text = text[:start] + f"Changed {name} for v2.\n" + text[end:]
    repo.write("prompts/judge.v2.md", text)


def _sampling_manifest(repo: Repo) -> None:
    sha = repo.load_prompt("v1").sha256
    repo.writer.write_json_atomic(SAMPLING_V1, {"prompt_sha256": sha, "calls": []})


def _frozen(tmp_path: Path) -> tuple[Repo, Board]:
    repo, board = _sealed(tmp_path)
    _run(repo, board, "v1", "dev")
    _write_v2(repo)
    _sampling_manifest(repo)
    pe.cmd_freeze(repo.ctx, load_prompt=repo.load_prompt)
    repo.commit("data/experiments/prompt/FREEZE.json")
    return repo, board


# --- select ----------------------------------------------------------------------


def test_select_requires_committed_procedure(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    board = make_board(DEFAULT_COUNTS)
    with pytest.raises(ExperimentError, match="PROCEDURE.md"):
        pe.cmd_select(repo.ctx, postings=board.postings, evaluate=board.evaluate)


def test_select_writes_outputs_without_strata_and_refuses_twice(
    tmp_path: Path, raw_handcheck: RawHandcheck
) -> None:
    repo = make_repo(tmp_path)
    board = make_board(DEFAULT_COUNTS)
    doc = _select(repo, board)
    assert doc["seed"] == 20261029
    assert doc["raw_sha256"] == raw_handcheck.meta["sha256"]
    selection_text = (repo.root / "data/experiments/prompt/selection.json").read_text()
    for forbidden in ('"M"', "N1", "N2", "N3", "MATCH", 'stratum"'):
        assert forbidden not in selection_text
    strata = repo.data("experiments/prompt/strata.json")
    assert set(strata["postings"]) == set(doc["sets"]["dev"]) | set(
        doc["sets"]["heldout"]
    )
    for set_name in SETS:
        assert (
            repo.root / f"data/experiments/prompt/worksheets/{set_name}.md"
        ).is_file()
        assert (
            repo.root
            / f"data/experiments/prompt/label-templates/{set_name}.labels.json"
        ).is_file()
    with pytest.raises(ExperimentError, match="already exists"):
        _select(repo, board)


def test_select_refuses_raw_that_differs_from_its_meta(
    tmp_path: Path, raw_handcheck: RawHandcheck
) -> None:
    repo = make_repo(tmp_path)
    repo.write(pe.HANDCHECK_META_REL, {**raw_handcheck.meta, "sha256": "0" * 64})
    with pytest.raises(ExperimentError, match="pinned"):
        _select(repo, make_board(DEFAULT_COUNTS))
    assert not repo.ctx.data_exists(pe.SELECTION)


# --- seal ------------------------------------------------------------------------


def test_seal_requires_all_labels_valid(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    board = make_board(DEFAULT_COUNTS)
    _select(repo, board)
    with pytest.raises(ExperimentError, match="missing file"):
        pe.cmd_seal(repo.ctx)
    write_labels(repo, _hand(board))
    heldout = repo.root / "experiments/prompt/labels/heldout.labels.json"
    heldout.write_text(heldout.read_text().replace('"NO_MATCH"', '"MAYBE"', 1))
    with pytest.raises(ExperimentError, match="heldout labels invalid"):
        pe.cmd_seal(repo.ctx)
    assert not (repo.root / "data/experiments/prompt/SEAL.json").exists()
    write_labels(repo, _hand(board))
    seal = pe.cmd_seal(repo.ctx)
    assert seal["label_counts"] == {"dev": 10, "heldout": 10}
    assert set(seal["sha256"]) == {
        "data/experiments/prompt/selection.json",
        "experiments/prompt/labels/dev.labels.json",
        "experiments/prompt/labels/heldout.labels.json",
    }
    with pytest.raises(ExperimentError, match="already exists"):
        pe.cmd_seal(repo.ctx)


# --- run gates -------------------------------------------------------------------


def test_dev_run_refuses_without_committed_seal(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    board = make_board(DEFAULT_COUNTS)
    _select(repo, board)
    write_labels(repo, _hand(board))
    judge, backend = first_reply_judge(repo, [])
    kwargs: dict[str, Any] = dict(
        prompt_version="v1",
        set_name="dev",
        postings=board.by_id(),
        load_prompt=repo.load_prompt,
        judge_call=judge,
    )
    with pytest.raises(ExperimentError, match="not sealed"):
        pe.cmd_run(repo.ctx, **kwargs)
    pe.cmd_seal(repo.ctx)
    with pytest.raises(ExperimentError, match="SEAL.json is not committed"):
        pe.cmd_run(repo.ctx, **kwargs)
    repo.commit("data/experiments/prompt/SEAL.json")
    with pytest.raises(ExperimentError, match="labels.json is not committed"):
        pe.cmd_run(repo.ctx, **kwargs)
    assert backend.calls == 0


def test_dev_run_once_first_reply_only(tmp_path: Path) -> None:
    repo, board = _sealed(tmp_path)
    judge, backend = first_reply_judge(repo, ["```json\n{}\n```"] * 10)
    doc = pe.cmd_run(
        repo.ctx,
        prompt_version="v1",
        set_name="dev",
        postings=board.by_id(),
        load_prompt=repo.load_prompt,
        judge_call=judge,
    )
    assert backend.calls == 10  # one call per posting, no retry
    assert all(not c["first_reply_valid"] for c in doc["calls"])
    assert all(c["validation_codes"] == ["CODE_FENCE"] for c in doc["calls"])
    with pytest.raises(ExperimentError, match="already run"):
        _run(repo, board, "v1", "dev")


def test_v2_dev_run_refuses_before_freeze(tmp_path: Path) -> None:
    repo, board = _sealed(tmp_path)
    _run(repo, board, "v1", "dev")
    _write_v2(repo)
    with pytest.raises(ExperimentError, match="not frozen"):
        _run(repo, board, "v2", "dev")
    _sampling_manifest(repo)
    pe.cmd_freeze(repo.ctx, load_prompt=repo.load_prompt)
    with pytest.raises(ExperimentError, match="FREEZE.json is not committed"):
        _run(repo, board, "v2", "dev")
    repo.commit("data/experiments/prompt/FREEZE.json")
    _run(repo, board, "v2", "dev")


def test_heldout_refuses_before_freeze(tmp_path: Path) -> None:
    repo, board = _sealed(tmp_path)
    _run(repo, board, "v1", "dev")
    with pytest.raises(ExperimentError, match="not frozen"):
        _run(repo, board, "v1", "heldout")


def test_heldout_refuses_before_both_dev_cells(tmp_path: Path) -> None:
    repo, board = _frozen(tmp_path)
    with pytest.raises(ExperimentError, match="v2 dev results missing"):
        _run(repo, board, "v1", "heldout")


def test_heldout_refuses_if_prompt_changed_after_freeze(tmp_path: Path) -> None:
    repo, board = _frozen(tmp_path)
    _run(repo, board, "v2", "dev")
    v2 = repo.root / "prompts/judge.v2.md"
    v2.write_text(v2.read_text() + "\n<!-- edited after freeze -->\n")
    with pytest.raises(ExperimentError, match="v2 changed after freeze"):
        _run(repo, board, "v1", "heldout")


def test_heldout_refuses_rerun(tmp_path: Path) -> None:
    repo, board = _frozen(tmp_path)
    _run(repo, board, "v2", "dev")
    _run(repo, board, "v1", "heldout")
    with pytest.raises(ExperimentError, match="already run"):
        _run(repo, board, "v1", "heldout")
    _run(repo, board, "v2", "heldout")


# --- freeze ----------------------------------------------------------------------


def test_freeze_rejects_multi_section_diff(tmp_path: Path) -> None:
    repo, board = _sealed(tmp_path)
    _run(repo, board, "v1", "dev")
    _sampling_manifest(repo)
    _write_v2(repo, sections=("label_definition", "output_schema"))
    with pytest.raises(ExperimentError, match="exactly one section"):
        pe.cmd_freeze(repo.ctx, load_prompt=repo.load_prompt)
    repo.write("prompts/judge.v2.md", (repo.root / "prompts/judge.v1.md").read_text())
    with pytest.raises(ExperimentError, match="exactly one section"):
        pe.cmd_freeze(repo.ctx, load_prompt=repo.load_prompt)
    _write_v2(repo)
    doc = pe.cmd_freeze(repo.ctx, load_prompt=repo.load_prompt)
    assert doc["changed_section"] == "label_definition"
    assert doc["v1_sha256"] == repo.load_prompt("v1").sha256


def test_freeze_requires_v1_dev_results_and_sampling_match(tmp_path: Path) -> None:
    repo, board = _sealed(tmp_path)
    _write_v2(repo)
    with pytest.raises(ExperimentError, match="v1 dev results missing"):
        pe.cmd_freeze(repo.ctx, load_prompt=repo.load_prompt)
    _run(repo, board, "v1", "dev")
    with pytest.raises(ExperimentError, match="sampling manifest missing"):
        pe.cmd_freeze(repo.ctx, load_prompt=repo.load_prompt)
    repo.writer.write_json_atomic(SAMPLING_V1, {"prompt_sha256": "0" * 64})
    with pytest.raises(ExperimentError, match="differs from the v1 used for sampling"):
        pe.cmd_freeze(repo.ctx, load_prompt=repo.load_prompt)


# --- score -----------------------------------------------------------------------


def _all_cells(tmp_path: Path) -> tuple[Repo, Board]:
    repo, board = _frozen(tmp_path)
    _run(repo, board, "v2", "dev", label="NOT_RELEVANT")
    _run(repo, board, "v1", "heldout")
    _run(repo, board, "v2", "heldout", label="NOT_RELEVANT")
    return repo, board


def test_score_verifies_seal_hashes(tmp_path: Path) -> None:
    repo, _ = _all_cells(tmp_path)
    labels = repo.root / "experiments/prompt/labels/dev.labels.json"
    labels.write_text(labels.read_text().replace("Test Student", "Someone Else"))
    with pytest.raises(ExperimentError, match="changed since seal"):
        pe.cmd_score(repo.ctx)


def test_score_rejects_changed_strata(tmp_path: Path) -> None:
    repo, _ = _all_cells(tmp_path)
    strata = repo.root / "data/experiments/prompt/strata.json"
    strata.write_text(strata.read_text() + " ")
    with pytest.raises(ExperimentError, match="strata.json changed"):
        pe.cmd_score(repo.ctx)


def test_score_end_to_end(tmp_path: Path) -> None:
    repo, board = _all_cells(tmp_path)
    doc = pe.cmd_score(repo.ctx)
    v1_dev = doc["cells"]["v1-dev"]
    # Every v1 reply says RELEVANT: agreement equals the share of MATCH hand labels.
    assert v1_dev["format_acceptance"]["k"] == 10
    assert v1_dev["agreement_invalid_as_disagreement"]["k"] == 4
    assert doc["cells"]["v2-dev"]["agreement_invalid_as_disagreement"]["k"] == 6
    assert len(doc["v1_v2_discordant"]["dev"]) == 10
    assert doc["rule_vs_hand_audit"] == {"dev": [], "heldout": []}
    tables = (
        repo.root / "data/experiments/prompt/PROMPT_EXPERIMENT.tables.md"
    ).read_text()
    assert "<!-- STUDENT WRITES THIS -->" in tables
    assert "accuracy" not in tables.replace("not accuracy", "")
    assert doc["complete"] is True and "INCOMPLETE" not in tables


def test_score_accepts_a_crashed_cell_and_marks_it_incomplete(
    tmp_path: Path,
) -> None:
    repo, board = _frozen(tmp_path)
    _run(repo, board, "v2", "dev")
    _run(repo, board, "v1", "heldout")
    judge, _ = first_reply_judge(repo, [reply_text()] * 4)
    made: list[str] = []

    def crashing(posting: Any, prompt: Any, log_dir: str) -> Any:
        if len(made) == 4:
            raise RuntimeError("simulated crash mid-cell")
        made.append(log_dir)
        return judge(posting, prompt, log_dir)

    kwargs: dict[str, Any] = {
        "prompt_version": "v2",
        "set_name": "heldout",
        "postings": board.by_id(),
        "load_prompt": repo.load_prompt,
        "judge_call": crashing,
    }
    with pytest.raises(RuntimeError, match="simulated crash"):
        pe.cmd_run(repo.ctx, **kwargs)
    results = repo.data("experiments/prompt/results/v2-heldout/results.json")
    assert results["complete"] is False and len(results["calls"]) == 4
    assert repo.data("experiments/prompt/results/v2-heldout/STARTED.json")
    with pytest.raises(ExperimentError, match="already run"):
        pe.cmd_run(repo.ctx, **kwargs)  # the run-once rule still holds
    doc = pe.cmd_score(repo.ctx)
    assert doc["complete"] is False
    assert doc["cells"]["v2-heldout"]["complete"] is False
    assert doc["cells"]["v2-heldout"]["format_acceptance"]["n"] == 4
    assert doc["cells"]["v1-dev"]["complete"] is True
    tables = (
        repo.root / "data/experiments/prompt/PROMPT_EXPERIMENT.tables.md"
    ).read_text()
    assert "**INCOMPLETE STUDY:**" in tables and "v2-heldout." in tables
    assert "| v2-heldout (INCOMPLETE) |" in tables


def test_rule_vs_hand_audit_reported_after_seal(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    board = make_board(DEFAULT_COUNTS)
    _select(repo, board)
    hand = _hand(board)
    slip = repo.data("experiments/prompt/selection.json")["sets"]["dev"][0]
    hand[slip] = "NO_MATCH" if hand[slip] == "MATCH" else "MATCH"
    write_labels(repo, hand)
    pe.cmd_seal(repo.ctx)  # seal succeeds: the audit is not a seal-time check
    repo.commit(
        "data/experiments/prompt/SEAL.json",
        "experiments/prompt/labels/dev.labels.json",
        "experiments/prompt/labels/heldout.labels.json",
    )
    _run(repo, board, "v1", "dev")
    _write_v2(repo)
    _sampling_manifest(repo)
    pe.cmd_freeze(repo.ctx, load_prompt=repo.load_prompt)
    repo.commit("data/experiments/prompt/FREEZE.json")
    for prompt, set_name in (("v2", "dev"), ("v1", "heldout"), ("v2", "heldout")):
        _run(repo, board, prompt, set_name)
    doc = pe.cmd_score(repo.ctx)
    audit = doc["rule_vs_hand_audit"]["dev"]
    assert [row["posting_id"] for row in audit] == [slip]
    assert audit[0]["decision"] is None
    assert doc["rule_vs_hand_audit"]["heldout"] == []
