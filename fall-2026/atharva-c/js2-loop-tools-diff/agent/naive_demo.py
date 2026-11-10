"""DEMO ONLY: the naive loop from WRONG_VERSIONS.md #1. Never used for real runs.

It is the real loop with one change: a 200 OK with zero jobs is treated as a
clean board with 0 jobs and 0 new, instead of being flagged. On an empty board
it therefore ends `finished` and reports "no new jobs": a finished wrong answer.

    python3 -m agent.naive_demo --replay evidence/SEEDED-empty-robinhood \
        --boards examples/boards-3-real.json
"""

import sys

from agent.loop import Loop, main


class NaiveLoop(Loop):
    def _visit(self, board: dict) -> dict:
        result = super()._visit(board)
        if result["status"] == "flagged":          # WRONG VERSION #1
            self._log("naive-accepted-empty", board=board["name"])
            return {"board": board["name"], "status": "ok", "jobs": 0, "new": 0,
                    "new_titles": []}
        return result


if __name__ == "__main__":
    sys.exit(main(loop_cls=NaiveLoop, run_prefix="NAIVE-DEMO-"))
