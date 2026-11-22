"""Redact the committed transcripts, and say exactly what was redacted (transcripts/REDACTIONS.md).

1. The home directory path is replaced by "~" everywhere (it names the machine's user).
2. In Claude Code's client-side stream (claude-*-client-side.jsonl), three account fields are replaced
   by "[redacted]": total_cost_usd, credential_expires_at and rate_limit_info.
Nothing else is changed: message order, ids, methods, arguments and results stay verbatim.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = str(Path.home())
ACCOUNT_KEYS = ("total_cost_usd", "credential_expires_at", "rate_limit_info")


def scrub(obj, counts):
    if isinstance(obj, dict):
        for k in list(obj):
            if k in ACCOUNT_KEYS and obj[k] != "[redacted]":
                obj[k] = "[redacted]"
                counts[k] = counts.get(k, 0) + 1
            else:
                scrub(obj[k], counts)
    elif isinstance(obj, list):
        for x in obj:
            scrub(x, counts)


LEDGER = ROOT / "transcripts" / "redactions.json"


def main():
    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
    rows = []
    for f in sorted((ROOT / "transcripts").glob("*.jsonl")):
        text = f.read_text(encoding="utf-8")
        counts = {"home path": text.count(HOME)}
        text = text.replace(HOME, "~")
        if f.name.endswith("-client-side.jsonl"):
            out = []
            for line in text.splitlines():
                obj = json.loads(line)
                scrub(obj, counts)
                out.append(json.dumps(obj, ensure_ascii=False))
            text = "\n".join(out) + "\n"
        f.write_text(text, encoding="utf-8")
        total = ledger.setdefault(f.name, {})
        for k, v in counts.items():
            if v:
                total[k] = total.get(k, 0) + v
    LEDGER.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    lines = ["# Redactions in transcripts/", "",
             "Written by `scripts/redact_transcripts.py` (running totals in `redactions.json`). "
             "Everything else in each file is verbatim.", "",
             "| file | replaced |", "|---|---|"]
    for name in sorted(ledger):
        lines.append(f"| {name} | " + (", ".join(f"{k}: {v}" for k, v in ledger[name].items()) or "nothing") + " |")
    (ROOT / "transcripts" / "REDACTIONS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
