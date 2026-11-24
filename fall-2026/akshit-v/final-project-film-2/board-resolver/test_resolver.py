#!/usr/bin/env python3
"""Offline tests for resolver.py, written from CONTRACT.md before resolver.py existed.

No network: urllib.request.urlopen is patched to raise in every test. All "API responses"
come from fixture transports built here. They are SYNTHETIC, not real board data.

Run from this folder:
  python -m unittest -v test_resolver.py
"""

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import resolver as rs  # noqa: E402

CANDIDATES = os.path.join(HERE, "inputs", "run-2-candidates.json")
BOARDS = os.path.join(HERE, "inputs", "boards.json")

GH = "https://boards-api.greenhouse.io/v1/boards/{}"
LV = "https://api.lever.co/v0/postings/{}?mode=json"
AB = "https://api.ashbyhq.com/posting-api/job-board/{}"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="resolver-test-")
        self.runs = os.path.join(self.tmp, "runs")
        os.makedirs(self.runs)
        p1 = mock.patch.object(rs, "RUNS_ROOT", self.runs)
        p2 = mock.patch("urllib.request.urlopen", side_effect=AssertionError("network call in a test"))
        p1.start(); p2.start()
        self.addCleanup(p1.stop); self.addCleanup(p2.stop)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def fixture(self, responses, default=None):
        path = os.path.join(self.tmp, "fixture.json")
        obj = {"_about": "SYNTHETIC test fixture", "responses": responses}
        if default is not None:
            obj["default"] = default
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        return path

    def main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = rs.main(list(argv))
        self.stdout, self.stderr = out.getvalue(), err.getvalue()
        return code

    def probe(self, fixture, *extra, run="r1"):
        out = os.path.join(self.runs, run)
        code = self.main("probe", "--candidates", CANDIDATES, "--boards", BOARDS,
                         "--fixture", fixture, "--out-dir", out, *extra)
        return code, out

    def company(self, out, name):
        props = load(os.path.join(out, "proposals.json"))
        return next(c for c in props["companies"] if c["company_name"] == name)


# ── slugs ────────────────────────────────────────────────────────────────────
class TestSlugs(unittest.TestCase):
    def test_dev_set_all_16_known_slugs_are_generated(self):
        """Development set: the 16 boards a human confirmed on 2026-10-03."""
        missed = [b["company_name"] for b in load(BOARDS)["boards"]
                  if b["slug"] not in [s for s, _ in rs.slug_candidates(b["company_name"])]]
        self.assertEqual(missed, [])

    def test_suffixes_punctuation_and_slug_shape(self):
        slugs = [s for s, _ in rs.slug_candidates("T-REX GROUP INC")]
        self.assertEqual(slugs[:3], ["trexgroup", "t-rex-group", "trex"])
        for name in ("RISE INTERACTIVE MEDIA & ANALYTICS LLC", "GREEN DOT CORP", "SOFAR SOUNDS LTD"):
            for s, _ in rs.slug_candidates(name):
                self.assertRegex(s, rs.SLUG_RE.pattern)
                self.assertFalse(s.endswith(("llc", "corp", "ltd", "inc")), s)

    def test_aliases_go_first_and_at_most_four_name_slugs(self):
        c = rs.slug_candidates("SOCIAL FINANCE INC", {"SOCIAL FINANCE INC": ["sofi"]})
        self.assertEqual(c[0], ("sofi", "alias"))
        self.assertLessEqual(len([r for _, r in c if r != "alias"]), 4)

    def test_first_word_slug_is_marked_weak(self):
        rules = dict(rs.slug_candidates("UPSTART NETWORK INC"))
        self.assertEqual(rules.get("upstart") in ("descriptor-stripped", "first-word"), True)
        self.assertIn("first-word", dict(rs.slug_candidates("OUTSET MEDICAL INC")).values())


