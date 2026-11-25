"""Two judges, labeled, for the new postings of a saved run report.

    python3 -m agent.judge reports/run-databricks-2026-10-30T204649Z.json

Re-reads the run's raw evidence (no fetch), applies the current written rule
(a record) and asks Claude once per posting (a judgment). Writes
reports/judged-<run>.json and .md; Claude replies go to evidence/claude/.
"""

import argparse
import json
import os

from agent import claude_judge, persona, rule
from agent.watch import read_saved


def judge_report(report_path, resume_path, prompt_path, claude_dir,
                 runner=claude_judge.run_claude):
    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)
    resume = persona.load(resume_path)
    by_id = {p["id"]: p
             for p in json.loads(read_saved(report["run"]["raw_path"]))["jobs"]}
    run_name = os.path.splitext(os.path.basename(report_path))[0]
    rows = []
    for pid in report["run"]["new_ids"]:
        posting = by_id[pid]
        record = rule.judge(posting, resume)
        claude = claude_judge.judge(posting, resume, prompt_path, runner=runner)
        claude_judge.save(claude, os.path.join(claude_dir, run_name), str(pid))
        rows.append({"posting_id": pid, "title": record["title"],
                     "location": record["location"], "rule": record,
                     "claude": claude})
    return {"run": report["run"], "rule_version": "v2 (2026-10-30)",
            "prompt": os.path.basename(prompt_path), "rows": rows}


def render_markdown(judged):
    lines = [f"# Two judges — {judged['run']['board']} run "
             f"{judged['run']['stamp']} ({judged['run']['kind']})", "",
             f"- Rule: CONTRACT.md {judged['rule_version']} — a **record**, "
             "recomputable by hand.",
             f"- Claude: `{judged['prompt']}` via `claude -p` — a "
             "**judgment**, not a fact. INVALID = rejected by the validator.",
             "", "| id | title | location | rule (record) | Claude (judgment) "
             "| agree? |", "|---|---|---|---|---|---|"]
    for r in judged["rows"]:
        a, b = r["rule"]["verdict"], r["claude"]["verdict"]
        agree = "—" if b == "INVALID" else ("yes" if a == b else "**no**")
        lines.append(f"| {r['posting_id']} | {r['title']} | {r['location']} "
                     f"| {a} | {b} | {agree} |")
    lines += ["", "## Claude's reasons (verbatim, with date)", ""]
    for r in judged["rows"]:
        c = r["claude"]
        why = c["parsed"]["reason"] if c["parsed"] else "; ".join(c["errors"])
        lines.append(f"- **{r['posting_id']}** ({c['asked_at']}, "
                     f"{', '.join(c['models_used']) or '?'}): {why}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("report")
    ap.add_argument("--resume", default="persona/priya-nair.resume.json")
    ap.add_argument("--prompt", default="prompts/baseline.md")
    ap.add_argument("--claude-dir", default="evidence/claude")
    a = ap.parse_args(argv)
    judged = judge_report(a.report, a.resume, a.prompt, a.claude_dir)
    base = os.path.join(os.path.dirname(a.report), "judged-" +
                        os.path.basename(a.report)[:-len(".json")])
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(judged, f, indent=2, ensure_ascii=False)
        f.write("\n")
    md = render_markdown(judged)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write(md)
    print(md)


if __name__ == "__main__":
    main()
