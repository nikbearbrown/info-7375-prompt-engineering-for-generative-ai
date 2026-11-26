"""GATE §6: the permission policy. Every fetch, read and write the agent makes is checked here, in code."""
import os
import urllib.parse

NEVER_TOOLS = {"apply", "send_email", "send_message", "login"}
TOOLS = {"fetch", "read", "write"}


class Refused(PermissionError):
    pass


class NeedsApproval(Refused):
    pass


def _inside(path, folder):
    """Compare whole path parts of the REAL paths, so runs-evil/ is not inside runs/ (W3) and
    runs/../x or a symlink pointing out of runs/ is judged by where it really lands."""
    p, f = os.path.realpath(path), os.path.realpath(folder)
    try:
        return os.path.commonpath([os.path.normcase(p), os.path.normcase(f)]) == os.path.normcase(f)
    except ValueError:          # different drives on Windows
        return False


class Policy:
    def __init__(self, root, hosts, write_dir="runs", approvals=()):
        self.root = os.path.realpath(root)
        self.hosts = {h.lower() for h in hosts}
        self.write_root = os.path.join(self.root, write_dir)
        self.approvals = set(approvals)

    def check_tool(self, name):
        if name in NEVER_TOOLS or name not in TOOLS:
            raise Refused(f"refused: tool '{name}' does not exist for this agent (GATE §6 never-list)")

    def check_fetch(self, url, method="GET"):
        u = urllib.parse.urlsplit(url)
        if method != "GET":
            raise Refused(f"refused: {method} {url} (GET only)")
        if u.scheme != "https":
            raise Refused(f"refused: {url} (https only)")
        if (u.hostname or "").lower() not in self.hosts:
            raise Refused(f"refused: host {u.hostname} is not on the allow-list")

    def check_read(self, path):
        if not _inside(path, self.root):
            raise Refused(f"refused: read {path} is outside the project folder")
        return os.path.realpath(path)

    def check_write(self, path, action="create", approval_key=None):
        if not _inside(path, self.write_root):
            raise Refused(f"refused: write {path} is outside runs/")
        if action in ("reset-state", "replace-evidence"):
            if not approval_key or approval_key not in self.approvals:
                raise NeedsApproval(f"needs approval: {action} needs --approve {approval_key}")
        elif action != "create":
            raise Refused(f"refused: unknown write action {action}")
        return os.path.realpath(path)
