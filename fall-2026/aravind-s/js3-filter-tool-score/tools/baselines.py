"""Baselines for the audit and the held-out set, how far the audit's random rejects sit from the boundary, and what
the held-out draw could detect. A diagnostic, computed after the fact from committed files: it changes no rule, no
verdict and no frozen result, and it opens nothing sealed that was not already opened.

1. Baselines. On the cards Aravind judged Keep or Reject (a "?" is left out, as the scorers do), how often three
   answers match his verdict: "reject everything", "keep everything" and the filter as frozen (FILTER.md v1.0's fates,
   as the sealed answers record them). For the audit (js3/audit/2026-11-21T044414Z/) by the kit's groups, with his
   frozen verdicts (VERDICTS.md) and with the checks asked after the reveal (AFTER-REVEAL.md), as RESULTS.md reports
   them; for the held-out set (js3/heldout/2026-11-21T044414Z/) by its two pools.
2. Distance from the boundary: how many hard rules each rejected posting fails, and which, for the audit's random
   rejects and for every reject of the v1.0 filter run (js3/filter-run/2026-11-21T044414Z/verdicts.json).
3. What the held-out draw could detect: for each change X1 to X6 (js3/score/CHANGES-TO-MEASURE.md, as
   tools/heldout_experiments.py's variant() builds them), the postings of the whole run it moves (fate, score, failed
   rules, and the recommendation at cutoffs 60, 55 and 50), how many of those were in the held-out kit's two pools
   (the exclusions of tools/heldout_kit.py), how many the draw held, and the exact chance C(N - m, n) / C(N, n) that a
   uniform draw of the kit's sizes holds none of them.

Where a committed file already states a number, the tool checks it and stops if it differs: the filter's audit
agreement against tools/score_audit.py's (which rebuilds RESULTS.md), the held-out fates and verdicts against the saved
run R0.json, the pool sizes against the held-out README, the whole-run fate and score counts against whole-run.json,
and every held-out card a change moves against the saved runs' rows (js3/score/runs/2026-11-22T083619Z/). Standard
library only; no network, no model.

Usage (from the repo root):
  python3 tools/baselines.py            write js3/checks/BASELINES.md
  python3 tools/baselines.py --check    write nothing; exit 1 if the committed file is not what this rebuilds
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(TOOLS))

import audit_kit  # noqa: E402
import heldout_experiments as hx  # noqa: E402
import heldout_kit  # noqa: E402
import score_audit  # noqa: E402
from job_agent import filter as flt  # noqa: E402

RUN_ID = "2026-11-21T044414Z"
FILTER_RUN = REPO / "js3" / "filter-run" / RUN_ID
AUDIT = REPO / "js3" / "audit" / RUN_ID
HELDOUT = REPO / "js3" / "heldout" / RUN_ID
SAVED = REPO / "js3" / "score" / "runs" / "2026-11-22T083619Z"
OUT = REPO / "js3" / "checks" / "BASELINES.md"
WRITTEN = "2026-11-24"
COMMAND = "python3 tools/baselines.py"
CHANGES = ("X1", "X2", "X3", "X4", "X5", "X6")
CUTOFFS = (60, 55, 50)
POOL_NAMES = {"random kept": "kept", "random rejected": "rejected"}


def rel(path: Path) -> str:
    return Path(path).resolve().relative_to(REPO).as_posix()


def recommended(record: dict, cutoff: int) -> bool:
    """As tools/heldout_experiments.py's metrics(): kept, and scoring at or above the cutoff."""
    return record["fate"] == "kept" and record["score"] is not None and record["score"] >= cutoff


def tally(rows: list, verdict: str) -> dict:
    """On the rows whose verdict is not "?": how often each answer matches it."""
    judged = [r for r in rows if r[verdict] != "?"]
    return {"cards": len(rows), "judged": len(judged),
            "reject_all": sum(1 for r in judged if r[verdict] == "Reject"),
            "keep_all": sum(1 for r in judged if r[verdict] == "Keep"),
            "filter": sum(1 for r in judged if (r["fate"] == "kept") == (r[verdict] == "Keep"))}


def none_drawn(population: int, moved: int, drawn: int) -> Fraction:
    """The exact chance that a uniform draw of `drawn` from `population` holds none of `moved` given postings."""
    return Fraction(math.comb(population - moved, drawn), math.comb(population, drawn))


