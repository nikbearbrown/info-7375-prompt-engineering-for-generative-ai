"""Deliberately wrong implementations from GATE.md section 7. The agent never imports this."""
from pathlib import Path

from agent2 import loop, policy


def wa_classify(ats, board, response, last_count):
    """W-a: an empty job list is accepted as a normal answer ("no new jobs")."""
    outcome, postings, detail = loop.classify(ats, board, response, None)   # ignores history
    return outcome, postings, detail


def wb_check_write(path, out_dir: Path = policy.OUT) -> Path:
    """W-b: string-prefix check, so 'out-evil/x' passes as if it were inside 'out/'."""
    p = Path(path).resolve()
    if not str(p).startswith(str(out_dir.resolve())):
        raise policy.PolicyViolation(f"write refused: {path}")
    return p
