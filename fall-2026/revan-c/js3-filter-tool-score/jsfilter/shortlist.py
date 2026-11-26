"""Source-grounded shortlist claims (FILTER.md section 2).

The filter's word matches become *draft* claims. Every claim starts `not reviewed`. Only a claim a human marked
`supported` after reading the saved posting may be published as a statement about the posting.
"""
import re

LABELS = ("supported", "contradicted", "insufficient", "not reviewed")


def _years_passage(text):
    m = re.search(r"\b\d+\s*\+?\s*(?:-\s*\d+\s*)?years?\b", text, flags=re.IGNORECASE)
    if not m:
        return None
    start = text.rfind("\n", 0, m.start()) + 1
    end = text.find("\n", m.end())
    line = text[start:end if end != -1 else len(text)]
    after_match = line[m.end() - start:]
    sentence_end = re.search(r"[.!?](?=\s|$)", after_match)
    if sentence_end:
        line = line[:m.end() - start + sentence_end.end()]
    return " ".join(line.split())


def _remote_eligibility_passage(text):
    if not text:
        return None
    m = re.search(r"To be eligible for consideration, candidates for fully remote positions must reside"
                  r".*?\b[A-Z]{2}\.", text, flags=re.IGNORECASE | re.DOTALL)
    return " ".join(m.group(0).split()) if m else None


def draft_claims(row, description=None):
    """One atomic claim per filter match, phrased as what a reader would take the shortlist to assert."""
    if row["fate"] != "kept":
        return []
    claims = []

    def add(kind, claim, field, excerpt):
        claims.append({"claim_id": f"{row['board']}:{row['id']}:{len(claims) + 1}", "kind": kind,
                       "claim": claim, "field": field, "excerpt": excerpt,
                       "label": "not reviewed", "reviewer": None, "missing": None, "note": None})

    rules = row["rules"]
    role = max(rules["R1"]["matched"], key=lambda r: len(r))
    add("role", f"The role is a {role} position.", rules["R1"]["field"], row["title"])
    add("location", "The posting names Boston as a job location.", rules["R4"]["field"], row["location"])
    remote_passage = _remote_eligibility_passage(description)
    add("location", "A Boston resident may work fully remotely in this role.",
        rules["R5"]["field"] if remote_passage else rules["R4"]["field"],
        remote_passage or (f"{row['location']}" +
                           (f" | workplaceType: {row['workplace_type']}" if row["workplace_type"] else "")))
    for topic in rules["R5"]["matched"]:
        add("topic", f"The job's own work is {topic} work.", rules["R5"]["field"], row["evidence"].get(topic))
    for skill in rules["R6"]["matched"]:
        add("skill", f"The role requires {skill}.", rules["R6"]["field"], row["evidence"].get(skill))
    add("seniority", "The role is open to someone with about two years of experience.",
        rules["R6"]["field"], (_years_passage(description) if description else None))
    return claims


def publishable(claims):
    return [c for c in claims if c["label"] == "supported" and c.get("reviewer")]


def render(row, claims):
    """The shortlist line. Without a reviewed `supported` claim the agent abstains (FILTER.md 2)."""
    ok = publishable(claims)
    contra = [c for c in claims if c["label"] == "contradicted" and c.get("reviewer")]
    head = f"{row['title']} ({row['board']} {row['id']}, score {row['total']})"
    if not ok:
        pending = sum(c["label"] == "not reviewed" for c in claims)
        return (f"I cannot tell from this posting whether it fits: {head}. "
                f"No claim is marked supported yet ({pending} not reviewed).")
    lines = [head] + [f"  supported: {c['claim']} — \"{c['excerpt']}\"" for c in ok]
    lines += [f"  contradicted: {c['claim']} — \"{c['excerpt']}\"" for c in contra]
    insufficient = [c for c in claims if c["label"] == "insufficient" and c.get("reviewer")]
    lines += [f"  I cannot tell: {c['claim']} (missing: {c['missing']})" for c in insufficient]
    return "\n".join(lines)
