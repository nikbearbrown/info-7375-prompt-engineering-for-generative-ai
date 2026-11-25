"""Score the fresh set for FILTER.md v1.1: Aravind's committed verdicts against the sealed answers.

Checks the answer file's SHA-256 against the one README.md published before any verdict, that VERDICTS.md has a
verdict for every card, and that it is committed with no uncommitted change. Writes RESULTS.md in the kit folder and
prints a short summary. What each outcome means and Claude Code's predictions were fixed in PREDICTIONS.md (with the
numbers as constants in tools/fresh_kit.py) before any verdict, and this script was committed with the kit. Run again
on the same committed files, it writes the same bytes.

Per card it compares his verdict with three recommendations: v1.0's (cutoff 60), v1.1's (cutoff 50) and v1.1's
without the export-control penalty. A "?" is counted on its own, never as a mistake. Checks asked after the answers
are opened go in AFTER-REVEAL.md (the audit's format) and are reported beside the frozen result, never in place of it.

Usage: python3 tools/score_fresh.py js3/fresh/<run id>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import fresh_kit  # noqa: E402
from score_audit import read_after_reveal, read_verdicts, upper_bound  # noqa: E402

VERSIONS = (("v1.0", "recommended_v10"), ("v1.1", "recommended_v11"),
            ("v1.1 without the penalty", "recommended_without_penalty"))


def published_hash(readme: Path) -> str:
    m = re.search(r"SHA-256 `([0-9a-f]{64})`", readme.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit("STOP: README.md publishes no SHA-256")
    return m.group(1)


def verdicts_commit(kit: Path) -> str:
    """The commit that last changed VERDICTS.md; refused if it was never committed or has uncommitted changes."""
    def git(*args):
        done = subprocess.run(["git", "-C", str(kit), *args], capture_output=True, text=True)
        return done.stdout.strip() if done.returncode == 0 else ""
    commit = git("log", "-1", "--format=%h", "--", "VERDICTS.md")
    if not commit:
        raise SystemExit("STOP: VERDICTS.md is not committed; commit the verdicts before the answers are opened")
    if git("status", "--porcelain", "--", "VERDICTS.md"):
        raise SystemExit("STOP: VERDICTS.md has uncommitted changes")
    return commit


def tally(rows: list, verdict_of) -> dict:
    out = {}
    for s in fresh_kit.STRATA + ("all",):
        sub = [r for r in rows if s == "all" or r["stratum"] == s]
        judged = [r for r in sub if verdict_of(r) != "?"]
        t = {"cards": len(sub), "Keep": sum(1 for r in sub if verdict_of(r) == "Keep"),
             "Reject": sum(1 for r in sub if verdict_of(r) == "Reject"),
             "?": sum(1 for r in sub if verdict_of(r) == "?"), "judged": len(judged),
             "fate": sum(1 for r in judged if (r["fate"] == "kept") == (verdict_of(r) == "Keep"))}
        for name, field in VERSIONS:
            t[name] = sum(1 for r in judged if r[field] == (verdict_of(r) == "Keep"))
        out[s] = t
    return out


def predictions(t: dict) -> dict:
    a, b, c, d = (t[s] for s in fresh_kit.STRATA)
    if a["Keep"] >= fresh_kit.PREDICT_A_KEEPS:
        pa = "held"
    elif a["Keep"] > a["Reject"]:
        pa = "partly"
    else:
        pa = "not held"
    pb = "held" if b["?"] >= fresh_kit.PREDICT_B_UNSURE else ("partly" if b["?"] == 1 else "not held")
    off = (c["cards"] - c["Keep"]) + (d["cards"] - d["Reject"])
    pc = "held" if off == 0 else ("partly" if off == 1 else "not held")
    return {"A": pa, "B": pb, "controls": pc, "controls_off": off}


def score(kit: Path, require_committed: bool = True) -> dict:
    kit = Path(kit)
    answers_path = kit / "sealed" / "answers.json"
    digest = hashlib.sha256(answers_path.read_bytes()).hexdigest()
    if digest != published_hash(kit / "README.md"):
        raise SystemExit(f"STOP: sealed/answers.json has SHA-256 {digest}, not the one README.md published")
    verdicts = read_verdicts(kit / "VERDICTS.md")
    sealed = json.loads(answers_path.read_text(encoding="utf-8"))
    answers = {a["card"]: a for a in sealed["answers"]}
    missing = sorted(set(answers) - set(verdicts))
    if missing:
        raise SystemExit(f"STOP: no verdict for cards {missing}")
    commit = verdicts_commit(kit) if require_committed else "(not checked)"
    rows = []
    for card in sorted(answers):
        a, (his, note) = answers[card], verdicts[card]
        rows.append({**a, "title": a["title"].strip(), "his": his, "note": note})
    frozen = tally(rows, lambda r: r["his"])
    a = frozen["A"]
    result = {"digest": digest, "commit": commit, "rows": rows, "tally": frozen, "predictions": predictions(frozen),
              "bound_A": upper_bound(a["Reject"], a["judged"]) if a["judged"] else None, "cutoffs": sealed["cutoffs"],
              "after": None}
    after = read_after_reveal(kit / "AFTER-REVEAL.md")
    if after:
        later = tally(rows, lambda r: after[r["card"]][0] if r["card"] in after else r["his"])
        result["after"] = {"checks": after, "tally": later, "predictions": predictions(later)}
    return result


def _rec(r: dict, field: str, score_field: str) -> str:
    if r["fate"] != "kept":
        return "rejected"
    return f"{r[score_field]}, {'yes' if r[field] else 'no'}"


def _summary(t: dict, p: dict, cut: dict) -> list:
    a, b = t["A"], t["B"]
    return [
        f"- **A, the cutoff of {cut['v1.1']}:** Keep {a['Keep']}, Reject {a['Reject']}, ? {a['?']} of {a['cards']}. "
        f"v1.1's recommendation agrees with him on {a['v1.1']} of the {a['judged']} he judged, v1.0's on {a['v1.0']}. "
        f"Prediction (Keep on at least {fresh_kit.PREDICT_A_KEEPS}): **{p['A']}**.",
        f"- **B, the export-control penalty:** Keep {b['Keep']}, Reject {b['Reject']}, ? {b['?']} of {b['cards']}. "
        f"Prediction (? on at least {fresh_kit.PREDICT_B_UNSURE}): **{p['B']}**.",
        f"- **Controls (C and D):** {p['controls_off']} of {t['C']['cards'] + t['D']['cards']} off the expected "
        f"verdict. Prediction (none off): **{p['controls']}**.",
        f"- **All {t['all']['cards']} cards:** {t['all']['judged']} judged; agreement with v1.0's recommendation "
        f"{t['all']['v1.0']}, with v1.1's {t['all']['v1.1']}, with v1.1's without the penalty "
        f"{t['all']['v1.1 without the penalty']}; with the filter's keep or reject (the same in both versions) "
        f"{t['all']['fate']}."]


def write_results(kit: Path, s: dict) -> str:
    kit = Path(kit)
    t, cut = s["tally"], s["cutoffs"]
    out = [f"# Results, fresh set for FILTER.md v1.1, filter run {kit.name}", "",
           "Computed by `tools/score_fresh.py` from Aravind's verdicts in VERDICTS.md (last committed in "
           f"`{s['commit']}`, before the answers were opened) and `sealed/answers.json` (SHA-256 `{s['digest']}`, the "
           "hash README.md published before any verdict). Claude Code wrote the kit, the script and this file; the "
           "verdicts are his. What each outcome means was fixed in PREDICTIONS.md before any verdict.", "",
           "## In short", ""] + _summary(t, s["predictions"], cut)
    if s["bound_A"] is not None:
        out += ["", f"On A, v1.1 disagrees with him on {t['A']['Reject']} of {t['A']['judged']} judged cards; the "
                f"exact one-sided 95% upper bound (Clopper-Pearson) is {s['bound_A'] * 100:.1f}%. It bounds what this "
                "draw supports for that stratum of one day's saved answers, not a rate for all postings."]
    out += ["", "## By stratum", "",
            "Agreement counts are over the cards he judged Keep or Reject (a ? is counted on its own).", "",
            "| Stratum | Cards | Keep | Reject | ? | Judged | v1.0 agrees | v1.1 agrees | v1.1 without the penalty "
            "agrees | Keep or reject agrees |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for key in fresh_kit.STRATA + ("all",):
        x = t[key]
        name = "**all**" if key == "all" else f"{key}: {fresh_kit.NAMES[key]}"
        out.append(f"| {name} | {x['cards']} | {x['Keep']} | {x['Reject']} | {x['?']} | {x['judged']} | {x['v1.0']} | "
                   f"{x['v1.1']} | {x['v1.1 without the penalty']} | {x['fate']} |")
    a = s["after"]
    if a:
        out += ["", "## With the checks asked after the reveal (AFTER-REVEAL.md)", "",
                "These were asked after `sealed/answers.json` was opened, so they are reported beside the frozen result, "
                "never in place of it. VERDICTS.md is unchanged.", "",
                "| Card | Frozen verdict | After the reveal | When | Why it was asked | His words |", "|---|---|---|---|---|---|"]
        frozen = {r["card"]: r["his"] for r in s["rows"]}
        for card, (verdict, when, why, words) in sorted(a["checks"].items()):
            out.append(f"| {card:02d} | {frozen.get(card, '')} | {verdict} | {when} | {why} | {words} |")
        out += [""] + _summary(a["tally"], a["predictions"], cut)
    out += ["", "## Every card", "",
            f"Score and whether it is recommended: v1.0 (cutoff {cut['v1.0']}), v1.1 (cutoff {cut['v1.1']}), and v1.1 "
            "without the export-control penalty.", "",
            "| Card | Title | Stratum | His verdict | His note | v1.0 | v1.1 | Without the penalty |",
            "|---|---|---|---|---|---|---|---|"]
    for r in s["rows"]:
        out.append(f"| {r['card']:02d} | {r['title']} | {r['stratum']} | {r['his']} | {r['note']} | "
                   f"{_rec(r, 'recommended_v10', 'score_v10')} | {_rec(r, 'recommended_v11', 'score_v11')} | "
                   f"{_rec(r, 'recommended_without_penalty', 'score_without_penalty')} |")
    text = "\n".join(out) + "\n"
    (kit / "RESULTS.md").write_text(text, encoding="utf-8")
    return text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kit", type=Path)
    args = ap.parse_args(argv)
    s = score(args.kit)
    text = write_results(args.kit, s)
    print(f"answers hash OK ({s['digest'][:12]}...); verdicts committed in {s['commit']}")
    print(text.split("## By stratum")[0].split("## In short")[1].strip())
    print(f"wrote {args.kit / 'RESULTS.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
