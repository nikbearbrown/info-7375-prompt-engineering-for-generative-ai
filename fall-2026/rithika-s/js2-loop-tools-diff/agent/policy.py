"""Permission policy for Job-Search Agent 2 (GATE.md section 5).

Every network request and every file read or write the agent makes goes
through this module. A refusal raises PolicyRefusal with one of the reason
codes from BOUNDARY_TESTS.md; the agent never works around one.

Paths:
  - A relative path is taken relative to the project root, not the current
    working directory.
  - Paths are fully resolved (symlinks followed, ".." collapsed) before they
    are checked, and compared by whole path components, never by string
    prefix: "out-evil/x.json" is not inside "out/".
  - The allowed areas themselves are NOT resolved: if "out" were a symlink
    to somewhere else, nothing inside it would count as being in "out/".
"""

import os
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com"})
ALLOWED_METHODS = frozenset({"GET"})
CREDENTIAL_HEADERS = frozenset({"authorization", "cookie",
                                "proxy-authorization"})
READ_AREAS = ("data", "config", "out")
WRITE_AREA = ("out",)
# The only place an existing file may be replaced: a board's own state file,
# rewritten at the end of a successful fetch. Everything else is write-once.
REPLACE_AREA = ("out", "state")

HOST_NOT_ALLOWED = "host_not_allowed"
NOT_HTTPS = "not_https"
METHOD_NOT_ALLOWED = "method_not_allowed"
CREDENTIALS_NOT_ALLOWED = "credentials_not_allowed"
REDIRECT_OFF_ALLOWLIST = "redirect_off_allowlist"
PATH_OUTSIDE_WRITE_AREA = "path_outside_write_area"
PATH_OUTSIDE_READ_AREA = "path_outside_read_area"
WOULD_OVERWRITE = "would_overwrite"
APPROVAL_DENIED = "approval_denied"


class PolicyRefusal(Exception):
    """A request the policy refuses. `code` is the reason code."""

    def __init__(self, code, detail=""):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)


# --- network ---------------------------------------------------------------

def _host_allowed(host):
    """Exact host match against the allow-list. Never 'ends with'."""
    return host in ALLOWED_HOSTS


def check_request(method, url, headers=None):
    """Return url if the request is allowed; raise PolicyRefusal otherwise."""
    if method not in ALLOWED_METHODS:
        raise PolicyRefusal(METHOD_NOT_ALLOWED, f"method {method!r}")
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise PolicyRefusal(NOT_HTTPS, f"scheme {parts.scheme!r} in {url}")
    host = (parts.hostname or "").lower()
    if not _host_allowed(host):
        raise PolicyRefusal(HOST_NOT_ALLOWED, f"host {host!r}")
    try:
        port = parts.port
    except ValueError:
        raise PolicyRefusal(HOST_NOT_ALLOWED, f"bad port in {url}") from None
    if port not in (None, 443):
        raise PolicyRefusal(HOST_NOT_ALLOWED, f"port {port} on {host}")
    if parts.username is not None or parts.password is not None:
        raise PolicyRefusal(CREDENTIALS_NOT_ALLOWED, "credentials in url")
    for name in (headers or {}):
        if str(name).strip().lower() in CREDENTIAL_HEADERS:
            raise PolicyRefusal(CREDENTIALS_NOT_ALLOWED, f"header {name!r}")
    return url


def check_redirect(from_url, location, headers=None):
    """Return the absolute redirect target if allowed; raise otherwise.

    A target whose host is off the allow-list is refused with
    redirect_off_allowlist. Any other refusal of the target (for example an
    http:// target) keeps its own reason code.
    """
    target = urllib.parse.urljoin(from_url, location or "")
    try:
        return check_request("GET", target, headers)
    except PolicyRefusal as exc:
        if exc.code == HOST_NOT_ALLOWED:
            raise PolicyRefusal(REDIRECT_OFF_ALLOWLIST,
                                f"{from_url} -> {target}") from None
        raise


