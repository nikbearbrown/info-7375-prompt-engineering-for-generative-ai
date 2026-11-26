"""After Saloni has labelled both sheets: compute everything and write it into the write-ups.

    python3 scripts/finish.py

Refuses to run while any audit or held-out row is unlabelled. It never writes a label.
It writes, from labels/*_sheet.csv and the committed run files:
  - out/audit_report.json, out/experiments/measure-audit.json, out/experiments/measure-heldout.json
  - AUDIT.md section 2 (hand verdicts) and the Dev result / Decision columns of section 4
  - FILTER.md section 6 (one changelog row recording C1-C3 as added or rejected)
  - SCORE.md section 3 (every variant against held-out labels)
  - the two [Saloni] counts in SIGNOFF.md
Re-running it rewrites the same blocks (between <!-- finish.py --> markers), so it is safe to repeat.

C1-C3 decision rule (AUDIT.md section 4, written 2026-11-26 before any label existed):
  adopt a candidate only if, on the 57 dev labels, it makes fewer filter errors than v1.0 AND it
  turns no row v1.0 got right into an error. A tie is a rejection (keep the simpler v1.0).
  Rows Saloni marked cannot_tell count for neither side.
"""
import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from js3.collect import latest_snapshot, load_postings  # noqa: E402
from js3.filter import score  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "scripts"))
from experiments import filter_variants  # noqa: E402

CANDIDATES = {"F2": "C1", "F3": "C2", "F4": "C3"}


