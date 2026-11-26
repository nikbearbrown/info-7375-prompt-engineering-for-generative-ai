# Sign-off — Job-Search Agent 3

**Template drafted by Claude Code (2026-11-25) for Aravind to edit and sign.**
- Claude Code pre-filled only "Checked", and every line there names a test or artifact that exists.
- "Not checked" and "Not claiming" are Aravind's to write.
- The "How" column is Aravind's to fill: delete what doesn't apply.
- **The Signed line stays blank until Aravind signs.**

## Checked: which properties, by which of my own tests

| Property | Test / evidence | How (by hand / test written before reading Claude's code / recomputation / with Claude's help: say which) |
|---|---|---|
| The filter is the document: weights, terms, threshold come from FILTER.md §6 | `test/spec.test.mjs` (W11; no §6 literal in `src/filter.mjs`) | |
| No non-PM title can pass; failing location or experience can't be bought back | `test/spec.test.mjs` W4; `test/filter.test.mjs` W13 (Aravind's exact cases) | |
| A veto is a veto, with a verbatim quote | `test/filter.test.mjs` W2, v1.1.0-c (including false-friend negatives) | |
| An unknown is not a match; abstain only when an unknown could flip the decision | `test/filter.test.mjs` W5, §2.3 | |
| Unavailable boards are null, not 0; null ids skipped; no `applyUrl` | `test/normalize.test.mjs` W6, W9; SNAPSHOT counts | |
| The snapshot is the one in MANIFEST | `test/normalize.test.mjs` (SHA-256 per file) | |
| Non-verbatim quotes can't support or contradict | `test/evidence.test.mjs` W10; `test/justify.test.mjs` | |
| A misfiled manual reply can't be imported | `test/import-manual.test.mjs` | |
| Audit error figures are exact intervals | `test/tools.test.mjs` (Clopper–Pearson against published values) | |
| The judge is unreachable from the filter and the MCP server; no process or network | `test/isolation.test.mjs`; the import-graph test in `test/mcp-server.test.mjs` | |
| The MCP server behaves as declared and refuses bad input | `test/mcp-server.test.mjs`; the real transcript `transcripts/2026-11-26T004241768Z-70635.jsonl` (call 3 refused) | |
| The reject audit and the recheck | my 45 verdicts and 14 rechecks; `audit/RESULTS.md` recomputed by `tools/audit-results.mjs` | by hand |
| Claim labels | my confirmed labels, re-checked by `tools/confirm-claims.mjs` | by hand |

## Not checked (at least three real items): written by Aravind

- 
- 
- 

## Not claiming: written by Aravind

- 

**Signed or withheld:** ____________ (name, date)

---

## Driver's seat

| Task | Claude should do | I should do | Why |
|---|---|---|---|
| Write and run the filter, tests, sampling, intervals | draft the code, run it, report counts with exact intervals | decide the rules and the thresholds; check the tests catch the wrong versions | a rule encodes my priorities; Claude can implement them, not choose them |
| Judge postings (audit, labels) | build blind sheets and tools; never fill a verdict | judge every row myself, against the written definition | the ground truth is my judgment; a model's judgment would make the audit circular |
| Justify a shortlisted posting | split it into claims with exact quotes; propose labels; abstain when the text is silent | confirm each label; catch claims that are entailed but not relevant | entailment can be checked mechanically, relevance can't |
| Decide whether a posting is worth my time | surface it with its evidence and its known limits | **decide, and decide whether to apply** | it depends on things no posting states: my goals, my visa situation, my tolerance for a stretch role, timing. It's my career and my risk. |
| Trust a tool server | read the source, test declared vs actual, mark verified vs inferred | make the trust decision and choose the configuration (`--read-only`, `--confine-roots`) | the risk falls on my machine and my files |
| Change a rule after seeing results | measure before and after; label it as dev use; refuse to change it just to grow the list | approve every change and own the post-hoc ones | changes made after seeing results are where self-deception gets in; the honesty record is mine |
