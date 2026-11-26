# The request given to Claude Code for the reviewed change

Sent on 2026-11-09 to a fresh Claude Code subagent session (no shared conversation), working in
an isolated git worktree of this repository at commit `affcbdd`. Verbatim:

---

You are working in a Python 3.12 repository (a discovery-only job-search agent; tools: uv,
pytest, ruff, mypy --strict). Read `GATE.md` §2, §5 and amendment A2 in §10, then
`src/job_search_agent/watch.py` and `tests/watch/test_floor.py`.

Make exactly one change: implement GATE.md amendment A2. A planned board may carry
`min_postings`. When a board's response parses but lists fewer postings than its floor, the
board is a failed board: its per-board run is `INVALID_RESPONSE` with the code `below_floor`,
its state is not written, its saved raw response is kept, and the loop cannot end `FINISHED`.
An empty board stays `EMPTY_RESPONSE`. A board without `min_postings` has no floor.

The failing tests in `tests/watch/test_floor.py` were written before this patch. Make them pass
without editing them. Also add `min_postings` to the boards in `config/watch.toml` and
`config/watch-wrong-board.toml` with the values listed in A2 (none for `ashby/linearapp`).

Constraints:
- Stay in scope: only what A2 needs. Do not refactor unrelated code, do not change what
  `jsa run` (the JS1 single-board command) does, and do not edit, skip or weaken any test.
- The loop report must show `below_floor` as the failed board's note.
- Run `uv run ruff format src tests`, `uv run ruff check src tests`, `uv run mypy src` and
  `uv run pytest -q`; all must pass.
- Do not commit. Do not run `jsa watch run` or anything else that uses the network. Do not
  touch `data/`, `GATE.md` or `docs/`.

When you finish, report: each file you changed and why, and every command you ran with its
result.

---

**Note on delivery.** A locally installed Claude Code plugin hook (`context-mode`) appended its
own block of tool-usage instructions to this prompt before it reached the subagent. That block
is about which tools to use for reading files; it does not change the request above. The first
launch attempt was held by auto mode for that reason and was re-sent unchanged.
