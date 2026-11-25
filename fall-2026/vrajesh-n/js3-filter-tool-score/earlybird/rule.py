"""The written rule from FILTER.md v1 (R1-R5 plus cannot_tell). Its output is a record: anyone can recompute it."""
import re

# FILTER.md v1 section 1. Vrajesh's list plus the JS2 words. Title only: description words never count.
ROLE = re.compile(
    r"software engineer|software developer|full[\s-]?stack (?:software )?engineer|"
    r"back[\s-]?end (?:software )?engineer|front[\s-]?end (?:software )?engineer|"
    r"java engineer|python engineer|\.net engineer|react developer|ui\s*/\s*ux developer|"
    r"\bai engineer|\bllm engineer|solutions architect|forward[\s-]deployed engineer",
    re.I,
)
# FILTER.md v1: machine learning roles are not wanted, AI engineer roles are.
ML = re.compile(r"(?i:machine[\s-]learning)|\bML\b")
SENIOR = re.compile(r"\b(senior|sr|staff|principal|lead|manager|head|director)\b", re.I)
# "3+ years", "5 years", "4-6 years", "1–4 years": the first number is the smallest in a range.
YEARS = re.compile(r"(\d+)\s*\+?\s*(?:(?:-|–|—|to)\s*\d+\s*)?\+?\s*years?\b", re.I)
NO_SPONSOR = re.compile(r"unable to sponsor|no sponsorship|not sponsor|without sponsorship", re.I)
# FILTER.md R5. A negation ("no security clearance") must not trigger it.
CLEARANCE = re.compile(r"(?<!no )(?<!not )(?<!without )(?:security clearance|ts/sci|top secret)", re.I)
US = {"usa", "us", "united states", "united states of america"}


def country(posting):
    return ((posting.get("address") or {}).get("postalAddress") or {}).get("addressCountry")


def years_asked(text):
    return [int(m.group(1)) for m in YEARS.finditer(text or "")]


def judge(posting, resume):
    title = posting.get("title", "")
    desc = (posting.get("descriptionPlain") or "").strip()
    n_exp = len(resume.get("experience", []))
    out = {"posting_id": posting["id"], "title": title, "kind": "record"}

    def fail(check, why, resume_fields, posting_fields):
        out.update(verdict="not_relevant", failed_check=check, justification=why,
                   resume_fields=resume_fields, posting_fields=posting_fields)
        return out

    def cannot_tell(field):
        out.update(verdict="cannot_tell", failed_check=None,
                   justification=f"I cannot tell: the posting's {field} is not mentioned (FILTER.md section 2)",
                   resume_fields=[], posting_fields=[field])
        return out

    if not ROLE.search(title):
        return fail("R1", f"title '{title}' is not one of the FILTER.md role phrases",
                    ["education[0].degree"], ["title"])
    if ML.search(title):
        return fail("R1", f"title '{title}' is a machine learning role; FILTER.md excludes ML roles",
                    ["education[0].degree"], ["title"])
    m = SENIOR.search(title)
    if m:
        return fail("R2", f"title has seniority word '{m.group(1)}'; resume has "
                    f"{n_exp} experience entries (new grad)", ["experience"], ["title"])
    if not desc:
        return cannot_tell("description")
    big = [y for y in years_asked(desc) if y >= 3]
    if big:
        return fail("R2", f"description asks for {big[0]}+ years; resume has "
                    f"{n_exp} experience entries (new grad)", ["experience"], ["descriptionPlain"])
    c = country(posting)
    if not c and not (posting.get("location") or "").strip():
        return cannot_tell("location")
    if not c or c.strip().lower() not in US:
        return fail("R3", f"posting country is {c!r} (location {posting.get('location')!r}), not the US; "
                    f"resume location is '{resume['personal']['location']}'",
                    ["personal.location"], ["address.postalAddress.addressCountry"])
    needs = (resume.get("work_authorization") or {}).get("needs_sponsorship") is True
    s = NO_SPONSOR.search(desc)
    if needs and s:
        return fail("R4", f"description says '{s.group(0)}' and resume needs sponsorship",
                    ["work_authorization.needs_sponsorship"], ["descriptionPlain"])
    cl = CLEARANCE.search(desc)
    if cl:
        return fail("R5", f"description mentions '{cl.group(0)}'; a clearance needs US citizenship and the "
                    f"resume needs sponsorship", ["work_authorization.needs_sponsorship"], ["descriptionPlain"])
    out.update(verdict="relevant", failed_check=None,
               justification=f"role title '{title}' with no seniority word and no 3+ years asked, "
                             f"US country '{c}', no sponsorship or clearance blocker; fits resume degree "
                             f"'{resume['education'][0]['degree']}' and {n_exp} experience entries",
               resume_fields=["education[0].degree", "experience", "work_authorization.needs_sponsorship"],
               posting_fields=["title", "descriptionPlain", "address.postalAddress.addressCountry"])
    return out
