"""Selection, worksheets and label files (PLAN §6.2)."""

from __future__ import annotations

from collections import Counter

import pytest

from job_search_agent.experiments._io import ExperimentError
from job_search_agent.experiments.selection import (
    HANDCHECK_IDS,
    QUOTAS,
    classify_stratum,
    label_template,
    render_worksheet,
    select_postings,
    validate_label_file,
)
from tests.experiments.helpers import (
    DEFAULT_COUNTS,
    hand_entry,
    make_board,
    make_verdict,
)


def test_classify_stratum_definitions() -> None:
    assert [
        classify_stratum(make_verdict(s)) for s in ("M", "N1", "N2", "N3", "X")
    ] == [
        "M",
        "N1",
        "N2",
        "N3",
        None,
    ]


def test_selection_deterministic_given_seed() -> None:
    board = make_board(DEFAULT_COUNTS)
    first = select_postings(board.postings, board.evaluate)
    second = select_postings(list(reversed(board.postings)), board.evaluate)
    assert first.dev == second.dev and first.heldout == second.heldout
    other = select_postings(board.postings, board.evaluate, seed=1)
    assert (other.dev, other.heldout) != (first.dev, first.heldout)


def test_selection_excludes_handcheck_ids() -> None:
    board = make_board(DEFAULT_COUNTS)
    selection = select_postings(board.postings, board.evaluate)
    chosen = set(selection.dev) | set(selection.heldout)
    assert not chosen & set(HANDCHECK_IDS)
    assert selection.pool_sizes["M"] == DEFAULT_COUNTS["M"]  # handcheck not pooled


def test_selection_quotas_and_split_balance() -> None:
    board = make_board(DEFAULT_COUNTS)
    selection = select_postings(board.postings, board.evaluate)
    assert len(selection.dev) == len(selection.heldout) == 10
    assert not set(selection.dev) & set(selection.heldout)
    for ids in (selection.dev, selection.heldout):
        counts = Counter(board.strata[pid] for pid in ids)
        assert counts == {"M": 4, "N1": 2, "N2": 2, "N3": 2}
    assert sum(QUOTAS.values()) == 20
    assert {f.stratum for f in selection.facts.values()} == {"M", "N1", "N2", "N3"}


def test_selection_fails_loudly_if_stratum_short() -> None:
    board = make_board({**DEFAULT_COUNTS, "N2": 3})
    with pytest.raises(ExperimentError, match="N2: 3 < 4"):
        select_postings(board.postings, board.evaluate)


def test_worksheet_hides_rule_verdict_and_strata() -> None:
    board = make_board(DEFAULT_COUNTS)
    selection = select_postings(board.postings, board.evaluate)
    text = render_worksheet("dev", selection.dev, board.by_id())
    for forbidden in (
        "MATCH\n",
        "stratum",
        "N1",
        "N2",
        "N3",
        "failed_gates",
        "US_BASED\n",
    ):
        assert forbidden not in text
    assert "rule verdict" not in text.lower()
    for pid in selection.dev:
        assert f"Posting {pid}" in text
        assert f"https://x.invalid/{pid}" in text
    assert "Java and Python on AWS" in text  # cleaned content shown
    assert "hand_label (MATCH / NO_MATCH):" in text
    template = label_template("dev", selection.dev)
    assert [e["posting_id"] for e in template["labels"]] == list(selection.dev)
    assert all(e["hand_label"] is None for e in template["labels"])


def _file(ids: list[str], **overrides: object) -> dict[str, object]:
    doc: dict[str, object] = {
        "set": "dev",
        "labeled_by": "Student",
        "labels": [hand_entry(pid, "NO_MATCH") for pid in ids],
    }
    doc.update(overrides)
    return doc


def test_label_file_valid() -> None:
    parsed = validate_label_file(
        _file(["1", "2"]), expected_set="dev", expected_ids=["1", "2"]
    )
    assert set(parsed.by_id().values()) == {"NO_MATCH"}


@pytest.mark.parametrize(
    ("doc", "message"),
    [
        (_file(["1"]), "missing IDs: 2"),
        (_file(["1", "2", "3"]), "unexpected IDs: 3"),
        (_file(["1", "1", "2"]), "duplicate IDs: 1"),
        (_file(["1", "2"], set="heldout"), "set is 'heldout'"),
        (_file(["1", "2"], labeled_by=None), "labeled_by"),
        (_file(["1", "2"], labels=[{"posting_id": "1"}]), "labels.0"),
    ],
)
def test_label_file_problems_rejected(doc: dict[str, object], message: str) -> None:
    with pytest.raises(ExperimentError, match=message):
        validate_label_file(doc, expected_set="dev", expected_ids=["1", "2"])


def test_label_inconsistent_with_own_gates_rejected() -> None:
    entry = hand_entry("1", "MATCH")
    entry["location_label"] = "NON_US"
    with pytest.raises(ExperimentError, match="does not follow"):
        validate_label_file(
            _file(["2"], labels=[entry, hand_entry("2", "NO_MATCH")]),
            expected_set="dev",
            expected_ids=["1", "2"],
        )


def test_label_skills_repeated_term_counts_once() -> None:
    entry = hand_entry("1", "MATCH")
    entry["skills"] = [entry["skills"][0], entry["skills"][0]]
    with pytest.raises(ExperimentError, match="does not follow"):
        validate_label_file(
            _file(["1"], labels=[entry]), expected_set="dev", expected_ids=["1"]
        )
