"""The permission policy from GATE.md, enforced in code. Every network call and every file
operation the agent makes goes through Policy; anything outside it raises PolicyRefused.

Three separate decisions, in this order: the operation vocabulary, then the target (host for
fetch, resolved path for files), then approval (reset_state only) or merge-only (update_state).
This is a preflight plus the write itself; it is not an operating-system sandbox.
"""
import json
import os
import tempfile
import urllib.parse
from pathlib import Path

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com"})
OPERATIONS = frozenset({"fetch", "read_file", "write_run_file", "update_state", "reset_state"})
FILE_OPERATIONS = OPERATIONS - {"fetch"}


class PolicyRefused(PermissionError):
    pass


class Policy:
    def __init__(self, root):
        self.root = Path(root).resolve()

    # --- the three decisions -----------------------------------------------------------------
    def _contained(self, base, path):
        # A relation between resolved paths, never a string prefix (wrong version 1).
        return path.is_relative_to(base)

    def _approved(self, value):
        # Exactly the boolean True; "yes", 1 and None are not approval (wrong version 4).
        return value is True

    def authorize(self, operation, target, method="GET", approved=False, old_ids=None, new_ids=None):
        """Host (fetch) or resolved Path (file operations) if allowed; PolicyRefused otherwise."""
        if operation not in OPERATIONS:
            raise PolicyRefused(f"operation {operation!r} is not in the vocabulary {sorted(OPERATIONS)}")
        if operation == "fetch":
            return self._check_fetch(target, method)
        path = (self.root / target).resolve()
        if not self._contained(self.root, path):
            raise PolicyRefused(f"{operation}: {target!r} resolves outside the output root")
        if operation == "reset_state" and not self._approved(approved):
            raise PolicyRefused(f"reset_state needs approved=True, got {approved!r}")
        if operation == "update_state" and old_ids is not None and new_ids is not None:
            dropped = set(old_ids) - set(new_ids)
            if dropped:
                raise PolicyRefused(f"update_state would drop {len(dropped)} existing id(s); "
                                    "replacing the set is reset_state, which needs approval")
        return path

    def _check_fetch(self, url, method):
        if method != "GET":
            raise PolicyRefused(f"method {method!r} refused: the agent only sends GET")
        parts = urllib.parse.urlsplit(url)
        host = parts.hostname
        if parts.scheme != "https" or parts.username or parts.password or host not in ALLOWED_HOSTS:
            raise PolicyRefused(f"host {host!r} ({parts.scheme}) is not on the allow-list {sorted(ALLOWED_HOSTS)}")
        return host

    def check_redirect(self, new_url):
        """A redirect is a new request: the target host is checked again before it is followed."""
        return self.authorize("fetch", new_url)

    # --- file operations, each through authorize ---------------------------------------------
    def read_file(self, target):
        return self.authorize("read_file", target).read_bytes()

    def exists(self, target):
        return self.authorize("read_file", target).exists()

    def write_run_file(self, target, data):
        path = self.authorize("write_run_file", target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def read_state(self, target):
        path = self.authorize("read_file", target)
        if not path.exists():
            return {"seen_ids": [], "boards": []}
        data = json.loads(path.read_text(encoding="utf-8"))
        return {"seen_ids": list(data.get("seen_ids", [])), "boards": list(data.get("boards", []))}

    def update_state(self, target, ids, boards=()):
        """Merge ids (and board keys) into the state; never drop one (wrong version 6)."""
        old = self.read_state(target)
        new_ids = sorted(set(old["seen_ids"]) | set(ids))
        path = self.authorize("update_state", target, old_ids=old["seen_ids"], new_ids=new_ids)
        self._write_json(path, {"seen_ids": new_ids, "boards": sorted(set(old["boards"]) | set(boards))})
        return new_ids

    def reset_state(self, target, ids, approved=False, boards=()):
        """Replace the state with exactly ids. Needs approved=True; never overrides containment."""
        path = self.authorize("reset_state", target, approved=approved)
        self._write_json(path, {"seen_ids": sorted(set(ids)), "boards": sorted(set(boards))})
        return sorted(set(ids))

    @staticmethod
    def _write_json(path, obj):
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                json.dump(obj, f, indent=2)
                f.write("\n")
            os.replace(tmp, path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise
