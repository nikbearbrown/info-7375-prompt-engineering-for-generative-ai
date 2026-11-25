"""The trace: one JSON line per event of a run (R17 "a record of every observation").

Events: every board request (retries included), every repeat that was skipped (GATE §3), every
board's end, every Claude call or call not started (with --claude), and the run's end. Kept as
data rather than log text because Step 6 recomputes the summary from it and Step 7's independent
check reads it; fixed fields make that a script, not reading by eye. Written into runs/<stamp>/trace.jsonl by report.py.
"""

import json


class Trace:
    def __init__(self, clock):
        self.clock = clock
        self.started_at = clock()
        self.rows: list[dict] = []

    def _add(self, event: str, **fields) -> None:
        # t = seconds since the run began: comparable across rows, and stable under a test clock.
        self.rows.append({"event": event, "t": round(self.clock() - self.started_at, 3), **fields})

    def request(self, board: str, url: str, attempt: int, http: int | None, code: str | None,
                seconds: float, received_bytes: int, budget: dict) -> None:
        self._add("request", board=board, url=url, attempt=attempt, http=http, code=code,
                  seconds=round(seconds, 3), bytes=received_bytes,
                  requests_left=budget["requests_left"], seconds_left=budget["seconds_left"])

    def repeat(self, board: str, kind: str, key: str) -> None:
        """kind is "url" or "posting"; key is what repeated (the URL, or source/board/job id)."""
        self._add("repeat_skipped", board=board, kind=kind, key=key)

    def claude_call(self, board: str, posting_id, code: str | None, seconds: float) -> None:
        """One selected posting sent to Claude (or not started, code 304)."""
        self._add("claude_call", board=board, posting_id=posting_id, code=code, seconds=round(seconds, 3))

    def board_end(self, row: dict) -> None:
        self._add("board_end", **row)

    def run_end(self, exit_: str, reason: str, budget: dict) -> None:
        self._add("run_end", exit=exit_, reason=reason, budget=budget)

    def jsonl(self) -> str:
        return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in self.rows)
