"""Phase 2e: the held-out draw (FILTER.md section 7) and the labeling helper.

Written by Claude Code (claude-opus-5-5), 2026-11-25. Every posting and sheet here is SEEDED
(hand-built in tmp folders); no test reads labels/heldout.csv.
"""
import ast
import json

import pytest

import js3kit
from jobwatch import heldout, js3cli, label, sheets
from jobwatch.policy import Policy
from jobwatch.tools import PolicyDenied, Tools


def seeded_line(i, title, board="greenhouse:seeded"):
    return {"key": f"{board}:{i}", "board": board, "posting_id": str(i), "url": f"https://example.invalid/{i}",
            "title": title, "location": "Boston", "text": f"SEEDED text {i}.", "fields": [], "sentences": []}


def seeded_dataset(tmp_path, n_a=35, n_b=12, n_other=5):
    lines = [seeded_line(i, f"SEEDED ML Engineer {i}") for i in range(n_a)]
    lines += [seeded_line(100 + i, f"SEEDED Software Engineer {i}", board="ashby:seeded") for i in range(n_b)]
    lines += [seeded_line(200 + i, f"SEEDED Account Executive {i}") for i in range(n_other)]
    (tmp_path / "data").mkdir()
    p = tmp_path / "data" / "postings-SEEDED.jsonl"
    p.write_text("".join(json.dumps(ln) + "\n" for ln in lines))
    return lines


def tools_at(tmp_path, read=("data", "labels", "audit", "shortlist"), write=("labels", "data/texts"), **kw):
    return Tools(Policy(str(tmp_path), read_dirs=read, write_dirs=write), **kw)


# --- strata ------------------------------------------------------------------------------------
@pytest.mark.parametrize("title,expected", [
    ("Machine Learning Engineer", "A"), ("Senior ML Engineer", "A"), ("AI/ML Platform", "A"), ("Data Analyst", "A"),
    ("Software Engineer", "B"), ("Research Engineer", "B"), ("Account Executive", None),
    ("Email Marketing Lead", None),   # "ai" inside "email" is not a whole word
    ("HTML Developer", "B"),          # "ml" inside "html" is not a whole word; "developer" is broad
])
def test_stratum_uses_whole_title_tokens(title, expected):
    assert heldout.stratum(title) == expected


def test_draw_is_deterministic_per_seed_and_independent_of_input_order(tmp_path):
    lines = seeded_dataset(tmp_path)
    _, a = heldout.draw(list(lines), {"A": 1, "B": 2})
    _, b = heldout.draw(list(reversed(lines)), {"A": 1, "B": 2})
    assert [x["key"] for x in a["A"]] == [x["key"] for x in b["A"]] and len(a["A"]) == 30 and len(a["B"]) == 10
    _, c = heldout.draw(list(lines), {"A": 3, "B": 2})
    assert [x["key"] for x in c["A"]] != [x["key"] for x in a["A"]]


def test_heldout_sheet_has_no_filter_output_and_records_sizes_and_seeds(tmp_path):
    seeded_dataset(tmp_path)
    tools = tools_at(tmp_path)
    sizes, rows = heldout.run(tools, "data/postings-SEEDED.jsonl", {"A": 11, "B": 12}, "SEEDED")
    comments, columns, got = sheets.read_sheet(tools, "labels/heldout.csv")
    assert tuple(columns) == heldout.COLUMNS and sizes == {"A": 35, "B": 12}
    assert not {"score", "decision", "matched_rules", "matched", "rules"} & set(columns)
    assert any("pool 35, drawn 30, seed 11" in c for c in comments) and any("pool 12, drawn 10, seed 12" in c for c in comments)
    assert all(r["label"] == "" and r["override_reason"] == "" for r in got) and len(got) == 40
    for r in got:
        body = (tmp_path / r["text_path"]).read_text()
        assert body.startswith("Title: ") and "score" not in body.lower()


