"""Fixed settings taken from CONTRACT.md (In, Refuses)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Refuses (1): the only host the agent may contact.
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
DEFAULT_BOARD = "figma"


def board_url(board: str) -> str:
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


# Out (2): the Claude judge always names its model.
CLAUDE_MODEL = "claude-opus-5-5"

EVIDENCE_DIR = ROOT / "evidence" / "raw"
STATE_FILE = ROOT / "state" / "seen_ids.json"
RUNS_DIR = ROOT / "runs"
PROMPTS_DIR = ROOT / "prompts"
JUDGE_PROMPT = PROMPTS_DIR / "judge_baseline.md"
