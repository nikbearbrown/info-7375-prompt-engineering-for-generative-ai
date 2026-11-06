"""Config file and allow-list (CONTRACT.md §1 items 1 and 4, §3.1)."""

import json
from pathlib import Path
from urllib.parse import urlsplit

from .errors import Refusal, RunError

# §1 item 1: the one fetch URL. There is no other URL form.
FETCH_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
BOARD_TOKEN = "stripe"
# §1 item 4 / §3.1: the allow-list is exactly this.
ALLOW_LIST = ["boards-api.greenhouse.io"]

PATH_KEYS = ("resume_path", "state_path", "evidence_dir", "claude_outputs_dir")
CONFIG_KEYS = ("board_token", "allow_list") + PATH_KEYS


def load_config(path):
    """Read config.json. Path values are resolved against the config file's folder."""
    path = Path(path)
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RunError(f"cannot read config {path}: {exc}") from exc
    if not isinstance(config, dict):
        raise RunError(f"{path} is not a JSON object")
    missing = [key for key in CONFIG_KEYS if key not in config]
    if missing:
        raise RunError(f"{path} is missing {', '.join(missing)} (§1 item 4)")
    if config["board_token"] != BOARD_TOKEN:
        raise Refusal(f"board_token must be {BOARD_TOKEN!r}; the agent reads one board only (§1 item 1)")
    if config["allow_list"] != ALLOW_LIST:
        raise Refusal(f"allow_list must be exactly {ALLOW_LIST} (§1 item 4, §3.1)")
    for key in PATH_KEYS:
        if not isinstance(config[key], str) or not config[key]:
            raise RunError(f"{path}: {key} must be a non-empty path string")
    base = path.resolve().parent
    resolved = dict(config)
    for key in PATH_KEYS:
        resolved[key] = base / config[key]
    return resolved


def fetch_url_for(board_token):
    return f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"


def url_refusal_reasons(url, allow_list):
    """Every reason §1/§3.1 refuses this URL. An empty list means it may be fetched."""
    reasons = []
    parts = urlsplit(url)
    if parts.scheme != "https":
        reasons.append(f"scheme is {parts.scheme!r}, not 'https'")
    try:
        host = parts.hostname
    except ValueError:
        host = None
    # Exact host equality: a prefix, suffix or query-string mention is not a match.
    if host not in allow_list:
        reasons.append(f"host {host!r} is not on the allow-list {list(allow_list)}")
    if url != FETCH_URL:
        reasons.append(f"not the one §1 fetch URL {FETCH_URL}")
    return reasons


def require_fetch_url(url, allow_list):
    """Called before every fetch (§1 item 4). Raises Refusal; nothing is fetched."""
    reasons = url_refusal_reasons(url, allow_list)
    if reasons:
        raise Refusal(f"refused to fetch {url!r}: " + "; ".join(reasons))
