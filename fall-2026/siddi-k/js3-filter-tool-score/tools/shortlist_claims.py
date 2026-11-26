"""Brief Step 2.2: the source-grounded shortlist. For each shortlisted posting, Claude writes the justification as
claims (prompts/justify_v1.md); a separate fresh Claude call labels them (prompts/label_claims_v1.md); the
mechanical quote check (js3/evidence.py) runs over both; the abstention rule gives the agent's answer.

Every Claude stdout is saved unmodified under output/shortlist/<filter>/<run>/raw/.
Usage: CLAUDE_BIN=... python tools/shortlist_claims.py --run RUN_ID [--config config/filter.v1.json]"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import claude_cli, collect, evidence, policy  # noqa: E402
from js3 import filter as flt  # noqa: E402
from js3.sheet import COMPANY  # noqa: E402


def one(cfg, persona, posting, out_dir, justify_t, label_t) -> dict:
    company = COMPANY.get(posting["board"], posting["board"])
    tag = f"{posting['board']}-{posting['id']}"
    values = evidence.prompt_values(persona, posting, company)
    rec = {"board": posting["board"], "id": posting["id"], "title": posting["title"],
           "location": posting["location"].get("name"), "model": claude_cli.MODEL,
           "prompts": ["justify_v1", "label_claims_v1"]}
    argv, out, err, code = claude_cli.run(evidence.fill(justify_t, values), [])
    policy.write_bytes(out_dir / "raw" / f"{tag}-justify.json", out)
    result, why = claude_cli.envelope_result(out)
    claims, why2 = evidence.validate_claims(result) if result is not None else (None, why)
    if claims is None:
        rec.update(status="justify_invalid", reason=why2 or why)
        return rec
    numbered = "\n".join(f"{i}. [{c['type']}] {c['claim']} (quoted: \"{c['quote']}\")" for i, c in enumerate(claims))
    argv, out, err, code = claude_cli.run(evidence.fill(label_t, {**values, "claims": numbered}), [])
    policy.write_bytes(out_dir / "raw" / f"{tag}-label.json", out)
    result, why = claude_cli.envelope_result(out)
    labels, why2 = evidence.validate_labels(result, len(claims)) if result is not None else (None, why)
    labelled = evidence.final_labels(cfg, posting, claims, labels)
    ans, rule = evidence.answer(posting, labelled)
    rec.update(status="ok" if labels else "label_invalid", label_reason=None if labels else (why2 or why),
               claims=labelled, answer=ans, answer_rule=rule)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--config", default="config/filter.v1.json")
    a = ap.parse_args()
    cfg = json.loads(policy.check_read(a.config).read_text(encoding="utf-8"))
    persona = json.loads(policy.check_read("data/persona_resume.json").read_text(encoding="utf-8"))
    postings = collect.load_postings(policy.ROOT / "data" / "collections" / a.run)
    by_key = {(p["board"], p["id"]): p for p in postings}
    short = flt.shortlist(cfg, [flt.evaluate(cfg, p) for p in postings])
    out_dir = policy.ROOT / "output" / "shortlist" / cfg["version"] / a.run
    justify_t = policy.check_read("prompts/justify_v1.md").read_text(encoding="utf-8")
    label_t = policy.check_read("prompts/label_claims_v1.md").read_text(encoding="utf-8")
    with ThreadPoolExecutor(max_workers=4) as ex:
        recs = list(ex.map(lambda r: one(cfg, persona, by_key[(r["board"], r["id"])], out_dir, justify_t, label_t),
                           short))
    for r, s in zip(recs, short):
        r["filter_score"] = s["score"]
    policy.write_bytes(out_dir / "claims.jsonl",
                       "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs).encode("utf-8"))
    for r in recs:
        print(f"{r['status']:15} {r.get('answer', '-'):15} {r['board']:7} {r['title']}  [{r.get('answer_rule', r.get('reason'))}]")
    print(f"wrote {out_dir.relative_to(policy.ROOT).as_posix()}/claims.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
