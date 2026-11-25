"""JS3 audit run: judge every saved posting once, offline, so the hand audit has one fixed list.

Why it exists: the audit samples from "everything the filter has seen". Postings repeat across
runs, so they are deduplicated by (board, posting id) and the newest folder's copy wins, since
that is what the filter would judge today. It reads only evidence/raw/ and the persona, fetches
nothing and calls no model.

Run: .venv/bin/python reports/audit_run.py   -> audit/all_verdicts.json, audit/summary.md
Tested by: tests/test_js3_audit.py (fake raw folders under tmp_path; never writes audit/)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from job_agent import inputs  # noqa: E402
from job_agent.common.paths import Paths  # noqa: E402
from job_agent.judges import rule  # noqa: E402
from job_agent.watch.boards import ashby, greenhouse  # noqa: E402

PARSERS = {"stripe": greenhouse, "cloudflare": greenhouse, "openai": ashby}
SUFFIX = "_content.json"
COLUMNS = ["1a", "1b", "2", "3", "4", "5", "6", "error", "relevant"]


def _url(board: str, job: dict) -> str:
    key = "jobUrl" if PARSERS[board] is ashby else "absolute_url"
    return job.get(key) or ""


def _show(path: Path) -> str:
    path = path.resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def collect(raw_root: Path) -> tuple[list[str], dict]:
    """(folder names, {(board, str id): (posting, url, raw file)}); later folders overwrite earlier ones."""
    folders = sorted(d for d in Path(raw_root).iterdir() if d.is_dir())
    found = {}
    for folder in folders:
        for f in sorted(folder.glob(f"*{SUFFIX}")):
            board = f.name[: -len(SUFFIX)]
            if board not in PARSERS:
                continue
            body = f.read_bytes()
            jobs = {str(j.get("id")): j for j in json.loads(body).get("jobs", []) if isinstance(j, dict)}
            for posting in PARSERS[board].parse(body):
                key = (board, str(posting.id))
                found[key] = (posting, _url(board, jobs.get(key[1], {})), f)
    return [d.name for d in folders], found


def column(p: dict) -> str:
    if p["status"] == "error":
        return "error"
    if p["verdict"] == "relevant":
        return "relevant"
    return p["failed_check"]


def summary_md(postings: list[dict], folders: list[str]) -> str:
    counts: dict[str, dict[str, int]] = {}
    for p in postings:
        counts.setdefault(p["board"], dict.fromkeys(COLUMNS, 0))[column(p)] += 1
    grand = dict.fromkeys(COLUMNS, 0)
    lines = ["# Audit run summary", "",
             f"All saved postings, deduplicated (newest folder wins), from {len(folders)} raw folders.",
             "Columns 1a-6 count not_relevant postings by the rule that cut them.", "",
             "| board | total | " + " | ".join(COLUMNS) + " |",
             "|---" * (len(COLUMNS) + 2) + "|"]
    for board in sorted(counts):
        c = counts[board]
        for col in COLUMNS:
            grand[col] += c[col]
        lines.append(f"| {board} | {sum(c.values())} | " + " | ".join(str(c[k]) for k in COLUMNS) + " |")
    lines.append(f"| total | {sum(grand.values())} | " + " | ".join(str(grand[k]) for k in COLUMNS) + " |")
    return "\n".join(lines) + "\n"


def run(raw_root: Path, out_dir: Path) -> int:
    paths = Paths()
    criteria = inputs.load_criteria(paths.default_resume, paths.default_profile, paths)
    folders, found = collect(Path(raw_root))
    postings = []
    for key in sorted(found):
        posting, url, raw_file = found[key]
        r = rule.judge(posting, criteria)
        postings.append({
            "board": key[0], "posting_id": posting.id, "title": posting.title, "location": posting.location,
            "url": url, "raw_file": _show(raw_file),
            "verdict": r.verdict["verdict"], "status": r.verdict["status"],
            "failed_check": r.failed_check, "justification": r.verdict["justification"],
        })
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data = {"generated_from": folders, "total": len(postings), "postings": postings}
    (out_dir / "all_verdicts.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "summary.md").write_text(summary_md(postings, folders), encoding="utf-8")
    print(f"{len(postings)} postings from {len(folders)} folders -> {_show(out_dir)}")
    return 0


def main() -> None:
    sys.exit(run(ROOT / "evidence" / "raw", ROOT / "audit"))


if __name__ == "__main__":
    main()
