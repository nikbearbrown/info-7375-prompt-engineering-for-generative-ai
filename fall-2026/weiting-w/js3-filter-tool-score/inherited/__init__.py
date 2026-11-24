"""The parts of JS2 that JS3 inherits, copied with one mechanical change.

Nothing in this package was written for JS3. These are the provider adapters,
the rule R-v3, the field helper, the error classes and the persona loader from
`fall-2026/weiting-w/js2-loop-tools-diff` (commit 1fb701b3), copied rather than
imported so this folder runs from a fresh clone on its own.

**They are not byte-identical, and the difference is worth stating exactly.**
JS2's modules import each other with package-relative imports (`from .fieldpath
import whole_word`). Those do not resolve from this package, so every such line
was rewritten to an absolute `inherited.` import. That is the *only* change:
no logic, no constant, no word list, no weight, no docstring.

`tests/test_inherited_is_unchanged.py` holds that claim rather than asserting
it in prose. When the JS2 folder is present as a sibling it compares every file
here against its JS2 original line by line and requires that every differing
line is an import statement and nothing else. It skips when the sibling is
absent, which is the only situation in which a copy could quietly drift.

FILTER.md section 5 lists these as `inherited`: the gates and the persona are
not re-litigated in this layer.
"""
