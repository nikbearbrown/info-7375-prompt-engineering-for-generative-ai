"""CONSTRUCTED postings and a CONSTRUCTED corpus folder for JS3 tests.

Nothing here came from a real board. The temporary corpus folder mimics the
project layout (CORPUS.sha256, config/boards.json, out/raw/) so js3.corpus,
js3.run_filter and js3.sample can be exercised without the frozen files.
"""

import hashlib
import html
import json
from pathlib import Path

from js3 import filter as js3_filter

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "filter-v1.0.json"
CONFIG = js3_filter.load_config(CONFIG_PATH)

RAW_NAME = "20990101T000000Z_constructed_a1.json"


def post(title, body, pid="c1", board="constructed"):
    """A CONSTRUCTED posting already in js3.corpus shape."""
    return {"board": board, "id": pid, "title": title, "location": "Nowhere",
            "url": f"https://example.invalid/{pid}", "body_text": body}


def constructed_jobs(count=120):
    """CONSTRUCTED Greenhouse-style jobs with known filter outcomes.

    i % 4 == 0: ML Engineer + 2 topic words   -> score 5, kept
    i % 4 == 1: Software Engineer + 1 word    -> score 1, rejected
    i % 4 == 2: Data Engineer, no topic word  -> score 3, rejected (close)
    i % 4 == 3: Account Executive + 1 word    -> score 1, rejected
    Bodies avoid filter vocabulary such as the decision names.
    """
    kinds = [
        ("ML Engineer", "<p>You will use <b>PyTorch</b> and Spark.</p>"),
        ("Software Engineer", "<p>Our stack uses Spark.</p>"),
        ("Data Engineer", "<p>Build pipelines for the finance team.</p>"),
        ("Account Executive", "<p>Sell our LLM products.</p>"),
    ]
    jobs = []
    for i in range(count):
        title, body = kinds[i % 4]
        jobs.append({
            "id": 100000 + i,
            "title": f"{title} {i}",
            "location": {"name": "Nowhere"},
            "content": html.escape(body),
            "absolute_url": f"https://example.invalid/{100000 + i}",
        })
    return jobs


def make_corpus(folder, jobs=None, corrupt=False, missing=False):
    """Write a CONSTRUCTED corpus into `folder`; return the folder."""
    folder = Path(folder)
    (folder / "out" / "raw").mkdir(parents=True)
    (folder / "config").mkdir()
    (folder / "config" / "boards.json").write_text(json.dumps({"boards": [
        {"name": "constructed", "ats": "greenhouse",
         "url": "https://example.invalid/constructed"},
        {"name": "constructed-404", "ats": "greenhouse",
         "url": "https://example.invalid/404"},
    ]}), "utf-8")
    raw = json.dumps({"jobs": constructed_jobs() if jobs is None else jobs,
                      "meta": {}}).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    if corrupt:
        digest = "0" * 64
    if not missing:
        (folder / "out" / "raw" / RAW_NAME).write_bytes(raw)
    (folder / "CORPUS.sha256").write_text(
        f"{digest}  out/raw/{RAW_NAME}\n", "utf-8")
    return folder
