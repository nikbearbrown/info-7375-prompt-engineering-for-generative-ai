"""Labeling aid: for each posting, show where each of the persona's skills occurs in the description.

It prints evidence only (the matching sentence fragment, whole-word and case-insensitive,
as in the contract), never a verdict. Hemanth decides each label from this evidence.

    python scripts/skill_evidence.py <id> [<id> ...]
"""
import gzip
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from jsagent import resume as resume_mod, rule  # noqa: E402

jobs = {j["id"]: j for j in json.loads(gzip.decompress((ROOT / "runs/2026-10-31T144337/raw.json.gz").read_bytes()))["jobs"]}
skills = resume_mod.skills(resume_mod.load(ROOT / "persona" / "priya-nair.resume.json"))
for pid in map(int, sys.argv[1:]):
    j = jobs[pid]
    text = rule.plain_text(j["content"])
    print(f"### {pid} — {j['title'].strip()}")
    found = False
    for s in skills:
        m = rule._word_pattern(s).search(text)
        if m:
            found = True
            frag = text[max(0, m.start() - 70):m.end() + 50]
            print(f"- **{s}**: …{frag}…")
    if not found:
        print("- none of the 10 skills appears as a whole word")
    print()
