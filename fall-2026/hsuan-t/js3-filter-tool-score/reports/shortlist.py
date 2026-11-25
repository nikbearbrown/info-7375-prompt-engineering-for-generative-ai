"""JS3 shortlist: turn every kept posting's justification into claims, each with a code-proposed label.

Why it exists: FILTER.md section 2 says a "relevant" verdict must be shown next to the evidence
for it, and missing information (no years, no visa line, no salary) must be visible as an
*insufficient* claim instead of hiding behind the verdict. This script reads the audit list
(audit/all_verdicts.json), re-reads each kept posting's JD from its saved raw file, and for rules
1b, 2, 3, 4, 5 and 6 writes one claim per justification line (one per skill for rule 3). Code
only proposes "supported" (with a verbatim quote) or "insufficient" (quote null); "contradicted"
and the final label are left to the hand review, so final_label / final_by / note stay empty.

A code "supported" means only that a sentence containing the matched words exists; it does not
check the sense ("You will learn Kubernetes" is still quoted). That judgment is the reviewer's.

Run: .venv/bin/python reports/shortlist.py   -> shortlist/shortlist.json, shortlist/SHORTLIST.md
Tested by: tests/test_js3_shortlist.py (fake postings under tmp_path; never writes shortlist/)
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from job_agent.common.paths import Paths  # noqa: E402
from job_agent.judges.checks import CHECKS  # noqa: E402
from job_agent.judges.words import has_all_words, salaries_in, strip_html, words, years_in  # noqa: E402
from job_agent.watch import board_list  # noqa: E402

SUFFIX = "_content.json"
CLAIM_RULES = ["1b", "2", "3", "4", "5", "6"]
NAMES = {c.id: c.name for c in CHECKS}   # 1b title, 2 location, 3 skills, 4 years, 5 visa, 6 salary
NO_RELEVANT = "no relevant postings"
SUPPORTED, INSUFFICIENT = "supported", "insufficient"
# A stop ends a sentence only when space or the end follows it: résumé skills like "Node.js" hold a
# dot, and splitting on every "." cut "Node.js" in two, so its claim found no quote (2 openai
# postings in the 2026-11-24 real-data run were labeled insufficient although the JD named Node.js).
_SENTENCE = re.compile(r"[.!?](?=\s|$)|\n")
_AS = re.compile(r"^(.*) \(as (.*)\)$")   # rule 3 result item "Kubernetes (as k8s)"


def sentences(plain: str) -> list[str]:
    """Split on . ! ? (when followed by space or the end) and newlines; each piece stripped, empty
    pieces dropped. Pieces are substrings of plain."""
    return [s.strip() for s in _SENTENCE.split(plain) if s.strip()]


def first_with(phrase: str, sents: list[str]) -> str | None:
    for s in sents:
        if has_all_words(phrase, set(words(s))):
            return s
    return None


def _extreme(sents: list[str], numbers, pick) -> str | None:
    """The first sentence holding the deciding number (largest years since FILTER v2 B2, largest salary)."""
    found = [(s, numbers(s)) for s in sents]
    found = [(s, n) for s, n in found if n]
    if not found:
        return None
    target = pick(x for _, n in found for x in n)
    return next(s for s, n in found if target in n)


def claim(rule_id: str, text: str, quote: str | None) -> dict:
    return {"rule": rule_id, "claim": text, "label": SUPPORTED if quote else INSUFFICIENT,
            "quote": quote or None, "label_by": "code", "final_label": "", "final_by": "", "note": ""}


def _match(result: str) -> str:
    return result[len("match: "):] if result.startswith("match: ") else ""


def claims_for(entry: dict, plain: str) -> list[dict]:
    """Claims for rules 1b-6 from the justification lines (same order as CHECKS); rule 1a gets none."""
    results = {c.id: line["result"] for c, line in zip(CHECKS, entry.get("justification") or [])}
    sents = sentences(plain)
    out = []
    for rid in CLAIM_RULES:
        result = results.get(rid, "")
        skipped = result.startswith("skipped:")
        if rid == "1b":
            hit = _match(result)
            title = entry.get("title") or ""
            out.append(claim(rid, f"The title is an engineering role Aarav targets ({hit})",
                             title.strip() if hit and title.strip() else None))
        elif rid == "2":
            hit = _match(result)
            loc = (entry.get("location") or "").strip()
            if skipped or not hit:
                out.append(claim(rid, "The job location is in the US", None))
            else:
                out.append(claim(rid, f"The job is in the US ({hit})", loc or None))
        elif rid == "3":
            items = result.split(": ", 1)[1].split(", ") if ": " in result else []
            for item in items:
                m = _AS.match(item)
                kw, spelling = (m.group(1), m.group(2)) if m else (item, item)
                out.append(claim(rid, f"The JD asks for {kw}, which Aarav has", first_with(spelling, sents)))
        elif rid == "4":
            quote = None if skipped else _extreme(sents, years_in, max)
            out.append(claim(rid, "The JD requires at most 4 years of experience", quote))
        elif rid == "5":
            # "no phrase found" means the JD doesn't refuse, but not mentioned is not "will sponsor".
            out.append(claim(rid, "The JD does not refuse visa sponsorship", None))
        elif rid == "6":
            quote = None if skipped else _extreme(sents, salaries_in, max)
            out.append(claim(rid, "The pay reaches $75,000", quote))
    return out


def summary(entry: dict, claims: list[dict]) -> str:
    names = []
    for c in claims:
        if c["label"] == INSUFFICIENT and NAMES[c["rule"]] not in names:
            names.append(NAMES[c["rule"]])
    return f"{entry['verdict']} — insufficient: {', '.join(names) if names else 'none'}"


class JDs:
    """Raw files parsed once each; the adapter is picked from data/boards.json by <board>_content.json."""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.boards = board_list.load(Paths().boards)
        self.cache: dict[Path, dict[str, str]] = {}

    def plain(self, raw_file: str, posting_id) -> str:
        path = Path(raw_file)
        if not path.is_absolute():
            path = self.repo_root / path
        if path not in self.cache:
            board = board_list.find(self.boards, path.name[: -len(SUFFIX)])
            self.cache[path] = {str(p.id): p.content for p in board.adapter.parse(path.read_bytes())}
        return strip_html(self.cache[path].get(str(posting_id), ""))


def _cell(text) -> str:
    return "—" if text is None else str(text).replace("|", "\\|").replace("\n", " ")


def shortlist_md(postings: list[dict], source: str) -> str:
    lines = ["# Shortlist", "",
             f"Kept postings from `{source}`. Labels are proposed by code (supported / insufficient);",
             "contradicted and the final label are left to the hand review (FILTER.md section 2).", ""]
    if not postings:
        return "\n".join(lines + [f"{NO_RELEVANT.capitalize()}: {NO_RELEVANT} in this audit.", ""])
    for p in postings:
        lines += [f"## {p['title']}", "",
                  f"- board: {p['board']}", f"- posting id: {p['posting_id']}", f"- url: {p['url']}",
                  f"- filter verdict: {p['verdict']}", f"- summary: {p['summary']}", "",
                  "| claim | code label | quote |", "|---|---|---|"]
        lines += [f"| {_cell(c['claim'])} | {c['label']} | {_cell(c['quote'])} |" for c in p["claims"]]
        lines.append("")
    return "\n".join(lines)


def run(audit_dir: Path, out_dir: Path, repo_root: Path = ROOT) -> int:
    audit_file = Path(audit_dir) / "all_verdicts.json"
    doc = json.loads(audit_file.read_text(encoding="utf-8"))
    kept = [e for e in doc.get("postings", []) if e.get("verdict") == "relevant" and e.get("status") == "ok"]
    jds = JDs(repo_root) if kept else None
    postings = []
    for e in kept:
        claims = claims_for(e, jds.plain(e["raw_file"], e["posting_id"]))
        postings.append({"board": e["board"], "posting_id": e["posting_id"], "title": e["title"],
                         "location": e["location"], "url": e["url"], "verdict": e["verdict"],
                         "summary": summary(e, claims), "claims": claims})
    data = {"postings": postings}
    if not postings:
        data["message"] = NO_RELEVANT
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "shortlist.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "SHORTLIST.md").write_text(shortlist_md(postings, audit_file.name), encoding="utf-8")
    print(f"{len(postings)} relevant postings -> {out_dir}" if postings else NO_RELEVANT)
    return 0


def main() -> None:
    sys.exit(run(ROOT / "audit", ROOT / "shortlist"))


if __name__ == "__main__":
    main()
