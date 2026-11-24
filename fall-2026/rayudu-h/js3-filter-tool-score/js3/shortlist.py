"""The source-grounded shortlist (FILTER.md R14 and section 3).

For each of the top-N kept postings: build the claims (C1, C2 per matched skill up to 3, C3, C4, C5),
ask Claude to label each against the posting's own text with a verbatim quote, check every quote
mechanically (js3.claims), and compute the answer. Every Claude call is saved with its date,
model, prompt hash and raw reply. Labels that fail the check are kept and marked invalid; they
are never silently repaired.
"""
from __future__ import annotations

import hashlib
import json

from . import ROOT, claims, corpus, filterdoc, score
from . import claude as claude_cli

PROMPT_FILE = ROOT / "prompts" / "claims_v1.md"
MAX_TEXT = 15000
SYSTEM = ("You label claims about a job posting against the posting's own text. "
          "Follow the output contract in the user message exactly.")


def default_caller(prompt: str, model: str) -> dict:
    return claude_cli.call(prompt, SYSTEM, model)


def build_prompt(posting: dict, claim_list: list) -> str:
    view = {"title": posting["title"], "location": posting["location"], "text": posting["text"][:MAX_TEXT]}
    items = [{"id": cid, "claim": c["text"]} for cid, c in claim_list]
    return (PROMPT_FILE.read_text()
            .replace("{{POSTING_JSON}}", json.dumps(view, indent=2, ensure_ascii=False))
            .replace("{{CLAIMS_JSON}}", json.dumps(items, indent=2, ensure_ascii=False)))


def claim_ids(result: dict) -> list:
    out = []
    for c in claims.claims_for(result):
        cid = c["claim"] + (f":{c['skill']}" if c.get("skill") else "")
        out.append((cid, c))
    return out


def parse_reply(text: str, ids: list) -> tuple:
    errors = []
    try:
        data = json.loads((text or "").strip())
    except json.JSONDecodeError as e:
        return None, [f"not a bare JSON object: {e}"]
    labels = data.get("labels") if isinstance(data, dict) else None
    if not isinstance(labels, list):
        return None, ['missing "labels" list']
    got = [lab.get("id") for lab in labels if isinstance(lab, dict)]
    if got != ids:
        errors.append(f"claim ids must be exactly {ids} in order; got {got}")
    return labels, errors


def label_posting(posting: dict, result: dict, caller=default_caller, model: str = "sonnet") -> dict:
    ids = claim_ids(result)
    prompt = build_prompt(posting, ids)
    call = caller(prompt, model)
    labels, errors = (parse_reply(call["result"], [i for i, _ in ids]) if not call["is_error"]
                      else (None, ["claude call failed"]))
    rows = []
    for cid, c in ids:
        lab = next((x for x in (labels or []) if isinstance(x, dict) and x.get("id") == cid), None)
        row = {"id": cid, "claim": c["claim"], "text": c["text"]}
        if lab is None:
            row.update(label=None, valid=False, errors=["no label returned"])
        else:
            norm = {"claim": c["claim"], "label": lab.get("label"), "quote": lab.get("quote"),
                    "conflict": lab.get("conflict")}
            errs = claims.validate_label(norm, posting)
            row.update(label=lab.get("label"), quote=lab.get("quote"), conflict=lab.get("conflict"),
                       valid=not errs, errors=errs)
        rows.append(row)
    valid_labels = [{"claim": r["claim"], "label": r["label"]} for r in rows if r["valid"]]
    invalid_core = [r["id"] for r in rows if not r["valid"] and r["claim"] in ("C1", "C2", "C3")]
    ans = claims.answer(valid_labels, cannot_tell_reason=(f"invalid labels for {invalid_core}" if invalid_core else None))
    return {"key": posting["key"], "title": posting["title"], "location": posting["location"], "url": posting["url"],
            "score": result["score"], "skills": result["skills"], "filter_version": result["filter_version"],
            "prompt_file": PROMPT_FILE.name, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            **{k: call[k] for k in ("started_at", "exit_code", "model_requested", "models_used", "duration_ms",
                                     "is_error")},
            "raw_reply": call["result"], "reply_errors": errors, "claims": rows, "answer": ans}


def build(caller=default_caller) -> dict:
    flt = filterdoc.load()
    c = corpus.load()
    results = {k: score.score(p, flt) for k, p in c["postings"].items()}
    top = score.shortlist(list(results.values()), corpus.latest_keys(c), flt["shortlist_size"])
    entries = [label_posting(c["postings"][r["key"]], r, caller=caller) for r in top]
    return {"filter_version": flt["filter_version"], "filter_sha256": flt["filter_sha256"],
            "snapshot": c["latest"], "entries": entries}


def finalize() -> dict:
    """Apply the hand check (shortlist/hand-check.csv: final_label) to Claude's labels and recompute answers.
    Claude's label, Hemanth's check and the final label all stay in the output."""
    import csv
    data = json.loads((ROOT / "shortlist" / "claims.json").read_text())
    rows = list(csv.DictReader(open(ROOT / "shortlist" / "hand-check.csv", newline="")))
    final = {(int(r["posting"]), r["claim"]): r for r in rows}
    for i, e in enumerate(data["entries"], 1):
        labs = []
        for c in e["claims"]:
            r = final[(i, c["id"])]
            c.update(claude_label=c["label"], hemanth_check=r["hemanth_check"], final_label=r["final_label"],
                     final_note=r["final_note"])
            labs.append({"claim": c["claim"], "label": r["final_label"]})
        e["claude_answer"] = e["answer"]
        e["answer"] = claims.answer(labs)
    return data


ABBR = {"supported": "S", "contradicted": "**C**", "insufficient": "I"}


def render(data: dict) -> str:
    """Every claim of every shortlisted posting, with Claude's label, Hemanth's check, the final label and quotes."""
    L = ["# Shortlist claims (generated by `python -m js3 shortlist-final` from shortlist/claims.json and "
         "shortlist/hand-check.csv)", "",
         f"Filter v{data['filter_version']} · snapshot {data['snapshot']} · labels by Claude (prompt "
         "`prompts/claims_v1.md`), checked by Hemanth, final label after the rule re-check.", ""]
    for i, e in enumerate(data["entries"], 1):
        L += [f"## #{i} {e['title']}", f"{e['location']} · score {e['score']} · {e['url']}",
              f"Claude call: {e['started_at']}, {', '.join(e['models_used'])}, prompt sha256 `{e['prompt_sha256'][:16]}…`",
              f"**Answer: {e['answer']['answer']}** ({e['answer']['why']})"
              + (f"; before the rule re-check: {e['claude_answer']['answer']}" if e['claude_answer'] != e['answer'] else ""),
              "", "| claim | Claude | Hemanth | final | evidence |", "|---|---|---|---|---|"]
        for c in e["claims"]:
            ev = ""
            if c.get("conflict"):
                ev = f"for: “{c['conflict']['for']}” · against: “{c['conflict']['against']}”"
            elif c.get("quote"):
                ev = f"“{c['quote']}”"
            if c.get("final_note"):
                ev += f" — {c['final_note']}"
            L.append(f"| {c['id']} {c['text']} | {c['claude_label']} | {c['hemanth_check']} | **{c['final_label']}** | "
                     f"{ev.replace('|', '/')} |")
        L.append("")
    return "\n".join(L) + "\n"