def test_heldout_is_drawn_once_and_never_overwritten(tmp_path):
    seeded_dataset(tmp_path)
    tools = tools_at(tmp_path)
    heldout.run(tools, "data/postings-SEEDED.jsonl", {"A": 1, "B": 2}, "SEEDED")
    before = (tmp_path / "labels" / "heldout.csv").read_bytes()
    with pytest.raises(heldout.SealedError):
        heldout.run(tools_at(tmp_path), "data/postings-SEEDED.jsonl", {"A": 9, "B": 9}, "SEEDED")
    assert (tmp_path / "labels" / "heldout.csv").read_bytes() == before


def test_heldout_and_label_modules_never_import_the_filter_or_scorer():
    for mod in ("heldout.py", "label.py", "sheets.py"):
        tree = ast.parse((js3kit.ROOT / "jobwatch" / mod).read_text())
        names = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {f"{n.module}.{a.name}" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module for a in n.names}
        assert not any(("filter" in x or "score" in x or "shortlist" in x or "audit" in x) for x in names), (mod, names)


# --- the labeling helper -----------------------------------------------------------------------
def make_sheet(tmp_path, columns, rows, folder="labels", name="sheet.csv"):
    (tmp_path / folder).mkdir(exist_ok=True)
    (tmp_path / "data" / "texts").mkdir(parents=True, exist_ok=True)
    for r in rows:
        (tmp_path / r["text_path"]).write_text(f"Title: SEEDED {r['posting_key']}\n\n" + "SEEDED body line.\n" * 70)
    path = f"{folder}/{name}"
    (tmp_path / path).write_bytes(sheets.sheet_bytes(["SEEDED comment"], columns, rows))
    return path


def scripted(answers):
    it = iter(answers)
    return lambda prompt: next(it)


def posting_rows(n, extra=None):
    return [{"posting_key": f"g:s:{i}", "group": "close_call", "score": "SCOREVALUE99", "text_path": f"data/texts/t{i}.txt",
             "verdict": "", "override_reason": "", **(extra or {})} for i in range(n)]


def test_label_writes_answers_override_with_reason_and_changes_no_other_cell(tmp_path):
    cols = ["posting_key", "group", "score", "text_path", "verdict", "override_reason"]
    path = make_sheet(tmp_path, cols, posting_rows(3), folder="audit")
    out = []
    # row 1: answer on page 1; row 2: page through then n; row 3: o -> r with a reason
    label.run(tools_at(tmp_path, write=("audit",), allow_rewrite=True), path,
              ask=scripted(["r", "", "", "n", "o", "r", "reads as mid level"]), out=out.append)
    comments, columns, rows = sheets.read_sheet(tools_at(tmp_path), path)
    assert columns == cols and comments == ["SEEDED comment"]
    assert [(r["verdict"], r["override_reason"]) for r in rows] == [
        ("relevant", ""), ("not_relevant", ""), ("relevant", "reads as mid level")]
    assert all(r["group"] == "close_call" and r["score"] == "SCOREVALUE99" for r in rows)
    printed = "\n".join(out)
    assert "SCOREVALUE99" not in printed and "close_call" not in printed


def test_label_resumes_at_the_first_empty_row_and_q_saves_progress(tmp_path):
    cols = ["posting_key", "stratum", "text_path", "label", "override_reason"]
    rows = [{"posting_key": f"k{i}", "stratum": "A", "text_path": f"data/texts/t{i}.txt", "label": "", "override_reason": ""}
            for i in range(3)]
    rows[0]["label"] = "not_relevant"
    path = make_sheet(tmp_path, cols, rows)
    tools = tools_at(tmp_path, write=("labels",), allow_rewrite=True)
    out = []
    label.run(tools, path, ask=scripted(["r", "q"]), out=out.append)
    _, _, got = sheets.read_sheet(tools, path)
    assert [r["label"] for r in got] == ["not_relevant", "relevant", ""]
    assert "1 of 3 rows answered" in out[0]
    assert all("stratum" not in line and "A)" not in line for line in out if "=====" in line)


