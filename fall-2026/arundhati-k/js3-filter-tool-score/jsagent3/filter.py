"""The FILTER.md rules as code. Every number comes from filter/<version>.json, never from this file."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

US_STATES = ("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY "
             "NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
US_WORDS = [
    "united states", "usa", "us-remote", "remote - us", "remote-us", "remote in the us", "us remote",
    "san francisco", "new york", "nyc", "seattle", "chicago", "boston", "austin", "denver", "atlanta",
    "los angeles", "washington dc", "south san francisco", "sf", "ny", "sea",
    "california", "washington", "texas", "illinois", "massachusetts", "colorado", "georgia",
]
NON_US_HINT = ["canada", "toronto", "vancouver", "dublin", "ireland", "london", "uk", "united kingdom", "india",
               "bangalore", "bengaluru", "singapore", "tokyo", "japan", "sydney", "australia", "paris", "berlin",
               "barcelona", "spain", "sao paulo", "brazil", "bucharest", "taiwan", "mexico", "seoul", "amsterdam",
               "netherlands", "germany", "france", "korea", "china", "hong kong", "melbourne", "stockholm"]


def load_rules(version="v1"):
    return json.loads((HERE / "filter" / f"{version}.json").read_text())


def role_match(title, rules):
    for rid, pat in rules["role"].items():
        if re.search(rf"(?i)\b{pat}\b", title or ""):
            return rid
    return None


def level_excluded(title, rules=None):
    pat = (rules or load_rules())["level_exclude"]
    m = re.search(f"(?i){pat}", title or "")
    return m.group(0) if m else None


def topic_hits(body, rules):
    if rules.get("topic_in_required_only"):
        from .evidence import sections
        body = "\n".join(ln for k, ln in sections(body) if k == "required")
    hits = []
    for tid, spec in rules["topic"].items():
        flags = re.I if "i" in spec.get("flags", "") else 0
        if re.search(spec["pattern"], body or "", flags):
            hits.append(tid)
    return hits


def is_us(location):
    """True / False / None (unknown). FILTER.md s3: no location is 'unknown', not 'not US'."""
    loc = (location or "").strip()
    if not loc or loc.lower() in {"n/a", "remote", "anywhere"}:
        return None
    low = loc.lower()
    tokens = re.findall(r"[a-z]+(?:-[a-z]+)?", low)
    upper_tokens = re.findall(r"\b[A-Z]{2}\b", loc)
    if any(w in low for w in ("united states", "us-remote", "remote - us", "remote-us", "remote in the us")):
        return True
    if any(t in US_STATES for t in upper_tokens if t != "US") or "US" in upper_tokens:
        return True
    for w in US_WORDS:
        if " " in w or "-" in w:
            if w in low:
                return True
        elif w in tokens:
            return True
    if any(w in low for w in NON_US_HINT):
        return False
    return False


def _years(body):
    from .evidence import min_required_years
    y = min_required_years(body)
    return y[0] if y else None


def decide(posting, rules):
    title, body = posting.get("title", ""), posting.get("body", "")
    role = role_match(title, rules)
    level = level_excluded(title, rules)
    topics = topic_hits(body, rules)
    score = len(topics)
    us = is_us(posting.get("location"))
    keep = False
    if not role:
        reason = "no role word in title"
    elif level:
        reason = f"level excluded: '{level}' in title"
    elif not body.strip():
        reason = "body missing"
    elif rules.get("us_required") and us is not True:
        reason = "location not US" if us is False else "location unknown"
    elif rules.get("max_required_years") is not None and _years(body) is not None \
            and _years(body) > rules["max_required_years"]:
        reason = f"requires {_years(body)}+ years > {rules['max_required_years']}"
    elif score < rules["threshold"]:
        reason = f"topic score {score} < threshold {rules['threshold']}"
    else:
        keep = True
        reason = f"role {role} + topic score {score} >= {rules['threshold']}"
    close = bool(role and not level and body.strip() and score in (rules["threshold"] - 1, rules["threshold"]))
    return {
        "id": posting.get("id"), "keep": keep, "reason": reason, "role": role, "level": level,
        "topics": topics, "topic_score": score, "us": us,
        "rank": score + (rules["us_bonus"] if us else 0), "close_call": close,
        "filter_version": rules["version"],
    }
