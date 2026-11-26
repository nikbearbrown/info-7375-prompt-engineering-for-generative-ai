"""Blind human checks added after the strict TA-style review (2026-11-25, evening).

    python3 -m jobfilter.blind_extra write     # writes the three worksheets and empty sheets (refuses to overwrite filled sheets)
    python3 -m jobfilter.blind_extra report    # writes audit/BLIND-EXTRA.md from whatever Ashwin has filled in

1. **Engineering rejects, blind.** 25 of the original 30 random rejects failed the role gate, so that audit could
   hardly find a real miss. This draws 20 *new* v1.0 development REJECTs whose title names an engineering role,
   excluding every posting in labels/audit-selection.json. Seed 20261127. Cards show the posting only: no score,
   reason or AI verdict. Sheet: labels/blind-eng-rejects-sheet.csv (verdict Y/N/? plus one reason).
2. **Claims, blind.** 15 of the 90 shortlist claims, seed 20261128, shown with quote and context but without the
   Codex label. Sheet: shortlist/claim-human-sheet.csv. The report counts agreement with the Codex label.
3. **Scores by hand.** Two postings with the rule and the raw inputs, but not the computed score. Ashwin writes the
   score in drafting/hand-score-check.csv; the report compares it with filter v1.0's.
"""
from __future__ import annotations

import csv
import json
import random
import re
import sys
from pathlib import Path

from .audit import SELECTION, wilson
from .audit_batches import CLEARANCE_RULE, card
from .claim_cards import context
from .claims import plain
from .corpus import HERE, load

ENG_TITLE = re.compile(r"\b(engineer|engineering|developer|swe)\b", re.I)
ENG_SEED, ENG_N = 20261127, 20
CLAIM_SEED, CLAIM_N = 20261128, 15
HAND_KEYS = ("greenhouse/klaviyo/8041054003", "lever/palantir/3c84af24-b7aa-483e-b2c3-e1d83494fe15")

ENG_SHEET = HERE / "labels" / "blind-eng-rejects-sheet.csv"
ENG_CARDS = HERE / "labels" / "blind-eng-rejects-cards.md"
CLAIM_SHEET = HERE / "shortlist" / "claim-human-sheet.csv"
CLAIM_CARDS = HERE / "shortlist" / "claim-human-cards.md"
HAND_SHEET = HERE / "drafting" / "hand-score-check.csv"
HAND_CARDS = HERE / "drafting" / "hand-score-check.md"
REPORT = HERE / "audit" / "BLIND-EXTRA.md"


def _decisions(version: str = "v1.0") -> list:
    return json.loads((HERE / "runs" / version / "decisions-dev.json").read_text())


def engineering_pool() -> list:
    used = set(json.loads(SELECTION.read_text())["sheet_order"])  # all 61 postings of every audit stratum
    return sorted(d["key"] for d in _decisions() if d["decision"] == "REJECT" and ENG_TITLE.search(d["title"])
                  and d["key"] not in used)


def engineering_reject_keys() -> list:
    return random.Random(ENG_SEED).sample(engineering_pool(), ENG_N)


def claim_ids() -> list:
    with (HERE / "shortlist" / "claim-sheet.csv").open(newline="", encoding="utf-8") as fh:
        ids = sorted(r["claim_id"] for r in csv.DictReader(fh))
    return random.Random(CLAIM_SEED).sample(ids, CLAIM_N)


def _filled(path: Path, column: str) -> bool:
    if not path.exists():
        return False
    with path.open(newline="", encoding="utf-8") as fh:
        return any((r.get(column) or "").strip() for r in csv.DictReader(fh))


