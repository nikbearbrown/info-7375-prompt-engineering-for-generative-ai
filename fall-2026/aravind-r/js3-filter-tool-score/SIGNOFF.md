# Sign-off — Job-Search Agent 3

**Template drafted by Claude Code (2026-11-25); "How", "Not checked", "Not claiming" and the
signature written by Aravind (with drafting help from chat-Claude, claude.ai Claude Opus 5.5).**

## Checked: which properties, by which of my own tests

| Property | Test / evidence | How |
|---|---|---|
| The filter is the document: weights, terms, threshold come from FILTER.md §6 | `test/spec.test.mjs` (W11; no §6 literal in `src/filter.mjs`) | With Claude's help: Claude Code wrote the test before the filter code (`bb88c420`); I accepted it from the summary |
| No non-PM title can pass; failing location or experience can't be bought back | `test/spec.test.mjs` W4; `test/filter.test.mjs` W13 | With Claude's help: I specified W13's four exact cases (the hole was found by chat-Claude); Claude Code coded them |
| A veto is a veto, with a verbatim quote | `test/filter.test.mjs` W2, v1.1.0-c (including false-friend negatives) | With Claude's help: I chose bounded phrases over a broad regex; Claude Code wrote the tests |
| An unknown is not a match; abstain only when an unknown could flip the decision | `test/filter.test.mjs` W5, §2.3 | With Claude's help: Claude Code wrote it before the filter code |
| Unavailable boards are null, not 0; null ids skipped; no `applyUrl` | `test/normalize.test.mjs` W6, W9; SNAPSHOT counts | With Claude's help |
| The snapshot is the one in MANIFEST | `test/normalize.test.mjs` (SHA-256 per file) | Recomputation by test |
| Non-verbatim quotes can't support or contradict | `test/evidence.test.mjs` W10; `test/justify.test.mjs` | With Claude's help |
| A misfiled manual reply can't be imported | `test/import-manual.test.mjs` | With Claude's help: added after my own misfiling (see FRICTIONAL) |
| Audit error figures are exact intervals | `test/tools.test.mjs` (Clopper–Pearson against published values) | Recomputation by test; I did not recompute the intervals by hand |
| The judge is unreachable from the filter and the MCP server; no process or network | `test/isolation.test.mjs`; the import-graph test in `test/mcp-server.test.mjs` | With Claude's help |
| The MCP server behaves as declared and refuses bad input | `test/mcp-server.test.mjs`; the real transcript `transcripts/2026-11-26T004241768Z-70635.jsonl` (call 3 refused) | By hand: I ran the 3 Claude Desktop calls myself; tests by Claude Code |
| The reject audit and the recheck | my 45 verdicts and 14 rechecks; `audit/RESULTS.md` recomputed by `tools/audit-results.mjs` | By hand |
| Claim labels | my confirmed labels, re-checked by `tools/confirm-claims.mjs` | By hand |

## Not checked (at least three real items)

- **Held-out recall.** All 20 held-out labels are not relevant, so the final filter's ability to
  find relevant postings it wasn't tuned on was never tested. Held-out only bounds false keeps.
- **The PM-titled rejects.** 15 of 133 were drawn and never judged, so there is no error estimate
  for the population where false rejects are most likely.
- **The extraction limits in FILTER.md §5.4.** Years under "Preferred" read as required, spelled-out
  numbers, multiple years lines, and 34 duplicate groups were counted, not fixed. Each count comes
  from a heuristic written while looking at the case that prompted it.
- **Most generated code, line by line.** I reviewed summaries and relied on a second Claude's
  review. I verified behavior through tests, transcripts and my own judgments, not by reading
  every source file.

## Not claiming

- That the filter works for a different persona, on other boards, or on postings after 2026-11-10.
- That 0/30 false rejects is a rate. It's a bound (up to 11.6%) for this snapshot under v1.0.0.
- That v1.1.0-e is validated. Its rules were changed using audit rows (dev use), and the held-out
  set had no positives to test it on.
- That the Claude justifications are reproducible. They came from claude.ai (its own system prompt,
  self-reported model), not tool-less `claude -p`.
- That the filesystem server is safe in general. My trust decision covers only `--read-only` with
  `--confine-roots`, from source reading, never run.

**Signed or withheld:** Signed, Aravind Ravi, 2026-11-25

---

## Driver's seat

| Task | Claude should do | I should do | Why |
|---|---|---|---|
| Write and run the filter, tests, sampling, intervals | draft the code, run it, report counts with exact intervals | decide the rules and the thresholds; check the tests catch the wrong versions | a rule encodes my priorities; Claude can implement them, not choose them |
| Judge postings (audit, labels) | build blind sheets and tools; never fill a verdict | judge every row myself, against the written definition | the ground truth is my judgment; a model's judgment would make the audit circular |
| Justify a shortlisted posting | split it into claims with exact quotes; propose labels; abstain when the text is silent | confirm each label; catch claims that are entailed but not relevant | entailment can be checked mechanically, relevance can't |
| Decide whether a posting is worth my time | surface it with its evidence and its known limits | **decide, and decide whether to apply** | it depends on things no posting states: my goals, work-authorization constraints, my tolerance for a stretch role, timing. It's my career and my risk. |
| Trust a tool server | read the source, test declared vs actual, mark verified vs inferred | make the trust decision and choose the configuration (`--read-only`, `--confine-roots`) | the risk falls on my machine and my files |
| Change a rule after seeing results | measure before and after; label it as dev use; refuse to change it just to grow the list | approve every change and own the post-hoc ones | changes made after seeing results are where self-deception gets in; the honesty record is mine |