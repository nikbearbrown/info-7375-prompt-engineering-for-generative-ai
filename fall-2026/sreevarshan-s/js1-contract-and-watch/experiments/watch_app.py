"""Claude judgments for the 10 new postings of the second watch run, run by hand in the Claude app.

    python3 -m experiments.watch_app build
    python3 -m experiments.watch_app score

No Claude call and no network. `build` writes experiments/watch_app/prompts/<posting_id>.txt for each
posting in evidence/rule/2026-10-30T23-59-22Z.json, built with js1.claude_judge.build_prompt and
prompts/baseline.txt exactly as the judge would send it. `score` reads experiments/watch_app/replies/<posting_id>.txt,
checks each with js1.claude_judge.validate (the judge's own validator), and writes experiments/results_watch_app.md:
the saved rule verdict (record) next to the Claude verdict (judgment). There are no hand labels for these postings,
so nothing is scored as pass or fail.
"""

import argparse
import json
import sys
from pathlib import Path

from experiments.heldout_app import check
from js1 import claude_judge
from js1.persona import PersonaRefused, load_persona

ROOT = Path(__file__).resolve().parent.parent
RULE = ROOT / "evidence" / "rule" / "2026-10-30T23-59-22Z.json"
RAW = ROOT / "evidence" / "raw" / "2026-10-30T23-59-22Z.json"
APP_DIR = ROOT / "experiments" / "watch_app"
RESULTS = ROOT / "experiments" / "results_watch_app.md"
PROMPT_NAME = "baseline"
RUN_DATE = "2026-10-31"
SURFACE = "Claude app, incognito, Sonnet 4.6, web search off, one reply per posting, no retry"

EXIT_OK = 0
EXIT_PERSONA = 1


def _records(rule):
    return json.loads(Path(rule).read_text(encoding="utf-8"))["records"]


def _postings(raw, ids):
    jobs = {j["id"]: j for j in json.loads(Path(raw).read_text(encoding="utf-8"))["jobs"]}
    missing = [i for i in ids if i not in jobs]
    if missing:
        raise ValueError(f"postings missing from {raw}: {missing}")
    return [jobs[i] for i in ids]


def build(resume, profile, rule=RULE, raw=RAW, out_dir=APP_DIR / "prompts", prompts_dir=claude_judge.PROMPTS_DIR):
    ids = [r["posting_id"] for r in _records(rule)]
    prompt_text = (Path(prompts_dir) / f"{PROMPT_NAME}.txt").read_text(encoding="utf-8")
    candidate = claude_judge.candidate_fields(resume, profile)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for posting in _postings(raw, ids):
        path = out_dir / f"{posting['id']}.txt"
        path.write_text(claude_judge.build_prompt(prompt_text, posting, candidate), encoding="utf-8")
        written.append(path)
    return written


def score(resume, profile, rule=RULE, replies_dir=APP_DIR / "replies", results=RESULTS):
    allowed = claude_judge.citable_fields(claude_judge.candidate_fields(resume, profile))
    rows = []
    for record in _records(rule):
        pid = record["posting_id"]
        judgment = check(Path(replies_dir) / f"{pid}.txt", pid, allowed)
        rows.append({"posting_id": pid, "title": record["title"].strip(), "record": record["verdict"],
                     "judgment": judgment})
    write_results_md(results, rows, rule, replies_dir)
    return rows


def _shown(result):
    return result["verdict"] if result["status"] == "valid" else result["status"]


def _rel(path):
    path = Path(path)
    return path.relative_to(ROOT) if path.is_relative_to(ROOT) else path


def write_results_md(path, rows, rule, replies_dir):
    table = "\n".join(
        f"| {r['posting_id']} | {r['title']} | {r['record']} | {_shown(r['judgment'])} "
        f"| {'yes' if r['judgment']['status'] == 'valid' and r['judgment']['verdict'] == r['record'] else 'no'} |"
        for r in rows
    )
    problems = [f"- {r['posting_id']}: {r['judgment']['status']} ({r['judgment']['error']})"
                for r in rows if r["judgment"]["status"] != "valid"]
    valid = [r for r in rows if r["judgment"]["status"] == "valid"]
    agree = sum(1 for r in valid if r["judgment"]["verdict"] == r["record"])
    Path(path).write_text(f"""# Watch run: rule record and Claude judgment for each new posting

Two separate judges on the 10 postings that the second live watch run (2026-10-30T23:59:22Z) reported as new.
The **record** is the rule judge's verdict, saved by that run; anyone can recompute it from the contract.
The **judgment** is Claude's verdict under the baseline prompt contract; it is an AI opinion, not a verified result.
Claude did not see the rule verdict.

- **Record:** `{_rel(rule)}`
- **Judgment run:** {RUN_DATE}, run by me in the {SURFACE}.
- **Prompts:** `experiments/watch_app/prompts/`, built with `js1.claude_judge.build_prompt` and `prompts/baseline.txt`, byte for byte what the judge would send.
- **Replies:** `{_rel(replies_dir)}/`, saved by hand.
- **Validator:** `js1.claude_judge.validate`, unchanged. An invalid or missing reply has no judgment.
- **No hand labels:** these postings are not in the labeled set, so neither judge is scored as right or wrong here.

| posting_id | title | rule verdict (record) | Claude verdict (judgment) | same verdict |
|---|---|---|---|---|
{table}

- **Valid judgments:** {len(valid)}/{len(rows)}
- **Same verdict as the record:** {agree} of {len(valid)} valid judgments

## Invalid or missing replies

{chr(10).join(problems) if problems else "None."}
""", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="experiments.watch_app")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="write experiments/watch_app/prompts/<posting_id>.txt")
    sub.add_parser("score", help="validate experiments/watch_app/replies/ and write experiments/results_watch_app.md")
    args = parser.parse_args(argv)
    try:
        resume, profile = load_persona(claude_judge.RESUME, claude_judge.PROFILE)
    except PersonaRefused as exc:
        print(exc, file=sys.stderr)
        return EXIT_PERSONA
    if args.cmd == "build":
        for path in build(resume, profile):
            print(path.relative_to(ROOT))
        return EXIT_OK
    rows = score(resume, profile)
    valid = [r for r in rows if r["judgment"]["status"] == "valid"]
    print(f"valid judgments: {len(valid)}/{len(rows)}")
    print(f"same verdict as the record: {sum(1 for r in valid if r['judgment']['verdict'] == r['record'])} of {len(valid)}")
    print(f"results: {RESULTS.relative_to(ROOT)}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
