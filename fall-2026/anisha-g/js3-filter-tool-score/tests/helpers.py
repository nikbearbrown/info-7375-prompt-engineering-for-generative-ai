"""Shared helpers. JS3_FILTER swaps the filter module, so the same tests run against the wrong versions (FILTER.md section 4)."""
import importlib, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def filt():
    return importlib.import_module(os.environ.get("JS3_FILTER", "js3.filter"))

def cfg():
    return filt().load_filter(ROOT / "filters" / "filter_v1.0.json")

def P(title="Data Analyst", text="", location="Boston, MA", id="t:1"):
    return {"id": id, "title": title, "text": text, "location": location, "url": "https://example.test/" + id}
