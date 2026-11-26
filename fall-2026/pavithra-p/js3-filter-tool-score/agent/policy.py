"""The permission policy from GATE.md, enforced in code. Every request and every file write goes through here."""
import os
import tempfile
import urllib.parse
from pathlib import Path

from . import config


class PolicyRefused(Exception):
    """Raised before the action happens: no connection is made and no file is written."""


class Policy:
    def __init__(self, root=config.ROOT, hosts=None, write_dirs=config.WRITE_DIRS, approval_paths=config.APPROVAL_PATHS):
        self.root = Path(root).resolve()
        self.hosts = frozenset(hosts if hosts is not None else config.load("hosts")["allowed_hosts"])
        self.write_dirs = [self.root / d for d in write_dirs]
        self.approval_paths = [self.root / p for p in approval_paths]

    def check_request(self, method, url):
        """Only GET, only https, only an allowed host (exact match, so a look-alike host fails)."""
        parts = urllib.parse.urlsplit(url)
        if method != "GET":
            raise PolicyRefused(f"refused: {method} {url} (the agent only sends GET)")
        if parts.scheme != "https":
            raise PolicyRefused(f"refused: {url} is not https")
        if parts.hostname not in self.hosts:
            raise PolicyRefused(f"refused: {parts.hostname!r} is not on the allow-list {sorted(self.hosts)}")
        return url

    def _resolve(self, path):
        """The real path after `..` and symlinks, so the check sees where a write would really land."""
        path = Path(path)
        return (path if path.is_absolute() else self.root / path).resolve()

    def check_read(self, path):
        real = self._resolve(path)
        if not real.is_relative_to(self.root):
            raise PolicyRefused(f"refused: read of {path} is outside {self.root.name}/")
        return real

    def check_write(self, path, approved=False):
        """Allowed inside runs/ or evidence/; config/ and the relevance rule only with my approval; nothing else."""
        real = self._resolve(path)
        if any(real.is_relative_to(d) for d in self.write_dirs):
            return real
        if any(real.is_relative_to(p) for p in self.approval_paths):
            if approved:
                return real
            raise PolicyRefused(f"refused: writing {path} needs my approval (GATE.md)")
        raise PolicyRefused(f"refused: {path} is outside runs/ and evidence/")

    def write_bytes(self, path, data, approved=False):
        """The only way the agent writes a file: checked first, then written atomically."""
        real = self.check_write(path, approved)
        real.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=real.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            os.replace(tmp, real)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise
        return real

    def write_text(self, path, text, approved=False):
        return self.write_bytes(path, text.encode("utf-8"), approved)
