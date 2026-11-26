"""The source-grounded shortlist (Chapter 7). Real Claude calls; replies saved with dates.

    python3 scripts/shortlist.py [--n 12] [--workers 4]

1. Shortlist = filter v1.0 keeps, one per distinct title (location variants dropped), highest
   score first; ties broken by SHA-256 of the uid (reproducible, not alphabetical).
2. Claude writes 3-6 claims per posting, each with a quote (prompts/justify_v1.md).
3. js3/evidence.py labels every claim supported / contradicted / insufficient against the
   posting's own text, and applies the "I cannot tell" rule.
Writes out/shortlist/shortlist.json and labels/claims_sheet.csv (for Saloni to agree/disagree).
"""
import argparse
import concurrent.futures as cf
import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from js3 import claude  # noqa: E402
from js3.collect import latest_snapshot, load_postings  # noqa: E402
from js3.evidence import abstain, label_justification  # noqa: E402
from js3.filter import load_filter  # noqa: E402


def base_title(t):
    t = re.sub(r"\s*[-|(]\s*(tokyo|brazil|london|dublin|zurich|seoul|singapore|sydney|paris|munich).*$", "", t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip().lower()


def pick(results, n):
    keeps = [r for r in results if r["decision"] == "keep"]
    keeps.sort(key=lambda r: (-r["score"], hashlib.sha256(r["uid"].encode()).hexdigest()))
    seen, out = set(), []
    for r in keeps:
        b = base_title(r["title"])
        if b not in seen:
            seen.add(b)
            out.append(r)
        if len(out) == n:
            break
    return out


def justify(p):
    reply = claude.call(claude.fill("prompts/justify_v1.md", p))
    try:
        claims = claude.parse_json_reply(reply["raw"])["claims"]
        assert isinstance(claims, list)
        reply["parse"] = "ok"
    except Exception as e:  # noqa: BLE001
        claims = []
        reply["parse"] = f"rejected: {e}"
    return reply, claims


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    flt = load_filter()
    posts = {p["uid"]: p for p in load_postings(latest_snapshot())}
    with open(os.path.join(HERE, "out", "filter", "v1.0", "results.jsonl"), encoding="utf-8") as f:
        results = [json.loads(line) for line in f]
    chosen = pick(results, a.n)
    with cf.ThreadPoolExecutor(a.workers) as ex:
        replies = list(ex.map(lambda r: justify(posts[r["uid"]]), chosen))
    items, sheet = [], []
    for r, (reply, claims) in zip(chosen, replies):
        p = posts[r["uid"]]
        labeled = label_justification(claims, p, flt["seniority_veto_title"])
        reasons = abstain(p, labeled, r, flt["text_min_chars"])
        items.append({"uid": r["uid"], "title": r["title"], "url": p.get("url"), "filter": r, "claude": reply,
                      "claims": labeled, "answer": "I cannot tell" if reasons else "keep", "abstain_reasons": reasons})
        for i, c in enumerate(labeled, 1):
            sheet.append({"row": len(sheet) + 1, "uid": r["uid"], "title": r["title"], "claim_no": i, "kind": c.get("kind"),
                          "claim": c.get("claim"), "term": c.get("term"), "quote": c.get("quote"),
                          "checker_label": c["label"], "checker_why": c["why"], "hand_label": "", "note": "", "labelled_at": ""})
    os.makedirs(os.path.join(HERE, "out", "shortlist"), exist_ok=True)
    with open(os.path.join(HERE, "out", "shortlist", "shortlist.json"), "w", encoding="utf-8") as f:
        json.dump({"filter_version": flt["filter_version"], "prompt": "prompts/justify_v1.md", "items": items}, f,
                  indent=2, ensure_ascii=False)
    path = os.path.join(HERE, "labels", "claims_sheet.csv")
    if os.path.exists(path):
        sys.exit("labels/claims_sheet.csv exists; not overwriting hand labels")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sheet[0]))
        w.writeheader()
        w.writerows(sheet)
    for it in items:
        tally = {k: sum(c["label"] == k for c in it["claims"]) for k in ("supported", "contradicted", "insufficient")}
        print(f"{it['answer']:<14} {tally}  {it['title'][:70]}  {it['abstain_reasons']}")


if __name__ == "__main__":
    main()
