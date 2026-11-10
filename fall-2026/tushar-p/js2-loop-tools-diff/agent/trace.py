"""Run evidence: trace.jsonl, summary.json and raw responses in runs/<run_id>/ (F20).

Each trace event carries the fields GATE "Board failure policy" asks for: board, operation,
attempt number where applicable, elapsed time, response status or error, raw file path if
there is one, and what the loop did next. The whole trace is rewritten through the FileGate
after every event, so a partial run still leaves its trace on disk.
"""

import json

from .errors import EvidenceError, PermissionDenied

TRACE_NAME = "trace.jsonl"
SUMMARY_NAME = "summary.json"
RAW_DIR = "raw"


class Trace:
    def __init__(self, gate, run_dir, elapsed):
        self.gate = gate
        self.run_dir = run_dir
        self.elapsed = elapsed
        self.events: list[dict] = []

    def rel(self, path) -> str:
        """A path as shown in evidence: relative to the output root."""
        return str(path.relative_to(self.gate.root))

    def event(self, operation: str, next_step: str, *, board=None, attempt=None,
              status=None, error=None, raw_path=None, **details) -> dict:
        record = {
            "seq": len(self.events) + 1,
            "elapsed_s": round(self.elapsed(), 3),
            "board": board,
            "operation": operation,
            "attempt": attempt,
            "status": status,
            "error": error,
            "raw_path": raw_path,
            "next": next_step,
        }
        record.update(details)
        self.events.append(record)
        self.flush()
        return record

    def flush(self) -> None:
        data = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in self.events).encode("utf-8")
        _write(self.gate, self.run_dir / TRACE_NAME, data, "trace")

    def save_raw(self, board, attempt: int, body: bytes) -> str:
        """Save response bytes before validation. Returns the path relative to the root."""
        path = self.run_dir / RAW_DIR / board.provider / board.token / f"attempt-{attempt}.raw"
        _write(self.gate, path, body, "raw response")
        return self.rel(path)

    def write_summary(self, summary: dict) -> str:
        path = self.run_dir / SUMMARY_NAME
        data = (json.dumps(summary, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        _write(self.gate, path, data, "summary")
        return self.rel(path)


def _write(gate, path, data: bytes, what: str) -> None:
    try:
        gate.write(path, data)
    except (PermissionDenied, OSError) as err:
        raise EvidenceError(f"cannot save the {what}: {err}") from None
