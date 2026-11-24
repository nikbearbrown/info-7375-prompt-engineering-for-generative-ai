"""JS3 seal tooling: the counts step, the draw and the replacement draw (SEAL.md v1.3; FILTER.md v1 §3).

Run from the JS3 folder:
    python3.13 tools/seal_draw.py counts
    python3.13 tools/seal_draw.py draw --final P O --js3 P O
    python3.13 tools/seal_draw.py replace-js3 --final P O --exposed P O --js3 P O

P and O are the numbers of "product" and "other" postings in a set.

No subcommand ever prints a posting id or a title. counts prints counts
only; draw and replace-js3 print set sizes only. The ids go to files in
vault/, the titles go nowhere.

replace-js3 (SEAL.md §8) re-derives the final's set and the exposed set (the
first JS3 set, retired) from the same ranking, checks them against the
committed vault files byte for byte, and writes the next ranks after the
exposed set in each group to vault/js3_heldout_ids_v2.tsv.

Standard library only.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# SEAL.md v1 §5: the seed is the first 8 characters of the CP1 commit
# (a6ac8bbb229a..., "JS3-CP1: FILTER.md v1"). It is a constant on purpose:
# SEAL.md §7 rules out drawing again with a different seed, so there is no
# seed option.
SEED = "a6ac8bbb"

# SEAL.md v1 §4: final's set 15 product + 5 other; JS3's held-out set
# 22 product + 8 other.
SEAL_PRODUCT_DRAWN = 15 + 22
SEAL_OTHER_DRAWN = 5 + 8

JS3_ROOT = Path(__file__).resolve().parent.parent
VAULT = "vault"
FINAL_FILE = "final_heldout_ids.tsv"
JS3_FILE = "js3_heldout_ids.tsv"  # the first JS3 set; since SEAL.md v1.3 §8, the exposed set
JS3_V2_FILE = "js3_heldout_ids_v2.tsv"  # SEAL.md §8: JS3's held-out set from now on
SEAL_HEADER = ("board_key", "id", "group", "rank")

J1 = "../js1-contract-and-watch/"
J2 = "../js2-loop-tools-diff/"

# FILTER.md v1 §3: the corpus is exactly these 20 files. Each entry is
# (board key, path relative to the JS3 folder, UTC time from the file name).
# A date-only file name counts as 00:00:00Z that day.
CORPUS = (
    ("greenhouse:stripe", J1 + "evidence/stripe_jobs_content_true_2026-10-25.json", "2026-10-25T00:00:00Z"),
    ("greenhouse:stripe", J1 + "evidence/stripe_jobs_content_true_2026-10-26.json", "2026-10-26T00:00:00Z"),
    ("greenhouse:stripe", J1 + "evidence/stripe_jobs_content_true_2026-10-27T223947Z.json", "2026-10-27T22:39:47Z"),
    ("greenhouse:stripe", J1 + "evidence/stripe_jobs_content_true_2026-10-29T011132Z.json", "2026-10-29T01:11:32Z"),
    ("greenhouse:stripe", J2 + "evidence/gate_probes/gh_stripe_2026-11-02T194203Z.json", "2026-11-02T19:42:03Z"),
    ("greenhouse:stripe", J2 + "evidence/snapshots/stripe_2026-11-05T194454Z.json", "2026-11-05T19:44:54Z"),
    ("greenhouse:stripe", J2 + "evidence/greenhouse_stripe_2026-11-07T000611Z_a1.json", "2026-11-07T00:06:11Z"),
    ("greenhouse:stripe", J2 + "evidence/greenhouse_stripe_2026-11-08T015437Z_a1.json", "2026-11-08T01:54:37Z"),
    ("greenhouse:duolingo", J2 + "evidence/gate_probes/gh_duolingo_2026-11-02T194205Z.json", "2026-11-02T19:42:05Z"),
    ("greenhouse:duolingo", J2 + "evidence/snapshots/duolingo_2026-11-05T194456Z.json", "2026-11-05T19:44:56Z"),
    ("greenhouse:duolingo", J2 + "evidence/greenhouse_duolingo_2026-11-07T000611Z_a1.json", "2026-11-07T00:06:11Z"),
    ("greenhouse:duolingo", J2 + "evidence/greenhouse_duolingo_2026-11-08T015438Z_a1.json", "2026-11-08T01:54:38Z"),
    ("greenhouse:robinhood", J2 + "evidence/gate_probes/gh_robinhood_2026-11-02T194206Z.json", "2026-11-02T19:42:06Z"),
    ("greenhouse:robinhood", J2 + "evidence/snapshots/robinhood_2026-11-05T194457Z.json", "2026-11-05T19:44:57Z"),
    ("greenhouse:robinhood", J2 + "evidence/greenhouse_robinhood_2026-11-07T000612Z_a1.json", "2026-11-07T00:06:12Z"),
    ("greenhouse:robinhood", J2 + "evidence/greenhouse_robinhood_2026-11-08T015438Z_a1.json", "2026-11-08T01:54:38Z"),
    ("ashby:notion", J2 + "evidence/gate_probes/ashby_notion_2026-11-02T194212Z.json", "2026-11-02T19:42:12Z"),
    ("ashby:notion", J2 + "evidence/snapshots/notion_2026-11-05T194458Z.json", "2026-11-05T19:44:58Z"),
    ("ashby:notion", J2 + "evidence/ashby_notion_2026-11-07T000611Z_a1.json", "2026-11-07T00:06:11Z"),
    ("ashby:notion", J2 + "evidence/ashby_notion_2026-11-08T015438Z_a1.json", "2026-11-08T01:54:38Z"),
)

# Folders whose SHA256SUMS.txt is checked against the corpus manifest.
SHA256SUMS_DIRS = (J2 + "evidence/gate_probes", J2 + "evidence/snapshots")

# JS1 worked on one board only.
JS1_BOARD = "greenhouse:stripe"

# SEAL.md v1 §2: the seen list. Each entry is (path relative to the JS3
# folder, kind, how ids are taken from it). Only committed JS1 and JS2 files.
# Agent state files are not here: they record what the agent fetched, not
# what a person opened, labeled, judged or sampled.
SEEN_SOURCES = (
    (J1 + "experiments/hand_labels_development.json", "hand label", "labels"),
    (J1 + "experiments/hand_labels_heldout.json", "hand label", "labels"),
    (J1 + "experiments/selected_ids.json", "other", "selected_ids"),
    (J1 + "claude_outputs/metadata.json", "saved reply", "metadata_keys"),
    (J1 + "experiments/prompt_experiment/baseline/metadata.json", "saved reply", "metadata_keys"),
    (J1 + "experiments/prompt_experiment/revision/metadata.json", "saved reply", "metadata_keys"),
    (J1 + "experiments/sampling/metadata.json", "sampled", "sampling_posting_ids"),
    (J1 + "experiments/action_surface/way2_input_8154295.txt", "action surface", "id_in_file_name"),
    (J1 + "experiments/action_surface/way2_reply_8154295.txt", "action surface", "id_in_file_name"),
    (J1 + "experiments/action_surface/way3_agent/way3_reply_8154295.txt", "action surface", "id_in_file_name"),
    (J1 + "evidence/run_report_run1_2026-10-27.json", "run report", "js1_run_report"),
    (J1 + "evidence/run_report_run2_2026-10-28.json", "run report", "js1_run_report"),
    (J1 + "evidence/run_report_run2_seeded_rerun_with_claude_2026-10-29.json", "run report", "js1_run_report"),
    (J1 + "run_report.json", "run report", "js1_run_report"),
    (J2 + "output/run_report_2026-11-07T000611Z.json", "run report", "js2_run_report"),
    (J2 + "output/run_report_2026-11-08T015437Z.json", "run report", "js2_run_report"),
    (J2 + "evidence/demo_finished_wrong_answer/run_report_2026-11-07T233828Z.json", "run report", "js2_run_report"),
)

# Ids a committed file names outside any structured field. Each is checked
# against its file at run time: if the file no longer contains the id, the
# run stops. (board key, id, path relative to the JS3 folder, kind)
SEEN_NAMED = (
    # CONTRACT.md §1 cites it as the example JSON-number id from the
    # 2026-10-25 response, and refusal case U03 uses it in a URL.
    (JS1_BOARD, "8172510", J1 + "CONTRACT.md", "other"),
)

_WHITESPACE = re.compile(r"\s+")
_ID_IN_NAME = re.compile(r"_(\d+)\.txt$")


class SealError(Exception):
    """Stops the run: nothing is printed as counts and no set is written."""


# ---------------------------------------------------------------- corpus

def clean_title(value):
    """FILTER.md F1: trim and collapse whitespace. Missing, non-text or empty is None."""
    if not isinstance(value, str):
        return None
    cleaned = _WHITESPACE.sub(" ", value).strip()
    return cleaned or None


def group_of(title):
    """SEAL.md §3: "product" if the cleaned title contains "product" (any case), else "other"."""
    cleaned = clean_title(title)
    return "product" if cleaned is not None and "product" in cleaned.lower() else "other"


def _job_id(board, job):
    if not isinstance(job, dict):
        return None
    raw = job.get("id")
    if board.startswith("greenhouse:"):
        # Greenhouse ids are JSON numbers; str() at the boundary, as in JS2.
        if isinstance(raw, bool):
            return None
        if isinstance(raw, int) or (isinstance(raw, str) and raw):
            return str(raw)
        return None
    if board.startswith("ashby:"):
        return raw if isinstance(raw, str) and raw else None
    raise SealError(f"unknown ATS in board key {board!r}")


def read_corpus_file(root, board, rel):
    """(bytes, [(id, raw title)]) for one corpus file. Missing or unparseable stops the run."""
    path = Path(root) / rel
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise SealError(f"corpus file missing or unreadable: {rel} ({type(exc).__name__})") from exc
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise SealError(f"corpus file is not JSON: {rel}") from exc
    jobs = data.get("jobs") if isinstance(data, dict) else None
    if not isinstance(jobs, list):
        raise SealError(f"corpus file has no 'jobs' list: {rel}")
    rows = []
    for index, job in enumerate(jobs):
        job_id = _job_id(board, job)
        if job_id is None:
            raise SealError(f"corpus file job #{index} has no usable id: {rel}")
        rows.append((job_id, job.get("title")))
    return raw, rows


def load_corpus(root, corpus):
    """Read every corpus file. Returns (manifest rows, {(board, id): raw title of the latest copy})."""
    files = []
    for board, rel, utc in corpus:
        raw, rows = read_corpus_file(root, board, rel)
        files.append((utc, board, rel, raw, rows))
    latest = {}
    manifest = []
    # FILTER.md §3: the copy from the latest file wins. Sorted by time, so a
    # later file overwrites; the sort is stable for equal times.
    for utc, board, rel, raw, rows in sorted(files, key=lambda f: f[0]):
        for job_id, title in rows:
            latest[(board, job_id)] = title
    for utc, board, rel, raw, rows in files:
        manifest.append({
            "path": rel,
            "board": board,
            "utc": utc,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "jobs": len(rows),
            "unique_ids": len({job_id for job_id, _ in rows}),
            "sidecar_sha256": read_sidecar_sha256(root, rel),
        })
    return manifest, latest


def read_sidecar_sha256(root, rel):
    """The sha256 in <file>.sidecar.json; None when there is no sidecar; "" when it has no usable sha256.

    A sidecar is evidence about a corpus file, not part of the corpus, so a
    bad sidecar is reported in the manifest and does not stop the run.
    """
    path = Path(root) / (rel + ".sidecar.json")
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8")).get("sha256")
    except (OSError, ValueError, AttributeError):
        return ""
    return value.lower() if isinstance(value, str) and value else ""


def sidecar_check(entry):
    expected = entry["sidecar_sha256"]
    if expected is None:
        return "no sidecar"
    if expected == "":
        return "sidecar without sha256"
    return "match" if expected == entry["sha256"] else "MISMATCH"


def read_sha256sums(root, dirs):
    """{normalized path relative to root: expected hash} from every SHA256SUMS.txt that exists."""
    listed = {}
    for rel_dir in dirs:
        sums = Path(root) / rel_dir / "SHA256SUMS.txt"
        if not sums.is_file():
            continue
        for line in sums.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 2:
                listed[_norm(f"{rel_dir}/{parts[1].lstrip('*')}")] = parts[0].lower()
    return listed


def _norm(rel):
    return str(Path(rel)).replace("\\", "/")


# ---------------------------------------------------------------- seen list

def _read_json(root, rel):
    try:
        return json.loads((Path(root) / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SealError(f"seen-list source missing or unreadable: {rel} ({type(exc).__name__})") from exc


def _seen_from_source(root, rel, how):
    """[(board, id)] that one source records. Raises SealError when its shape is not the expected one."""
    if how == "id_in_file_name":
        if not (Path(root) / rel).is_file():
            raise SealError(f"seen-list source missing: {rel}")
        match = _ID_IN_NAME.search(rel)
        if not match:
            raise SealError(f"seen-list source has no id in its name: {rel}")
        return [(JS1_BOARD, match.group(1))]
    data = _read_json(root, rel)
    try:
        if how == "labels":
            return [(JS1_BOARD, str(entry["id"])) for entry in data["labels"]]
        if how == "selected_ids":
            return [(JS1_BOARD, str(i)) for i in data["development"] + data["held_out"]]
        if how == "metadata_keys":
            return [(JS1_BOARD, str(key)) for key in data]
        if how == "sampling_posting_ids":
            return [(JS1_BOARD, str(entry["posting_id"])) for entry in data.values()]
        if how == "js1_run_report":
            ids = [str(i) for i in data["summary"]["new_ids"]]
            ids += [str(p["posting_id"]) for p in data["new_postings"]]
            return [(JS1_BOARD, i) for i in ids]
        if how == "js2_run_report":
            out = []
            for board in data["boards"]:
                ids = [str(i) for i in board.get("new_ids", [])]
                ids += [str(p["posting_id"]) for p in board.get("new_postings", [])]
                out += [(board["board"], i) for i in ids]
            return out
    except (KeyError, TypeError, AttributeError) as exc:
        raise SealError(f"seen-list source has an unexpected shape: {rel}") from exc
    raise SealError(f"unknown extraction {how!r} for {rel}")


def load_seen(root, sources, named):
    """Sorted, de-duplicated rows (board, id, source, kind)."""
    rows = set()
    for rel, kind, how in sources:
        for board, posting_id in _seen_from_source(root, rel, how):
            rows.add((board, posting_id, rel, kind))
    for board, posting_id, rel, kind in named:
        path = Path(root) / rel
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SealError(f"seen-list source missing or unreadable: {rel}") from exc
        if posting_id not in text:
            raise SealError(f"seen-list source no longer names its id: {rel}")
        rows.add((board, posting_id, rel, kind))
    return sorted(rows)


# ---------------------------------------------------------------- pool and groups

def build(root, corpus, sources, named):
    """Everything counts and draw share. Raises SealError before anything is printed or written."""
    manifest, latest = load_corpus(root, corpus)
    seen_rows = load_seen(root, sources, named)
    seen = {(board, posting_id) for board, posting_id, _, _ in seen_rows}
    pool = {key: title for key, title in latest.items() if key not in seen}
    groups = {"product": [], "other": []}
    for key, title in pool.items():
        groups[group_of(title)].append(key)
    return {
        "manifest": manifest,
        "latest": latest,
        "seen_rows": seen_rows,
        "seen": seen,
        "pool": pool,
        "groups": groups,
        "boards": [b for b in dict.fromkeys(board for board, _, _ in corpus)],
    }


def rank(board, posting_id):
    """SEAL.md §5: SHA-256 of "<seed>:<board key>:<id>", lowercase hex."""
    return hashlib.sha256(f"{SEED}:{board}:{posting_id}".encode("utf-8")).hexdigest()


def ranked(keys):
    """Lowest rank first; (board, id) breaks a tie, which SHA-256 makes practically impossible."""
    return sorted(keys, key=lambda key: (rank(*key), key))


# ---------------------------------------------------------------- counts

def _per_board(keys, boards):
    counts = {board: 0 for board in boards}
    for board, _ in keys:
        counts[board] = counts.get(board, 0) + 1
    return ", ".join(f"{board} {counts[board]}" for board in sorted(counts)) + f"; total {len(keys)}"


def counts_text(state, sums):
    boards = state["boards"]
    groups = state["groups"]
    seen = state["seen"]
    in_corpus = sum(1 for key in seen if key in state["latest"])
    listed = [m for m in state["manifest"] if _norm(m["path"]) in sums]
    matching = [m for m in listed if sums[_norm(m["path"])] == m["sha256"]]
    with_sidecar = [m for m in state["manifest"] if m["sidecar_sha256"]]
    sidecar_matching = [m for m in with_sidecar if sidecar_check(m) == "match"]
    product, other = len(groups["product"]), len(groups["other"])
    product_fits = product >= 2 * SEAL_PRODUCT_DRAWN
    other_fits = other >= SEAL_OTHER_DRAWN
    lines = [
        "JS3 seal counts (SEAL.md v1). Counts only: no ids, no titles.",
        f"corpus files read: {len(state['manifest'])}",
        f"corpus files listed in a SHA256SUMS.txt: {len(listed)}; hash matches: {len(matching)}",
        f"corpus files with a sidecar sha256: {len(with_sidecar)}; hash matches: {len(sidecar_matching)}",
        f"unique postings: {_per_board(list(state['latest']), boards)}",
        f"seen ids found: {len(seen)}; in the corpus: {in_corpus}; not in the corpus: {len(seen) - in_corpus}",
        f"pool: {_per_board(list(state['pool']), boards)}",
        f"product group: {_per_board(groups['product'], boards)}",
        f"other group: {_per_board(groups['other'], boards)}",
        f"SEAL.md §4 sizes: product drawn {SEAL_PRODUCT_DRAWN} (final 15 + JS3 22) needs a product group of "
        f"at least {2 * SEAL_PRODUCT_DRAWN}: {'fits' if product_fits else 'does not fit'} ({product})",
        f"SEAL.md §4 sizes: other drawn {SEAL_OTHER_DRAWN} (final 5 + JS3 8) needs an other group of "
        f"at least {SEAL_OTHER_DRAWN}: {'fits' if other_fits else 'does not fit'} ({other})",
    ]
    return "\n".join(lines) + "\n"


def _write_tsv(path, header, rows):
    lines = ["\t".join(header)] + ["\t".join(str(cell) for cell in row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_counts(root, corpus, sources, named, sums_dirs, out):
    state = build(root, corpus, sources, named)
    sums = read_sha256sums(root, sums_dirs)
    text = counts_text(state, sums)
    vault = Path(root) / VAULT
    vault.mkdir(exist_ok=True)
    manifest_rows = []
    for m in state["manifest"]:
        expected = sums.get(_norm(m["path"]))
        check = "not listed" if expected is None else ("match" if expected == m["sha256"] else "MISMATCH")
        manifest_rows.append((m["path"], m["board"], m["utc"], m["sha256"], m["jobs"], m["unique_ids"], check,
                              sidecar_check(m)))
    _write_tsv(vault / "corpus_manifest.tsv",
               ("path", "board_key", "utc_time", "sha256", "jobs", "unique_ids", "sha256sums_check",
                "sidecar_check"),
               manifest_rows)
    _write_tsv(vault / "seen_ids.tsv",
               ("board_key", "id", "source_file", "kind", "in_corpus"),
               [(b, i, src, kind, "yes" if (b, i) in state["latest"] else "no")
                for b, i, src, kind in state["seen_rows"]])
    (vault / "counts.txt").write_text(text, encoding="utf-8")
    out.write(text)


# ---------------------------------------------------------------- draw

def draw_sets(groups, final, js3):
    """{"final": [...], "js3": [...]} of (board, id, group, rank). final and js3 are (product, other)."""
    sets = {"final": [], "js3": []}
    for index, name in enumerate(("product", "other")):
        n_final, n_js3 = final[index], js3[index]
        order = ranked(groups[name])
        if n_final + n_js3 > len(order):
            raise SealError(f"the {name} group has {len(order)} postings; {n_final + n_js3} were asked for")
        sets["final"] += [(b, i, name, rank(b, i)) for b, i in order[:n_final]]
        sets["js3"] += [(b, i, name, rank(b, i)) for b, i in order[n_final:n_final + n_js3]]
    return sets


def cmd_draw(root, corpus, sources, named, final, js3, out):
    if min(final + js3) < 0:
        raise SealError("set sizes must be 0 or more")
    vault = Path(root) / VAULT
    targets = (vault / FINAL_FILE, vault / JS3_FILE)
    existing = [t.name for t in targets if t.exists()]
    if existing:
        raise SealError("refusing to overwrite: " + ", ".join(f"{VAULT}/{name}" for name in existing))
    state = build(root, corpus, sources, named)
    product = len(state["groups"]["product"])
    drawn_product = final[0] + js3[0]
    # SEAL.md §4: the development pool keeps at least half of the product group either way.
    if 2 * drawn_product > product:
        raise SealError(f"{drawn_product} product postings drawn would leave less than half of the "
                        f"product group ({product}) in the development pool (SEAL.md §4)")
    sets = draw_sets(state["groups"], final, js3)
    vault.mkdir(exist_ok=True)
    header = ("board_key", "id", "group", "rank")
    for target, name in zip(targets, ("final", "js3")):
        lines = ["\t".join(header)] + ["\t".join(row) for row in sets[name]]
        with open(target, "x", encoding="utf-8") as handle:  # "x": never overwrite
            handle.write("\n".join(lines) + "\n")
    out.write(f"final's set: product {final[0]}, other {final[1]}\n"
              f"JS3's held-out set: product {js3[0]}, other {js3[1]}\n")


# ---------------------------------------------------------------- replacement draw (SEAL.md §8)

def set_text(rows):
    """A set file's text exactly as draw writes it: the header, then one line per (board, id, group, rank)."""
    return "\n".join(["\t".join(SEAL_HEADER)] + ["\t".join(row) for row in rows]) + "\n"


