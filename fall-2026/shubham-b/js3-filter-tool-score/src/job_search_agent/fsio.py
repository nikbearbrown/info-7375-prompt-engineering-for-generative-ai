"""File policy: the write root (``OutputRoot``) and the read roots (``ReadPolicy``).

CONTRACT §12 forbids writing outside the configured data directory. ``OutputRoot``
enforces that for every write the agent makes:

* A write path (``rel``) is a relative POSIX string in canonical form. Absolute
  paths, ``~``, ``..``, NUL bytes, backslashes, empty or ``.`` components are
  rejected before the filesystem is touched.
* The path is then walked one component at a time with directory file descriptors
  opened ``O_NOFOLLOW``, so a symlink anywhere below the root (including one that
  appears after a check) is refused rather than followed. Containment is decided by
  path components, never by string prefix, so ``data-evil`` is not inside ``data``.
* Writes are atomic: a temporary file in the same directory is written and fsynced,
  moved over the target with ``os.replace``, then the directory is fsynced. A
  failure at any step leaves the previous file intact and removes the temporary.

Permissions: every file the agent writes under the data root is created ``0o600``
and every directory it creates ``0o700`` (before the umask), so state files and raw
model replies are private to the owner. Applying this to all of ``data/`` is simpler
than per-file modes and safe: only this user's ``jsa`` and ``claude`` processes read
these files, and git records only the executable bit, not read permissions.

``OutputRoot.lock`` takes an exclusive, non-blocking ``flock`` on a lock file (the
pipeline uses ``data/<live|seeded>/.lock``). Lock files are empty, git-ignored
(``data/*/.lock``) and are not evidence: nothing reads their contents.

``ReadPolicy`` limits reads to the project's input and output roots (persona/,
evidence/, data/, prompts/, config/, experiments/) after resolving symlinks.

Every rejection raises ``PathRejected`` whose message holds a reason code only.
"""

from __future__ import annotations

import contextlib
import fcntl
import json
import os
import secrets
import stat
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path, PurePosixPath
from typing import Any, Final

from pydantic import BaseModel

from job_search_agent.errors import PathRejected, RunLocked

DEFAULT_READ_ROOTS: Final = (
    "persona",
    "evidence",
    "data",
    "prompts",
    "config",
    "experiments",
)
"""Top-level project directories the agent may read (PLAN §1.2)."""

_DIR_FLAGS: Final = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
_TMP_PREFIX: Final = ".tmp-"
_FILE_MODE: Final = 0o600
"""Every file under the data root is owner-only (state, raw replies, reports)."""
_DIR_MODE: Final = 0o700
"""Every directory ``OutputRoot`` creates is owner-only."""


def is_within(child: Path, parent: Path) -> bool:
    """Returns True if ``child`` is ``parent`` or below it, by path components.

    Both paths should already be absolute and resolved. ``/x/data-evil`` is not
    within ``/x/data`` even though the strings share a prefix.

    Args:
        child: Candidate path.
        parent: Containing directory.

    Returns:
        Whether ``child`` lies inside ``parent``.
    """
    return child == parent or child.is_relative_to(parent)


def relative_within(
    path: Path | str,
    root: Path,
    *,
    follow_symlinks: bool = True,
    allow_root: bool = False,
) -> str:
    """Returns ``path`` relative to ``root`` (POSIX), or refuses it.

    This is the single containment check of the project: the résumé gate, the CLI's
    path arguments, ``ReadPolicy`` and the configuration's path validation all call
    it (review fix 4), so "inside" means the same thing everywhere.

    Args:
        path: Absolute, or relative to ``root``.
        root: The containing directory; resolved before comparing.
        follow_symlinks: Resolve symlinks in ``path`` (``Path.resolve``) before
            comparing. ``False`` normalises ``..`` lexically instead, for paths that
            ``OutputRoot`` will then open without following symlinks.
        allow_root: Accept ``path == root`` (returned as ``"."``).

    Returns:
        The relative POSIX path, e.g. ``"evidence/handcheck/x.json"``.

    Raises:
        PathRejected: ``"nul"`` for a NUL byte, ``"outside_root"`` when ``path`` is
            not inside ``root`` (by components, never by string prefix).
    """
    text = os.fspath(path)
    if "\x00" in text:
        raise PathRejected("nul", text)
    base = Path(root).resolve()
    candidate = Path(text)
    if not candidate.is_absolute():
        candidate = base / candidate
    target = (
        candidate.resolve() if follow_symlinks else Path(os.path.normpath(candidate))
    )
    if not is_within(target, base) or (target == base and not allow_root):
        raise PathRejected("outside_root", text)
    return target.relative_to(base).as_posix()


