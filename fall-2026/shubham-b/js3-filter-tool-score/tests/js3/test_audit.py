"""FILTER.md §5: the interval, the draw and the tally."""

from __future__ import annotations

import json

import pytest

from job_search_agent.js3 import audit
from tests.conftest import REPO_ROOT


@pytest.mark.parametrize(
    ("k", "n", "lo", "hi"),
    [(0, 40, 0.0, 0.0881), (5, 20, 0.0866, 0.4910), (40, 40, 0.9119, 1.0)],
)
def test_clopper_pearson_known_values(k: int, n: int, lo: float, hi: float) -> None:
    got = audit.clopper_pearson(k, n)
    assert got[0] == pytest.approx(lo, abs=5e-4) and got[1] == pytest.approx(
        hi, abs=5e-4
    )


def test_committed_draw_has_the_registered_sizes() -> None:
    d = json.loads((REPO_ROOT / "data/js3/audit/draw.json").read_text(encoding="utf-8"))
    sizes = {k: len(v) for k, v in d["strata"].items()}
    assert (
        sizes["random_rejects"] == 40
        and sizes["close_rejected"] == 8
        and sizes["close_kept"] == 8
        and sizes["random_kept"] == 12
    )
    assert sorted(d["worksheet_order"]) == sorted(
        {k for v in d["strata"].values() for k in v}
    )
    assert all(
        not d["scores"][k]["v0.1"]["kept"] for k in d["strata"]["random_rejects"]
    )
    assert all(d["scores"][k]["v0.1"]["kept"] for k in d["strata"]["random_kept"])


def test_tally_counts_both_error_directions() -> None:
    strata = {"s": ["a", "b", "c", "d"]}
    verdicts = {
        "a": "RELEVANT",
        "b": "NOT_RELEVANT",
        "c": "CANNOT_TELL",
        "d": "RELEVANT",
    }
    kept = {"a": False, "b": True, "c": True, "d": True}
    assert audit.tally(strata, verdicts, kept)["s"] == {
        "n": 4,
        "wrong": 2,
        "right": 1,
        "cannot_tell": 1,
    }


def test_validate_rejects_blank_template() -> None:
    order = ["x"]
    blank = {
        "judged_by": None,
        "judged_on": None,
        "verdicts": [{"key": "x", "verdict": None}],
    }
    assert len(audit.validate_verdicts(blank, order)) == 2
    full = {
        "judged_by": "me",
        "judged_on": "2026-11-26",
        "verdicts": [{"key": "x", "verdict": "RELEVANT"}],
    }
    assert audit.validate_verdicts(full, order) == []
