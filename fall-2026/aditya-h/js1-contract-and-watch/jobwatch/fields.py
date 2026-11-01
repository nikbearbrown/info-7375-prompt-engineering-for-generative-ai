"""Resolve dotted field paths such as ``experience[0].title`` against JSON data."""
import re

_TOKEN = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def resolve(obj, path):
    """Return the value at ``path`` or raise KeyError if any step is missing."""
    if not path or not isinstance(path, str):
        raise KeyError(path)
    cur = obj
    pos = 0
    for m in _TOKEN.finditer(path):
        if m.start() != pos and path[pos:m.start()] != ".":
            raise KeyError(path)
        pos = m.end()
        key, idx = m.group(1), m.group(2)
        if key is not None:
            if not isinstance(cur, dict) or key not in cur:
                raise KeyError(path)
            cur = cur[key]
        else:
            i = int(idx)
            if not isinstance(cur, list) or i >= len(cur):
                raise KeyError(path)
            cur = cur[i]
    if pos != len(path):
        raise KeyError(path)
    return cur
