"""What the rule changed from JS1, pinned to the posting.

Two amendments are under test here, and they are different kinds of change.

**A1 (R-v2 -> R-v2a), a letter bump.** Normalising three applicant-tracking
systems into one posting shape changed *where* G3 and G4 read from and nothing
about what they decide. That claim was testable and was tested: recompute over
the 163 real Greenhouse postings JS1 captured live on 2026-10-31 and require
every verdict to match JS1's committed R-v2.

**A2 (R-v2a -> R-v3), a number bump.** G4 stopped treating "remote" as a
location, which *does* change verdicts. So the test above cannot survive
unchanged, and the honest replacement is not to delete it: it is to say which
verdicts were allowed to move, name them, and assert that nothing else did.
`EXPECTED_MOVES` below is that list. It was not read off a test run — it is the
two postings `tests/test_review_g4_location.py` reproduced the defect on,
before the patch existed, and both are postings Weiting hand-labelled `no` in
JS1's labelling pass while R-v2 called them relevant.

If a verdict moves that is not in `EXPECTED_MOVES`, the patch did more than it
claimed and the review packet's scope finding was wrong.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent import providers
from agent import rule as rule_judge

ROOT = Path(__file__).resolve().parents[1]
RESPONSE = ROOT / "evidence" / "fixtures" / "js1-greenhouse-reddit-20261031.json"
BASELINE = ROOT / "evidence" / "fixtures" / "js1-rv2-verdicts.json"

# posting_id -> (what R-v2 said, what R-v3 must say, why it was allowed to move)
EXPECTED_MOVES = {
    "7131934": (
        ("relevant", None),
        ("not_relevant", "G4_location"),
        "Machine Learning Engineer, 'Remote - Ontario, Canada': remote, but not "
        "in a location the persona can work in.",
    ),
    "6512458": (
        ("relevant", None),
        ("not_relevant", "G4_location"),
        "Software Engineer, Ads, 'Remote - Ontario, Canada': same defect, same "
        "board, same capture.",
    ),
}


@pytest.fixture(scope="module")
def baseline():
    return json.loads(BASELINE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def postings():
    payload = json.loads(RESPONSE.read_text(encoding="utf-8"))
    return providers.get("greenhouse").parse("greenhouse:reddit", payload)


def test_the_baseline_is_the_one_js1_committed(baseline):
    import hashlib

    p = baseline["provenance"]
    assert p["js1_rule_version"] == "R-v2"
    assert p["postings"] == 163
    assert hashlib.sha256(RESPONSE.read_bytes()).hexdigest() == p["source_sha256"], (
        "the baseline was computed over different bytes than this test reads"
    )


def test_rv3_moves_exactly_the_verdicts_the_amendment_claimed(postings, baseline, persona):
    """The whole point of a number bump: say which verdicts move, then prove it."""
    assert len(postings) == 163
    moved = {}
    for posting in postings:
        got = rule_judge.judge(posting.for_rule(), persona)
        want = baseline["verdicts"][posting.posting_id]
        before = (want["verdict"], want["gate_failed"])
        after = (got["verdict"], got["gate_failed"])
        if before != after:
            moved[posting.posting_id] = (before, after, posting.title, posting.location)

    unexpected = {k: v for k, v in moved.items() if k not in EXPECTED_MOVES}
    assert unexpected == {}, (
        f"{len(unexpected)} verdict(s) moved that the amendment did not claim: "
        f"{unexpected}"
    )

    missing = set(EXPECTED_MOVES) - set(moved)
    assert missing == set(), (
        f"the amendment claimed these would move and they did not: {missing} — "
        "either the patch regressed or the defect was never there"
    )

    for posting_id, (before, after, _, _) in moved.items():
        want_before, want_after, _why = EXPECTED_MOVES[posting_id]
        assert before == want_before, f"{posting_id}: R-v2 baseline is not what A2 recorded"
        assert after == want_after, f"{posting_id}: R-v3 did not land where A2 said"


def test_the_other_161_verdicts_are_untouched(postings, baseline, persona):
    """Stated as a count, because 'exactly two moved' is the scope claim."""
    agree = sum(
        1
        for p in postings
        if (
            lambda got, want: (got["verdict"], got["gate_failed"])
            == (want["verdict"], want["gate_failed"])
        )(rule_judge.judge(p.for_rule(), persona), baseline["verdicts"][p.posting_id])
    )
    assert agree == 163 - len(EXPECTED_MOVES) == 161


def test_the_g4_defect_is_gone_from_the_real_board(postings, persona):
    """A2's reason for existing, checked on the data that exposed it.

    `tests/test_review_g4_location.py` holds the property in full; this one is
    here so that a future amendment that reintroduces the bypass fails in the
    file about carried-over behaviour too, not only in the review file.
    """
    relevant = [
        p for p in postings
        if rule_judge.judge(p.for_rule(), persona)["verdict"] == "relevant"
    ]
    assert relevant, "if nothing is relevant this test proves nothing"
    offenders = [
        (p.identity, p.location) for p in relevant
        if not any(phrase in p.location.casefold() for phrase in persona["locations_ok"])
    ]
    assert offenders == [], f"G4 is admitting unreachable locations again: {offenders}"


def test_the_g1_defect_is_still_present(postings, persona):
    """Carried over deliberately, not inherited by accident.

    One change per version: A2 fixed G4 and touched nothing else, so the
    seniority defect JS1 documented is still standing. G1 reads seniority out of
    the title while the board states it outright in a `Management Level` field,
    so a posting marked IC6 can still pass the title-word gate. It is written
    down in GATE.md and in README.md's sign-off as a known, unfixed defect — not
    repaired quietly here, where no review packet would cover it.
    """
    ic_levels = []
    for p in postings:
        for entry in p.raw.get("metadata") or []:
            if entry.get("name") == "Management Level" and entry.get("value"):
                ic_levels.append((p, entry["value"]))
                break
    assert ic_levels, "the fixture should carry Management Level values"
    senior_level_but_passes_g1 = [
        p for p, level in ic_levels
        if level in {"IC5", "IC6", "IC7"}
        and rule_judge.judge(p.for_rule(), persona)["gate_failed"] != "G1_title_block"
    ]
    assert senior_level_but_passes_g1, (
        "at least one high-level posting should slip past the title-word gate"
    )


def test_every_justification_names_a_provider_native_field(postings, persona):
    """Provenance survives normalisation (JS1 CONTRACT.md O2)."""
    for posting in postings[:40]:
        verdict = rule_judge.judge(posting.for_rule(), persona)
        assert verdict["justification"]
        for c in verdict["justification"]:
            assert c["posting_field"] in {"title", "location.name", "job_family"}
            assert c.get("provider_field"), (
                f"{posting.identity}: citation {c} lost its provider-native path"
            )
