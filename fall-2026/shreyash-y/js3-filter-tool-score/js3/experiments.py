"""What moves the score (Chapter 9): one change to one object at a time, measured on the held-out
labels (labels/sample.json "held_out", 24 postings), which no rule, prompt or setting here was designed
from. The conditions were fixed in this file before any held-out label existed (commit order).

  B   baseline: JS1's prompt baseline-v1 (inherited), CONTRACT.md's rule in it, model opus, no tools
  B2  B again, unchanged, in new sessions: the noise floor
  P   the prompt: JS1's revision-1-quote-evidence (one instruction added: quote the words behind each failure)
  C   the context: the rule Claude is given is FILTER.md v1 (Shreyash's words) instead of CONTRACT.md
  S   a setting: model haiku instead of opus
  T   the tool list: the score_posting tool (this folder's MCP server) is offered and allowed
The filter-file change is deterministic and is measured in js3/score.py, not here.

  python3 -m js3.experiments B [P C ...]       (resumable: a saved call is never repeated)
"""
import concurrent.futures as cf
import json
import pathlib
import sys

from js3 import corpus, judge

HERE = pathlib.Path(__file__).resolve().parent.parent
CONDITIONS = {
    "B": {"prompt": "prompts/baseline-v1.md", "model": "opus", "tool": False},
    "B2": {"prompt": "prompts/baseline-v1.md", "model": "opus", "tool": False},
    "P": {"prompt": "prompts/revision-1-quote-evidence.md", "model": "opus", "tool": False},
    "C": {"prompt": "prompts/context-filter-v1.md", "model": "opus", "tool": False},
    "S": {"prompt": "prompts/baseline-v1.md", "model": "haiku", "tool": False},
    "T": {"prompt": "prompts/baseline-v1.md", "model": "opus", "tool": True},
}


def held_out_keys():
    s = json.loads((HERE / "labels" / "sample.json").read_text())
    return sorted(set().union(*s["held_out"].values()))


def path_for(cond, key):
    return HERE / "results" / "judge" / cond / (key.replace(":", "__") + ".json")


def run(cond, keys, workers=4):
    spec = CONDITIONS[cond]
    postings = {p["key"]: p for p in corpus.load()}
    todo = [k for k in keys if not path_for(cond, k).exists()]

    def one(key):
        rec = judge.judge(cond, spec["prompt"], spec["model"], postings[key], with_tool=spec["tool"])
        path = path_for(cond, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
        return key, rec["valid"], rec["parsed"]["verdict"] if rec["parsed"] else None

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in cf.as_completed([ex.submit(one, k) for k in todo]):
            try:
                key, valid, verdict = fut.result()
                print(f"{cond} {key} valid={valid} verdict={verdict}", flush=True)
            except Exception as e:  # a failed call is reported and left to retry; never guessed
                print(f"{cond} FAILED: {e}", flush=True)
    done = sum(path_for(cond, k).exists() for k in keys)
    print(f"{cond}: {done} of {len(keys)} saved", flush=True)


if __name__ == "__main__":
    keys = held_out_keys()
    for c in sys.argv[1:]:
        run(c, keys)
