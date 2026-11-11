"""The only module that writes files. Every write is decided by policy.Policy.check_write() first.

- write_new():  evidence (raw responses, reports). O_EXCL | O_NOFOLLOW: never overwrites, never
                follows a symlink planted at the final path after the check.
- append():     only to a file this Store created in this run (the trace).
- write_state(): the per-board state file, via a temp file + os.replace.
Every decision (ALLOW or not) is passed to `on_decision` so the loop can put it in the trace.
"""
import json
import os

from . import policy

_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)


class Store:
    def __init__(self, pol, on_decision=None):
        self.policy = pol
        self.on_decision = on_decision or (lambda d: None)
        self.created = set()

    def _check(self, path):
        d = self.policy.check_write(path)
        self.on_decision(d)
        if d["decision"] != policy.ALLOW:
            raise policy.PolicyDenied(d)
        return d

    def makedirs(self, path):
        if os.path.isdir(path):
            # an existing dir is only usable if its real path is inside runs/
            d = self.policy.check_write(os.path.join(path, ".probe-not-written"))
            if d["decision"] != policy.ALLOW:
                self.on_decision(d)
                raise policy.PolicyDenied(d)
            return
        self._check(path)
        os.makedirs(path)

    def write_new(self, path, data):
        self._check(path)
        if isinstance(data, str):
            data = data.encode("utf-8")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW, 0o644)
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        self.created.add(os.path.realpath(path))
        return path

    def append(self, path, line):
        if os.path.realpath(path) not in self.created:
            self.write_new(path, line)
            return
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | _NOFOLLOW)
        with os.fdopen(fd, "a", encoding="utf-8") as f:
            f.write(line)

    def write_state(self, path, obj):
        tmp = path + ".tmp"
        if os.path.lexists(tmp):
            raise policy.PolicyDenied(policy._d("write", tmp, policy.DENY, "stale temp state file present"))
        self.write_new(tmp, json.dumps(obj, indent=1, sort_keys=True))
        self.created.discard(os.path.realpath(tmp))
        self._check(path)
        os.replace(tmp, path)
