"""FILTER.md v0.2: each change C1–C6 on tiny synthetic postings (a pass case and a fail or
unknown case), the rule modes, v0.1 reproduction, and single-change isolation on the saved run.

The corpus checks run every mode on evidence/runs/live-text-1 (committed). They compare modes
with each other only; no hand labels are read here.
"""

import hashlib
import json
import re

import pytest

from agent import PROJECT_DIR
from agent import filter as flt
from agent.postings import load_run, normalize_ashby, normalize_greenhouse
from agent.text import html_blocks, normalize, plain_blocks, strip_html

FILLER = " Our team builds products." * 10  # pads text past the 200-character minimum
PERSONA = {"skills": ["Python", "Java", "TypeScript", "SQL", "PostgreSQL", "Spring Boot", "React", "Docker", "AWS"],
           "target_titles": ["Software Engineer", "AI Engineer", "Backend Engineer"],
           "years_experience": 0, "needs_sponsorship": True, "work_country": "US"}
RUN = PROJECT_DIR / "evidence" / "runs" / "live-text-1"
# sha256 of out/filter-v0.1/results.jsonl as built in step 1 (commit 6cc68807) and recorded in
# out/filter-v0.1/sheet-key.json before any hand label existed.
V01_RESULTS_SHA256 = "8f18b3b4d0c36900093e6c665be4026df4f941ed8ef17b17b384caa4e8ea11ef"


def posting(text, title="Software Engineer", locations=("San Francisco, CA",), blocks=None, block_kinds=None):
    p = {"board": "greenhouse/stripe", "id": 1, "title": title, "locations": list(locations),
         "text": text, "date": "2026-11-20", "url": "https://example.com/job"}
    if blocks is not None:
        p["blocks"] = blocks
    if block_kinds is not None:
        p["block_kinds"] = block_kinds
    return p


def run(mode, text, **kw):
    return flt.evaluate(posting(text, **kw), PERSONA, flt.RULE_MODES[mode])


def g4(mode, text, **kw):
    return run(mode, text, **kw)["gates"]["G4"]


SCORED = "Backend API work in Python and Java."  # topic 2, skills 2: keeps whenever the gates pass


# ---------- rule modes ----------

def test_rule_modes_are_v01_v02_and_one_per_change():
    assert set(flt.RULE_MODES) == {"v0.1", "v0.2", *(f"v0.1+C{i}" for i in range(1, 7))}
    assert flt.RULE_MODES["v0.1"] == frozenset()
    assert flt.RULE_MODES["v0.2"] == frozenset({"C1", "C2", "C3", "C4", "C5", "C6"})
    for i in range(1, 7):
        assert flt.RULE_MODES[f"v0.1+C{i}"] == frozenset({f"C{i}"})


def test_unknown_mode_is_refused(tmp_path):
    with pytest.raises(SystemExit) as err:
        flt.main(["--run", str(RUN), "--out", str(tmp_path / "o"), "--rules", "v0.3"])
    assert err.value.code == 2 and not (tmp_path / "o").exists()


# ---------- C1: no stated experience passes G4 ----------

def test_c1_pass_no_stated_experience():
    text = SCORED + FILLER
    assert g4("v0.1", text)["result"] == "unknown"
    assert g4("v0.1+C1", text)["result"] == "pass"
    assert run("v0.1+C1", text)["verdict"] == "keep"


def test_c1_does_not_rescue_short_text_or_a_failing_minimum():
    short = run("v0.1+C1", "Backend API in Python.")          # under 200 characters
    assert short["gates"]["G4"]["result"] == "unknown" and short["verdict"] == "cannot_tell"
    assert g4("v0.1+C1", "Requires 5+ years of Go. " + SCORED + FILLER)["result"] == "fail"


# ---------- C2: a stated maximum that 0 years satisfies ----------

@pytest.mark.parametrize("phrase", ["You have less than two years of engineering experience.",
                                    "Up to 3 years of experience.", "No more than 1 year in industry.",
                                    "less than 2 years of experience"])
