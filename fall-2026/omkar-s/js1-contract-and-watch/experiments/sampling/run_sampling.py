"""Chapter 1 sampling: ask the SAME prompt contract about each posting N times, each a
fresh `claude -p` conversation, and record every verdict (valid or rejected).

    python3 -m experiments.sampling.run_sampling --n 4 ID1 ID2 ID3 ID4 ID5"""
import argparse
import os

from experiments.common import RESUME, ROOT, SAMPLING_OUT as OUT, append_jsonl, load_postings, sha256
from jsagent import claude_judge, persona

PROMPT = os.path.join(ROOT, "prompts", "baseline.txt")

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=4)
ap.add_argument("ids", nargs="+")
a = ap.parse_args()
postings, resume = load_postings(), persona.load(RESUME)
with open(PROMPT, encoding="utf-8") as f:
    template = f.read()
for pid in a.ids:
    for trial in range(1, a.n + 1):
        j = claude_judge.judge(postings[pid], resume, template,
                               raw_dir=os.path.join(ROOT, "experiments", "sampling", "claude-raw"),
                               tag=f"t{trial}-")
        append_jsonl(OUT, {"posting_id": pid, "trial": trial, "prompt_sha256": sha256(PROMPT), **j})
        print(pid, trial, j["status"], j["verdict"], j.get("rejection", ""))
