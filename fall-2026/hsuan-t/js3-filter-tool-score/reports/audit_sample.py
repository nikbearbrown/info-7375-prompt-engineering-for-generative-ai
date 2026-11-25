"""JS3 hand-judging sheet: a seeded, stratified, blind sample of the audit run's verdicts.

Why it exists: Isaac labels a sample by hand to measure the filter. Three strata answer three
questions: random rejects (does the filter throw away good postings?), close calls (postings that
sat on a rule's edge) and kept postings (does it let bad ones through?). The sheet Isaac reads
(to_judge.md) shows only the posting, never the filter's decision, so the labels are not anchored
on it; the decision is kept in sample_key.json for audit_report.py. A fixed seed makes the sample
reproducible, and a CSV with labels in it is never overwritten.

Run: .venv/bin/python reports/audit_sample.py   (after reports/audit_run.py)
     -> audit/to_judge.md, audit/hand_verdicts.csv, audit/sample_key.json
Tested by: tests/test_js3_audit.py (fake raw folders under tmp_path; never writes audit/)
"""

import csv
import io
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from job_agent.judges.words import strip_html  # noqa: E402

SEED = 20261124
N_RANDOM_REJECT = 30
N_CLOSE_CALL = 10
N_KEPT = 10
CSV_HEADER = ["sample_id", "board", "posting_id", "my_label", "my_reason"]


def _key(p: dict) -> tuple[str, str]:
    return (p["board"], str(p["posting_id"]))


def _result(p: dict, idx: int) -> str:
    j = p["justification"]
    return j[idx]["result"] if len(j) > idx else ""


def close_call_groups(postings: list[dict]) -> list[list[dict]]:
    """The four edge cases, in priority order (justification line 3 is rule 3, line 4 is rule 4).
    Rule 4 says "min N" under FILTER v1 and "max N" under v2; both are read so a v2 re-run still finds them."""
    ok = [p for p in postings if p["status"] == "ok"]
    fc = lambda p: p["failed_check"]  # noqa: E731
    return [
        [p for p in ok if len(p["justification"]) > 3 and fc(p) != "3" and _result(p, 3).startswith("1 found")],
        [p for p in ok if fc(p) == "4" and _result(p, 4).startswith(("min 5 years", "max 5 years"))],
        [p for p in ok if len(p["justification"]) > 4 and fc(p) != "4" and _result(p, 4).startswith(("min 4 years", "max 4 years"))],
        [p for p in ok if fc(p) == "2"],
    ]


def draw(postings: list[dict], rng: random.Random) -> list[tuple[str, dict]]:
    """(stratum, posting) picks; no posting is picked twice."""
    postings = sorted(postings, key=_key)  # draws depend on the content, not on file order
    rejects = [p for p in postings if p["status"] == "ok" and p["verdict"] == "not_relevant"]
    picks = [("random_reject", p) for p in rng.sample(rejects, min(N_RANDOM_REJECT, len(rejects)))]
    taken = {_key(p) for _, p in picks}

    close = []
    for group in close_call_groups(postings):
        for p in rng.sample(group, len(group)):
            if len(close) >= N_CLOSE_CALL:
                break
            if _key(p) not in taken:
                close.append(p)
                taken.add(_key(p))
    picks += [("close_call", p) for p in close]

    relevant = [p for p in postings if p["status"] == "ok" and p["verdict"] == "relevant" and _key(p) not in taken]
    picks += [("kept", p) for p in rng.sample(relevant, min(N_KEPT, len(relevant)))]
    rng.shuffle(picks)
    return picks


def _raw_path(raw_file: str) -> Path:
    path = Path(raw_file)
    return path if path.is_absolute() else ROOT / path


def jd_text(p: dict) -> str:
    """The JD as plain text, read from the raw file the verdict came from."""
    data = json.loads(_raw_path(p["raw_file"]).read_text(encoding="utf-8"))
    for job in data.get("jobs", []):
        if isinstance(job, dict) and str(job.get("id")) == str(p["posting_id"]):
            return strip_html(job.get("content") or job.get("descriptionHtml") or "").strip()
    return ""


def to_judge_md(samples: list[tuple[str, dict]]) -> str:
    lines = ["# Postings to judge", "",
             "For each posting, decide whether you would apply (relevant) or not (not_relevant), and write",
             "the label and a short reason into hand_verdicts.csv. Judge from the posting alone.", ""]
    for sid, p in samples:
        lines += [f"## {sid}", "",
                  f"- board: {p['board']}",
                  f"- title: {p['title']}",
                  f"- location: {p['location']}",
                  f"- url: {p['url']}", "",
                  jd_text(p) or "(no job description text)", ""]
    return "\n".join(lines)


def _filled_labels(csv_path: Path) -> list[str]:
    if not csv_path.exists():
        return []
    with csv_path.open(newline="", encoding="utf-8") as f:
        return [row.get("sample_id", "?") for row in csv.DictReader(f) if (row.get("my_label") or "").strip()]


def sample(audit_dir: Path, out_dir: Path, seed: int = SEED) -> int:
    out_dir = Path(out_dir)
    filled = _filled_labels(out_dir / "hand_verdicts.csv")
    if filled:
        print(f"refusing to write: {out_dir / 'hand_verdicts.csv'} already has labels "
              f"({', '.join(filled)}); move it away to draw a new sample", file=sys.stderr)
        return 1
    data = json.loads((Path(audit_dir) / "all_verdicts.json").read_text(encoding="utf-8"))
    rng = random.Random(seed)
    picks = draw(data["postings"], rng)
    samples = [(f"S{i:02d}", p) for i, (_, p) in enumerate(picks, start=1)]

    key = {sid: {"board": p["board"], "posting_id": p["posting_id"], "title": p["title"], "stratum": stratum,
                 "verdict": p["verdict"], "failed_check": p["failed_check"], "seed": seed}
           for (sid, p), (stratum, _) in zip(samples, picks)}
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(CSV_HEADER)
    for sid, p in samples:
        writer.writerow([sid, p["board"], str(p["posting_id"]), "", ""])

    text = to_judge_md(samples)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sample_key.json").write_text(json.dumps(key, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "hand_verdicts.csv").write_text(buf.getvalue(), encoding="utf-8", newline="")
    (out_dir / "to_judge.md").write_text(text, encoding="utf-8")
    counts = {s: sum(1 for st, _ in picks if st == s) for s in ("random_reject", "close_call", "kept")}
    print(f"{len(samples)} samples (seed {seed}): {counts}")
    return 0


def main() -> None:
    sys.exit(sample(ROOT / "audit", ROOT / "audit"))


if __name__ == "__main__":
    main()
