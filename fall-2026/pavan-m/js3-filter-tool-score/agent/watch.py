"""Watch the Glean Greenhouse board: save raw evidence, diff against seen ids, update state atomically."""

import argparse
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from agent.net import make_client
from agent.resume import load_resume

BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/gleanwork/jobs?content=true"
BOARD_SLUG = "gleanwork"


def _save_evidence(evidence_dir: Path, mode: str, raw: str) -> Path:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    path = evidence_dir / f"{stamp}_{mode}_{BOARD_SLUG}.json"
    suffix = 1
    # Never overwrite evidence from an earlier run in the same second.
    while True:
        try:
            with open(path, "x", encoding="utf-8", newline="") as f:
                f.write(raw)
            return path
        except FileExistsError:
            path = evidence_dir / f"{stamp}_{mode}_{BOARD_SLUG}_{suffix}.json"
            suffix += 1


def _load_seen_ids(state_path: Path):
    """Return the set of seen ids, or None if there is no state yet (baseline)."""
    if not state_path.exists():
        return None
    state = json.loads(state_path.read_text())
    seen = state.get("seen_ids") if isinstance(state, dict) else None
    if not isinstance(seen, list) or not all(_usable_id(i) for i in seen):
        raise ValueError(f"state file {state_path} is malformed")
    return set(seen)


def _usable_id(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _write_state_atomic(state_path: Path, seen_ids) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=state_path.parent, prefix=state_path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"seen_ids": sorted(seen_ids)}, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, state_path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def run_watch(state_path, evidence_dir, client=None, seeded_file=None) -> dict:
    state_path = Path(state_path)
    evidence_dir = Path(evidence_dir)

    if seeded_file is not None:
        mode = "seeded"
        raw = Path(seeded_file).read_text(encoding="utf-8")
    else:
        mode = "live"
        if client is None:
            client = make_client()
        response = client.get(BOARD_URL)
        response.raise_for_status()
        raw = response.text

    evidence_file = _save_evidence(evidence_dir, mode, raw)

    seen = _load_seen_ids(state_path)
    jobs = json.loads(raw)["jobs"]
    if not isinstance(jobs, list):
        raise ValueError("response 'jobs' is not a list")

    current_ids = []
    invalid_postings = []
    for index, job in enumerate(jobs):
        job_id = job.get("id") if isinstance(job, dict) else None
        if not _usable_id(job_id):
            invalid_postings.append({"index": index, "id": job_id, "reason": "missing or non-integer id"})
            continue
        if job_id not in current_ids:
            current_ids.append(job_id)

    baseline = seen is None
    new_ids = [] if baseline else [i for i in current_ids if i not in seen]

    _write_state_atomic(state_path, (seen or set()) | set(current_ids))

    return {
        "mode": mode,
        "baseline": baseline,
        "new_ids": new_ids,
        "evidence_file": str(evidence_file),
        "invalid_postings": invalid_postings,
    }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="python -m agent.watch")
    parser.add_argument("--resume", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--seeded")
    args = parser.parse_args(argv)

    # Validate the fictional identity before any network request.
    load_resume(args.resume)
    result = run_watch(args.state, args.evidence, seeded_file=args.seeded)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