def test_label_claims_sheet_asks_s_c_i_with_note_and_hides_the_pre_label(tmp_path):
    cols = ["claim_id", "posting_key", "claim", "field", "quote", "pre_label", "text_path", "label", "note"]
    rows = [{"claim_id": "c1", "posting_key": "g:s:1", "claim": "SEEDED uses PyTorch", "field": "text",
             "quote": "PyTorch", "pre_label": "PRELABELVALUE", "text_path": "data/texts/t1.txt", "label": "", "note": ""}]
    path = make_sheet(tmp_path, cols, rows, folder="shortlist")
    out = []
    label.run(tools_at(tmp_path, write=("shortlist",), allow_rewrite=True), path,
              ask=scripted(["i", "quote is boilerplate"]), out=out.append)
    _, _, got = sheets.read_sheet(tools_at(tmp_path), path)
    assert (got[0]["label"], got[0]["note"], got[0]["pre_label"]) == ("insufficient", "quote is boilerplate", "PRELABELVALUE")
    assert "PRELABELVALUE" not in "\n".join(out)


def test_label_cannot_write_outside_the_sheets_folder(tmp_path):
    tools = tools_at(tmp_path, write=("labels",), allow_rewrite=True)
    with pytest.raises(PolicyDenied):
        tools.write_file("audit/x.csv", b"x")


def test_label_command_refuses_a_sheet_outside_the_three_folders(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "x.csv").write_text("label,override_reason\n")
    assert js3cli.main(["label", "x.csv"]) == 1
    assert "must be directly in one of labels, audit, shortlist" in capsys.readouterr().err


# --- clear and the relevance hint (added after the first audit pass had mis-keys) ------------------
def answered_sheet(tmp_path, folder="audit"):
    cols = ["posting_key", "group", "text_path", "verdict", "override_reason"]
    rows = [{"posting_key": f"k{i}", "group": "random_reject", "text_path": f"data/texts/t{i}.txt",
             "verdict": "relevant" if i % 2 else "not_relevant", "override_reason": "why" if i == 1 else ""} for i in range(4)]
    return make_sheet(tmp_path, cols, rows, folder=folder, name="audit-SEEDED.csv"), rows


def test_clear_needs_the_file_name_typed_and_otherwise_changes_nothing(tmp_path):
    path, _ = answered_sheet(tmp_path)
    before = (tmp_path / path).read_bytes()
    out = []
    assert label.clear(tools_at(tmp_path, write=("audit",), allow_rewrite=True), path, ask=scripted(["yes"]), out=out.append) == 1
    assert (tmp_path / path).read_bytes() == before and "unchanged" in out[-1]


def test_clear_empties_only_the_answer_and_reason_columns_and_reports_the_count(tmp_path):
    path, rows = answered_sheet(tmp_path)
    out = []
    assert label.clear(tools_at(tmp_path, write=("audit",), allow_rewrite=True), path,
                       ask=scripted(["audit-SEEDED.csv"]), out=out.append) == 0
    comments, columns, got = sheets.read_sheet(tools_at(tmp_path), path)
    assert all(r["verdict"] == "" and r["override_reason"] == "" for r in got)
    assert [(r["posting_key"], r["group"], r["text_path"]) for r in got] == [(r["posting_key"], r["group"], r["text_path"]) for r in rows]
    assert comments == ["SEEDED comment"] and out[-1].startswith("Cleared 5 cells")


def test_clear_on_a_heldout_style_sheet_uses_label_and_override_reason(tmp_path):
    cols = ["posting_key", "stratum", "text_path", "label", "override_reason"]
    path = make_sheet(tmp_path, cols, [{"posting_key": "k", "stratum": "A", "text_path": "data/texts/t.txt",
                                        "label": "relevant", "override_reason": ""}])
    label.clear(tools_at(tmp_path, write=("labels",), allow_rewrite=True), path, ask=scripted([path]), out=lambda s: None)
    _, _, got = sheets.read_sheet(tools_at(tmp_path), path)
    assert (got[0]["label"], got[0]["stratum"]) == ("", "A")


def test_every_posting_row_starts_with_the_relevance_hint(tmp_path):
    cols = ["posting_key", "group", "score", "text_path", "verdict", "override_reason"]
    path = make_sheet(tmp_path, cols, posting_rows(2), folder="audit")
    out = []
    label.run(tools_at(tmp_path, write=("audit",), allow_rewrite=True), path, ask=scripted(["r", "n"]), out=out.append)
    headers = [i for i, s in enumerate(out) if s.startswith("\n=====")]
    assert len(headers) == 2 and all(out[i + 1] == label.RELEVANT_HINT for i in headers)
    assert label.RELEVANT_HINT == "r = RELEVANT to Riley (worth her time), n = NOT relevant. r does not mean reject."


