"""F5 one-change-at-a-time runs on Isaac's 20 fresh held-out labels (JS3 2.4, R30-R31).

Why it exists: each run changes exactly one object and is scored only on labels nobody tuned on
(heldout/, drawn and committed in de5824c before Isaac labeled it).
  E1  filter file   rule v1 -> v2 (FILTER.md v2: rule 4 A + B2). No Claude call: both verdicts
                    already exist (audit/v1/all_verdicts.json, audit/all_verdicts.json).
  E2  prompt        Claude judge prompts/claude_judge.v2 -> v3 (one line: years as "at least half"
                    of the largest requirement, plus the ceiling). Same model, profile, résumé, validator.
"Pass" = the verdict equals Isaac's hand label; a rejected or failed Claude answer counts as a fail,
as in JS1's reports/experiment.py. A held-out run of a prompt is done once: an existing result file
is never overwritten, so a disappointing number can't be re-rolled.

Run: .venv/bin/python reports/f5_experiment.py e1
     .venv/bin/python reports/f5_experiment.py e2 claude_judge.v2      (and claude_judge.v3)
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from job_agent import inputs                     # noqa: E402
from job_agent.common.paths import Paths         # noqa: E402
from job_agent.judges import claude, claude_cli  # noqa: E402
from job_agent.watch.boards import ashby, greenhouse  # noqa: E402

OUT = ROOT / "reports" / "f5"
PARSERS = {"stripe": greenhouse, "cloudflare": greenhouse, "openai": ashby}
PROMPTS = ("claude_judge.v2", "claude_judge.v3")


def labels() -> dict:
    return {r["sample_id"]: r for r in csv.DictReader((ROOT / "heldout" / "hand_verdicts.csv").open())}


def key() -> dict:
    return json.loads((ROOT / "heldout" / "sample_key.json").read_text())


def e1() -> None:
    lab, k = labels(), key()
    runs = {}
    for name, path in (("rule v1", "audit/v1/all_verdicts.json"), ("rule v2", "audit/all_verdicts.json")):
        v = {(p["board"], str(p["posting_id"])): p["verdict"] for p in json.loads((ROOT / path).read_text())["postings"]}
        runs[name] = {sid: v[(e["board"], str(e["posting_id"]))] for sid, e in k.items()}
    rows = [{"sample_id": sid, "title": k[sid]["title"], "hand_label": lab[sid]["my_label"],
             **{n: r[sid] for n, r in runs.items()}} for sid in sorted(k)]
    result = {"experiment": "E1", "object": "filter file (FILTER.md v1 -> v2)", "total": len(rows),
              "passed": {n: sum(row[n] == row["hand_label"] for row in rows) for n in runs}, "rows": rows}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e1_rule.heldout.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    print(result["passed"], "of", len(rows))


def e2(prompt_name: str) -> None:
    out = OUT / f"e2_{prompt_name}.heldout.json"
    if out.exists():
        sys.exit(f"refusing: {out.name} exists; a held-out run is done once")
    paths = Paths()
    criteria = inputs.load_criteria(paths.default_resume, paths.default_profile, paths)
    prompt = claude.Prompt.load(paths.prompt(prompt_name))
    ask = claude_cli.make_ask()
    lab, k = labels(), key()
    cache, rows, raws = {}, [], []
    for sid in sorted(k):
        e = k[sid]
        if e["raw_file"] not in cache:
            cache[e["raw_file"]] = {str(p.id): p for p in PARSERS[e["board"]].parse((ROOT / e["raw_file"]).read_bytes())}
        post = cache[e["raw_file"]][str(e["posting_id"])]
        r = claude.judge(post, criteria, ask, prompt)
        got = r.verdict["verdict"] if r.verdict["status"] == "ok" else "error"
        rows.append({"sample_id": sid, "title": post.title, "hand_label": lab[sid]["my_label"],
                     "claude": got, "pass": got == lab[sid]["my_label"], "verdict": r.verdict})
        raws.append(r.raw)
        print(sid, lab[sid]["my_label"], "->", got, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"experiment": "E2", "object": "prompt", "prompt": prompt_name, "model": claude.MODEL,
                               "via": "cli", "passed": sum(x["pass"] for x in rows), "total": len(rows),
                               "rows": rows}, indent=1, ensure_ascii=False) + "\n")
    (OUT / f"e2_{prompt_name}.heldout.raw.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in raws))
    print(f"{prompt_name}: {sum(x['pass'] for x in rows)}/{len(rows)}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["e1"]:
        e1()
    elif sys.argv[1:2] == ["e2"] and len(sys.argv) == 3 and sys.argv[2] in PROMPTS:
        e2(sys.argv[2])
    else:
        sys.exit(__doc__)
