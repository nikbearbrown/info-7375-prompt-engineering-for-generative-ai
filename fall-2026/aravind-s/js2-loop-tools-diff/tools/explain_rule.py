"""The rule's seven checks for one posting in a saved answer, without running the agent.

Usage (from the repo root):
  python3 tools/explain_rule.py <saved answer> <posting id> [--system ashby|greenhouse|lever] [--contract 0.1|0.2]

<saved answer> is layer 1's runs/<run id>/response.json (Ashby) or a layer 2
runs/<run id>/boards/<system>-<name>/attempt-N.json.gz, whose system is read from the board folder's
name unless --system is given. The résumé is Jane Doe's. Prints the verdict and one line per check.
--contract picks the rule's contract version: 0.2 (the agent's, the default) or 0.1, which shows the
reading of check 7 before the review packet's patch (4b1a418), so posting 19's bug can still be seen.
"""

from __future__ import annotations

import gzip
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from job_agent import CONTRACT_VERSION, providers, resume, rule  # noqa: E402

CONTRACTS = ("0.1", "0.2")


def load(answer: Path, system: str = None) -> tuple:
    raw = answer.read_bytes()
    body = gzip.decompress(raw) if answer.suffix == ".gz" else raw
    if system is None:
        folder = answer.parent.name
        system = next((s for s in providers.SYSTEMS if folder.startswith(s + "-")), "ashby")
    return system, providers.read(system, 200, body)


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    system, contract = None, CONTRACT_VERSION
    if "--system" in args:
        at = args.index("--system")
        system = args[at + 1]
        del args[at:at + 2]
    if "--contract" in args:
        at = args.index("--contract")
        contract = args[at + 1] if at + 1 < len(args) else ""
        del args[at:at + 2]
        if contract not in CONTRACTS:
            print(f"--contract must be one of {', '.join(CONTRACTS)}")
            return 2
    if len(args) != 2:
        print(__doc__.strip().splitlines()[2].strip())
        return 2
    system, postings = load(Path(args[0]), system)
    posting = next((p for p in postings if p["id"] == args[1]), None)
    if posting is None:
        print(f"no posting {args[1]} in {args[0]}")
        return 1
    verdict = rule.judge(posting, resume.load(REPO / "persona" / "jane-doe.json"), contract)
    print(f"{posting['title']} ({system}, {posting['id']}), contract v{contract}")
    print(f"Rule verdict (record): {verdict['verdict']}")
    for line in verdict["lines"]:
        print(f"- {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
