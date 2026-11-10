# FRICTIONAL: Job-Search Agent 2

My log for JS2. Each entry is my own text, sent in chat; Claude Code copied it here word for word, adding only the dated headings and the evidence lines. Times are Eastern. JS1's log is in [js1/FRICTIONAL.md](js1/FRICTIONAL.md).

## Friday 11/6 to early Saturday 11/7 (written Sunday 11/8)

- **What I expected:** Signed in to Canvas on Friday afternoon expecting a straightforward setup process and standard rule definitions for the new assignment.
- **What surprised me:** The unexpected strictness required during the late-night gate setup around 1:00 AM, specifically navigating the permission boundaries and making sure every single potential failure case was accounted for before locking down GATE.md.
- **Why I'm typing my own notes now:** Taking full personal ownership of every reflection and note to ensure complete academic integrity, avoiding the generic AI phrasing that cost points on previous assignments.
- **Why 20 Claude calls:** Chose 20 calls because OpenAI alone has accumulated around 60 new postings since the last run, capping it at 20 judges a solid batch per run while keeping execution fast and within budget, leaving the rest of the backlog to wait for subsequent runs as designed.
- **What I hadn't checked yet:** As of early Saturday morning, no real run had actually been executed yet, I hadn't run the tests myself, the actual loop code hadn't even been written yet, and nobody knew about the upcoming Claude app update or the cc-plugin-privacy plugin.
- **What I decided versus what Claude did:** Claude laid out the options with measured numbers first and proposed defaults for the exits, repeat rule, and field mapping. I chose the budgets, error policies, and permission rules, and approved GATE.md (84d9f4c), while Claude drafted the code, tests, and documentation based on those accepted choices.

Evidence: GATE.md (`84d9f4c`); the build commits `ab2df17`, `10833a9`, `5df1dc4`.

## Sunday 11/8

- **App update and plugin trust:** Encountered the unexpected Claude app update (from 2.1.309 to 2.1.317) and chose to trust the new cc-plugin-privacy plugin because the call loaded zero tools, servers, or commands, accepting the reality of not knowing the plugin's internal workings.
- **Boundary predictions and Case 8:** Ran the 19 boundary tests with 18 of 19 matching my initial predictions, learning from case 8 that while the initial request to api.lever.co was allowed, its redirect to evil.example was correctly blocked as designed.
- **First real runs and backlog:** Executed the first real runs across the day using 75 Claude calls (74 valid, all agreeing with my rule), with the OpenAI backlog waiting across multiple runs before being completely cleared by the fourth run, which ended incomplete instead of budget-exhausted.
- **Guess versus actual count:** Guessed 12 candidate flips for the year-reading change before seeing the data, whereas the actual count turned out to be just 2.
- **Review and accept decision:** Reviewed the review packet and accepted the patch because both flips were completely correct, the tests went from 4 of 5 failing to 5 of 5 passing, and all 61 planted mistakes were caught.
- **Demo and independent check:** Saw how the independent check_run.py tool successfully caught the planted wrong version 1(a) where a 404 board was falsely reported as a finished, successful read of zero postings.
- **What I'm still unsure about:** Whether sentences stating years purely as a bonus (such as "10+ years in the industry is a plus") will end up incorrectly rejecting otherwise strong candidate postings.

Evidence: the plugin decision (`8ca0d4b`); my predictions (`21f33b7`) and the boundary tests (`e569577`); my four runs (`8aa6075`, `62ef1a6`, `0be7a10`, `84630ab`) and the report fix my second run exposed (`e42796d`); the demo (`c03eb75`); the review packet, from my guess (`e3ea1e2`) and my failing test (`788852b`) to the patch (`4b1a418`) and my decision (`584eac4`); every command I ran, in MY-CHECKS.md.

## Monday 11/9

- **Tried and expected:** Expected the run to end incomplete (code 1) or budget-exhausted before my 4:07 PM run.
- **Friction and response:** I ran the independent check at 4:12 PM using python3 tools/check_run.py runs/2026-11-09T210704Z. It checked the report against the saved raw board responses and showed no disagreement. The run had found 15 new postings and 22 gone postings, and all 15 new postings were judged.
- **What I did vs. what Claude did:** Claude drafted the documentation and ran the recomputations; I read the drafts before confirming them, ran the live run resulting in `incomplete` due to the 404 made-up board, and approved the run and check commits (`b490e1c`).
- **Verifications and approvals:** Ran `check_run.py` (no disagreement), while separate recomputation found the 15 new and 22 gone postings. Claude Code handled the separate recomputation.
- **Tests and fixes:** I reviewed the diff for the duplicated paragraph, the outdated reproduction command and the five broken links before approving the changes. Claude Code implemented the fixes and ran the tests, full test suite and planted-mistake checks.
- **What is still unresolved:** I understand that the current rule treats optional experience statements like "10+ years in the industry is a plus" as requirements. What I still don't know is whether this could cause the agent to reject suitable jobs in future postings. I need to examine more real job descriptions to understand how often this happens and whether optional qualifications should be treated differently from mandatory requirements.
- **What's next for tomorrow:** Packaging the repository, ensuring the zip matches the GitHub folder exactly, and completing the final submission.

Evidence: my run and my check (`b490e1c`; MY-CHECKS.md, 4:07 PM and 4:12 PM); the fixes I approved after reading the diff (`487ab4c`, `2695e78`); the README and SOURCES I approved (`65703fe`).
