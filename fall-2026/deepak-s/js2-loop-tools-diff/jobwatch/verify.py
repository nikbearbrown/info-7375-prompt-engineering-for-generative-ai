"""`python -m jobwatch verify runs/<run-id>`: the independent check, GATE.md section 7.

Imports only the Python standard library, and no jobwatch module. Reads files with
open(path, "rb") only, and only under runs/, after its own realpath + commonpath check.
Lists directories under runs/ to find the prior run. Never writes, never uses the network,
prints its report to stdout.

Counts postings on its own. The location of each system's postings array was taken from the
bodies in evidence/manual-capture/20261110T184001Z/:
    greenhouse  {"jobs": [...]}       (01-greenhouse-stripe.body)
    lever       [...] at the top      (04-lever-eu-lever.body, 05-lever-us-palantir.body)
    ashby       {"jobs": [...]}       (06-ashby-linear.body, 07-ashby-notion.body)

Exit 0 when nothing is flagged, 2 when anything is flagged.
"""
import hashlib
import json
import os
import sys

CLEAN, FLAGGED = 0, 2


class Unreadable(Exception):
    pass


def _runs_root(root):
    return os.path.realpath(os.path.join(root, "runs"))


def _contained(path, root):
    """realpath + commonpath containment under runs/ (GATE.md section 7, Reads)."""
    real = os.path.realpath(path)
    base = _runs_root(root)
    try:
        inside = os.path.commonpath([real, base]) == base
    except ValueError:
        inside = False
    if not inside:
        raise Unreadable(f"{path} is outside runs/")
    return real


def _read(path, root):
    real = _contained(path, root)
    try:
        with open(real, "rb") as f:
            return f.read()
    except OSError as e:
        raise Unreadable(f"cannot read {path}: {type(e).__name__}") from None


def _read_json(path, root):
    data = _read(path, root)
    try:
        return json.loads(data)
    except ValueError:
        raise Unreadable(f"{path} is not JSON") from None


def count_postings(system, data):
    """verify's own count: the length of the postings array for each system, or None."""
    if system == "lever":
        return len(data) if isinstance(data, list) else None
    if system in ("greenhouse", "ashby"):
        jobs = data.get("jobs") if isinstance(data, dict) else None
        return len(jobs) if isinstance(jobs, list) else None
    return None


def _final_file(manifest, key):
    files = [f for f in manifest.get("files", []) if f.get("board") == key]
    return max(files, key=lambda f: f.get("attempt", 0)) if files else None


def _recount(run_dir, manifest, key, system, root):
    """(count, problem) from the run's final raw body for this board."""
    entry = _final_file(manifest, key)
    if entry is None:
        return None, "no raw body in the manifest"
    body = _read(os.path.join(run_dir, entry["path"]), root)
    try:
        data = json.loads(body)
    except ValueError:
        return None, "raw body is not JSON"
    n = count_postings(system, data)
    return n, None if n is not None else "no postings array where expected"


def suspect_check(prior_count, count):
    """SUSPECT: more than 0 in the prior run and 0 now (W11)."""
    return prior_count is not None and prior_count > 0 and count == 0


def prior_ok_run(run_dir, system, slug, root):
    """The latest earlier runs/<id>/ where the same (system, slug) ended OK: (run_id, count) or None."""
    runs = _runs_root(root)
    this = os.path.basename(os.path.realpath(run_dir))
    earlier = sorted((d for d in os.listdir(runs) if d < this and os.path.isdir(os.path.join(runs, d))),
                     reverse=True)
    for name in earlier:
        d = os.path.join(runs, name)
        try:
            summary = _read_json(os.path.join(d, "summary.json"), root)
            manifest = _read_json(os.path.join(d, "manifest.json"), root)
        except Unreadable:
            continue
        for b in summary.get("boards", []):
            if b.get("system") == system and b.get("slug") == slug and b.get("status") == "OK":
                n, _ = _recount(d, manifest, f"{system}:{slug}", system, root)
                return name, n
    return None


def verify(run_dir, root="."):
    """Return (flags, lines). Each flag is (FLAG, board, message)."""
    flags, lines = [], []
    try:
        summary = _read_json(os.path.join(run_dir, "summary.json"), root)
        manifest = _read_json(os.path.join(run_dir, "manifest.json"), root)
    except Unreadable as e:
        return [("INVALID", None, str(e))], [f"INVALID  {e}"]

    for entry in manifest.get("files", []):
        try:
            body = _read(os.path.join(run_dir, entry["path"]), root)
        except Unreadable as e:
            flags.append(("MISMATCH", entry.get("board"), str(e)))
            continue
        if hashlib.sha256(body).hexdigest() != entry.get("sha256"):
            flags.append(("MISMATCH", entry.get("board"), f"sha256 of {entry['path']} differs from manifest.json"))
        try:
            json.loads(body)
        except ValueError:
            flags.append(("INVALID", entry.get("board"), f"{entry['path']} is not JSON"))

    for b in summary.get("boards", []):
        key, system, slug = b.get("key"), b.get("system"), b.get("slug")
        if b.get("status") != "OK":
            if b.get("count") is not None or b.get("new_ids") is not None:
                flags.append(("MISMATCH", key, f"board is {b.get('status')} but summary.json reports a count"))
            lines.append(f"{'':9}{key}: {b.get('status')} ({b.get('reason')}), not counted")
            continue
        n, problem = _recount(run_dir, manifest, key, system, root)
        if problem:
            flags.append(("MISMATCH", key, problem))
            continue
        if n != b.get("count"):
            flags.append(("MISMATCH", key, f"verify counts {n}, summary.json says {b.get('count')}"))
        prior = prior_ok_run(run_dir, system, slug, root)
        if n == 0:
            if prior is None:
                flags.append(("UNCONFIRMED", key, "first observation is a 200 with 0 postings"))
            elif suspect_check(prior[1], n):
                flags.append(("SUSPECT", key, f"{prior[1]} postings in prior run {prior[0]}, 0 now"))
        lines.append(f"{'':9}{key}: verify counts {n}; summary.json says {b.get('count')}; "
                     f"prior OK run: {prior[0] + ' (' + str(prior[1]) + ')' if prior else 'none'}")
    return flags, lines


def main(argv):
    if len(argv) != 1:
        print("usage: python -m jobwatch verify runs/<run-id>")
        return FLAGGED
    run_dir = argv[0]
    flags, lines = verify(run_dir)
    print(f"verify {run_dir} (independent check; reads raw bytes only)")
    for line in lines:
        print(line)
    for flag, board, msg in flags:
        print(f"{flag:<9}{board or '-'}: {msg}")
    print(f"result: {'FLAGGED' if flags else 'CLEAN'} ({len(flags)} flag(s))")
    return FLAGGED if flags else CLEAN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
