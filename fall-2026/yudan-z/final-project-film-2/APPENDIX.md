# Appendix — *A Job Agent I Can Check*

## Executive summary

This appendix holds the detail behind the film, as the brief asks: the data, the method step by step, the resources, the evaluation plan, and the source of every claim the film makes.
- **The project:** a job-search agent that reads public job boards every day, finds new postings, and judges each one with a written rule I can recompute by hand.
- **Built so far:** Job-Search Agents 1 and 2.
- **Still to come:** the layers in Job-Search Agents 3–5, and then the final project on 2026-12-20.

- **Student:** Yudan Zhou (`@yudanzhou`), INFO 7375, Fall 2026
- **Film:** `job-search-agent-film.mp4`, 3:49, 1920×1080
- **Narration:** a synthetic voice (Kokoro `af_heart`, run locally) reading my own script. The film says so in its first ten seconds.

## A. Data

| Source | What it gives | Access |
|---|---|---|
| Greenhouse Job Board API (`boards-api.greenhouse.io`) | Pinterest, Databricks | public, no key, read-only |
| Ashby Posting API (`api.ashbyhq.com`) | Ramp | public, no key, read-only |
| Lever Postings API (`api.lever.co`) | Palantir | public, no key, read-only |
| `persona/resume.json` | the person being matched | **fictional** persona (`@example.com`, `555`); my real résumé never leaves my laptop |

The second real run, on 2026-11-10, read 1,566 listed postings from the four boards. One board name (`no-such-board-js2`) does not exist and is kept on purpose, so that a failure is tested on every run.

## B. Method, step by step

1. **Contract before code** (JS1, `CONTRACT.md`). Nine checks, R1–R9, each naming the résumé field and the posting field it compares:
   - title family, not senior, work country, stated experience;
   - **no citizenship or clearance requirement (R5), sponsorship not ruled out (R6)**;
   - degree, skills, graduation window.

   Every answer is labelled either `record` (my rule, recomputable) or `model judgment` (Claude, checked by a strict validator).
2. **Watch** (JS1). The agent remembers every posting id it has seen and reports only new ones. The first run on a board is a baseline.
3. **Bounded loop** (JS2, `GATE.md` written before the code):
   - over 3 applicant tracking systems;
   - budgets of 6 boards, 12 requests and 120 seconds;
   - four exits: `finished`, `error`, `incomplete`, `budget-exhausted`;
   - one retry, for temporary errors only.
4. **Permission policy in code** (JS2, `agent/policy.py`).
   - The agent can send `GET` requests over HTTPS to three allow-listed hosts.
   - It writes only inside `runs/`.
   - Resetting state or replacing evidence needs my approval key.
   - There is no tool to apply, email, message or log in.
   - 19 boundary cases were predicted, then tested.
5. **Change through reviewed diffs** (JS2, `REVIEW-PACKET.md`). Every change follows the same order:
   - reproduce the defect;
   - write my predicted answers as tests;
   - let a separate Claude Code session write the patch;
   - read the diff as a change in behaviour on real data;
   - decide whether to accept, revise or reject.
6. **Next layers**, one assignment each. I know only their titles today, so the details are future work:
   - JS3, "The Filter, the Tool, and the Score" (11-25);
   - JS4, "The Plan, the Evidence, and the Memory" (12-01);
   - JS5, "The Gate, the Register, and the Supervised Run" (12-13);
   - the final project (12-20), tested on postings I label by hand across all three systems.

## C. Resources: do I have what I need?

| Need | Status |
|---|---|
| Compute | my laptop (Windows 11); one run takes about 3 seconds |
| Language and libraries | Python 3.14, standard library only; nothing to install |
| Data access | public APIs with no key and no account |
| Model | a Claude account, through Claude Code CLI 2.1.314, for the model judge and for code review |
| Token credits | covered by that account. The agent's daily loop uses the rule only and makes no model call |

## D. Evaluation

**Already measured:**

