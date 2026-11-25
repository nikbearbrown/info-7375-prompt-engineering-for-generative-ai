# Sources

JS1's sources are in [js1/SOURCES.md](js1/SOURCES.md); everything listed there still applies to the code JS2 builds on.

## How the work was split

The gate came first. I made its calls: the boards (from my own target list), the budgets, one retry for transient failures only, my approval for replacing or deleting a board's state, and all four wrong versions, picking each after seeing the measured numbers. Claude Code laid out the options, proposed the defaults I accepted, and put it all into words; I approved GATE.md before any JS2 code existed (`84d9f4c`, 2026-11-07, 1:45 AM ET). Only then did Claude Code write the code, the tests and the tools against it.

I ran every live run in `runs/` from 2026-11-08 on, and every command in [MY-CHECKS.md](MY-CHECKS.md). I typed my 19 boundary predictions before any boundary test existed, every part of REVIEW-PACKET.md marked as mine, every FRICTIONAL.md entry, my sign-off and the reasons in the driver's seat. Claude Code copied those word for word and added only headings, dates, labels and evidence lines.

## What Claude Code did, specifically

- **Before the gate (2026-11-06):** sent one GET each, with `curl`, to seven public boards (Snowflake, Ramp and Plaid on Ashby; DoorDash, Databricks and Verkada on Greenhouse; Palantir on Lever) and to a made-up name on each system, to count postings and sizes for the options it gave me. The answers were kept only in its scratch folder and are not evidence. It also listed the files in Lectern and in one classmate's merged JS2 folder in the course repo, read Lectern's board list (`sources.json`) and the folder's commit messages, and opened no other file of either. No code or text from either is used.
- **Wrote GATE.md's text** from my decisions and the defaults I accepted; its last section says which is which.
- **Wrote layer 2:** the loop, the three systems' adapters, the permission policy, the fetch, the budgets, the per-board state, the trace and the report (`job_agent/`); 107 new tests (206 in all); 24 new planted mistakes in `tools/mutants.py` (61 in all); and the tools `check_run.py`, `wrong_answer_demo.py`, `boundary_table.py`, `explain_rule.py` and `rule_verdicts.py`.
- **Rehearsed the loop once** on 2026-11-07 at 2:22 AM ET, from a scratch copy of the repo, against the live boards, with no Claude calls, to check the code before my first run. Not kept, not evidence.
- **Found the Claude Code update problem** on 2026-11-08: the desktop app had moved the CLI from 2.1.309 to 2.1.317, whose new built-in plugin `cc-plugin-privacy` made the lockdown refuse every call. It made two Claude calls that day, one that showed the refusal and one that checked the fix, kept only in its scratch folder; the first call's startup record, with its folder path replaced, became `tests/fixtures/claude-code-2.1.317-init.json`. I decided to trust the plugin (`8ca0d4b`).
- **Wrote the 19 boundary cases** (the list on 2026-11-07, the tests on 2026-11-08 after my predictions were committed in `21f33b7`) and filled BOUNDARY-TESTS.md's Actual column with `tools/boundary_table.py`.
- **For the review packet:** recommended the defect (posting 19, noted in JS1), measured how readings A to D would change the verdicts and recommended E, drafted my test `tests/test_years_v02.py` from my pick E (I ran it before the patch, and it failed), and wrote the patch (`4b1a418`). The packet marks every part that is mine.
- **Fixed a bug in its own report code** that my second run exposed (55 postings counted as judged after waiting, where 20 were): a regression test that failed first, then the fix (`e42796d`).
- **Fixed three problems of its own on 2026-11-09**, at my word: `tools/boundary_table.py` added its summary paragraph again on each refill (BOUNDARY-TESTS.md had it twice); `tools/explain_rule.py` could no longer show posting 19's bug after the patch, so it now takes `--contract 0.1`; and five links in `js1/` pointed to `experiment/` from the wrong folder. The four new tests in `tests/test_doc_tools.py` came with the first two fixes, and three of them failed before the fixes.
- **Wrote README.md, this file, and the facts around my words** in BOUNDARY-TESTS.md, REVIEW-PACKET.md and MY-CHECKS.md, and, on 2026-11-09, ran the independent check on all five live runs and recomputed the new and gone postings of that day's run from the saved answers alone.
- **Checked what I wrote against the record and the code** before it went in (my FRICTIONAL.md entries, my parts of the review packet, my sign-off and my driver's-seat reasons), and asked me to rewrite what did not match. The text is mine; it did not reword it.
- **Wrote an explainer of the whole agent for me** on 2026-11-09 (facts and concepts only, no answers), so I could write my sign-off, driver's-seat reasons and Monday entry myself.

## What I used

- The JS2 brief, in the course repo (`assignments/assignment-js2-the-loop-the-tools-and-the-diff.md`), and the course's Frictional guide (`prerequisites/frictional.md`).
- My own JS1 agent (layer 1, final commit `d8b3896`), the starting point for all of JS2.
- Three public job-board APIs, GET only and with no login: Ashby's posting API (OpenAI), Greenhouse's job board API (Verkada) and Lever's postings API (Palantir). All three companies come from my own new-grad target list.
- The Claude Code CLI 2.1.317, signed in with my claude.ai seat (no API key), model `claude-sonnet-5-5`.
- Klaxon, my own project (github.com/AravindKumar2504/klaxon): the locked-down Claude Code adapter and the mutation runner's approach, as in JS1.
- The Reallocation Engine (Nik Bear Brown, MIT license): Jane Doe's résumé layout, from JS1. Its ATS providers and `greenhouse-watch` skill were not used.
- Lectern (`fall-2026/nik-bear-brown/lectern` in the course repo): its board list was read on 2026-11-06 while I chose boards. Its collectors were not used.
- Python's standard library only.
- Another AI assistant organized my notes for the sign-off, the driver's-seat reasons and my Monday entry, from Claude Code's explainer, as the course's Frictional guide allows ("AI can organize your notes; you must supply the actual experience"). The experience and the final sentences are mine.

**The course AI policy:** I read the course AI policy and watched its video, titled "AI Policy for Professor Bear's Courses | Using AI Responsibly in Class", before starting JS1.
