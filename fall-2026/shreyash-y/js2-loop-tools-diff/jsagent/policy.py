"""The permission policy from GATE.md section 6, enforced in code (GATE-NOTES.md says how each
phrase was read). Every network request and every file write in the agent goes through here."""
import os
import pathlib
import re
import urllib.parse

ALLOWED = {
    "boards-api.greenhouse.io": re.compile(r"^/v1/boards/[a-z0-9-]{1,64}/jobs$"),
    "api.ashbyhq.com": re.compile(r"^/posting-api/job-board/[A-Za-z0-9-]{1,64}$"),
    "api.lever.co": re.compile(r"^/v0/postings/[A-Za-z0-9-]{1,64}$"),
}


class PolicyViolation(Exception):
    def __init__(self, kind, message):
        super().__init__(f"{kind}: {message}")
        self.kind = kind


class NeedsApproval(PolicyViolation):
    def __init__(self, message):
        super().__init__("needs-approval", message)


def check_request(method, url):
    if method != "GET":
        raise PolicyViolation("method", f"{method} refused; the agent only reads (GET)")
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise PolicyViolation("scheme", f"{url} is not https")
    if parts.username or parts.password or parts.port or parts.hostname not in ALLOWED:
        raise PolicyViolation("host", f"host {parts.hostname!r} is not on the allow-list {sorted(ALLOWED)}")
    if not ALLOWED[parts.hostname].match(parts.path):
        raise PolicyViolation("path", f"{parts.path} is not the job-list endpoint for {parts.hostname}")


def check_redirect(old_url, new_url):
    check_request("GET", urllib.parse.urljoin(old_url, new_url))


class Files:
    """Reads inside the project folder; writes inside runs/ only. A file that already existed when
    this object was made cannot be overwritten, appended to or deleted without approve=True."""

    def __init__(self, project, runs, approve=False):
        self.project = pathlib.Path(project).resolve()
        self.runs = pathlib.Path(runs).resolve()
        self.approve = approve
        self.created = set()

    @staticmethod
    def _inside(real, root):
        return real != root and root in real.parents

    def _writable(self, path):
        p = pathlib.Path(path)
        if p.is_symlink():
            raise PolicyViolation("outside-runs", f"{path} is a symlink; writes never follow links")
        real = p.resolve()
        if not self._inside(real, self.runs):
            raise PolicyViolation("outside-runs", f"{path} resolves to {real}, outside {self.runs}")
        return real

    def _guard_existing(self, real, verb):
        if real.exists() and real not in self.created and not self.approve:
            raise NeedsApproval(f"{verb} {real} would change saved evidence or state; rerun with --approve-overwrite")

    def write(self, path, data):
        real = self._writable(path)
        self._guard_existing(real, "writing")
        real.parent.mkdir(parents=True, exist_ok=True)
        real.write_bytes(data)
        self.created.add(real)
        return real

    def append(self, path, data):
        real = self._writable(path)
        self._guard_existing(real, "appending to")
        real.parent.mkdir(parents=True, exist_ok=True)
        with open(real, "ab") as f:
            f.write(data)
        self.created.add(real)
        return real

    def delete(self, path):
        real = self._writable(path)
        if not self.approve:
            raise NeedsApproval(f"deleting {real} needs approval")
        os.unlink(real)

    def read(self, path):
        real = pathlib.Path(path).resolve()
        if not (real == self.project or self.project in real.parents):
            raise PolicyViolation("read-outside", f"{path} is outside {self.project}")
        return real.read_bytes()
