"""The filter, FILTER.md sections 1 to 4 (version v1). Pure functions over dataset lines.

    evaluate(line, rules=V1) -> {"decision": "keep"|"reject"|"abstain", "score", "reasons", "matched", ...}
    run(lines, meta, rules=V1) -> [output lines], one per posting plus one per failed board
    rank(outputs) -> outputs sorted by the section 2 tie order
    python -m jobwatch filter --dataset data/postings-<run-id>.jsonl --version v1

Matching (section 1): JS1 tokens; a term matches when its tokens appear consecutively. Title and
location terms match in the normalized title or location. Body terms (T01-T18, E01) match inside
one non-boilerplate sentence of the posting text at a time: boilerplate is decided per sentence
(section 3), so a body match never spans two sentences. Every match carries its character span
and quote in the field it was found in (title, location or text).

Decision (section 2, precedence bullet): hard rejections first (X01-X08 in the title; no role
word; a known nonmatching location; E01 finds more than five years). Then abstention conditions
(missing or empty description; missing or empty location; a bare Remote without a US token; a
Senior title where E01 finds no requirement). With an abstention condition, a missing or empty
description gives I cannot tell; otherwise the posting rejects when its score stays below T for
every resolution (the location +2 assumed), and gives I cannot tell when it could reach T.
With no condition, score = 5 + 2 + topics and the posting is kept when score >= T.
Scores: null for gate rejects and abstentions, and for a reject decided by the score bound under
an abstention condition (it was never fully scored); the number for every other posting.
"""
import dataclasses
import re
from dataclasses import dataclass, field

from jobwatch.textmatch import tokens as js1_tokens

T_DEFAULT = 8


@dataclass(frozen=True)
class Rules:
    version: str
    exclude: tuple   # (id, term)
    senior: tuple    # (id, term)
    roles: tuple
    locations: tuple  # (id, term) for L01-L04
    remote: tuple     # (id, term)
    us_tokens: tuple
    topics: tuple
    skip_words: tuple
    experience_words: tuple
    max_years: int = 5
    role_weight: int = 5
    location_weight: int = 2
    topic_weight: int = 1
    threshold: int = T_DEFAULT
    missing_location_values: tuple = ()   # normalized location strings read as missing (C4)
    extra: dict = field(default_factory=dict)


V1 = Rules(
    version="v1",
    exclude=(("X01", "Senior Staff"), ("X02", "Staff"), ("X03", "Principal"), ("X04", "Director"),
             ("X05", "Intern"), ("X06", "Manager"), ("X07", "Lead"), ("X08", "Head")),
    senior=("X09", "Senior"),
    roles=(("R01", "Machine Learning Engineer"), ("R02", "ML Engineer"), ("R03", "AI Engineer"),
           ("R04", "Applied Scientist"), ("R05", "Data Scientist"), ("R06", "Research Engineer"),
           ("R07", "Research Scientist"), ("R08", "Machine Learning Scientist"), ("R09", "LLM Engineer"),
           ("R10", "Applied AI Engineer")),
    locations=(("L01", "Boston"), ("L02", "New York"), ("L03", "NYC"), ("L04", "Seattle")),
    remote=("L05", "Remote"),
    us_tokens=("us", "usa", "united states", "u s"),
    topics=(("T01", "Python"), ("T02", "PyTorch"), ("T03", "TensorFlow"), ("T04", "Keras"), ("T05", "scikit-learn"),
            ("T06", "Machine Learning"), ("T07", "Deep Learning"), ("T08", "LLM"), ("T09", "NLP"),
            ("T10", "Model Training"), ("T11", "Model Evaluation"), ("T12", "Inference"), ("T13", "Fine-tuning"),
            ("T14", "RAG"), ("T15", "Embeddings"), ("T16", "Transformers"), ("T17", "MLOps"),
            ("T18", "Computer Vision")),
    skip_words=("preferred", "nice to have", "bonus", "ideally", "plus"),
    experience_words=("experience", "experienced"),
)
VERSIONS = {"v1": V1}

