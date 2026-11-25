"""Evidence files under evidence/: CONTRACT.md Out (Files written by each run, run_id, manifest), Amendment A8."""
import hashlib
import json
import os
import tempfile
from datetime import timezone
from pathlib import Path

EVIDENCE = Path("evidence")
RAW_DIR = EVIDENCE / "raw"
RUNS_DIR = EVIDENCE / "runs"
SAMPLING_DIR = EVIDENCE / "sampling"
EXPERIMENTS_DIR = EVIDENCE / "experiments"


def as_utc(dt):
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def utc_iso(dt):
    return as_utc(dt).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    """Write bytes to a temp file in the same directory, then rename over `path`."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def json_bytes(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def utc_stamp(now):
    return as_utc(now).strftime("%Y%m%dT%H%M%SZ")


def new_run_id(now, token):
    """YYYYMMDDTHHMMSSZ_<token>, with -2, -3 ... appended on a collision."""
    base = utc_stamp(now) + "_" + token
    run_id, n = base, 1
    while (RUNS_DIR / run_id).exists() or (RAW_DIR / f"{run_id}.raw").exists():
        n += 1
        run_id = f"{base}-{n}"
    return run_id


def new_stamp_dir(parent, now):
    """parent/YYYYMMDDTHHMMSSZ, with -2, -3 ... appended on a collision (Amendment A8)."""
    base = Path(parent) / utc_stamp(now)
    path, n = base, 1
    while path.exists():
        n += 1
        path = base.with_name(f"{base.name}-{n}")
    return path


class OutDir:
    """An evidence directory: new, unless exist_ok (a resumed experiment, Amendment A14)."""

    def __init__(self, path, exist_ok=False):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=exist_ok)

    def write(self, name, data):
        path = self.path / name
        atomic_write(path, data if isinstance(data, bytes) else data.encode("utf-8"))
        return path.as_posix()

    def write_json(self, name, obj):
        return self.write(name, json_bytes(obj))


class RunDir(OutDir):
    def __init__(self, run_id):
        self.run_id = run_id
        super().__init__(RUNS_DIR / run_id)

    def write_raw(self, body):
        """Body bytes exactly as received; returns the path written, as a POSIX string."""
        path = RAW_DIR / f"{self.run_id}.raw"
        atomic_write(path, body)
        return path.as_posix()
