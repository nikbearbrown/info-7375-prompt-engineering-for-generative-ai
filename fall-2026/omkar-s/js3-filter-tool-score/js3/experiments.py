"""What moves the score (Chapter 9): one change to one object at a time, measured on held-out labels.

    python3 -m js3.experiments lock      # freeze prompts, variants, filter and labels (sha256) BEFORE any run
    python3 -m js3.experiments run       # runs every condition on the 20 held-out postings (Claude calls are cached)
    python3 -m js3.experiments report    # writes experiments/SCORE-RESULTS.md
    python3 -m js3.experiments fit-threshold   # DEV labels only (Omkar's audit verdicts): a fitted threshold, not adopted

Held-out labels: Omkar's 20 JS1 hand labels (labels/heldout-js1/). No JS3 number was set from them.

Conditions (each differs from its baseline in exactly ONE object):
  F0  filter v1.4 as in force                         baseline for E1, E2
  E1  filter FILE: T3 seniority weight -2.0 -> 0.0     (experiments/variants/filter-E1-noT3.json)
  E2  SETTING: threshold 5.0 -> 4.0                    (experiments/variants/filter-E2-threshold4.json)
  C0  Claude, prompt P1, posting only, no tools        baseline for E3, E4, E5
  C0b C0 again, fresh sessions                         the noise floor: what changes when NOTHING changes
  E3  PROMPT: P1 + one abstention instruction (and the cannot_tell option it needs)
  E4  CONTEXT: P1 + the filter's own result for that posting (score lines and claim labels)
  E5  TOOL LIST: P1 unchanged, plus the js3-score MCP tool (score_posting) offered
Batch 2 (locked separately, after batch 1 had run; decided from the audit sample, not from these labels):
  E6  filter FILE: v1.4 -> v1.5 (explicit "N+ years" counts alone)       baseline F0
  E7  filter FILE: v1.5 -> v1.6 (sub-requirements do not set the minimum) baseline E6
"""
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

from . import data, scorer, store
from . import textutil as tu
from .js2 import persona as persona_mod

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP = "experiments"
LOCKS = {1: f"{EXP}/lock.json", 2: f"{EXP}/lock-2.json"}
MODEL = "claude-sonnet-5-5"
P1 = "prompts/judge-P1.txt"
E3_RULE = ("ABSTENTION: if the posting does not state its years requirement, or its text does not let you check "
           "one of the four conditions, answer \"cannot_tell\" instead of guessing.")
FILTERS = {"F0": "filter/filter-v1.4.json", "E1": f"{EXP}/variants/filter-E1-noT3.json",
           "E2": f"{EXP}/variants/filter-E2-threshold4.json"}
FILTERS2 = {"F0": "filter/filter-v1.4.json", "E6": "filter/filter-v1.5.json", "E7": "filter/filter-v1.6.json"}
CLAUDE_CONDS = ("C0", "C0b", "E3", "E4", "E5")
MAX_CHARS = 12000


