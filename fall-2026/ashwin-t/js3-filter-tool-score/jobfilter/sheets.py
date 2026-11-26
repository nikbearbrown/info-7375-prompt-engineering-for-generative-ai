"""Blind labeling sheets: what Ashwin reads to give a hand verdict, without any filter output.

A sheet shows the posting's own fields and full text only. The filter's decision, score and
reasons are kept in a separate key file and are never written into the sheet.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .text import normalize

QUESTION = "Would Supriya Sharma (fictional new-grad backend/software engineer, Boston or remote-US) want to see this posting?"
VERDICTS = "Y = yes, show it · N = no · ? = cannot tell from the posting"


def locations(p: dict) -> list:
    out = [p["location"]["name"]] if p["location"].get("name") else []
    return out + [o["name"] for o in p.get("offices") or [] if o["name"] not in out]


def write_sheet(path: Path, title: str, intro: str, postings: list) -> None:
    lines = [f"# {title}", "", intro, "", f"**Question:** {QUESTION}", "",
             f"**Verdicts:** {VERDICTS}", "",
             f"Write each verdict in `{path.with_suffix('.csv').name}` (column `verdict`, optional `note`).", ""]
    for i, p in enumerate(postings, 1):
        text = normalize(p["content"])
        lines += [f"## {i:02d}. {p['title']}", "",
                  f"- key: `{p['key']}`",
                  f"- board: {p['provider']}/{p['board']}",
                  f"- locations: {'; '.join(locations(p)) or '(none given)'}",
                  f"- url: {p['absolute_url']}", "",
                  "<details><summary>Full posting text (normalized)</summary>", "",
                  text, "", "</details>", ""]
    path.write_text("\n".join(lines) + "\n")
    with path.with_suffix(".csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "key", "title", "verdict", "note"])
        for i, p in enumerate(postings, 1):
            w.writerow([i, p["key"], p["title"], "", ""])


def read_verdicts(csv_path: Path, allow_blank: bool = False) -> dict:
    """key -> {"verdict": Y|N|?, "note": str}. Raises on an invalid verdict, and on a blank one unless
    allow_blank (then the row is left out: not judged, never treated as a verdict)."""
    out = {}
    with Path(csv_path).open(newline="") as fh:
        for row in csv.DictReader(fh):
            v = (row.get("verdict") or "").strip().upper()
            if allow_blank and not v:
                continue
            if v not in {"Y", "N", "?"}:
                raise ValueError(f"{csv_path}: row {row.get('n')} ({row.get('key')}) has verdict {v!r}")
            out[row["key"]] = {"verdict": v, "note": (row.get("note") or "").strip()}
    return out
