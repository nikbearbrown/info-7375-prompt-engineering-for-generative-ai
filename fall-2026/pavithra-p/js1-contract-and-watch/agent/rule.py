"""The written rule from CONTRACT.md. Its verdict is a record: anyone can recompute it by hand."""
import html
import re
from dataclasses import dataclass, field

from .resume import SKILL_LISTS

ROLE_WORDS = ("Software", "Backend", "Back-end", "Full-stack", "Full Stack", "Fullstack", "Cloud", "AI")
EXPERIENCE_WORDS = ("Senior", "Sr", "Staff", "Principal", "Lead", "Manager", "Director", "Head",
                    "Distinguished", "Intern")
US_WORDS = ("United States", "USA", "US")
MAX_YEARS = 3  # a description asking for 3 or more years fails rule 3
# Decimals are read whole: "1.5+ years" is 1.5, not 5 (fixed 2026-10-31 after experiment 2).
YEARS = re.compile(r"(?<![\d.])(\d{1,2}(?:\.\d+)?)\s*\+?\s*years\b", re.IGNORECASE)


def find_words(text, words):
    """Whole words, ignoring case: "Java" does not match "JavaScript"."""
    return [w for w in words if re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", text, re.IGNORECASE)]


def description_text(job):
    text = html.unescape(job.get("content") or "")
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


def resume_skills(resume):
    """Each skill with the résumé field it comes from, in résumé order."""
    seen, out = set(), []
    for name in SKILL_LISTS:
        for skill in resume["skills"][name]:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                out.append((skill, f"skills.{name}"))
    return out


@dataclass
class RuleVerdict:
    job_id: int
    verdict: str
    checks: dict
    matched_skills: list
    reason: str
    posting_fields: list = field(default_factory=lambda: ["title", "description", "location"])
    resume_fields: list = field(default_factory=list)
    kind: str = "record (written rule)"


def judge(job, resume):
    title = job.get("title", "")
    location = (job.get("location") or {}).get("name", "")
    description = description_text(job)

    role_words = find_words(title, ROLE_WORDS)
    role_ok = bool(find_words(title, ("Engineer",))) and bool(role_words)

    skills = resume_skills(resume)
    matched = [(s, src) for s, src in skills if find_words(description, (s,))]
    skills_ok = len(matched) >= 2

    title_words = find_words(title, EXPERIENCE_WORDS)
    years = [float(n) for n in YEARS.findall(description)]
    too_many_years = [n for n in years if n >= MAX_YEARS]
    experience_ok = not title_words and not too_many_years

    us_words = find_words(location, US_WORDS)
    location_ok = bool(us_words)

    checks = {"role": role_ok, "skills": skills_ok, "experience": experience_ok, "location": location_ok}
    verdict = "Relevant" if all(checks.values()) else "Not Relevant"

    parts = [
        f"role {'met' if role_ok else 'not met'}: title \"{title}\""
        + (f" has \"Engineer\" and {', '.join(role_words)}" if role_ok else " lacks \"Engineer\" plus a role word"),
        f"skills {'met' if skills_ok else 'not met'}: description has {len(matched)} of the résumé's skills"
        + (f" ({', '.join(f'{s} from {src}' for s, src in matched)})" if matched else ""),
        f"experience {'met' if experience_ok else 'not met'} (the 0–2 year limit set for the résumé's experience): "
        + (f"title has {', '.join(title_words)}" if title_words else "title has no seniority word")
        + (f"; description asks for {', '.join(f'{n:g}' for n in too_many_years)} years" if too_many_years else ""),
        f"location {'met' if location_ok else 'not met'}: location \"{location}\""
        + (f" has {', '.join(us_words)}" if location_ok else " has no United States, USA or US"),
    ]
    resume_fields = sorted({src for _, src in matched}) + ["experience"]
    return RuleVerdict(job["id"], verdict, checks, [s for s, _ in matched], f"{verdict}. " + "; ".join(parts) + ".",
                       resume_fields=resume_fields)


def judge_all(jobs, resume):
    return [judge(job, resume) for job in jobs]