def replacement_sets(groups, final, exposed, js3):
    """(final's rows, exposed rows, replacement rows). Each size is (product, other).

    The final's set and the exposed set are re-derived with draw_sets, the code
    that wrote the committed files. The replacement takes, in each group, the
    next ranks after the exposed set.
    """
    for index, name in enumerate(("product", "other")):
        needed = final[index] + exposed[index] + js3[index]
        if needed > len(groups[name]):
            raise SealError(f"the {name} group has {len(groups[name])} postings; the final's, exposed and "
                            f"replacement ranges need {needed}")
    sets = draw_sets(groups, final, exposed)
    replacement = []
    for index, name in enumerate(("product", "other")):
        start = final[index] + exposed[index]
        replacement += [(b, i, name, rank(b, i)) for b, i in ranked(groups[name])[start:start + js3[index]]]
    return sets["final"], sets["js3"], replacement


def check_committed(vault, file_name, rows):
    """Stop unless vault/<file_name> is byte for byte the file draw would write for rows. Never prints a row."""
    shown = f"{VAULT}/{file_name}"
    try:
        actual = (Path(vault) / file_name).read_bytes()
    except OSError as exc:
        raise SealError(f"cannot read {shown} ({type(exc).__name__}); nothing written") from exc
    expected = set_text(rows).encode("utf-8")
    if actual == expected:
        return
    got, want = actual.splitlines(), expected.splitlines()
    if len(got) != len(want):
        detail = f"it has {len(got)} lines, the re-derived set has {len(want)}"
    else:
        differing = [number for number, (a, b) in enumerate(zip(got, want), start=1) if a != b]
        detail = f"line {differing[0]} differs" if differing else "its line endings differ"
    raise SealError(f"{shown} does not match the re-derived set: {detail}; nothing written")


