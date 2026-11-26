"""Synthetic postings for the tests. Nothing here is collected data or Claude output."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def cfg(version: str = "v1") -> dict:
    return json.loads((ROOT / "config" / f"filter.{version}.json").read_text(encoding="utf-8"))


def posting(title="Data Engineer", text="<p>We use python, sql, spark and airflow.</p>", board="stripe",
            location="San Francisco, CA", country=None, other=None, text_format="html", pid="1"):
    return {"board": board, "system": "greenhouse", "id": pid, "title": title,
            "location": {"name": location, "country": country, "remote": None, "other": other or []},
            "text_format": text_format, "text": text, "text_missing": None if text else "empty",
            "url": None, "updated_at": None}
