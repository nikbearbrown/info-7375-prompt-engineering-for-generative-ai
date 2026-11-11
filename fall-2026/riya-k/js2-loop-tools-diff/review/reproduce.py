"""Reproduce the Intern defect on a REAL posting from today's live run (no network).

    python3 review/reproduce.py
Prints the rule's verdict for Databricks posting 6866538002 "Data Science Intern (2027 Start)".
Before the fix: relevant (the defect). After the fix: not_relevant.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from jsagent import ats, rules  # noqa: E402

raw = (ROOT / "tests/fixtures/databricks-6866538002.json").read_text()
job = json.loads(raw)["job"]
posting = ats.greenhouse_parse(json.dumps({"jobs": [job]}).encode())[0]
v = rules.judge(posting, json.loads((ROOT / "persona/arya-sahni.json").read_text()))
print(f"{v['id']}  {v['title']!r}  ->  {v['verdict']}")
print(f"justification: {v['justification']}")
