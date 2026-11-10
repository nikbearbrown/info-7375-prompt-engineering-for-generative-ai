"""One live Claude judge call on the contract's worked example, to check the locked-down CLI works on the seat.

The posting (55150071-..., "Software Engineer, Applied Emerging Talent (2027)") is not one of the 20 labeled
postings. The call is saved under experiment/check/ like any other.

Usage (from the repo root):  python3 tools/claude_check.py [--model MODEL]
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from job_agent import claude_judge, resume  # noqa: E402

WORKED_EXAMPLE = "55150071-fce8-48f5-aea4-14ed78b83511"


def main(argv):
    model = argv[argv.index("--model") + 1] if "--model" in argv else claude_judge.DEFAULT_MODEL
    jobs = json.loads((REPO / "runs" / "2026-10-30T093102Z" / "response.json").read_bytes())["jobs"]
    posting = next(j for j in jobs if j["id"] == WORKED_EXAMPLE)
    verdict = claude_judge.judge(posting, resume.load(REPO / "persona" / "jane-doe.json"),
                                 prompt_path=REPO / "prompts" / "baseline.txt",
                                 record_dir=REPO / "experiment" / "check", model=model, label="check")
    record = json.loads((REPO / "experiment" / verdict["record"]).read_text(encoding="utf-8"))
    print("Claude Code reported:", json.dumps(record.get("claude_code"), ensure_ascii=False))
    print("seconds:", record.get("seconds"), "| exit:", record.get("exit_code"), "| cost (CLI estimate, USD):", record.get("cost_usd"))
    print("validation:", record.get("validation"))
    print("Claude's judgment (model output, not verified):", verdict.get("verdict") or "no valid judgment")
    for line in verdict["lines"]:
        print("  ", line)
    return 0 if verdict["valid"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