def test_c2_pass_maximum(phrase):
    text = phrase + " " + SCORED + FILLER
    assert g4("v0.1+C2", text)["result"] == "pass"
    assert any(m.startswith("max: ") for m in g4("v0.1+C2", text)["matched"])


def test_c2_without_c2_is_unknown_and_minimum_still_decides():
    text = "You have less than two years of engineering experience. " + SCORED + FILLER
    assert g4("v0.1", text)["result"] == "unknown"
    # a conflicting mandatory minimum decides; the maximum never overrides it
    both = "Less than 2 years of experience in Go. Requires 5+ years of backend work. " + SCORED + FILLER
    assert g4("v0.1+C2", both)["result"] == "fail"
    # 0 years cannot satisfy "less than 0 years"
    assert g4("v0.1+C2", "Less than 0 years of experience. " + SCORED + FILLER)["result"] == "fail"


def test_c2_number_inside_a_maximum_is_not_a_minimum():
    text = "Less than 5 years of experience. " + SCORED + FILLER
    assert g4("v0.1", text)["result"] == "fail"           # v0.1 reads "5 years of" as a minimum
    gate = g4("v0.1+C2", text)
    assert gate["result"] == "pass" and gate["matched"] == ["max: Less than 5 years"]


# ---------- C3: cutoff 3 -> 2 ----------

def test_c3_cutoff_is_two():
    three, two = "Requires 3+ years. " + SCORED + FILLER, "Requires 2+ years. " + SCORED + FILLER
    assert g4("v0.1", three)["result"] == "pass"
    assert g4("v0.1+C3", three)["result"] == "fail"
    assert g4("v0.1+C3", two)["result"] == "pass"
    assert run("v0.1+C3", two)["verdict"] == "keep"


# ---------- C4: every mandatory minimum, mixed -> unknown, preferred ignored ----------

def test_c4_pass_range_counts_by_lower_bound():
    text = "Minimum requirements 2–12+ years of industry experience. " + SCORED + FILLER
    assert g4("v0.1+C4", text)["result"] == "pass"


def test_c4_mixed_minimums_are_unknown_and_all_above_fail():
    mixed = "Requires 2+ years of Python. Requires 5+ years of Go. " + SCORED + FILLER
    assert g4("v0.1", mixed)["result"] == "fail"          # v0.1: the largest minimum decides
    assert g4("v0.1+C4", mixed)["result"] == "unknown"
    assert run("v0.1+C4", mixed)["verdict"] == "cannot_tell"
    above = "Requires 4+ years of Python. Requires 5+ years of Go. " + SCORED + FILLER
    assert g4("v0.1+C4", above)["result"] == "fail"


@pytest.mark.parametrize("word", ["preferred", "nice to have", "a bonus", "a plus"])
def test_c4_minimum_in_a_preferred_sentence_is_ignored(word):
    text = f"Requires 1+ years of Python. 5+ years of Go is {word}. " + SCORED + FILLER
    gate = g4("v0.1+C4", text)
    assert gate["result"] == "pass"
    assert "ignored (preferred): 5+ years" in gate["matched"]
    assert g4("v0.1", text)["result"] == "fail"


REQ_BLOCKS = ["Minimum requirements", "1+ years of Python", "Preferred qualifications", "5+ years of Go",
              SCORED + FILLER]
REQ_KINDS = ["heading", "item", "heading", "item", "text"]


def test_c4_minimum_under_a_preferred_heading_is_ignored():
    """FILTER.md v0.2 C4 (amended 2026-11-23): a preferred heading marks its items as preferred."""
    gate = g4("v0.1+C4", " ".join(REQ_BLOCKS), blocks=REQ_BLOCKS, block_kinds=REQ_KINDS)
    assert gate["result"] == "pass"
    assert gate["matched"] == ["1+ years", "ignored (preferred): 5+ years"]
    assert g4("v0.1", " ".join(REQ_BLOCKS))["result"] == "fail"          # v0.1: the largest minimum, 5


def test_c4_minimum_under_minimum_requirements_counts():
    blocks = ["Minimum Requirements", "4+ years of experience as an engineer", SCORED + FILLER]
    gate = g4("v0.1+C4", " ".join(blocks), blocks=blocks, block_kinds=["heading", "item", "text"])
    assert gate["result"] == "fail" and gate["matched"] == ["4+ years"]


