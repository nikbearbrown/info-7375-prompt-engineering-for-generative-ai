"""agent/claims.py and tools/label_claims.py: the prompt contract, strict reply validation,
quote checks, one retry, the blind claim sheet, and the claim labeler. Offline: the API client
here is a fake that returns canned replies; no test calls Claude."""

import copy
import csv
import json
from types import SimpleNamespace

import pytest

from agent import PROJECT_DIR
from agent import claims as cl
from tools import label_claims as lc
from tools.label import LabelError

TEXT = ("Software Engineer. You will build backend services in Python. "
        "Requires 2+ years of experience. Based in San Francisco, CA. "
        "Visa sponsorship is available for this role.")
POSTING = {"board": "greenhouse/acme", "id": 42, "title": "Software Engineer", "locations": ["San Francisco, CA"],
           "text": TEXT, "blocks": [TEXT], "date": "2026-11-01", "url": "https://example.test/42"}
PERSONA = {"skills": ["Python"], "target_titles": ["Software Engineer"], "years_experience": 0,
           "needs_sponsorship": True, "work_country": "US"}
GOOD = {"posting_id": "42", "claims": [
    {"kind": "role", "claim": "The role is software engineering.", "quote": "Software Engineer.",
     "proposed_label": "supported"},
    {"kind": "location", "claim": "The job is in the US.", "quote": "Based in San Francisco, CA.",
     "proposed_label": "supported"},
    {"kind": "experience", "claim": "At most 2 years required.", "quote": "Requires 2+ years of experience.",
     "proposed_label": "supported"},
    {"kind": "sponsorship", "claim": "The employer sponsors visas.",
     "quote": "Visa sponsorship is available for this role.", "proposed_label": "supported"},
]}


def reply(data):
    return json.dumps(data)


def mutated(fn):
    data = copy.deepcopy(GOOD)
    fn(data)
    return reply(data)


# ---------------------------------------------------------------- the prompt contract

def test_prompt_has_filter_md_definitions_word_for_word():
    prompt, sha = cl.load_prompt()
    filter_md = (PROJECT_DIR / "FILTER.md").read_text(encoding="utf-8").splitlines()
    for line in filter_md:
        for label in cl.LABELS:
            if line.startswith(f"| **{label}** |"):
                definition = line.split("|")[2].strip()
                assert f"- {label}: {definition}" in prompt
    assert next(ln for ln in filter_md if ln.startswith("**Relevance is not entailment.**")) in prompt
    assert len(sha) == 64


def test_model_and_sdk_pin_are_inherited_from_js1():
    js1 = PROJECT_DIR.parent / "js1-contract-and-watch"
    config = json.loads((js1 / "config.json").read_text())
    assert cl.MODEL == config["model"] == "claude-sonnet-5-5" and cl.MAX_TOKENS == config["max_tokens"]
    pins = {ln.replace(" ", "") for ln in (js1 / "requirements.txt").read_text().splitlines() if "anthropic" in ln}
    assert "anthropic==2.3.0" in pins
    assert "anthropic==2.3.0" in (PROJECT_DIR / "requirements.txt").read_text().splitlines()


