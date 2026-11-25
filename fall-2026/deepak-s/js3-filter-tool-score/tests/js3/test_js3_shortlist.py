"""Phase 4: claims, the checker's pre-labels, section 4 rule 3 on the shortlist, wrong version F05,
and the judge wrapper with a fake CLI. Written by Claude Code (claude-opus-5-5), 2026-11-25.
All postings and CLI outputs here are SEEDED."""
import json

import pytest

import js3kit  # noqa: F401
from filter_checks import line
from jobwatch import claude_judge, judge_cli, shortlist
from jobwatch import filter as flt
from jobwatch.policy import Policy
from jobwatch.tools import Tools


def kept():
    about = "About us: we love Python."
    ln = line(title="ML Engineer", location="Seattle, WA",
              body=(f"<p>{about}</p><li>Train PyTorch models.</li><li>3 years of experience required.</li>",), boilerplate=(about,))
    return ln, flt.evaluate(ln, flt.V1)


def test_one_claim_per_matched_rule_with_its_span_and_quote():
    ln, o = kept()
    rows = shortlist.claims_for(ln, o, flt.V1, 1, "data/texts/x.txt", [])
    by = {r["source"]: r for r in rows}
    assert set(by) == {"rule:R02", "rule:L04", "rule:T02", "rule:E01"}
    assert by["rule:R02"]["claim"] == "The role is a ML Engineer role." and by["rule:R02"]["quote"] == "ML Engineer"
    assert by["rule:L04"]["claim"] == "The job is based in Seattle."
    assert by["rule:T02"]["claim"] == "The work involves PyTorch."
    assert by["rule:E01"]["claim"].startswith("The minimum required experience stated is 3 years")
    assert all(r["pre_label"] == "quote found, not boilerplate" for r in rows)


def test_checker_pre_labels_boilerplate_and_missing_quotes_as_insufficient():
    ln, o = kept()
    rows = shortlist.claims_for(ln, o, flt.V1, 1, "t", [{"claim": "SEEDED uses Python", "quote": "we love Python"},
                                                       {"claim": "SEEDED invented", "quote": "not in the posting"}])
    judge = [r for r in rows if r["source"] == "judge"]
    assert [r["pre_label"] for r in judge] == ["insufficient (boilerplate)", "insufficient (quote not found)"]
    assert judge[0]["field"] == "text" and judge[1]["field"] == "" and judge[1]["quote_found"] is False


def test_parse_judge_keeps_at_most_two_well_formed_claims():
    raw = json.dumps({"claims": [{"claim": "a", "quote": "b"}, {"claim": 1}, {"claim": "c", "quote": "d"}, {"claim": "e", "quote": "f"}]})
    claims, why = shortlist.parse_judge(raw)
    assert [c["claim"] for c in claims] == ["a", "c"] and why is None
    assert shortlist.parse_judge("Sure! Here are claims")[0] == []


def labeled(ln, o, labels):
    rows = shortlist.claims_for(ln, o, flt.V1, 1, "t", [])
    for r in rows:
        r["label"] = labels.get(r["source"], "supported")
    return rows


def check_F05_insufficient_is_not_supported():
    ln, o = kept()
    assert shortlist.decide(labeled(ln, o, {}))[0] == "keep"
    assert shortlist.decide(labeled(ln, o, {"rule:T02": "insufficient"}))[0] == "I cannot tell"
    assert shortlist.decide(labeled(ln, o, {"rule:L04": "insufficient"}))[0] == "I cannot tell"
    assert shortlist.decide(labeled(ln, o, {"rule:R02": "contradicted"}))[0] == "I cannot tell"


def test_section4_rule3_abstains_when_a_needed_claim_is_insufficient():
    check_F05_insufficient_is_not_supported()


def test_F05_insufficient_treated_as_supported_is_caught(monkeypatch):
    real = shortlist._status
    monkeypatch.setattr(shortlist, "_status", lambda c: "supported" if real(c) == "insufficient" else real(c))
    with pytest.raises(AssertionError):
        check_F05_insufficient_is_not_supported()


def test_decide_uses_pre_labels_when_no_hand_label_exists():
    ln, o = kept()
    rows = shortlist.claims_for(ln, o, flt.V1, 1, "t", [])
    assert shortlist.decide(rows)[0] == "keep"


class FakeDone:
    def __init__(self, stdout, code=0):
        self.stdout, self.stderr, self.returncode = stdout, "", code


def test_judge_call_saves_prompt_argv_model_date_and_raw_response(tmp_path, monkeypatch):
    seen = {}

    def fake_run(argv, **kw):
        seen["argv"], seen["input"], seen["cwd"] = argv, kw["input"], kw["cwd"]
        return FakeDone(json.dumps({"result": "{\"claims\": []}", "modelUsage": {"claude-sonnet-5-5": {}}, "usage": {}}))
    monkeypatch.setattr(judge_cli, "run_subprocess", fake_run)
    monkeypatch.setattr(judge_cli.CliJudge, "version", lambda self: "SEEDED 0.0")
    tools = Tools(Policy(str(tmp_path), read_dirs=("shortlist",), write_dirs=("shortlist",)))
    res = claude_judge.call(tools, "SYS", "USER", "claude-sonnet-5-5", "k", "shortlist/judge", lambda: 1764100000.0)
    req = json.loads((tmp_path / "shortlist/judge/k.request.json").read_text())
    meta = json.loads((tmp_path / "shortlist/judge/k.meta.json").read_text())
    assert req["system"] == "SYS" and req["stdin"] == "USER" and "--model" in req["argv"] and "--tools" in req["argv"]
    assert seen["input"] == "USER" and seen["cwd"] != str(tmp_path)
    assert meta["model_reported"] == ["claude-sonnet-5-5"] and meta["called_at_utc"].endswith("Z") and meta["error"] is None
    assert (tmp_path / "shortlist/judge/k.response.txt").read_text().startswith("{") and res["error"] is None


def test_prompt_file_fills_its_placeholders():
    system, user = claude_judge.fill((js3kit.ROOT / "prompts" / "js3_claims_v1.md").read_text(), TITLE="T1", LOCATION="L1", TEXT="X1")
    assert system.startswith("You read one job posting") and "Title: T1" in user and "{{" not in user
