"""Ask Claude (one fresh `claude -p` conversation per call, no tools) about selected postings
from run 1's saved raw response. Every call is saved under <out>/calls/.

  PYTHONPATH=. python3 experiments/run_claude.py --prompt prompts/baseline-v1.md \
      --set development --first 5 --repeats 4 --out experiments/sampling --tag sample
"""
import argparse
import concurrent.futures
import json
import pathlib

from jsagent import claude_judge, persona, posting

ap = argparse.ArgumentParser()
ap.add_argument("--prompt", required=True)
ap.add_argument("--set", choices=["development", "held_out"], required=True)
ap.add_argument("--first", type=int, default=10, help="use the first N postings of the set")
ap.add_argument("--repeats", type=int, default=1)
ap.add_argument("--out", required=True)
ap.add_argument("--tag", required=True)
ap.add_argument("--workers", type=int, default=5)
ap.add_argument("--selection", default="experiments/selected_postings.json")
ap.add_argument("--board", default="oscar")
a = ap.parse_args()

sel = json.loads(pathlib.Path(a.selection).read_text())
jobs = {j["id"]: j for j in json.loads(pathlib.Path(sel["raw_file"]).read_bytes())["jobs"]}
view = persona.public_view(persona.load("persona/alex_morgan.json"))
ids = [x["id"] for x in sel[a.set]][: a.first]
tasks = [(pid, k) for pid in ids for k in range(1, a.repeats + 1)]


def one(task):
    pid, k = task
    p = posting.normalize(jobs[pid], a.board)
    return claude_judge.judge(a.prompt, view, p, pathlib.Path(a.out) / "calls", f"{a.tag}{k}")


with concurrent.futures.ThreadPoolExecutor(a.workers) as ex:
    records = list(ex.map(one, tasks))
summary = pathlib.Path(a.out) / f"{a.tag}-summary.jsonl"
with summary.open("a") as f:
    for r in records:
        f.write(json.dumps({k: r[k] for k in ("called_at", "model", "prompt_file", "prompt_sha256",
                                              "posting_id", "tag", "valid", "errors", "parsed")}) + "\n")
for r in records:
    v = r["parsed"]["verdict"] + " " + str(sorted(r["parsed"]["failed_conditions"])) if r["valid"] else "REJECTED " + r["errors"][0]
    print(r["posting_id"], r["tag"], v)
