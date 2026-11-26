"""Evidence rules (FILTER.md B): label each shortlist claim against the posting's own text, then answer
relevant / not relevant / "I cannot tell" by the abstention rule. The mechanical checks run first and can only
make a label weaker (a quote that is not in the posting, or is only in cut boilerplate, is insufficient)."""
from __future__ import annotations

import json
import re

from .sheet import readable_text
from .textprep import normalize_quotes, posting_sentences

LABELS = ("supported", "contradicted", "insufficient")
CLAIM_TYPES = ("role", "location", "years", "skill", "degree", "other")
DECIDING = ("role", "location")
PERSONA_FIELDS = ("education", "highest_degree", "years_experience", "skills", "target_title_keywords", "remote_ok")
MAX_TEXT = 12000


def norm(s: str) -> str:
    s = normalize_quotes(s or "").replace("\xa0", " ").lower()
    return re.sub(r"\s+", " ", s).strip()


def quote_check(cfg: dict, posting: dict, quote: str) -> str:
    """'empty' | 'not_found' | 'boilerplate_only' | 'found' (FILTER.md B, supported: the first two conditions)."""
    q = norm(quote)
    if not q:
        return "empty"
    loc = posting["location"]
    names = [loc.get("name") or ""] + [o.get("name") or "" for o in loc.get("other") or []]
    own = [norm(posting["title"])] + [norm(n) for n in names]
    if any(q in f for f in own):
        return "found"
    if q not in norm(readable_text(posting)):
        return "not_found"
    prepared = norm(" ".join(posting_sentences(posting, cfg["boilerplate"])))
    return "found" if q in prepared else "boilerplate_only"


def _strict_json(text: str):
    def no_dupes(pairs):
        keys = [k for k, _ in pairs]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate keys")
        return dict(pairs)
    return json.loads(text, object_pairs_hook=no_dupes)


def validate_claims(result: str) -> tuple[list[dict] | None, str | None]:
    """The justify_v1 output contract. Nothing is repaired."""
    try:
        obj = _strict_json(result)
    except ValueError:
        return None, "result is not exactly one JSON object"
    if not isinstance(obj, dict) or set(obj) != {"claims"} or not isinstance(obj["claims"], list):
        return None, "result must be {\"claims\": [...]}"
    claims = obj["claims"]
    if not 4 <= len(claims) <= 7:
        return None, f"{len(claims)} claims, need 4-7"
    for c in claims:
        if not isinstance(c, dict) or set(c) != {"type", "claim", "quote"}:
            return None, "each claim needs exactly type, claim, quote"
        if c["type"] not in CLAIM_TYPES or not isinstance(c["claim"], str) or not c["claim"].strip() \
                or not isinstance(c["quote"], str):
            return None, f"bad claim {c!r:.80}"
    for t in ("role", "location", "years"):
        if sum(c["type"] == t for c in claims) != 1:
            return None, f"need exactly one {t} claim"
    return claims, None


def validate_labels(result: str, n: int) -> tuple[list[dict] | None, str | None]:
    try:
        obj = _strict_json(result)
    except ValueError:
        return None, "result is not exactly one JSON object"
    if not isinstance(obj, dict) or set(obj) != {"labels"} or not isinstance(obj["labels"], list):
        return None, "result must be {\"labels\": [...]}"
    labels = obj["labels"]
    if [x.get("i") if isinstance(x, dict) else None for x in labels] != list(range(n)):
        return None, f"labels must be numbered 0..{n - 1} in order"
    for x in labels:
        if set(x) != {"i", "label", "evidence", "why"} or x["label"] not in LABELS \
                or not isinstance(x["evidence"], str) or not isinstance(x["why"], str):
            return None, f"bad label entry {x!r:.80}"
    return labels, None


def final_labels(cfg: dict, posting: dict, claims: list[dict], claude_labels: list[dict] | None) -> list[dict]:
    """Mechanical quote check first; Claude's label only where the quote is really in the job's own text."""
    out = []
    for i, c in enumerate(claims):
        qc = quote_check(cfg, posting, c["quote"])
        cl = claude_labels[i] if claude_labels else None
        if cl and cl["label"] == "contradicted" and quote_check(cfg, posting, cl["evidence"]) == "found":
            label, source = "contradicted", "claude_labeler"          # its contradicting words are really there
        elif cl and cl["label"] == "contradicted":
            label, source = "insufficient", "mechanical:contradiction_evidence_not_found"
        elif qc in ("empty", "not_found", "boilerplate_only"):
            label, source = "insufficient", f"mechanical:{qc}"
        elif cl:
            label, source = cl["label"], "claude_labeler"
        else:
            label, source = None, "unlabelled"
        out.append({**c, "i": i, "quote_check": qc, "claude_label": cl["label"] if cl else None,
                    "claude_evidence": cl["evidence"] if cl else None, "claude_why": cl["why"] if cl else None,
                    "label": label, "label_source": source})
    return out


def answer(posting: dict, labelled: list[dict]) -> tuple[str, str]:
    """The abstention rule (FILTER.md B). Returns (answer, the rule that decided it)."""
    if not posting.get("text"):
        return "I cannot tell", "posting text missing"
    if not (posting["location"].get("name") or posting["location"].get("country")):
        return "I cannot tell", "posting location missing"
    for c in labelled:
        if c["type"] in ("role", "location", "years") and c["label"] == "contradicted":
            return "not relevant", f"{c['type']} claim contradicted"
    for c in labelled:
        if c["type"] in DECIDING and c["label"] != "supported":
            return "I cannot tell", f"{c['type']} claim {c['label']}"
    return "relevant", "role and location supported; nothing deciding contradicted"


def fill(template: str, values: dict) -> str:
    body = template.split("---", 2)[2].lstrip("\n") if template.startswith("---") else template
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], body)   # one pass: posting text is never re-filled


def prompt_values(persona: dict, posting: dict, company: str) -> dict:
    text = readable_text(posting)
    if len(text) > MAX_TEXT:
        text = text[:MAX_TEXT] + "\n[... truncated]"
    return {"persona": json.dumps({k: persona[k] for k in PERSONA_FIELDS}), "company": company,
            "title": posting["title"], "location": posting["location"].get("name") or "(none given)", "text": text}
