"""Allow-listed fetch of Greenhouse boards (v3: every board in config/boards.json); raw bytes saved as evidence."""
import html
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_PATH = ROOT / "config" / "allowlist.json"
BOARDS_PATH = ROOT / "config" / "boards.json"
JOB_ID_RE = re.compile(r"^\d+$")
MAX_WORKERS = 8
BOARD_RE = re.compile(r"^[a-z0-9-]+$")
USER_AGENT = "INFO7375-job-search-agent-1 (student coursework; read-only)"


class HostNotAllowed(Exception):
    pass


def load_allowlist(path=ALLOWLIST_PATH):
    return set(json.loads(Path(path).read_text())["hosts"])


def check_url(url, allow):
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise HostNotAllowed(f"refusing non-https URL: {url}")
    if parts.hostname not in allow:
        raise HostNotAllowed(f"refusing host not on allow-list: {parts.hostname}")


def load_boards(path=BOARDS_PATH):
    return list(json.loads(Path(path).read_text())["boards"])


def list_url(board):
    """Job list without descriptions (v3): small; descriptions are fetched only for postings that get judged."""
    return board_url(board).replace("?content=true", "")


def job_url(board, job_id):
    if not isinstance(job_id, str) or not JOB_ID_RE.match(job_id):
        raise ValueError(f"bad job id: {job_id!r}")
    return list_url(board) + "/" + job_id


def get_bytes(url, allow):
    check_url(url, allow)
    opener = urllib.request.build_opener(AllowListRedirectHandler(allow))
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with opener.open(req, timeout=60) as resp:
        check_url(resp.geturl(), allow)
        return resp.read()


def fetch_lists(boards, run_dir, allow=None):
    """GET every board's job list (at most MAX_WORKERS at once); save raw bytes. Returns (raws, errors)."""
    from concurrent.futures import ThreadPoolExecutor
    allow = load_allowlist() if allow is None else allow
    out = Path(run_dir) / "boards"
    out.mkdir(parents=True, exist_ok=True)

    def one(board):
        try:
            body = get_bytes(list_url(board), allow)
        except HostNotAllowed:
            raise
        except Exception as e:  # a failed board is recorded, never guessed
            return board, None, f"{type(e).__name__}: {e}"[:200]
        unused_path(out / f"{board}.json").write_bytes(body)
        return board, body, None

    raws, errors = {}, {}
    with ThreadPoolExecutor(MAX_WORKERS) as ex:
        for board, body, err in ex.map(one, boards):
            if err:
                errors[board] = err
            else:
                raws[board] = body
    return raws, errors


def fetch_job(board, job_id, run_dir, allow=None):
    allow = load_allowlist() if allow is None else allow
    body = get_bytes(job_url(board, job_id), allow)
    out = Path(run_dir) / "jobs"
    out.mkdir(parents=True, exist_ok=True)
    unused_path(out / f"{board}_{job_id}.json").write_bytes(body)
    return body


def load_run_dir(run_dir):
    """Read a saved run folder: {board: raw list bytes}."""
    return {p.stem: p.read_bytes() for p in sorted((Path(run_dir) / "boards").glob("*.json"))}


def saved_job(run_dir, board, job_id):
    return (Path(run_dir) / "jobs" / f"{board}_{job_id}.json").read_bytes()


def board_url(board):
    if not isinstance(board, str) or not BOARD_RE.match(board):
        raise ValueError(f"bad board token: {board!r}")
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


class AllowListRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, allow):
        super().__init__()
        self.allow = allow

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl, self.allow)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_board(board, raw_dir, allow=None, now=None):
    """GET the board JSON, save the raw bytes untouched, return (path, bytes)."""
    allow = load_allowlist() if allow is None else allow
    url = board_url(board)
    check_url(url, allow)
    opener = urllib.request.build_opener(AllowListRedirectHandler(allow))
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with opener.open(req, timeout=30) as resp:
        check_url(resp.geturl(), allow)
        body = resp.read()
    now = now or datetime.now().astimezone()
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = unused_path(raw_dir / f"{now:%Y-%m-%dT%H%M%S}_{board}_live.json")
    path.write_bytes(body)
    return path, body


def unused_path(path):
    """Never overwrite evidence: two fetches in the same second get _2, _3, ... (bug found 2026-10-31)."""
    path = Path(path)
    n = 2
    candidate = path
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}_{n}{path.suffix}")
        n += 1
    return candidate


_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def html_to_text(s):
    # Greenhouse ships content HTML-escaped: unescape, strip tags, unescape entities left inside.
    text = _TAG.sub(" ", html.unescape(s or ""))
    return _WS.sub(" ", html.unescape(text)).strip()


def _normalize(j):
    return {
            "id": str(j["id"]),
            "title": (j.get("title") or "").strip(),
            "location": {"name": ((j.get("location") or {}).get("name") or "").strip()},
            "departments": [d.get("name", "") for d in j.get("departments") or []],
            "content": html_to_text(j.get("content")),
            "absolute_url": j.get("absolute_url", ""),
            "updated_at": j.get("updated_at", ""),
    }


def parse_postings(raw_bytes, board=None):
    postings = [_normalize(j) for j in json.loads(raw_bytes)["jobs"]]
    if board is not None:
        for p in postings:
            p["board"] = board
    return postings


def parse_job(raw_bytes, board):
    return dict(_normalize(json.loads(raw_bytes)), board=board)


def posting_field(posting, field):
    if field == "location.name":
        return posting["location"]["name"]
    if field in ("title", "content"):
        return posting[field]
    if field == "departments":
        return ", ".join(posting["departments"])
    raise KeyError(field)