# --- checklist mode ----------------------------------------------------------------------------
def checklist_sheet(tmp_path, n=4, folder="audit", answer="verdict"):
    cols = ["posting_key", "group", "score", "text_path", answer, "override_reason"]
    rows = [{"posting_key": f"k{i}", "group": "near_decision", "score": "SCOREVALUE99", "text_path": f"data/texts/t{i}.txt",
             answer: "", "override_reason": ""} for i in range(n)]
    path = make_sheet(tmp_path, cols, rows, folder=folder, name="cl.csv")
    for r in rows:  # one page of text, so no page-turn prompts
        (tmp_path / r["text_path"]).write_text(f"Title: SEEDED {r['posting_key']}\n\nSEEDED body.\n")
    return path, cols


def test_checklist_label_is_derived_only_from_the_answers_and_stops_at_the_first_n(tmp_path):
    path, cols = checklist_sheet(tmp_path)
    out = []
    answers = ["y", "y", "y", "",          # row 1: all y -> relevant, no override
               "y", "n", "",               # row 2: seniority n -> not_relevant; location not asked
               "n", "",                    # row 3: family n -> not_relevant
               "y", "y", "n", "o", "r", "remote team explicitly includes Boston"]  # row 4: override
    label.run(tools_at(tmp_path, write=("audit",), allow_rewrite=True), path, ask=scripted(answers), out=out.append, checklist=True)
    _, columns, got = sheets.read_sheet(tools_at(tmp_path), path)
    assert columns == ["posting_key", "group", "score", "text_path", "check_family", "check_seniority", "check_location",
                       "verdict", "override_reason"]
    assert [(r["check_family"], r["check_seniority"], r["check_location"], r["verdict"], r["override_reason"]) for r in got] == [
        ("y", "y", "y", "relevant", ""), ("y", "n", "", "not_relevant", ""), ("n", "", "", "not_relevant", ""),
        ("y", "y", "n", "relevant", "remote team explicitly includes Boston")]
    assert all(r["score"] == "SCOREVALUE99" for r in got)
    printed = "\n".join(out)
    assert "SCOREVALUE99" not in printed and "near_decision" not in printed


def test_checklist_questions_are_asked_in_the_stated_order(tmp_path):
    path, _ = checklist_sheet(tmp_path, n=1)
    prompts = []
    replies = iter(["y", "y", "y", ""])

    def ask(prompt):
        prompts.append(prompt)
        return next(replies)
    label.run(tools_at(tmp_path, write=("audit",), allow_rewrite=True), path, ask=ask, out=lambda s: None, checklist=True)
    asked = [p.strip() for p in prompts if p.strip().endswith("y/n")]
    assert asked == [q for _, q in label.CHECKS]
    assert label.CHECKS[0][1].startswith("Job family: is the job itself ML, AI, data science, LLM or applied ML research work?")


def test_checklist_column_order_is_stable_and_resume_starts_at_the_first_empty_row(tmp_path):
    path, _ = checklist_sheet(tmp_path, n=3, folder="labels", answer="label")
    tools = tools_at(tmp_path, write=("labels",), allow_rewrite=True)
    label.run(tools, path, ask=scripted(["n", "", "q"]), out=lambda s: None, checklist=True)
    _, cols1, rows1 = sheets.read_sheet(tools, path)
    out = []
    label.run(tools, path, ask=scripted(["y", "y", "y", "", "n", ""]), out=out.append, checklist=True)
    _, cols2, rows2 = sheets.read_sheet(tools, path)
    assert cols1 == cols2 and cols1.index("check_family") == cols1.index("label") - 3
    assert "1 of 3 rows answered" in out[0]
    assert [r["label"] for r in rows2] == ["not_relevant", "relevant", "not_relevant"] and rows2[0] == rows1[0]


