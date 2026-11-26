"""Every shortlist claim with its quote, the checker's label and my hand label; both answers per posting.

    python -B scripts/shortlist_report.py --version v1.0
Writes out/shortlist/<version>/claims_table.md. My labels come from labels/claim_checks_<version>.csv;
under FILTER.md E4 they stand where they differ from the checker's.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent3 import claims as cl, policy  # noqa: E402


def cell(s: str, n: int = 160) -> str:
    s = " ".join((s or "").split()).replace("|", "/")
    return s if len(s) <= n else s[:n - 1] + "…"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1.0")
    a = ap.parse_args()
    run = json.loads((policy.OUT / "shortlist" / a.version / "run.json").read_text(encoding="utf-8"))
    with (ROOT / "labels" / f"claim_checks_{a.version}.csv").open(encoding="utf-8", newline="") as f:
        mine = {int(r["k"]): r for r in csv.DictReader(f)}
    lines = [f"# Every shortlist claim ({a.version}), labeled", "",
             "`checker` = a fresh Claude session given only the posting text and the claims (prompts/check_v1.md), after the "
             "code's verbatim check. `mine` = my blind hand check (labels/claim_checks_v1.0.csv), which under E4 stands.", ""]
    k = 0
    for rank, pid in enumerate(run["shortlist"], 1):
        rec = run["records"][pid]
        labs_mine = []
        rows = []
        for cm in rec["claims"]:
            k += 1
            m = mine[k]
            labs_mine.append({**cm, "label": m["my_label"]})
            rows.append(f"| {k} | {cm['kind']} | {cell(cm['claim'])} | {cell(cm['quote'], 120) or '*(no quote)*'} | "
                        f"{cm['label']} | {m['my_label']} | {cell(cm.get('why', ''), 110)} |")
        ans_mine = cl.answer(rec["filter"], labs_mine)
        lines += [f"## {rank}. {rec['title']} ({rec['board']})", f"`{pid}` · {rec['url']}", "",
                  f"- answer with the checker's labels: **{rec['answer']['answer']}** ({rec['answer']['rule']}: {rec['answer']['why']})",
                  f"- answer with my labels (E4, in force): **{ans_mine['answer']}** ({ans_mine['rule']}: {ans_mine['why']})", "",
                  "| # | kind | claim | quote | checker | mine | checker's reason |", "|---|---|---|---|---|---|---|"] + rows + [""]
    policy.write_bytes(policy.OUT / "shortlist" / a.version / "claims_table.md", ("\n".join(lines) + "\n").encode("utf-8"))
    print(f"{k} claims -> out/shortlist/{a.version}/claims_table.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
