"""The source-grounded shortlist (FILTER.md section 2): justify, check every claim, answer or abstain.

    python -B -m agent3.shortlist --version v1.0

For each shortlisted posting:
  1. Claude (fresh session, prompts/justify_v1.md) writes claims, each with a quote.
  2. Code checks every quote is in the posting verbatim (E1/E3). A claim that fails never reaches step 3.
  3. A second fresh Claude session (prompts/check_v1.md) labels what the verbatim quotes mean (E4).
     It sees only the posting text and the claims: no résumé, no score, no verdict.
  4. claims.answer applies A1-A3: relevant / not_relevant / cannot_tell.
Then I verify every label by hand (labels/claim_checks.csv); where I disagree, my label stands.
Writes out/shortlist/<version>/run.json and labels/claim_checks_blank.csv.
"""
import argparse
import csv
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agent3 import claims as cl, corpus, filter as flt, policy
from agent3.claude import ask_claude, parse_json_reply
from agent3.judge import resume_for_claude
from agent3.resume import load_resume

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ("core_work", "level", "employment")


def posting_block(p: dict) -> str:
    lines = [f"title: {p['title']}", f"content: {p['content_text']}"]
    if p.get("employment_type"):
        lines.append(f"employment type: {p['employment_type']}")
    return "\n".join(lines)


def validate_claims(obj) -> tuple:
    if not isinstance(obj, dict) or set(obj) != {"claims"} or not isinstance(obj["claims"], list):
        return None, 'reply must be {"claims": [...]} and nothing else'
    out = []
    for c in obj["claims"]:
        if not isinstance(c, dict) or set(c) != {"kind", "claim", "quote"}:
            return None, "each claim must have exactly kind, claim, quote"
        if c["kind"] not in cl.KINDS or not isinstance(c["claim"], str) or not isinstance(c["quote"], str):
            return None, f"bad claim: {c!r}"[:200]
        out.append(c)
    kinds = [c["kind"] for c in out]
    for k in REQUIRED:
        if kinds.count(k) != 1:
            return None, f"need exactly one {k} claim, got {kinds.count(k)}"
    n_req = sum(k in ("has", "lacks") for k in kinds)
    if not 1 <= n_req <= 4:
        return None, f"need 1-4 has/lacks claims, got {n_req}"
    return out, None


def validate_labels(obj, n: int) -> tuple:
    if not isinstance(obj, dict) or not isinstance(obj.get("labels"), list):
        return None, 'reply must be {"labels": [...]}'
    got = {}
    for x in obj["labels"]:
        if not isinstance(x, dict) or x.get("i") not in range(1, n + 1) or x.get("label") not in cl.LABELS:
            return None, f"bad label entry: {x!r}"[:200]
        if x["i"] in got:
            return None, f"claim {x['i']} labeled twice"
        got[x["i"]] = x
    if len(got) != n:
        return None, f"labeled {len(got)} of {n} claims"
    return got, None


def check_prompt(p: dict, to_check: list) -> str:
    lines = ["POSTING TEXT:", posting_block(p), "", "CLAIMS:"]
    for i, c in enumerate(to_check, 1):
        lines.append(f"{i}. claim: {c['claim']}\n   quote: \"{c['quote']}\"")
    return "\n".join(lines)


def process(p: dict, fres: dict, resume: dict, justify_tpl: str, check_tpl: str, ask=ask_claude) -> dict:
    rec = {"id": p["id"], "title": p["title"], "board": p["board"], "url": p["url"], "filter": fres}
    user = "RÉSUMÉ (JSON):\n" + json.dumps(resume_for_claude(resume), indent=2, ensure_ascii=False) + \
           "\n\nPOSTING TEXT:\n" + posting_block(p)
    rec["justify_reply"] = ask(justify_tpl, user)
    obj, why = parse_json_reply(rec["justify_reply"].get("raw_text"))
    claims_list, why = (validate_claims(obj) if obj is not None else (None, why))
    if claims_list is None:
        rec.update(rejection=f"justification rejected: {why}", claims=[],
                   answer=cl.answer(fres, [], board_failed=False) | {"note": "no valid justification"})
        return rec
    verbatim = [c for c in claims_list if c["quote"].strip() and cl.quote_in_posting(c["quote"], p)]
    meaning = {}
    if verbatim:
        rec["check_reply"] = ask(check_tpl, check_prompt(p, verbatim))
        obj, why = parse_json_reply(rec["check_reply"].get("raw_text"))
        got, why = (validate_labels(obj, len(verbatim)) if obj is not None else (None, why))
        if got is None:
            rec["check_rejection"] = why
        else:
            meaning = {id(c): got[i] for i, c in enumerate(verbatim, 1)}

    def meaning_check(c, _p):
        m = meaning.get(id(c))
        if m is None:
            return {"label": None}
        return {"label": m["label"], "why": m.get("why", ""), "contra_quote": m.get("contra_quote"),
                "checked_by": "claude_checker"}

    rec["claims"] = [cl.label_claim(c, p, meaning_check) for c in claims_list]
    rec["answer"] = cl.answer(fres, rec["claims"])
    return rec


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1.0", choices=sorted(flt.VERSIONS))
    ap.add_argument("--resume", default=ROOT / "data" / "resume_jack_spencer.json", type=Path)
    args = ap.parse_args(argv)
    cfg = flt.VERSIONS[args.version]
    c = corpus.load()
    res = flt.run(c["postings"].values(), cfg)
    resume = load_resume(policy.check_read(args.resume))
    jt = (ROOT / "prompts" / "justify_v1.md").read_text(encoding="utf-8")
    ct = (ROOT / "prompts" / "check_v1.md").read_text(encoding="utf-8")
    ids = res["shortlist"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = {pid: pool.submit(process, c["postings"][pid], res["results"][pid], resume, jt, ct) for pid in ids}
        recs = {pid: f.result() for pid, f in futs.items()}
    out = {"filter_version": cfg["version"], "shortlist": ids, "missing_boards": c["missing"],
           "prompts": ["prompts/justify_v1.md", "prompts/check_v1.md"], "records": recs}
    folder = policy.OUT / "shortlist" / cfg["version"]
    policy.write_bytes(folder / "run.json", (json.dumps(out, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    rows = []
    for rank, pid in enumerate(ids, 1):
        for j, cm in enumerate(recs[pid].get("claims", []), 1):
            rows.append({"rank": rank, "id": pid, "title": recs[pid]["title"], "claim_no": j, "kind": cm["kind"],
                         "claim": cm["claim"], "quote": cm["quote"], "checker_label": cm["label"],
                         "checker_why": cm.get("why", ""), "my_label": "", "my_note": ""})
    sheet = ROOT / "labels" / "claim_checks_blank.csv"
    with sheet.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["rank"])
        w.writeheader()
        w.writerows(rows)
    for pid in ids:
        r = recs[pid]
        labs = [x["label"] for x in r.get("claims", [])]
        print(f"{r['answer']['answer']:<13} {r['title'][:50]:<50} claims {len(labs)}: "
              f"S{labs.count('supported')} C{labs.count('contradicted')} I{labs.count('insufficient')}"
              f"{'  ' + r['rejection'] if r.get('rejection') else ''}")
    print(f"{len(rows)} claims -> {sheet.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