# --- disk ------------------------------------------------------------------

def _resolve(path, root):
    """Absolute path with symlinks followed and '..' collapsed."""
    path = Path(path)
    if not path.is_absolute():
        path = Path(root) / path
    return path.resolve(strict=False)


def _area(root, parts):
    return Path(root).resolve().joinpath(*parts)


def _inside(path, area):
    """True if path is area or below it, compared by whole components."""
    return Path(path).is_relative_to(area)


def check_read(path, root=ROOT):
    """Return the resolved path if it is inside data/, config/ or out/."""
    resolved = _resolve(path, root)
    for name in READ_AREAS:
        if _inside(resolved, _area(root, (name,))):
            return resolved
    raise PolicyRefusal(PATH_OUTSIDE_READ_AREA, str(path))


def check_write(path, root=ROOT, replace=False):
    """Return the resolved path if a write there is allowed.

    Writes are allowed only inside out/. An existing file is never
    overwritten, except a state file under out/state/ when replace=True.
    """
    resolved = _resolve(path, root)
    out = _area(root, WRITE_AREA)
    if not _inside(resolved, out) or resolved == out:
        raise PolicyRefusal(PATH_OUTSIDE_WRITE_AREA, str(path))
    if os.path.lexists(resolved):
        replaceable = (replace and resolved.is_file()
                       and _inside(resolved, _area(root, REPLACE_AREA)))
        if not replaceable:
            raise PolicyRefusal(WOULD_OVERWRITE, str(path))
    return resolved


def _check_state_path(path, root):
    """A path under out/state/ that may be replaced or reset."""
    if not _inside(_resolve(path, root), _area(root, REPLACE_AREA)):
        raise PolicyRefusal(PATH_OUTSIDE_WRITE_AREA,
                            f"{path} is not a state file under out/state/")
    return check_write(path, root=root, replace=True)


# --- approval --------------------------------------------------------------

def _ask(approver, prompt):
    """Return the approver's answer, or None when no one answers."""
    if approver is None:
        return None
    try:
        return approver(prompt)
    except Exception:  # EOF on stdin, a crashed prompt: no one answered
        return None


def _is_yes(answer):
    if answer is True:
        return True
    return isinstance(answer, str) and answer.strip().lower() == "yes"


def request_state_reset(path, approver=None, root=ROOT):
    """Delete a board's state file, only with an explicit yes.

    `approver` is called with a prompt string and must return True or "yes".
    Anything else, including no approver, None, or an exception, is a no.
    Returns the resolved path that was reset.
    """
    resolved = _check_state_path(path, root)
    prompt = (f"Reset state file {resolved}? Every posting on that board "
              f"will look new on the next run. Answer yes to allow.")
    if not _is_yes(_ask(approver, prompt)):
        raise PolicyRefusal(APPROVAL_DENIED, str(path))
    if resolved.exists():
        resolved.unlink()
    return resolved


# --- file operations that go through the checks ----------------------------

def read_bytes(path, root=ROOT):
    return check_read(path, root).read_bytes()


def write_new(path, data, root=ROOT):
    """Create a new file inside out/; refuse if it already exists."""
    resolved = check_write(path, root)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with open(resolved, "xb") as handle:
        handle.write(data)
    return resolved


def open_new_text(path, root=ROOT):
    """Create a new text file inside out/ and return it open for writing."""
    resolved = check_write(path, root)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return open(resolved, "x", encoding="utf-8")


def replace_state(path, data, tmp_suffix, root=ROOT):
    """Atomically write a state file under out/state/ (may already exist)."""
    resolved = _check_state_path(path, root)
    tmp = write_new(resolved.with_name(f"{resolved.name}.{tmp_suffix}.tmp"),
                    data, root)
    os.replace(tmp, check_write(resolved, root, replace=True))
    return resolved