def _rank_range(start, n):
    return f"ranks {start + 1}-{start + n}" if n else "no ranks"


def cmd_replace_js3(root, corpus, sources, named, final, exposed, js3, out):
    if min(final + exposed + js3) < 0:
        raise SealError("set sizes must be 0 or more")
    vault = Path(root) / VAULT
    target = vault / JS3_V2_FILE
    if target.exists():
        raise SealError(f"refusing to overwrite: {VAULT}/{JS3_V2_FILE}")
    state = build(root, corpus, sources, named)
    product = len(state["groups"]["product"])
    # SEAL.md §8 with §4's half-rule: the exposed set returns to the development pool, so the
    # sealed product postings are the final's plus the replacement's.
    sealed_product = final[0] + js3[0]
    if 2 * sealed_product > product:
        raise SealError(f"{sealed_product} sealed product postings (final's {final[0]} + replacement's {js3[0]}) "
                        f"would leave less than half of the product group ({product}) in the development "
                        f"pool (SEAL.md §4, §8)")
    final_rows, exposed_rows, replacement = replacement_sets(state["groups"], final, exposed, js3)
    check_committed(vault, FINAL_FILE, final_rows)
    check_committed(vault, JS3_FILE, exposed_rows)
    with open(target, "x", encoding="utf-8") as handle:  # "x": never overwrite
        handle.write(set_text(replacement))
    p_start, o_start = final[0] + exposed[0], final[1] + exposed[1]
    out.write(f"final's set: product {final[0]}, other {final[1]}; matches {VAULT}/{FINAL_FILE}\n"
              f"exposed set: product {exposed[0]}, other {exposed[1]}; matches {VAULT}/{JS3_FILE}\n"
              f"JS3's held-out set v2: product {js3[0]} ({_rank_range(p_start, js3[0])}), "
              f"other {js3[1]} ({_rank_range(o_start, js3[1])}); written to {VAULT}/{JS3_V2_FILE}\n"
              f"sealed product postings: {sealed_product} of {product}; the development pool keeps "
              f"{product - sealed_product}\n")


