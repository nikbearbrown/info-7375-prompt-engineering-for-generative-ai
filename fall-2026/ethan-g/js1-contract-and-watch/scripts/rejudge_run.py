"""Re-run only the Claude judge on the new postings of a saved run report, after a judge fix.
Writes a separate evidence file; the original run report is never modified.

    python3 scripts/rejudge_run.py evidence/runs/2026-10-31T165802_live.json "why"
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from jsagent import claude_judge, fetch, resume  # noqa: E402

report_path, why = Path(sys.argv[1]).resolve(), sys.argv[2]
report = json.loads(report_path.read_text())
r = resume.load_resume(ROOT / report["resume_file"])
ps = {p["id"]: p for p in fetch.parse_postings((ROOT / report["raw_file"]).read_bytes())}
out = {"rejudge_of": str(report_path.relative_to(ROOT)), "why": why,
       "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"), "postings": []}
for item in report["new_postings"]:
    j = claude_judge.judge(ps[item["id"]], r, ROOT / "prompts" / "judge_v1_baseline.txt")
    before = item["claude_verdict_judgment"] or {}
    out["postings"].append({"id": item["id"], "title": item["title"],
                            "rule_verdict": item["rule_verdict_record"]["verdict"],
                            "claude_before": before.get("verdict", before.get("status")),
                            "claude_after": j.get("verdict", j["status"]), "judgment": j})
    print(f"{item['id']} rule={item['rule_verdict_record']['verdict']:<12} claude before={out['postings'][-1]['claude_before']:<12} "
          f"after={out['postings'][-1]['claude_after']:<12} truncated={j.get('content_truncated')}  {item['title'][:45]}")
dest = report_path.with_name(report_path.stem + "_REJUDGED-after-truncation-fix.json")
dest.write_text(json.dumps(out, indent=2) + "\n")
print("saved", dest.relative_to(ROOT))