# Candidate rule changes proposed at Gate 3b, each one change to v1 (FILTER.md section 8).
CANDIDATES = {
    "C1": ("add \"Forward Deployed\" as an exclusion term (X10)",
           dataclasses.replace(V1, version="v1+C1", exclude=V1.exclude + (("X10", "Forward Deployed"),))),
    "C2": ("add title role patterns R11-R14: \"Software Engineer, Machine Learning\", \"Engineer, Machine Learning\", "
           "\"Software Engineer, AI\", \"Machine Learning\"",
           dataclasses.replace(V1, version="v1+C2", roles=V1.roles + (
               ("R11", "Software Engineer, Machine Learning"), ("R12", "Engineer, Machine Learning"),
               ("R13", "Software Engineer, AI"), ("R14", "Machine Learning")))),
    "C3": ("replace T12 \"Inference\" with \"model inference\"",
           dataclasses.replace(V1, version="v1+C3", topics=tuple(
               (rid, "model inference" if rid == "T12" else term) for rid, term in V1.topics))),
    "C4": ("treat a location of \"N/A\" as missing (I cannot tell)",
           dataclasses.replace(V1, version="v1+C4", missing_location_values=("n/a",))),
    "C5": ("add \"Internship\" as an exclusion term next to X05 Intern (X05b)",
           dataclasses.replace(V1, version="v1+C5", exclude=V1.exclude + (("X05b", "Internship"),))),
}


# --- tokens with spans (the JS1 tokenization, positions kept) -----------------------------------
def token_spans(text):
    """[(token, start, end)]: lowercase with str.lower(); maximal runs of isalnum() or "+#"."""
    out, start = [], None
    for i, ch in enumerate(text):
        if ch.isalnum() or ch in "+#":
            if start is None:
                start = i
        elif start is not None:
            out.append((text[start:i].lower(), start, i))
            start = None
    if start is not None:
        out.append((text[start:].lower(), start, len(text)))
    return out


def find_term(term, spans):
    """First consecutive-token match of `term` in `spans`: (start, end) characters, or None."""
    t = js1_tokens(term)
    n = len(t)
    if not n:
        return None
    toks = [s[0] for s in spans]
    for i in range(len(toks) - n + 1):
        if toks[i:i + n] == t:
            return spans[i][1], spans[i + n - 1][2]
    return None


def _match(rule_id, field_name, text, span, offset=0):
    s, e = span
    return {"rule": rule_id, "field": field_name, "start": offset + s, "end": offset + e, "quote": text[s:e]}


# --- body sentences -----------------------------------------------------------------------------
def body_sentences(line):
    """Non-boilerplate sentences: (start offset, sentence text). Section 1: body matches ignore boilerplate."""
    text = line["text"]
    return [(s["start"], text[s["start"]:s["end"]]) for s in line["sentences"] if not s["boilerplate"]]


def topic_matches(line, rules):
    """Each topic rule at most once: its first match in non-boilerplate sentences, in text order."""
    out = []
    sents = [(off, sent, token_spans(sent)) for off, sent in body_sentences(line)]
    for rule_id, term in rules.topics:
        for off, sent, spans in sents:
            hit = find_term(term, spans)
            if hit:
                out.append(_match(rule_id, "text", sent, hit, off))
                break
    return out


# --- E01 ------------------------------------------------------------------------------------------
_YEARS = re.compile(r"(?<![\d.])(\d+)(?:\s*[-–—]\s*\d+|\s+to\s+\d+)?\s*(?:\+|\s+or\s+more)?\s*years\b", re.IGNORECASE)


def experience_requirement(line, rules):
    """E01 reading rule. Returns (largest N, its match) or (None, None)."""
    best = None
    for off, sent in body_sentences(line):
        spans = token_spans(sent)
        if not any(find_term(w, spans) for w in rules.experience_words):
            continue
        if any(find_term(w, spans) for w in rules.skip_words):
            continue
        for m in _YEARS.finditer(sent):
            n = int(m.group(1))
            if best is None or n > best[0]:
                best = (n, _match("E01", "text", sent, (m.start(), m.end()), off))
    return best if best else (None, None)


# --- location ------------------------------------------------------------------------------------
def primary_location(line):
    """FILTER.md section 5: only the primary location field (secondary locations are not read)."""
    return line.get("location")


