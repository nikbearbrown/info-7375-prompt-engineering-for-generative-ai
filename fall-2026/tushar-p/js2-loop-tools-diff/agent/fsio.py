"""Gated local reads and writes (GATE.md "Local reads", "Local writes", "Protected write";
F16, F18, F19).

Reads: the selected board config, <root>/state.json, and, in offline mode, the selected
fixture's exact resolved path. Every other read is refused before any file is opened.

Writes: only inside the resolved output root, through a temp file in the destination's
folder, then os.replace. The root itself must not be a symlink; its real path is resolved
once at startup, so aliases in its ancestors (/var -> /private/var) work. Any symlink in a
managed path below the root is refused, even one whose target stays inside the root.
<root>/protected/shortlist.json needs an Approval for that destination, those exact bytes,
and this run.
"""

import hmac
import os
import secrets
import stat
from pathlib import Path

from . import PROJECT_DIR
from .approval import PROTECTED_DIR, SHORTLIST_NAME, Approval, sha256_hex
from .errors import ReadDenied, WriteDenied

DEFAULT_ROOT = PROJECT_DIR / "out"
STATE_NAME = "state.json"

_O_CLOEXEC = getattr(os, "O_CLOEXEC", 0)
_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)


class FileGate:
    """The only way the agent touches local files. One gate per run."""

    def __init__(self, root, run_id: str, *, config_path=None, fixture_path=None):
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")
        root_given = Path(os.path.abspath(root))
        if os.path.islink(root_given):
            raise WriteDenied(f"output root {root_given} is a symlink")
        root_given.mkdir(parents=True, exist_ok=True)
        if os.path.islink(root_given) or not root_given.is_dir():
            raise WriteDenied(f"output root {root_given} is not a real directory")
        self.root_given = root_given
        self.root = Path(os.path.realpath(root_given))  # resolved once (F19)
        self.run_id = run_id
        self._read_grants = set()
        if config_path is not None:
            self._read_grants.add(os.path.realpath(config_path))
        if fixture_path is not None:  # F18: offline mode grants this exact resolved path only
            self._read_grants.add(os.path.realpath(fixture_path))

    @property
    def state_path(self) -> Path:
        return self.root / STATE_NAME

    # ---------- paths ----------

    def _relative_parts(self, path, error) -> tuple[str, ...] | None:
        """Parts of path below the root, None if it is outside, or raise on '..'."""
        p = Path(path)
        if ".." in p.parts:
            raise error(f"refused {str(path)!r}: '..' is not allowed in a managed path")
        if not p.is_absolute():
            p = Path.cwd() / p
        for base in (self.root, self.root_given):
            try:
                rel = p.relative_to(base)
            except ValueError:
                continue
            return rel.parts
        return None

    def _check_components(self, parts: tuple[str, ...], error) -> None:
        """Refuse a symlink anywhere below the root, a non-directory on the way, or a
        non-regular file at the end. Missing components are fine (they get created)."""
        current = self.root
        for i, name in enumerate(parts):
            current = current / name
            try:
                st = os.lstat(current)
            except FileNotFoundError:
                return
            except OSError as err:
                raise error(f"refused {current}: {err}") from None
            if stat.S_ISLNK(st.st_mode):
                raise error(f"refused {current}: symlinks are not allowed below the output root")
            last = i == len(parts) - 1
            if not last and not stat.S_ISDIR(st.st_mode):
                raise error(f"refused {current}: not a directory")
            if last and not stat.S_ISREG(st.st_mode):
                raise error(f"refused {current}: not a regular file")

    # ---------- reads ----------

    def read(self, path) -> bytes:
        """Bytes of an allowed file. Denials happen before any open()."""
        absolute = os.path.abspath(path)
        parts = self._relative_parts(absolute, ReadDenied)
        if parts is not None:
            # Inside the output root the agent may read only state.json, never through a symlink.
            if parts != (STATE_NAME,):
                raise ReadDenied(f"refused read of {path!s}: only {STATE_NAME} may be read from the output root")
            self._check_components(parts, ReadDenied)
            target = str(self.state_path)
        else:
            target = os.path.realpath(absolute)
            if target not in self._read_grants:
                raise ReadDenied(f"refused read of {path!s}: not the selected config, state, or fixture")
        try:
            fd = os.open(target, os.O_RDONLY | _O_NOFOLLOW | _O_CLOEXEC)
        except OSError as err:
            raise ReadDenied(f"cannot open {target}: {err}") from None
        with os.fdopen(fd, "rb") as handle:
            return handle.read()

    # ---------- writes ----------

    def _check_protected(self, parts, data: bytes, approval) -> None:
        # Compare case-insensitively: macOS volumes are usually case-insensitive, so
        # "Protected/Shortlist.json" would land on the protected file.
        if len(parts) != 2 or parts[1].casefold() != SHORTLIST_NAME.casefold():
            raise WriteDenied(f"refused write under {PROTECTED_DIR}/: only {SHORTLIST_NAME} is writable, with approval")
        if approval is None:
            raise WriteDenied(f"refused write to {PROTECTED_DIR}/{SHORTLIST_NAME}: no approval")
        if not isinstance(approval, Approval):
            raise WriteDenied("refused protected write: approval is not an Approval")
        if approval.run_id != self.run_id:
            raise WriteDenied("refused protected write: approval belongs to a different run")
        approved_parts = self._relative_parts(approval.dest, WriteDenied)
        if approved_parts is None:
            raise WriteDenied("refused protected write: approval destination is outside the output root")
        if approved_parts != parts:
            raise WriteDenied("refused protected write: approval is for a different destination")
        if not hmac.compare_digest(approval.sha256, sha256_hex(data)):
            raise WriteDenied("refused protected write: bytes differ from the approved bytes")

    def write(self, path, data: bytes, *, approval: Approval | None = None) -> Path:
        """Write exact bytes to a managed path below the root. Returns the real destination."""
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        parts = self._relative_parts(path, WriteDenied)
        if parts is None:
            raise WriteDenied(f"refused write to {str(path)!r}: outside the output root {self.root}")
        if not parts:
            raise WriteDenied("refused write to the output root itself")
        self._check_components(parts, WriteDenied)
        if parts[0].casefold() == PROTECTED_DIR.casefold():
            self._check_protected(parts, data, approval)

        # Every check passed; now create missing folders one at a time, re-checking each.
        parent = self.root
        for name in parts[:-1]:
            parent = parent / name
            try:
                os.mkdir(parent, 0o755)
            except FileExistsError:
                pass
            st = os.lstat(parent)
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
                raise WriteDenied(f"refused {parent}: not a real directory")
        if os.path.realpath(parent) != str(parent):
            raise WriteDenied(f"refused {parent}: resolves outside the expected location")

        dest = parent / parts[-1]
        tmp = parent / f".{parts[-1]}.{secrets.token_hex(8)}.tmp"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | _O_NOFOLLOW | _O_CLOEXEC, 0o644)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if os.path.islink(dest):
                raise WriteDenied(f"refused {dest}: became a symlink")
            os.replace(tmp, dest)
        except BaseException:
            try:
                os.unlink(tmp)
            except FileNotFoundError:
                pass
            raise
        return dest