def test_c4_heading_change_ends_the_preferred_scope():
    blocks = ["Nice to have", "1+ years of Rust", "Who you are", "5+ years of Go", SCORED + FILLER]
    kinds = ["text", "item", "text", "item", "text"]   # short, unpunctuated <p>/line headings
    gate = g4("v0.1+C4", " ".join(blocks), blocks=blocks, block_kinds=kinds)
    assert gate["result"] == "fail"
    assert gate["matched"] == ["5+ years", "ignored (preferred): 1+ years"]


def test_c4_heading_definition():
    assert flt.is_heading("Preferred qualifications", "text")       # short <p> or Ashby line
    assert flt.is_heading("NICE TO HAVE", "text")
    assert flt.is_heading("A heading with many more than eight words in it here", "heading")  # <h1>–<h6>
    assert not flt.is_heading("Preferred qualifications", "item")   # a list item is never a heading
    assert not flt.is_heading("Payments experience is preferred.", "text")   # ends with "."
    assert not flt.is_heading("one two three four five six seven eight nine", "text")  # 9 words


def test_c4_no_block_structure_means_no_headings():
    """Without block kinds there are no headings: only the minimum's own sentence counts."""
    with_blocks = g4("v0.1+C4", " ".join(REQ_BLOCKS), blocks=REQ_BLOCKS)
    assert with_blocks["result"] == "unknown"                              # 1 and 5 are both mandatory
    assert with_blocks["detail"] == "mandatory minimums on both sides of 3 years"
    # Without blocks the flat text is one sentence containing "Preferred", so both are ignored.
    assert g4("v0.1+C4", " ".join(REQ_BLOCKS))["detail"] == "only preferred minimums stated"
    only_preferred = ["Preferred qualifications: 5+ years of Go.", SCORED + FILLER]
    gate = g4("v0.1+C4", " ".join(only_preferred), blocks=only_preferred)
    assert gate["result"] == "unknown" and gate["detail"] == "only preferred minimums stated"


def test_greenhouse_block_kinds_from_html():
    content = ("&lt;h3&gt;Preferred qualifications&lt;/h3&gt;&lt;ul&gt;&lt;li&gt;5+ years of Go&lt;/li&gt;&lt;/ul&gt;"
               "&lt;p&gt;&lt;strong&gt;Nice to Have&lt;/strong&gt;&lt;/p&gt;&lt;p&gt;We are a team.&lt;/p&gt;")
    p = normalize_greenhouse("greenhouse/stripe", {"id": 1, "title": "SE", "content": content}, with_blocks=True)
    assert p["blocks"] == ["Preferred qualifications", "5+ years of Go", "Nice to Have", "We are a team."]
    assert p["block_kinds"] == ["heading", "item", "text", "text"]
    a = normalize_ashby("ashby/notion", {"id": "a", "descriptionPlain": "NICE TO HAVE\n\n - 3+ years of Go"},
                        with_blocks=True)
    assert a["block_kinds"] == ["text", "item"] and flt.is_heading(a["blocks"][0], a["block_kinds"][0])


# ---------- C5: "platform" removed from the topic words ----------

def test_c5_platform_is_not_a_topic_word():
    boiler = "Stripe is a financial infrastructure platform for businesses. Requires 2+ years." + FILLER
    assert run("v0.1", boiler)["score"]["topic"]["matched"] == ["infrastructure", "platform"]
    assert run("v0.1", boiler)["verdict"] == "keep"
    after = run("v0.1+C5", boiler)
    assert after["score"]["topic"]["matched"] == ["infrastructure"] and after["verdict"] == "reject"


def test_c5_pass_real_topic_words_still_score():
    text = "Requires 2+ years. " + SCORED + FILLER
    assert run("v0.1+C5", text)["score"] == run("v0.1", text)["score"]
    assert run("v0.1+C5", text)["verdict"] == "keep"


# ---------- C6: "two (2) years" counts as 2 ----------