def split_rel(rel: str) -> tuple[str, ...]:
    """Validates a write path and returns its components.

    Args:
        rel: Path relative to the output root, e.g. ``"live/runs/x/report.json"``.

    Returns:
        The non-empty components.

    Raises:
        PathRejected: ``"type"``, ``"empty"``, ``"nul"``, ``"backslash"``,
            ``"absolute"``, ``"dotdot"`` or ``"not_canonical"``.
    """
    if not isinstance(rel, str):
        raise PathRejected("type", repr(rel))
    if not rel:
        raise PathRejected("empty", rel)
    if "\x00" in rel:
        raise PathRejected("nul", rel)
    if "\\" in rel:
        raise PathRejected("backslash", rel)
    if rel.startswith(("/", "~")) or (rel[:1].isalpha() and rel[1:2] == ":"):
        raise PathRejected("absolute", rel)
    raw_parts = rel.split("/")
    if ".." in raw_parts:
        raise PathRejected("dotdot", rel)
    if any(part in ("", ".") for part in raw_parts) or str(PurePosixPath(rel)) != rel:
        raise PathRejected("not_canonical", rel)
    return tuple(raw_parts)


def _encode_json(obj: Any, *, sort_keys: bool, indent: int | None) -> str:  # noqa: ANN401
    """Serialises ``obj`` (pydantic models via ``model_dump(mode="json")``)."""
    if isinstance(obj, BaseModel):
        obj = obj.model_dump(mode="json")
    separators = (",", ": ") if indent is not None else (",", ":")
    return json.dumps(
        obj,
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=False,
        allow_nan=False,
        separators=separators,
    )


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(fd, view)
        view = view[written:]


