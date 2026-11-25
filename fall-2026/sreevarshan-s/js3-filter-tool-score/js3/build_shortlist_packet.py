"""Build the source-grounded shortlist review packet for the 47 passed postings.

Usage (from the repo root):
    python3 -m js3.build_shortlist_packet

Reads output/filter_results.json (to know which postings passed) and the JS2
raw files read-only (for each posting's own text), and writes
output/shortlist_packet.json and output/shortlist_packet.md.

Every label here is an AI-prepared *proposal* for human review, produced by
simple text rules (FILTER.md section 5):
- supported:    the posting's own text says it; the quoted span is included.
- contradicted: the posting's own text says the opposite; span included.
- insufficient: the field is absent, empty, or silent. This is the default.

Nothing is inferred from the company name, the job board, or what a title
usually implies. Python, ML experience, sponsorship, clearance, and years of
experience are labelled only from text that states them.

Re-running refuses to overwrite either output if it has been edited (same
guard as js3/sample_for_audit.py).
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

from js3.filter import ROLE_WORDS, SOFTWARE_ENGINEER, _find
from js3.sample_for_audit import OverwriteRefused, write_outputs

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "output" / "filter_results.json"
PACKET_JSON = ROOT / "output" / "shortlist_packet.json"
PACKET_MD = ROOT / "output" / "shortlist_packet.md"

RAW_DIR = Path("/Users/sreevarshansathiyamurthy/eng_job 2/output/raw")
SOURCES = {
    "databricks": RAW_DIR / "20261106T191045895303Z-greenhouse-databricks.json",
    "stripe": RAW_DIR / "20261106T191046089299Z-greenhouse-stripe.json",
    "spotify": RAW_DIR / "20261106T191046946413Z-lever-spotify.json",
}
BOARDS = ["databricks", "stripe", "spotify"]

CANDIDATE = (
    "Priya Nair (fictional): MS Information Systems, completed 2025-12; one "
    "8-month AI Engineer co-op; F-1 OPT, needs sponsorship; Boston, open to remote."
)

CLAIMS = [
    ("role_type", "The role is hands-on ML, AI, data engineering, or data science work."),
    ("us_location", "The job can be done from the US."),
    ("early_career_level", "The posting's stated level is open to an early-career candidate."),
    ("regular_role", "This is a regular (non-internship) position."),
    ("masters_ok", "A master's degree meets the posting's degree requirement."),
    ("years_within_reach", "The years of experience asked for are within Priya's (one 8-month co-op)."),
    ("asks_python", "The posting names Python as a skill it wants."),
    ("offers_sponsorship", "The employer will sponsor a work visa for this role."),
    ("no_clearance", "No security clearance is required."),
]

# Title words that name a job function other than hands-on engineering/science.
NON_ENGINEERING_FUNCTIONS = ["solutions architect", "developer advocate", "advocate", "sales"]
SENIOR_WORDS = ["senior staff", "senior", "sr.", "staff", "principal", "lead"]
EARLY_WORDS = ["new grad", "entry level", "entry-level", "junior", "intern"]

US_PLACES = [
    "united states", "california", "san francisco", "mountain view", "new york",
    "seattle", "wa", "ny", "boston", "massachusetts", "chicago", "remote - us",
]
NON_US_PLACES = [
    "bengaluru", "india", "amsterdam", "netherlands", "israel", "toronto",
    "london", "stockholm", "dublin", "canada",
]

SPONSOR_YES = [r"will sponsor", r"sponsorship (?:is )?available", r"offers? (?:visa )?sponsorship"]
SPONSOR_NO = [
    r"unable to sponsor", r"not (?:able to )?(?:provide|offer) (?:visa )?sponsorship",
    r"without (?:the need for )?(?:visa )?sponsorship", r"does not sponsor", r"cannot sponsor",
]
CLEARANCE_NO = [r"no (?:security )?clearance (?:is )?required", r"clearance is not required"]
CLEARANCE_YES = [r"(?:active|current|secret|top secret|ts/sci)[^.]{0,40}clearance", r"clearance[^.]{0,40}required"]


# ---------------------------------------------------------------- text utils

def _plain(text) -> str:
    if not text:
        return ""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", str(text))).split())


def _word(term: str) -> re.Pattern:
    return re.compile(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", re.IGNORECASE)


def _span(text: str, start: int, end: int, pad: int = 70) -> str:
    """Return the sentence-ish window around a match, trimmed for the packet."""
    left = max(0, start - pad)
    right = min(len(text), end + pad)
    prefix = "…" if left > 0 else ""
    suffix = "…" if right < len(text) else ""
    return prefix + text[left:right].strip() + suffix


def _first(patterns, fields: dict[str, str]):
    for name, text in fields.items():
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return name, _span(text, m.start(), m.end()), m
    return None


def _label(label: str, field: str | None = None, quote: str | None = None, note: str = "") -> dict:
    return {"proposed": label, "field": field, "quote": quote, "note": note, "my_label": ""}


# ----------------------------------------------------------- evidence model

def _evidence(board: str, job: dict) -> dict:
    """Collect the posting's own text, by field, plus what is missing."""
    if board == "spotify":
        cats = job.get("categories") or {}
        text_fields = {"descriptionPlain": _plain(job.get("descriptionPlain"))}
        for i, item in enumerate(job.get("lists") or []):
            if isinstance(item, dict):
                heading = " ".join(str(item.get("text") or "").split())
                text_fields[f"lists[{i}] {heading}"] = _plain(item.get("content"))
        text_fields["additionalPlain"] = _plain(job.get("additionalPlain"))
        structured = {
            "categories.location": cats.get("location"),
            "categories.allLocations": cats.get("allLocations"),
            "country": job.get("country"),
            "workplaceType": job.get("workplaceType"),
            "categories.commitment": cats.get("commitment"),
            "categories.team": cats.get("team"),
            "categories.department": cats.get("department"),
        }
        company = "Spotify"
        company_note = "Lever payload has no company field; company taken from the board name."
        url = job.get("hostedUrl")
        title = job.get("text") or ""
        missing = [k for k, v in text_fields.items() if not v]
        missing += [k for k, v in structured.items() if v in (None, "", [])]
    else:
        md = {
            m.get("name"): m.get("value")
            for m in job.get("metadata") or [] if isinstance(m, dict)
        }
        text_fields = {}  # Greenhouse descriptions were not fetched.
        structured = {"location.name": (job.get("location") or {}).get("name")}
        structured.update({f"metadata.{k}": v for k, v in md.items()})
        company = job.get("company_name") or board
        company_note = ""
        url = job.get("absolute_url")
        title = job.get("title") or ""
        missing = ["content (description not fetched: no responsibilities, qualifications, "
                   "skills, years, degree, sponsorship, or clearance text)"]
        missing += [k for k, v in structured.items() if v in (None, "", [], "N/A")]
    return {
        "company": company,
        "company_note": company_note,
        "url": url,
        "title": " ".join(title.split()),
        "text_fields": text_fields,
        "structured": structured,
        "missing_fields": missing,
    }


