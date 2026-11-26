"""The one place JS3 writes generated files (reports, records). Same idea as JS2 store.py.

A write is allowed only if the real path is inside this assignment folder and not inside a
protected folder: config/ (budgets, sources), filter/ (the filter is changed by hand, with a
FILTER.md change-log row), labels/ (Omkar's labels), evidence/ (frozen copies), persona/.
Generated reports may be overwritten; data/ (raw responses) is written only by js3.collect.
"""
import os

from .js2.policy import _inside

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTECTED = ("config", "filter", "labels", "evidence", "persona", "data")


class WriteRefused(Exception):
    pass


def check(path):
    p = path if os.path.isabs(path) else os.path.join(BASE, path)
    if not _inside(p, BASE):
        raise WriteRefused(f"{path}: outside the assignment folder")
    for d in PROTECTED:
        if _inside(p, os.path.join(BASE, d)):
            raise WriteRefused(f"{path}: {d}/ is protected (written by hand or by js3.collect only)")
    return p


def write_text(path, text):
    p = check(path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def write_bytes(path, data):
    p = check(path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)
    return p