def test_clear_also_empties_the_check_columns(tmp_path):
    path, _ = checklist_sheet(tmp_path, n=1)
    tools = tools_at(tmp_path, write=("audit",), allow_rewrite=True)
    label.run(tools, path, ask=scripted(["y", "n", ""]), out=lambda s: None, checklist=True)
    label.clear(tools, path, ask=scripted(["cl.csv"]), out=lambda s: None)
    _, _, got = sheets.read_sheet(tools, path)
    assert all(got[0][c] == "" for c in label.CHECK_COLUMNS + ("verdict", "override_reason"))


def test_checklist_on_a_claims_sheet_keeps_the_s_c_i_mode(tmp_path):
    cols = ["claim_id", "posting_key", "claim", "field", "quote", "pre_label", "text_path", "label", "note"]
    rows = [{"claim_id": "c1", "posting_key": "g:s:1", "claim": "SEEDED", "field": "text", "quote": "q",
             "pre_label": "x", "text_path": "data/texts/t1.txt", "label": "", "note": ""}]
    path = make_sheet(tmp_path, cols, rows, folder="shortlist")
    label.run(tools_at(tmp_path, write=("shortlist",), allow_rewrite=True), path, ask=scripted(["s", ""]), out=lambda s: None, checklist=True)
    _, columns, got = sheets.read_sheet(tools_at(tmp_path), path)
    assert columns == cols and got[0]["label"] == "supported"


# --- family mode -------------------------------------------------------------------------------
def family_sheet(tmp_path, specs, folder="audit", answer="verdict", old_checks=False):
    """specs: [(title, location)]. A one-page SEEDED text per row."""
    cols = ["posting_key", "group", "title", "location", "text_path"]
    cols += ["check_family", "check_seniority", "check_location"] if old_checks else []
    cols += [answer, "override_reason"]
    rows = [{"posting_key": f"k{i}", "group": "random_reject", "title": t, "location": loc, "text_path": f"data/texts/t{i}.txt",
             answer: "", "override_reason": "", **({"check_family": "", "check_seniority": "", "check_location": ""} if old_checks else {})}
            for i, (t, loc) in enumerate(specs)]
    path = make_sheet(tmp_path, cols, rows, folder=folder, name="fam.csv")
    for r in rows:
        (tmp_path / r["text_path"]).write_text("Title: SEEDED\n\nSEEDED body.\n")
    return path


@pytest.mark.parametrize("title,expected", [("ML Engineer", "y"), ("Senior ML Engineer", "y"), ("Senior Staff ML Engineer", "n"),
                                            ("ML Engineer Intern", "n"), ("Engineering Manager", "n"), ("Head of AI", "n"),
                                            ("Leadership Program Analyst", "y"), ("Internship, Software", "n"),
                                            ("Software Engineer, Internship - Infrastructure", "n")])
def test_mechanical_seniority_uses_section0_words_as_whole_tokens(title, expected):
    assert label.seniority_title_check(title)[0] == expected


@pytest.mark.parametrize("loc,expected", [("Boston, MA", "y"), ("New York City", "y"), ("NYC", "y"), ("Seattle", "y"),
                                          ("Remote - US", "y"), ("U.S. Remote", "y"), ("Remote", "n"), ("San Francisco", "n"),
                                          ("", "n"), ("N/A", "n"), ("Chicago, Seattle", "y")])
def test_mechanical_location_uses_section0_list(loc, expected):
    assert label.location_check(loc)[0] == expected


