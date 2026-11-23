"""The numbers reports/reject-audit.md §3 and §5 report, pinned.

The labels are a file; the analysis is a program. Both are in the repository,
so every number in the audit can be recomputed, and this file is what notices
if a later change to the filter silently moves one of them.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LABELS = ROOT / "audit" / "labels-weiting.json"

pytestmark = pytest.mark.skipif(
    not LABELS.exists(), reason="the hand labels are not in this checkout"
)


@pytest.fixture(scope="module")
def analysis(tmp_path_factory):
    out = tmp_path_factory.mktemp("audit") / "analysis.json"
    subprocess.run(
        [sys.executable, "tools/analyse_audit.py", str(LABELS), "--out", str(out)],
        cwd=ROOT, check=True, capture_output=True,
    )
    return json.loads(out.read_text(encoding="utf-8"))


def test_all_48_were_labelled(analysis):
    assert analysis["counts"]["labelled"] == 48


def test_the_labels_are_blind(analysis):
    assert "no score, no bucket and no gate" in analysis["blind"]
    assert analysis["labels_from"] == "Weiting Wang"


def test_three_disagreements(analysis):
    c = analysis["counts"]
    assert c["decided"] == 42
    assert c["unsure"] == 6
    assert c["agree"] == 39
    assert c["disagree"] == 3
    assert c["filter_missed_something_she_wanted"] == 2
    assert c["filter_kept_something_she_did_not"] == 1


def test_the_single_false_positive_is_the_case_frictional_flagged(analysis):
    """§5 of FRICTIONAL predicted this one and left it for the audit."""
    kept_but_unwanted = [
        d for d in analysis["disagreements"]
        if d["filter_kept"] and d["her"] == "no"
    ]
    assert len(kept_but_unwanted) == 1
    d = kept_but_unwanted[0]
    assert d["title"].strip() == "Software Engineer, Backend, Credit"

    from jobfilter import score as scorer

    body = _body_for(d["identity"])
    assert "2+ years" in body
    assert scorer._experience_wall(body) is None, (
        "MIN_WALL_YEARS is 3, so a 2+ years posting keeps its points -- which "
        "is why this is the audit's only false positive"
    )


def test_the_staff_disagreement_was_judged_without_a_body(analysis):
    wanted_but_dropped = [
        d for d in analysis["disagreements"]
        if not d["filter_kept"] and d["her"] == "yes"
    ]
    assert len(wanted_but_dropped) == 2
    staff = next(d for d in wanted_but_dropped if "Staff" in d["title"])
    assert staff["gate_failed"] == "G1_title_block"
    assert staff["score"] is None


def test_the_shortlist_got_one_clear_yes_out_of_four(analysis):
    """The least flattering number in the submission, asserted so it stays."""
    labels = json.loads(LABELS.read_text(encoding="utf-8"))["labels"]
    from inherited import resume as resume_mod
    from jobfilter import corpus as corpus_mod, pipeline

    persona = resume_mod.load(ROOT / "data" / "resume.persona.json")
    short = [
        d for d in pipeline.run(corpus_mod.load(), persona)
        if d.bucket == pipeline.SHORTLISTED
    ]
    verdicts = sorted(labels.get(d.posting.identity, "(unlabelled)") for d in short)
    assert verdicts == ["no", "unsure", "unsure", "yes"]


def test_the_refit_changes_nothing(analysis):
    t = analysis["threshold_refit"]
    assert t["best_t_on_train"] == 7
    assert t["held_out_at_best_t"] == t["held_out_at_baseline_6"] == "6/7"


def test_the_training_half_cannot_distinguish_t7_from_t10(analysis):
    """A 'best' decided by iteration order has not identified anything."""
    on_train = analysis["threshold_refit"]["all_candidates_on_train"]
    tied = {t: v for t, v in on_train.items() if v == "6/6"}
    assert set(tied) == {"7", "8", "9", "10"}


def _body_for(identity: str) -> str:
    from jobfilter import corpus as corpus_mod

    return next(p for p in corpus_mod.load() if p.identity == identity).body
