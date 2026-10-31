"""Allow-listed fetch of a public Ashby job board; the raw response is saved as evidence."""
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from . import Refused

ALLOWED_HOSTS = {"api.ashbyhq.com"}
BOARDS = {"commure": "https://api.ashbyhq.com/posting-api/job-board/commure"}
# Ashby answered 403 to urllib's default User-Agent on 2026-10-14; identify ourselves honestly.
USER_AGENT = "earlybird/0.1 (INFO 7375 student project; read-only)"


def check_host(url):
    host = urlparse(url).hostname
    if host not in ALLOWED_HOSTS:
        raise Refused(f"not able to fetch {host}: it is not on the allow-list {sorted(ALLOWED_HOSTS)}")


def fetch(url, opener=urllib.request.urlopen):
    check_host(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener(req, timeout=30) as resp:
        return resp.read()


def save_raw(body, raw_dir, day, board):
    out = Path(raw_dir) / day
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"ashby_{board}.json"
    path.write_bytes(body)
    return path
