"""The agent's file tool. Every operation asks the permission policy first and uses the
path the policy returns, so a refused operation raises PolicyDenied before anything
touches the disk (GATE.md wrong versions 5 and 6)."""

import os
import secrets
from pathlib import PurePosixPath


class Files:
    def __init__(self, policy):
        self.policy = policy

    def exists(self, path):
        return self.policy.check_file("read", path).exists()

    def read_bytes(self, path):
        return self.policy.check_file("read", path).read_bytes()

    def mkdir(self, path):
        """Create a folder and any missing parents, each checked as a write."""
        rel = PurePosixPath(path)
        for depth in range(1, len(rel.parts) + 1):
            folder = PurePosixPath(*rel.parts[:depth]).as_posix()
            target = self.policy.check_file("write", folder)
            target.mkdir(exist_ok=True)

    def write_bytes(self, path, data):
        target = self.policy.check_file("write", path)
        parent = PurePosixPath(path).parent
        if str(parent) != ".":
            self.mkdir(parent.as_posix())
        target.write_bytes(data)

    def write_atomic(self, path, data):
        """Write a temporary file next to the target, flush it to disk, then rename it
        over the target, so a reader sees the old file or the new one, never half."""
        target = self.policy.check_file("write", path)
        parent = PurePosixPath(path).parent
        if str(parent) != ".":
            self.mkdir(parent.as_posix())
        temp_rel = (parent / f".{target.name}.{secrets.token_hex(6)}.tmp").as_posix()
        temp = self.policy.check_file("write", temp_rel)
        try:
            with open(temp, "xb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, target)
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
