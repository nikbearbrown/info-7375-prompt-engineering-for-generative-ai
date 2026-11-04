"""Summarize logs/sampling_raw/*.json per posting: verdict counts, unanimous
vs split, and the differing justifications side by side for splits.
Reads only saved files; makes no API calls. Hand labels are NOT used here.

    python3 scripts/summarize_sampling.py
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "logs" / "sampling_raw"
OUT = ROOT / "logs" / "sampling_summary.md"


def main():
    calls = defaultdict(list)
    for path in RAW_DIR.glob("*.json"):
        r = json.loads(path.read_text())
        calls[r["id"]].append(r)

    lines = ["# Sampling summary (raw repeated-call data; no hand labels)", "",
             "Every call: judge-v1, pinned model, independent stateless request.", ""]
    for pid in sorted(calls):
        rs = sorted(calls[pid], key=lambda r: r["call_n"])
        ok = [r for r in rs if r["status"] == "ok"]
        bad = [r for r in rs if r["status"] != "ok"]
        rel = sum(r["verdict"] == "relevant" for r in ok)
        notrel = sum(r["verdict"] == "not relevant" for r in ok)
        if not ok:
            spread = "NO VALID JUDGMENTS"
        elif rel and notrel:
            spread = "SPLIT"
        else:
            spread = "UNANIMOUS" + (" (among valid calls)" if bad else "")
        models = sorted({r["served_model"] for r in ok})
        lines += [f"## {pid}: {rs[0]['posting_title']}", "",
                  f"- calls: {len(rs)} (valid {len(ok)}, unavailable {len(bad)})",
                  f"- relevant: {rel}   not relevant: {notrel}   -> **{spread}**",
                  f"- served model(s): {', '.join(m for m in models if m) or 'n/a'}", ""]
        lines += ["| call | status | verdict | justification |", "|---:|---|---|---|"]
        for r in rs:
            j = (r["justification"] or r["error"] or "").replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {r['call_n']} | {r['status']} | {r['verdict'] or 'UNAVAILABLE'} | {j} |")
        if spread == "SPLIT":
            lines += ["", "**Split, side by side:**", "",
                      "| relevant | not relevant |", "|---|---|"]
            a = [r for r in ok if r["verdict"] == "relevant"]
            b = [r for r in ok if r["verdict"] == "not relevant"]
            for i in range(max(len(a), len(b))):
                cell = lambda xs: (f"call {xs[i]['call_n']}: " + xs[i]["justification"].replace("|", "\\|")) if i < len(xs) else ""
                lines.append(f"| {cell(a)} | {cell(b)} |")
        lines.append("")
    OUT.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nsaved: {OUT}")


if __name__ == "__main__":
    main()
