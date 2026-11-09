"""Fixed settings from GATE.md. The board list, budgets and hosts live in config/ and change only by a committed edit."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
RESUME = ROOT / "data" / "rohan-mehta.resume.json"
RUNS_DIR = ROOT / "runs"
STATE = RUNS_DIR / "state" / "seen_ids.json"
RAW_DIR = ROOT / "evidence" / "raw"

# Permission policy (GATE.md): the only folders the agent may write, and the paths that need my approval.
WRITE_DIRS = ("runs", "evidence")
APPROVAL_PATHS = ("config", "agent/rule.py", "CONTRACT-JS1.md")


def load(name):
    """One of config/boards.json, config/budgets.json, config/hosts.json."""
    return json.loads((CONFIG_DIR / f"{name}.json").read_text(encoding="utf-8"))
