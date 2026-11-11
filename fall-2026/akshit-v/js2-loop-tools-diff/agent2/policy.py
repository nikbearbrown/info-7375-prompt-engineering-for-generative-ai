"""The permission policy from GATE.md section 6, enforced in code (not in a prompt).

Every network request and every file write in the agent goes through these checks.
"""
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.lever.co", "api.ashbyhq.com"})
ALLOWED_METHODS = frozenset({"GET"})
APPROVAL_RESET_STATE = "reset-state"


class PolicyViolation(Exception):
    """A request the policy refuses. The loop treats this as exit `error`."""


class NeedsApproval(PolicyViolation):
    """A request that is allowed only with an explicit approval from me."""


def check_request(method: str, url: str) -> None:
    parts = urlsplit(url)
    if method.upper() not in ALLOWED_METHODS:
        raise PolicyViolation(f"method {method!r} refused: GET only (the agent never applies, emails, messages, or logs in)")
    if parts.scheme != "https":
        raise PolicyViolation(f"scheme {parts.scheme!r} refused: https only")
    if parts.hostname not in ALLOWED_HOSTS:
        raise PolicyViolation(f"host {parts.hostname!r} refused: not on the allow-list")
    if parts.username or parts.password:
        raise PolicyViolation("credentials in URL refused: the agent never logs in")


def _inside(path: Path, folder: Path) -> bool:
    # resolve() follows symlinks and Windows junctions, and removes "..". Compare whole
    # path components, never string prefixes ("out-evil" must not pass as "out").
    return path.resolve().is_relative_to(folder.resolve())


def check_write(path, out_dir: Path = OUT) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    if not _inside(p, out_dir):
        raise PolicyViolation(f"write refused: {path} resolves outside the output folder {out_dir}")
    return p.resolve()


def check_read(path, root: Path = ROOT) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    if not _inside(p, root):
        raise PolicyViolation(f"read refused: {path} resolves outside the project folder")
    return p.resolve()


def write_bytes(path, data: bytes, out_dir: Path = OUT) -> Path:
    p = check_write(path, out_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    check_write(p.parent, out_dir)  # the folder just created must also be inside
    p.write_bytes(data)
    return p


def reset_state(state_path, approvals=frozenset(), out_dir: Path = OUT) -> None:
    """Deleting the seen-id state needs my explicit approval (--approve reset-state)."""
    p = check_write(state_path, out_dir)
    if APPROVAL_RESET_STATE not in approvals:
        raise NeedsApproval("resetting the state file needs approval: pass --approve reset-state")
    if p.exists():
        p.unlink()
