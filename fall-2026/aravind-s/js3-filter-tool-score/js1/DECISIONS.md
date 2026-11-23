# My decisions for JS1

Every choice below was mine, made in the Claude Code app on 2026-10-30 and 2026-10-31 (Eastern time), most of them as multiple-choice picks among options Claude Code laid out. Times are approximate. The commit that applied each one is named, so the split between what I decided and what Claude Code did can be checked in the history. Conversation transcripts stay on my machine, as the brief asks; this log is the record instead.

| When (ET) | Decision | Applied in |
|---|---|---|
| 10/30, earlier chat | The board: OpenAI on Ashby, after comparing it with Databricks. The persona Jane Doe: my situation, none of my identity. Python standard library only. Claude through Claude Code on my seat, no API key. | CONTRACT.md, persona/ |
| 04:45 | Contract picks: up to 3 years and a posting that states no years passes; software-engineering titles; all four wrong versions; the watch failure sentence. | e989f8b |
| 04:50 | Framing: the contract reads as mine, and SOURCES.md says Claude Code wrote the wording from my decisions. | e989f8b, SOURCES.md |
| 04:58 | "Commit it": CONTRACT.md is the first commit. | e989f8b |
| 05:26 to 05:31 | I ran the tests (53 passed) and the planted mistakes (13 of 13 caught) myself. | 304c0a0 |
| 05:31 | "Yes, commit and run": the watch committed, then the Friday baseline. | 304c0a0, 629a279 |
| 05:40 | Claude Code may commit each step on 10/30 without asking each time; pushes and the PR still need me. | all later commits |
| 05:40 | Labeling rule: the seven checks plus seniority in words; a required specialty Jane lacks makes a posting not relevant; 20 engineering postings, 10 + 10 by the rule, seed 7375. | b6b2b13 |
| 06:05 to 06:15 | My 20 hand labels: one pick per posting for the ten the rule passes, read from their requirement lines and the sheet; one confirmation for the ten the rule rejects, which part 1 of my labeling rule decides. | 882909e |
| 06:27 | The prompt experiment's one change: add the specialty point. | 2196c65 |
| 06:32 | The agent keeps the baseline prompt; I run live run 2 myself on Saturday; GitHub waits for Saturday, after review; the action surfaces are run for real, all three. | ce7aea6 |
| 07:00 | An independent review of the whole repo before anything is public. | 5ab508d |
| 07:25 | Rewrite the three commits that held my account name, before the first push; keep my contract's wording; relabel posting 11 as a missing specialty and report both scorings. | history before 5ab508d, c254ab9 |
| 07:40 | After the rescoring, keep the baseline prompt: it is my contract's seven checks, and ten cases cannot separate it from the revision. The specialty point waits for a contract v0.2. | README.md |
| 10/31 19:10 | I ran live run 2 myself. | runs/2026-10-31T231042Z |
| 10/31 19:12 | I ran the 99 tests, the 37 planted mistakes and the independent recompute myself. | README.md, sign-off |
| 10/31 19:15 | My sign-off: four "not checked" items, way 1 as the least autonomy that suffices, signed. Publishing: commit, my public repo, the course PR, the zip. | README.md, ACTION-SURFACE.md |
