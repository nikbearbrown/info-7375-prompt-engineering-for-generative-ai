"""Sampling report data (brief Step 4.1, R21-R22): the same 5 postings, 4 fresh Claude conversations each.

Why it exists: one Claude answer can't show whether the judgment is stable. Asking the same
question in fresh conversations shows how much the verdict moves; comparing with Isaac's hand
label shows that a stable answer can still be wrong (the brief's point: repeatability is not
correctness).

The 5 postings come only from the dev set (labels/split.json), never held-out, so the held-out
set stays unseen until the end of the prompt experiment. Chosen by a fixed rule, not by hand:
every dev posting where the CONTRACT rule disagrees with Isaac's label (4), plus the one dev
posting with an engineering title that Isaac labeled not_relevant.

Same judge as the agent (claude.judge + validator, prompt v1, claude -p), so a rejected answer
counts here exactly as it would in a run. Every reply is saved as received.
Run: .venv/bin/python reports/sampling.py   -> reports/sampling/results.json + raw.jsonl
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from job_agent import inputs                   # noqa: E402
from job_agent.common.paths import Paths       # noqa: E402
from job_agent.judges import claude, claude_cli  # noqa: E402
from job_agent.watch.boards import greenhouse  # noqa: E402

RAW = ROOT / "evidence/raw/2026-10-31T214118Z/stripe_content.json"   # where the labeled postings came from
POSTINGS = [7235875, 8131144, 8301253, 8072257, 7913700]
TIMES = 4
PROMPT = "claude_judge.v1"
OUT = ROOT / "reports" / "sampling"


def main() -> None:
    dev = set(json.loads((ROOT / "labels/split.json").read_text())["dev"])
    assert set(POSTINGS) <= dev, "sampling must use dev postings only (held-out stays unseen)"
    paths = Paths()
    criteria = inputs.load_criteria(paths.default_resume, paths.default_profile, paths)
    prompt = claude.Prompt.load(paths.prompt(PROMPT))
    posts = {p.id: p for p in greenhouse.parse(RAW.read_bytes())}
    ask = claude_cli.make_ask()          # each call = its own claude -p process = a fresh conversation

    OUT.mkdir(parents=True, exist_ok=True)
    results, raws = [], []
    for pid in POSTINGS:
        for k in range(1, TIMES + 1):
            start = time.time()
            r = claude.judge(posts[pid], criteria, ask, prompt)
            results.append({"posting_id": pid, "try": k, "seconds": round(time.time() - start, 1), **r.verdict})
            raws.append({"try": k, **r.raw})
            print(pid, k, r.verdict["status"], r.verdict["verdict"], flush=True)
    (OUT / "results.json").write_text(json.dumps(
        {"prompt": PROMPT, "model": claude.MODEL, "via": "cli", "times": TIMES, "postings": POSTINGS,
         "source": str(RAW.relative_to(ROOT)), "results": results}, indent=1, ensure_ascii=False) + "\n")
    (OUT / "raw.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in raws))


if __name__ == "__main__":
    main()
