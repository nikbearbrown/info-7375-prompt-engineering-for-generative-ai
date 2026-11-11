"""Experiment tooling with a fake judge — no network, no API key. Written after the code."""
import itertools

import pytest

from conftest import IRRELEVANT, RELEVANT
from experiment.common import ExperimentError, wilson
from experiment.make_label_sheet import select_title_matches, write_sheet
from experiment.run_experiment import check_heldout_allowed, run_experiment, score
from experiment.sample import check_ids, run_sampling
from experiment.split import stratified_split

LABELS = {
    1001: {"title": "Software Engineer - Platform Tools", "label": "relevant"},
    1002: {"title": "Enterprise Account Executive", "label": "not_relevant"},
}
POSTINGS = {1001: RELEVANT, 1002: IRRELEVANT}


def fixed_judge(verdicts):
    cycle = itertools.cycle(verdicts)

    def judge(resume, posting):
        return {"claude_verdict": next(cycle), "claude_justification": [], "claude_reason": "fake"}
    return judge


def test_stratified_split_is_deterministic_and_balanced():
    labels = {i: ("relevant" if i < 4 else "not_relevant") for i in range(20)}
    a, b = stratified_split(labels, seed=7), stratified_split(labels, seed=7)
    assert a == b
    assert len(a["dev"]) == len(a["heldout"]) == 10
    assert set(a["dev"]).isdisjoint(a["heldout"])
    for ids in a.values():
        assert any(labels[i] == "relevant" for i in ids)


def test_split_keeps_one_relevant_on_each_side_when_only_two():
    labels = {i: ("relevant" if i < 2 else "not_relevant") for i in range(20)}
    split = stratified_split(labels, seed=1)
    assert [sum(labels[i] == "relevant" for i in ids) for ids in split.values()] == [1, 1]


def test_sampling_refuses_heldout_and_unlabeled_ids():
    with pytest.raises(ExperimentError):
        check_ids([1001], LABELS, {"heldout": [1001]})
    with pytest.raises(ExperimentError):
        check_ids([9999], LABELS, {"heldout": []})


def test_sampling_counts_spread_against_hand_label(tmp_path, resume):
    summary = run_sampling([1001], 4, fixed_judge(["relevant", "not_relevant", "relevant", "invalid"]),
                           POSTINGS, resume, LABELS, {"heldout": [1002]}, tmp_path,
                           {"started_at": "t", "model": "m", "effort": "e",
                            "prompt": {"path": "p", "sha256": "0" * 64}})
    row = summary["postings"][0]
    assert row["counts"] == {"relevant": 2, "not_relevant": 1, "invalid": 1, "unavailable": 0}
    assert row["agreement"] == 0.5 and row["matches_hand_label"] == 2
    assert len(list((tmp_path / "raw").glob("*.json"))) == 4


def test_score_counts_invalid_as_fail():
    results = {1001: {"claude_verdict": "invalid"}, 1002: {"claude_verdict": "not_relevant"}}
    s = score([1001, 1002], results, LABELS)
    assert (s["passes"], s["invalid_or_unavailable"]) == (1, 1)
    assert s["confusion_relevant_positive"] == {"tp": 0, "fp": 0, "tn": 1, "fn": 0}


def test_wilson_is_wide_for_ten_cases():
    low, high = wilson(8, 10)
    assert low < 0.5 < 0.8 < high


def test_heldout_guard(tmp_path):
    fp = {"path": "prompts/revision-1.txt", "sha256": "a" * 64, "last_commit": "abc",
          "uncommitted_changes": False}
    with pytest.raises(ExperimentError):
        check_heldout_allowed(fp, final=False, results_dir=tmp_path)
    with pytest.raises(ExperimentError):
        check_heldout_allowed(dict(fp, uncommitted_changes=True), final=True, results_dir=tmp_path)
    with pytest.raises(ExperimentError):  # no dev run yet
        check_heldout_allowed(fp, final=True, results_dir=tmp_path)

    run_experiment("dev", [1001], fixed_judge(["relevant"]), POSTINGS, None, LABELS,
                   tmp_path / "2026_dev_revision-1",
                   {"started_at": "t", "model": "m", "effort": "e", "prompt": fp})
    check_heldout_allowed(fp, final=True, results_dir=tmp_path)  # now allowed


def test_label_sheet_selection_and_no_overwrite(tmp_path, resume):
    postings = {1001: RELEVANT, 1002: IRRELEVANT}
    assert select_title_matches(postings, resume["target_titles"]) == [1001]
    path = tmp_path / "labels.csv"
    write_sheet(path, postings, [1001], "snap.json")
    assert "relevant" not in path.read_text()  # no verdicts are pre-filled
    with pytest.raises(ExperimentError):
        write_sheet(path, postings, [1001], "snap.json")
