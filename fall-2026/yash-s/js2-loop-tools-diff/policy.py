"""Job-Search Agent 2: the permission policy, enforced in code (GATE.md section 5).

Every network request and every file the agent reads or writes goes through this module.
Nothing here depends on a prompt: a refused action raises PolicyViolation.

  network  HTTPS GET only, to exactly two hosts, no redirects
  read     persona/, config/, the run folder and the state folder
  write    evidence only inside the run folder, create-only (never overwrites an earlier file);
           state only inside the state folder; resetting a state file needs an explicit approval
Python 3.9 or newer, standard library only.
"""
import json
import os
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com"})
ALLOWED_METHODS = frozenset({"GET"})


class PolicyViolation(Exception):
    """A refused action. The agent stops with exit status 'error' (GATE.md section 4)."""


def check_request(method, url):
    """Allow only an HTTPS GET to an exact allowed host, with no user part and no other port."""
    if method not in ALLOWED_METHODS:
        raise PolicyViolation(f"refusing {method} {url}: only GET is allowed")
    p = urlparse(url)
    if p.scheme != "https":
        raise PolicyViolation(f"refusing {url!r}: HTTPS only")
    if p.hostname not in ALLOWED_HOSTS:
        raise PolicyViolation(f"refusing host {p.hostname!r}: not on the allow-list {sorted(ALLOWED_HOSTS)}")
    if p.username or p.password:
        raise PolicyViolation(f"refusing {url!r}: no user or password in the URL")
    if p.port not in (None, 443):
        raise PolicyViolation(f"refusing {url!r}: port {p.port} is not allowed")
    return url


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect could leave the allow-list, so every redirect is refused (GATE.md: no redirects)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise PolicyViolation(f"refusing redirect ({code}) to {newurl!r}")


def inside(path, folder):
    """True only if `path`, with `..` and every symlink resolved, is `folder` itself or below it.
    Compares whole path components, so `runs-evil` is not inside `runs`."""
    return Path(path).resolve().is_relative_to(Path(folder).resolve())


class Policy:
    def __init__(self, runs_dir, state_dir, read_dirs=()):
        self.runs_dir = Path(runs_dir).resolve()
        self.state_dir = Path(state_dir).resolve()
        self.read_dirs = [Path(d).resolve() for d in read_dirs]

    def check_read(self, path):
        allowed = self.read_dirs + [self.runs_dir, self.state_dir]
        if not any(inside(path, d) for d in allowed):
            raise PolicyViolation(f"refusing to read {path}: outside {[str(d) for d in allowed]}")
        return Path(path).resolve()

    def check_write(self, path, area):
        folder = {"evidence": self.runs_dir, "state": self.state_dir}[area]
        if not inside(path, folder):
            raise PolicyViolation(f"refusing to write {path}: {area} may only be written inside {folder}")
        return Path(path).resolve()

    def read_bytes(self, path):
        return self.check_read(path).read_bytes()

    def make_run_dir(self, name):
        """A new folder for one run's evidence. Never reuses an existing one: `name`, `name-2`, ..."""
        n = 1
        while True:
            candidate = self.runs_dir / (name if n == 1 else f"{name}-{n}")
            target = self.check_write(candidate, "evidence")
            try:
                target.mkdir(parents=True, exist_ok=False)
                return target
            except FileExistsError:
                n += 1

    def write_evidence(self, path, data):
        """Create-only: an existing file is never overwritten (GATE.md: Evidence Preservation)."""
        target = self.check_write(path, "evidence")
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "xb") as f:
            f.write(data if isinstance(data, bytes) else data.encode("utf-8"))
        return target

    def update_state(self, path, obj):
        """The validated normal state update. Atomic: a crash never leaves half a file."""
        target = self.check_write(path, "state")
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=target.name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=2)
                f.write("\n")
            os.replace(tmp, target)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise
        return target

    def reset_state(self, path, approved=False):
        """Removing a board's state (its next run is a baseline) needs explicit approval.
        The folder check comes first: approval never allows a path outside the state folder."""
        target = self.check_write(path, "state")
        if approved is not True:
            raise PolicyViolation(f"refusing to reset {path}: needs explicit approval (--approve-reset)")
        target.unlink(missing_ok=True)
        return target