def test_c6_pass_spelled_plus_digit():
    text = "Two (2) years of experience. " + SCORED + FILLER
    assert g4("v0.1", text)["result"] == "unknown"
    gate = g4("v0.1+C6", text)
    assert gate["result"] == "pass" and gate["matched"] == ["Two (2) years of"]
    assert g4("v0.1+C6", "At least two (2) years in industry. " + SCORED + FILLER)["result"] == "pass"


def test_c6_fail_and_spelled_alone_is_still_not_a_minimum():
    text = "Plus five (5) years of post-bachelor's experience. " + SCORED + FILLER
    assert g4("v0.1+C6", text)["result"] == "fail"
    assert g4("v0.1+C6", "Two years of experience. " + SCORED + FILLER)["result"] == "unknown"


def test_c6_keeps_preferred_and_maximum_roles():
    preferred = "Requires 1+ years. Five (5) years of Go is preferred. " + SCORED + FILLER
    assert g4("v0.2", preferred)["result"] == "pass"
    maximum = "Less than two (2) years of experience. " + SCORED + FILLER
    gate = g4("v0.2", maximum)
    assert gate["result"] == "pass" and gate["matched"] == ["max: Less than two (2) years"]


def test_v02_combines_every_change():
    text = "Requires 3+ years. " + SCORED + FILLER
    assert g4("v0.2", text)["result"] == "fail"           # C3
    assert g4("v0.2", SCORED + FILLER)["result"] == "pass"  # C1


# ---------- blocks ----------

def test_html_blocks_join_back_to_strip_html():
    content = ("&lt;h3&gt;Minimum &lt;em&gt;requirements&lt;/em&gt;&lt;/h3&gt;&lt;ul&gt;&lt;li&gt;2+ years"
               "&lt;/li&gt;&lt;li&gt;Python&lt;br/&gt;Go&lt;/li&gt;&lt;/ul&gt;")
    blocks = html_blocks(content)
    assert blocks == ["Minimum requirements", "2+ years", "Python", "Go"]
    assert normalize(" ".join(blocks)) == strip_html(content)
    assert plain_blocks("A\n\n - B  c\n\n") == ["A", "- B c"]


def test_blocks_only_when_asked():
    gh = {"id": 1, "title": "SE", "content": "&lt;p&gt;One.&lt;/p&gt;&lt;p&gt;Two.&lt;/p&gt;"}
    assert "blocks" not in normalize_greenhouse("greenhouse/stripe", gh)
    assert normalize_greenhouse("greenhouse/stripe", gh, with_blocks=True)["blocks"] == ["One.", "Two."]
    ab = {"id": "a", "descriptionPlain": "One.\nTwo."}
    assert normalize_ashby("ashby/notion", ab, with_blocks=True)["blocks"] == ["One.", "Two."]
    assert normalize_ashby("ashby/notion", {"id": "b", "descriptionPlain": " "}, with_blocks=True)["blocks"] is None


# ---------- the saved run: v0.1 reproduction and single-change isolation ----------

@pytest.fixture(scope="module")
def corpus():
    postings, failures = load_run(RUN, with_blocks=True)
    assert not failures and len(postings) == 979
    persona = flt.load_persona(flt.DEFAULT_PERSONA)
    results = {mode: [flt.evaluate(p, persona, rules) for p in postings] for mode, rules in flt.RULE_MODES.items()}
    return postings, results


def test_blocks_join_back_to_text_for_every_posting(corpus):
    postings, _ = corpus
    for p in postings:
        assert (p["blocks"] is None) == (p["text"] is None) == (p["block_kinds"] is None)
        assert p["blocks"] is None or len(p["blocks"]) == len(p["block_kinds"])
        if p["text"] is not None:
            assert normalize(" ".join(p["blocks"])) == p["text"]


def test_v01_mode_reproduces_step1_results_exactly(corpus, tmp_path):
    _, results = corpus
    body = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in results["v0.1"])
    assert hashlib.sha256(body.encode("utf-8")).hexdigest() == V01_RESULTS_SHA256
    assert flt.main(["--run", str(RUN), "--out", str(tmp_path / "o"), "--rules", "v0.1"]) == 0
    assert hashlib.sha256((tmp_path / "o" / "results.jsonl").read_bytes()).hexdigest() == V01_RESULTS_SHA256
    summary = json.loads((tmp_path / "o" / "summary.json").read_text())
    assert summary["filter_version"] == "0.1" and "rules" not in summary


