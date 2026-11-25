"""Load a private copy of js3/filter.py and replace one function, so each wrong version differs from the real filter
in exactly one place (same pattern as my JS2 wrong_versions)."""
import importlib.util
from pathlib import Path
def clone(name, **overrides):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parent.parent / "js3" / "filter.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    for k, v in overrides.items(): setattr(m, k, v)
    return m
