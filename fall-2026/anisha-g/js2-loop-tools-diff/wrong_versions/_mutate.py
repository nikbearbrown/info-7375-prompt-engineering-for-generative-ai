"""Build a deliberately wrong copy of watcher/loop.py by replacing ONE piece of source. The real file is never changed."""
import types
from pathlib import Path
def mutant(name, old, new):
    src = (Path(__file__).resolve().parent.parent / "watcher" / "loop.py").read_text()
    assert src.count(old) == 1, f"mutation target not found exactly once: {old!r}"
    m = types.ModuleType(name); exec(compile(src.replace(old, new), f"<{name}>", "exec"), m.__dict__); return m