def listing(items: list) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def postings(n: int) -> str:
    return f"{n} moved posting" + ("" if n == 1 else "s")


def card_list(cards: list) -> str:
    return ("card " if len(cards) == 1 else "cards ") + ", ".join("%02d" % n for n in cards)


def percent(chance: Fraction) -> str:
    value = float(chance) * 100
    return f"{value:.1f}%" if value >= 0.1 or value == 0 else f"{value:.4f}%"


def in_words(chance: Fraction) -> str:
    if chance >= Fraction(1, 2):
        return "more likely than not"
    if chance >= Fraction(1, 5):
        return "quite possible"
    if chance >= Fraction(1, 20):
        return "possible"
    return "unlikely"


def only_the_cutoff_differs(base: dict, variant: dict) -> bool:
    rest = lambda r: {k: v for k, v in r.items() if k != "ranking"}  # noqa: E731
    rank = lambda r: {k: v for k, v in r["ranking"].items() if k != "shortlist_min"}  # noqa: E731
    return rest(base) == rest(variant) and rank(base) == rank(variant)


def audit_part() -> dict:
    s = score_audit.score(AUDIT, FILTER_RUN)  # checks the sealed hash against SAMPLE.md; reads, writes nothing
    after = score_audit.read_after_reveal(AUDIT / "AFTER-REVEAL.md")
    rows = [{"card": r["card"], "group": r["group"], "fate": r["fate"], "frozen": r["his"],
             "after": after[r["card"]][0] if r["card"] in after else r["his"], "failed_rules": r["failed_rules"]}
            for r in s["rows"]]
    frozen = tally(rows, "frozen")
    if frozen["filter"] != sum(1 for r in s["rows"] if r["outcome"] == "agree"):
        raise SystemExit("STOP: the filter's agreement differs from tools/score_audit.py's")
    return {"digest": s["digest"], "rows": rows, "after": after}


