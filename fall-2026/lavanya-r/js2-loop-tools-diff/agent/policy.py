"""The permission policy from GATE.md section 5, enforced in code.

Every network call and every file read or write in JS2 goes through a Policy
object. Nothing here depends on a prompt: a refused request raises before any
socket is opened or any byte is written.

    decide(...)  -> Decision(outcome, reason)   pure: no side effects
    check_*(...) -> raises Refused / NeedsApproval, or returns the safe path
"""

import os
import pathlib
import urllib.parse
from dataclasses import dataclass

ALLOWED_HOSTS = frozenset({
    "boards-api.greenhouse.io",
    "api.lever.co",
    "api.ashbyhq.com",
})
ALLOWED_ACTIONS = frozenset({"fetch_board", "read_file", "write_file"})
NEVER_ACTIONS = frozenset({"apply", "email", "message", "login"})
WRITE_DIRS = ("runs", "state")

ALLOW, REFUSE, ASK = "allow", "refuse", "ask"


class Refused(PermissionError):
    """The policy said no. Nothing was fetched or written."""


class NeedsApproval(Refused):
    """The policy needs Lavanya's approval, and it was not given."""


@dataclass(frozen=True)
class Decision:
    outcome: str          # allow | refuse | ask
    reason: str


def _inside(path, folder):
    """True if real path `path` is `folder` or below it. Compares path parts,
    not strings, so `runs-evil` is not inside `runs`."""
    try:
        pathlib.Path(path).relative_to(folder)
        return True
    except ValueError:
        return False


class Policy:
    def __init__(self, root, read_roots=None):
        # root = this JS2 folder. Reads: JS2 and the sibling JS1 folder.
        self.root = pathlib.Path(os.path.realpath(root))
        self.read_roots = [pathlib.Path(os.path.realpath(r)) for r in (
            read_roots or [self.root,
                           self.root.parent / "js1-contract-and-watch"])]
        self.write_roots = [self.root / d for d in WRITE_DIRS]

    # ---------- pure decisions ----------

    def decide_action(self, name):
        if name in NEVER_ACTIONS:
            return Decision(REFUSE, f"{name!r} is on the never list")
        if name not in ALLOWED_ACTIONS:
            return Decision(REFUSE, f"{name!r} is not an allowed action")
        return Decision(ALLOW, f"{name!r} is an allowed action")

    def decide_url(self, url, method="GET"):
        if method != "GET":
            return Decision(REFUSE, f"method {method} not allowed; GET only")
        p = urllib.parse.urlsplit(url)
        if p.scheme != "https":
            return Decision(REFUSE, f"scheme {p.scheme!r} not allowed; "
                                    "https only")
        if p.username or p.password:
            return Decision(REFUSE, "credentials in URL not allowed")
        try:
            port = p.port
        except ValueError:
            return Decision(REFUSE, "malformed port")
        if port not in (None, 443):
            return Decision(REFUSE, f"port {port} not allowed")
        if p.hostname not in ALLOWED_HOSTS:
            return Decision(REFUSE, f"host {p.hostname!r} is not one of "
                                    f"{sorted(ALLOWED_HOSTS)}")
        return Decision(ALLOW, f"host {p.hostname!r} is allowed")

    def _real(self, path):
        path = pathlib.Path(path)
        if not path.is_absolute():
            path = self.root / path
        # realpath follows every symlink that exists, and `..`
        return pathlib.Path(os.path.realpath(path))

    def decide_read(self, path):
        real = self._real(path)
        if any(_inside(real, r) for r in self.read_roots):
            return Decision(ALLOW, f"read inside {real.parent}")
        return Decision(REFUSE, f"read of {real} is outside my JS1/JS2 "
                                "folders")

    def decide_write(self, path):
        real = self._real(path)
        if not any(_inside(real, w) and real != w for w in self.write_roots):
            return Decision(REFUSE, f"write to {real} is outside "
                                    f"{', '.join(WRITE_DIRS)}/")
        if _inside(real, self.root / "state") and real.exists():
            return Decision(ASK, f"overwriting {real.name} in state/ needs "
                                 "approval")
        return Decision(ALLOW, f"write inside {real.parent}")

    # ---------- enforcement ----------

    def check_action(self, name):
        d = self.decide_action(name)
        if d.outcome != ALLOW:
            raise Refused(d.reason)

    def check_url(self, url, method="GET"):
        d = self.decide_url(url, method)
        if d.outcome != ALLOW:
            raise Refused(d.reason)
        return url

    def check_read(self, path):
        d = self.decide_read(path)
        if d.outcome != ALLOW:
            raise Refused(d.reason)
        return self._real(path)

    def check_write(self, path, approver=None):
        """Return the real path to write to, or raise. `approver(path)` is
        asked only when the decision is ASK; no approver means no."""
        d = self.decide_write(path)
        if d.outcome == REFUSE:
            raise Refused(d.reason)
        real = self._real(path)
        if d.outcome == ASK and not (approver and approver(real)):
            raise NeedsApproval(d.reason + "; approval not given")
        return real

    # ---------- the only file I/O JS2 does ----------

    def read_bytes(self, path):
        self.check_action("read_file")
        return self.check_read(path).read_bytes()

    def write_bytes(self, path, data, approver=None):
        self.check_action("write_file")
        real = self.check_write(path, approver)
        real.parent.mkdir(parents=True, exist_ok=True)
        # check again after mkdir: a symlink could have appeared in between
        if self._real(real) != real or not any(
                _inside(real, w) for w in self.write_roots):
            raise Refused(f"{real} moved outside the write folders")
        tmp = real.with_name(real.name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, real)
        return real


def no_approval(_path):
    return False


def always_approve(_path):
    return True


def ask_on_terminal(path):
    """Interactive approval: only a human typing y at a real terminal."""
    import sys
    if not sys.stdin.isatty():
        return False
    ans = input(f"Overwrite {path}? This replaces the saved list of jobs "
                "already seen. [y/N] ")
    return ans.strip().lower() == "y"