class OutputRoot:
    """The single directory the agent writes to (CONTRACT §3, §12).

    Args:
        root: An existing directory. It is resolved once; everything below it is
            walked without following symlinks.

    Raises:
        PathRejected: ``"root_missing"`` if ``root`` is not an existing directory.
    """

    def __init__(self, root: Path) -> None:
        resolved = Path(root).resolve()
        if not resolved.is_dir():
            raise PathRejected("root_missing", str(root))
        self._root = resolved

    @property
    def root(self) -> Path:
        """The resolved absolute root (for opening files only; never write it out)."""
        return self._root

    def __repr__(self) -> str:
        """Returns a representation without the absolute root path."""
        return f"OutputRoot(<{self._root.name}>)"

    # --- directory walking -------------------------------------------------

    @contextlib.contextmanager
    def _parent_fd(self, parts: Sequence[str], *, create: bool) -> Iterator[int]:
        """Yields an fd for the directory holding ``parts[-1]``.

        Raises:
            PathRejected: ``"symlink"`` or ``"not_dir"`` on a bad component.
            FileNotFoundError: If a directory is missing and ``create`` is False.
        """
        fd = os.open(self._root, _DIR_FLAGS)
        try:
            for part in parts[:-1]:
                if create:
                    with contextlib.suppress(FileExistsError):
                        os.mkdir(part, _DIR_MODE, dir_fd=fd)
                next_fd = self._open_child_dir(fd, part, "/".join(parts))
                os.close(fd)
                fd = next_fd
            self._check_leaf(fd, parts[-1], "/".join(parts))
            yield fd
        finally:
            os.close(fd)

    @staticmethod
    def _open_child_dir(fd: int, part: str, rel: str) -> int:
        info = os.stat(part, dir_fd=fd, follow_symlinks=False)
        if stat.S_ISLNK(info.st_mode):
            raise PathRejected("symlink", rel)
        if not stat.S_ISDIR(info.st_mode):
            raise PathRejected("not_dir", rel)
        try:
            return os.open(part, _DIR_FLAGS, dir_fd=fd)
        except OSError as exc:  # raced into a symlink or non-directory
            raise PathRejected("symlink", rel) from exc

    @staticmethod
    def _leaf_mode(fd: int, name: str) -> int | None:
        try:
            return os.stat(name, dir_fd=fd, follow_symlinks=False).st_mode
        except FileNotFoundError:
            return None

    def _check_leaf(self, fd: int, name: str, rel: str) -> None:
        mode = self._leaf_mode(fd, name)
        if mode is not None and stat.S_ISLNK(mode):
            raise PathRejected("symlink", rel)

    # --- public API ----------------------------------------------------------

    def resolve_for_write(self, rel: str) -> Path:
        """Validates ``rel`` and returns the absolute path it names.

        Existing components must be real directories (no symlinks); missing ones
        are allowed and created by the write methods.

        Args:
            rel: Path relative to the root.

        Returns:
            ``root / rel``.

        Raises:
            PathRejected: On any policy violation.
        """
        parts = split_rel(rel)
        fd = os.open(self._root, _DIR_FLAGS)
        try:
            for index, part in enumerate(parts):
                mode = self._leaf_mode(fd, part)
                if mode is None:
                    break
                if stat.S_ISLNK(mode):
                    raise PathRejected("symlink", rel)
                if index < len(parts) - 1:
                    next_fd = self._open_child_dir(fd, part, rel)
                    os.close(fd)
                    fd = next_fd
        finally:
            os.close(fd)
        target = self._root.joinpath(*parts)
        if not is_within(target, self._root):  # defence in depth
            raise PathRejected("outside_root", rel)
        return target

    def write_bytes_atomic(self, rel: str, data: bytes) -> Path:
        """Atomically replaces ``rel`` with ``data``, creating parent directories.

        Args:
            rel: Path relative to the root.
            data: The complete new contents.

        Returns:
            The absolute path written.

        Raises:
            PathRejected: On any policy violation, or ``"is_dir"`` if the target is
                a directory.
            OSError: If the filesystem fails; the previous file is left intact.
        """
        parts = split_rel(rel)
        with self._parent_fd(parts, create=True) as dir_fd:
            name = parts[-1]
            mode = self._leaf_mode(dir_fd, name)
            if mode is not None and stat.S_ISDIR(mode):
                raise PathRejected("is_dir", rel)
            tmp = f"{_TMP_PREFIX}{name}.{secrets.token_hex(6)}"
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
            fd = os.open(tmp, flags, _FILE_MODE, dir_fd=dir_fd)
            try:
                try:
                    _write_all(fd, data)
                    os.fsync(fd)
                finally:
                    os.close(fd)
                os.replace(tmp, name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
            except BaseException:
                with contextlib.suppress(OSError):
                    os.unlink(tmp, dir_fd=dir_fd)
                raise
            os.fsync(dir_fd)
        return self._root.joinpath(*parts)

    def write_json_atomic(
        self,
        rel: str,
        obj: Any,  # noqa: ANN401 - any JSON-serialisable value or pydantic model
        *,
        sort_keys: bool = True,
    ) -> Path:
        """Atomically writes ``obj`` as UTF-8 JSON (indent 2, trailing newline).

        Args:
            rel: Path relative to the root.
            obj: A JSON-serialisable value or a pydantic model.
            sort_keys: Sort object keys. Pass False to keep insertion order, e.g. for
                §7 records whose key order is part of the contract.

        Returns:
            The absolute path written.

        Raises:
            PathRejected: On any policy violation.
            ValueError: If ``obj`` holds NaN or infinity.
            TypeError: If ``obj`` is not JSON-serialisable.
        """
        text = _encode_json(obj, sort_keys=sort_keys, indent=2) + "\n"
        return self.write_bytes_atomic(rel, text.encode("utf-8"))

    def append_jsonl(
        self,
        rel: str,
        obj: Any,  # noqa: ANN401 - any JSON-serialisable value or pydantic model
        *,
        sort_keys: bool = True,
    ) -> Path:
        """Appends ``obj`` as one compact JSON line and fsyncs the file.

        Args:
            rel: Path relative to the root; created if missing.
            obj: A JSON-serialisable value or a pydantic model.
            sort_keys: Sort object keys.

        Returns:
            The absolute path appended to.

        Raises:
            PathRejected: On any policy violation.
        """
        line = (_encode_json(obj, sort_keys=sort_keys, indent=None) + "\n").encode()
        parts = split_rel(rel)
        with self._parent_fd(parts, create=True) as dir_fd:
            flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW
            try:
                fd = os.open(parts[-1], flags, _FILE_MODE, dir_fd=dir_fd)
            except IsADirectoryError as exc:
                raise PathRejected("is_dir", rel) from exc
            try:
                _write_all(fd, line)
                os.fsync(fd)
            finally:
                os.close(fd)
        return self._root.joinpath(*parts)

    def make_empty_dir(self, rel: str) -> Path:
        """Creates ``rel`` (and parents) and checks that it is empty.

        Used for the per-call empty working directory of the ``claude`` CLI (A32).

        Args:
            rel: Path relative to the root, e.g. ``"tmp/judge-<id>"``.

        Returns:
            The absolute directory path.

        Raises:
            PathRejected: On any policy violation, ``"not_dir"`` if a file is in the
                way, or ``"not_empty"`` if the directory already has entries.
        """
        parts = split_rel(rel)
        with self._parent_fd(parts, create=True) as dir_fd:
            with contextlib.suppress(FileExistsError):
                os.mkdir(parts[-1], _DIR_MODE, dir_fd=dir_fd)
            leaf_fd = self._open_child_dir(dir_fd, parts[-1], rel)
            try:
                if os.listdir(leaf_fd):
                    raise PathRejected("not_empty", rel)
            finally:
                os.close(leaf_fd)
        return self._root.joinpath(*parts)

    def read_bytes(self, rel: str) -> bytes:
        """Reads ``rel`` under the same no-symlink policy as writes.

        Args:
            rel: Path relative to the root.

        Returns:
            The file contents.

        Raises:
            PathRejected: On any policy violation.
            FileNotFoundError: If the file or a parent directory does not exist.
        """
        parts = split_rel(rel)
        with self._parent_fd(parts, create=False) as dir_fd:
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dir_fd)
            try:
                with os.fdopen(fd, "rb", closefd=False) as handle:
                    return handle.read()
            finally:
                os.close(fd)

    @contextlib.contextmanager
    def lock(self, rel: str) -> Iterator[None]:
        """Holds an exclusive, non-blocking ``flock`` on ``rel`` for the ``with`` body.

        The lock file is created (empty, owner-only) if missing and left in place;
        the lock is released when the file descriptor is closed, including when the
        process dies, so a crash never leaves a stale lock.

        Args:
            rel: Path relative to the root, e.g. ``"live/.lock"``.

        Yields:
            Nothing; the lock is held until the block exits.

        Raises:
            RunLocked: Another open file description holds the lock.
            PathRejected: On any policy violation (a symlinked lock file included).
        """
        parts = split_rel(rel)
        with self._parent_fd(parts, create=True) as dir_fd:
            flags = os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW
            try:
                fd = os.open(parts[-1], flags, _FILE_MODE, dir_fd=dir_fd)
            except IsADirectoryError as exc:
                raise PathRejected("is_dir", rel) from exc
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RunLocked(rel) from exc
            yield
        finally:
            os.close(fd)

    def exists(self, rel: str) -> bool:
        """Returns True if ``rel`` exists (as anything but a symlink).

        Raises:
            PathRejected: On any policy violation, including a symlink.
        """
        parts = split_rel(rel)
        try:
            with self._parent_fd(parts, create=False) as dir_fd:
                return self._leaf_mode(dir_fd, parts[-1]) is not None
        except FileNotFoundError:
            return False


