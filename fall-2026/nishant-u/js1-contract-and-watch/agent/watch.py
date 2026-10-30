"""The watch: fetch one allow-listed board, save the raw response, report ids new since last run."""
import hashlib
import json
import os
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/faire/jobs?content=true"
USER_AGENT = "info7375-js1-coursework (GET only)"


class RefusedHost(ValueError):
    pass


def check_host(url):
    host = urllib.parse.urlsplit(url).hostname
    if host not in ALLOWED_HOSTS:
        raise RefusedHost(f"host {host!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")
    return host


class _AllowListRedirects(urllib.request.HTTPRedirectHandler):
    # Without this, urlopen would follow a redirect to any host.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_host(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(_AllowListRedirects)


def fetch(url, opener=None):
    """GET url and return the body bytes, refusing a non-allow-listed host before any request."""
    check_host(url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    with (opener or _OPENER.open)(request, timeout=30) as response:
        return response.read()


def parse_jobs(body):
    jobs = json.loads(body.decode("utf-8"))["jobs"]
    for job in jobs:
        if type(job.get("id")) is not int:
            raise ValueError("every posting must have an integer id")
    return jobs


def new_run_dir(runs_dir, day):
    runs_dir = Path(runs_dir)
    n = 1
    while (runs_dir / f"{day}-{n}").exists():
        n += 1
    path = runs_dir / f"{day}-{n}"
    path.mkdir(parents=True)
    return path


def write_json_atomic(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def save_raw(run_dir, body, **meta):
    """Save the response bytes verbatim as raw.json, and its sha256 and provenance as meta.json."""
    (Path(run_dir) / "raw.json").write_bytes(body)
    meta = dict(meta, sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
    write_json_atomic(Path(run_dir) / "meta.json", meta)
    return meta


def compare_seen(state_path, ids):
    """(new ids, is_baseline). With no state file yet, the run is a baseline and nothing is new."""
    state_path = Path(state_path)
    if not state_path.exists():
        return [], True
    seen = set(json.loads(state_path.read_text(encoding="utf-8"))["seen_ids"])
    return sorted(set(ids) - seen), False


SEEDED_NOTE = "SEEDED state, not a live change: updated by a run labeled seeded ({run_id})."


def save_seen(state_path, ids, run_id, seeded=False):
    """Merge ids into the state. A state once marked seeded keeps "seeded": true and its note,
    and a seeded run marks the state it writes, so a seeded state can never look real."""
    state_path = Path(state_path)
    old = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    state = {}
    if seeded or old.get("seeded"):
        state = {"seeded": True, "note": old.get("note") or SEEDED_NOTE.format(run_id=run_id)}
    state.update({"last_run": run_id, "seen_ids": sorted(set(old.get("seen_ids", [])) | set(ids))})
    write_json_atomic(state_path, state)
