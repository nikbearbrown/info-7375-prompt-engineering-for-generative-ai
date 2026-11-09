"""The permission policy from GATE.md, enforced in code. Every tool call is checked here.

Anything refused raises PolicyViolation, and the loop turns that into an `error` exit.
Path checks resolve `..` and symlinks first (realpath), then compare whole path
components (commonpath), so a sibling such as runs-evil/ is never inside runs/.
"""
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com", "api.lever.co"})
ALLOWED_METHODS = frozenset({"GET"})
FORBIDDEN_HEADERS = frozenset({"cookie", "authorization"})
WRITE_DIRS = ("runs", "state")
MAX_WRITE_BYTES = 5 * 1024 * 1024


class PolicyViolation(Exception):
    pass


def ask_in_terminal(action):
    """Approval asks y/N in the terminal. With no terminal attached, the answer is no."""
    if not sys.stdin.isatty():
        return False
    return input(f"Approve: {action}? [y/N] ").strip().lower() == "y"


def inside(path, base):
    path, base = os.path.realpath(path), os.path.realpath(base)
    return os.path.commonpath([path, base]) == base


class Policy:
    def __init__(self, root=HERE, approve=ask_in_terminal):
        self.root = os.path.realpath(root)
        self.approve = approve
        self.decisions = []  # every approval asked for, and the answer

    def _abs(self, path):
        return os.path.realpath(path if os.path.isabs(path) else os.path.join(self.root, path))

    def _rel(self, path):
        return os.path.relpath(path, self.root)

    def check_request(self, method, url, headers=None):
        parts = urllib.parse.urlsplit(url)
        if method.upper() not in ALLOWED_METHODS:
            raise PolicyViolation(f"refused {method} {url}: only GET is allowed")
        if parts.scheme != "https":
            raise PolicyViolation(f"refused {url}: only HTTPS is allowed")
        if parts.hostname not in ALLOWED_HOSTS:
            raise PolicyViolation(f"refused {url}: host {parts.hostname!r} is not on the allow-list")
        if parts.username or parts.password:
            raise PolicyViolation(f"refused {url}: credentials in the URL")
        if parts.port not in (None, 443):
            raise PolicyViolation(f"refused {url}: port {parts.port} is not 443")
        for name in headers or {}:
            if name.lower() in FORBIDDEN_HEADERS:
                raise PolicyViolation(f"refused {url}: the {name} header is never sent")

    def check_read(self, path):
        target = self._abs(path)
        if not inside(target, self.root):
            raise PolicyViolation(f"refused read of {path}: outside {self.root}")
        return target

    def check_write(self, path, size=0):
        target = self._abs(path)
        if not any(inside(target, os.path.join(self.root, d)) for d in WRITE_DIRS):
            raise PolicyViolation(f"refused write to {path}: only {', '.join(d + '/' for d in WRITE_DIRS)} are writable")
        if size > MAX_WRITE_BYTES:
            self.require_approval(f"write {size} bytes to {self._rel(target)} (over {MAX_WRITE_BYTES} bytes)")
        return target

    def check_new_run_dir(self, path):
        target = self.check_write(path)
        if os.path.lexists(target):
            raise PolicyViolation(f"refused to reuse {self._rel(target)}: a run never overwrites an earlier run")
        return target

    def check_delete_run(self, path):
        target = self.check_write(path)
        if not inside(target, os.path.join(self.root, "runs")) or target == os.path.join(self.root, "runs"):
            raise PolicyViolation(f"refused delete of {path}: only a single folder inside runs/ can be deleted")
        self.require_approval(f"delete run folder {self._rel(target)}")
        return target

    def check_state_update(self, old, new):
        """A normal run only adds seen ids. Dropping any needs approval."""
        dropped = {key: sorted(set(board["seen"]) - set(new.get("boards", {}).get(key, {}).get("seen", [])))
                   for key, board in (old or {}).get("boards", {}).items()}
        dropped = {key: ids for key, ids in dropped.items() if ids}
        if dropped:
            count = sum(len(ids) for ids in dropped.values())
            self.require_approval(f"drop {count} seen id(s) from state ({', '.join(sorted(dropped))})")

    def check_board_list(self, old_list, new_list):
        if old_list is not None and list(old_list) != list(new_list):
            self.require_approval(f"change the board list from {old_list} to {new_list}")

    def require_approval(self, action):
        granted = bool(self.approve(action))
        self.decisions.append({"action": action, "approved": granted})
        if not granted:
            raise PolicyViolation(f"not approved: {action}")
