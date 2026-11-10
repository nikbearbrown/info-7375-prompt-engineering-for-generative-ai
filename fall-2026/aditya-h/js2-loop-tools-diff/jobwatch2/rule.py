"""JS1 rule title-us-v1 (../js1-contract-and-watch/CONTRACT.md), applied to normalized postings."""
import re

RULE_ID = "title-us-v1"
TITLE_PHRASES = ("product manager", "product analyst", "product strategy", "product operations", "product owner")
US_MARKERS = ("US", "USA", "United States", "Remote-US", "US-Remote", "US Remote", "San Francisco", "SF",
              "New York", "New-York", "NYC", "NY", "Seattle", "SEA", "Chicago", "Atlanta", "Boston")


def phrase_match(phrase, text):
    return re.search(r"(?<![A-Za-z])" + re.escape(phrase) + r"(?![A-Za-z])", text, re.IGNORECASE) is not None


def verdict(p):
    """The rule's verdict alone; the résumé only supplies the cited fields, not the decision."""
    return judge(p, None)["verdict"]


def judge(p, resume):
    title = " ".join(p["title"].lower().split())
    t_hit = next((ph for ph in TITLE_PHRASES if phrase_match(ph, title)), None)
    loc = p["location_name"] if p["location_name"].strip().upper() != "N/A" else ""
    m_hit = next((m for m in US_MARKERS if loc and phrase_match(m, loc)), None)
    us = p["us_office"] or m_hit is not None
    verdict = "relevant" if t_hit and us else "not_relevant"
    reason = (f"title {'contains ' + repr(t_hit) if t_hit else 'has no product-family phrase'}; "
              f"location {'US (office/country)' if p['us_office'] else ('US marker ' + repr(m_hit)) if m_hit else 'not US / unknown'}")
    cited = {} if resume is None else {"experience[0].title": resume["experience"][0]["title"],
                                       "personal.location": resume["personal"]["location"]}
    return {"verdict": verdict, "reason": reason,
            "resume_fields": cited,
            "posting_fields": {"title": p["title"], "location_name": p["location_name"], "us_office": p["us_office"]}}
