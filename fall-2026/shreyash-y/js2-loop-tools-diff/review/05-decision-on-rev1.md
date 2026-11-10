# Decision on patch revision 1: REVISE

*Shreyash's words, typed into the session on 2026-11-09 after running the three commands in `04-commands-run-by-shreyash-2026-11-09.txt`. Claude Code added only this heading and note.*

I want to revise the patch because even though all 84 tests passed, the 16 Linear postings show that the logic is still making mistakes. It is treating perks as job requirements, which can lead to incorrect results. I don't want to accept the patch just because the tests are green. I'll fix the perk misread, add regression tests using those real postings, and rerun the tests before accepting it. I'll leave the current evidence unchanged so I can show what went wrong and how I fixed it.