def create_output_root(root: Path) -> OutputRoot:
    """Creates the data directory if it is absent and returns its ``OutputRoot``.

    Args:
        root: The configured data directory.

    Returns:
        The output root.

    Raises:
        OSError: If the directory cannot be created.
    """
    Path(root).mkdir(parents=True, exist_ok=True)
    return OutputRoot(root)


class ReadPolicy:
    """Allowed read roots inside the project (PLAN §1.2).

    Args:
        project_root: The repository root.
        roots: Top-level directory names that may be read.

    Raises:
        PathRejected: ``"root_missing"`` if ``project_root`` is not a directory.
    """

    def __init__(
        self, project_root: Path, roots: Iterable[str] = DEFAULT_READ_ROOTS
    ) -> None:
        resolved = Path(project_root).resolve()
        if not resolved.is_dir():
            raise PathRejected("root_missing", str(project_root))
        self._project_root = resolved
        self._roots = tuple(resolved / split_rel(name)[0] for name in roots)

    def check(self, path: Path | str) -> Path:
        """Resolves ``path`` (following symlinks) and checks it is readable.

        Args:
            path: Absolute, or relative to the project root.

        Returns:
            The resolved absolute path.

        Raises:
            PathRejected: ``"nul"`` or ``"outside_read_roots"``.
        """
        text = os.fspath(path)
        try:
            rel = relative_within(text, self._project_root)
        except PathRejected as exc:
            if exc.reason == "nul":
                raise
            raise PathRejected("outside_read_roots", text) from None
        resolved = self._project_root / rel
        if any(is_within(resolved, root) for root in self._roots):
            return resolved
        raise PathRejected("outside_read_roots", text)

    def read_bytes(self, path: Path | str) -> bytes:
        """Checks ``path`` and returns its contents.

        Raises:
            PathRejected: If the path is outside the read roots.
            OSError: If the file cannot be read.
        """
        return self.check(path).read_bytes()

    def repo_rel(self, path: Path | str) -> str:
        """Returns the checked path relative to the project root (POSIX).

        Raises:
            PathRejected: If the path is outside the read roots.
        """
        return self.check(path).relative_to(self._project_root).as_posix()
