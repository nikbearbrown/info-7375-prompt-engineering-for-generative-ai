"""JS2 permission policy, enforced in code (GATE.md section 5). Every request and every file access in the loop goes through here.

Network: HTTPS GET only, exact allow-listed hosts. The host and scheme check is JS1's fetch.check_url, reused.
Files: read only the listed folders; write only inside the output root; overwriting or deleting needs a named approval.
"""
import json
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from . import fetch

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_PATH = ROOT / "config" / "allowlist.json"
PROTECTED = ("config", "baseline", "persona", "prompts", "tests", "jsagent", "scripts")
READABLE = ("config", "persona", "baseline", "prompts", "tests/fixtures")
ALLOWED_METHODS = {"GET"}


class PolicyViolation(Exception):
    def __init__(self, rule, message):
        super().__init__(f"[{rule}] {message}")
        self.rule = rule
        self.message = message


class NeedsApproval(Exception):
    def __init__(self, path):
        super().__init__(f"[files.approval] this write needs --approve {path}")
        self.path = path


def load_allowlist(path=ALLOWLIST_PATH):
    return set(json.loads(Path(path).read_text())["hosts"])


# ---------------------------------------------------------------- network

def check_url(url, allow, method="GET"):
    """Refuse anything but an HTTPS GET to an allow-listed host. Raises PolicyViolation."""
    if str(method).upper() not in ALLOWED_METHODS:
        raise PolicyViolation("network.method", f"only GET is allowed; refused {method} {url}")
    try:
        fetch.check_url(url, allow)  # JS1's scheme + exact-host check, reused unchanged
    except fetch.HostNotAllowed as e:
        raise PolicyViolation("network.host", str(e)) from None


def normalize_url(url):
    """The repeat rule's identity for a URL: lowercase scheme and host, no default port, no trailing slash, sorted query."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    try:
        port = p.port
    except ValueError:
        port = None
    netloc = host if port in (None, 443) else f"{host}:{port}"
    path = p.path.rstrip("/") or "/"
    query = urlencode(sorted(parse_qsl(p.query, keep_blank_values=True)))
    return urlunsplit((p.scheme.lower(), netloc, path, query, ""))


# ---------------------------------------------------------------- files

def _resolve(path, base):
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = base / p
    return p.resolve()  # follows ".." and symlinks first; containment is compared on the real path


def _inside(path, folder):
    return path == folder or path.is_relative_to(folder)  # path components, never a string prefix


def check_out_root(out_root, root=ROOT):
    root = Path(root).resolve()
    out = _resolve(out_root, root)
    if out == root:
        raise PolicyViolation("files.out_root", "the output root may not be the project root")
    for name in PROTECTED:
        if _inside(out, (root / name).resolve()):
            raise PolicyViolation("files.out_root", f"the output root {out} is inside the protected folder {name}/")
    if out == (root / "evidence").resolve():
        raise PolicyViolation("files.out_root", "the output root may not be evidence/ itself (RUNS.md lives there)")
    return out


class FilePolicy:
    def __init__(self, out_root, root=ROOT, approvals=()):
        self.root = Path(root).resolve()
        self.out = check_out_root(out_root, self.root)
        self.approvals = {_resolve(a, self.root) for a in approvals}
        self.used_approvals = set()

    def resolve(self, path):
        return _resolve(path, self.root)

    def check_read(self, path):
        rp = self.resolve(path)
        readable = [(self.root / d).resolve() for d in READABLE] + [self.out]
        if any(_inside(rp, folder) for folder in readable):
            return rp
        raise PolicyViolation("files.read", f"read outside the readable folders: {path}")

    def check_write(self, path, kind="create"):
        """kind: create (a new file), state (the state file or its temp file), overwrite, delete.
        Returns the resolved path, or raises PolicyViolation / NeedsApproval."""
        rp = self.resolve(path)
        if not _inside(rp, self.out):
            raise PolicyViolation("files.write", f"write outside the output root: {path}")
        for name in PROTECTED:
            if _inside(rp, (self.root / name).resolve()):
                raise PolicyViolation("files.write", f"write into the protected folder {name}/: {path}")
        if kind == "state":
            if rp.parent != self.out / "state":
                raise PolicyViolation("files.state", f"state writes stay in {self.out / 'state'}: {path}")
            return rp
        if kind in ("overwrite", "delete") or rp.exists():
            if rp in self.approvals:
                self.used_approvals.add(rp)
                return rp
            raise NeedsApproval(rp)
        if kind != "create":
            raise PolicyViolation("files.write", f"unknown write kind {kind!r}")
        return rp


def write_new(files, path, data):
    """Create a new file inside the output root. Never overwrites: the open is exclusive, even after the check."""
    rp = files.check_write(path, "create")
    rp.parent.mkdir(parents=True, exist_ok=True)
    with open(rp, "xb") as f:
        f.write(data)
    return rp