# ------------------------------------------------------------- claim rules

def _role_type(ev: dict) -> dict:
    title = ev["title"]
    functions = [f for f in NON_ENGINEERING_FUNCTIONS if _word(f).search(title)]
    roles = _find(ROLE_WORDS + [SOFTWARE_ENGINEER], title)
    if functions:
        return _label(
            "insufficient", "title", title,
            f"The title names the topic ({', '.join(roles)}) but the job function is "
            f"'{functions[0]}'; whether the work is hands-on engineering is not established.",
        )
    hits = [r for r in roles if r != SOFTWARE_ENGINEER]
    if hits:
        return _label("supported", "title", title, f"Title names the role: {', '.join(hits)}.")
    return _label("insufficient", "title", title, "No target role named in the title.")


def _us_location(board: str, ev: dict) -> dict:
    s = ev["structured"]
    if board == "spotify":
        where = next((v for k, v in ev["text_fields"].items() if "where" in k.lower()), "")
        loc = f"country={s.get('country')}; location={s.get('categories.location')}; " \
              f"allLocations={s.get('categories.allLocations')}"
        if s.get("country") == "US":
            return _label("supported", "country / categories.location", loc,
                          f"'Where you'll be': {where[:160]}" if where else "")
        if s.get("country"):
            return _label("contradicted", "country / categories.location", loc,
                          f"'Where you'll be': {where[:160]}" if where else "")
        return _label("insufficient", None, None, "No country or location given.")
    loc = s.get("location.name") or ""
    if not loc or loc.strip().upper() == "N/A":
        return _label("insufficient", "location.name", loc or None, "Location is missing or 'N/A'.")
    low = loc.lower()
    us = [p for p in US_PLACES if _word(p).search(low)]
    non_us = [p for p in NON_US_PLACES if _word(p).search(low)]
    if us and non_us:
        return _label("supported", "location.name", loc, "Mixed list; at least one US location.")
    if us:
        return _label("supported", "location.name", loc)
    if non_us:
        return _label("contradicted", "location.name", loc, "Only non-US locations listed.")
    return _label("insufficient", "location.name", loc, "Location not recognised as US or non-US.")


