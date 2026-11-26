"""Two ATS providers (Greenhouse, Ashby): URL, parse, and the repeat-rule key.

Pattern adapted from the Reallocation Engine's scripts/ats/providers (greenhouse.mjs, ashby.mjs),
but keeping each posting's id (the RE providers drop it) and refusing malformed bodies.
"""
from __future__ import annotations

import html
import json
import re
from urllib.parse import quote, unquote

ATS = ("greenhouse", "ashby")


class Malformed(Exception):
    pass


def board_key(ats: str, slug: str) -> str:
    """Repeat rule (GATE §3): same ATS + same slug after URL-decoding and case-folding."""
    return f"{ats.casefold()}/{unquote(slug).strip().casefold()}"


def board_url(ats: str, slug: str, content: bool = False) -> str:
    """JS3: content=True adds Greenhouse's ?content=true (the posting text). Ashby always sends descriptionPlain."""
    name = quote(unquote(slug), safe="")
    if ats == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{name}/jobs" + ("?content=true" if content else "")
    if ats == "ashby":
        return f"https://api.ashbyhq.com/posting-api/job-board/{name}"
    raise ValueError(f"unknown ats {ats!r}")


def html_to_text(s: str) -> str:
    """Greenhouse `content` is HTML, itself HTML-escaped (&lt;p&gt;). Unescape, drop tags, unescape entities."""
    s = html.unescape(s)
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6])>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"[ \t\r\f\v]+", " ", html.unescape(s)).strip()


def parse(ats: str, body: bytes) -> list[dict]:
    """Normalize to [{id, title, location, url, updated, text}] or raise Malformed. Never invents a field:
    `text` is None when the response carries no posting text (JS2's runs had none for Greenhouse)."""
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise Malformed(f"not JSON: {e}") from e
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise Malformed("expected an object with a 'jobs' list")
    out = []
    for j in data["jobs"]:
        if not isinstance(j, dict) or j.get("id") in (None, ""):
            raise Malformed("a job without an id")
        if ats == "greenhouse":
            loc = (j.get("location") or {}).get("name", "") if isinstance(j.get("location"), dict) else ""
            out.append({"id": str(j["id"]), "title": j.get("title", ""), "location": loc,
                        "url": j.get("absolute_url", ""), "updated": j.get("updated_at"),
                        "text": html_to_text(j["content"]) if isinstance(j.get("content"), str) and j["content"].strip() else None})
        else:
            locs = [j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or [] if isinstance(s, dict)]
            loc = "; ".join(x for x in locs if x) + ("; Remote" if j.get("isRemote") else "")
            out.append({"id": str(j["id"]), "title": j.get("title", ""), "location": loc,
                        "url": j.get("jobUrl", ""), "updated": j.get("publishedAt"),
                        "text": j["descriptionPlain"] if isinstance(j.get("descriptionPlain"), str) and j["descriptionPlain"].strip() else None})
    return out
