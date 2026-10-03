#!/usr/bin/env python3
"""Offline tests for daily_check.py — no network, fixtures only. Exits 0 when every test passes.

    python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/test_daily_check.py

Unit tests cover the pieces that decide things (timeline factor, experience parsing, location,
title filters, board links, sponsorship lookup against the real CSV). End-to-end tests run the
real command on the fixtures with DAILY_CHECK_OFFLINE=1, which makes any network call an error,
and check the failure cases the recipe names (F1–F10) end the way the recipe says.
"""
import csv
import datetime as dt
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SCRIPT = Path(os.environ.get("DAILY_CHECK_SCRIPT") or HERE / "daily_check.py").resolve()   # break_attempts.py points this at a mutant
FIX = HERE / "fixtures"
PERSONA_CANDIDATE = REPO / "search" / "examples" / "atharva" / "daily-check.candidate.json"
spec = importlib.util.spec_from_file_location("daily_check", SCRIPT)
dc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dc)

CAND = {"families": sorted([{"phrase": p, "fit": 0.7, "soc": None} for p in
                            ("data analyst", "business intelligence analyst", "business analyst",
                             "analytics engineer", "data engineer")], key=lambda f: -len(f["phrase"])),
        "exclude_title_words": ["senior", "sr", "lead", "manager", "intern", "iii"],
        "flag_title_words": ["ii"], "max_years": 3}


def run_cli(*args, env_extra=None):
    env = dict(os.environ, DAILY_CHECK_OFFLINE="1", **(env_extra or {}))
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=REPO, capture_output=True, text=True, env=env)


