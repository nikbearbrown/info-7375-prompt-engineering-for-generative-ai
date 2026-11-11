"""One test per wrong version in CONTRACT.md (Wrong versions), numbered to match. Each test runs the real code on a
fixture and asserts the property that wrong version breaks. Run: python tests/run_tests.py (or pytest)."""
from __future__ import annotations

import builtins
import io
import json
from pathlib import Path

from harness import (CFG, CUT_V1, DROP_V1, GOOD_REQ, PERSONA, job, ok_stdout, quiet, read_jsonl, sentences,
                     stub_claude, temp_root, verdict, write_board)

from agent import claude_judge, config, fetch, labels, lines, persona, rule, state, watch

SF = "San Francisco, CA"
BASE_JOBS = [job(101, "Recruiter", "Dublin, Ireland", "<p>Hiring experience.</p>"),
             job(102, "Account Executive", "London", "<p>Sales experience.</p>")]


def seeded_pair(root: Path, new_jobs: list[dict]):
    """Seeded baseline on BASE_JOBS, then a seeded run on BASE_JOBS + new_jobs. Returns the later board's path."""
    watch.run(root, "seeded", write_board(root, "earlier", BASE_JOBS), log=quiet)
    later = write_board(root, "later", BASE_JOBS + new_jobs)
    watch.run(root, "seeded", later, log=quiet)
    return later


def _checker(root):
    return lambda line: lines.check(line, root, config.load(root), PERSONA, lines.BoardCache(root))


# Title and seniority -------------------------------------------------------------------------------------------

def test_wv_01():
    r = verdict("Senior Machine Learning Engineer", SF, GOOD_REQ)
    assert r["rule_checks"]["skill_overlap"]["passed"] and r["rule_checks"]["title_match"]["passed"]
    assert r["rule_checks"]["seniority_ok"]["seniority_token"] == "senior"
    assert r["rule_verdict"] == "not_relevant"


def test_wv_02():
    r = verdict("Sr. Software Engineer - ML", SF, GOOD_REQ)
    assert r["rule_checks"]["seniority_ok"]["seniority_token"] == "sr"
    assert r["rule_verdict"] == "not_relevant"


def test_wv_03():
    t = rule.title_check("HTML Email Developer", PERSONA)
    assert t["matched_keyword"] is None and not t["passed"]


def test_wv_04():
    r = verdict("Software Engineer - Machine Learning", SF, GOOD_REQ)
    assert r["rule_checks"]["title_match"] == {"passed": True, "matched_keyword": "machine learning", "exclusion_hit": None}
    assert r["rule_verdict"] == "relevant"


def test_wv_05():
    a = rule.title_check("Account Executive, AI/ML", PERSONA)
    b = rule.title_check("Solutions Architect - Data Engineering", PERSONA)
    assert a["matched_keyword"] and a["exclusion_hit"] == "account" and not a["passed"]
    assert b["matched_keyword"] and b["exclusion_hit"] == "solutions" and not b["passed"]


# Location ------------------------------------------------------------------------------------------------------

def test_wv_06():
    assert rule.location_check("San Francisco, California", PERSONA) == {"passed": True, "matched": "san francisco"}


def test_wv_07():
    assert not rule.location_check("Remote - Australia", PERSONA)["passed"]
    assert rule.location_check("Remote - United States", PERSONA)["passed"]      # the allowed remote case still passes


def test_wv_08():
    assert not rule.location_check("United States", PERSONA)["passed"]


# Years ---------------------------------------------------------------------------------------------------------

def test_wv_09():
    # Separate fixtures: the rule takes the minimum, so a wrong 10 next to a right 2 would hide behind the 2.
    founded = sentences("<p>We were founded 10 years ago.</p><ul><li>Experience with Python and SQL</li></ul>")
    ranged = sentences("<ul><li>2–4 years of experience with Python</li></ul>")
    assert rule.years_required(founded) is None
    assert rule.years_required(ranged) == 2


