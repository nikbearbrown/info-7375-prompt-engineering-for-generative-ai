"""Review packet helper: the rule before and after the fix, on every job in run 1's saved raw responses.

Run from the js2-loop-tools-diff folder:  python3 evidence/review/compare_rule_versions.py
"Before" is agent/rule.py as committed in a5fc261 (read with git show); "after" is the working copy.
"""
import glob
import subprocess
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agent import ats, config, resume, rule  # noqa: E402

old_source = subprocess.run(["git", "show", "a5fc261:./agent/rule.py"], capture_output=True, text=True, check=True).stdout
old_rule = types.ModuleType("old_rule")
exec(old_source.replace("from .resume import", "from agent.resume import"), old_rule.__dict__)

persona = resume.load(config.RESUME)
total, changed = 0, []
for path in sorted(glob.glob("evidence/raw/20261110T133054Z-*-a1.json")):
    system, board = Path(path).stem.split("-", 1)[1].rsplit("-a1", 1)[0].split("-", 1)
    try:
        jobs = ats.parse(system, Path(path).read_bytes())
    except ats.BadData:
        continue
    for job in jobs:
        total += 1
        before, after = old_rule.judge(job, persona), rule.judge(job, persona)
        if (before.checks["experience"], before.verdict) != (after.checks["experience"], after.verdict):
            changed.append((f"{system}:{board}", job["id"], job["title"], before.checks["experience"], after.checks["experience"],
                            before.verdict, after.verdict))
print(f"jobs compared: {total} (run 1, 2026-11-10T13:30:54Z)")
print(f"jobs whose experience part or verdict changed: {len(changed)}")
for c in changed:
    print(f"- {c[0]} {c[1]} {c[2]!r}: experience {c[3]} -> {c[4]}, verdict {c[5]} -> {c[6]}")