def _sha(path):
    with open(os.path.join(BASE, path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def locked_files(batch=1):
    common = ["labels/heldout-js1/labels.csv", "labels/heldout-js1/postings-20.json",
              "persona/aarav-patel.example.json", "js3/scorer.py", "js3/textutil.py"]
    if batch == 1:
        return [P1, *FILTERS.values(), *common, "js3/mcp_server.py"]
    return [*FILTERS2.values(), *common]


def lock(batch=1):
    path = LOCKS[batch]
    if os.path.exists(os.path.join(BASE, path)):
        raise SystemExit(f"{path} exists; a new lock would hide what changed. Delete it by hand and say why in FRICTIONAL.md.")
    body = {"batch": batch, "locked_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "model": MODEL,
            "e3_rule": E3_RULE, "sha256": {p: _sha(p) for p in locked_files(batch)}}
    store.write_text(path, json.dumps(body, indent=1))
    return body


def lock_status(batch):
    """(lock, files changed since it). Never raises; the report shows the changes."""
    path = os.path.join(BASE, LOCKS[batch])
    if not os.path.exists(path):
        return None, []
    with open(path, encoding="utf-8") as f:
        lk = json.load(f)
    return lk, [p for p, h in lk["sha256"].items() if _sha(p) != h]


def check_lock(batch=1):
    """Refuse to RUN anything new for a batch whose locked files changed."""
    lk, bad = lock_status(batch)
    if lk is None:
        raise SystemExit(f"no {LOCKS[batch]}: run `python3 -m js3.experiments lock{'' if batch == 1 else ' 2'}` first")
    if bad or lk["e3_rule"] != E3_RULE:
        raise SystemExit(f"lock {batch} broken: {bad or 'E3 rule text'} changed after {lk['locked_utc']}. New runs would not be held-out.")
    return lk


def prompt_for(cond, p, persona, cfg_f0):
    with open(os.path.join(BASE, P1), encoding="utf-8") as f:
        tmpl = f.read()
    text = tu.clean(p.get("content"))[:MAX_CHARS]
    extra, ctx, ct = "", "", ""
    if cond == "E3":
        extra, ct = "\n" + E3_RULE + "\n", ' | "cannot_tell"'
    if cond == "E4":
        rec = scorer.evaluate(p, persona, cfg_f0)
        lines = [f"verdict {rec['verdict']}, score {rec['score']} (threshold {cfg_f0['threshold']})"]
        lines += [f"{l['rule']} {l['points']:+g}: {l['why']}" for l in rec["lines"]] + rec["reasons"]
        if rec["verdict"] == "keep":
            lines += [f"[{c['label']}] {c['text']}" for c in scorer.claims(p, rec, cfg_f0)]
        ctx = "\nFILTER RESULT (Omkar's JS3 filter v1.4, computed from the same posting):\n" + "\n".join(lines) + "\n"
    # E5 uses the P1 prompt unchanged: the ONLY difference is that the tool is offered (its name and
    # description reach Claude through the tool list, not through the prompt).
    return tmpl.format(persona=json.dumps(persona_mod.for_model(persona), indent=1), extra_rule=extra, context=ctx,
                       title=p.get("title", ""), location=(p.get("location") or {}).get("name", ""), content=text,
                       cannot_tell_option=ct)


def claude(prompt, tools=False):
    args = ["claude", "-p", prompt, "--model", MODEL, "--setting-sources", "", "--no-session-persistence",
            "--output-format", "stream-json", "--verbose"]
    if tools:
        args += ["--tools", "", "--strict-mcp-config", "--mcp-config", os.path.join(BASE, "mcp", "js3.mcp.json"),
                 "--allowedTools", "mcp__js3-score__score_posting"]
        cwd, env = BASE, dict(os.environ, JS3_MCP_LOG_SUBDIR="e5")
    else:
        args += ["--tools", ""]
        cwd, env = None, None
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(args, cwd=cwd or d, env=env, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    out = {"exit": r.returncode, "tool_calls": [], "result": None, "session_id": None, "cost_usd": None}
    for line in r.stdout.splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "assistant":
            for c in e["message"]["content"]:
                if c.get("type") == "tool_use":
                    out["tool_calls"].append({"name": c["name"], "input_keys": sorted(c.get("input", {}))})
        if e.get("type") == "result":
            out.update(result=e.get("result"), session_id=e.get("session_id"), cost_usd=e.get("total_cost_usd"))
    return out


def _parse(text):
    t = (text or "").strip()
    s, e = t.find("{"), t.rfind("}")
    v = json.loads(t[s:e + 1])
    return v


def _filter_rows(filters, held, persona):
    rows = []
    for cond, path in filters.items():
        cfg = scorer.load_filter(os.path.join(BASE, path))
        for p, label, _ in held:
            rec = scorer.evaluate(p, persona, cfg)
            v = {"keep": "relevant", "reject": "not_relevant"}.get(rec["verdict"], "cannot_tell")
            rows.append({"cond": cond, "id": p["id"], "verdict": v, "score": rec["score"],
                         "computed_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    return "".join(json.dumps(r) + "\n" for r in rows)


def run(workers=6):
    held = data.load_heldout()
    persona = data.load_persona()
    cfg_f0 = scorer.load_filter(os.path.join(BASE, FILTERS["F0"]))
    # batch 1 filter conditions: computed once, under lock 1, and never overwritten
    if not os.path.exists(os.path.join(BASE, EXP, "runs", "filters.jsonl")):
        check_lock(1)
        store.write_text(f"{EXP}/runs/filters.jsonl", _filter_rows(FILTERS, held, persona))
    # batch 2: computed under lock 2 (F0 again, to show the later code did not change it)
    if os.path.exists(os.path.join(BASE, LOCKS[2])) and not os.path.exists(os.path.join(BASE, EXP, "runs", "filters-2.jsonl")):
        check_lock(2)
        store.write_text(f"{EXP}/runs/filters-2.jsonl", _filter_rows(FILTERS2, held, persona))
    # Claude conditions: cached per (cond, id); a cached answer is never re-asked
    os.makedirs(os.path.join(BASE, EXP, "runs"), exist_ok=True)
    jobs = []
    for cond in CLAUDE_CONDS:
        path = os.path.join(BASE, EXP, "runs", f"{cond}.jsonl")
        have = set()
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                have = {json.loads(l)["id"] for l in f if l.strip()}
        jobs += [(cond, p) for p, _, _ in held if p["id"] not in have]
    lk = check_lock(1) if jobs else lock_status(1)[0]

    def one(job):
        cond, p = job
        prompt = prompt_for(cond, p, persona, cfg_f0)
        t0 = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        r = claude(prompt, tools=(cond == "E5"))
        row = {"cond": cond, "id": p["id"], "asked_utc": t0, "model": MODEL, "lock": lk["locked_utc"],
               "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), **r}
        try:
            v = _parse(r["result"])
            row["verdict"], row["reason"], row["quote"] = v.get("verdict"), v.get("reason"), v.get("quote")
            allowed = ("relevant", "not_relevant") + (("cannot_tell",) if cond == "E3" else ())
            if row["verdict"] not in allowed:
                row["invalid"] = f"verdict {row['verdict']!r} not allowed in {cond}"
            elif row.get("quote") and row["quote"].strip() and row["quote"].strip()[:60].lower() not in tu.clean(p["content"]).lower() \
                    and row["quote"].strip()[:60].lower() not in (p.get("title") or "").lower():
                row["quote_not_in_posting"] = True
        except Exception as e:
            row["invalid"] = f"{e.__class__.__name__}: {e}"
        return row

    with ThreadPoolExecutor(workers) as ex:
        for row in ex.map(one, jobs):
            with open(os.path.join(BASE, EXP, "runs", f"{row['cond']}.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(row["cond"], row["id"], row.get("verdict"), row.get("invalid", ""), f"tools={len(row['tool_calls'])}")
    return len(jobs)


def _load(cond, batch=1):
    name = ("filters.jsonl" if batch == 1 else "filters-2.jsonl") if cond in FILTERS or cond in FILTERS2 else f"{cond}.jsonl"
    path = os.path.join(BASE, EXP, "runs", name)
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, encoding="utf-8") as f:
        for l in f:
            r = json.loads(l)
            if r["cond"] == cond:
                out[r["id"]] = r
    return out


def metrics(res, labels):
    n = len(labels)
    ans = [i for i in labels if res.get(i, {}).get("verdict") in ("relevant", "not_relevant")]
    correct = sum(res[i]["verdict"] == labels[i] for i in ans)
    tp = sum(res[i]["verdict"] == "relevant" and labels[i] == "relevant" for i in ans)
    fp = sum(res[i]["verdict"] == "relevant" and labels[i] == "not_relevant" for i in ans)
    fn = sum(res[i]["verdict"] == "not_relevant" and labels[i] == "relevant" for i in ans)
    return {"n": n, "answered": len(ans), "abstained": n - len(ans), "correct": correct, "tp": tp, "fp": fp, "fn": fn,
            "invalid": sum(1 for i in labels if res.get(i, {}).get("invalid"))}


def report():
    lk, changed1 = lock_status(1)
    lk2, changed2 = lock_status(2)
    held = data.load_heldout()
    labels = {p["id"]: lab for p, lab, _ in held}
    titles = {p["id"]: p["title"] for p, _, _ in held}
    conds = [("F0", None, "filter v1.4 as in force"), ("E1", "F0", "filter file: T3 seniority -2.0 → 0.0"),
             ("E2", "F0", "setting: threshold 5.0 → 4.0"), ("C0", None, "Claude P1, posting only, no tools"),
             ("C0b", "C0", "nothing changed (fresh sessions): the noise floor"),
             ("E3", "C0", "prompt: + one abstention instruction"), ("E4", "C0", "context: + the filter's result"),
             ("E5", "C0", "tool list: + score_posting offered"),
             ("E6", "F0", "filter file: v1.4 → v1.5 (`N+ years` alone) [batch 2]"),
             ("E7", "E6", "filter file: v1.5 → v1.6 (sub-requirements ignored) [batch 2]")]
    res = {c: _load(c) for c, _, _ in conds[:-2]}
    res["E6"], res["E7"] = _load("E6", 2), _load("E7", 2)
    f0_again = _load("F0", 2)
    conds = [c for c in conds if res[c[0]]]
    L = ["# What moves the score: results (generated)", "",
         f"Generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ} by `python3 -m js3.experiments report`. "
         f"Batch 1 lock {lk['locked_utc']} (sha256 of prompt P1, the 3 batch-1 filter files, labels, persona and scorer/textutil/mcp_server code; "
         "the runner refuses to make new runs for a batch whose locked files changed). "
         + (f"Files changed after lock 1: {', '.join('`' + c + '`' for c in changed1)}. Batch-1 results were all produced before those changes (see asked_utc / computed_utc). " if changed1 else "No locked file changed since lock 1. ")
         + (f"Batch 2 lock {lk2['locked_utc']}" + (f"; changed since: {', '.join(changed2)}" if changed2 else "; unchanged since") + ". " if lk2 else "")
         + (f"F0 recomputed under batch-2 code: {'identical' if all(f0_again[i]['verdict'] == res['F0'][i]['verdict'] for i in f0_again) else 'DIFFERENT'} to batch 1. " if f0_again else "")
         + 
         f"Model {lk['model']} through `claude -p`, one fresh session per call, no session persistence, no settings files. "
         "Held-out set: Omkar's 20 JS1 labels "
         f"({sum(v == 'relevant' for v in labels.values())} relevant, {sum(v == 'not_relevant' for v in labels.values())} not_relevant).", "",
         "| Cond | One change vs baseline | Answered | Correct (of answered) | Abstained | FP | FN | Verdicts changed vs baseline | Invalid |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for c, base, what in conds:
        m = metrics(res[c], labels)
        ch = "—" if not base else str(sum(1 for i in labels if res[c].get(i, {}).get("verdict") != res[base].get(i, {}).get("verdict")))
        L.append(f"| {c} | {what} | {m['answered']}/{m['n']} | {m['correct']}/{m['answered']} | {m['abstained']} | {m['fp']} | {m['fn']} | {ch} | {m['invalid']} |")
    L += ["", "FP = said relevant, Omkar said not_relevant. FN = said not_relevant, Omkar said relevant. "
          "Accuracy is over answered postings; abstentions are counted apart, never as right.", "",
          "## Every held-out posting", "", "| id | Title | Omkar | " + " | ".join(c for c, _, _ in conds) + " |",
          "|---|---|---|" + "---|" * len(conds)]
    short = {"relevant": "R", "not_relevant": "n", "cannot_tell": "?", None: "·"}
    for i in labels:
        cells = []
        for c, _, _ in conds:
            v = res[c].get(i, {}).get("verdict")
            mark = short.get(v, "!")
            if v in ("relevant", "not_relevant") and v != labels[i]:
                mark = f"**{mark}✗**"
            cells.append(mark)
        L.append(f"| {i} | {titles[i][:55]} | {short[labels[i]]} | " + " | ".join(cells) + " |")
    L += ["", "R relevant · n not_relevant · ? cannot_tell · ✗ disagrees with Omkar.", "",
          "## Tool use in E5", ""]
    e5 = res["E5"]
    used = [i for i in e5 if e5[i].get("tool_calls")]
    L.append(f"Claude called score_posting in {len(used)} of {len(e5)} E5 sessions. "
             f"When it called the tool, its verdict matched the filter's (F0) in "
             f"{sum(1 for i in used if e5[i].get('verdict') == res['F0'][i]['verdict'])} of {len(used)}.")
    nq = sum(1 for c in CLAUDE_CONDS for r in res[c].values() if r.get("quote_not_in_posting"))
    cost = sum((r.get("cost_usd") or 0) for c in CLAUDE_CONDS for r in res[c].values())
    L += ["", f"Quotes not found verbatim in the posting (first 60 chars): {nq}. Total Claude cost: ${cost:.2f}.", ""]
    store.write_text(f"{EXP}/SCORE-RESULTS.md", "\n".join(L))


def fit_threshold():
    """Fit the threshold on DEV labels (Omkar's audit verdicts). Reports; never edits the filter."""
    from . import audit
    k = audit._load_key()
    om = audit._omkar()
    if not om:
        raise SystemExit("no audit verdicts yet: run `python3 -m js3.audit label` first")
    run_id, corpus = data.load_corpus(k["meta"]["corpus_run"])
    by = {(p["source"], p["id"]): p for p in corpus}
    persona = data.load_persona()
    cfg = scorer.load_filter()
    pts = []
    for e in k["key"]:
        o = om.get(e["card"])
        if not o or o["verdict"] == "cannot_tell":
            continue
        rec = scorer.evaluate(by[(e["source"], e["id"])], persona, cfg)
        gates = all(g["pass"] for g in rec["gates"].values())
        pts.append((rec["score"], gates, o["verdict"] == "keep"))
    L = ["# Threshold fitted on DEV labels (Omkar's audit verdicts) — reported, not adopted", "",
         f"{len(pts)} labelled cards (cannot_tell left out). The cards over-represent close calls and kept postings, so this is a biased dev set.", "",
         "| Threshold | Kept | Correct | FP | FN |", "|---:|---:|---:|---:|---:|"]
    best = None
    for t10 in range(20, 91, 5):
        t = t10 / 10
        kept = [(s, g, y) for s, g, y in pts if g and s >= t]
        fp = sum(1 for _, _, y in kept if not y)
        fn = sum(1 for s, g, y in pts if y and not (g and s >= t))
        correct = len(pts) - fp - fn
        L.append(f"| {t} | {len(kept)} | {correct} | {fp} | {fn} |")
        if best is None or correct > best[1]:
            best = (t, correct)
    L += ["", f"Best on dev: threshold {best[0]} ({best[1]} of {len(pts)} correct). The filter keeps {cfg['threshold']} "
          "until Omkar decides; a change would be a FILTER.md change-log row and then a held-out run (E2 shows the held-out effect of 4.0)."]
    store.write_text(f"{EXP}/FIT-THRESHOLD-dev.md", "\n".join(L) + "\n")
    return best


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "report"
    if cmd == "lock":
        print(json.dumps(lock(int(argv[1]) if len(argv) > 1 else 1), indent=1))
    elif cmd == "run":
        print(f"{run()} Claude calls made")
    elif cmd == "report":
        report()
        print("wrote experiments/SCORE-RESULTS.md")
    elif cmd == "fit-threshold":
        print(fit_threshold())
    else:
        raise SystemExit(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