def test_wv_10():
    s = sentences("<ul><li>Our team has 100+ years of combined experience</li><li>Python</li></ul>")
    assert rule.years_required(s) is None


def test_wv_11():
    s = sentences("<ul><li>BS + 6 years, MS + 4 years, PhD + 2 years of experience</li></ul>")
    assert rule.years_required(s) == 6


def test_wv_12():
    curly = sentences("<ul><li>Master’s degree + 1 year of experience, or 6+ years of experience</li></ul>")
    entity = sentences("<ul><li>Master&rsquo;s degree + 1 year of experience, or 6+ years of experience</li></ul>")
    assert rule.years_required(curly) == 6 and rule.years_required(entity) == 6


# Text preparation and skills -----------------------------------------------------------------------------------

def test_wv_13():
    s = sentences("<ul><li>3+ years of experience with Python and SQL</li><li>Spark, Kafka and Airflow</li>"
                  "<li>We are the original creators of Apache Spark&trade; and Delta Lake</li>"
                  "<li>Mentor new hires for 1 year</li></ul>")
    assert rule.years_required(s) == 3
    assert rule.posting_skills(s, CFG.vocab) == ["python", "sql", "spark", "airflow", "kafka"]
    assert not any("original creators of" in x for x in s)


def test_wv_14():
    s = sentences("<p>Requirements: Python, SQL, Spark.</p><h3>Benefits:</h3><p>Kafka and Airflow training</p>")
    assert rule.posting_skills(s, CFG.vocab) == ["python", "sql", "spark"]


def test_wv_15():
    s = sentences("<p>Databricks is the data and AI company, founded by the original creators of Apache Spark™.</p>"
                  "<p>You know Python and SQL.</p><h3>Pay Range Transparency</h3><p>Spark and Kafka</p>")
    assert rule.posting_skills(s, CFG.vocab) == ["python", "sql"]


def test_wv_16():
    s = sentences("<p>Experience in R&amp;D teams using Python and SQL on the Databricks platform.</p>")
    assert rule.posting_skills(s, CFG.vocab) == ["python", "sql"]
    assert not {"r", "go", "c", "databricks"} & set(CFG.vocab)


def test_wv_17():
    r = verdict("Data Engineer", SF, "<ul><li>Java, Terraform, Python, SQL and Spark</li></ul>")
    sk = r["rule_checks"]["skill_overlap"]
    assert "java" in sk["posting_skills"] and set(sk["matched"]) <= set(PERSONA["skills"])
    with temp_root() as root, stub_claude([ok_stdout()]):
        seeded_pair(root, [job(201, "Data Engineer", SF, GOOD_REQ)])
        line = read_jsonl(root / "output" / "verdicts.jsonl")[0]
        line["rule_checks"]["skill_overlap"]["matched"].append("java")
        line["rule_checks"]["skill_overlap"]["posting_skills"].append("java")
        assert any("not in persona skills" in e for e in _checker(root)(line))


def test_wv_18():
    with temp_root() as root, stub_claude([ok_stdout()]):
        seeded_pair(root, [job(201, "Data Engineer", SF, GOOD_REQ), job(202, "Data Engineer", "Austin, TX", GOOD_REQ)])
        out = read_jsonl(root / "output" / "verdicts.jsonl")
        for line in out:
            assert (line["rule_verdict"] == "relevant") == all(c["passed"] for c in line["rule_checks"].values())
        good = next(x for x in out if x["rule_verdict"] == "relevant")
        good["rule_checks"]["location_ok"]["passed"] = False
        assert any("disagrees with the four" in e for e in _checker(root)(good))


def test_wv_19():
    with temp_root() as root, stub_claude([ok_stdout()]):
        later = seeded_pair(root, [job(201, "Data Engineer", SF, GOOD_REQ), job(202, "ML Engineer", SF, GOOD_REQ)])
        titles = {j["id"]: j["title"] for j in json.loads((root / later).read_text())["jobs"]}
        out = read_jsonl(root / "output" / "verdicts.jsonl")
        assert [(x["posting_id"], x["posting_title"]) for x in out] == [(201, titles[201]), (202, titles[202])]
        out[0]["posting_title"] = titles[202]
        assert any("do not match" in e for e in _checker(root)(out[0]))


