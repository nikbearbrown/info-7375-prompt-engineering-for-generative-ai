"""Run state: every step, budget counter and stop reason, saved per run and in a ledger."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

STOP_REASONS = (
    "approved_and_exported",   # human approved the exact view; report written
    "refused_by_human",        # human refused; nothing written
    "deferred_by_human",       # human deferred, or approval did not match the view
    "answered_not_released",   # evaluation run: answer scored, no gate, nothing written
    "refused_by_policy",       # question screened out before any model call
    "deferred_clarification",  # model asked for clarification; no SQL run
    "stopped_policy_denials",  # repeated unsafe or off-policy SQL
    "budget_exhausted",        # proposals or wall-clock time used up
    "source_mismatch",         # database is not the checked workbook
)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class RunState:
    def __init__(self, question, qid, adapter_label, contract_name):
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
        self.question = question
        self.qid = qid
        self.adapter = adapter_label
        self.contract = contract_name
        self.started = now()
        self.finished = None
        self.steps = []
        self.used = {"proposals": 0, "denials": 0, "errors": 0}
        self.stop_reason = None
        self.result = None
        self.view_hash = None
        self.decision = None
        self.export_path = None

    def add(self, kind, **data):
        self.steps.append({"at": now(), "step": kind, **data})

    def stop(self, why, **data):
        if why not in STOP_REASONS:
            raise ValueError(f"unknown stop reason {why}")
        self.stop_reason = why
        self.finished = now()
        self.add("stop", stop_reason=why, **data)
        return self

    def to_dict(self):
        return {key: getattr(self, key) for key in (
            "run_id", "question", "qid", "adapter", "contract", "started", "finished",
            "used", "stop_reason", "view_hash", "decision", "export_path", "steps", "result")}

    def save(self, state_dir):
        state_dir = Path(state_dir)
        (state_dir / "runs").mkdir(parents=True, exist_ok=True)
        path = state_dir / "runs" / f"{self.run_id}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str) + "\n", encoding="utf-8")
        line = {"run_id": self.run_id, "qid": self.qid,
                "question_sha256": hashlib.sha256(self.question.encode()).hexdigest()[:16],
                "stop_reason": self.stop_reason, "view_hash": self.view_hash,
                "decision": self.decision, "finished": self.finished}
        with open(state_dir / "ledger.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(line) + "\n")
        return path
