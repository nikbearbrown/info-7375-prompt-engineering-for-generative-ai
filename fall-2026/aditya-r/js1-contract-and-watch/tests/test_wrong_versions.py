"""CONTRACT.md §5: the two plausible-but-wrong implementations, and proof that the checks catch them.

Each check is run twice: against the real code (must pass) and against a deliberately faulty
variant from tests/faulty_variants.py (must be flagged). All data here is SYNTHETIC.
"""
import argparse
import json
import random
import time

from agent.validate import validate_judgment
from agent.watch import EXIT_INCOMPLETE, run
from tests import faulty_variants
from tests.fixtures import NEAR_MISS, NOT_RELEVANT, PERSONA, RELEVANT, board, fake_judge_from, valid_response

POSTINGS = [RELEVANT, NOT_RELEVANT, NEAR_MISS]


# ---- Wrong version 1: verdicts attached to the wrong postings ------------------------------------

def association_violations(rows, by_id):
    """Contract check: each reported JUDGMENT must be about the posting it is attached to, and
    its verdict and evidence must validate against that posting."""
    bad = []
    for row in rows:
        pid = row["posting_id"]
        j = row["JUDGMENT"]["evidence"]
        if not j or j.get("posting_id") != pid:
            bad.append((pid, "id mismatch"))
            continue
        ok, errs, _ = validate_judgment(json.dumps(j), by_id[pid], PERSONA)
        if not ok:
            bad.append((pid, errs))
    return bad


def _run_real(tmp_path, judge_fn):
    persona = tmp_path / "p.json"
    persona.write_text(json.dumps(PERSONA))
    b0, b1 = tmp_path / "b0.json", tmp_path / "b1.json"
    b0.write_bytes(board())
    b1.write_bytes(board(*POSTINGS))
    common = dict(board="synthetic", resume=str(persona), state=str(tmp_path / "s.json"),
                  runs_dir=str(tmp_path / "runs"), seeded_note="SYNTHETIC", resume_run=None, workers=3,
                  prompt_version="test")
    run(argparse.Namespace(label="base", from_file=str(b0), **common), judge_fn=lambda *a: None)
    code = run(argparse.Namespace(label="second", from_file=str(b1), **common), judge_fn=judge_fn)
    rep = json.loads(next((tmp_path / "runs").glob("*_second")).joinpath("report.json").read_text())
    return code, rep["new_postings"]


def test_wv1_real_pipeline_keeps_association_under_out_of_order_completion(tmp_path):
    responses = {p["id"]: valid_response(p) for p in POSTINGS}

    def slow_random_judge(p, resume):  # completions arrive in a shuffled order
        time.sleep(random.Random(p["id"]).uniform(0, 0.05))
        return fake_judge_from(responses)(p, resume)

    _, rows = _run_real(tmp_path, slow_random_judge)
    assert association_violations(rows, {p["id"]: p for p in POSTINGS}) == []
    assert {r["posting_id"]: r["JUDGMENT"]["verdict"] for r in rows} == {101: "relevant", 202: "not_relevant", 303: "not_relevant"}


def test_wv1_faulty_positional_join_is_caught():
    responses = [valid_response(p) for p in POSTINGS]
    reordered = list(reversed(responses))  # e.g. batch results returned in a different order
    rows = faulty_variants.join_by_position(POSTINGS, reordered, PERSONA)
    violations = association_violations(rows, {p["id"]: p for p in POSTINGS})
    assert violations, "the association check failed to catch wrong version 1"
    assert {v[0] for v in violations} == {101, 303}  # the middle one happens to line up


def test_wv1_real_pipeline_rejects_a_swapped_response(tmp_path):
    """If the model answers about another posting, the real code refuses to complete it."""
    swapped = {101: valid_response(NOT_RELEVANT), 202: valid_response(RELEVANT), 303: valid_response(NEAR_MISS)}
    code, rows = _run_real(tmp_path, fake_judge_from(swapped))
    assert code == EXIT_INCOMPLETE
    status = {r["posting_id"]: r["JUDGMENT"]["valid"] for r in rows}
    assert status == {101: False, 202: False, 303: True}


# ---- Wrong version 2: structurally valid but unsupported justification ---------------------------

def unsupported_response():
    """SYNTHETIC: well-formed JSON whose cited evidence is absent from the inputs."""
    d = json.loads(valid_response(RELEVANT))
    d["shared_skills"]["skills"][0]["quote"] = "5+ years of Python in production at scale"
    d["shared_skills"]["skills"][1]["resume_field"] = "skills.backend_automation"  # SQL is not there
    return json.dumps(d)


def accepts_unsupported(validator):
    return validator(unsupported_response(), RELEVANT, PERSONA)[0]


def test_wv2_real_validator_rejects_unsupported_justification():
    assert not accepts_unsupported(validate_judgment)


def test_wv2_faulty_shallow_validator_is_caught():
    assert accepts_unsupported(faulty_variants.shallow_validate), "fixture should fool the shallow validator"
    # the contract check (reject unsupported evidence) therefore flags the faulty variant:
    assert accepts_unsupported(faulty_variants.shallow_validate) != accepts_unsupported(validate_judgment)


def test_wv2_unsupported_response_is_not_reported_as_evaluated(tmp_path):
    code, rows = _run_real(tmp_path, fake_judge_from({101: unsupported_response(),
                                                      202: valid_response(NOT_RELEVANT),
                                                      303: valid_response(NEAR_MISS)}))
    assert code == EXIT_INCOMPLETE
    row = next(r for r in rows if r["posting_id"] == 101)
    assert not row["JUDGMENT"]["valid"] and row["JUDGMENT"]["verdict"] is None
