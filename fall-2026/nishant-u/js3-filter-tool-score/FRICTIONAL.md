# FRICTIONAL — Job-Search Agent 3 (nishant-u)

An honest log of what went wrong, what I checked, and what I accepted, changed or rejected. JS2's log is `fall-2026/nishant-u/js2-loop-tools-diff/FRICTIONAL.md` at `f956e22`; JS1's is linked from there.

## 2026-11-24 — The abstention threshold never fired

FILTER.md v1 abstains when a posting's text is under 300 characters after removing HTML.
- **What the data showed:** on all 182 postings it fired **0 times**. The shortest posting is 2,679 characters.
- **The limit:** I could only show the rule's limits with a constructed posting. In SHORTLIST.md, 880 characters of company boilerplate plus a one-line role were accepted by both v1 and v2 instead of abstaining.
- **What I learned:** counting characters doesn't measure how much the text says about the job.
- **Unresolved:** I haven't changed the rule.

## 2026-11-24 — F3 rejected Poshmark's US offices

Before writing any tests I read the real location strings. Poshmark writes US offices as `US California (Redwood City) - Office`, which ends in neither a state code nor "Remote", so F3 v1 rejects it.
- **What I did:** I kept v1 literal, and a test pinned the behavior, so the audit would have to find it rather than me patching it quietly.
- **The fix:** v2 change 7 accepts `US <State> (<City>) - Office`.
- **The effect:** it changed no verdicts. Every such posting fails F1 first. So the fix is right, but this data doesn't test it.

## 2026-11-25 — False friends

Four disagreements in the reject audit came from a title word matching or blocking for the wrong reason:
- **"Lead" (row 4):** *Strategy & Analytics Senior Lead* is "a high-impact individual contributor".
- **"Lead" (row 28):** the same pattern.
- **"Manager" (row 10):** *Insights Manager II* is "the analytical backbone".
- **"Software Engineer" (row 30):** the title hides "ML infrastructure" work.

Near misses, where the verdict was right but the word could mislead:
- **"AML":** anti-money laundering. Whole-word matching saved it.
- **"Ads Manager":** a product name.
- **"hybrid":** "preload vs. tool-calling vs. hybrid", about AI architecture, was quoted as evidence against "Remote".
- **"Employer-sponsored retirement plan":** C3 correctly ignored it.

## 2026-11-25 — The v2 decisions: what they fixed and broke

I accepted changes 1 (cut "lead"), 2 (count Priya's résumé practices in F4), 7 (US office form) and 8 ("hybrid" needs office/day/schedule words). I rejected 4, 5 and 6.
- **Fixed:** on my 45 audit verdicts, v2 fixes rows 4, 8, 27, 35 and 44.
- **Broke:** row 15. A Staff scientist who will "mentor or manage" is now accepted; I accepted that as a known miss.
- **Still missed:** rows 10, 28 and 30.
- **Unaudited:** one posting I never judged changed verdict (*Strategy & Analytics Lead*).
- **The catch:** agreement went from 37 to 41 of 45, but on the same sample that suggested the changes, so it overstates the improvement. v2 hasn't been tested on a fresh sample.

## 2026-11-25 — The C2 "MySQL" quote bug

While writing SHORTLIST.md, I found that `faire:8806617002`'s "Uses SQL: supported" quoted a sentence containing only "MySQL".
- **Cause:** the label was right, but the code located its quote with a substring search instead of the whole-word match.
- **Fix:** in `409b995`, with a regression test. Labels and verdicts didn't change.
- **Left as is:** the committed v1 output still shows the old quote, so re-running v1 now matches `results.json` byte for byte but differs from `shortlist.md` by that one quote.

## 2026-11-25 — My held-out labels were exposed to the audit

For SCORE.md I measured v1 vs v2 on my JS1 held-out labels.
- **The problem:** 4 of the 10 held-out postings were in the reject audit I used to choose v2. Two of them (rows 44 and 27) are among the postings change 2 was designed to fix.
- **A second problem:** the JS1 labels are my old keyword rule applied by hand. v1 matches them 10/10 almost by construction. v2 scores 8/10 because it disagrees exactly where I decided to change the rule.
- **What I did:** logged the exposure in SPLIT.md (`bcf17ad`).
- **Unresolved:** a fair test of v2 still needs fresh labels under my audit rule.

## 2026-11-25 — The reference-server run failed on a client path bug

My first scripted-client run against the course server sent nothing. The client computed the repository root one level too shallow (`parents[2]` instead of `parents[3]`), so it started a file that doesn't exist, and the process exited. No transcript was written. The client was fixed and the run repeated; that run is the reference transcript.

## 2026-11-25 — Redacting private paths from the transcripts

Claude Code's event stream from the MCP run contained my Windows user name, local plugin, memory and socket paths, and my installed skills. Two client-side logs had absolute paths in the server command.
- **What's committed:** redacted copies.
- **What's kept locally:** the originals, in a git-ignored folder. Their sha256 hashes are in `mcp_server/CLAUDE-CODE-RUN.md`.
- **Prevention:** the client now logs repo-relative paths.

## 2026-11-25 — My server's descriptions overstated what it does

My server's `initialize` instructions said "Read-only", but the server appends every message to its transcript log. Its tool description made "score" sound like a fresh judgment, when it returns a saved FILTER.md v2 verdict for postings collected on 2026-11-10. I said so in my trust decision, and fixed both descriptions in `32f95f1`, with a test pinning the wording. The transcripts keep the old wording, as recorded.

## 2026-11-25 — Excel broke the encoding in audit.csv

After I saved `audit/audit.csv` from Excel, 11 notes showed double-encoded characters (`rÃ©sumÃ©`, `â€”`).
- **The first fix:** that version had already been committed. Before anything was pushed, I repaired it and replaced that commit, and the replaced commit was pruned from the repository.
- **A second change:** a later save changed "résumé" to "resume" and em dashes to hyphens. That version is the audit commit, `b8b0a20`.
- **Effect on results:** none of this changed a verdict.
- **What I'd do differently:** edit the CSV in a text editor, or check its encoding before committing.
