"""Load the saved JS2 postings (read-only) and turn their HTML into sentences.

FILTER.md section 2: postings are identified by board and posting ID, and a
posting that appears in several runs is counted once, using the latest saved
version. The JS2 files are only read, never written.
"""
import hashlib
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_JS2 = HERE.parent / "js2-loop-tools-diff"
PERSONA_NAME = "priya-nair.resume.example.json"

# (board, applicant-tracking system, raw file name inside each JS2 run folder)
BOARDS = (
    ("Databricks", "greenhouse", "raw-greenhouse-databricks-attempt1-http200.json"),
    ("Anthropic", "greenhouse", "raw-greenhouse-anthropic-attempt1-http200.json"),
    ("OpenAI", "ashby", "raw-ashby-openai-attempt1-http200.json"),
)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def to_posting(board, ats, job, run_name, file_name):
    """One raw job dict -> the fields the filter uses, keeping the original markup."""
    if ats == "greenhouse":
        location = (job.get("location") or {}).get("name") or ""
        # Greenhouse sends the description HTML-escaped; unescaping once gives the HTML.
        markup = html.unescape(job.get("content") or "")
        url = job.get("absolute_url") or ""
    else:
        parts = [job.get("location") or ""]
        parts += [(x or {}).get("location") or "" for x in (job.get("secondaryLocations") or [])]
        location = " · ".join(p for p in parts if p)
        markup = job.get("descriptionHtml") or ""
        if not markup and job.get("descriptionPlain"):
            markup = html.escape(job["descriptionPlain"]).replace("\n", "<br>")
        url = job.get("jobUrl") or ""
    return {
        "board": board,
        "id": str(job["id"]),
        "title": (job.get("title") or "").strip(),
        "location": location.strip(),
        "url": url,
        "markup": markup,
        "source_run": run_name,
        "source_file": file_name,
    }


def load_saved_postings(js2_dir=DEFAULT_JS2):
    """Return (postings sorted by board and ID, list of source files with fingerprints).

    Runs are read in name order (their names are UTC timestamps), so a later run
    replaces an earlier copy of the same (board, ID).
    """
    js2_dir = Path(js2_dir)
    runs = sorted(p for p in (js2_dir / "runs").glob("run-*") if p.is_dir())
    if not runs:
        raise FileNotFoundError(f"no JS2 run folders under {js2_dir / 'runs'}")
    by_key, sources = {}, []
    for run in runs:
        for board, ats, name in BOARDS:
            path = run / name
            if not path.is_file():
                raise FileNotFoundError(f"missing saved response: {path}")
            jobs = json.loads(path.read_bytes())["jobs"]
            sources.append({"run": run.name, "board": board, "file": f"runs/{run.name}/{name}",
                            "sha256": sha256(path), "postings_in_file": len(jobs)})
            for job in jobs:
                p = to_posting(board, ats, job, run.name, name)
                by_key[(board, p["id"])] = p
    postings = [by_key[k] for k in sorted(by_key)]
    return postings, sources


def load_persona(js2_dir=DEFAULT_JS2):
    path = Path(js2_dir) / "persona" / PERSONA_NAME
    return json.loads(path.read_text(encoding="utf-8")), {"file": f"persona/{PERSONA_NAME}", "sha256": sha256(path)}


# ---------------------------------------------------------------- text cleaning

_HEADING_MARK = "\x01"
_BLOCK = re.compile(r"(?is)<\s*/?\s*(p|div|li|ul|ol|br|h[1-6]|tr|table|section|blockquote)\b[^>]*>")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?;])\s+(?=[A-Z\[(\"'])")


def blocks(markup):
    """HTML -> list of (line, is_heading). Headings are <h1>-<h6>, a paragraph that is
    only bold text, or a short line ending in ':'."""
    t = re.sub(r"(?is)<(script|style)\b.*?</\1\s*>", " ", markup or "")
    t = re.sub(r"(?is)<\s*p\b[^>]*>\s*<\s*(strong|b)\b[^>]*>(.*?)<\s*/\s*\1\s*>\s*<\s*/\s*p\s*>",
               lambda m: "\n" + _HEADING_MARK + m.group(2) + "\n", t)
    t = re.sub(r"(?is)<\s*h[1-6]\b[^>]*>", "\n" + _HEADING_MARK, t)
    t = _BLOCK.sub("\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    out = []
    for raw in t.split("\n"):
        marked = raw.lstrip().startswith(_HEADING_MARK)
        line = re.sub(r"\s+", " ", raw.replace(_HEADING_MARK, " ")).strip()
        if not line:
            continue
        short = len(line.split()) <= 10
        out.append((line, short and (marked or line.endswith(":"))))
    return out


def sentences(markup):
    """HTML -> list of {"text", "heading"}: every sentence with the heading it sits under."""
    out, heading = [], ""
    for line, is_heading in blocks(markup):
        if is_heading:
            heading = line
        for s in _SENTENCE_SPLIT.split(line):
            s = s.strip()
            if s:
                out.append({"text": s, "heading": heading})
    return out


def plain_text(markup):
    """The cleaned description as readable text (one line per block), for hand review."""
    return "\n".join(line for line, _ in blocks(markup))
