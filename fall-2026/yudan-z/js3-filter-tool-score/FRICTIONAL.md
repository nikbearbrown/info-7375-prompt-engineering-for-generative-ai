# FRICTIONAL — Job-Search Agent 3

Yudan Zhou (@yudanzhou) · INFO 7375 · 2026-11-25

*Drafted with Claude from this session's record; I reviewed every entry and agree with it (2026-11-25).*

This is a log of where the work did not go as planned. For each entry it says who found the problem, what I decided, and where the change shows.

| # | What happened | Who found it | What I decided or changed | Where it shows |
|---|---|---|---|---|
| 1 | My first filter kept **1 of 1,595** postings. The four companies post almost no jobs titled "Data Analyst" or "Business Analyst" | the v1 run | The plan (proposed by Claude, which I accepted) was to label before changing anything, so the change would be measured, not guessed | AUDIT §1, `4469e7b` |
| 2 | I labelled 30 of 61 rows Y on my first pass. Claude then checked the Y rows against the full text: 14 of them had a deciding sentence that the label sheet's excerpt **did not show**, such as a security-clearance requirement or a 4+ year minimum | Claude, after my first pass | I re-read the 14 sentences. I changed 8 to N and kept 6 as Y. The first pass is kept unchanged in git. **Only my Y rows were re-checked, so my N rows may hold the same kind of error** | AUDIT §2, `2ef8ac2` → `72a0b61` |
| 3 | I edited `LABEL-ME.csv` directly instead of the re-check sheet Claude made, and asked whether row 8 had been changed. "8 行" in Claude's message meant **eight rows**, not row 8 | me | Nothing was lost: Claude compared both files cell by cell | `labels-pass2.csv` |
| 4 | Row 39 (*Senior Associate*, 4+ years) was Y, while rows 5, 6 and 13 (senior titles) were N with the note "经验不足" | Claude | I changed row 39 to N for consistency | `labels-final.csv` |
| 5 | My Y labels include engineers, strategists and a legal-ops role, not just analysts | Claude asked which rule my labels followed | **My rule is "any entry-level US job Mira can apply to."** This is broader than the persona's five target roles. I chose to keep my labels and change the filter, not the other way round | FILTER §5, AUDIT §2 |
| 6 | Dropping the 3+ years penalty (v2e) found 2 more Y rows on the development set | Claude's measurement | **Rejected it.** It did nothing on the held-out rows and doubled what reaches Mira | SCORE-CHANGES §2 |
| 7 | The first time v2 was measured, every number was identical to v1 | Claude | The v2 files had a "threshold 5 → 0" description but still said `"threshold": 5`. A change that is described but not made looks exactly like a change that does nothing. Fixed before any result was recorded | `filter/filter-v2a.json` |
| 8 | In the real Claude session, the first posting scored listed **Excel** as a skill. The word in the posting was "everyone can **excel**". This is true of 927 of 958 matches | the MCP session, read by Claude | **Adopted** the fix, though my labels cannot measure it (48 unlabelled postings are no longer shown) | AUDIT §4, step v2f |
| 9 | All three v3 "keeps" said "does not rule out sponsorship: **supported**", quoting "sponsor you for relocation" and "executive sponsorship" | Claude, reading the v3 keeps | This broke my own FILTER.md §2. v4 needs a sponsor word **and** a visa word. Result: **0 keeps**; all 138 postings are "cannot tell" | SHORTLIST §2 |
| 10 | The rule from #9 still accepts "Visa sponsorship is available for senior roles only" | Claude, constructing a counterexample | Not fixed. A test pins the wrong behaviour so it cannot change silently | SHORTLIST §3 |
| 11 | Claude Code opened with `server/discover`, a newer handshake my server does not know. The session worked only because the client fell back to `initialize` | the server's own log | Recorded as "declared vs actual". My server did not handle it; the client did | TOOL-SERVER §1 |
| 12 | My server's tools say `readOnlyHint: true`, but the server writes a log file | Claude, writing the evaluation | Stated in TOOL-SERVER §1 as a gap; not changed | TOOL-SERVER §1 |
| 13 | While designing v2b–v2d, Claude printed all 61 rows, the held-out ones included | Claude, writing SCORE-CHANGES | My held-out set is **not blind**. SCORE-CHANGES §3 says so, rather than presenting it as untouched | SCORE-CHANGES §3 |

## What I accepted, modified and rejected from Claude

- **Accepted:** the sample design; filter steps v2a–v2d; the v4 evidence fix; the MCP server.
- **Modified:** my own labels, after reading what the sheet had hidden (#2, #4).
- **Rejected:** v2e (#6). Claude's first-pass sheet as a basis for judging rows, because its excerpts left out deciding sentences.

## What is unresolved

- **Graduation years.** No rule reads graduation years. Row 46 ("graduating in 2028") still reaches Mira.
- **"Manager" as a senior word.** It marks *Associate Product Manager, New Grad* as senior.
- **Qualified yeses.** "Sponsorship for senior roles only" is read as yes (#10).
- **My N labels** were never checked against the full text (#2).
