"""The experiment harness, without Claude: one change per config, no contact fields, honest counting."""
import json

from conftest import ROOT, posting
from js3 import experiment
from jsagent import resume as resume_mod


def test_each_experiment_changes_exactly_one_object_from_its_baseline():
    base = experiment.CONFIGS["E0a"]
    assert experiment.CONFIGS["E0b"] == {**base, "what": experiment.CONFIGS["E0b"]["what"]}
    for name in ("E2", "E3", "E4", "E5"):
        cfg = experiment.CONFIGS[name]
        ref = experiment.CONFIGS[cfg.get("base", "E0a")]
        changed = [k for k in ("prompt", "context", "model") if cfg[k] != ref[k]]
        assert len(changed) == 1, (name, changed)


def test_prompt_v3_changes_only_the_rule_paragraph():
    v2 = (ROOT / "prompts" / "judge_v2.md").read_text().splitlines()
    v3 = (ROOT / "prompts" / "judge_v3.md").read_text().splitlines()
    assert len(v2) - len(v3) == 4                      # the 5-line rule paragraph became 1 line
    assert [x for x in v3 if x not in v2] == [v3[4]] and "worth the candidate's time to read in full" in v3[4]


def test_the_wider_context_carries_no_contact_fields():
    resume = resume_mod.load(ROOT / "persona" / "priya-nair.resume.json")
    view = json.dumps(experiment.resume_view(resume, "profile"))
    for secret in ("priya.nair@example.com", "555-0163", "linkedin", "github", "Priya"):
        assert secret not in view
    assert json.loads(view)["needs_visa_sponsorship"] is True


def test_agreement_counts_abstentions_and_invalid_answers_as_not_agreeing():
    labels = {"a": {"verdict": "relevant"}, "b": {"verdict": "not relevant"},
              "c": {"verdict": "relevant"}, "d": {"verdict": "not relevant"}}
    m = experiment.agreement({"a": "relevant", "b": "relevant", "c": "cannot judge", "d": None}, labels)
    assert (m["TP"], m["FP"], m["abstain"], m["invalid"], m["agree"], m["n"]) == (1, 1, 1, 1, 1, 4)


def test_experiments_use_only_the_heldout_postings():
    keys, labels = experiment.heldout()
    s = json.loads((ROOT / "audit" / "samples.json").read_text())
    assert set(keys) == set(s["heldout"]) and len(keys) == 40
    audit_keys = set(s["audit_random_rejects"] + s["audit_closest"] + s["audit_kept"])
    assert not set(keys) & audit_keys