def heldout_part() -> dict:
    raw = (HELDOUT / "sealed" / "answers.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if f"`{digest}`" not in (HELDOUT / "README.md").read_text(encoding="utf-8"):
        raise SystemExit("STOP: the held-out answers do not match the SHA-256 their README published")
    verdicts = score_audit.read_verdicts(HELDOUT / "VERDICTS.md")
    rows = [{"card": a["card"], "key": (a["board"], a["id"]), "pool": POOL_NAMES[a["pool"]], "fate": a["fate"],
             "his": verdicts[a["card"]][0]} for a in json.loads(raw.decode("utf-8"))["answers"]]
    r0 = json.loads((SAVED / "R0.json").read_text(encoding="utf-8"))["rows"]
    if sorted((r["card"], r["fate"], r["his"]) for r in r0) != sorted((r["card"], r["fate"], r["his"]) for r in rows):
        raise SystemExit("STOP: the held-out answers and verdicts differ from the saved baseline run R0.json")
    return {"digest": digest, "rows": rows}


def boundary_part(records: list, audit_rows: list) -> dict:
    groups = {"random": [r["failed_rules"] for r in audit_rows if r["group"] == "random reject"],
              "all": [r["failed_rules"] for r in records if r["fate"] == "rejected"]}
    out = {}
    for name, lists in groups.items():
        out[name] = {"n": len(lists), "by_count": collections.Counter(len(f) for f in lists),
                     "at_all": {k: sum(1 for f in lists if k in f) for k in flt.HARD_RULES},
                     "only": {k: sum(1 for f in lists if f == [k]) for k in flt.HARD_RULES},
                     "r4": sum(1 for f in lists if "R4" in f), "two_plus": sum(1 for f in lists if len(f) >= 2),
                     "near": sum(1 for f in lists if len(f) == 1 and f != ["R4"])}
    near = [r for r in audit_rows if r["group"] == "random reject" and len(r["failed_rules"]) == 1
            and r["failed_rules"] != ["R4"]]
    out["near_judged"] = [r for r in near if r["frozen"] != "?"]
    out["near_misses"] = sum(1 for r in near if r["frozen"] == "Keep")
    out["close_one_rule"] = sum(1 for r in audit_rows if r["group"] == "close call: failed one rule")
    out["kept_from_card"] = [r for r in audit_rows if r["group"] == "random reject" and r["frozen"] == "Keep"]
    return out


def power_part(data: dict, heldout_rows: list) -> dict:
    records = data["records"]
    base = {(r["board"], r["id"]): r for r in records}
    audit_answers = json.loads((AUDIT / "sealed" / "answers.json").read_text(encoding="utf-8"))["answers"]
    audit_keys = {(a["board"], a["id"]) for a in audit_answers}
    short_keys = {(k["board"], k["id"]) for k in data["shortlist"]}
    excluded = heldout_kit.left_out(records, audit_keys | short_keys)
    pools = {p: {k for k, r in base.items() if r["fate"] == p and k not in excluded} for p in heldout_kit.POOLS}
    sizes = {"kept": heldout_kit.N_KEPT, "rejected": heldout_kit.N_REJECTED}
    drawn = {r["key"]: r["card"] for r in heldout_rows}
    for p in heldout_kit.POOLS:  # the kit's own numbers: the pools it drew from and what it drew
        if sum(1 for r in heldout_rows if r["pool"] == p) != sizes[p] or not {r["key"] for r in heldout_rows
                                                                            if r["pool"] == p} <= pools[p]:
            raise SystemExit(f"STOP: the held-out {p} pool is not what tools/heldout_kit.py drew from")
    readme = (HELDOUT / "README.md").read_text(encoding="utf-8")
    for p in heldout_kit.POOLS:
        if f"| {len(pools[p])} | {sizes[p]} |" not in readme:
            raise SystemExit(f"STOP: the {p} pool has {len(pools[p])} postings, not what the held-out README says")
    rules = flt.load_rules(version=data["meta"]["filter_version"])
    profile = flt.load_profile()
    postings = {k: p for k, (p, _) in audit_kit.saved_postings(data).items()}
    whole = json.loads((SAVED / "whole-run.json").read_text(encoding="utf-8"))
    saved = {name: {r["card"]: r for r in json.loads((SAVED / f"{name}.json").read_text(encoding="utf-8"))["rows"]}
             for name in ("R0",) + CHANGES}
    out = {}
    for name in CHANGES:
        variant = hx.variant(rules, name)
        own = variant["ranking"]["shortlist_min"]
        cutoff_only = only_the_cutoff_differs(rules, variant)
        if cutoff_only:  # judge() reads no shortlist_min, so the fates and scores are v1.0's; whole-run.json agrees
            new = base
        else:
            new = {k: flt.judge(p, profile, variant, k[0]) for k, p in postings.items()}
        moved = {"fate": {k for k in base if new[k]["fate"] != base[k]["fate"]},
                 "score": {k for k in base if new[k]["score"] != base[k]["score"]},
                 "failed rules": {k for k in base if (new[k]["failed_rules"], new[k]["deciding_rule"])
                                  != (base[k]["failed_rules"], base[k]["deciding_rule"])}}
        if (len(moved["fate"]), len(moved["score"])) != (whole[name]["fates"], whole[name]["scores"]):
            raise SystemExit(f"STOP: {name} moves other fates or scores than js3/score/runs/.../whole-run.json says")
        if cutoff_only:
            moved[f"recommended at {own}"] = {k for k in base if recommended(new[k], own) != recommended(base[k], 60)}
        else:
            for c in CUTOFFS:
                moved[f"recommended at {c}"] = {k for k in base if recommended(new[k], c) != recommended(base[k], c)}
        for k, card in drawn.items():  # the held-out cards in each set must be the ones the saved runs show moving
            b, x = saved["R0"][card], saved[name][card]
            shown = {"fate": b["fate"] != x["fate"], "score": b["score"] != x["score"],
                     "failed rules": (b["failed_rules"], b["deciding_rule"]) != (x["failed_rules"], x["deciding_rule"])}
            for measure, changed in moved.items():
                if measure.startswith("recommended at "):
                    c = int(measure.rsplit(" ", 1)[1])
                    shown[measure] = recommended(x, c) != recommended(b, 60 if cutoff_only else c)
                if (k in changed) != shown[measure]:
                    raise SystemExit(f"STOP: {name}, {measure}: held-out card {card} differs from the saved runs")
        rows = []
        for measure, keys in moved.items():
            m = {p: len(keys & pools[p]) for p in heldout_kit.POOLS}
            chance = Fraction(1)
            for p in heldout_kit.POOLS:
                chance *= none_drawn(len(pools[p]), m[p], sizes[p])
            factors = [f"C({len(pools[p]) - m[p]}, {sizes[p]}) / C({len(pools[p])}, {sizes[p]})"
                       for p in heldout_kit.POOLS if m[p]]
            rows.append({"measure": measure, "run": len(keys), "pool": m, "chance": chance, "factors": factors,
                         "cards": sorted(card for k, card in drawn.items() if k in keys)})
        out[name] = {"rows": rows, "cutoff_only": cutoff_only, "own": own}
    return {"pools": {p: len(v) for p, v in pools.items()}, "sizes": sizes, "changes": out}


def render() -> str:
    data = json.loads((FILTER_RUN / "verdicts.json").read_text(encoding="utf-8"))
    audit = audit_part()
    held = heldout_part()
    boundary = boundary_part(data["records"], audit["rows"])
    power = power_part(data, held["rows"])
    fates = collections.Counter(r["fate"] for r in data["records"])
    lines = [f"Computed by Claude Code on {WRITTEN} from committed files, after the fact. Not a new measurement. "
             f"Rebuild: `{COMMAND}` from the repo root (`--check` compares without writing).", "",
             "# Baselines, distance from the boundary, and what the held-out draw could detect", "",
             "A diagnostic. It changes no rule, no verdict and no frozen result, and it opens nothing sealed that was "
             "not already open: the audit's answers were opened on 2026-11-22 (`js3/audit/" + RUN_ID + "/RESULTS.md`), "
             "the held-out answers on 2026-11-22 for the one measurement (`js3/heldout/" + RUN_ID + "/CHANGES.md`).",
             "", "Read from:", "",
             f"- `{rel(AUDIT / 'sealed' / 'answers.json')}` (SHA-256 `{audit['digest']}`, the hash `SAMPLE.md` "
             f"published), `{rel(AUDIT / 'VERDICTS.md')}`, `{rel(AUDIT / 'AFTER-REVEAL.md')}`",
             f"- `{rel(HELDOUT / 'sealed' / 'answers.json')}` (SHA-256 `{held['digest']}`, the hash `README.md` "
             f"published), `{rel(HELDOUT / 'VERDICTS.md')}`",
             f"- `{rel(FILTER_RUN / 'verdicts.json')}` (FILTER.md v{data['meta']['filter_version']}) and the saved "
             "board answers it names, checked against their SHA-256",
             f"- `{rel(SAVED)}/` (`R0.json`, `X1.json` to `X6.json`, `whole-run.json`), used as cross-checks",
             "- `FILTER.md` Section 7, version 1.0; `persona/jane-doe.json`; the changes as "
             "`tools/heldout_experiments.py` builds them", ""]
    lines += audit_section(audit, fates)
    lines += heldout_section(held)
    lines += boundary_section(boundary, fates)
    lines += power_section(power)
    return "\n".join(lines).rstrip("\n") + "\n"


def baseline_table(rows: list, groups: list, verdict: str, key: str) -> list:
    out = ["| " + ("Group" if key == "group" else "Pool") + " | Cards | Judged | Reject everything | Keep everything | "
           "The filter as frozen (v1.0) |", "|---|---:|---:|---:|---:|---:|"]
    for g in groups:
        t = tally([r for r in rows if r[key] == g], verdict)
        out.append(f"| {g} | {t['cards']} | {t['judged']} | {t['reject_all']} of {t['judged']} | "
                   f"{t['keep_all']} of {t['judged']} | {t['filter']} of {t['judged']} |")
    t = tally(rows, verdict)
    out.append(f"| **all** | **{t['cards']}** | **{t['judged']}** | **{t['reject_all']} of {t['judged']}** | "
               f"**{t['keep_all']} of {t['judged']}** | **{t['filter']} of {t['judged']}** |")
    return out


def audit_section(audit: dict, fates: collections.Counter) -> list:
    rows = audit["rows"]
    frozen, after = tally(rows, "frozen"), tally(rows, "after")
    random = tally([r for r in rows if r["group"] == "random reject"], "frozen")
    with_fate = fates["kept"] + fates["rejected"]
    kept_cards = sum(1 for r in rows if r["fate"] == "kept")
    by_card = {r["card"]: r for r in rows}
    checks = "; ".join(f"card {c:02d} from {by_card[c]['frozen']} to {v[0]}" for c, v in sorted(audit["after"].items()))
    out = ["## 1. The audit: the filter against \"reject everything\" and \"keep everything\"", "",
           "On the cards Aravind judged Keep or Reject; a \"?\" is left out, as `tools/score_audit.py` does. The "
           "filter is FILTER.md v1.0 as frozen: the fates in the sealed answers. A constant answer agrees with him "
           "wherever his verdict is that answer.", "", "His verdicts as frozen (`VERDICTS.md`, commit `45fc2c0`):", ""]
    out += baseline_table(rows, score_audit.GROUPS, "frozen", "group")
    out += ["", f"With the checks asked after the reveal (`AFTER-REVEAL.md`: {checks}), reported beside the frozen "
            "result, never in place of it, as `RESULTS.md` does:", ""]
    out += baseline_table(rows, score_audit.GROUPS, "after", "group")
    out += ["", "What this shows:", "",
            "- Inside each group the filter gives every card the same answer, because the kit drew each group by the "
            "filter's fate. So in each group it equals one of the two constant answers by construction, and a group "
            "alone cannot tell the filter from a constant.",
            f"- Over all {frozen['judged']} judged cards the filter agrees on {frozen['filter']} and \"reject "
            f"everything\" on {frozen['reject_all']} (after the reveal: {after['filter']} and {after['reject_all']}). "
            "The filter is the only one of the three answers that matches him in every group.",
            f"- The totals depend on the kit's mix, which over-draws kept postings on purpose: {kept_cards} of the "
            f"{len(rows)} cards are postings the filter kept, against {fates['kept']} of the {with_fate} postings the "
            f"run gave a fate ({fates['kept'] * 100 / with_fate:.1f}%). He marked Reject on {random['reject_all']} "
            f"of the {random['judged']} random rejects he judged, so on a uniform sample of the run \"reject "
            "everything\" would agree more often than here, and \"keep everything\" less often.", ""]
    return out


def heldout_section(held: dict) -> list:
    rows = held["rows"]
    t = tally(rows, "his")
    out = ["## 2. The held-out set (development data since 2026-11-22)", "",
           "Development data since 2026-11-22: after the one measurement, Aravind's three calls for FILTER.md v1.1 "
           "(cutoff 50, an export-control line costs 10 points, \"build systems\" dropped) used its results, so it has "
           "guided a change (`js3/heldout/" + RUN_ID + "/CHANGES.md`). These numbers describe the set; they are not "
           "an independent test of v1.1.", "",
           "On the cards he judged Keep or Reject, his verdicts as frozen (`VERDICTS.md`, commit `1e2b1e1`); the "
           "filter is v1.0 as frozen (the fates in the sealed answers, the same as the saved run `R0.json`):", ""]
    out += baseline_table(rows, list(heldout_kit.POOLS), "his", "pool")
    out += ["", f"The pools were drawn equally ({heldout_kit.N_KEPT} kept, {heldout_kit.N_REJECTED} rejected), so the "
            f"constant answers score {t['reject_all']} and {t['keep_all']} of {t['judged']} because of that design, "
            "and again each pool alone cannot tell the filter from a constant.", ""]
    return out


def boundary_section(b: dict, fates: collections.Counter) -> list:
    r, a = b["random"], b["all"]
    with_fate = fates["kept"] + fates["rejected"]
    out = ["## 3. How far the audit's random rejects sit from the boundary", "",
           "Distance here is the number of hard rules a rejected posting fails (every rule runs on every posting, "
           f"`verdicts.json`). The v1.0 run gave {with_fate} postings a fate: {fates['rejected']} rejected "
           f"({fates['rejected'] * 100 / with_fate:.1f}%) and {fates['kept']} kept. The audit's {r['n']} random "
           f"rejects are a uniform sample of the {a['n']} rejects.", "",
           f"| Hard rules failed | Audit random rejects ({r['n']}) | All rejects of the run ({a['n']}) |",
           "|---:|---:|---:|"]
    for n in sorted(set(r["by_count"]) | set(a["by_count"])):
        out.append(f"| {n} | {r['by_count'].get(n, 0)} | {a['by_count'].get(n, 0)} |")
    out += ["", "| Rule | Random rejects failing it | All rejects failing it | Random rejects failing only it | "
            "All rejects failing only it |", "|---|---:|---:|---:|---:|"]
    for k in flt.HARD_RULES:
        out.append(f"| {k} {flt.RULE_NAMES[k]} | {r['at_all'][k]} | {a['at_all'][k]} | {r['only'][k]} | "
                   f"{a['only'][k]} |")
    n_near, k_near = len(b["near_judged"]), b["near_misses"]
    bound = score_audit.upper_bound(k_near, n_near) if n_near else None
    out += ["", f"- **{r['r4']} of the {r['n']} random rejects fail R4** (the title names no software engineering "
            f"role, or names an excluded one), and **{r['two_plus']} fail two or more rules**. Over all {a['n']} "
            f"rejects: {a['r4']} fail R4 ({a['r4'] * 100 / a['n']:.1f}%) and {a['two_plus']} fail two or more "
            f"({a['two_plus'] * 100 / a['n']:.1f}%).",
            f"- Near the boundary means an engineering title (it passes R4) that fails exactly one other rule: "
            f"{a['near']} of the {a['n']} rejects ({a['near'] * 100 / a['n']:.1f}%), and {r['near']} of the "
            f"{r['n']} random rejects."]
    if bound is not None:
        cards = listing(["%02d (%s)" % (x["card"], x["failed_rules"][0]) for x in b["near_judged"]])
        out.append(f"- So the clean result on the random rejects is mostly a result on easy rejects. The random "
                   f"rejects near the boundary are {'card' if n_near == 1 else 'cards'} {cards}: {k_near} misses in "
                   f"{n_near} judged, which bounds the "
                   f"miss share among those {a['near']} postings only at {bound * 100:.1f}% (the exact one-sided 95% "
                   f"upper bound, `upper_bound()` in `tools/score_audit.py`). The audit's {b['close_one_rule']} close "
                   "calls that failed one rule were drawn one per rule, then at random, so they are not a uniform "
                   "sample and give no rate.")
    for card in b["kept_from_card"]:
        rules = " and ".join(card["failed_rules"])
        out.append(f"- Rule counts measure distance by the filter's own rules, not by his judgment: card "
                   f"{card['card']:02d} failed {len(card['failed_rules'])} rules ({rules}), and he kept it from the "
                   "card he saw.")
    return out + [""]


def power_section(p: dict) -> list:
    pools, sizes = p["pools"], p["sizes"]
    keep = " to ".join(n for n in (CHANGES[0], [n for n, c in p["changes"].items() if not c["cutoff_only"]][-1]))
    cut = " and ".join(n for n, c in p["changes"].items() if c["cutoff_only"])
    out = ["## 4. What the held-out draw could detect", "",
           f"The held-out kit drew {sizes['kept']} postings from a pool of {pools['kept']} kept and "
           f"{sizes['rejected']} from a pool of {pools['rejected']} rejected (the audit's postings, the shortlist and "
           "their same-title copies left out, as `tools/heldout_kit.py` does). For each change, the postings of the "
           "whole run it moves "
           "against v1.0, judged by the filter with the change: its fate, its score, its failed rules, or whether it "
           f"is recommended (kept and at or above the cutoff). {keep} keep the cutoff, so their recommendation is "
           f"compared at each of 60, 55 and 50; {cut} are the cutoff, so v1.0 at 60 is compared with the change "
           "at its own cutoff (their fates and scores are v1.0's: the tool checks that only the cutoff differs, and "
           "`whole-run.json` records 0 and 0 for both).", "",
           "| Change | Fates | Scores | Failed rules | Recommended at 60 | At 55 | At 50 |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    for name, c in p["changes"].items():
        got = {row["measure"]: row["run"] for row in c["rows"]}
        cells = []
        for cut in CUTOFFS:
            key = f"recommended at {cut}"
            if key in got:
                cells.append(f"{got[key]}" + (" (v1.0 at 60 against this cutoff)" if c["cutoff_only"] else ""))
            else:
                cells.append("n/a")
        out.append(f"| {name} | {got['fate']} | {got['score']} | {got['failed rules']} | " + " | ".join(cells) + " |")
    out += ["", f"Where a change moved anything, how much of it the draw could reach. The chance is exact: "
            f"C(N - m, n) / C(N, n) for each pool that holds moved postings, multiplied, with N the pool, m the moved "
            f"postings in it and n the kit's draw from it ({sizes['kept']} kept, {sizes['rejected']} rejected).", "",
            f"| Change | What moved | In the run | In the kept pool ({pools['kept']}) | In the rejected pool "
            f"({pools['rejected']}) | In the held-out draw | Chance a uniform draw holds none |",
            "|---|---|---:|---:|---:|---|---|"]
    for name, c in p["changes"].items():
        for row in c["rows"]:
            if not row["run"]:
                continue
            m, ch = row["pool"], row["chance"]
            exact = f" = {ch.numerator}/{ch.denominator}" if max(len(str(ch.numerator)), len(str(ch.denominator))) \
                <= 12 else ""
            formula = " x ".join(row["factors"]) + exact if row["factors"] else "1 (nothing in the pools)"
            held = f"{len(row['cards'])} ({card_list(row['cards'])})" if row["cards"] else "0"
            out.append(f"| {name} | {row['measure']} | {row['run']} | {m['kept']} | {m['rejected']} | {held} | "
                       f"{formula}: {percent(ch)} |")
    out += ["", "What each result could show:", ""]
    for name, c in p["changes"].items():
        rows = [row for row in c["rows"] if row["run"]]
        if not rows:
            out.append(f"- **{name}** moved nothing in the whole run by any of these measures, so no draw could show "
                       "it: \"no card changes\" is certain, not a sample result.")
            continue
        reach = lambda row: row["pool"]["kept"] + row["pool"]["rejected"]  # noqa: E731
        missed = [row for row in rows if reach(row) and not row["cards"]]
        held = [row for row in rows if row["cards"]]
        if missed and not held:
            out.append(f"- **{name}:** the draw held none of the postings {name} moved, so \"none moved here\" "
                       f"says little about {name}:")
        elif missed:
            out.append(f"- **{name}:** the draw held some of the postings {name} moved, and none for "
                       + listing([row["measure"] for row in missed]) + ":")
        else:
            out.append(f"- **{name}:** the draw held some of the postings {name} moved:")
        for row in rows:
            m, ch, cards = reach(row), row["chance"], row["cards"]
            if not m:
                out.append(f"  - {row['measure']}: none of the {postings(row['run'])} was in the pools, so no draw "
                           "could hold one.")
            elif not cards:
                out.append(f"  - {row['measure']}: " + ("not the one moved posting in the pools; a uniform draw "
                                                        "misses it" if m == 1 else
                                                        f"none of the {postings(m)} in the pools; a uniform draw "
                                                        "holds none of them")
                           + f" {percent(ch)} of the time ({in_words(ch)}).")
            else:
                out.append(f"  - {row['measure']}: " + (f"the one moved posting in the pools ({card_list(cards)}); "
                                                        "a draw without it" if m == 1 else
                                                        f"{len(cards)} of the {postings(m)} in the pools "
                                                        f"({card_list(cards)}); a draw with none of them")
                           + f" was {in_words(ch)} ({percent(ch)})."
                           + (f" `EXPERIMENTS.md` reports no card change for {name} because it compares fates and "
                              f"scores only; these cards' failed rules differ between the saved `R0.json` and "
                              f"`{name}.json`." if row["measure"] == "failed rules" else ""))
        measured = f"recommended at {c['own']}"
        scores = any(row["run"] for row in c["rows"] if row["measure"] == "score")
        if scores and not any(row["run"] for row in c["rows"] if row["measure"] == measured):
            out.append(f"  - {measured}, the cutoff it was measured with: no posting moves anywhere in the run, so "
                       "no draw could show a change in what is recommended there (the prediction: "
                       f"\"{hx.PREDICTIONS[name]}\").")
    out += ["", "These chances describe the draw's design (which postings a change moves on the whole run, which is "
            "development data), not his verdicts: they say how often a draw of this size would contain no posting a "
            "change moves, whatever he would say about it.", ""]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if the committed file differs")
    args = ap.parse_args(argv)
    text = render()
    if args.check:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print(f"{rel(OUT)}: {'the same as' if same else 'DIFFERENT FROM'} what the committed files rebuild")
        return 0 if same else 1
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {rel(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