def _write_csv(path: Path, header: list, rows: list) -> None:
    if _filled(path, header[-2]):
        raise SystemExit(f"{path.name} already has answers; refusing to overwrite")
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def write() -> None:
    by = {p["key"]: p for p in load()["postings"]}
    # 1. engineering rejects
    keys = engineering_reject_keys()
    L = ["# Blind check: 20 new engineering-titled rejects", "",
         "Each posting here was REJECTED by filter v1.0 and is not in the earlier 47-row audit. No score, reason or "
         "AI verdict is shown. For each: would Supriya want to see it? **Y / N / ?**, plus one short reason in your "
         "own words.", "", CLEARANCE_RULE, ""]
    for i, k in enumerate(keys, 1):
        L += card(100 + i, by[k])
    ENG_CARDS.write_text("\n".join(L) + "\n", encoding="utf-8")
    _write_csv(ENG_SHEET, ["n", "key", "title", "verdict", "reason"],
               [[100 + i, k, by[k]["title"], "", ""] for i, k in enumerate(keys, 1)])
    # 2. claims
    with (HERE / "shortlist" / "claim-sheet.csv").open(newline="", encoding="utf-8") as fh:
        claims = {r["claim_id"]: r for r in csv.DictReader(fh)}
    ids = claim_ids()
    L = ["# Blind check: 15 shortlist claims", "",
         "Label each claim against the posting text only. **S** = the posting supports the claim as written, "
         "**C** = the posting contradicts it, **I** = the posting does not settle it. Add one short reason. "
         "The Codex label is hidden.", ""]
    for i, cid in enumerate(ids, 1):
        r = claims[cid]
        p = by[r["key"]]
        st = p.get("structured") or {}
        ctx = context(plain(p["content"]), r["quote"]) if r["quote"] else ""
        L += [f"### H{i}. {p['title']} ({cid})", "",
              f"- **Claim:** {r['claim']}",
              f"- **Quote:** {r['quote'] or '(none: abstention)'}",
              f"- **Context:** {ctx or '(quote not located, or none)'}",
              f"- **Structured fields (not shown to Claude):** "
              f"{', '.join(f'{k} {v}' for k, v in st.items() if k in ('workplaceType', 'isRemote', 'commitment')) or 'none'}",
              f"- **Link:** {p['absolute_url']}", ""]
    CLAIM_CARDS.write_text("\n".join(x.replace("|", "/") for x in L) + "\n", encoding="utf-8")
    _write_csv(CLAIM_SHEET, ["n", "claim_id", "claim", "human_label", "reason"],
               [[f"H{i}", cid, claims[cid]["claim"], "", ""] for i, cid in enumerate(ids, 1)])
    # 3. hand scores
    dec = {d["key"]: d for d in _decisions()}
    rule = json.loads((HERE / "filters" / "v1.0.json").read_text())["weights"]
    L = ["# Hand check: compute two filter v1.0 scores yourself", "",
         "Rule (filters/v1.0.json): score = title points + topic points + location points.", "",
         f"- Title: {rule['title']} if the title has a qualifying role phrase (and passed the seniority gate).",
         f"- Topics: {rule['topic']} per distinct résumé topic group found in the text, capped at {rule['topic_cap']}. "
         "Groups: Python, Java, PostgreSQL, Redis, Docker, Kubernetes, Distributed Systems.",
         f"- Location: {rule['location_preferred']} for Boston or US-remote, {rule['location_us_other']} for another US "
         f"location, {rule['location_unresolved']} if unresolved.",
         f"- KEEP needs score ≥ {rule['threshold']} and at least {rule['min_topic_groups']} topic groups.", "",
         "Read the posting at the link (or the text below), then write the score and KEEP/REJECT in "
         "`drafting/hand-score-check.csv`. The computed score is deliberately not shown.", ""]
    for i, k in enumerate(HAND_KEYS, 1):
        p = by[k]
        L += [f"## {i}. {p['title']}", "", f"- **Location field:** {dec[k]['location']['best']['value'] if dec[k]['location'].get('best') else '(none)'}",
              f"- **Link:** {p['absolute_url']}", "", "Posting text:", "", "> " + plain(p["content"]), ""]
    HAND_CARDS.write_text("\n".join(L) + "\n", encoding="utf-8")
    _write_csv(HAND_SHEET, ["n", "key", "title", "ashwin_score", "ashwin_decision"],
               [[i, k, by[k]["title"], "", ""] for i, k in enumerate(HAND_KEYS, 1)])
    print("wrote", ENG_CARDS.name, CLAIM_CARDS.name, HAND_CARDS.name)


