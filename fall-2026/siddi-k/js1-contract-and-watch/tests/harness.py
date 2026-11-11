"""Shared fixtures for tests/test_wrong_versions.py: throwaway roots, fixture boards, and the stub `claude` on PATH.
Tests never call the real `claude` and never touch the network."""
from __future__ import annotations

import contextlib
import html
import json
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUBS = ROOT / "tests" / "stubs"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import config, rule, textprep  # noqa: E402

PERSONA = json.loads((ROOT / "data" / "persona_resume.json").read_text(encoding="utf-8"))
CFG = config.load(ROOT)
# v1 (Databricks) boilerplate, used where a wrong version is about a heading or blurb phrase that v1 named.
CUT_V1 = ("benefits", "pay range transparency", "our commitment to diversity and inclusion", "compliance")
DROP_V1 = ("original creators of", "founded by the original", "databricks is the data and ai company")
GOOD_REQ = ("<h2>Minimum requirements</h2><ul><li>2+ years of experience building data pipelines</li>"
            "<li>Python, SQL, Spark and Kafka</li><li>Airflow or dbt</li></ul>")


def ok_stdout(verdict="relevant", **over) -> str:
    answer = {"verdict": verdict, "justification": "Requirements name Python and SQL, both in skills.",
              "cited_resume_fields": ["skills"], "cited_posting_fields": ["content"], **over}
    return json.dumps({"type": "result", "is_error": False, "result": json.dumps(answer)})


def job(i: int, title: str, location: str, content_html: str) -> dict:
    """A posting shaped like Greenhouse's: content is escaped HTML."""
    return {"id": i, "title": title, "location": {"name": location}, "content": html.escape(content_html),
            "absolute_url": f"https://stripe.com/jobs/listing/{i}"}


def sentences(content_html: str, cut=CUT_V1, drop=DROP_V1) -> list[str]:
    return textprep.requirements_sentences(html.escape(content_html), cut, drop)


def verdict(title: str, location: str, content_html: str, cut=CUT_V1, drop=DROP_V1) -> dict:
    return rule.judge({"id": 1, "title": title, "location": location}, sentences(content_html, cut, drop),
                      PERSONA, CFG.vocab)


@contextlib.contextmanager
def temp_root():
    """A copy of the agent and its frozen config in a fresh temp dir (no raw/, state/ or output/ yet)."""
    tmp = Path(tempfile.mkdtemp(prefix="js1t"))
    try:
        for d in ("agent", "config", "data", "prompts", "experiments"):
            if (ROOT / d).exists():
                shutil.copytree(ROOT / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__", "output"))
        (tmp / "boards").mkdir()
        yield tmp
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def write_board(root: Path, name: str, jobs: list[dict]) -> str:
    rel = f"boards/{name}.json"
    (root / rel).write_text(json.dumps({"jobs": jobs, "meta": {"total": len(jobs)}}), encoding="utf-8")
    return rel


@contextlib.contextmanager
def stub_claude(responses: list[str]):
    """Put tests/stubs first on PATH; yields a function returning the stub's logged calls."""
    stub_dir = Path(tempfile.mkdtemp(prefix="js1stub"))
    (stub_dir / "responses.json").write_text(json.dumps(responses), encoding="utf-8")
    posix_stub = STUBS / "claude"
    posix_stub.chmod(posix_stub.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    saved = {k: os.environ.get(k) for k in ("PATH", "JS1_STUB_DIR", "JS1_STUB_PYTHON")}
    os.environ.update({"PATH": str(STUBS) + os.pathsep + os.environ.get("PATH", ""),
                       "JS1_STUB_DIR": str(stub_dir), "JS1_STUB_PYTHON": sys.executable})

    def calls():
        log = stub_dir / "calls.jsonl"
        return [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []

    try:
        yield calls
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(stub_dir, ignore_errors=True)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def quiet(*_a, **_k):
    pass
