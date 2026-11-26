"""Source-grounded shortlist (FILTER.md section 5). Claude writes atomic claims with exact quotes for each kept
posting. Code checks each quote mechanically. Ashwin labels every claim supported / contradicted / insufficient.

    python3 -m jobfilter.claims --run      # live Claude calls, one per kept development posting (dated, saved raw)
    python3 -m jobfilter.claims --sheet    # writes shortlist/claim-sheet.{md,csv} from the latest run

The mechanical check can only say "quote found / not found / negation present / abstained". It never says
"supported": that is a judgment (FILTER.md section 5, "Mechanical checks ... do not replace semantic judgment").
"""
from __future__ import annotations

import csv
import html
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from .corpus import HERE, load
from .filter import Filter, load_config, rank
from .sheets import locations

PROMPT = HERE / "prompts" / "claims-v1.md"
OUT = HERE / "shortlist"
ABSTAIN = "I cannot tell from this posting"
FIELDS = ("title", "location", "content")
MIN_CLAIMS, MAX_CLAIMS = 3, 5
NEGATION = re.compile(r"(?<![a-z])(not|no|never|without|n't|none|nor)(?![a-z])")
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


def plain(value: Optional[str]) -> str:
    """HTML removed, case kept: the text Claude is shown."""
    t = html.unescape(value or "")
    t = _TAG.sub(" ", t)
    return _SPACE.sub(" ", html.unescape(t)).strip()


def _match_form(text: str) -> str:
    t = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r"[‐-―]", "-", t)
    return _SPACE.sub(" ", t).strip().casefold()


def posting_view(p: dict) -> dict:
    return {"key": p["key"], "title": p["title"], "location": "; ".join(locations(p)), "content": plain(p["content"])}


def field_text(view: dict, field: str) -> str:
    return view.get(field, "")


def mechanical(claim: dict, view: dict) -> str:
    """abstained | quote-not-found | quote-found-negation (needs a human) | quote-found (needs a human)."""
    if claim["claim"].startswith(ABSTAIN):
        return "abstained"
    if _match_form(claim["quote"]) not in _match_form(field_text(view, claim["field"])):
        return "quote-not-found"
    if NEGATION.search(_match_form(claim["quote"])):
        return "quote-found-negation"
    return "quote-found"


def w7_presence_only(claim: dict, view: dict) -> str:
    """WRONG VERSION W7: any quote that is present counts as support, even "Java is not required"."""
    if claim["claim"].startswith(ABSTAIN):
        return "abstained"
    return "supported" if _match_form(claim["quote"]) in _match_form(field_text(view, claim["field"])) else "unsupported"


def validate_reply(text: str) -> tuple:
    """(claims, None) or (None, reason). Strict: JSON object only, 3-5 claims, typed fields."""
    try:
        data = json.loads(text.strip())
    except json.JSONDecodeError as exc:
        return None, f"not JSON: {exc}"
    if not isinstance(data, dict) or set(data) != {"claims"} or not isinstance(data["claims"], list):
        return None, 'expected exactly {"claims": [...]}'
    claims = data["claims"]
    if not MIN_CLAIMS <= len(claims) <= MAX_CLAIMS:
        return None, f"{len(claims)} claims; {MIN_CLAIMS}-{MAX_CLAIMS} required"
    for i, c in enumerate(claims):
        if not isinstance(c, dict) or set(c) != {"claim", "quote", "field"}:
            return None, f"claim {i} must have exactly claim, quote, field"
        if not all(isinstance(c[k], str) for k in c) or not c["claim"].strip():
            return None, f"claim {i} has a non-string or empty value"
        if c["field"] not in FIELDS:
            return None, f"claim {i} field {c['field']!r} not in {FIELDS}"
        if c["claim"].startswith(ABSTAIN) != (c["quote"] == ""):
            return None, f"claim {i}: an abstention must have an empty quote, and only an abstention may"
    return claims, None


def call_claude(prompt: str, timeout: float = 300.0, runner: Callable = subprocess.run) -> dict:
    """One fresh, tool-free Claude Code session from an empty folder (the JS1 call, unchanged in shape)."""
    called_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cmd = ["claude", "-p", "--output-format", "json", "--tools", "", "--no-session-persistence",
           "--setting-sources", "", "--strict-mcp-config"]
    with tempfile.TemporaryDirectory(prefix="js3-claude-") as empty:
        try:
            done = runner(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=empty)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"ok": False, "error": f"claude call failed: {exc}", "called_at": called_at}
    if done.returncode != 0:
        return {"ok": False, "error": f"claude exited {done.returncode}: {done.stderr.strip()[:300]}", "called_at": called_at}
    try:
        env = json.loads(done.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "claude output was not a JSON envelope", "called_at": called_at}
    if env.get("is_error"):
        return {"ok": False, "error": f"claude reported an error: {env.get('result')}", "called_at": called_at}
    return {"ok": True, "text": env.get("result", ""), "called_at": called_at,
            "model": ",".join(sorted(env.get("modelUsage") or {})), "session_id": env.get("session_id")}


