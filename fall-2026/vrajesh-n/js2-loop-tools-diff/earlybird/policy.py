"""The permission policy from GATE.md, enforced in code. Every network or disk action asks this first."""
from pathlib import Path
from urllib.parse import urlparse

from . import Refused

ALLOWED_HOSTS = frozenset({"api.ashbyhq.com", "boards-api.greenhouse.io", "api.lever.co"})
WRITABLE = ("data/raw", "data/state", "reports")
NEEDS_APPROVAL = ("config/boards.json",)
APPROVAL_WORD = "yes"


class Policy:
    def __init__(self, root):
        self.root = Path(root).resolve()

    # --- network -------------------------------------------------------
    def check_fetch(self, url, method="GET"):
        if method != "GET":
            raise Refused(f"method {method} refused: GET only")
        u = urlparse(url)
        if u.scheme != "https":
            raise Refused(f"{url} refused: https only")
        if u.username is not None or u.password is not None:
            raise Refused(f"{url} refused: credentials in a URL mean logging in, which the agent never does")
        host = (u.hostname or "").lower()
        if host not in ALLOWED_HOSTS:
            raise Refused(f"{host or url} refused: not on the allow-list {sorted(ALLOWED_HOSTS)}")
        if u.port not in (None, 443):
            raise Refused(f"{url} refused: non-standard port {u.port}")
        return url

    # --- disk ----------------------------------------------------------
    def resolve(self, path):
        """Absolute, with `..` and symlinks/junctions resolved, so the check sees where a write really lands."""
        p = Path(path)
        if not p.is_absolute():
            p = self.root / p
        return p.resolve()

    @staticmethod
    def _inside(path, base):
        # Path.is_relative_to compares whole components, so `reports-evil` is not inside `reports`.
        return path.is_relative_to(base)

    def check_read(self, path):
        p = self.resolve(path)
        if not self._inside(p, self.root):
            raise Refused(f"read of {path} refused: outside the project folder")
        return p

    def check_write(self, path, approval=None):
        p = self.resolve(path)
        for rel in NEEDS_APPROVAL:
            if p == (self.root / rel).resolve():
                if (approval or "").strip() != APPROVAL_WORD:
                    raise Refused(f"write to {rel} refused: needs the owner to type '{APPROVAL_WORD}' "
                                  f"(got {approval!r})")
                return p
        for rel in WRITABLE:
            base = (self.root / rel).resolve()
            if p != base and self._inside(p, base):
                return p
        raise Refused(f"write to {path} refused: it resolves to {p}, outside {list(WRITABLE)}")
