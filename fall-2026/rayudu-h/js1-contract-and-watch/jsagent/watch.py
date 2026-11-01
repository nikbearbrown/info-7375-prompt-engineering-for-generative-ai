"""The watch: allow-listed fetch, raw response saved as evidence, new-since-last by posting id.

CONTRACT.md: the allow-list is boards-api.greenhouse.io only (Refuses 1); a raw response is
never overwritten (Refuses 6); links inside postings are never followed (Refuses 8); a failed
fetch is reported as "fetch failed", never as "nothing new".
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_HOSTS = {"boards-api.greenhouse.io"}
BOARD_TOKEN = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


class Refused(Exception):
    """An action the contract refuses. The caller logs it and skips the action."""


class FetchFailed(Exception):
    """The fetch failed or did not return the board's JSON."""


def board_url(board: str) -> str:
    if not BOARD_TOKEN.match(board or ""):
        raise Refused(f"board token {board!r} is not a plain Greenhouse board name")
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


def check_allowed(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise Refused(f"host {parsed.hostname!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")


class _AllowListRedirects(urllib.request.HTTPRedirectHandler):
    """Check every redirect target against the allow-list before following it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_allowed(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str, timeout: float = 30.0) -> bytes:
    check_allowed(url)
    req = urllib.request.Request(url, headers={"User-Agent": "info7375-js1-student-agent (read-only)"})
    opener = urllib.request.build_opener(_AllowListRedirects)
    try:
        with opener.open(req, timeout=timeout) as resp:
            check_allowed(resp.geturl())
            if resp.status != 200:
                raise FetchFailed(f"HTTP {resp.status}")
            return resp.read()
    except urllib.error.URLError as e:
        raise FetchFailed(str(e)) from e


def parse_jobs(raw: bytes) -> list:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise FetchFailed(f"response is not JSON: {e}") from e
    jobs = data.get("jobs") if isinstance(data, dict) else None
    if not isinstance(jobs, list) or not all(isinstance(j, dict) and "id" in j for j in jobs):
        raise FetchFailed("response is not a Greenhouse board (no jobs[] with ids)")
    return jobs


def save_raw(run_dir: Path, raw: bytes, meta: dict) -> dict:
    """Save raw bytes gzipped plus their SHA-256. Refuses to overwrite."""
    run_dir.mkdir(parents=True, exist_ok=True)
    target = run_dir / "raw.json.gz"
    if target.exists():
        raise Refused(f"{target} already exists; raw responses are never overwritten")
    with gzip.open(target, "xb") as f:
        f.write(raw)
    meta = dict(meta, raw_sha256=hashlib.sha256(raw).hexdigest(), raw_bytes=len(raw), saved_as=target.name)
    (run_dir / "raw.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def load_seen(state_path: Path):
    """Return the set of seen ids, or None when there is no state yet (baseline run)."""
    if not state_path.exists():
        return None
    data = json.loads(state_path.read_text())
    return set(data["seen_ids"])


def save_seen(state_path: Path, ids, run_id: str) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"updated_by_run": run_id, "seen_ids": sorted(ids)}, indent=2) + "\n")


def new_postings(jobs: list, seen) -> list:
    """Postings whose `id` is not in seen. Baseline (seen is None) reports none as new.

    Keyed on the Greenhouse posting `id`, the only field unique per posting
    (CONTRACT.md, Wrong version 1).
    """
    if seen is None:
        return []
    return [j for j in jobs if j["id"] not in seen]
