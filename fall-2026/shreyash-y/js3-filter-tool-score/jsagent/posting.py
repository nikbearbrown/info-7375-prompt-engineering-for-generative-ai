"""Turn one Greenhouse job into the plain fields the rule reads (INTERPRETATIONS.md,
'Reading a posting'). The raw job is kept untouched in runs/raw/; this is a view of it."""
import html
import re


def content_text(escaped_html):
    """Greenhouse content is HTML escaped once: unescape, strip tags, unescape, squash."""
    if not escaped_html:
        return ""
    text = html.unescape(escaped_html)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def normalize(job, board_token):
    return {
        "id": job["id"],
        "board_token": board_token,
        "title": (job.get("title") or "").strip(),
        "departments": [d["name"] for d in job.get("departments") or [] if d.get("name")],
        "location": ((job.get("location") or {}).get("name") or "").strip(),
        "offices": [o["name"] for o in job.get("offices") or [] if o.get("name")],
        "content": content_text(job.get("content")),
        "absolute_url": job.get("absolute_url"),
        "updated_at": job.get("updated_at"),
    }
