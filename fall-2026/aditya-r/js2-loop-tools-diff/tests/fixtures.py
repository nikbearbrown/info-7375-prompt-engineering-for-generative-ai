"""SYNTHETIC test fixtures — constructed for tests, NOT real postings and NOT Claude responses."""
import html
import json

PERSONA = {
    "_comment": "SYNTHETIC test copy of the fictional persona's structure.",
    "personal": {"name": "Test Persona", "email": "test.persona@example.com", "phone": "(617) 555-0100"},
    "skills": {
        "languages": ["Python", "SQL"],
        "data_bi": ["Databricks", "Power BI"],
        "backend_automation": ["LangGraph"],
        "database_cloud": ["Delta Lake", "AWS"],
    },
}


def posting(pid, title, description_html):
    """Greenhouse-shaped posting; `content` is entity-escaped HTML like the real API."""
    return {
        "id": pid,
        "title": title,
        "content": html.escape(description_html),
        "location": {"name": "Synthetic City"},
        "departments": [{"name": "Synthetic Dept"}],
        "absolute_url": f"https://example.invalid/jobs/{pid}",
    }


# Contrasting outcomes with distinct evidence (used for wrong version 1).
RELEVANT = posting(101, "Software Engineer II", "<p>You will write Python and SQL every day.</p>")
NOT_RELEVANT = posting(202, "Account Executive", "<p>Grow revenue with LangGraph customers. Experience with Databricks.</p>")
NEAR_MISS = posting(303, "Senior Data Engineer", "<p>Python, SQL and Databricks pipelines.</p>")


def board(*postings):
    return json.dumps({"jobs": list(postings), "meta": {"total": len(postings)}}).encode()


def valid_response(p, persona=PERSONA):
    """A correct judgment for the synthetic posting, built from the rule (SYNTHETIC)."""
    from agent.rules import evaluate, html_to_text

    rec = evaluate(p, persona)
    a, b, c = rec["checks"]["A_role_phrase"], rec["checks"]["B_no_excluded_term"], rec["checks"]["C_shared_skills"]
    text = html_to_text(p["content"])
    skills = []
    for s in c["shared"]:
        field = "description"
        idx = text.lower().find(s["skill"])
        skills.append({"skill": s["skill"], "resume_field": s["resume_fields"][0], "posting_field": field,
                       "quote": text[idx: idx + len(s["skill"])]})
    return json.dumps({
        "posting_id": p["id"],
        "verdict": rec["verdict"],
        "role_phrase": {"pass": a["pass"], "matched": a["matched"][0] if a["matched"] else None},
        "excluded_terms": {"pass": b["pass"], "found": b["found"]},
        "shared_skills": {"pass": c["pass"], "skills": skills},
        "explanation": "Based on the title and description and the résumé skills arrays.",
    })


def fake_judge_from(responses_by_id):
    """A judge stand-in that returns pre-built text (no model is called)."""
    def judge(p, resume):
        return {"response_text": responses_by_id[p["id"]], "models_used": ["SYNTHETIC"], "session_id": None,
                "prompt_version": "test", "prompt_sha256": "test"}
    return judge