| Check | Result | Evidence |
|---|---|---|
| Tests written before the code | 87 pass | JS2 `README.md`; commit order `ff7a40c` → `14909bd` |
| A board that does not exist | HTTP 404, not retried; run `incomplete` (exit 3), never "0 new" | JS2 `runs/live/terminal-run1.txt`, `terminal-run2.txt` |
| Finished but wrong | Ramp read on Greenhouse: `finished`, 1 posting. The independent check (`check/crosscheck.py`, which imports nothing from the agent) found 176 on Ashby and flagged it | JS2 `FINISHED-WRONG.md` |
| Rule defect on real data | R3 rejected 364 of 1,561 US postings that spell the state in full. After the reviewed fix: 364 fail → pass, 0 pass → fail | JS2 `review/01`, `review/12` |
| Second real day | 34 new postings, all `not_relevant` for the persona | JS2 `runs/live/run-20261110T234346Z.md` |

**What will tell me it worked** (my criteria, stated in the film):
- every failure is reported;
- no posting I labelled relevant is missed;
- it does better than a lazy rule.

**What will tell me it did not work:**
- a failure shows up as zero;
- a relevant job goes missing;
- a lazy rule, marking everything relevant or marking nothing, does just as well.

The lazy-rule comparison is there because "no relevant posting missed" alone can be met by marking everything relevant. A criterion that cannot fail is not a criterion.

**A known limit found while checking the film (2026-11-23).** R6 matches a fixed list of phrases. Claude ran four test sentences through the JS2 rule, and I re-ran the same command in my own PowerShell with the same result (`evidence/2026-11-23_r6-four-phrasings_yudan-ran.txt`):
- caught: "will not sponsor", "without sponsorship";
- missed: "do not provide visa sponsorship", "sponsorship is not offered".

A posting written the second way passes R6 although it rules sponsorship out. That is the worst kind of miss for an F-1 student. The verdict names whichever phrase it found, so the miss is visible when the evidence says `none`, but the list is not complete. Widening it is filter work, planned for Job-Search Agent 3.

**Not yet checked:**
- the part that reports a relevant match has run only in tests, because no real relevant posting has appeared yet;
- no hand-labelled test set exists yet across all three systems.

## E. What others have done

| Who | What it does | Source (read 2026-11-23) |
|---|---|---|
| LinkedIn job alerts | sends new postings that match a saved search, daily or weekly, by email or in the app | [LinkedIn Help: Job alerts](https://www.linkedin.com/help/linkedin/answer/a511279) |
| Jobright | compares a résumé with a job; reports skills, seniority, industry experience and keyword gaps; the weighting is not published; calls its Match Score "a decision aid" and not a guarantee | [AI Job Match](https://jobright.ai/ai-job-match), [Resume Job Matcher](https://jobright.ai/tools/resume-job-matcher) |
| Visa filing databases (h1bdata.info, USCIS H-1B Employer Data Hub) | a company's past filings, by employer and year, not today's openings | my Pitch Film screenshots, 2026-10-13 |

**The gap I am working on:** checkability. A verdict I can recompute by hand, and a failure that is never reported as zero.

## F. Fact-check of the narration

Every spoken claim was checked against a file or a page before rendering. Two review passes by a second, separate Claude session changed the script (each change is logged in `FRICTIONAL.md`):
- they removed an unsupported "score from 0 to 100" for Jobright;
- they made the sponsorship checks visible;
- they turned down a comparison with a renamed product (F1 Hire, now FrogHire) whose contrast described my earlier project;
- they added the lazy-rule baselines.

The full table, with each claim's verdict and source, is `FACTCHECK.md`.

## G. How the film was made

- `beat_sheet.json`: the narration and picture plan for 15 beats, with the measured audio durations.
- `scene_body.py`: the 13 drawn scenes (Manim).
- `build/`: my outro component and the Windows `npx` wrapper.
- `FACTCHECK.md`, `SHOTLIST.md`, `SOURCES.md`: the toolkit's paperwork, written before rendering.

Toolkit: brutalist.art (show-tell skill) at `519fcbb`, Manim 0.20.1, Remotion, and the Kokoro-82M voice, all run locally. No image, video or voice generation service was used.

**Who did what:**
- **Me:** chose the topic and the plan version tied to the course schedule, ran the review session, passed findings between the two sessions and made the final call on each suggestion, and approved every narration sentence, including the evaluation criteria.
- **Claude Code:** drafted the script from my JS1/JS2 files, the scenes, and this appendix.
