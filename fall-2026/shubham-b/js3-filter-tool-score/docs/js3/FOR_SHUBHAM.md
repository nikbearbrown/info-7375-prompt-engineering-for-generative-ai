# JS3: what is left for Shubham, in order

Claude built and ran everything that is not your judgment (2026-11-25, overnight, at your
request). These steps are yours. `scripts/package_js3.sh` refuses to build the zip while any
`[Shubham` placeholder, the unsigned sign-off, an unadopted FILTER.md or missing audit verdicts
remain.

**Do step 1 first, before reading anything else in `docs/js3/`, FILTER.md §8 or the README "What
ran" table.** Those files name the postings the filter kept and the ones its changes flipped, so
reading them first would make your audit verdicts less blind.

1. **The reject audit (12 points; must be your own judgment).** Copy
   `experiments/js3/audit/hand_verdicts.template.json` to `hand_verdicts.json`. Open
   `docs/js3/audit/WORKSHEET.md` (78 postings, full saved text, no scores, shuffled) and, for each,
   write `RELEVANT`, `NOT_RELEVANT` or `CANNOT_TELL` and a short reason. Fill `judged_by` and
   `judged_on`. The worksheet header lists every file to avoid until you finish. Commit the verdicts,
   then run `uv run python -m job_search_agent.js3 audit-report` and commit
   `docs/js3/audit/AUDIT_REPORT.md`. Then add two or three sentences to `docs/js3/AUDIT.md` §3 in
   your words: what you had read before judging, how many the filter got wrong, and what you can
   honestly say from 40.
2. **Read and adopt `FILTER.md`.** It is Claude's draft (v0.1 → v0.3). To adopt it unchanged,
   change **only the Status line** (e.g. "Adopted by Shubham Bagwe on <date>") and commit; leave the
   `version = "0.3"` in the filter block alone, because tests, frozen copies and the numbers in the
   docs are pinned to it. If you change a rule or number instead: add a §8 row, bump the block's
   version, copy the file to `experiments/js3/filters/FILTER.v<new>.md`, re-run `filter` and
   `shortlist`, update `tests/js3/test_filter.py::test_filter_md_is_the_frozen_v03` and the
   `filter_version` assertion in `tests/js3/test_mcp_server.py`, and fix the counts (53 kept, 384
   claims, 21 contradicted) in README, `docs/js3/SHORTLIST_NOTES.md`, `SCORE.md` and `AUDIT.md`.
3. **Trust decisions.** In `docs/js3/TOOL_SERVER.md` §3 and §4, replace the two
   `[Shubham: confirm or change…]` lines with your decision and reason.
4. **Check two or three things yourself** and note what you ran: e.g. recompute one shortlisted
   posting's score by hand from FILTER.md §1; open the New Grad posting (8128744) and confirm the
   18-month sentence; read the Claude transcript `data/js3/mcp/mcp-wire-claude-code-client-2026-11-25.jsonl`.
5. **README:** the sign-off (Checked / How / Not checked / Not claiming / Signed) and the driver's
   seat "why the judgment stays mine" column, in your words. The "What I should do" column is
   Claude's draft; edit it. Facts: `docs/js3/FACTS_FOR_SIGNOFF.md`.
6. **FRICTIONAL.md:** a JS3 section in your own voice, dated, with what you checked, accepted,
   changed or rejected from Claude, and commit links (the JS1 TA took points off for a log that
   read as compiled from the build log).
7. **SOURCES.md:** fill "What I wrote (JS3)".
8. Run `uv run pytest -q`, then `scripts/package_js3.sh`, then commit and push the course folder
   it prints, and submit the zip and the commit hash on Canvas. The due date was 2026-11-23.
