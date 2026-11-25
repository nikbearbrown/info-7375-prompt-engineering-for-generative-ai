"""CONSTRUCTED postings for the JS3 tests. None of these is a real posting."""
from agent import config, filter as filt, resume

PERSONA = resume.load(config.RESUME)
SPEC = filt.load_filter(config.ROOT / "filters" / "v1.0.json")
SKILLS = filt.resume_skills(PERSONA, SPEC["skill_lists"])


def job(title="Software Engineer, Backend", location="Remote, US", content="<p>Python, Kafka and Redis</p>", id="c1"):
    return {"id": id, "title": title, "location": {"name": location}, "content": content,
            "url": f"https://example.invalid/{id}"}


def decide(**kw):
    return filt.decide(job(**kw), "constructed:board", PERSONA, SPEC)
