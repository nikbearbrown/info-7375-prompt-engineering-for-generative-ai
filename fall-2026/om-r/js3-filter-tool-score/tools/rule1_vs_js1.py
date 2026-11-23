"""Cross-check: JS3 rule 1 must agree with JS1's agent/rule.py verdict on
every collected posting that has content (rule 1 is a port of JS1's rule).
JS1 is imported in its own subprocess because JS1 and JS2 both name their
package `agent`.

    python3 tools/rule1_vs_js1.py logs/run_<stamp>.json
"""
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from js3 import filter as flt
from js3.postings import load_run

JS1 = Path(os.environ.get("JS1_ROOT", Path.home() / "Desktop" / "js1-contract-and-watch")).resolve()
_, postings, _ = load_run(Path(sys.argv[1]).resolve(), ROOT)
postings = [p for p in postings if flt.field_text(p, "content")]
child = ("import json,sys; from agent.rule import verdict; "
         "print(json.dumps([verdict(p) for p in json.load(sys.stdin)]))")
js1 = json.loads(subprocess.run([sys.executable, "-c", child], cwd=JS1, input=json.dumps(postings),
                                capture_output=True, text=True, check=True).stdout)
js3 = ["relevant" if len(flt.classify(p)["matched_skills"]) >= flt.SKILL_THRESHOLD else "not relevant"
       for p in postings]
diff = [(p["board"], p["id"], p["title"], a, b) for p, a, b in zip(postings, js1, js3) if a != b]
print(f"compared {len(postings)} postings with content; JS1 rule relevant {js1.count('relevant')}, "
      f"JS3 rule 1 pass {js3.count('relevant')}; disagreements {len(diff)}")
for d in diff:
    print("  DISAGREE", d)
sys.exit(1 if diff else 0)
