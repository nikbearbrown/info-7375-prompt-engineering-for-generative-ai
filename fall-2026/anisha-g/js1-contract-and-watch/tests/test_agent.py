"""Tests written from CONTRACT.md. Run: python3 -m unittest discover -s tests -v"""
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); import agent

R = json.loads((Path(agent.ROOT) / "persona/resume.json").read_text())
def P(id_, title, text): return {"id": str(id_), "title": title, "location": "Boston", "url": "", "text": text}
GOOD = P(1, "Data Analyst", "You will use SQL and Tableau daily. 1-2 years of experience.")
SENIOR = P(2, "Senior Data Analyst", "SQL, Python, Looker. 5+ years of experience required.")
WRONGTITLE = P(3, "Software Engineer", "SQL and Python, 2 years of experience.")
ONESKILL = P(4, "Business Intelligence Analyst", "Strong Excel. 2 years.")
def raw(*ids): return {"jobs": [{"id": i, "title": f"Job {i}", "content": "", "location": {"name": "x"}} for i in ids]}

class Refuses(unittest.TestCase):
    def test_host_not_on_allow_list(self):
        with self.assertRaises(PermissionError): agent.check_host("https://evil.example.com/jobs")
    def test_bad_slug_refused_before_network(self):
        for s in ["../etc", "UPPER", "", "a/b"]:
            with self.assertRaises(ValueError): agent.fetch(s)
    def test_real_looking_resume_refused(self):
        import tempfile, copy
        bad = copy.deepcopy(R); bad["personal"]["email"] = "someone@gmail.com"
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump(bad, f); f.close()
        with self.assertRaises(PermissionError): agent.load_resume(f.name)
    def test_persona_is_fictional(self):
        self.assertTrue(R["personal"]["email"].endswith("@example.com")); self.assertIn("555", R["personal"]["phone"])

class Watch(unittest.TestCase):
    def test_baseline_reports_none_then_only_new(self):
        st = Path(tempfile.mkdtemp()) / "seen.json"
        new, base = agent.watch(raw(1, 2, 3), st, "r1"); self.assertTrue(base); self.assertEqual(new, [])
        new, base = agent.watch(raw(1, 2, 3, 4), st, "r2"); self.assertFalse(base); self.assertEqual([p["id"] for p in new], ["4"])
        new, _ = agent.watch(raw(1, 2, 3, 4), st, "r3"); self.assertEqual(new, [])

class RuleJudge(unittest.TestCase):
    def test_contract_examples(self):
        self.assertEqual(agent.rule_judge(R, GOOD)["verdict"], "relevant")
        for p in (SENIOR, WRONGTITLE, ONESKILL): self.assertEqual(agent.rule_judge(R, p)["verdict"], "not_relevant", p["title"])
    def test_justification_names_both_sides(self):
        j = agent.rule_judge(R, GOOD); txt = " ".join(j["justification"])
        self.assertIn("resume.skills.core", txt); self.assertIn("posting.title", txt); self.assertIn("SQL", txt)
    def test_wrong_version_1_labels_paired_with_wrong_postings(self):
        ps = [GOOD, SENIOR, WRONGTITLE, ONESKILL]; right = [agent.rule_judge(R, p)["verdict"] for p in ps]
        shifted = right[1:] + right[:1]          # a buggy implementation that pairs verdicts with the wrong posting
        self.assertNotEqual(right, shifted)

class ClaudeContract(unittest.TestCase):
    ok = json.dumps({"verdict": "relevant", "resume_fields": ["skills.core"], "posting_quotes": ["SQL and Tableau"], "reason": "fits"})
    def test_valid_reply_accepted_and_labelled_judgment(self):
        self.assertEqual(agent.validate(self.ok, GOOD)["kind"], "JUDGMENT (Claude)")
    def test_rejects(self):
        bad = ["Sure! It is relevant.", json.dumps({"verdict": "yes", "resume_fields": ["skills.core"], "posting_quotes": ["SQL"], "reason": "x"}),
               json.dumps({"verdict": "relevant", "resume_fields": ["skills.core"], "posting_quotes": [], "reason": "x"}),   # wrong version 2: cites nothing
               json.dumps({"verdict": "relevant", "resume_fields": ["skills.core"], "posting_quotes": ["10 years of Kubernetes"], "reason": "x"}),  # invented quote
               json.dumps({"verdict": "relevant", "resume_fields": ["hobbies"], "posting_quotes": ["SQL"], "reason": "x"}),
               json.dumps({"verdict": "relevant", "resume_fields": ["skills.core"], "posting_quotes": ["SQL"], "reason": "x", "extra": 1})]
        for b in bad:
            with self.assertRaises(ValueError, msg=b): agent.validate(b, GOOD)

if __name__ == "__main__": unittest.main()