# ── name matching ────────────────────────────────────────────────────────────
class TestNameMatch(unittest.TestCase):
    def test_dev_set_greenhouse_names(self):
        """Real board names recorded at G1 on 2026-10-03: 11 exact, Upstart only partial."""
        got = {b["company_name"]: rs.name_match(b["company_name"], b["board_reported_name"])
               for b in load(BOARDS)["boards"] if b["board_reported_name"]}
        self.assertEqual(got.pop("UPSTART NETWORK INC"), "name-partial")
        self.assertEqual(set(got.values()), {"name-match"})
        self.assertEqual(len(got), 11)

    def test_mismatch(self):
        self.assertEqual(rs.name_match("DV01 INC", "Data Vault One"), "name-mismatch")


# ── permission policy ────────────────────────────────────────────────────────
class TestPolicy(Base):
    def test_policy_allows_only_get_https_three_hosts(self):
        rs.check_policy("GET", GH.format("yext"))
        for method, url in [("GET", "https://example.com/x"), ("GET", "http://api.lever.co/v0/postings/x"),
                            ("POST", GH.format("yext")), ("GET", "https://api.lever.co.evil.com/x")]:
            with self.assertRaises(rs.PolicyError, msg=(method, url)):
                rs.check_policy(method, url)

    def test_no_network_without_live(self):
        code = self.main("probe", "--candidates", CANDIDATES, "--boards", BOARDS,
                         "--out-dir", os.path.join(self.runs, "x"))
        self.assertEqual(code, 3)

    def test_out_dir_outside_runs_refused(self):
        code = self.main("probe", "--candidates", CANDIDATES, "--boards", BOARDS,
                         "--fixture", self.fixture({}), "--out-dir", os.path.join(self.tmp, "elsewhere"))
        self.assertEqual(code, 3)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "elsewhere")))

    def test_bad_alias_slug_is_input_error(self):
        aliases = os.path.join(self.tmp, "aliases.json")
        with open(aliases, "w") as f:
            json.dump({"YEXT INC": ["../../evil"]}, f)
        code, _ = self.probe(self.fixture({}), "--aliases", aliases, "--only", "YEXT INC")
        self.assertEqual(code, 2)


