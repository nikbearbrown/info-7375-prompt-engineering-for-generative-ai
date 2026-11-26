"""Permission policy for JS3 (FILTER.md §C and the brief's privacy rules), enforced in code.

Carried over from JS2's agent2/policy.py: https only, GET only, three allow-listed hosts, no credentials,
and writes only inside this assignment folder's output areas."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com", "api.smartrecruiters.com"})
WRITE_ROOTS = ("data/collections", "data/heldout", "output", "evidence", "labels")
SECRET_NAMES = frozenset({".env", ".credentials.json", "credentials.json", "id_rsa", ".netrc", ".git-credentials"})


class Refused(Exception):
    """Never allowed."""


def check_url(url: str, method: str = "GET") -> None:
    p = urlparse(url)
    if method != "GET":
        raise Refused(f"{method} is never allowed: the agent only reads public boards")
    if p.scheme != "https":
        raise Refused(f"{url!r}: only https is allowed")
    if p.username or p.password:
        raise Refused(f"{url!r}: authenticated requests are never allowed")
    if p.hostname not in ALLOWED_HOSTS:
        raise Refused(f"{url!r}: host {p.hostname!r} is not on the allow-list")


def _real(path) -> Path:
    raw = Path(path)
    if ".." in raw.parts:
        raise Refused(f"{path!s}: '..' path segments are never allowed")
    return (raw if raw.is_absolute() else ROOT / raw).resolve()


def check_read(path) -> Path:
    real = _real(path)
    if not real.is_relative_to(ROOT.resolve()):
        raise Refused(f"{path!s}: reads are allowed only inside this assignment folder")
    if real.name in SECRET_NAMES:
        raise Refused(f"{path!s}: secrets and credentials are never read")
    return real


def check_write(path) -> Path:
    real = _real(path)
    root = ROOT.resolve()
    if not any(real.is_relative_to(root / w) for w in WRITE_ROOTS):
        raise Refused(f"{path!s}: writes are allowed only under {', '.join(WRITE_ROOTS)}")
    return real


def write_bytes(path, data: bytes) -> Path:
    real = check_write(path)
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_bytes(data)
    return real
