"""The rule judge: a record anyone can recompute by hand (CONTRACT.md: The rule)."""
import re

DISQUALIFYING_WORDS = ("Staff", "Principal", "Director", "Manager", "Head of",
                       "Intern", "PhD", "Contract", "Temporary")
TITLE_MATCH_MIN_SKILLS = 3   # Step 4 (a)
STRONG_MIN_SKILLS = 4        # Step 4 (b): "more than 3"


def whole_word(term: str) -> re.Pattern:
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", re.IGNORECASE)


def judge(posting: dict, resume: dict) -> dict:
    title = posting["title"]

    # Step 1: disqualify, and stop checking.
    disq = [w for w in DISQUALIFYING_WORDS if whole_word(w).search(title)]
    if disq:
        return {
            "id": posting["id"],
            "verdict": "not_relevant",
            "branch": "disqualified",
            "disqualifying_words": disq,
            "title_matches": [],
            "skills_found": [],
            "cited_resume_fields": ["seniority"],
            "cited_posting_fields": ["title"],
            "because": f'title "{title}" contains disqualifying word(s): {", ".join(disq)}',
        }

    # Step 2: title contains a target_titles phrase (case-insensitive).
    title_matches = [t for t in resume["target_titles"] if t.lower() in title.lower()]
    # Step 3: skills found in content as whole words (case-insensitive).
    skills_found = [s for s in resume["skills"] if whole_word(s).search(posting["content_text"])]
    n = len(skills_found)

    # Step 4: verdict.
    if title_matches and n >= TITLE_MATCH_MIN_SKILLS:
        verdict, branch = "relevant", "a: title match and >=3 skills"
    elif not title_matches and n >= STRONG_MIN_SKILLS:
        verdict, branch = "relevant", "b: no title match but >=4 skills"
    else:
        verdict, branch = "not_relevant", "neither (a) nor (b)"

    title_part = (f'target_titles "{title_matches[0]}" in title' if title_matches
                  else f'no target_titles phrase in title "{title}"')
    skills_part = f"skills in content ({n}/{len(resume['skills'])}): {', '.join(skills_found) or 'none'}"
    return {
        "id": posting["id"],
        "verdict": verdict,
        "branch": branch,
        "disqualifying_words": [],
        "title_matches": title_matches,
        "skills_found": skills_found,
        "cited_resume_fields": ["target_titles", "skills"],
        "cited_posting_fields": ["title", "content"],
        "because": f"{title_part}; {skills_part} -> rule {branch}",
    }


def judge_all(postings: list[dict], resume: dict) -> dict[str, dict]:
    """Results keyed by posting id, never by position (guards against W1)."""
    return {p["id"]: judge(p, resume) for p in postings}
