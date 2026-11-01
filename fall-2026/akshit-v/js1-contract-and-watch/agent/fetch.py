"""Allow-listed fetch of one Greenhouse board; every response is saved as evidence.

Usage (fetch and save only, no state change):
    python -m agent.fetch --board figma
"""
import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from agent.config import ALLOWED_HOSTS, DEFAULT_BOARD, EVIDENCE_DIR, board_url


class HostNotAllowed(Exception):
    pass


def check_allowed(url: str) -> None:
    """Refuses (1): raise unless the URL is https on an allow-listed host."""
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
        raise HostNotAllowed(f"refused: {parts.hostname!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")


class _AllowListRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect is a new fetch, so it must pass the allow-list too."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_allowed(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def check_board(board: str) -> None:
    if not re.fullmatch(r"[a-z0-9-]+", board):
        raise ValueError(f"board name must be a Greenhouse token like 'figma', got {board!r}")


def fetch_board(board: str, evidence_dir: Path = EVIDENCE_DIR) -> Path:
    """Fetch the board's public JSON and save the raw bytes plus a .meta.json sidecar."""
    check_board(board)
    url = board_url(board)
    check_allowed(url)
    opener = urllib.request.build_opener(_AllowListRedirects)
    req = urllib.request.Request(url, headers={"User-Agent": "INFO7375-js1-student-agent (read-only)"})
    with opener.open(req, timeout=30) as resp:
        check_allowed(resp.geturl())
        status = resp.status
        body = resp.read()

    now = datetime.now(timezone.utc)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"{now:%Y%m%dT%H%M%SZ}_{board}_live.json"
    path.write_bytes(body)
    meta = {
        "kind": "live",
        "url": url,
        "fetched_at_utc": now.isoformat(timespec="seconds"),
        "http_status": status,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }
    path.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", default=DEFAULT_BOARD)
    args = ap.parse_args()
    path = fetch_board(args.board)
    print(f"saved raw response: {path}")


if __name__ == "__main__":
    main()
