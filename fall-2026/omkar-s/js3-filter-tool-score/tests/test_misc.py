"""store (write boundary), audit statistics and blindness, the one-change experiment design, redaction."""
import json
import os


def _json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
import tempfile
import unittest

from js3 import audit, experiments, redact, store
from tests.helpers import cfg, persona, posting

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Store(unittest.TestCase):
    def test_refuses_outside_and_protected(self):
        for p in (os.path.join(tempfile.gettempdir(), "x"), "../x.md", "config/x.json", "filter/CURRENT",
                  "labels/heldout-js1/labels.csv", "evidence/x", "data/raw/x", "persona/x.json"):
            with self.assertRaises(store.WriteRefused, msg=p):
                store.check(p)

    def test_allows_reports(self):
        self.assertTrue(store.check("audit/AUDIT-RESULTS.md").endswith("AUDIT-RESULTS.md"))


class AuditStats(unittest.TestCase):
    def test_clopper_pearson_known_values(self):
        lo, hi = audit.clopper_pearson(0, 30)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.1157, places=3)  # the "rule of three" neighbourhood: 3/30 = 0.10
        lo, hi = audit.clopper_pearson(3, 30)
        self.assertAlmostEqual(lo, 0.0211, places=3)
        self.assertAlmostEqual(hi, 0.2653, places=3)

    def test_cards_are_blind(self):
        k = audit._load_key()
        for c in k["cards"]:
            self.assertFalse({"score", "filter_verdict", "parts", "reasons", "verdict"} & set(c), c["card"])
        self.assertGreaterEqual(k["meta"]["parts"]["R"], 30)
        self.assertEqual(len(k["cards"]), len(k["key"]))

    def test_draw_refuses_when_verdicts_exist(self):
        path = os.path.join(BASE, audit.OMKAR)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with self.assertRaises(SystemExit):
                audit.draw()


class OneLineLabel(unittest.TestCase):
    """label_one() on a temp copy of the audit folder: never touches the real verdicts."""

    def test_save_refuse_duplicate_and_bad_input(self):
        import shutil
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            shutil.copytree(os.path.join(BASE, "audit"), os.path.join(d, "audit"))
            vf = os.path.join(d, "audit", "omkar-verdicts.csv")
            if os.path.exists(vf):
                os.remove(vf)
            with mock.patch.object(audit, "BASE", d), mock.patch.object(store, "BASE", d):
                out = []
                audit.label_one(3, "r", "sales role", out=out.append)
                self.assertEqual(audit._omkar()[3]["verdict"], "reject")
                self.assertIn("saved card 3: reject", out[0])
                with self.assertRaises(SystemExit):
                    audit.label_one(3, "keep", "changed my mind", out=out.append)  # no silent overwrite
                audit.label_one(3, "keep", "changed my mind", out=out.append, replace=True)
                self.assertEqual(audit._omkar()[3]["verdict"], "keep")
                with open(os.path.join(d, "audit", "omkar-verdicts-replaced.csv")) as f:
                    self.assertIn("sales role", f.read())  # the old row is kept
                with self.assertRaises(SystemExit):
                    audit.label_one(4, "maybe", "a real reason", out=out.append)
                with self.assertRaises(SystemExit):
                    audit.label_one(999, "keep", "a real reason", out=out.append)
                for placeholder in ("your reason here", "type your own reason", ""):
                    with self.assertRaises(SystemExit):
                        audit.label_one(5, "reject", placeholder, out=out.append)
                self.assertNotIn(5, audit._omkar())
                shown = []
                audit.show(out=shown.append)
                text = "\n".join(shown)
                self.assertIn("Card 1 ", text)  # next unlabelled
                self.assertNotIn("filter_verdict", text)


class OneChangeAtATime(unittest.TestCase):
    def setUp(self):
        self.p = posting(body="Requirements: 2+ years of experience with Python and AWS.")
        self.f0 = cfg("1.4")

    def prompts(self):
        return {c: experiments.prompt_for(c, self.p, persona(), self.f0) for c in experiments.CLAUDE_CONDS}

    def test_e5_and_c0b_prompts_equal_c0(self):
        pr = self.prompts()
        self.assertEqual(pr["E5"], pr["C0"])
        self.assertEqual(pr["C0b"], pr["C0"])

    def test_e3_adds_only_the_abstention_rule(self):
        pr = self.prompts()
        diff = pr["E3"].replace("\n" + experiments.E3_RULE + "\n", "", 1).replace(' | "cannot_tell"', "", 1)
        self.assertEqual(diff, pr["C0"])

    def test_e4_adds_only_the_filter_result(self):
        pr = self.prompts()
        start = pr["E4"].index("\nFILTER RESULT")
        end = pr["E4"].index("POSTING\n")
        self.assertEqual(pr["E4"][:start] + "\n" + pr["E4"][end:], pr["C0"])

    def test_filter_variants_differ_in_one_field(self):
        base = _json(os.path.join(BASE, experiments.FILTERS["F0"]))
        for cond, key in (("E1", "weights"), ("E2", "threshold")):
            v = _json(os.path.join(BASE, experiments.FILTERS[cond]))
            changed = sorted(k for k in set(base) | set(v) if base.get(k) != v.get(k) and k not in ("version", "_comment"))
            self.assertEqual(changed, [key], cond)
        e1 = _json(os.path.join(BASE, experiments.FILTERS["E1"]))["weights"]
        self.assertEqual([k for k in e1 if e1[k] != base["weights"][k]], ["T3_seniority"])

    def test_metrics(self):
        labels = {"a": "relevant", "b": "not_relevant", "c": "relevant"}
        res = {"a": {"verdict": "relevant"}, "b": {"verdict": "relevant"}, "c": {"verdict": "cannot_tell"}}
        m = experiments.metrics(res, labels)
        self.assertEqual((m["answered"], m["correct"], m["fp"], m["fn"], m["abstained"]), (2, 1, 1, 0, 1))


class Redact(unittest.TestCase):
    def test_main_walks_subfolders_and_skips_directories(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "transcripts", "e5"))
            home = os.path.expanduser("~")
            with open(os.path.join(d, "transcripts", "e5", "s.jsonl"), "w") as f:
                f.write(f'{{"cwd": "{home}/x"}}')
            with mock.patch.object(redact, "BASE", d), mock.patch("builtins.print"):
                self.assertEqual(redact.main(), 0)
            with open(os.path.join(d, "transcripts", "e5", "s.jsonl")) as f:
                self.assertNotIn(home, f.read())

    def test_home_and_user_replaced(self):
        s = redact.redact_text('{"cwd":"/Users/jdoe/x","p":"-Users-jdoe-x","u":"jdoe"}', home="/Users/jdoe")
        self.assertEqual(s, '{"cwd":"<HOME>/x","p":"-<HOME>-x","u":"<USER>"}')


if __name__ == "__main__":
    unittest.main()
