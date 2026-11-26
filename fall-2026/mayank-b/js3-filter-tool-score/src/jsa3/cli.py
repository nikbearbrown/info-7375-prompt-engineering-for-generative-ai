"""JS3 commands. Every write goes through the JS2 permission policy (runs/<run-id>/ only), plus one
JS3 rule: blank hand-judgment sheets may be CREATED in labels/, audit/ or shortlist/, never overwritten,
so a command can never erase a verdict I wrote.

  python3 jsa3.py filter  --corpus runs/<fetch-run> [--config config/filter.json]
  python3 jsa3.py draw    --filter-run runs/<filter-run>        # held-out sheet (blind) + the audit draw
  python3 jsa3.py audit-sheet --filter-run runs/<filter-run>    # only after the held-out labels are committed
  python3 jsa3.py audit-summary --filter-run runs/<filter-run>  # reads my verdicts
  python3 jsa3.py boilerplate --filter-run runs/<filter-run>
  python3 jsa3.py shortlist --filter-run runs/<filter-run> --n 10 --env <path to .env> [--rerun 5]
  python3 jsa3.py measure --heldout labels/heldout-sheet.md --before runs/<a> --after runs/<b>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

from jsa import policy
from . import corpus as C, filter as F, sheets, shortlist as S, stats

ROOT = Path(__file__).resolve().parents[2]
SHEET_ROOTS = ("labels", "audit", "shortlist")


def now_id(label: str) -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ") + "-" + label


def run_write(run_id: str, rel: str, text: str):
    policy.write_text(ROOT, f"runs/{run_id}/{rel}", text, run_id=run_id)


def create_sheet(rel: str, text: str) -> Path:
    path = policy._resolve(ROOT, rel)
    if not any(policy._inside(path, policy._resolve(ROOT, r)) for r in SHEET_ROOTS):
        raise policy.PolicyError("outside-write-root", rel)
    if path.exists():
        raise policy.PolicyError("sheet-exists", f"{rel} already exists; it may hold my verdicts, so it is never overwritten")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def load_json(rel):
    return json.loads(policy.read_text(ROOT, rel))


def records_of(run_rel: str) -> list[dict]:
    return [json.loads(l) for l in policy.read_text(ROOT, f"{run_rel}/records.jsonl").splitlines() if l.strip()]


def run_id_of(run_rel: str) -> str:
    return Path(run_rel).name


def corpus_of(filter_run: str) -> dict:
    meta = load_json(f"{filter_run}/run.json")
    return C.load(policy.authorize(ROOT, meta["corpus"], "read"))


# ---- commands -------------------------------------------------------------------------------

def cmd_filter(a) -> int:
    cfg = load_json(a.config)
    corp = C.load(policy.authorize(ROOT, a.corpus, "read"))
    rid = a.run_id or now_id(f"filter-v{cfg['version']}")
    recs = [F.evaluate(p, cfg) for p in corp["postings"]]
    by = Counter((r["board"], r["verdict"]) for r in recs)
    close = sum(F.is_close_call(r, cfg) for r in recs)
    meta = {"run_id": rid, "corpus": a.corpus, "corpus_run": corp["run"], "boards": corp["boards"], "config": a.config,
            "filter_version": cfg["version"], "postings": len(recs), "close_calls": close,
            "verdicts": {f"{b} {v}": n for (b, v), n in sorted(by.items())}}
    run_write(rid, "records.jsonl", "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs))
    run_write(rid, "run.json", json.dumps(meta, indent=1))
    boards = sorted({r["board"] for r in recs})
    lines = [f"# Filter v{cfg['version']} on {corp['run']}", "", f"Postings: {len(recs)} · close calls (score {cfg['threshold_T'] - 1}): {close}", "",
             "| Board | keep | reject | cannot tell | errors |", "|---|---:|---:|---:|---|"]
    for b in boards:
        lines.append(f"| {b} | {by[(b, 'keep')]} | {by[(b, 'reject')]} | {by[(b, 'cannot_tell')]} | |")
    for b, info in corp["boards"].items():
        if "error" in info:
            lines.append(f"| {b} | — | — | — | **{info['error']}** (an error, not 0 postings) |")
    reasons = Counter(r["reason"].split(":")[0] if r["verdict"] != "keep" else "keep: " + r["reason"].split(":")[0] for r in recs)
    lines += ["", "Why (first clause of each reason):", ""] + [f"- {n} × {k}" for k, n in reasons.most_common()]
    run_write(rid, "summary.md", "\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nrun folder: runs/{rid}/")
    return 0


def cmd_draw(a) -> int:
    cfg = load_json(load_json(f"{a.filter_run}/run.json")["config"])
    seeds = load_json("config/seeds.json")
    recs = records_of(a.filter_run)
    d = sheets.draw(recs, cfg, seeds["seeds"], seeds["sizes"])
    corp = C.by_id(corpus_of(a.filter_run))
    rid = run_id_of(a.filter_run)
    key = {"seeds": seeds["seeds"], "sizes": seeds["sizes"], "pools": d["pools"],
           "H": [{"tag": f"H{i + 1:02d}", "board": r["board"], "id": r["id"], "stratum": r["stratum"]} for i, r in enumerate(d["H"])],
           "D": {part: [{"board": r["board"], "id": r["id"]} for r in rs] for part, rs in d["D"].items()}}
    run_write(rid, "draws.json", json.dumps(key, indent=1))
    head = ["# Held-out labels (BLIND): is this posting worth Priya's time?", "",
            f"Drawn by seed {seeds['seeds']['heldout']} from `{a.filter_run}` on {dt.date.today().isoformat()}: {len(d['H'])} postings, shuffled. "
            "This sheet hides the filter's verdict, score and matched words on purpose. Label from the posting alone, "
            "then commit this file before opening any audit sheet or filter output. It is used once (SCORE.md).", "",
            "Write `keep`, `reject` or `cannot tell` after **My verdict:**, and one line after **Why:**. "
            "Priya: early-career AI/ML engineer (MS Information Systems, Staples AI Engineer co-op: LangGraph agent, MLflow, LLM evaluation, Python, SQL, Databricks); "
            "Boston, or SF / NYC, or remote in the US; not senior, not an internship.", ""]
    body = [sheets.block(f"H{i + 1:02d}", r, corp.get(r["id"], {}), blind=True) for i, r in enumerate(d["H"])]
    p = create_sheet("labels/heldout-sheet.md", "\n".join(head + body))
    print(f"wrote {p.relative_to(ROOT)} (blind, {len(d['H'])} postings) and runs/{rid}/draws.json")
    print("pools:", d["pools"], "· audit parts:", {k: len(v) for k, v in d["D"].items()})
    return 0


def cmd_audit_sheet(a) -> int:
    key = load_json(f"{a.filter_run}/draws.json")
    recs = {(r["board"], r["id"]): r for r in records_of(a.filter_run)}
    corp = C.by_id(corpus_of(a.filter_run))
    meta = load_json(f"{a.filter_run}/run.json")
    tags = {"random-rejects": "R", "close-calls": "C", "kept": "K"}
    out = [f"# Reject audit, filter v{meta['filter_version']}", "",
           f"Filter run `{a.filter_run}` on corpus `{meta['corpus']}` (raw SHA-256 per board in its run.json). "
           f"Seed {key['seeds']['audit']}. Pools: {key['pools']}. Draw: {key['sizes']['audit_rejects']} uniform random rejects, "
           f"the close calls (score {load_json(meta['config'])['threshold_T'] - 1}; all, or a seeded {key['sizes']['audit_close_max']}), "
           f"{key['sizes']['audit_kept']} random kept. The held-out postings are excluded.", "",
           "For each posting: **My verdict** = what Priya should get (`keep` / `reject` / `cannot tell`), judged from the original posting. "
           "**False friend** = a word that matched for the wrong reason (for example `pipeline` meaning a sales pipeline). Claude Code never fills these lines.", ""]
    for part, rows in key["D"].items():
        out += [f"## Part: {part} ({len(rows)})", ""]
        for i, x in enumerate(rows):
            r = recs[(x["board"], x["id"])]
            out.append(sheets.block(f"{tags[part]}{i + 1:02d}", r, corp.get(r["id"], {}), blind=False))
    p = create_sheet(f"audit/reject-audit-v{meta['filter_version']}.md", "\n".join(out))
    print(f"wrote {p.relative_to(ROOT)}")
    return 0


def cmd_audit_summary(a) -> int:
    meta = load_json(f"{a.filter_run}/run.json")
    key = load_json(f"{a.filter_run}/draws.json")
    recs = {(r["board"], r["id"]): r for r in records_of(a.filter_run)}
    v = sheets.read_verdicts(policy.read_text(ROOT, a.sheet) if a.sheet.startswith("runs/") else (ROOT / a.sheet).read_text())
    lines = [f"# Reject audit summary, filter v{meta['filter_version']}", "", "Computed by `python3 jsa3.py audit-summary` from my verdicts. A row is **wrong** when my verdict differs from the filter's.", "",
             "| Part | n | judged | filter wrong | blank | wrong ids |", "|---|---:|---:|---:|---:|---|"]
    res = {}
    for part, rows in key["D"].items():
        judged = [(x, v.get((x["board"], x["id"]), {}).get("verdict")) for x in rows]
        blank = [x for x, y in judged if not y or y.startswith("INVALID")]
        wrong = [x for x, y in judged if y and not y.startswith("INVALID") and y.replace(" ", "_") != recs[(x["board"], x["id"])]["verdict"]]
        res[part] = (len(rows), len(rows) - len(blank), len(wrong))
        lines.append(f"| {part} | {len(rows)} | {len(rows) - len(blank)} | {len(wrong)} | {len(blank)} | {', '.join(x['id'] for x in wrong) or '-'} |")
    n, j, k = res.get("random-rejects", (0, 0, 0))
    if j:
        up = stats.upper_one_sided(k, j)
        lo, hi = stats.two_sided(k, j)
        lines += ["", f"**What the random sample can show.** {k} of {j} randomly drawn rejects were wrong. For this snapshot's reject pool "
                  f"({key['pools']['rejects']} rejects), the one-sided 95 % upper bound on the share the filter wrongly rejected is "
                  f"**{up:.1%}** (exact two-sided 95 % interval {lo:.1%}–{hi:.1%}). That is a statement about this one pool on this date, "
                  "not a rate for all postings and not a rate for any other board or day. The close calls and kept rows are not random "
                  "samples of anything, so they give counts, not rates."]
    run_write(run_id_of(a.filter_run), "audit-summary.md", "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


def cmd_boilerplate(a) -> int:
    meta = load_json(f"{a.filter_run}/run.json")
    cfg = load_json(meta["config"])
    corp = corpus_of(a.filter_run)
    per = {}
    for p in corp["postings"]:
        if not p.get("text"):
            continue
        b = per.setdefault(p["board"], Counter())
        b["_n"] += 1
        for w, forms in cfg["topic_words_text"].items():
            if any(F.find_term(p["text"], f) for f in forms):
                b[w] += 1
    words = list(cfg["topic_words_text"])
    lines = ["# Topic-word share per board (FILTER.md 1.6: a word in >= 90 % of one board's postings is boilerplate there)", "",
             "| Board | postings with text | " + " | ".join(words) + " |", "|---|---:|" + "---:|" * len(words)]
    flagged = []
    for b, c in sorted(per.items()):
        cells = []
        for w in words:
            share = c[w] / c["_n"]
            cells.append(f"{c[w]} ({share:.0%})" + (" **≥90 %**" if share >= 0.9 else ""))
            if share >= 0.9:
                flagged.append((b, w, c[w], c["_n"]))
        lines.append(f"| {b} | {c['_n']} | " + " | ".join(cells) + " |")
    lines += ["", "Over the 90 % line: " + (", ".join(f"`{w}` on {b} ({k}/{n})" for b, w, k, n in flagged) or "none")]
    run_write(run_id_of(a.filter_run), "boilerplate.md", "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


def cmd_shortlist(a) -> int:
    persona = load_json("persona/priya-nair.resume.json")
    recs = records_of(a.filter_run)
    key = load_json(f"{a.filter_run}/draws.json") if (ROOT / a.filter_run / "draws.json").exists() else {"H": []}
    held = {(h["board"], h["id"]) for h in key["H"]}
    picks = [r for r in S.select([r for r in recs if (r["board"], r["id"]) not in held], a.n)]
    corp = C.by_id(corpus_of(a.filter_run))
    rid = a.run_id or now_id("shortlist")
    if a.via == "api":
        env = Path(a.env).expanduser().resolve()
        call = lambda text: S.call_claude(text, env)
    else:
        call = S.call_claude_cli
    results = []
    for i, r in enumerate(picks):
        post = corp[r["id"]]
        resp = call(S.prompt(post, persona))
        stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        run_write(rid, f"responses/{i + 1:02d}-{r['id']}.json", json.dumps({"at": stamp, "model": S.MODEL, "posting": r["id"], "response": resp}, indent=1))
        results.append((r, post, S.claims_from(resp), stamp, resp.get("usage")))
        print(f"{i + 1}/{len(picks)} {r['id']} {r['title'][:60]} -> {len(results[-1][2])} claims")
    reruns = []
    for r, post, _, _, _ in results[:a.rerun]:
        resp = call(S.prompt(post, persona))
        stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        run_write(rid, f"responses/rerun-{r['id']}.json", json.dumps({"at": stamp, "model": S.MODEL, "posting": r["id"], "response": resp}, indent=1))
        reruns.append((r["id"], S.claims_from(resp)))
    out = ["# Source-grounded shortlist: claims to label", "",
           f"Filter run `{a.filter_run}`; top {a.n} kept postings by (role word in title, then score), held-out postings excluded. "
           f"Justifications by `{S.MODEL}` through {'the Messages API' if a.via == 'api' else 'the Claude Code CLI (`claude -p`, no tools)'} on the dates shown (real responses, saved in `runs/{rid}/responses/`). "
           "**Mechanical check** only says whether the quoted passage is really in the posting; it never says supported. "
           "**My label** is mine: `supported` / `contradicted` / `insufficient`, judged against the posting text.", "",
           "Abstention rule (FILTER.md 2): if C2 or C3 has no passage in the posting, the posting leaves the shortlist for the cannot-tell list.", ""]
    abstained = []
    for i, (r, post, claims, stamp, usage) in enumerate(results):
        pre = {c["id"]: S.prelabel(c, post) for c in claims}
        gone = not claims or any(pre.get(cid, "").startswith("insufficient") for cid in ("C2", "C3"))
        if gone:
            abstained.append(r["id"])
        out += [f"## S{i + 1:02d} · {r['board']} · {r['id']}{'  — ABSTAINED: moved to cannot tell' if gone else ''}", "",
                f"**{r['title']}** · {r['location']} · [original posting]({r['url']}) · filter: {r['reason']} · Claude response {stamp}", "",
                "| Claim | Claude's sentence | Passage Claude quoted | Mechanical check | **My label** | **Deciding sentence (if I disagree)** |",
                "|---|---|---|---|---|---|"]
        for c in claims:
            q = S.collapse(c.get("quote")).replace("|", "/")[:300]
            out.append(f"| {c['id']} | {S.collapse(c['claim']).replace('|', '/')} | {q or '(none)'} | {pre[c['id']]} |  |  |")
        if not claims:
            out.append("| - | (no parsable claims in the response) | | | | |")
        out.append("")
    if reruns:
        out += ["## Variation: the same prompt sent again", ""]
        first = {r["id"]: claims for r, _, claims, _, _ in results}
        for pid, claims in reruns:
            for c in claims:
                old = next((x for x in first.get(pid, []) if x["id"] == c["id"]), None)
                same = old is not None and S.collapse(old["quote"]) == S.collapse(c["quote"])
                out.append(f"- {pid} {c['id']}: quote {'unchanged' if same else 'CHANGED'}; second sentence: {S.collapse(c['claim'])}")
        out.append("")
    out += [f"Abstained (moved to cannot tell): {', '.join(abstained) or 'none'}"]
    run_write(rid, "run.json", json.dumps({"run_id": rid, "filter_run": a.filter_run, "n": a.n, "model": S.MODEL, "effort": S.EFFORT,
                                           "api_version": S.API_VERSION, "via": a.via, "calls": len(results) + len(reruns), "abstained": abstained,
                                           "usage": [u for *_, u in results]}, indent=1))
    p = create_sheet("shortlist/claims.md", "\n".join(out) + "\n")
    print(f"wrote {p.relative_to(ROOT)}; responses in runs/{rid}/responses/")
    return 0


def cmd_measure(a) -> int:
    v = sheets.read_verdicts((ROOT / a.heldout).read_text())
    labels = {k: x["verdict"] for k, x in v.items() if x["verdict"] and not x["verdict"].startswith("INVALID")}
    rows = ["| Filter run | version | agree | false keeps | false rejects | other disagreements | n |", "|---|---|---:|---:|---:|---:|---:|"]
    for run in (a.before, a.after):
        recs = {(r["board"], r["id"]): r for r in records_of(run)}
        ver = load_json(f"{run}/run.json")["filter_version"]
        agree = fk = fr = other = 0
        for k, lab in labels.items():
            got = recs[k]["verdict"].replace("_", " ")
            if got == lab:
                agree += 1
            elif got == "keep" and lab == "reject":
                fk += 1
            elif got == "reject" and lab == "keep":
                fr += 1
            else:
                other += 1
        rows.append(f"| `{run}` | {ver} | {agree} | {fk} | {fr} | {other} | {len(labels)} |")
    out = ["# Held-out measurement (used once)", "", f"Labels: `{a.heldout}` ({len(labels)} labelled, blind). "
           "False keep = the filter keeps, I said reject. False reject = the filter rejects, I said keep.", ""] + rows
    print("\n".join(out))
    if a.write:
        rid = run_id_of(a.after)
        run_write(rid, "heldout-measure.md", "\n".join(out) + "\n")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="jsa3.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("filter"); f.add_argument("--corpus", required=True); f.add_argument("--config", default="config/filter.json"); f.add_argument("--run-id")
    for name in ("draw", "audit-sheet", "boilerplate"):
        x = sub.add_parser(name); x.add_argument("--filter-run", required=True)
    s = sub.add_parser("audit-summary"); s.add_argument("--filter-run", required=True); s.add_argument("--sheet", default="audit/reject-audit-v0.1.md")
    sl = sub.add_parser("shortlist"); sl.add_argument("--filter-run", required=True); sl.add_argument("--n", type=int, default=10)
    sl.add_argument("--via", choices=("api", "claude-cli"), default="api"); sl.add_argument("--env"); sl.add_argument("--rerun", type=int, default=0); sl.add_argument("--run-id")
    m = sub.add_parser("measure"); m.add_argument("--heldout", required=True); m.add_argument("--before", required=True); m.add_argument("--after", required=True)
    m.add_argument("--write", action="store_true")
    a = p.parse_args(argv)
    try:
        return {"filter": cmd_filter, "draw": cmd_draw, "audit-sheet": cmd_audit_sheet, "audit-summary": cmd_audit_summary,
                "boilerplate": cmd_boilerplate, "shortlist": cmd_shortlist, "measure": cmd_measure}[a.cmd](a)
    except policy.PolicyError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
