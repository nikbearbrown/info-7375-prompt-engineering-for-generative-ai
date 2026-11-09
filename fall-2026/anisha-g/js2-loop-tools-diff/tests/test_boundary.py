"""Boundary tests for the permission policy. The expected values are MY 17 predictions (PREDICTIONS.md), given before any test or code existed.
`python3 tests/test_boundary.py --table` prints predicted vs actual."""
import json, os, re, sys, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
if os.environ.get('JS2_WRONG'): sys.path.insert(0, str(HERE.parent / 'wrong_versions' / os.environ['JS2_WRONG']))  # run the SAME tests against a deliberately wrong version
from sandbox import make_sandbox, expand
from policy import Policy

CASES = json.loads((HERE / "boundary_cases.json").read_text())

def run_case(c, sb):
    pol = Policy(sb["ROOT"], sb["OUT"], approved_paths=[expand(p, sb) for p in c.get("approve", [])])
    k = c["kind"]
    if k == "url": return pol.check_url(c["url"], c.get("method", "GET"))
    if k == "redirect": return pol.check_redirect(c["url"], c["to"])
    if k == "read": return pol.check_read(expand(c["path"], sb))
    if k == "write": return pol.check_write(expand(c["path"], sb), append=c.get("append", False))
    if k == "delete": return pol.check_delete(expand(c["path"], sb))
    if k == "action": return pol.check_action(c["name"], approved=c.get("approved_flag", False))
    raise AssertionError(k)

class Boundary(unittest.TestCase):
    def test_at_least_ten_cases(self): self.assertGreaterEqual(len(CASES), 10)
    def test_every_case_matches_my_prediction(self):
        sb = make_sandbox()
        for c in CASES:
            with self.subTest(c["id"]):
                d = run_case(c, sb); self.assertEqual(d.verdict, c["expect"], f"{c['id']}: {d.reason}")
    def test_predictions_md_equals_case_file(self):
        text = (HERE.parent / "PREDICTIONS.md").read_text()
        word = {"allowed": "ALLOW", "blocked": "DENY", "ask me": "NEEDS_APPROVAL"}
        mine = {f"B{int(n):02d}": word[w] for n, w in re.findall(r"^\| (\d+) \|.*?\| (allowed|blocked|ask me) — ", text, re.M)}
        self.assertEqual(len(mine), 17); self.assertEqual(mine, {c["id"]: c["expect"] for c in CASES})
    def test_settings_and_source_are_never_writable(self):    # GATE 5: never change source code or settings
        sb = make_sandbox(); pol = Policy(sb["ROOT"], sb["OUT"])
        for p in ("config/budgets.json", "agent.py", "persona/resume.json"):
            self.assertEqual(pol.check_write(sb["ROOT"] / p).verdict, "DENY", p)
    def test_never_list_actions(self):                         # GATE 5b: apply, email, message, log in
        pol = Policy(*[make_sandbox()[k] for k in ("ROOT", "OUT")])
        for a in ("apply", "email", "message", "login", "delete", "publish"):
            self.assertEqual(pol.check_action(a, approved=True).verdict, "DENY", a)

if __name__ == "__main__":
    if "--table" in sys.argv:
        sb = make_sandbox(); print("| id | my prediction | actual | reason from policy.py |\n|---|---|---|---|")
        for c in CASES:
            d = run_case(c, sb); print(f"| {c['id']} | {c['expect']} | {d.verdict} {'✔' if d.verdict == c['expect'] else '✘ MISMATCH'} | {d.reason} |")
    else: unittest.main()
