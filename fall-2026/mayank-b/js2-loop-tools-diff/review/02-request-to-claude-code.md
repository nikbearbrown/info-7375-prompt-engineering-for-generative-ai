# The change requested from Claude Code (2026-11-10)

**Who asked:** Mayank Bhadrasen, through the gate (GATE.md §8, his answer 9: "JS1's safeWrite follows symlinks out of its folder"), in the Claude Code session that built JS2.
**Who made it:** Claude Code (Claude Opus 5.5), the same session.

**The request, as given:**
> Fix the symlink escape in `src/jsa/policy.py`. `authorize()` must judge a path by where it resolves on disk (following symlinks), so `runs/<id>/link/x.json` with `link` → a folder outside the project is refused with `outside-write-root`, and the path returned is the resolved one. Tests B8 and B8b (tests/test_policy.py, committed in JS2-CP5 before this change) define done. **Scope:** change only how `policy.py` resolves paths. Do not change the tests, the allow-list, the approval rule, the loop, the checker, or any other file.

Note on independence: the same session wrote the code, the tests and the patch. The patch can't count as a second opinion ("the first opinion run twice"). What makes it checkable is that the tests came first (CP5) and that Mayank reruns the commands himself (03-review.md).
