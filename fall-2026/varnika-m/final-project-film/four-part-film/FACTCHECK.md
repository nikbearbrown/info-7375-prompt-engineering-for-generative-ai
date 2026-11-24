# Fact check — A Job-Search Agent You Can Check

Status: claims checked 2026-11-23 by Claude Code against the files named below. The JS1 and JS2
test counts were re-run that day (73 OK, 122 OK). The company-page claims in Part 2 were researched
by Claude Code on 2026-11-23, and every quote was matched word for word against the saved pages in
`evidence/others-2026-11-23/`. Varnika supplied claim 1 (her own reason) and chose the pass line
used in Part 4. Varnika watched the final cut and approved it on 2026-11-23.

Every factual claim in the narration or on screen. Plans ("will") are not facts. They are listed
only where a drawing could be mistaken for something that exists, and every such drawing carries
a "planned" label on screen.

| # | Beat | Claim | Verdict | Source | Fix |
|---|---|---|---|---|---|
| 1 | B01 | I'm searching for a job myself, and reading hundreds of postings by hand takes hours | EXEMPT | Varnika's own reason, chosen by her on 2026-11-23 | — |
| 2 | B01 | "hundreds of job postings" | PASS | One board alone had 675 (claim 4) | — |
| 3 | B01 | Drawing of a shortlist where each posting shows why it made the list | EXEMPT | Planned (JS3 shortlist); on-screen "planned · drawing" | — |
| 4 | B02 | On October 31, my written rules checked all 675 postings on Anthropic's job board against a made-up candidate; only one matched | PASS | `../../js1-contract-and-watch/README.md` (run table: 675 postings, live run 2026-10-31; line 132: rule on the whole board, 1 match of 675); `../../js1-contract-and-watch/SOURCES.md` row of 2026-10-31 (Rules 1–5 are Varnika's own `CONTRACT.md`) | "made-up candidate", never a real person |
| 5 | B03 | It won't apply for jobs or send anything | PASS | `../../js2-loop-tools-diff/POLICY.md`: `POST`, `mailto:` and every host off the allow-list are refused, in code (boundary cases B01–B28) | Said of the agent as built; no claim about future code beyond the plan |
| 6 | B03 | It will hand a person the shortlist; only that person can say yes, no, or not yet | EXEMPT | Planned (JS5 approval gate); on-screen "planned · drawing" | — |
| 7 | B04 | A tool that picks jobs should show its reasons so you can check it | EXEMPT | Argument, not a factual claim | — |
| 8 | B05 | LinkedIn and Indeed save your search and send new postings daily or weekly | PASS | `evidence/others-2026-11-23/li_alerts.html` ("create a job alert for your current search criteria"; "The job alert will default to daily"); `indeed.html` ("A job alert is an email notification about new jobs on Indeed"; "You can choose between daily or weekly emails"). Fetched 2026-11-23 | — |
| 9 | B05 | Their help pages don't explain why a job matched | PASS | Same two pages: no explanation of why a job matched | Limited to those help pages |
| 10 | B06 | LinkedIn's Skills Match compares your profile with the job description | PASS | `evidence/others-2026-11-23/li_skills.html`: "The Skills Match insight allows you to see which job opportunities are a good fit by comparing your profile with the job description." Page says "Last updated: 2 years ago" | — |
| 11 | B06 | Jobright says its agent matches roles and applies for you | PASS | `evidence/others-2026-11-23/jr_agent.html` (jobright.ai/ai-agent): "proactively matching roles, customizing your resume, and applying for you." | Said as "says", a company claim |
| 12 | B06 | LazyApply says its agent handles the entire application | PASS | `evidence/others-2026-11-23/lazy.html` (lazyapply.com): "Our agent handles the entire application process." | Said as "says", a company claim |
| 13 | B06 | Simplify's Autopilot submits with no review step | PASS | `evidence/others-2026-11-23/simp_auto.html`: "There is no review step before submission." | — |
| 14 | B06 | Simplify's Copilot mode leaves the final click to you | PASS | `evidence/others-2026-11-23/simp_copilot.html`: "click the employer’s final Submit button yourself." | Included so the film does not claim that no tool has a human step |
| 15 | B07 | None of these pages mentions rules you can recheck, a separate program that checks each run, or a person approving the shortlist | PASS | The seven saved pages above, read on 2026-11-23 | An absence claim about these pages only, not about every tool |
| 16 | B08 | The data comes from public job board feeds that need no login: Anthropic on Greenhouse, Palantir on Lever, Linear on Ashby | PASS | `../../js2-loop-tools-diff/config/boards.json`; JS2 README ("credentials (there are none)") | — |
| 17 | B08 | The candidate, Aarav Patel, is made up; no real person's data is used | PASS | `../../js2-loop-tools-diff/persona/` (fictional résumé, `@example.com`, 555 phone); JS1 fictional-résumé check | — |
| 18 | B09 | In JS1 the agent watched one board, reported only new postings, and judged each with five written rules: title, seniority, location, experience, skills | PASS | `../../js1-contract-and-watch/README.md`; `CONTRACT.md` Rules 1–5 (Job title, Seniority, Location, Experience, Skills) | — |
| 19 | B09 | On screen: "JS1 · 73 tests" | PASS | Re-run 2026-11-23: `Ran 73 tests … OK` | — |
| 20 | B10 | In JS2 it became a loop over four boards on three systems, with a budget and a permission policy in code that blocks any site not on its list | PASS | `../../js2-loop-tools-diff/README.md`, `GATE.md`, `POLICY.md`, `agent/policy.py` | On screen, the fourth board is marked as failing on purpose (it does) |
| 21 | B10 | One run read 1,014 postings | PASS | `../../js2-loop-tools-diff/jobs/runs/2026-11-10T212848Z.json`: Anthropic 677 + Palantir 304 + Linear 33 = 1,014 | Source tag shows the sum |
| 22 | B10 | It has 122 tests | PASS | Re-run 2026-11-23: `Ran 122 tests … OK` | — |
| 23 | B10 | A separate checker caught a real bug in one of my own runs | PASS | JS2 README: live run 2 (run by Varnika) → `check_run.py` NOT SUPPORTED, `gone_recomputed`; `REVIEW-FINDINGS.md` row 7b | — |
| 24 | B11 | Next steps: filter + audit + tool (JS3), plan + checks + memory (JS4), approval tied to the exact shortlist (JS5) | EXEMPT | Planned, from the JS3–JS5 briefs in `assignments/`; on-screen "planned" | — |
| 25 | B12 | Python with nothing to install | PASS | JS1 and JS2 READMEs: standard library only | — |
| 26 | B12 | Claude Code through my university | PASS | JS1 README (Claude Code CLI 2.1.283 for the judge); NEU-provisioned (October `../SOURCES.md`) | — |
| 27 | B12 | Free public job boards; my laptop | PASS / EXEMPT | Boards: claim 16. Laptop: self-report (all runs on Varnika's Mac) | — |
| 28 | B12 | No paid API credits are needed | PASS | JS1's Claude judge runs through `claude -p` (Claude Code); JS2 calls no model | A plan statement for JS3–JS5 |
| 29 | B13, B14, B16, B17 | The four checks and their pass lines | EXEMPT | Planned evaluation; on-screen "planned check". Pass line chosen by Varnika on 2026-11-23 ("Strict"); see `APPENDIX.md` | — |
| 30 | B14 | A healthy run should skip at least half of what it sees | PASS | `assignments/assignment-js5-the-gate-the-register-and-the-supervised-run.md`: "A healthy run skips at least half of what it evaluates" | — |
| 31 | B15 | In my second assignment, the checker already caught one planted failure | PASS | `../../js2-loop-tools-diff/FINISHED-WRONG.md`: wrong version W5 on a constructed empty response ended `finished`; `check_run.py` said NOT SUPPORTED | On screen "seeded" |
| 32 | BOUT | Title and name | EXEMPT | Film title set in `make_sheet.py` (`TITLE`); name as on my earlier films | — |