# ---------------------------------------------------------------- command line

def main(argv=None, root=JS3_ROOT, corpus=CORPUS, sources=SEEN_SOURCES, named=SEEN_NAMED,
         sums_dirs=SHA256SUMS_DIRS, out=None, err=None):
    out = out or sys.stdout
    err = err or sys.stderr
    parser = argparse.ArgumentParser(prog="seal_draw.py",
                                     description="JS3 seal: counts, the draw, the replacement draw (SEAL.md v1.3).")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("counts", help="print counts only; write vault/corpus_manifest.tsv, seen_ids.tsv, counts.txt")
    draw = sub.add_parser("draw", help="write vault/final_heldout_ids.tsv and vault/js3_heldout_ids.tsv")
    draw.add_argument("--final", nargs=2, type=int, required=True, metavar=("P", "O"))
    draw.add_argument("--js3", nargs=2, type=int, required=True, metavar=("P", "O"))
    replace = sub.add_parser("replace-js3", help="check the committed sets, then write vault/js3_heldout_ids_v2.tsv "
                                                 "(SEAL.md §8)")
    replace.add_argument("--final", nargs=2, type=int, required=True, metavar=("P", "O"))
    replace.add_argument("--exposed", nargs=2, type=int, required=True, metavar=("P", "O"))
    replace.add_argument("--js3", nargs=2, type=int, required=True, metavar=("P", "O"))
    args = parser.parse_args(argv)
    try:
        if args.command == "counts":
            cmd_counts(root, corpus, sources, named, sums_dirs, out)
        elif args.command == "draw":
            cmd_draw(root, corpus, sources, named, tuple(args.final), tuple(args.js3), out)
        else:
            cmd_replace_js3(root, corpus, sources, named, tuple(args.final), tuple(args.exposed),
                            tuple(args.js3), out)
    except SealError as exc:
        err.write(f"error: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