# ── the loop ─────────────────────────────────────────────────────────────────
class TestLoop(Base):
    def test_name_match_is_proposed_raw_saved_and_search_stops_early(self):
        code, out = self.probe(self.fixture({GH.format("yext"): {"status": 200, "body": {"name": "Yext"}}}),
                               "--only", "YEXT INC")
        self.assertEqual(code, 0)
        c = self.company(out, "YEXT INC")
        self.assertEqual(c["status"], "proposed")
        self.assertEqual(c["best"]["outcome"], "name-match")
        self.assertEqual(len(c["probes"]), 1)  # stopped after the strong hit
        raw = load(os.path.join(out, c["best"]["raw_path"]))
        self.assertEqual(sha(raw["body_text"].encode("utf-8")), c["best"]["sha256"])
        summary = load(os.path.join(out, "summary.json"))
        self.assertEqual(summary["stop_reason"], "done")
        self.assertEqual(summary["requests_used"], 3 + 1)  # 3 canaries + 1

    def test_F1_name_collision_is_only_partial_and_search_continues(self):
        code, out = self.probe(self.fixture({GH.format("human"): {"status": 200, "body": {"name": "Human Interest"}}}),
                               "--only", "HUMAN INC")
        c = self.company(out, "HUMAN INC")
        self.assertEqual(c["best"]["outcome"], "name-partial")
        self.assertEqual(len(c["probes"]), 3)  # greenhouse hit didn't stop it; lever + ashby also tried

    def test_F1b_mismatch_only(self):
        code, out = self.probe(self.fixture({GH.format("dv01"): {"status": 200, "body": {"name": "Data Vault One"}}}),
                               "--only", "DV01 INC")
        self.assertEqual(self.company(out, "DV01 INC")["status"], "mismatch-only")

    def test_not_found_everywhere(self):
        code, out = self.probe(self.fixture({}), "--only", "ZANBATO INC")
        c = self.company(out, "ZANBATO INC")
        self.assertEqual(c["status"], "not-found")
        self.assertEqual(len(c["probes"]), 3 * len(rs.slug_candidates("ZANBATO INC")))

    def test_F2_rate_limit_streak_stops_and_is_not_a_miss(self):
        canaries = {u.format(rs.CANARY_SLUG): {"status": 404, "body": {}} for u in (GH, LV, AB)}
        code, out = self.probe(self.fixture(canaries, default={"status": 429, "body": "slow down"}),
                               "--only", "ZANBATO INC", "--max-errors", "3")
        self.assertEqual(code, 5)
        self.assertEqual(load(os.path.join(out, "summary.json"))["stop_reason"], "upstream-errors")
        self.assertEqual(self.company(out, "ZANBATO INC")["status"], "incomplete")

    def test_F3_malformed_json_is_an_error(self):
        code, out = self.probe(self.fixture({GH.format("yext"): {"status": 200, "body": "<html>not json"}}),
                               "--only", "YEXT INC")
        p = self.company(out, "YEXT INC")["probes"][0]
        self.assertEqual((p["outcome"], p["detail"]), ("error", "malformed-json"))

    def test_F4_budget_stop(self):
        code, out = self.probe(self.fixture({}), "--only", "ZANBATO INC", "--only", "YEXT INC", "--budget", "5")
        self.assertEqual(code, 4)
        s = load(os.path.join(out, "summary.json"))
        self.assertEqual((s["stop_reason"], s["requests_used"]), ("budget", 5))
        statuses = [c["status"] for c in load(os.path.join(out, "proposals.json"))["companies"]]
        self.assertIn("incomplete", statuses)

    def test_F5_canary_failure_stops_before_any_company(self):
        code, out = self.probe(self.fixture({GH.format(rs.CANARY_SLUG): {"status": 200, "body": {"name": "?"}}}),
                               "--only", "YEXT INC")
        self.assertEqual(code, 6)
        self.assertEqual(load(os.path.join(out, "summary.json"))["stop_reason"], "canary-failed:greenhouse")
        self.assertEqual(self.company(out, "YEXT INC")["probes"], [])

    def test_lever_with_postings_and_ashby_empty(self):
        fx = self.fixture({LV.format("yext"): {"status": 200, "body": [{"text": "a"}, {"text": "b"}]},
                           AB.format("zanbato"): {"status": 200, "body": {"jobs": []}}})
        code, out = self.probe(fx, "--only", "YEXT INC", "--only", "ZANBATO INC")
        y = self.company(out, "YEXT INC")["best"]
        self.assertEqual((y["outcome"], y["posting_count"]), ("exists-no-name", 2))
        self.assertEqual(self.company(out, "ZANBATO INC")["best"]["outcome"], "exists-empty")

    def test_only_unmapped_companies_are_probed(self):
        code, out = self.probe(self.fixture({}), "--limit", "3")
        names = [c["company_name"] for c in load(os.path.join(out, "proposals.json"))["companies"]]
        confirmed = {b["company_name"] for b in load(BOARDS)["boards"]}
        self.assertEqual(len(names), 3)
        self.assertFalse(confirmed & set(names))

    def test_log_has_every_loop_phase(self):
        code, out = self.probe(self.fixture({}), "--only", "YEXT INC")
        with open(os.path.join(out, "log.jsonl"), encoding="utf-8") as f:
            kinds = {json.loads(line)["kind"] for line in f}
        self.assertTrue({"observe", "decide", "act", "record", "stop"} <= kinds)


