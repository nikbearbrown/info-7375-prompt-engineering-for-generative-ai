"""Hand recomputation of one RECORD, with the answer hidden until you ask for it.

    .venv/bin/python scripts/handcheck.py show     # writes labeling/handcheck_posting.md (no verdict)
    .venv/bin/python scripts/handcheck.py reveal   # prints the RECORD for that posting

The posting is drawn with random.Random(7375 + 2) from the run-2 new postings that are outside
the 20-posting sample and whose title passes condition A (so A is given; B and C are the check).
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.resume import load_resume  # noqa: E402
from agent.rules import ELIGIBLE_PHRASES, contains_phrase, evaluate, normalize  # noqa: E402
from experiments.select_sample import readable  # noqa: E402

LIVE = ROOT / "evidence/runs/20261030T213823Z_live"


def pick():
    jobs = {j["id"]: j for j in json.loads((LIVE / "raw_response.json").read_text())["jobs"]}
    new = [o["posting_id"] for o in json.loads((LIVE / "report.json").read_text())["new_postings"]]
    manifest = json.loads((ROOT / "experiments/sample/manifest.json").read_text())
    sample = set(manifest["dev_ids"]) | set(manifest["heldout_ids"])
    pool = sorted(i for i in new if i not in sample
                  and any(contains_phrase(normalize(jobs[i]["title"]), p) for p in ELIGIBLE_PHRASES))
    return jobs[random.Random(7375 + 2).choice(pool)], len(pool)


def main():
    job, pool = pick()
    if sys.argv[1:] == ["show"]:
        out = ROOT / "labeling/handcheck_posting.md"
        out.write_text(
            f"# Hand check — posting {job['id']}\n\n"
            f"Drawn from {pool} run-2 new postings outside the sample whose title passes condition A.\n"
            "Apply A, B and C from CONTRACT.md §4 by hand. Write your result down, then run\n"
            "`.venv/bin/python scripts/handcheck.py reveal`.\n\n"
            f"- **title:** {job['title']}\n- **location:** {(job.get('location') or {}).get('name')}\n\n"
            "**description:**\n\n```text\n" + readable(job.get("content")) + "\n```\n")
        print(f"wrote {out.relative_to(ROOT)} (posting {job['id']}); no verdict shown")
    elif sys.argv[1:] == ["reveal"]:
        rec = evaluate(job, load_resume(ROOT / "resume/priya-nair.resume.example.json"))
        print(json.dumps({k: rec[k] for k in ("posting_id", "verdict", "explanation")}, indent=1, ensure_ascii=False))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
