"""The claim labeler's checks, with a fake Claude (no network). Postings are CONSTRUCTED."""
import json

from conftest import posting
from js3 import claims, filterdoc, score, shortlist
from test_js3_wrong_versions import FILLER

P = posting("sl1", "Data Engineer", FILLER + "<p>You will write Python and SQL every day. "
                                              "This role is based in our Boston office.</p>")


def fake(reply: dict):
    def caller(prompt, model):
        return {"started_at": "2026-11-22T00:00:00-05:00", "exit_code": 0, "model_requested": model,
                "models_used": ["fake"], "duration_ms": 1, "is_error": False, "result": json.dumps(reply)}
    return caller


def _labels(overrides):
    r = score.score(P, filterdoc.load())
    ids = [i for i, _ in shortlist.claim_ids(r)]
    labs = [{"id": i, "label": "insufficient", "quote": None, "conflict": None} for i in ids]
    for lab in labs:
        lab.update(overrides.get(lab["id"], {}))
    return r, {"labels": labs}


def test_grounded_labels_give_worth_reading():
    r, reply = _labels({"C1": {"label": "supported", "quote": "Data Engineer"},
                        "C2:Python": {"label": "supported", "quote": "You will write Python and SQL every day."}})
    out = shortlist.label_posting(P, r, caller=fake(reply))
    assert all(c["valid"] for c in out["claims"])
    assert out["answer"]["answer"] == claims.WORTH


def test_an_invented_quote_is_invalid_and_the_answer_abstains():
    r, reply = _labels({"C1": {"label": "supported", "quote": "Data Engineer"},
                        "C2:Python": {"label": "supported", "quote": "Python is used for ML pipelines."}})
    out = shortlist.label_posting(P, r, caller=fake(reply))
    bad = [c for c in out["claims"] if c["id"] == "C2:Python"][0]
    assert not bad["valid"] and "not found" in bad["errors"][0]
    assert out["answer"]["answer"] == claims.CANNOT


def test_contradicted_level_means_not_for_priya():
    r, reply = _labels({"C1": {"label": "supported", "quote": "Data Engineer"},
                        "C2:Python": {"label": "supported", "quote": "You will write Python and SQL every day."},
                        "C3": {"label": "contradicted", "quote": "You will write Python"}})
    out = shortlist.label_posting(P, r, caller=fake(reply))
    assert out["answer"]["answer"] == claims.NOT_FOR


def test_wrong_claim_ids_are_reported():
    r, reply = _labels({})
    reply["labels"] = reply["labels"][:-1]
    out = shortlist.label_posting(P, r, caller=fake(reply))
    assert out["reply_errors"] and out["claims"][-1]["valid"] is False