def shortlist_postings() -> list:
    """The ranked KEEPs among the development postings (held-out never enters)."""
    dev = json.loads((HERE / "runs" / "v1.0" / "decisions-dev.json").read_text())
    by_key = {p["key"]: p for p in load()["postings"]}
    return [(d, by_key[d["key"]]) for d in rank(dev)]


def run(caller: Callable = call_claude) -> Path:
    template = PROMPT.read_text()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    out = OUT / f"claims-v1-{stamp}"
    (out / "raw").mkdir(parents=True)
    items = shortlist_postings()

    def one(item):
        d, p = item
        view = posting_view(p)
        prompt = template.replace("{posting}", json.dumps(view, ensure_ascii=False, indent=1))
        r = caller(prompt)
        rec = {"key": d["key"], "rank_score": d["score"], "called_at": r.get("called_at"), "model": r.get("model"),
               "ok": r["ok"], "error": r.get("error"), "reply_text": r.get("text")}
        claims, why = validate_reply(r["text"]) if r["ok"] else (None, r.get("error"))
        rec["valid"] = claims is not None
        rec["invalid_reason"] = why
        rec["claims"] = [dict(c, id=f"{d['key'].split('/')[1]}-{d['key'].split('/')[2][:8]}-c{i + 1}",
                              mechanical=mechanical(c, view)) for i, c in enumerate(claims or [])]
        (out / "raw" / (d["key"].replace("/", "__") + ".json")).write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
        return rec

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(one, items))
    (out / "results.json").write_text(json.dumps({"prompt": "prompts/claims-v1.md", "filter_version": "v1.0",
                                                 "run_started_utc": stamp, "results": results},
                                                indent=1, ensure_ascii=False) + "\n")
    return out


def latest_run() -> Path:
    runs = sorted(OUT.glob("claims-v1-*"))
    if not runs:
        raise SystemExit("no claims run yet")
    return runs[-1]


def write_sheet(run_dir: Path) -> None:
    existing = OUT / "claim-sheet.csv"
    if existing.exists() and any((r.get("label") or "").strip() for r in csv.DictReader(existing.open())):
        raise SystemExit("shortlist/claim-sheet.csv already has labels; refusing to overwrite it")
    res = json.loads((run_dir / "results.json").read_text())["results"]
    by_key = {p["key"]: p for p in load()["postings"]}
    lines = ["# Claim-labeling sheet", "",
             f"Claims Claude wrote on {res[0]['called_at'][:10]} (`{run_dir.name}`) for each kept posting. For each claim, "
             "judge it against the posting's own text (open the fold-out section) and write S, C or I in "
             "`claim-sheet.csv`:", "",
             "- **S** supported: the posting explicitly states the claim, or a faithful paraphrase of it.",
             "- **C** contradicted: the posting states something incompatible with the claim.",
             "- **I** insufficient: silent, ambiguous, or only a related word without establishing the claim.",
             "", "For an \"I cannot tell\" claim, write S if the posting really does not settle the question, and "
             "C if it does settle it (the abstention was wrong). FILTER.md section 5 has the full rules.", ""]
    rows = []
    for r in res:
        p = by_key[r["key"]]
        lines += [f"## {p['title']}", "", f"- key: `{r['key']}` · locations: {'; '.join(locations(p))}", ""]
        if not r["valid"]:
            lines += [f"**Claim generation failed** ({r['invalid_reason']}). Nothing to label; the agent abstains for "
                      "this posting.", ""]
            continue
        for c in r["claims"]:
            lines += [f"- **{c['id']}**: {c['claim']}", f"  - quote ({c['field']}): \"{c['quote']}\""]
            rows.append([c["id"], r["key"], c["claim"], c["quote"], c["field"], "", ""])
        lines += ["", "<details><summary>Posting text</summary>", "", plain(p["content"]), "", "</details>", ""]
    OUT.mkdir(exist_ok=True)
    (OUT / "claim-sheet.md").write_text("\n".join(lines) + "\n")
    with (OUT / "claim-sheet.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["claim_id", "key", "claim", "quote", "field", "label", "note"])
        w.writerows(rows)
    print(f"{len(rows)} claims from {len(res)} postings -> shortlist/claim-sheet.md, claim-sheet.csv")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--run"]:
        out = run()
        res = json.loads((out / "results.json").read_text())["results"]
        print(f"{out.name}: {len(res)} postings, {sum(r['valid'] for r in res)} valid replies")
        return 0 if all(r["ok"] for r in res) else 1
    if argv == ["--sheet"]:
        write_sheet(latest_run())
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