def _rows(path: Path) -> list:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_by() -> dict:
    return {p["key"]: p for p in load()["postings"]}


def report() -> Path:
    dec = {d["key"]: d for d in _decisions()}
    eng = [r for r in _rows(ENG_SHEET) if r["verdict"].strip()]
    counts = {v: sum(1 for r in eng if r["verdict"].strip() == v) for v in ("Y", "N", "?")}
    corrected = [r["n"] for r in eng if "correction" in r["reason"]]
    L = ["# Blind human checks added on 2026-11-25 (evening)", "",
         "Generated by `python3 -m jobfilter.blind_extra report`. Every verdict, label and score below is Ashwin's choice, "
         "recorded by Claude Code into the sheets named exactly as chosen. First answers were made with the AI labels "
         "and filter outputs hidden. Rows whose reason says \"correction\" or \"re-label\" were changed later, after "
         "TA-style reviews had discussed them, so those rows are not blind. Claude Code drew the samples, built the "
         "cards and computed the comparisons. Nothing blank was filled in.", "",
         "## 1. Twenty new engineering-titled rejects (`labels/blind-eng-rejects-sheet.csv`)", "",
         f"Answered: {len(eng)} of {ENG_N}. Y (a miss by the filter): {counts['Y']} · N: {counts['N']} · ?: {counts['?']}.", "",
         "Ashwin answered in chat through a fixed four-option form (Y new-grad backend fit / N wrong role or too senior / "
         "N location or job type / ? can't tell); each question showed the posting's title, company, location, job "
         "type, stated years and clearance text, and nothing from the filter. After two TA-style reviews pointed out "
         f"answers that contradicted their own cards or reasons, Ashwin corrected {len(corrected)} of them "
         f"({', '.join(corrected)}); each row keeps its first answer in the reason. The {len(eng) - len(corrected)} "
         "other rows are the original blind answers. The card-fact reasons were drafted by Claude Code and approved by "
         "Ashwin. Any unanswered row is left blank, not filled in.", ""]
    if eng:
        k, n, q = counts["Y"], len(eng), counts["?"]
        lo, hi = wilson(k, n)
        lo2, hi2 = wilson(k + q, n)
        pool = len(engineering_pool())
        L += ["**What a sample this size can show.**", "",
              f"- The draw is {n} of the {pool} engineering-titled v1.0 rejects outside the earlier audit sample, not "
              f"of all 750 rejects. Non-engineering rejects are not covered by it.",
              f"- {k} of {n} were judged Y (a filter miss): {k / n:.0%}, 95% Wilson interval {lo:.0%} to {hi:.0%}. "
              f"If all {q} '?' rows turned out Y, it would be {k + q} of {n}, interval {lo2:.0%} to {hi2:.0%}.",
              f"- The interval is wide: anywhere from about {lo:.0%} to {hi:.0%} of these rejects could be misses. "
              "20 postings cannot pin the miss rate down or say which rule causes most misses.",
              f"- The verdicts were quick form answers, and {len(corrected)} were corrected after review, so they are "
              "less careful than a full read of each posting, and the corrected rows are not blind.", ""]
    if eng:
        L += ["| n | Title | Filter reason | Ashwin | Reason |", "|---|---|---|---|---|"]
        for r in eng:
            L.append(f"| {r['n']} | {r['title']} | {'; '.join(dec[r['key']]['reasons'])} | **{r['verdict']}** | {r['reason']} |")
        L.append("")
        ys = [r for r in eng if r["verdict"].strip() == "Y"]
        clear = [r["n"] for r in ys if re.search(r"clearance", plain(load_by()[r["key"]]["content"]), re.I)]
        excluded = [r["n"] for r in ys if any("excluded" in x for x in dec[r["key"]]["reasons"])]
        L += ["**What this shows (computed, no judgment added).**", "",
              f"- {len(ys)} of the {len(eng)} answered rejects are Y: by these verdicts the filter missed them.",
              f"- Y rows rejected by an exclusion: {len(excluded)} ({', '.join(excluded) or 'none'}). Each was rejected by an exclusion "
              "that the approved FILTER.md asked for (forward deployed, internship, or a seniority term such as senior or sr). So these verdicts disagree with "
              "the written filter rules, not only with the code.",
              (f"- {len(clear)} Y rows ({', '.join(clear)}) mention a security clearance. Ashwin's earlier labeling "
               "rule says clearance with unknown eligibility is `?`. These verdicts are recorded as given; the "
               "conflict is left visible, not resolved." if clear else
               "- No Y row mentions a security clearance: after the corrections, every clearance posting is `?` or "
               "`N`, consistent with Ashwin's clearance rule."), ""]
    claims = {r["claim_id"]: r for r in _rows(HERE / "shortlist" / "claim-sheet.csv")}
    hum = [r for r in _rows(CLAIM_SHEET) if r["human_label"].strip()]
    agree = sum(1 for r in hum if r["human_label"].strip().upper() == claims[r["claim_id"]]["label"])
    L += ["## 2. Fifteen claims labeled blind (`shortlist/claim-human-sheet.csv`)", "",
          f"Answered: {len(hum)} of {CLAIM_N}. Agreement with the Codex label: {agree} of {len(hum)}.", ""]
    if hum:
        L += ["| n | Claim id | Ashwin | Codex | Same | Reason |", "|---|---|---|---|---|---|"]
        for r in hum:
            c = claims[r["claim_id"]]["label"]
            L.append(f"| {r['n']} | `{r['claim_id']}` | {r['human_label']} | {c} | "
                     f"{'yes' if r['human_label'].strip().upper() == c else '**no**'} | {r['reason']} |")
        L.append("")
    if hum:
        diff = [r["n"] for r in hum if r["human_label"].strip().upper() != claims[r["claim_id"]]["label"]]
        L += [f"Ashwin labeled each claim in chat from S/C/I, shown the claim, its quote and the posting facts, with "
              f"the Codex label hidden on the card. This is not fully blind: earlier the same day Ashwin had relayed all 90 "
              "Codex labels in chat. H12's first card stated a false fact (that \"relocation\" never appears; Claude "
              "Code's case-sensitive search had missed \"Relocation assistance\"); Ashwin re-labeled it with the "
              "correct fact. H13 was corrected after a second review. "
              f"Disagreements: {', '.join(diff) or 'none'}. They are recorded as given; neither label is treated as "
              "the truth. `claim-sheet.csv` still holds the Codex labels for all 90 claims.", ""]
    hand = [r for r in _rows(HAND_SHEET) if r["ashwin_score"].strip()]
    L += ["## 3. Two scores computed by hand (`drafting/hand-score-check.csv`)", ""]
    if hand:
        L += ["Ashwin applied the written rule in chat to the facts shown for each posting (title, topic words "
              "found, location), choosing among four scores; the computed score was hidden.", ""]
        L += ["| Posting | Ashwin's score | Code's score | Ashwin's decision | Code's decision |", "|---|---:|---:|---|---|"]
        for r in hand:
            d = dec[r["key"]]
            L.append(f"| {r['title']} | {r['ashwin_score']} | {d['score']} | {r['ashwin_decision']} | {d['decision']} |")
        same = sum(1 for r in hand if r["ashwin_decision"].strip() == dec[r["key"]]["decision"])
        exact = sum(1 for r in hand if r["ashwin_score"].strip() == str(dec[r["key"]]["score"]))
        parts = "; ".join(f"{r['title']}: {dec[r['key']]['components']['title']} + {dec[r['key']]['components']['topics']} + "
                          f"{dec[r['key']]['components']['location']} = {dec[r['key']]['score']}" for r in hand)
        L += ["", f"Decisions agree on {same} of {len(hand)}; scores agree on {exact} of {len(hand)}. The rule's "
              f"parts (title + topics + location) give: {parts}. Recorded as given, not corrected."]
    else:
        L.append("Not done.")
    REPORT.write_text("\n".join(x if x.startswith("|") else x for x in L) + "\n", encoding="utf-8")
    return REPORT


if __name__ == "__main__":
    {"write": write, "report": lambda: print(report())}[sys.argv[1] if len(sys.argv) > 1 else "write"]()
