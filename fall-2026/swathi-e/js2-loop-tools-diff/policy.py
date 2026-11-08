"""The permission policy from GATE.md, enforced in code (not in a prompt).

Every request, read and write the agent makes goes through a Policy. A refusal
is always a raised PolicyRefused naming the rule, never a quiet False.

- Hosts: https only, and the hostname must equal one of ALLOWED_HOSTS
  (https is Claude Code's addition, accepted by Swathi on 2026-11-04).
- Reads: only inside the JS2 folder (which holds the persona files).
- Writes: only inside runs/ and state/, after resolving .. and symlinks.
- runs/ is evidence: files are created once, never overwritten.
- state/ may be updated on a normal run; resetting it needs Swathi's
  approval file, which the agent cannot write.
"""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

ALLOWED_HOSTS = ("boards-api.greenhouse.io", "api.ashbyhq.com")
WRITE_DIRS = ("runs", "state")
EVIDENCE_DIR = "runs"
STATE_FILE = Path("state") / "seen_ids.json"
APPROVAL_FILE = Path("approvals") / "reset-state.json"
APPROVAL_KEYS = ("state_sha256", "date", "reason")


class PolicyRefused(Exception):
    def __init__(self, rule, target, reason):
        super().__init__(f"{rule}: {reason}")
        self.rule = rule
        self.target = str(target)


class Policy:
    def __init__(self, root):
        self.root = Path(root).resolve()

    # Hosts

    def _host_refusal(self, url):
        parts = urllib.parse.urlsplit(str(url))
        if parts.scheme != "https":
            return f"{url!r} is not https"
        if parts.hostname not in ALLOWED_HOSTS:
            return f"host {parts.hostname!r} is not on the allow-list {list(ALLOWED_HOSTS)}"
        if parts.port not in (None, 443):
            return f"port {parts.port} is not allowed"
        return None

    def check_host(self, url):
        reason = self._host_refusal(url)
        if reason:
            raise PolicyRefused("host_not_allowed", url, reason)
        return url

    def check_redirect(self, new_url):
        reason = self._host_refusal(new_url)
        if reason:
            raise PolicyRefused("redirect_not_allowed", new_url, f"redirect refused: {reason}")
        return new_url

    def redirect_handler(self):
        policy = self

        class _AllowListRedirects(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                policy.check_redirect(newurl)
                return super().redirect_request(req, fp, code, msg, headers, newurl)

        return _AllowListRedirects()

    # Paths

    def _resolve(self, path):
        path = Path(path)
        return (path if path.is_absolute() else self.root / path).resolve()

    def _strictly_inside(self, path, base):
        return path != base and path.is_relative_to(base)

    def _relative(self, path):
        return path.relative_to(self.root) if path.is_relative_to(self.root) else path

    def check_read(self, path):
        resolved = self._resolve(path)
        if not self._strictly_inside(resolved, self.root):
            raise PolicyRefused("read_outside", path, f"{path} resolves to {resolved}, outside the JS2 folder")
        return resolved

    def check_write(self, path, allowed=WRITE_DIRS):
        resolved = self._resolve(path)
        for name in allowed:
            base = (self.root / name).resolve()
            if self._strictly_inside(base, self.root) and self._strictly_inside(resolved, base):
                return resolved
        raise PolicyRefused("write_outside", path,
                            f"{path} resolves to {resolved}, outside {', '.join(d + '/' for d in allowed)}")

    # Writes

    def write_evidence(self, path, data):
        resolved = self.check_write(path, allowed=(EVIDENCE_DIR,))
        resolved.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(resolved, "xb") as f:
                f.write(data)
        except FileExistsError:
            raise PolicyRefused("overwrite_evidence", path,
                                f"{self._relative(resolved)} already exists; evidence is never overwritten") from None
        return resolved

    def write_state(self, data):
        target = self.check_write(STATE_FILE)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.check_write(target.with_name(f".{target.name}.{os.getpid()}.tmp"))
        with open(temporary, "xb") as f:
            f.write(data)
        os.replace(temporary, target)
        return target

    def reset_state(self):
        state = self.check_write(STATE_FILE)
        approval_path = self.check_read(APPROVAL_FILE)
        if not approval_path.exists():
            current = hashlib.sha256(state.read_bytes()).hexdigest() if state.exists() else None
            raise PolicyRefused("approval_required", APPROVAL_FILE,
                                f"resetting the state needs Swathi's approval: create {APPROVAL_FILE.as_posix()} "
                                f"with state_sha256 {current}, date and reason")
        if not state.exists():
            raise PolicyRefused("approval_invalid", STATE_FILE, "there is no state file to reset")
        try:
            approval = json.loads(approval_path.read_text(encoding="utf-8"))
        except ValueError:
            raise PolicyRefused("approval_invalid", APPROVAL_FILE, "the approval file is not valid JSON") from None
        missing = [k for k in APPROVAL_KEYS if not (isinstance(approval, dict) and str(approval.get(k, "")).strip())]
        if missing:
            raise PolicyRefused("approval_invalid", APPROVAL_FILE, f"the approval file is missing {missing}")
        old = state.read_bytes()
        if approval["state_sha256"] != hashlib.sha256(old).hexdigest():
            raise PolicyRefused("approval_invalid", APPROVAL_FILE,
                                "the approval is for a different state (state_sha256 does not match)")
        stamp = datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S-%f%z")
        saved = self.write_evidence(Path(EVIDENCE_DIR) / f"state_before_reset_{stamp}.json", old)
        state.unlink()
        return saved