def test_request_carries_the_posting_and_no_credentials(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-a-real-key")
    req = cl.build_request(POSTING, PERSONA, "SYSTEM")
    payload = json.loads(req["messages"][0]["content"])
    assert payload["posting_id"] == "42" and payload["posting_text"] == TEXT
    assert set(payload["cole"]) == {"target_titles", "years_experience", "needs_sponsorship", "work_country", "skills"}
    assert req["model"] == "claude-sonnet-5-5" and req["system"] == "SYSTEM"
    assert req["output_config"]["format"]["schema"] == cl.OUTPUT_SCHEMA
    assert "sk-test" not in json.dumps(req)


# ---------------------------------------------------------------- validator: one rejection per rule

def test_valid_reply_passes():
    assert cl.validate_reply(reply(GOOD), "42") == GOOD


@pytest.mark.parametrize("text, reason", [
    (None, "no text"),
    ("   ", "no text"),
    ("Here are the claims: " + reply(GOOD), "not only JSON"),
    (reply(GOOD) + "\nThanks!", "not only JSON"),
    ("[1, 2]", "not a JSON object"),
    (mutated(lambda d: d.pop("claims")), "top-level keys"),
    (mutated(lambda d: d.update(extra=1)), "top-level keys"),
    (mutated(lambda d: d.update(posting_id=42)), "posting_id is not a string"),
    (mutated(lambda d: d.update(posting_id="43")), "is not '42'"),
    (mutated(lambda d: d.update(claims={"a": 1})), "claims is not a list"),
    (mutated(lambda d: d.update(claims=d["claims"][:2])), "2 claims; must be 3 to 6"),
    (mutated(lambda d: d.update(claims=d["claims"] + d["claims"][:3])), "7 claims; must be 3 to 6"),
    (mutated(lambda d: d["claims"].__setitem__(0, "a string")), "claim 0 is not an object"),
    (mutated(lambda d: d["claims"][0].pop("quote")), "claim 0 keys"),
    (mutated(lambda d: d["claims"][0].update(confidence=0.9)), "claim 0 keys"),
    (mutated(lambda d: d["claims"][0].update(kind="salary")), "kind 'salary'"),
    (mutated(lambda d: d["claims"][0].update(proposed_label="likely")), "proposed_label 'likely'"),
    (mutated(lambda d: d["claims"][0].update(claim="  ")), "empty claim"),
    (mutated(lambda d: d["claims"][0].update(quote=None)), "quote is not a string"),
    (mutated(lambda d: d["claims"][0].update(quote="")), "empty quote but label 'supported'"),
])
def test_validator_rejects(text, reason):
    with pytest.raises(cl.ClaimsValidationError, match=reason):
        cl.validate_reply(text, "42")


@pytest.mark.parametrize("kind", cl.REQUIRED_KINDS)
def test_validator_requires_each_required_kind(kind):
    def drop(d):
        for c in d["claims"]:
            if c["kind"] == kind:
                c["kind"] = "skill"
    with pytest.raises(cl.ClaimsValidationError, match=f"no claim of kind \\['{kind}'\\]"):
        cl.validate_reply(mutated(drop), "42")


def test_empty_quote_with_insufficient_is_valid():
    text = mutated(lambda d: d["claims"][3].update(quote="", proposed_label="insufficient"))
    assert cl.validate_reply(text, "42")["claims"][3]["quote"] == ""


# ---------------------------------------------------------------- quote checks

def test_quote_not_found_is_flagged_never_accepted():
    claims = copy.deepcopy(GOOD["claims"])
    claims[0]["quote"] = "Senior Software Engineer."                         # not in the text
    claims[1]["quote"] = "Based in  San Francisco, CA."                       # whitespace differs
    claims[2]["quote"] = "Requires 2+ years of experience"                    # exact substring
    claims[3]["quote"] = ""
    checked = cl.check_quotes(claims, TEXT)
    assert [c["quote_found"] for c in checked] == [False, False, True, None]
    assert [c["flags"] for c in checked] == [["quote_not_found"], ["quote_not_found"], [], []]


# ---------------------------------------------------------------- one retry, then failed

class FakeClient:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []
        self.messages = SimpleNamespace(create=self.create)

    def create(self, **request):
        self.calls.append(request)
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        text, stop = r if isinstance(r, tuple) else (r, "end_turn")
        return SimpleNamespace(
            model="claude-sonnet-5-5", stop_reason=stop,
            content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
            usage=SimpleNamespace(input_tokens=1000, output_tokens=200, cache_creation_input_tokens=0,
                                  cache_read_input_tokens=0))


META = {"label": cl.LIVE_LABEL, "prompt_sha256": "x" * 64}


def test_invalid_reply_gets_one_retry_with_the_same_request(tmp_path):
    client = FakeClient(["not json", reply(GOOD)])
    rec = cl.claims_for(client, POSTING, PERSONA, "SYSTEM", tmp_path / "raw", META, now=lambda: "T")
    assert rec["status"] == "ok" and len(rec["attempts"]) == 2
    assert client.calls[0] == client.calls[1]
    assert "not only JSON" in rec["attempts"][0]["reason"]
    assert rec["usage"]["input_tokens"] == 2000 and rec["usage"]["output_tokens"] == 400
    assert sorted(p.name for p in (tmp_path / "raw").iterdir()) == [
        "greenhouse-acme-42-attempt1-request.json", "greenhouse-acme-42-attempt1-response.json",
        "greenhouse-acme-42-attempt2-request.json", "greenhouse-acme-42-attempt2-response.json"]


def test_two_invalid_replies_record_a_failure(tmp_path):
    client = FakeClient([mutated(lambda d: d.update(claims=[])), ("{}", "refusal")])
    rec = cl.claims_for(client, POSTING, PERSONA, "SYSTEM", tmp_path / "raw", META, now=lambda: "T")
    assert rec["status"] == "failed" and len(client.calls) == 2 and "claims" not in rec
    assert rec["failure"] == "stop_reason refusal"


def test_api_error_counts_as_an_invalid_attempt(tmp_path):
    client = FakeClient([ConnectionError("down"), reply(GOOD)])
    rec = cl.claims_for(client, POSTING, PERSONA, "SYSTEM", tmp_path / "raw", META, now=lambda: "T")
    assert rec["status"] == "ok" and rec["attempts"][0]["reason"] == "API call failed: ConnectionError"


def test_raw_request_is_saved_with_timestamp_and_no_key(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-a-real-key")
    cl.claims_for(FakeClient([reply(GOOD)]), POSTING, PERSONA, "SYSTEM", tmp_path, META, now=lambda: "2026-11-23T23:00:00-05:00")
    saved = (tmp_path / "greenhouse-acme-42-attempt1-request.json").read_text()
    assert json.loads(saved)["sent_at"] == "2026-11-23T23:00:00-05:00" and "sk-test" not in saved


def test_run_refuses_without_live_flag(capsys):
    assert cl.main(["run"]) == 2
    assert "--live" in capsys.readouterr().out


def test_cost_estimate():
    usage = {"input_tokens": 1_000_000, "output_tokens": 100_000, "cache_creation_input_tokens": 0,
             "cache_read_input_tokens": 0}
    assert cl.cost_usd(usage) == pytest.approx(2.0 + 1.0)


# ---------------------------------------------------------------- the blind sheet

def records():
    good = cl.check_quotes(copy.deepcopy(GOOD["claims"]), TEXT)
    good[0] = {**good[0], "quote": "missing words", "quote_found": False, "flags": ["quote_not_found"]}
    return [{"board": "greenhouse/acme", "posting_id": "42", "title": "Software Engineer", "status": "ok",
             "claims": good},
            {"board": "greenhouse/acme", "posting_id": "43", "title": "Failed One", "status": "failed"}]


@pytest.fixture()
def sheet(tmp_path):
    info = cl.build_sheet(records(), {("greenhouse/acme", "42"): POSTING}, root=tmp_path,
                          key_path=tmp_path / "out" / "claims-key.json")
    return tmp_path, info


def test_sheet_hides_proposed_label(sheet):
    root, info = sheet
    with open(root / "labels" / "claims-sheet.csv", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert tuple(reader.fieldnames) == cl.SHEET_COLUMNS
    assert "proposed_label" not in reader.fieldnames
    assert all(set(r) == set(cl.SHEET_COLUMNS) for r in rows)
    assert len(rows) == info["rows"] == 4 and {r["posting_id"] for r in rows} == {"42"}   # failed posting skipped
    assert [r["quote_found"] for r in rows] == ["no", "yes", "yes", "yes"]
    assert all(r["my_label"] == "" and r["note"] == "" for r in rows)
    key = json.loads((root / "out" / "claims-key.json").read_text())
    assert [k["proposed_label"] for k in key["rows"]] == ["supported"] * 4
    assert key["rows"][0]["flags"] == ["quote_not_found"]


def test_sheet_refuses_to_overwrite(sheet):
    root, _ = sheet
    with pytest.raises(FileExistsError):
        cl.build_sheet(records(), {("greenhouse/acme", "42"): POSTING}, root=root, key_path=root / "out" / "k.json")


# ---------------------------------------------------------------- the claim labeler

def test_labeler_refuses_a_sheet_that_shows_proposed_label(tmp_path):
    bad = tmp_path / "labels" / "claims-sheet.csv"
    bad.parent.mkdir()
    bad.write_text(",".join(cl.SHEET_COLUMNS + ("proposed_label",)) + "\n1,42,t,role,c,q,yes,,,supported\n")
    with pytest.raises(LabelError, match="unblind"):
        lc.read_sheet(bad)


def test_labeler_shows_paragraph_or_first_800(sheet):
    root, _ = sheet
    blocks = ["Intro paragraph.", "Requires 2+ years of experience. More here.", "x" * 900]
    shown, why = lc.context_for(blocks, "2+ years of experience")
    assert shown == "Requires 2+ years of experience. More here." and why.startswith("the paragraph")
    shown, why = lc.context_for(blocks, "")
    assert len(shown) == 801 and why.startswith("quote is empty")
    _, why = lc.context_for(blocks, "not in the text")
    assert why.startswith("QUOTE NOT FOUND")
    assert lc.text_blocks(root / "labels" / "claims-sheet.csv", "42") == [TEXT]


def test_labeler_writes_once_and_corrects_with_history(sheet):
    root, _ = sheet
    path = root / "labels" / "claims-sheet.csv"
    keys = iter(["s", "", "i", "nice to have", "q"])
    out = []
    lc.label_session(path, ask=lambda _: next(keys), say=out.append, now=lambda: "2026-11-23T23:10:00-05:00")
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    assert [r["my_label"] for r in rows] == ["supported", "insufficient", "", ""]
    assert rows[1]["note"] == "nice to have" and rows[0]["labeled_at"] == "2026-11-23T23:10:00-05:00"
    with pytest.raises(LabelError, match="written once"):
        lc.write_label(path, "1", "contradicted", "", "T")
    note = lc.correct_label(path, "1", "contradicted", "re-read", "2026-11-24T08:00:00-05:00")
    assert note == "[corrected 2026-11-24: was supported (labeled 2026-11-23T23:10:00-05:00)] re-read"
    with pytest.raises(LabelError, match="no label yet"):
        lc.correct_label(path, "3", "supported", "", "T")


def test_labeler_never_reads_out(tmp_path):
    (tmp_path / "out").mkdir()
    sheet = tmp_path / "out" / "claims-sheet.csv"
    sheet.write_text(",".join(cl.SHEET_COLUMNS) + "\n")
    with pytest.raises(LabelError, match="blind labeling"):
        lc.read_sheet(sheet)
