"""The written rule from CONTRACT.md (R1-R4). Its output is a record: anyone can recompute it."""
import re

ROLE = re.compile(
    r"software engineer|software developer|full[\s-]?stack engineer|back[\s-]?end engineer|front[\s-]?end engineer",
    re.I,
)
SENIOR = re.compile(r"\b(senior|sr|staff|principal|lead|manager|head|director)\b", re.I)
# "3+ years", "5 years", "4-6 years", "1–4 years": the first number is the smallest in a range.
YEARS = re.compile(r"(\d+)\s*\+?\s*(?:(?:-|–|—|to)\s*\d+\s*)?\+?\s*years?\b", re.I)
NO_SPONSOR = re.compile(r"unable to sponsor|no sponsorship|not sponsor|without sponsorship", re.I)
US = {"usa", "us", "united states", "united states of america"}


def country(posting):
    return ((posting.get("address") or {}).get("postalAddress") or {}).get("addressCountry")


def years_asked(text):
    return [int(m.group(1)) for m in YEARS.finditer(text or "")]


def judge(posting, resume):
    title = posting.get("title", "")
    desc = posting.get("descriptionPlain", "")
    n_exp = len(resume.get("experience", []))
    out = {"posting_id": posting["id"], "title": title, "kind": "record"}

    def fail(check, why, resume_fields, posting_fields):
        out.update(verdict="not_relevant", failed_check=check, justification=why,
                   resume_fields=resume_fields, posting_fields=posting_fields)
        return out

    if not ROLE.search(title):
        return fail("R1", f"title '{title}' is not a software engineering role; "
                    f"resume degree is '{resume['education'][0]['degree']}'",
                    ["education[0].degree"], ["title"])
    m = SENIOR.search(title)
    if m:
        return fail("R2", f"title has seniority word '{m.group(1)}'; resume has "
                    f"{n_exp} experience entries (new grad)", ["experience"], ["title"])
    big = [y for y in years_asked(desc) if y >= 3]
    if big:
        return fail("R2", f"description asks for {big[0]}+ years; resume has "
                    f"{n_exp} experience entries (new grad)", ["experience"], ["descriptionPlain"])
    c = country(posting)
    if not c or c.strip().lower() not in US:
        return fail("R3", f"posting country is {c!r}, not the US; resume location is "
                    f"'{resume['personal']['location']}'",
                    ["personal.location"], ["address.postalAddress.addressCountry"])
    needs = (resume.get("work_authorization") or {}).get("needs_sponsorship") is True
    s = NO_SPONSOR.search(desc)
    if needs and s:
        return fail("R4", f"description says '{s.group(0)}' and resume needs sponsorship",
                    ["work_authorization.needs_sponsorship"], ["descriptionPlain"])
    out.update(verdict="relevant", failed_check=None,
               justification=f"software title '{title}' with no seniority word and no 3+ years asked, "
                             f"US country '{c}', no sponsorship blocker; fits resume degree "
                             f"'{resume['education'][0]['degree']}' and {n_exp} experience entries",
               resume_fields=["education[0].degree", "experience", "work_authorization.needs_sponsorship"],
               posting_fields=["title", "descriptionPlain", "address.postalAddress.addressCountry"])
    return out
