"""Label each claim in a shortlist justification against the posting's own text (FILTER.md section 2).

supported     a quoted span of the posting says it
contradicted  a quoted span of the posting says the opposite
insufficient  the text neither says it nor denies it -> the agent says "I cannot tell"

Absence is never support: a posting that is silent about sponsorship does not support "will sponsor".
Deterministic and recomputable; no model is called."""
import re

from . import rule

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                "nine": 9, "ten": 10}
_NUM = r"(\d+|" + "|".join(NUMBER_WORDS) + r")"
# A range ("2–12+ years", "1-4 years") asks for its first number at minimum; same reading as rule.YEARS.
YEARS = re.compile(r"\b" + _NUM + r"\s*\+?\s*(?:(?:-|–|—|to)\s*" + _NUM + r"\s*)?\+?\s*years?\b", re.I)
OFFER = re.compile(r"visa sponsorship (?:is )?(?:available|provided|offered)|will (?:provide |offer )?(?:visa )?sponsor|"
                   r"we (?:do )?sponsor (?:visas|work)|offers? (?:visa )?sponsorship|sponsors? (?:h-?1b|work visas)", re.I)
NO_CLEARANCE = re.compile(r"no (?:security )?clearance (?:is )?(?:required|needed|necessary)|"
                          r"clearance (?:is )?not required|does not require (?:a )?(?:security )?clearance", re.I)
AI_TEXT = re.compile(r"\bLLMs?\b|large language model|generative ai|\bgenai\b|ai agents?|agentic", re.I)
# Skills the persona lists as shipped (skills.familiar_with_not_shipped is deliberately left out).
CASE_SENSITIVE = {"Go", "SQL", "AWS", "GCP"}
SPECIAL = {"Next.js": r"Next\.js", "Tailwind CSS": r"Tailwind", "PostgreSQL": r"Postgres(?:QL)?",
           "Kubernetes": r"Kubernetes|k8s"}


def _snip(text, m, pad=60):
    return "..." + re.sub(r"\s+", " ", text[max(0, m.start() - pad):m.end() + pad]).strip() + "..."


def _claim(name, text, label, quote="", why=""):
    return {"claim": name, "statement": text, "label": label, "quote": quote, "why": why}


def _num(token):
    return int(token) if token.isdigit() else NUMBER_WORDS[token.lower()]


def _go(text):
    """'Go' the language: the capitalised word next to a comma, slash or bracket, or 'Golang'.
    'go-to-market' and 'Go to market' do not count."""
    m = re.search(r"\bGolang\b", text)
    if m:
        return m
    for m in re.finditer(r"(?<![\w-])Go(?![\w-])", text):
        before = text[:m.start()].rstrip()[-1:]
        after = text[m.end():].lstrip()[:1]
        if before in ",/(" or after in ",/)":
            return m
    return None


# stack_fit v2 (Vrajesh's hand labels, claim-check items 5, 18, 24): only technologies in the persona's documented
# shipped project count. Option lists ('or', slashes) still count, by Vrajesh's decision.
EXTRA_TECH = ["GraphQL", "DigitalOcean"]  # named in project bullets but not in the skills lists


def _matches(name, text, strict_go=True):
    """All mentions of a technology. 'Go' is strict in posting text ('go-to-market' is not the language)."""
    if name == "Go":
        if not strict_go:
            return list(re.finditer(r"\bGo\b", text))
        out = list(re.finditer(r"\bGolang\b", text, re.I))
        for m in re.finditer(r"(?<![\w-])Go(?![\w-])", text):
            before = text[:m.start()].rstrip()[-1:]
            after = text[m.end():].lstrip()[:1]
            if before in ",/(" or after in ",/)":
                out.append(m)
        return sorted(out, key=lambda m: m.start())
    pat = SPECIAL.get(name, r"\b" + re.escape(name) + r"\b")
    return list(re.finditer(pat, text, 0 if name in CASE_SENSITIVE else re.I))


def shipped_skills(resume):
    """Skills (and extra tech) that appear in the persona's project bullets."""
    sk = resume.get("skills", {})
    names = []
    for group in ("languages", "frontend", "database_cloud", "devops_cicd"):
        names += sk.get(group, [])
    bullets = " ".join(b for p in resume.get("projects", []) for b in p.get("bullets", []))
    return [n for n in names + EXTRA_TECH if _matches(n, bullets, strict_go=False)]


def label_claims(posting, resume):
    title = posting.get("title", "")
    text = posting.get("descriptionPlain") or ""
    out = []

    m = rule.ROLE.search(title)
    out.append(_claim("role", "The title is a target role.", "supported" if m else "insufficient",
                      f'title: "{title}"' if m else ""))

    found = [(_num(x.group(1)), x) for x in YEARS.finditer(text)]
    big = [(n, x) for n, x in found if n >= 3]
    if big:
        out.append(_claim("early_career", "The posting asks for fewer than 3 years of experience.", "contradicted",
                          _snip(text, big[0][1])))
    elif found:
        out.append(_claim("early_career", "The posting asks for fewer than 3 years of experience.", "supported",
                          _snip(text, found[0][1])))
    else:
        out.append(_claim("early_career", "The posting asks for fewer than 3 years of experience.", "insufficient",
                          why="the text states no years of experience"))

    loc = (posting.get("location") or "").strip()
    c = rule.country(posting)
    if c and c.strip().lower() in rule.US:
        out.append(_claim("us_location", "The role is in the US.", "supported", f'location: "{loc or c}"'))
    elif loc or c:
        out.append(_claim("us_location", "The role is in the US.", "contradicted", f'location: "{loc or c}"'))
    else:
        out.append(_claim("us_location", "The role is in the US.", "insufficient", why="no location in the posting"))

    s = rule.NO_SPONSOR.search(text)
    o = OFFER.search(text)
    if s:
        out.append(_claim("sponsorship", "The employer will sponsor a visa.", "contradicted", _snip(text, s)))
    elif o:
        out.append(_claim("sponsorship", "The employer will sponsor a visa.", "supported", _snip(text, o)))
    else:
        out.append(_claim("sponsorship", "The employer will sponsor a visa.", "insufficient",
                          why="the text says nothing about sponsoring visas"))

    n = NO_CLEARANCE.search(text)
    r = rule.CLEARANCE.search(text)
    if n:
        out.append(_claim("no_clearance", "No security clearance is required.", "supported", _snip(text, n)))
    elif r:
        out.append(_claim("no_clearance", "No security clearance is required.", "contradicted", _snip(text, r)))
    else:
        out.append(_claim("no_clearance", "No security clearance is required.", "insufficient",
                          why="the text does not mention a clearance"))

    hits = []
    for name in shipped_skills(resume):
        found = _matches(name, text)
        if found:
            hits.append((name, found[0]))
    stmt = "The posting names a technology from Rohan's documented shipped project, (option lists count)."
    if hits:
        out.append(_claim("stack_fit", stmt, "supported",
                          " | ".join(_snip(text, m, 25) for _, m in hits[:3])) | {"skills": [n for n, _ in hits]})
    else:
        out.append(_claim("stack_fit", stmt, "insufficient",
                          why="no shipped technology appears as a stated need (skills listed on the resume but not shipped do not count)"))

    if re.search(r"\bai\b|\bllm\b", title, re.I):
        a = AI_TEXT.search(text)
        out.append(_claim("ai_focus", "The work involves building with LLMs or AI agents.",
                          "supported" if a else "insufficient", _snip(text, a) if a else "",
                          "" if a else "the title says AI but the text names no LLM or agent work"))
    return out