# Claude step ---------------------------------------------------------------------------------------------------

def test_wv_20():
    empty = ok_stdout(cited_resume_fields=[])
    assert claude_judge.validate_output(empty.encode())[0] is None
    with temp_root() as root, stub_claude([empty]):
        seeded_pair(root, [job(201, "Data Engineer", SF, GOOD_REQ)])
        line = read_jsonl(root / "output" / "verdicts.jsonl")[0]
        assert line["claude_status"] == "invalid_output"
        line.update(claude_status="ok", claude_verdict="relevant", claude_justification="x",
                    claude_cited_resume_fields=[], claude_cited_posting_fields=["content"])
        assert any("cited-field" in e for e in _checker(root)(line))


def test_wv_21():
    answer = json.loads(json.loads(ok_stdout())["result"])
    fenced = json.dumps({"is_error": False, "result": "```json\n" + json.dumps(answer) + "\n```"})
    cased = ok_stdout(verdict="Relevant")
    prose = json.dumps({"is_error": False, "result": "Here is my answer: " + json.dumps(answer)})
    extra = ok_stdout(confidence=0.9)
    for bad in (fenced, cased, prose, extra):
        assert claude_judge.validate_output(bad.encode())[0] is None


def test_wv_22():
    with temp_root() as root, stub_claude(["not json at all"]) as calls:
        seeded_pair(root, [job(201, "Data Engineer", SF, GOOD_REQ)])
        out = read_jsonl(root / "output" / "verdicts.jsonl")
        fails = read_jsonl(root / "output" / "claude_failures.jsonl")
        assert len(calls()) == 2 and len(out) == 1
        assert out[0]["claude_status"] == "invalid_output" and out[0]["rule_verdict"] == "relevant"
        assert out[0]["claude_verdict"] is None and out[0]["claude_justification"] is None
        assert fails[0]["posting_id"] == 201 and len(fails[0]["raw_paths"]) == 2
        assert all((root / p).exists() for p in fails[0]["raw_paths"])


def test_wv_23():
    with temp_root() as root, stub_claude([ok_stdout("relevant")]):
        seeded_pair(root, [job(201, "Account Executive, AI", "Austin, TX", GOOD_REQ)])
        line = read_jsonl(root / "output" / "verdicts.jsonl")[0]
        assert (line["rule_verdict"], line["rule_label"]) == ("not_relevant", "record")
        assert (line["claude_verdict"], line["claude_label"]) == ("relevant", "judgment")
        line["claude_label"] = "record"
        assert any("claude_label" in e for e in _checker(root)(line))


def test_wv_24():
    with temp_root() as root, stub_claude([ok_stdout()]) as calls:
        seeded_pair(root, [job(201, "Data Engineer", SF, GOOD_REQ)])
        call = calls()[0]
        argv = call["argv"]
        assert argv[argv.index("--model") + 1] == CFG.claude_model
        assert argv[argv.index("--tools") + 1] == ""
        assert not Path(call["cwd"]).resolve().is_relative_to(root.resolve()) and call["cwd_listing"] == []
        assert read_jsonl(root / "output" / "verdicts.jsonl")[0]["claude_model"] == CFG.claude_model


def test_wv_25():
    with temp_root() as root, stub_claude(["<ECHO>"]) as calls:
        seeded_pair(root, [job(201, "Data Engineer – Payments™", SF,
                               GOOD_REQ + "<p>Café analytics experience with Python.</p>")])
        sent = bytes.fromhex(calls()[0]["stdin_hex"]).decode("utf-8")
        assert "–" in sent and "™" in sent and "é" in sent


# State and runs ------------------------------------------------------------------------------------------------

