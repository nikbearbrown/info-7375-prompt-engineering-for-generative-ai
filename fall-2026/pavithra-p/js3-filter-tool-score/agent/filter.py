"""The filter in FILTER.md as code. It reads one filter file (filters/v*.json) so every word list, weight and threshold
lives in a file I can diff, and every verdict is a record: anyone can recompute it from the posting and the file.

Verdicts: "keep", "reject", "cannot tell" (a field the filter needs is missing; it does not guess).
"""
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import rule

KEEP, REJECT, CANNOT_TELL = "keep", "reject", "cannot tell"


def load_filter(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("version", "us_words", "seniority_words", "max_years", "role_words", "plain_role_words", "points",
                "skill_cap", "skill_lists", "threshold", "close_call_scores"):
        if key not in data:
            raise ValueError(f"filter file {path} has no {key!r}")
    # Optional rules, off unless the filter file sets them. Each one is a change recorded in FILTER.md's change log.
    data.setdefault("us_place_words", [])          # extra G1 words, e.g. US cities written without a country
    data.setdefault("body_seniority_gate", False)  # G4: reject when the text asks for a senior engineer
    data.setdefault("case_sensitive_skills", [])   # skills matched only as written, e.g. "Helm" but not "HELM"
    return data


SENIOR_IN_TEXT = re.compile(r"\bsenior\s+(?:\w+\s+){0,2}(?:engineer|developer)s?\b", re.IGNORECASE)


def find_words(text, words):
    """Whole words, ignoring case (inherited from JS1): "Java" does not match "JavaScript"."""
    return rule.find_words(text, words)


def skill_in(description, skill, f, words=find_words):
    if skill in f.get("case_sensitive_skills", []):
        return bool(re.search(rf"(?<![\w-]){re.escape(skill)}(?![\w-])", description))
    return bool(words(description, (skill,)))


def resume_skills(resume, lists):
    seen, out = set(), []
    for name in lists:
        for skill in resume["skills"][name]:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                out.append(skill)
    return out


def years_asked(description):
    """Each number of years the description asks for; a range counts as its lowest number (JS2, 0ecb3d5)."""
    return [min(float(low), float(high or low)) for low, high in rule.YEARS.findall(description)]


@dataclass
class Decision:
    board: str
    job_id: str
    title: str
    location: str
    url: str
    verdict: str
    score: int
    close_call: bool
    gates: dict
    parts: dict
    reason: str
    filter_version: str
    missing: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def decide(job, board, resume, f, words=find_words):
    """One posting through the gates and the score. `words` is the matcher; only the wrong versions change it."""
    title = job.get("title") or ""
    location = (job.get("location") or {}).get("name") or ""
    description = rule.description_text(job)
    base = dict(board=board, job_id=str(job.get("id")), title=title, location=location, url=job.get("url") or "",
                filter_version=f["version"])

    missing = [name for name, value in (("description", description), ("location", location)) if not value.strip()]
    if missing:
        return Decision(**base, verdict=CANNOT_TELL, score=0, close_call=False, gates={}, parts={}, missing=missing,
                        reason=f"cannot tell: the posting has no {' and no '.join(missing)}, so "
                               + ("G1 cannot be checked" if "location" in missing else "")
                               + ("; " if len(missing) == 2 else "")
                               + ("G3 and S2 cannot be checked" if "description" in missing else ""))

    us = words(location, f["us_words"]) or words(location, f.get("us_place_words", []))
    senior = words(title, f["seniority_words"])
    too_many = [n for n in years_asked(description) if n >= f["max_years"]]
    gates = {
        "G1 location": {"passed": bool(us), "evidence": f"location \"{location}\"" + (f" has {', '.join(us)}" if us else " names no US word")},
        "G2 seniority": {"passed": not senior, "evidence": f"title has {', '.join(senior)}" if senior else "title has no seniority word"},
        "G3 years": {"passed": not too_many, "evidence": f"description asks for {', '.join(f'{n:g}' for n in too_many)} years" if too_many else f"no ask of {f['max_years']} or more years"},
    }
    if f.get("body_seniority_gate"):
        senior_text = SENIOR_IN_TEXT.findall(description) and SENIOR_IN_TEXT.search(description).group(0)
        gates["G4 senior in text"] = {"passed": not senior_text,
                                      "evidence": f"description says \"{senior_text}\"" if senior_text else "description asks for no senior engineer"}
    role_words = words(title, f["role_words"])
    plain = words(title, f["plain_role_words"])
    if words(title, ("Engineer",)) and role_words:
        role_points, role_ev = f["points"]["role_full"], f"title has Engineer and {', '.join(role_words)}"
    elif plain:
        role_points, role_ev = f["points"]["role_plain"], f"title has {', '.join(plain)} but no role word"
    else:
        role_points, role_ev = 0, "title has no Engineer or Developer"
    skills = [s for s in resume_skills(resume, f["skill_lists"]) if skill_in(description, s, f, words)]
    skill_points = min(len(skills), f["skill_cap"]) * f["points"]["skill"]
    parts = {"S1 role": {"points": role_points, "evidence": role_ev},
             "S2 skills": {"points": skill_points, "skills": skills}}
    score = role_points + skill_points

    failed = [name for name, g in gates.items() if not g["passed"]]
    if failed:
        verdict = REJECT
        reason = "reject: fails " + "; ".join(f"{n} ({gates[n]['evidence']})" for n in failed)
    elif score >= f["threshold"]:
        verdict = KEEP
        reason = f"keep: passes every gate; score {score} = role {role_points} ({role_ev}) + skills {skill_points} ({', '.join(skills) or 'none'}), threshold {f['threshold']}"
    else:
        verdict = REJECT
        reason = f"reject: passes every gate but score {score} = role {role_points} ({role_ev}) + skills {skill_points} ({', '.join(skills) or 'none'}) is below the threshold {f['threshold']}"
    close = not failed and score in f["close_call_scores"]
    return Decision(**base, verdict=verdict, score=score, close_call=close, gates=gates, parts=parts, reason=reason)


def decide_all(postings, resume, f, words=find_words):
    """postings: (board, job) pairs, in collection order."""
    return [decide(job, board, resume, f, words) for board, job in postings]