def _early_career(ev: dict) -> dict:
    title = ev["title"]
    senior = next((w for w in SENIOR_WORDS if _word(w).search(title)), None)
    if senior:
        return _label("contradicted", "title", title, f"Title states the level: '{senior}'.")
    early = next((w for w in EARLY_WORDS if _word(w).search(title)), None)
    if early:
        return _label("supported", "title", title, f"Title states the level: '{early}'.")
    return _label("insufficient", "title", title, "No level stated in the title.")


def _regular_role(board: str, ev: dict) -> dict:
    title = ev["title"]
    if _word("intern").search(title):
        return _label("contradicted", "title", title, "Title says this is an internship.")
    commitment = ev["structured"].get("categories.commitment")
    if board == "spotify" and commitment:
        if str(commitment).lower() == "permanent":
            return _label("supported", "categories.commitment", commitment)
        return _label("insufficient", "categories.commitment", commitment,
                      "Commitment is not 'Permanent'; check the posting.")
    return _label("insufficient", None, None,
                  "No employment-type field; a title without 'Intern' does not establish it.")


def _masters_ok(ev: dict) -> dict:
    title = ev["title"]
    if _word("phd").search(title):
        return _label("contradicted", "title", title, "Title says PhD.")
    if _word("master's").search(title) or _word("masters").search(title):
        return _label("supported", "title", title, "Title says Master's.")
    found = _first([r"(?:bachelor|master)['’]?s? degree", r"\bBS/MS\b", r"\bMS or PhD\b"],
                   ev["text_fields"])
    if found:
        name, quote, m = found
        if "phd" in m.group(0).lower() and "ms" not in m.group(0).lower():
            return _label("contradicted", name, quote)
        return _label("supported", name, quote,
                      "The degree asked for is at or below a master's. This covers degree "
                      "level only, not whether Priya's field of study is accepted.")
    return _label("insufficient", None, None, "No degree requirement stated.")


def _years(ev: dict) -> dict:
    found = _first([r"(\d+)\s*\+?\s*(?:\+\s*)?years"], ev["text_fields"])
    if not found:
        why = "No years of experience stated." if ev["text_fields"] else "Description not fetched."
        return _label("insufficient", None, None, why)
    name, quote, m = found
    n = int(m.group(1))
    if n >= 2:
        return _label("contradicted", name, quote, f"Asks for {n}+ years.")
    return _label("supported", name, quote, f"Asks for {n} year(s).")


def _python(ev: dict) -> dict:
    for name, text in ev["text_fields"].items():
        m = _word("python").search(text)
        if m:
            quote = _span(text, m.start(), m.end())
            window = text[max(0, m.start() - 40): m.end() + 40].lower()
            note = ""
            if re.search(r"\bor\b|or similar", window):
                note = ("Python is one accepted option among alternatives; this does not "
                        "establish that Python is required.")
            return _label("supported", name, quote, note)
    if re.search(r"no python|python (?:is )?not required", " ".join(ev["text_fields"].values()), re.I):
        return _label("contradicted", None, None)
    why = "Description present but Python is not named." if ev["text_fields"] \
        else "Description not fetched; the title and company say nothing about Python."
    return _label("insufficient", None, None, why)


def _sponsorship(ev: dict) -> dict:
    no = _first(SPONSOR_NO, ev["text_fields"])
    if no:
        return _label("contradicted", no[0], no[1])
    yes = _first(SPONSOR_YES, ev["text_fields"])
    if yes:
        return _label("supported", yes[0], yes[1])
    why = "Description present but says nothing about visas or sponsorship." if ev["text_fields"] \
        else "Description not fetched."
    return _label("insufficient", None, None, why)


def _clearance(ev: dict) -> dict:
    no = _first(CLEARANCE_NO, ev["text_fields"])
    if no:
        return _label("supported", no[0], no[1])
    yes = _first(CLEARANCE_YES, ev["text_fields"])
    if yes:
        return _label("contradicted", yes[0], yes[1])
    why = "Description present but says nothing about clearance." if ev["text_fields"] \
        else "Description not fetched."
    return _label("insufficient", None, None, why)


def label_claims(board: str, ev: dict) -> dict:
    return {
        "role_type": _role_type(ev),
        "us_location": _us_location(board, ev),
        "early_career_level": _early_career(ev),
        "regular_role": _regular_role(board, ev),
        "masters_ok": _masters_ok(ev),
        "years_within_reach": _years(ev),
        "asks_python": _python(ev),
        "offers_sponsorship": _sponsorship(ev),
        "no_clearance": _clearance(ev),
    }


# -------------------------------------------------------------- assembly