def location_status(line, rules):
    """("missing", None) | ("bare_remote", match) | ("match", match) | ("nonmatch", None)."""
    loc = primary_location(line)
    if loc is None or not js1_tokens(loc) or loc.strip().lower() in rules.missing_location_values:
        return "missing", None
    spans = token_spans(loc)
    for rule_id, term in rules.locations:
        hit = find_term(term, spans)
        if hit:
            return "match", _match(rule_id, "location", loc, hit)
    rid, term = rules.remote
    hit = find_term(term, spans)
    if hit:
        if any(find_term(u, spans) for u in rules.us_tokens):
            return "match", _match(rid, "location", loc, hit)
        return "bare_remote", _match(rid, "location", loc, hit)
    return "nonmatch", None


# --- the decision ---------------------------------------------------------------------------------
def evaluate(line, rules=V1):
    title = line.get("title") or ""
    tspans = token_spans(title)
    matched, reasons = [], []
    hard, abstain = [], []

    excl = [_match(rid, "title", title, hit) for rid, term in rules.exclude if (hit := find_term(term, tspans))]
    if excl:
        hard.append("exclusion term in the title: " + ", ".join(f"{m['rule']} {m['quote']!r}" for m in excl))
        matched += excl
    roles = [_match(rid, "title", title, hit) for rid, term in rules.roles if (hit := find_term(term, tspans))]
    matched += roles
    if not roles:
        hard.append("no role word R01-R10 in the title")
    senior_hit = find_term(rules.senior[1], tspans)
    if senior_hit:
        matched.append(_match(rules.senior[0], "title", title, senior_hit))

    loc_state, loc_match = location_status(line, rules)
    if loc_match:
        matched.append(loc_match)
    if loc_state == "nonmatch":
        hard.append("known nonmatching location (no L01-L05)")
    elif loc_state == "missing":
        abstain.append("location missing or empty")
    elif loc_state == "bare_remote":
        abstain.append("location is Remote without a US token")

    has_description = bool(js1_tokens(line.get("text") or ""))
    if not has_description:
        abstain.append("description missing or empty")
        n_years, e_match = None, None
    else:
        n_years, e_match = experience_requirement(line, rules)
    if e_match:
        matched.append(e_match)
    if n_years is not None and n_years > rules.max_years:
        hard.append(f"E01: minimum required experience {n_years} years (> {rules.max_years})")
    elif n_years is None and senior_hit and has_description:
        abstain.append("Senior title and E01 found no experience requirement")

    topics = topic_matches(line, rules) if has_description else []
    matched += topics
    out = {"key": line["key"], "board": line["board"], "posting_id": line["posting_id"], "version": rules.version,
           "matched": matched, "topics": len(topics), "years": n_years}

    if hard:
        return {**out, "decision": "reject", "score": None, "reasons": hard}
    if abstain:
        if not has_description:
            return {**out, "decision": "abstain", "score": None, "reasons": ["I cannot tell: " + "; ".join(abstain)]}
        best = rules.role_weight + rules.location_weight + rules.topic_weight * len(topics)
        if best < rules.threshold:
            return {**out, "decision": "reject", "score": None,
                    "reasons": [f"score at most {best} < T={rules.threshold} for every resolution of: " + "; ".join(abstain)]}
        return {**out, "decision": "abstain", "score": None, "reasons": ["I cannot tell: " + "; ".join(abstain)]}
    score = rules.role_weight + rules.location_weight + rules.topic_weight * len(topics)
    if score >= rules.threshold:
        return {**out, "decision": "keep", "score": score, "reasons": [f"score {score} >= T={rules.threshold}"]}
    return {**out, "decision": "reject", "score": score, "reasons": [f"score {score} < T={rules.threshold}"]}


def tie_key(o):
    """Section 2: score descending (null scores last), then board, then posting id, as strings."""
    s = o.get("score")
    return (0 if s is not None else 1, -(s or 0), str(o["board"]), str(o["posting_id"]))


def rank(outputs):
    return sorted(outputs, key=tie_key)


def run(lines, meta, rules=V1):
    outs = [evaluate(ln, rules) for ln in lines]
    for b in meta.get("failed_boards", []):
        outs.append({"key": None, "board": b, "posting_id": None, "version": rules.version, "scope": "board",
                     "decision": "abstain", "score": None, "matched": [], "topics": 0, "years": None,
                     "reasons": ["I cannot tell: board failed in this run"]})
    return outs