def _changed(results, mode):
    return [(a, b) for a, b in zip(results["v0.1"], results[mode]) if a != b]


@pytest.mark.parametrize("mode", [f"v0.1+C{i}" for i in range(1, 7)])
def test_single_change_never_touches_g1_g2_g3_g5(corpus, mode):
    _, results = corpus
    for a, b in zip(results["v0.1"], results[mode]):
        for gate in ("G1", "G2", "G3", "G5"):
            assert a["gates"][gate] == b["gates"][gate]


@pytest.mark.parametrize("mode", ["v0.1+C1", "v0.1+C2", "v0.1+C3", "v0.1+C4", "v0.1+C6"])
def test_g4_changes_leave_the_score_terms_alone(corpus, mode):
    _, results = corpus
    for a, b in zip(results["v0.1"], results[mode]):
        if a["score"] is not None and b["score"] is not None:
            assert a["score"] == b["score"]


def test_c1_changes_only_unknown_g4_with_nothing_stated(corpus):
    _, results = corpus
    changed = _changed(results, "v0.1+C1")
    assert changed
    for a, b in changed:
        assert a["gates"]["G4"]["result"] == "unknown" and a["text_status"] == "ok"
        assert b["gates"]["G4"]["result"] == "pass" and b["gates"]["G4"]["matched"] == []


def test_c2_changes_only_postings_with_a_maximum(corpus):
    postings, results = corpus
    by_key = {(p["board"], p["id"]): p for p in postings}
    changed = _changed(results, "v0.1+C2")
    assert changed
    for a, b in changed:
        assert flt.g4_maximums(by_key[(a["board"], a["id"])]["text"], {"C2"})
        assert any(m.startswith("max: ") for m in b["gates"]["G4"]["matched"])


def test_c3_changes_only_a_largest_minimum_of_three(corpus):
    _, results = corpus
    changed = _changed(results, "v0.1+C3")
    assert changed
    flipped = 0
    for a, b in changed:
        ga, gb = a["gates"]["G4"], b["gates"]["G4"]
        assert ga["matched"] == gb["matched"]
        if ga["result"] != gb["result"]:      # only a largest minimum of exactly 3 flips
            flipped += 1
            assert ga["detail"] == "largest stated minimum is 3 years (<= 3)" and gb["result"] == "fail"
        else:                                 # otherwise only the cutoff named in the detail differs
            assert ga["detail"].replace("(> 3)", "(> 2)").replace("(<= 3)", "(<= 2)") == gb["detail"]
            assert a["verdict"] == b["verdict"]
    assert flipped


def test_c4_changes_only_postings_with_a_stated_minimum(corpus):
    _, results = corpus
    changed = _changed(results, "v0.1+C4")
    assert changed
    for a, b in changed:
        assert a["gates"]["G4"]["matched"], "C4 only re-reads stated minimums"
        assert a["gates"]["G4"] != b["gates"]["G4"]


def test_c5_changes_only_the_topic_term(corpus):
    _, results = corpus
    changed = _changed(results, "v0.1+C5")
    assert changed
    for a, b in changed:
        assert a["gates"] == b["gates"]
        assert "platform" in a["score"]["topic"]["matched"]
        assert b["score"]["topic"]["matched"] == [w for w in a["score"]["topic"]["matched"] if w != "platform"]
        assert a["score"]["skills"] == b["score"]["skills"]


def test_c6_changes_only_postings_with_a_spelled_plus_digit_form(corpus):
    postings, results = corpus
    by_key = {(p["board"], p["id"]): p for p in postings}
    form = re.compile(r"\(\s*\d+\s*\)\s*\+?\s*(?:[-–—]\s*\S+\s*)?years", re.IGNORECASE)
    changed = _changed(results, "v0.1+C6")
    assert changed
    for a, b in changed:
        assert form.search(by_key[(a["board"], a["id"])]["text"])
        assert a["gates"]["G4"] != b["gates"]["G4"]