def test_wv_26():
    with temp_root() as root:
        summary = watch.run(root, "seeded", write_board(root, "earlier", BASE_JOBS), log=quiet)
        st = state.load(state.path_for(root, "seeded"))
        assert summary["baseline"] and summary["new"] == 0
        assert st["seen_ids"] == [101, 102] and not (root / "output" / "verdicts.jsonl").exists()


def test_wv_27():
    with temp_root() as root, stub_claude([ok_stdout()]) as calls:
        seeded_pair(root, [job(201, "Data Engineer", SF, GOOD_REQ),
                           job(202, "Data Engineer", SF, "<h3>In-office expectations</h3><p>Python, SQL</p>")])
        before = len(calls())
        summary = watch.run(root, "seeded", "boards/later.json", log=quiet)
        assert summary["new"] == 0 and len(calls()) == before
        assert len(read_jsonl(root / "output" / "skipped.jsonl")) == 1
        assert len(read_jsonl(root / "output" / "verdicts.jsonl")) == 1


def test_wv_28():
    with temp_root() as root, stub_claude([ok_stdout()]):
        watch.run(root, "seeded", write_board(root, "earlier", BASE_JOBS), log=quiet)
        later = write_board(root, "later", BASE_JOBS + [job(201, "Data Engineer", SF, GOOD_REQ),
                                                        job(202, "ML Engineer", SF, GOOD_REQ)])
        real, n = claude_judge.judge, {"calls": 0}

        def crash_on_second(*a, **k):
            n["calls"] += 1
            if n["calls"] == 2:
                raise RuntimeError("simulated crash")
            return real(*a, **k)

        claude_judge.judge = crash_on_second
        try:
            watch.run(root, "seeded", later, log=quiet)
            raise AssertionError("the simulated crash did not happen")
        except RuntimeError:
            pass
        finally:
            claude_judge.judge = real
        assert state.load(state.path_for(root, "seeded"))["runs"][-1]["completed_at"] is None
        watch.run(root, "seeded", later, log=quiet)
        good, bad = lines.read_valid(root, config.load(root), PERSONA)
        assert sorted(x["posting_id"] for x in good) == [201, 202]
        assert len(bad) == 1 and "never completed" in bad[0][1][0]


def test_wv_29():
    with temp_root() as root, stub_claude([ok_stdout()]):
        live = state.path_for(root, "live")
        state.save(live, {"seen_ids": [101], "baseline_run_id": "earlier-live", "runs": []})
        before = live.read_bytes()
        real_open, fetch._open = fetch._open, lambda *a, **k: (_ for _ in ()).throw(AssertionError("network used"))
        try:
            first = watch.run(root, "seeded", write_board(root, "earlier", BASE_JOBS), log=quiet)
            watch.run(root, "seeded", write_board(root, "later", BASE_JOBS + [job(201, "Data Engineer", SF, GOOD_REQ)]),
                      log=quiet)
        finally:
            fetch._open = real_open
        assert first["baseline"] and live.read_bytes() == before
        line = read_jsonl(root / "output" / "verdicts.jsonl")[0]
        assert line["run_mode"] == "seeded" and line["seeded_from"] == "boards/later.json"


def test_wv_30():
    with temp_root() as root, stub_claude([ok_stdout()]):
        seeded_pair(root, [job(201, "Data Engineer", SF, GOOD_REQ)])
        line = read_jsonl(root / "output" / "verdicts.jsonl")[0]
        check = _checker(root)
        assert check(line) == []
        (root / line["claude_raw_paths"][0]).unlink()
        assert any("claude_raw_paths" in e for e in check(line))
        board = root / "raw" / line["run_id"] / "board.json"
        board.write_bytes(board.read_bytes() + b" ")
        assert any("byte-for-byte" in e for e in _checker(root)(line))


# Safety and persona --------------------------------------------------------------------------------------------