# ── human gate G1 and coverage ───────────────────────────────────────────────
class TestGate(Base):
    def setUp(self):
        super().setUp()
        fx = self.fixture({GH.format("yext"): {"status": 200, "body": {"name": "Yext"}}})
        code, self.out = self.probe(fx, "--only", "YEXT INC", "--only", "ZANBATO INC")
        self.hit = self.company(self.out, "YEXT INC")["best"]

    def decide(self, decision, seen=None, slug="yext", company="YEXT INC"):
        return self.main("decide", "--run", self.out, "--company", company, "--ats", "greenhouse",
                         "--slug", slug, "--decision", decision, "--by", "Test Person",
                         "--seen-sha256", seen or self.hit["sha256"][:12])

    def coverage(self):
        self.assertEqual(self.main("coverage", "--run", self.out, "--candidates", CANDIDATES, "--boards", BOARDS), 0)
        return load(os.path.join(self.out, "coverage.json"))

    def test_proposals_never_count(self):
        cov = self.coverage()
        self.assertEqual((cov["covered"], cov["total"]), (16, 123))
        self.assertEqual(cov["proposed_unreviewed"], 1)

    def test_approve_with_seen_hash_counts_and_keeps_the_16(self):
        self.assertEqual(self.decide("approve"), 0)
        cov = self.coverage()
        self.assertEqual(cov["covered"], 17)
        resolved = load(os.path.join(self.out, "boards.resolved.json"))["boards"]
        self.assertEqual(resolved[:16], load(BOARDS)["boards"])
        new = resolved[16]
        self.assertEqual((new["company_name"], new["slug"], new["confirmed"]), ("YEXT INC", "yext", True))
        self.assertEqual(new["seen_sha256"], self.hit["sha256"])

    def test_F6_wrong_hash_refused(self):
        self.assertEqual(self.decide("approve", seen="0" * 12), 7)
        self.assertEqual(self.coverage()["covered"], 16)

    def test_F7_tampered_raw_file_refused(self):
        path = os.path.join(self.out, self.hit["raw_path"])
        raw = load(path); raw["body_text"] = '{"name": "Someone Else"}'
        with open(path, "w", encoding="utf-8") as f:
            json.dump(raw, f)
        self.assertEqual(self.decide("approve"), 7)

    def test_decide_on_a_miss_refused(self):
        z = self.company(self.out, "ZANBATO INC")["probes"][0]
        code = self.main("decide", "--run", self.out, "--company", "ZANBATO INC", "--ats", z["ats"],
                         "--slug", z["slug"], "--decision", "approve", "--by", "T", "--seen-sha256", z["sha256"][:12])
        self.assertEqual(code, 7)

    def test_refuse_defer_and_last_decision_wins(self):
        self.assertEqual(self.decide("defer"), 0)
        self.assertEqual(self.coverage()["covered"], 16)
        self.assertEqual(self.decide("approve"), 0)
        self.assertEqual(self.decide("refuse"), 0)
        cov = self.coverage()
        self.assertEqual((cov["covered"], cov["refused"]), (16, 1))
        self.assertEqual(len(load(os.path.join(self.out, "decisions.json"))["decisions"]), 3)


class TestConsoleEncoding(unittest.TestCase):
    """Regression, found 2026-11-23 in the offline demo: on a cp1252 Windows console, `decide`
    wrote the approval to decisions.json and THEN crashed printing '→', exiting 1. The
    in-process tests above capture output in a StringIO, so they could never see it."""

    def test_decide_on_a_cp1252_console_exits_0(self):
        import subprocess
        tmp = tempfile.mkdtemp(prefix="resolver-enc-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        work = os.path.join(tmp, "board-resolver")
        os.makedirs(work)
        for f in ("resolver.py",):
            shutil.copy(os.path.join(HERE, f), work)
        shutil.copytree(os.path.join(HERE, "inputs"), os.path.join(work, "inputs"))
        fx = os.path.join(tmp, "fx.json")
        with open(fx, "w", encoding="utf-8") as f:
            json.dump({"responses": {GH.format("yext"): {"status": 200, "body": {"name": "Yext"}}}}, f)
        env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        run = lambda *a: subprocess.run([sys.executable, os.path.join(work, "resolver.py"), *a],
                                        capture_output=True, env=env, cwd=work)
        out = os.path.join(work, "runs", "enc")
        self.assertEqual(run("probe", "--fixture", fx, "--out-dir", out, "--only", "YEXT INC").returncode, 0)
        h = next(c for c in load(os.path.join(out, "proposals.json"))["companies"])["best"]["sha256"]
        r = run("decide", "--run", out, "--company", "YEXT INC", "--ats", "greenhouse", "--slug", "yext",
                "--decision", "approve", "--by", "T", "--seen-sha256", h[:12])
        self.assertEqual(r.returncode, 0, r.stderr.decode("cp1252", "replace"))
        self.assertEqual(run("coverage", "--run", out).returncode, 0)


if __name__ == "__main__":
    unittest.main()
