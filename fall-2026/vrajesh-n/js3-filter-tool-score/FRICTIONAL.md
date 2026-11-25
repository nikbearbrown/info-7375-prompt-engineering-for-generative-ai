# FRICTIONAL - JS3

> The entries are my (Vrajesh's) own words, given to Claude Code in chat and placed here verbatim. [Brackets] are Claude's notes with facts, not my words. The traceability table at the end was compiled by Claude from the files and runs.

## 2026-11-25

**The audit surprise.**
"The audit surprise: The biggest surprise was that R4 matched nothing. Having a sponsorship rule in the code had made it look as though that condition was covered. The kept postings exposed more problems than the random rejects, so checking only rejected postings would have missed an important failure."
[Facts: v1 R4 matched 0 of 3,068 postings; the v2 wording moved 14 Roblox postings to R4. In the audit, 0 of 35 random rejects were false rejects, and 3 of the 15 kept postings were wrong, with 2 more marked "?".]

**My own labels.**
"My own labels: The inconsistencies showed that the reference labels needed checking too. “Unknown” should have been “?” rather than N. For items 22 and 24, the same Go mention should receive the same judgment. I accepted the correction to item 24 while preserving the original labels as the record of the blind check."
[Facts: audit labels 26 and 34 were changed from N to ? in commit `cbcec48`, after the key was opened; the originals are in `183e7f3`. Claim-check items 22 and 24 are two different Glean postings with the sentence "C++/Java/Python/Go"; `claim-check-labels.csv` still has 22 = supported and 24 = insufficient, unchanged since `934163a`, and the labeler now agrees with 22, not 24 (23 of 24 agree).]

**What I accepted, changed or rejected from Claude.**
"Claude’s suggestions: I accepted restricting stack-fit to documented project technologies, but rejected excluding “or” and slash lists. A list still supports “names a technology”; it does not establish that the technology is required. I also accepted the network-guard fixes and chose variant B, while keeping the evidence for B explicitly weak."
[Facts: shipped-only `stack_fit` and the dropped option-list exclusion are in `b53a43c`; the network-guard fix is in `31c4313`; variant B became the default in `b805498`.]

**A wrong claim.**
"A wrong claim: Both examples reduced my willingness to accept a description without checking its implementation. “No network” was stronger than the guard demonstrated, and “shipped” was stronger than a skills-list match. I want the wording, code, and tests to support the same claim."
[Facts: the first guard patched `connect()` only and `connect_ex()` still connected (`review/14-network-guard-red.txt`); the first `stack_fit` statement said "shipped" while the code matched the whole skills list (`review/9-stackfit-tests-red.txt`).]

**The server work.**
"The server work: The recorded server/discover probe showed that successful integration depended partly on the client’s fallback behavior. The fetch findings also showed why a read-only annotation is not a complete description: the default could install dependencies, and the prompt interface could fetch a page that the tool refused under robots.txt."
[Facts: Claude Code's first message to my server was `server/discover` (protocol 2026-07-28), answered -32601, then it fell back to `initialize` (`transcripts/claude-code-server-side.jsonl`). The `npm install` default was read in the fetch server's source and not run; the `prompts/get` fetch of the disallowed page is in `evaluations/fetch-server/2-allow-private-ips.jsonl`.]

**What remains unresolved.**
"What remains unresolved: “U.S. Person Required” needs separate handling from sponsorship and clearance. “Clearance is a plus” should not be treated as mandatory. Variant B remains a provisional choice: three favorable differences and p = 0.25 do not establish a general improvement, especially without repeated runs."
[Facts: 3 shortlisted Palantir postings say "U.S. Person Required"; R5 still rejects "clearance is a plus" (audit item 55); the one-change result is 3 misleading without the statement, 0 with it, no A-against-A repeat (`REPORT-one-change.md`).]

**What I checked myself.**
"7. What I checked myself: I made the recorded scope and default-behavior decisions and discussed the disagreements. The CSV judgments, The commands, implementation inspection, and test runs were performed by me."
[Claude's note, not Vrajesh's words: within this Claude Code session, Claude wrote the code and ran the commands and test runs through its tools, and I did not write any of the label files (`audit-labels.csv`, `claim-check-labels.csv`, `onechange-labels.csv`); they were filled in between Claude's turns. SOURCES.md and the sign-off describe Claude's part, and the sign-off "How" line has to match what Vrajesh did himself.]

## Traceability (compiled by Claude)

| What | Where |
|---|---|
| FILTER.md written before any JS3 code | commit `63e249b` (FILTER.md only) |
| Tests before code for the filter; wrong filters W1-W3 | `tests/cases.py`, `tests/wrong_filters.py`; red run `review/1-tests-before-rule-change.txt`, green `review/2-...` |
| R4 matched nothing | `results/filter-v1-summary.txt`, `scripts/diff_runs.py results/filter-v1.json results/filter-v2a-r4.json` (14 postings) |
| Audit labels, then key | labels `183e7f3`, key opened after; edit to items 26 and 34 `cbcec48` |
| Audit numbers | `scripts/audit_summary.py`, `results/audit-summary.txt`, `review/AUDIT.md` |
| Claim labeler: en-dash bug, shipped-only, option lists | `review/7-...` to `review/10-...`; `b53a43c` |
| MCP server tests first; real Claude Code run | `review/11-...`, `12-...`; `transcripts/` |
| Network guard weaker than claimed | `review/14-network-guard-red.txt`, `review/15-...` |
| Fetch server evaluation | `evaluations/EVAL-fetch-server.md`, `evaluations/fetch-server/` |
| One-change experiment | held-out pairs `55a0bae`; labels `a116952`; report `f73c95c`; default B `b805498` |
