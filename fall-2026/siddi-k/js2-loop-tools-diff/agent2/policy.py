"""Permission policy (GATE.md §5), enforced in code: every URL, read and write goes through here."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com", "api.smartrecruiters.com"})
WRITE_ROOT = ROOT / "evidence" / "runs"
# Writes here need Siddi's explicit approval (config, budgets, allow-list, source code, the gate itself).
APPROVAL_ROOTS = ("config", "agent2", "GATE.md")
SECRET_NAMES = frozenset({".env", ".credentials.json", "credentials.json", "id_rsa", ".netrc", ".git-credentials"})


class Refused(Exception):
    """Never allowed under GATE.md §5."""


class NeedsApproval(Exception):
    """Allowed only with Siddi's explicit approval (GATE.md §5)."""


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


def _resolve(path) -> tuple[Path, Path]:
    raw = Path(path)
    if ".." in raw.parts:
        raise Refused(f"{path!s}: '..' path segments are never allowed")
    full = raw if raw.is_absolute() else ROOT / raw
    return full, full.resolve()          # resolve() follows symlinks and Windows junctions


def check_read(path) -> Path:
    full, real = _resolve(path)
    if not real.is_relative_to(ROOT.resolve()):
        raise Refused(f"{path!s}: reads are allowed only inside this assignment folder")
    if real.name in SECRET_NAMES:
        raise Refused(f"{path!s}: secrets and credentials are never read")
    return real


def check_write(path, approved: bool = False) -> Path:
    full, real = _resolve(path)
    root = ROOT.resolve()
    if not real.is_relative_to(root):
        raise Refused(f"{path!s}: resolves outside this assignment folder ({real})")
    if real.is_relative_to(WRITE_ROOT.resolve()):
        if real.exists() and not approved:
            raise NeedsApproval(f"{path!s}: overwriting an existing file needs approval")
        return real
    rel = real.relative_to(root)
    if rel.parts and rel.parts[0] in APPROVAL_ROOTS:
        if not approved:
            raise NeedsApproval(f"{path!s}: changing {rel.parts[0]} needs approval")
        return real
    raise Refused(f"{path!s}: writes are allowed only under evidence/runs/")


def write_bytes(path, data: bytes, approved: bool = False) -> Path:
    real = check_write(path, approved)
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_bytes(data)
    return real


def read_bytes(path) -> bytes:
    return check_read(path).read_bytes()