def test_family_mode_asks_family_then_experience_only_when_rules_pass(tmp_path):
    path = family_sheet(tmp_path, [("ML Engineer", "Boston"), ("ML Engineer", "San Francisco"), ("Engineering Manager", "Seattle"),
                                   ("Account Executive", "NYC"), ("ML Engineer", "New York")])
    prompts = []
    replies = iter(["y", "y", "",      # row 1: family y, rules pass, experience y -> relevant
                    "y", "",           # row 2: location fails mechanically: no experience question
                    "y", "",           # row 3: seniority fails mechanically
                    "n", "",           # row 4: family n
                    "y", "n", ""])     # row 5: experience n

    def ask(p):
        prompts.append(p)
        return next(replies)
    label.run(tools_at(tmp_path, write=("audit",), allow_rewrite=True), path, ask=ask, out=lambda s: None, family=True)
    _, cols, got = sheets.read_sheet(tools_at(tmp_path), path)
    assert cols == ["posting_key", "group", "title", "location", "text_path", *label.FAMILY_COLUMNS, "verdict", "override_reason"]
    assert [(r["check_family"], r["check_seniority_title"], r["check_location"], r["check_experience"], r["verdict"]) for r in got] == [
        ("y", "y", "y", "y", "relevant"), ("y", "y", "n", "", "not_relevant"), ("y", "n", "y", "", "not_relevant"),
        ("n", "y", "y", "", "not_relevant"), ("y", "y", "y", "n", "not_relevant")]
    assert got[0]["check_source"] == f"mechanical: {label.SENIORITY_SOURCE}, location; asked: family, experience"
    assert got[1]["check_source"] == f"mechanical: {label.SENIORITY_SOURCE}, location; asked: family"
    assert "Internship from section 0's meaning, not its literal word list" in got[0]["check_source"]
    asked = [p.strip() for p in prompts if p.strip().endswith("y/n")]
    assert asked.count(label.FAMILY_Q) == 5 and asked.count(label.EXPERIENCE_Q) == 2


def test_family_override_needs_a_reason_of_at_least_15_characters(tmp_path):
    path = family_sheet(tmp_path, [("Account Executive", "NYC")])
    label.run(tools_at(tmp_path, write=("audit",), allow_rewrite=True), path, out=lambda s: None, family=True,
              ask=scripted(["n", "o", "r", "short", "fifteen chars!", "applied ML work in the text body"]))
    _, _, got = sheets.read_sheet(tools_at(tmp_path), path)
    assert (got[0]["verdict"], got[0]["override_reason"]) == ("relevant", "applied ML work in the text body")


def test_family_mode_replaces_empty_older_check_columns_and_refuses_filled_ones(tmp_path):
    path = family_sheet(tmp_path, [("ML Engineer", "Boston")], old_checks=True)
    tools = tools_at(tmp_path, write=("audit",), allow_rewrite=True)
    label.run(tools, path, ask=scripted(["n", ""]), out=lambda s: None, family=True)
    _, cols, _ = sheets.read_sheet(tools, path)
    assert "check_seniority" not in cols and cols.count("check_location") == 1
    sheet = tmp_path / "audit" / "fam2.csv"
    sheet.write_bytes(sheets.sheet_bytes([], ["posting_key", "title", "location", "text_path", "check_seniority", "verdict", "override_reason"],
                                         [{"posting_key": "k", "title": "t", "location": "Boston", "text_path": "data/texts/t0.txt",
                                           "check_seniority": "y", "verdict": "", "override_reason": ""}]))
    with pytest.raises(ValueError, match="run label --clear first"):
        label.run(tools, "audit/fam2.csv", ask=scripted([]), out=lambda s: None, family=True)


def test_family_mode_prints_no_filter_output_and_resumes(tmp_path):
    path = family_sheet(tmp_path, [("ML Engineer", "Boston"), ("Account Executive", "NYC")], folder="labels", answer="label")
    tools = tools_at(tmp_path, write=("labels",), allow_rewrite=True)
    out = []
    label.run(tools, path, ask=scripted(["n", "", "q"]), out=out.append, family=True)
    label.run(tools, path, ask=scripted(["n", ""]), out=out.append, family=True)
    _, _, got = sheets.read_sheet(tools, path)
    assert [r["label"] for r in got] == ["not_relevant", "not_relevant"]
    assert any("1 of 2 rows answered" in s for s in out)
    assert "random_reject" not in "\n".join(out)


def test_clear_empties_every_check_column(tmp_path):
    path = family_sheet(tmp_path, [("ML Engineer", "Boston")])
    tools = tools_at(tmp_path, write=("audit",), allow_rewrite=True)
    label.run(tools, path, ask=scripted(["y", "y", ""]), out=lambda s: None, family=True)
    label.clear(tools, path, ask=scripted(["fam.csv"]), out=lambda s: None)
    _, _, got = sheets.read_sheet(tools, path)
    assert all(got[0][c] == "" for c in label.FAMILY_COLUMNS + ("verdict", "override_reason"))
