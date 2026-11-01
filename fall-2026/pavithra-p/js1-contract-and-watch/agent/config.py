"""Fixed settings from CONTRACT.md. Changing any of these is a contract change."""
from pathlib import Path

BOARD = "pinterest"
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
# The prompt experiments also draw postings from more boards on the same host
# (experiment/README.md, experiment-2/README.md).
EXPERIMENT_BOARDS = ("pinterest", "figma", "twilio", "affirm", "airbnb", "brex", "databricks", "reddit", "stripe")


def board_url(board):
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


BOARD_URL = board_url(BOARD)

ROOT = Path(__file__).resolve().parent.parent
RESUME = ROOT / "data" / "rohan-mehta.resume.json"
RAW_DIR = ROOT / "evidence" / "raw"
RUNS_DIR = ROOT / "evidence" / "runs"
CLAUDE_DIR = ROOT / "evidence" / "claude"
STATE = ROOT / "state" / "seen_ids.json"
SEEDED_STATE = ROOT / "state" / "seen_ids-SEEDED.json"
