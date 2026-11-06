"""Live fetch, raw evidence and seeded mode (CONTRACT.md §1 items 1, 6, 7; §2; §3.1)."""

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .config import BOARD_TOKEN, require_fetch_url
from .errors import Refusal, RunError

SIDECAR_SUFFIX = ".sidecar.json"


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """§3.1: a redirect is refused and logged, not followed.

    Decision 2026-10-27: every redirect, even to the same host, since §1 allows one URL only.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Refusal(f"server answered {code} with a redirect to {newurl!r}; redirects are not followed (§3.1)")


def fetch_live(url, allow_list, timeout=30):
    """Fetch the one §1 URL. Returns (raw response bytes, UTC fetch time)."""
    require_fetch_url(url, allow_list)
    opener = urllib.request.build_opener(_RefuseRedirects)
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    fetched_at = datetime.now(timezone.utc)
    try:
        with opener.open(request, timeout=timeout) as response:
            status = response.status
            final_url = response.geturl()
            raw = response.read()
    except OSError as exc:  # includes urllib.error.URLError and HTTPError
        raise RunError(f"fetch of {url} failed: {exc}") from exc
    if final_url != url:
        raise Refusal(f"response came from {final_url!r}, not {url!r} (§3.1)")
    if status != 200:
        raise RunError(f"fetch of {url} returned HTTP {status}")
    return raw, fetched_at


def save_evidence(raw, url, fetched_at, evidence_dir):
    """Save the raw bytes unchanged plus a sidecar note (§2). Never overwrites a file."""
    stamp = fetched_at.strftime("%Y-%m-%dT%H%M%SZ")
    name = f"{BOARD_TOKEN}_jobs_content_true_{stamp}.json"
    note = {
        "url": url,
        "fetched_at": fetched_at.isoformat(timespec="seconds"),
        "file": name,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    try:
        with open(evidence_dir / name, "xb") as fh:
            fh.write(raw)
        with open(evidence_dir / (name + SIDECAR_SUFFIX), "x", encoding="utf-8") as fh:
            json.dump(note, fh, indent=2)
            fh.write("\n")
    except FileExistsError as exc:
        raise RunError(f"evidence file already exists, not overwriting: {exc.filename}") from exc
    return note


def load_seed(seed_path, evidence_dir):
    """§1 item 6: a seeded run reads one saved board response from evidence/ only."""
    seed = Path(seed_path).resolve()
    evidence = Path(evidence_dir).resolve()
    if seed == evidence or not seed.is_relative_to(evidence):
        raise Refusal(f"seed file {seed_path!r} is not inside {evidence_dir} (§1 item 6)")
    if seed.name.endswith(SIDECAR_SUFFIX):
        raise Refusal(f"{seed.name} is a sidecar note, not a saved board response")
    try:
        raw = seed.read_bytes()
    except OSError as exc:
        raise RunError(f"cannot read seed file {seed}: {exc}") from exc
    source = {
        "file": seed.relative_to(evidence).as_posix(),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    return raw, source
