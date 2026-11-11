"""GATE.md §5.5 — the 19 boundary cases, run against the real policy.

No network is involved: every network refusal happens on the URL string before
a socket is opened, which is the point of checking the policy there.
"""

from __future__ import annotations

import pytest

from agent import errors
from agent.policy import Policy
from tests.boundary_cases import CASES


def prepare(project, case) -> Policy:
    """Set up whatever the case needs on disk, and build the policy for it."""
    if case.get("needs") == "symlink":
        link = project / "evidence" / "link"
        if not link.exists():
            link.symlink_to(project.parent, target_is_directory=True)
    if case.get("needs") == "existing":
        (project / "evidence" / "raw" / "already-there.json").write_text("{}", encoding="utf-8")
    return Policy(
        project_root=project,
        output_root=(project / "evidence").resolve(),
        approve_overwrite=bool(case.get("approve")),
    )


def exercise(policy: Policy, project, case):
    if case["kind"] == "net":
        return policy.check_request(case["method"], case["url"])
    target = project / case["path"] if not case["path"].startswith("..") else project / "evidence" / case["path"]
    if case["kind"] == "write":
        return policy.check_write(target)
    return policy.check_read(target)


def actual_outcome(policy, project, case) -> str:
    try:
        exercise(policy, project, case)
        return "allow"
    except errors.PolicyRefusal as exc:
        return f"deny:{type(exc).__name__}"


@pytest.mark.parametrize("case", CASES, ids=[f"case{c['n']}" for c in CASES])
def test_boundary_case_matches_its_prediction(case, project):
    policy = prepare(project, case)
    assert actual_outcome(policy, project, case) == case["predicted"], (
        f"case {case['n']} ({case['desc']}): predicted {case['predicted']}"
    )


def test_every_category_the_assignment_names_is_covered():
    kinds = {c["kind"] for c in CASES}
    assert kinds == {"net", "write", "read"}
    predicted = [c["predicted"] for c in CASES]
    for required in (
        "deny:DisallowedHost",
        "deny:DisallowedScheme",
        "deny:DisallowedPort",
        "deny:MethodNotAllowed",
        "deny:PathEscapes",
        "deny:RefusedRealResume",
        "deny:NeedsApproval",
        "allow",
    ):
        assert required in predicted, f"no boundary case predicts {required}"
    assert len(CASES) >= 10


def test_the_prefix_trick_and_the_symlink_are_distinct_cases():
    """Both must be present: either one alone leaves a real hole open."""
    paths = {c.get("path") for c in CASES}
    assert "evidence-evil/x.json" in paths
    assert "evidence/link/x.json" in paths


def test_approval_only_ever_adds_the_overwrite_permission(project):
    """--approve-overwrite must not widen a host, a method, or a path."""
    approving = Policy(
        project_root=project,
        output_root=(project / "evidence").resolve(),
        approve_overwrite=True,
    )
    with pytest.raises(errors.DisallowedHost):
        approving.check_request("GET", "https://evil.example/jobs")
    with pytest.raises(errors.MethodNotAllowed):
        approving.check_request("POST", "https://boards-api.greenhouse.io/x")
    with pytest.raises(errors.PathEscapes):
        approving.check_write(project / "evidence-evil" / "x.json")


# --- W2, which GATE.md §7 says boundary case 12 catches -----------------------
#
# The gate's claim is conditional: *if* the write boundary were a string prefix
# test, case 12 would catch it. Nothing was checking that. `PrefixPathPolicy`
# sat in tests/wrong_versions.py unused, so §7's "caught by boundary case 12"
# was an assertion about a test that was never run against the wrong version.
# Added 2026-11-09, after the freeze, when the gap was noticed while auditing
# §7 against the suite.

def case(n: int) -> dict:
    (found,) = [c for c in CASES if c["n"] == n]
    return found


def test_W2_is_admitted_by_the_prefix_check_and_refused_by_the_real_one(project):
    """Case 12 — `evidence-evil/x.json`, the sibling that shares a prefix."""
    from tests import wrong_versions as wrong

    target = project / case(12)["path"]
    target.parent.mkdir(parents=True, exist_ok=True)

    bad = wrong.PrefixPathPolicy(
        project_root=project, output_root=(project / "evidence").resolve()
    )
    # W2 allows it. This is the hole, stated as the thing it lets through.
    assert bad.check_write(target) == target

    good = Policy(project_root=project, output_root=(project / "evidence").resolve())
    with pytest.raises(errors.PathEscapes):
        good.check_write(target)


def test_W2_is_plausible_because_it_passes_most_other_write_cases(project):
    """Why a reviewer would wave the one-liner through — and what §7 missed.

    W2 is not obviously broken. It gets the `..` traversal right, it gets the
    symlink right (both resolve to paths that do not share the prefix), and it
    enforces the overwrite approval. Two write cases distinguish it:

    - **case 12**, `evidence-evil/x.json`, the sibling sharing a prefix, which
      GATE.md §7 predicted; and
    - **case 14**, the output root itself, which §7 did **not** mention.
      `str(evidence).startswith(str(evidence))` is trivially true, so W2 will
      happily write over the evidence directory.

    §7 said W2 was "caught by boundary case 12". True, and incomplete — it is
    caught by 12 and 14, and the second one is the more destructive of the two.
    Found 2026-11-09 by running §7's claim instead of reading it; recorded in
    §8 A3.
    """
    from tests import wrong_versions as wrong

    write_cases = [c for c in CASES if c["kind"] == "write"]
    assert len(write_cases) >= 5

    disagreements = []
    for c in write_cases:
        bad = prepare(project, c)
        bad = wrong.PrefixPathPolicy(
            project_root=project,
            output_root=(project / "evidence").resolve(),
            approve_overwrite=bool(c.get("approve")),
        )
        if actual_outcome(bad, project, c) != c["predicted"]:
            disagreements.append(c["n"])

    assert disagreements == [12, 14], (
        "W2 should be distinguished by exactly the sibling-prefix case and the "
        f"output-root case; got {disagreements}"
    )


def test_W2_would_also_let_the_evidence_directory_itself_be_written(project):
    """Case 14, which GATE.md §7 did not predict W2 would fail.

    This is the one I would rather have caught in review than in an audit: a
    prefix check cannot distinguish "inside the output root" from "is the output
    root", so W2 permits writing over `evidence/` — the directory holding every
    saved response this submission rests on.
    """
    from tests import wrong_versions as wrong

    target = project / "evidence"
    bad = wrong.PrefixPathPolicy(
        project_root=project, output_root=(project / "evidence").resolve()
    )
    assert bad.check_write(target) == target

    good = Policy(project_root=project, output_root=(project / "evidence").resolve())
    with pytest.raises(errors.PathEscapes):
        good.check_write(target)
