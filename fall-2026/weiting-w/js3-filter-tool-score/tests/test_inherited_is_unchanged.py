"""The `inherited/` package must differ from JS2 only in its import lines.

`inherited/__init__.py` claims that the copies carried over from JS2 are
unchanged apart from package-relative imports being rewritten. That is a claim
about bytes, so it is checked against the bytes rather than trusted.

The test skips when the JS2 folder is not a sibling — a fresh clone of just
this folder has nothing to compare against. That skip is the one case where a
copy could drift unnoticed, and it is named in README.md's sign-off rather than
hidden here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
JS2 = HERE.parent / "js2-loop-tools-diff" / "agent"

PAIRS = [
    ("inherited/rule.py", "rule.py"),
    ("inherited/fieldpath.py", "fieldpath.py"),
    ("inherited/resume.py", "resume.py"),
    ("inherited/errors.py", "errors.py"),
    ("inherited/providers/__init__.py", "providers/__init__.py"),
    ("inherited/providers/base.py", "providers/base.py"),
    ("inherited/providers/greenhouse.py", "providers/greenhouse.py"),
    ("inherited/providers/lever.py", "providers/lever.py"),
    ("inherited/providers/ashby.py", "providers/ashby.py"),
]

needs_js2 = pytest.mark.skipif(
    not JS2.is_dir(), reason="JS2 folder is not a sibling; nothing to compare against"
)


@needs_js2
@pytest.mark.parametrize("mine,theirs", PAIRS, ids=[p[0] for p in PAIRS])
def test_every_differing_line_is_an_import(mine, theirs):
    a = (HERE / mine).read_text(encoding="utf-8").splitlines()
    b = (JS2 / theirs).read_text(encoding="utf-8").splitlines()
    assert len(a) == len(b), f"{mine}: line count changed ({len(b)} -> {len(a)})"
    for i, (mine_line, their_line) in enumerate(zip(a, b), 1):
        if mine_line == their_line:
            continue
        stripped = mine_line.strip()
        assert stripped.startswith("from inherited."), (
            f"{mine}:{i} differs from JS2 and is not an import rewrite:\n"
            f"  JS2: {their_line!r}\n  JS3: {mine_line!r}"
        )
        assert their_line.strip().startswith("from ."), (
            f"{mine}:{i} rewrote a line that was not a relative import"
        )


@needs_js2
def test_the_persona_is_byte_identical():
    """The persona really is unchanged, so this one is a hash check."""
    import hashlib

    mine = (HERE / "data" / "resume.persona.json").read_bytes()
    theirs = (JS2.parent / "data" / "resume.persona.json").read_bytes()
    assert hashlib.sha256(mine).hexdigest() == hashlib.sha256(theirs).hexdigest()


@needs_js2
def test_the_rule_version_is_the_one_js2_submitted():
    import sys

    sys.path.insert(0, str(HERE))
    from inherited import rule

    assert rule.RULE_VERSION == "R-v3"