def test_wv_31():
    for url in ("https://stripe.com/jobs/listing/201", "http://boards-api.greenhouse.io/v1/boards/stripe/jobs",
                "https://evil.example/boards-api.greenhouse.io"):
        try:
            fetch.check_allowed(url)
            raise AssertionError(f"allowed {url}")
        except fetch.RefusedHost:
            pass
    try:
        fetch._NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://stripe.com/")
        raise AssertionError("redirect followed")
    except fetch.RefusedHost:
        pass
    seen = []
    body = json.dumps({"jobs": BASE_JOBS}).encode()
    with temp_root() as root:
        real_open, fetch._open = fetch._open, lambda url, timeout: (seen.append(url), (200, body))[1]
        try:
            watch.run(root, "live", log=quiet)
        finally:
            fetch._open = real_open
    assert seen == [config.BOARD_URL]


def test_wv_32():
    with temp_root() as root, stub_claude([ok_stdout()]) as calls:
        seeded_pair(root, [job(202, "Data Engineer", SF, "<h3>In-office expectations</h3><p>Python, SQL</p>")])
        assert not (root / "output" / "verdicts.jsonl").exists() and calls() == []
        assert read_jsonl(root / "output" / "skipped.jsonl")[0]["posting_id"] == 202


def test_wv_33():
    for bad in ({"email": "jordan.lee@gmail.com"}, {"phone": "(617) 555-0142"}):
        assert persona.problems({**PERSONA, **bad}, CFG.vocab)
    assert persona.problems(PERSONA, CFG.vocab) == []


def test_wv_34():
    no_remote = {k: v for k, v in PERSONA.items() if k != "remote_ok"}
    for bad in ({**PERSONA, "skills": PERSONA["skills"] + ["excel"]}, no_remote, {**PERSONA, "address": "1 Main St"}):
        assert persona.problems(bad, CFG.vocab)


# Experiments ---------------------------------------------------------------------------------------------------

def _label_board():
    titles = ["Data Engineer", "ML Engineer", "Data Scientist", "AI Engineer", "Recruiter", "Account Executive"]
    return {"jobs": [job(300 + i, titles[i % len(titles)], SF, GOOD_REQ) for i in range(30)]}


def test_wv_35():
    a, b = labels.select(_label_board(), PERSONA, CFG), labels.select(_label_board(), PERSONA, CFG)
    assert (a["dev"], a["held_out"]) == (b["dev"], b["held_out"]) and len(a["dev"]) == len(a["held_out"]) == 10


def test_wv_36():
    from experiments import runner
    with temp_root() as root, stub_claude([ok_stdout()]):
        board = write_board(root, "pool", _label_board()["jobs"])
        sel = labels.select(json.loads((root / board).read_text()), PERSONA, CFG)
        (root / "experiments" / "output").mkdir(parents=True)
        (root / "experiments" / "output" / "label_selection.json").write_text(json.dumps({"board": board}))
        (root / "labels").mkdir()
        (root / "labels" / "hand_labels.jsonl").write_text("".join(
            json.dumps({"posting_id": i, "split": "dev", "label": "relevant"}) + "\n" for i in sel["dev"]))
        for d in ("state", "output"):
            (root / d).mkdir()
            (root / d / "sentinel.json").write_text("{}")
        touched, real = [], io.open

        def spy(file, *a, **k):
            touched.append(Path(file).resolve() if not isinstance(file, int) else file)
            return real(file, *a, **k)

        io.open = builtins.open = spy
        try:
            runner.score(root, "judge_v1", "dev", log=quiet)
            runner.sample(root, sel["dev"][:1], 2, "judge_v1", log=quiet)
        finally:
            io.open = builtins.open = real
        forbidden = [(root / d).resolve() for d in ("state", "output")]
        assert not [p for p in touched if isinstance(p, Path) and any(p.is_relative_to(f) for f in forbidden)]
        assert sorted(x.name for d in ("state", "output") for x in (root / d).iterdir()) == ["sentinel.json"] * 2
        assert (root / "experiments" / "output" / "experiment_judge_v1_dev.jsonl").exists()
