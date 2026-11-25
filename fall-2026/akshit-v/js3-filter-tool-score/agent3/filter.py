"""The filter, exactly as FILTER.md states it. One dict per version; nothing else decides.

Every number and word list below is copied from FILTER.md. A version changes only through
a FILTER.md version-log entry. Each result names every word that matched and where, so a
person can recompute the score by hand from the posting text.
"""
import re

EMPLOYERS = {"snowflake": "Snowflake", "figma": "Figma", "spotify": "Spotify"}   # F6: board -> employer name

V1_0 = {
    "version": "v1.0",
    # F2: disqualify by title word (inherited from JS1)
    "disqualify_title": ["Staff", "Principal", "Director", "Manager", "Head of", "Intern", "PhD",
                         "Contract", "Temporary"],
    # F3: disqualify by structured field (None = unknown, never a reject)
    "fulltime_values": {"ashby": {"FullTime"}, "lever": {"Permanent"}},
    # F4: role words in the title, +4 if any
    "role_words": ["Data Engineer", "Data Engineering", "Data Platform", "Data Infrastructure",
                   "Analytics Engineer", "Analytics Engineering", "ETL", "Data Integration", "Data Pipeline"],
    "role_weight": 4,
    # F5: topic groups in the content, +1 per group, at most +4
    "topic_groups": {
        "T1 pipelines": ["data pipeline", "data pipelines", "ETL", "ELT"],
        "T2 storage": ["data warehouse", "data warehouses", "data warehousing", "data lake", "data lakes", "lakehouse"],
        "T3 modeling": ["data modeling", "data model", "data models"],
        "T4 orchestration": ["orchestration"],
        "T5 streaming": ["streaming"],
        "T6 batch": ["batch processing", "batch job", "batch jobs"],
        "T7 quality": ["data quality"],
    },
    "topic_cap": 4,
    # F6: Jack's skills in the content, +1 each; the employer's own name never counts on its own board
    "skills": ["Python", "SQL", "Spark", "Airflow", "Kafka", "dbt", "Snowflake", "AWS"],
    "skip_employer_skill": True,
    # F7: keep if score >= threshold
    "threshold": 6,
    "keep_op": ">=",
    # F8: too little text -> "I cannot tell"
    "min_content_chars": 300,
    # F9: shortlist size and the close-call band (threshold +/- 1)
    "shortlist_size": 10,
    "close_band": 1,
}

VERSIONS = {"v1.0": V1_0}


def term_re(term: str) -> re.Pattern:
    """Whole-word, case-insensitive; spaces inside a phrase match any run of whitespace."""
    body = r"\s+".join(re.escape(w) for w in term.split())
    return re.compile(r"(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])", re.IGNORECASE)


def find(term: str, text: str):
    """First whole-word match as (start, end, matched text), or None."""
    m = term_re(term).search(text or "")
    return (m.start(), m.end(), m.group(0)) if m else None


def apply(posting: dict, cfg: dict = V1_0) -> dict:
    """Score one posting. Returns verdict "keep" | "reject" | "cannot_tell" with every match cited."""
    title, text = posting.get("title") or "", posting.get("content_text") or ""
    board_key = posting.get("board") or posting["id"].rsplit(":", 1)[0]
    ats, board = board_key.split(":", 1)
    out = {"id": posting["id"], "board": board_key, "title": title, "filter_version": cfg["version"],
           "disqualified_by": [], "role_hits": [], "topic_hits": {}, "skill_hits": {}, "skipped_skills": [],
           "role": 0, "topics": 0, "skills": 0, "score": 0, "verdict": None, "because": ""}

    # F8: too little text is not evidence of irrelevance
    if len(text) < cfg["min_content_chars"]:
        out.update(verdict="cannot_tell",
                   because=f"content is {len(text)} characters (< {cfg['min_content_chars']}): I cannot tell (F8/A1)")
        return out

    # F2: title words
    out["disqualified_by"] = [f"title:{w}" for w in cfg["disqualify_title"] if find(w, title)]
    # F3: structured employment type; missing = unknown
    et = posting.get("employment_type")
    allowed = cfg["fulltime_values"].get(ats)
    if allowed is not None and et is not None and et not in allowed:
        out["disqualified_by"].append(f"employment_type:{et}")

    # F4, F5, F6: always computed, so a disqualified posting still shows what it matched
    out["role_hits"] = [w for w in cfg["role_words"] if find(w, title)]
    out["role"] = cfg["role_weight"] if out["role_hits"] else 0
    for group, terms in cfg["topic_groups"].items():
        hit = next((find(t, text) for t in terms if find(t, text)), None)
        if hit:
            out["topic_hits"][group] = {"matched": hit[2], "at": hit[0]}
    out["topics"] = min(len(out["topic_hits"]), cfg["topic_cap"])
    employer = EMPLOYERS.get(board, "") if cfg["skip_employer_skill"] else ""
    for s in cfg["skills"]:
        if employer and s.lower() == employer.lower():
            out["skipped_skills"].append(f"{s} (employer name on its own board, F6)")
            continue
        hit = find(s, text)
        if hit:
            out["skill_hits"][s] = {"matched": hit[2], "at": hit[0]}
    out["skills"] = len(out["skill_hits"])
    out["score"] = out["role"] + out["topics"] + out["skills"]

    passes = out["score"] >= cfg["threshold"] if cfg["keep_op"] == ">=" else out["score"] > cfg["threshold"]
    parts = (f"role {out['role']} ({', '.join(out['role_hits']) or 'none'}) + topics {out['topics']} "
             f"({', '.join(out['topic_hits']) or 'none'}) + skills {out['skills']} "
             f"({', '.join(out['skill_hits']) or 'none'}) = {out['score']}")
    if out["disqualified_by"]:
        out.update(verdict="reject", because=f"disqualified by {', '.join(out['disqualified_by'])}; [{parts}]")
    elif passes:
        out.update(verdict="keep", because=f"{parts} {cfg['keep_op']} {cfg['threshold']}")
    else:
        out.update(verdict="reject", because=f"{parts}, below {cfg['threshold']}")
    return out


def rank_key(r: dict):
    """F9: score high first; ties -> role-word title, then more skills, then id."""
    return (-r["score"], -r["role"], -r["skills"], r["id"])


def run(postings, cfg: dict = V1_0) -> dict:
    results = {p["id"]: apply(p, cfg) for p in postings}
    kept = sorted((r for r in results.values() if r["verdict"] == "keep"), key=rank_key)
    for i, r in enumerate(kept, 1):
        r["rank"] = i
    return {"version": cfg["version"], "results": results, "ranked": [r["id"] for r in kept],
            "shortlist": [r["id"] for r in kept[:cfg["shortlist_size"]]]}


def is_close_call(r: dict, cfg: dict = V1_0) -> bool:
    """Scores within the band around the threshold (5, 6, 7 in v1.0), not disqualified, not abstained."""
    return (r["verdict"] != "cannot_tell" and not r["disqualified_by"]
            and abs(r["score"] - cfg["threshold"]) <= cfg["close_band"])