def build(results: dict, raw_by_board: dict[str, list[dict]]) -> dict:
    index = {b: {j.get("id"): j for j in jobs} for b, jobs in raw_by_board.items()}
    postings = []
    for board in BOARDS:
        for r in results.get(board, []):
            if not r.get("passed"):
                continue
            job = index[board][r["id"]]
            ev = _evidence(board, job)
            postings.append({
                "n": len(postings) + 1,
                "board": board,
                "id": r["id"],
                "company": ev["company"],
                "company_note": ev["company_note"],
                "title": ev["title"],
                "source_url": ev["url"],
                "filter_reason": r.get("reason"),
                "filter_matched_words": r.get("matched_words"),
                "evidence_available": {
                    "structured": ev["structured"],
                    "text_fields": {k: len(v) for k, v in ev["text_fields"].items() if v},
                },
                "missing_fields": ev["missing_fields"],
                "claims": label_claims(board, ev),
            })
    return {
        "status": "AI-prepared evidence packet, pending human review. Not verified judgments.",
        "candidate": CANDIDATE,
        "claims": dict(CLAIMS),
        "postings": postings,
    }


def _cell(text) -> str:
    return " ".join(str(text if text is not None else "").split()).replace("|", "\\|")


def render_md(packet: dict) -> str:
    claim_text = packet["claims"]
    rows = packet["postings"]
    counts = {c: {"supported": 0, "contradicted": 0, "insufficient": 0} for c in claim_text}
    for p in rows:
        for c, lab in p["claims"].items():
            counts[c][lab["proposed"]] += 1

    out = [
        "# Shortlist evidence packet (AI-prepared, pending review)",
        "",
        "**Status:** Claude prepared these proposed labels with simple text rules for "
        "Sreevarshan to review. They are not independently verified judgments. Fill in "
        "\"My label\" to accept or correct each one.",
        "",
        f"**Candidate:** {packet['candidate']}",
        "",
        "**Labels (FILTER.md section 5):** *supported*: the posting's own text says it (quoted). "
        "*contradicted*: the posting's own text says the opposite (quoted). *insufficient*: "
        "the field is missing or silent. Nothing is inferred from the company name, the board, "
        "or what a title usually implies.",
        "",
        f"**Postings:** {len(rows)} (all postings that passed the filter). Databricks and Stripe "
        "are Greenhouse postings with no saved description; Spotify (Lever) has full text.",
        "",
        "## Label counts by claim",
        "",
        "| Claim | Supported | Contradicted | Insufficient |",
        "|---|---|---|---|",
    ]
    for c, text in claim_text.items():
        k = counts[c]
        out.append(f"| {_cell(text)} | {k['supported']} | {k['contradicted']} | {k['insufficient']} |")
    out += ["", "## Postings", ""]
    for p in rows:
        out += [
            f"### {p['n']}. {_cell(p['title'])}",
            "",
            f"- **Board / ID:** {p['board']} / `{p['id']}`",
            f"- **Company:** {p['company']}" + (f" ({p['company_note']})" if p["company_note"] else ""),
            f"- **Source URL:** {p['source_url']}",
            f"- **Filter reason:** {p['filter_reason']} "
            f"(role: {', '.join(p['filter_matched_words']['role']) or '-'}; "
            f"topic: {', '.join(p['filter_matched_words']['topic']) or '-'})",
            "- **Evidence available:** "
            + "; ".join(f"{k} = {_cell(v)}" for k, v in p["evidence_available"]["structured"].items())
            + (("; text fields: " + ", ".join(p["evidence_available"]["text_fields"]))
               if p["evidence_available"]["text_fields"] else ""),
            f"- **Missing:** {'; '.join(p['missing_fields']) or 'none'}",
            "",
            "| Claim | Proposed | Evidence | Note | My label |",
            "|---|---|---|---|---|",
        ]
        for c, lab in p["claims"].items():
            evidence = f"{lab['field']}: \"{lab['quote']}\"" if lab["quote"] else "-"
            out.append(
                f"| {_cell(claim_text[c])} | {lab['proposed']} | {_cell(evidence)} | "
                f"{_cell(lab['note'])} | |"
            )
        out.append("")
    return "\n".join(out)


def load_raw() -> dict[str, list[dict]]:
    raw = {}
    for board, path in SOURCES.items():
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        raw[board] = data.get("jobs", []) if isinstance(data, dict) else data
    return raw


def main(results_path: Path = RESULTS, json_out: Path = PACKET_JSON, md_out: Path = PACKET_MD) -> dict:
    with Path(results_path).open("r", encoding="utf-8") as f:
        results = json.load(f)
    packet = build(results, load_raw())
    write_outputs({
        Path(json_out): json.dumps(packet, indent=2, ensure_ascii=False) + "\n",
        Path(md_out): render_md(packet),
    })
    print(f"postings: {len(packet['postings'])}")
    print(f"wrote {json_out}")
    print(f"wrote {md_out}")
    return packet


if __name__ == "__main__":
    try:
        main()
    except OverwriteRefused as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