def sheet(name):
    with open(os.path.join(HERE, "labels", f"{name}_sheet.csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run(*args):
    r = subprocess.run([sys.executable, *args], cwd=HERE, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"{' '.join(args)} failed:\n{r.stderr or r.stdout}")


def jload(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as f:
        return json.load(f)


def put(path, marker, block):
    """Replace the text between <!-- finish.py:marker --> and <!-- /finish.py:marker -->."""
    full = os.path.join(HERE, path)
    with open(full, encoding="utf-8") as f:
        doc = f.read()
    a, b = f"<!-- finish.py:{marker} -->", f"<!-- /finish.py:{marker} -->"
    if a not in doc:
        sys.exit(f"{path}: marker {a} not found")
    doc = re.sub(re.escape(a) + r".*?" + re.escape(b), lambda _: f"{a}\n{block.strip()}\n{b}", doc, flags=re.S)
    with open(full, "w", encoding="utf-8") as f:
        f.write(doc)


def wrong(decision, hand):
    if hand == "cannot_tell":
        return None
    return (decision == "keep") != (hand == "worth_time")


def decide(dev):
    posts = {p["uid"]: p for p in load_postings(latest_snapshot())}
    hand = {r["uid"]: r["hand_label"] for r in dev}
    variants = filter_variants()
    base = {u: wrong(score(posts[u], variants["F0"][1])["decision"], h) for u, h in hand.items()}
    out = {}
    for f, c in CANDIDATES.items():
        cand = {u: wrong(score(posts[u], variants[f][1])["decision"], h) for u, h in hand.items()}
        b_err = sum(1 for v in base.values() if v)
        c_err = sum(1 for v in cand.values() if v)
        fixed = sorted(u for u in hand if base[u] and cand[u] is False)
        broke = sorted(u for u in hand if base[u] is False and cand[u])
        adopt = c_err < b_err and not broke
        out[c] = {"v1_errors": b_err, "errors": c_err, "fixed": fixed, "broke": broke,
                  "decision": "added" if adopt else "rejected",
                  "why": ("fewer dev errors and no new error" if adopt else
                          "would turn a correct row into an error" if broke else
                          "no fewer dev errors than v1.0 (tie = keep v1.0)")}
    return out, posts


def main():
    dev, held = sheet("audit"), sheet("heldout")
    left = sum(not r["hand_label"] for r in dev + held)
    if left:
        sys.exit(f"{left} rows still unlabelled. Run:\n  python3 scripts/label.py labels/audit_sheet.csv labels/heldout_sheet.csv")

    run("scripts/audit_report.py")
    run("scripts/experiments.py", "measure", "--sheet", "audit")
    run("scripts/experiments.py", "measure")
    rep = jload("out", "audit_report.json")
    held_m = jload("out", "experiments", "measure-heldout.json")
    dec, posts = decide(dev)
    title = lambda u: posts[u]["title"]  # noqa: E731

    # AUDIT.md section 2
    S = rep["strata"]
    rows = []
    for name in ("random_reject", "near_threshold", "random_keep"):
        s = S[name]
        ci = (f"{s['error_rate_95ci'][0]:.1%} – {s['error_rate_95ci'][1]:.1%}" if "error_rate_95ci" in s
              else "(not random: no rate)")
        rows.append(f"| {name} | {s['n']} | {s['cannot_tell']} | {s['judged']} | {s['filter_wrong']} | {ci} |")
    rr, rk = S["random_reject"], S["random_keep"]
    errs = "\n".join(f"- {e['stratum']}: **{e['title']}** — filter {e['filter']}, my label {e['hand']}, score "
                     f"{e['score']}" + (f"; note: {e['note']}" if e["note"] else "") for e in rep["errors"]) or "- none"
    split = rep["matched_word_vs_hand_label"]
    words = "\n".join(f"| `{w}` | {c.get('worth_time', 0)} | {c.get('not_worth_time', 0)} | {c.get('cannot_tell', 0)} |"
                      for w, c in list(split.items())[:12])
    put("AUDIT.md", "verdicts", f"""
Labelled by Saloni with `scripts/label.py`, blind to the filter's decision. Computed by
`scripts/audit_report.py` into `out/audit_report.json` and written here by `scripts/finish.py`.

| Stratum | n | cannot tell | judged | filter wrong (by Saloni's label) | exact 95% interval |
|---|---|---|---|---|---|
{chr(10).join(rows)}

**What the sample can honestly say.** {rr['filter_wrong']} of {rr['judged']} judged random rejects were
wrong by my label. {rr['if_this_sample_is_typical'].capitalize()}. For keeps: {rk['filter_wrong']} of
{rk['judged']} judged random keeps were wrong; {rk['if_this_sample_is_typical']}. A sample of
{rr['n']} cannot show that the filter misses "almost nothing". The near-threshold stratum was
chosen by score, so it shows where the filter is fragile and gives no rate for anything.

**Rows where the filter and I disagree:**

{errs}

**Each matched word against my labels (dev rows only; top 12 by count):**

| matched word | worth time | not worth time | cannot tell |
|---|---|---|---|
{words}
""")

    # AUDIT.md section 4 + FILTER.md section 6
    eff = {"C1": "610 score changes, 0 decision flips", "C2": "34 keeps become rejects",
           "C3": "187 score changes, 12 keeps become rejects"}
    chg = {"C1": "cut topic word `training`", "C2": "add title veto `architect`, `recruiter`",
           "C3": "R4 reads \"5+ years\" without the word \"experience\""}
    lines = []
    for c, d in dec.items():
        det = f"v1.0 {d['v1_errors']} errors → {d['errors']}; fixes {len(d['fixed'])}, breaks {len(d['broke'])}"
        if d["fixed"] or d["broke"]:
            det += " (" + "; ".join([f"fixes {title(u)}" for u in d["fixed"]] + [f"breaks {title(u)}" for u in d["broke"]]) + ")"
        lines.append(f"| {c} | {chg[c]} | {eff[c]} | {det} | **{d['decision']}**: {d['why']} |")
    put("AUDIT.md", "candidates", f"""
| Candidate | Change | Effect on all 1,651 (measured, no labels needed) | Dev result (Saloni's 57 labels) | Decision (by the rule above) |
|---|---|---|---|---|
{chr(10).join(lines)}
""")
    added = [c for c, d in dec.items() if d["decision"] == "added"]
    rejected = [c for c, d in dec.items() if d["decision"] == "rejected"]
    put("FILTER.md", "changelog", f"""
| C1–C3 | 2026-11-26 | added {', '.join(added) or 'none'}; rejected {', '.join(rejected) or 'none'} (rule fixed before labelling, AUDIT.md §4) | 57 dev labels, `out/experiments/measure-audit.json` | see AUDIT.md §4 | v1.1 = v1.0 + {', '.join(added) or 'nothing'}; decided, not yet run (every number here is from v1.0; SCORE.md §3 measures v1.0 and each candidate side by side) |
""")

    # SCORE.md section 3
    srows = []
    for r in held_m:
        lo, hi = r["agreement_95ci"]
        srows.append(f"| {r['variant']} | {r['changed']} | {r['agreement']} | {lo:.0%} – {hi:.0%} | "
                     f"{r['pred_cannot_tell']} | {r['hand_cannot_tell']} | {r['tp']}/{r['fp']}/{r['fn']}/{r['tn']} |")
    put("SCORE.md", "heldout", f"""
Measured once, by `python3 scripts/experiments.py measure`, against Saloni's 30 held-out labels
(`out/experiments/measure-heldout.json`). Agreement counts only rows where both gave a yes/no.
The held-out set is 15 random keeps + 15 random rejects, so it over-represents keeps compared
with all 1,651 postings: agreement here is not the filter's accuracy on all postings.

| Variant | changed | agreement | exact 95% interval | cannot tell (variant) | cannot tell (Saloni) | tp/fp/fn/tn |
|---|---|---|---|---|---|---|
{chr(10).join(srows)}

J1's prompt contains my labeling rule, so higher agreement for J1 would show the prompt was told
the answer key, not that Claude got better. With n = 30, intervals this wide overlap for most
variants; a difference smaller than the overlap is not evidence of a better variant.
""")

    # SIGNOFF.md counts
    sp = os.path.join(HERE, "SIGNOFF.md")
    with open(sp, encoding="utf-8") as f:
        s = f.read()
    s = re.sub(r"\[Saloni\] the reject audit: .*", f"the reject audit: {rr['filter_wrong']} of {rr['judged']} judged random "
               f"rejects wrong, by my hand labels (exact 95% interval {rr['error_rate_95ci'][0]:.1%} – "
               f"{rr['error_rate_95ci'][1]:.1%})", s)
    with open(sp, "w", encoding="utf-8") as f:
        f.write(s)

    print("done: AUDIT.md §2 and §4, FILTER.md §6, SCORE.md §3, SIGNOFF.md counts. Read them before signing.")


if __name__ == "__main__":
    main()