def labeled_values(obj, path="$"):
    """Every {value, source} pair anywhere in the log."""
    if isinstance(obj, dict):
        if "value" in obj and "source" in obj:
            yield path, obj
        for k, v in obj.items():
            yield from labeled_values(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from labeled_values(v, f"{path}[{i}]")


class Units(unittest.TestCase):
    def test_timeline_factor(self):
        today, cliff = dt.date(2026, 10, 1), dt.date(2026, 12, 10)
        self.assertEqual(dc.timeline_factor(today, cliff, 8, 21)[:2], (0.667, dt.date(2026, 11, 26)))   # 14 days slack
        self.assertEqual(dc.timeline_factor(today, cliff, 12, 21)[0], 0.0)    # starts after the cliff
        self.assertEqual(dc.timeline_factor(today, cliff, 4, 21)[0], 1.0)     # slack ≥ buffer
        self.assertEqual(dc.timeline_factor(today, cliff, 8, 0)[0], 1.0)      # no buffer wanted, slack ≥ 0

    def test_runway_takes_the_earlier_cliff_and_counts_days_since_as_of(self):
        v = {"opt_end_date": dt.date(2026, 12, 30), "unemployment_days_used": 20,
             "unemployment_days_as_of": dt.date(2026, 9, 21), "unemployment_limit_days": 90}
        r = dc.runway(v, dt.date(2026, 10, 1))
        self.assertEqual(r["unemployment_days_used_today"], 30)               # 20 + 10 days still unemployed
        self.assertEqual(r["cliff"], dt.date(2026, 11, 30))
        self.assertEqual(r["binding"], "unemployment allowance")
        v["unemployment_days_used"] = 0
        v["unemployment_days_as_of"] = dt.date(2026, 10, 1)
        self.assertEqual(dc.runway(v, dt.date(2026, 10, 1))["binding"], "OPT end date")

    def test_parse_experience(self):
        cases = {
            "You have 2+ years of experience with SQL.": "within",
            "0-2 years of experience in analytics": "within",
            "3-5 years of experience in business analysis": "mixed",
            "5+ years of experience building data models": "above",
            "At least 4 years of professional experience": "above",
            "minimum of two (2) years of relevant experience": "within",
            "Bachelor's plus 5 years of experience, or a Master's plus 3 years of experience": "mixed",
            "We have been profitable for 10 years. Join us.": "not-stated",
            "A 4 year degree and SQL experience": "not-stated",
            "&lt;p&gt;6+ years of experience&lt;/p&gt;": "above",           # Greenhouse sends escaped HTML
        }
        for text, want in cases.items():
            with self.subTest(text=text):
                self.assertEqual(dc.parse_experience(text, 3)[0], want)

    def test_classify_location(self):
        cases = [
            ((["San Francisco, CA"],), "us"), ((["US-Remote"],), "us-remote"), ((["Remote - USA"],), "us-remote"),
            ((["Chicago"],), "us"), ((["London"],), "non-us"), ((["Toronto, ON"],), "non-us"),
            ((["US / Canada"],), "us"), ((["Dublin, London"],), "non-us"), ((["New Mexico"],), "us"),
            ((["Remote"],), "remote-unverified"), ((["N/A"],), "unverified"), ((["N/A", "US"],), "us"),
            ((["Remote"], True, ["United States"]), "us-remote"), ((["Toronto, ON"], False, ["Canada"]), "non-us"),
            ((["Bengaluru"],), "non-us"), ((["Indianapolis, IN"],), "us"),
        ]
        for args, want in cases:
            with self.subTest(args=args):
                self.assertEqual(dc.classify_location(*args), want)

    def test_match_title(self):
        fam, excl, flag = dc.match_title("Associate Data Analyst", CAND)
        self.assertEqual((fam["phrase"], excl, flag), ("data analyst", [], []))
        self.assertEqual(dc.match_title("Business Intelligence Analyst", CAND)[0]["phrase"], "business intelligence analyst")
        self.assertEqual(dc.match_title("Sr. Data Engineer", CAND)[1], ["sr"])
        self.assertEqual(dc.match_title("Data Analyst II", CAND)[2], ["ii"])
        self.assertEqual(dc.match_title("Data Analyst III", CAND)[1], ["iii"])
        self.assertIsNone(dc.match_title("Software Engineer, Data Platform", CAND)[0])
        self.assertIsNone(dc.match_title("Data Scientist", CAND)[0])

    def test_resolve_board(self):
        self.assertEqual(dc.resolve_board("https://job-boards.greenhouse.io/Stripe"), ("greenhouse", "stripe"))
        self.assertEqual(dc.resolve_board("https://boards.greenhouse.io/airbnb/jobs/123"), ("greenhouse", "airbnb"))
        self.assertEqual(dc.resolve_board("https://boards-api.greenhouse.io/v1/boards/figma/jobs"), ("greenhouse", "figma"))
        self.assertEqual(dc.resolve_board("https://jobs.ashbyhq.com/Jasper%20AI"), ("ashby", "Jasper AI"))
        self.assertIsNone(dc.resolve_board("https://adobe.wd5.myworkdayjobs.com/en-US/external"))   # F8
        self.assertIsNone(dc.resolve_board("not a url"))


class SponsorshipAgainstRealCsv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ix = dc.SponsorIndex(dc.SPONSOR_CSV)
        with open(dc.SPONSOR_CSV, encoding="utf-8", errors="replace", newline="") as f:
            cls.rows = {r["company_name"].strip(): r for r in csv.DictReader(f)}

    def test_proven_values_are_the_csv_row(self):
        r = self.ix.lookup({"name": "Stripe"}, CAND["families"])
        row = self.rows["STRIPE INC"]
        self.assertEqual(r["status"], "record")
        self.assertEqual(r["csv_row"]["value"], "STRIPE INC")
        self.assertEqual(r["approvals"]["value"], float(row["Total Approvals"]))
        self.assertEqual(r["tier"]["value"], "Proven")
        self.assertEqual(r["p"], {"value": 0.9, "source": "record", "note": r["p"]["note"]})

    def test_f1_no_row_is_unknown_with_a_hint_never_zero(self):
        r = self.ix.lookup({"name": "Notion"}, CAND["families"])     # legal name is NOTION LABS INC
        self.assertEqual(r["status"], "no-row")
        self.assertNotIn("p", r)
        self.assertTrue(any("NOTION LABS INC" in s for s in r["did_you_mean"]))
        self.assertEqual(self.ix.lookup({"name": "Northwind Analytics"}, CAND["families"])["status"], "no-row")

    def test_csv_name_override_finds_the_legal_name(self):
        r = self.ix.lookup({"name": "Notion", "csv_name": "NOTION LABS INC"}, CAND["families"])
        self.assertEqual((r["status"], r["tier"]["value"], r["match_method"]["source"]), ("record", "Proven", "your-input"))

    def test_f2_row_without_h1b_fields_is_unknown(self):
        r = self.ix.lookup({"name": "Coinbase", "csv_name": "COINBASE GLOBAL INC"}, CAND["families"])
        self.assertEqual(r["status"], "no-h1b-fields")
        self.assertNotIn("p", r)

    def test_f6_identical_records_are_not_trusted(self):
        r = self.ix.lookup({"name": "Apricus Biosciences"}, CAND["families"])
        self.assertEqual(r["status"], "duplicate-record")
        self.assertIn("ASCUS BIOSCIENCES INC", r["twins"])
        self.assertNotIn("p", r)

    def test_similar_name_trap_is_flagged(self):
        r = self.ix.lookup({"name": "Chime"}, CAND["families"])      # CHIME INC (2 approvals) vs CHIME FINANCIAL INC
        self.assertEqual((r["csv_row"]["value"], r["tier"]["value"]), ("CHIME INC", "Likely"))
        self.assertTrue(any("CHIME FINANCIAL" in s for s in r["similar_names_with_h1b"]))
        self.assertTrue(any("similar name" in f for f in r["flags"]))


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="daily-check-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def sample(self, *extra):
        p = run_cli("--sample", "--out-dir", str(self.tmp / "out"), *extra)
        self.assertEqual(p.returncode, 0, p.stderr)
        day = self.tmp / "out" / dc.SAMPLE_TODAY
        return json.loads((day / "daily-check.json").read_text()), day

    def test_sample_run_end_to_end(self):
        log, day = self.sample()
        for f in ("daily-check.json", "daily-check.md", "roles.json", "role-scores.json", "role-scores.md"):
            self.assertTrue((day / f).exists(), f)
        md = (day / "daily-check.md").read_text()
        self.assertTrue(md.startswith("# Daily job check"))
        self.assertTrue(md.split("\n## ")[1].startswith("Executive summary"))     # first section, before any table
        # the EXISTING scorer produced the decisions (not a copy)
        scores = json.loads((day / "role-scores.json").read_text())
        self.assertEqual(scores["_scorer"], "bayesian-role-scorer")
        self.assertEqual(log["scorer"]["command"][1], "scripts/score/role-scorer.mjs")
        # every labeled value carries an allowed label, and there are plenty of them
        pairs = list(labeled_values(log))
        self.assertGreater(len(pairs), 100)
        for path, v in pairs:
            self.assertIn(v["source"], dc.SOURCES, path)
        for r in json.loads((day / "roles.json").read_text()):
            for term in ("sponsorship", "fit", "liveness", "timeline"):
                self.assertIn(r[term]["source"], dc.SOURCES, (r["role_id"], term))

        P = {p["key"]: p for p in log["postings"]}
        final = {k: p["decision"]["final"] for k, p in P.items()}
        self.assertEqual(final["greenhouse:stripe:9100001"], "Apply")
        self.assertEqual(final["ashby:notion:n0t10n00-0001"], "Apply")          # csv_name override → Proven
        self.assertEqual(final["greenhouse:chime:9800001"], "Consider")         # Likely tier = soft spot
        # F4 (timeline): expected start after the cliff → the scorer's timeline gate closes
        r = P["greenhouse:roblox:9600001"]
        self.assertEqual((r["decision"]["final"], r["decision"]["decided_by"]), ("Skip", "scorer"))
        self.assertIn("gated: timeline", r["scorer"]["reason"])
        # F7: not E-Verify enrolled → the recipe's gate skips it even though the scorer said Apply
        m = P["greenhouse:moloco:9500001"]
        self.assertEqual((m["decision"]["final"], m["decision"]["decided_by"], m["scorer"]["recommendation"]),
                         ("Skip", "recipe gate: E-Verify", "Apply"))
        # E-Verify not recorded → held, with the scorer's view shown as a preview only
        self.assertEqual(final["greenhouse:pinterest:9700001"], "Held")
        self.assertIn("scorer", P["greenhouse:pinterest:9700001"])
        # F1 / F2 / F6: no sponsorship value is invented — held, and never sent to the scorer
        role_ids = {r["role_id"] for r in json.loads((day / "roles.json").read_text())}
        for key in ("greenhouse:coinbase:9200001", "greenhouse:northwind-analytics:9300001",
                    "greenhouse:apricus-biosciences:9400001"):
            self.assertEqual(final[key], "Held", key)
            self.assertIsNone(P[key]["sponsorship_vote"], key)
            self.assertNotIn(key, role_ids, key)
        # filters: senior, London, 5+ years (F10), intern, Toronto are out; 3-5 yrs and unstated stay, flagged
        for gone in ("greenhouse:stripe:9100002", "greenhouse:stripe:9100003", "greenhouse:stripe:9100004",
                     "greenhouse:stripe:9100008", "ashby:benchling:b1a2c3d4-0002", "greenhouse:stripe:9100006"):
            self.assertNotIn(gone, P)
        self.assertEqual(P["greenhouse:stripe:9100005"]["experience"]["value"], "mixed")
        self.assertEqual(P["greenhouse:stripe:9100007"]["experience"]["value"], "not-stated")
        self.assertTrue(any("open 108 days" in f for f in P["greenhouse:stripe:9100007"]["flags"]))
        self.assertEqual(P["greenhouse:stripe:9100009"]["location"]["value"], "us")   # from the office name "US"
        # F8 / F9: unsupported board and unreadable board are reported, not skipped silently
        nc = {n["company"]: n["reason"] for n in log["not_checked"]}
        self.assertIn("not Greenhouse or Ashby", nc["Adobe"])
        self.assertIn("could not be read", nc["Dropbox"])
        # sponsor on record with nothing open → a networking target
        self.assertEqual([n["company"] for n in log["network_targets"]], ["Databricks"])
        # the timeline is shown with the dates that produced it
        self.assertEqual(P["greenhouse:stripe:9100001"]["timeline"]["expected_start"], "2026-11-26")
        self.assertEqual(log["runway"]["cliff"]["value"], "2026-12-17")

    def test_second_run_reports_new_and_closed_and_leaves_unread_boards_alone(self):
        boards = self.tmp / "boards"
        shutil.copytree(FIX / "boards", boards)
        common = ["--candidate", str(PERSONA_CANDIDATE), "--targets", str(FIX / "targets.sample.json"),
                  "--boards-dir", str(boards), "--out-dir", str(self.tmp / "out")]
        self.assertEqual(run_cli(*common, "--today", "2026-10-01").returncode, 0)
        stripe = json.loads((boards / "greenhouse-stripe.json").read_text())
        stripe["jobs"] = [j for j in stripe["jobs"] if j["id"] != 9100001]           # filled / taken down
        new = dict(stripe["jobs"][0], id=9100010, title="Associate Data Analyst",
                   absolute_url="https://job-boards.greenhouse.io/stripe/jobs/9100010",
                   content="&lt;p&gt;0-2 years of experience.&lt;/p&gt;", location={"name": "Austin, TX"})
        stripe["jobs"].append(new)
        (boards / "greenhouse-stripe.json").write_text(json.dumps(stripe))
        (boards / "greenhouse-chime.json").unlink()                                    # F9 on day 2
        p = run_cli(*common, "--today", "2026-10-02")
        self.assertEqual(p.returncode, 0, p.stderr)
        log = json.loads((self.tmp / "out" / "2026-10-02" / "daily-check.json").read_text())
        closed = {c["key"] for c in log["closed_since_last_run"]}
        self.assertEqual(closed, {"greenhouse:stripe:9100001"})                        # chime NOT closed: board unread
        P = {p["key"]: p for p in log["postings"]}
        self.assertTrue(P["greenhouse:stripe:9100010"]["new"])
        self.assertFalse(P["greenhouse:stripe:9100009"]["new"])
        self.assertEqual(P["greenhouse:stripe:9100009"]["first_seen"], "2026-10-01")
        state = json.loads((self.tmp / "out" / "state.json").read_text())
        self.assertEqual(state["postings"]["greenhouse:stripe:9100001"]["status"], "closed")
        self.assertEqual(state["postings"]["greenhouse:chime:9800001"]["status"], "open")

    def test_f4_past_opt_date_stops_at_the_intake_gate(self):
        p = run_cli("--sample", "--candidate", str(FIX / "candidate.expired.fictional.json"), "--out-dir", str(self.tmp / "out"))
        self.assertEqual(p.returncode, 2)
        self.assertIn("OPT end date 2026-09-15 is not after today", p.stderr)
        day = self.tmp / "out" / dc.SAMPLE_TODAY
        self.assertIn("stopped early", (day / "daily-check.md").read_text())
        self.assertFalse((day / "roles.json").exists())

    def test_missing_value_stops_instead_of_defaulting(self):
        c = json.loads((PERSONA_CANDIDATE).read_text())
        c["visa"]["unemployment_days_used"] = None
        f = self.tmp / "candidate.json"
        f.write_text(json.dumps(c))
        p = run_cli("--sample", "--candidate", str(f), "--out-dir", str(self.tmp / "out"))
        self.assertEqual(p.returncode, 2)
        self.assertIn("unemployment_days_used is missing", p.stderr)

    def test_sponsorship_override_is_labeled_your_input(self):
        t = json.loads((FIX / "targets.sample.json").read_text())
        for c in t["companies"]:
            if c["name"] == "Coinbase":
                c["sponsorship_override"] = {"tier": "Likely", "source": "SYNTHETIC: recruiter said so"}
        f = self.tmp / "targets.json"
        f.write_text(json.dumps(t))
        log, day = self.sample("--targets", str(f))
        roles = {r["role_id"]: r for r in json.loads((day / "roles.json").read_text())}
        self.assertEqual(roles["greenhouse:coinbase:9200001"]["sponsorship"],
                         {"p": 0.6, "tier": "Likely", "source": "your-input"})

    def test_offline_guard_blocks_any_network_call(self):
        p = run_cli("--candidate", str(PERSONA_CANDIDATE), "--targets", str(FIX / "targets.sample.json"),
                    "--out-dir", str(self.tmp / "out"), "--today", "2026-10-01")          # no --boards-dir → would fetch
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("network fetch attempted while DAILY_CHECK_OFFLINE=1", p.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
