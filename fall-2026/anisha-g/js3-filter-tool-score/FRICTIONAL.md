# FRICTIONAL: Job-Search Agent 3
Anisha Gaikar. Times are Eastern, 2026-11-25. Claude (Claude Code on my Mac) drafted the factual entries from what happened in our session and from the logs and commits named in each entry. Entries marked **(my own words)** are mine.

## Log
**~1:58 pm: The gate.** In a claude.ai chat I made 8 choices for FILTER.md:
- analyst/analytics/BI/insights title words;
- reject seniority words;
- ≥2 skills and ≤3 years;
- my 3 JS2 boards plus Stripe and Lyft;
- a strict quote rule for evidence;
- "I cannot tell" when years are unstated or the text is missing;
- missing ≠ not relevant;
- wrong versions: substring match and rank by word count.

Claude wrote the wording. I committed FILTER.md **alone, first**: `7ee4178`, 14:02. Grading feedback on JS1 told me to gate before Claude starts, so I did the gate before any code.

**~2:04 pm: A parallel draft in the folder.** Claude Code found an **untracked** draft from 2026-11-13 in my JS3 folder: a different persona ("Riley Park"), 24 boards, filters v1–v1.4, and logs claiming runs. It also didn't match my gate, and its file dates were older than the gate. Claude moved it out of the repo intact (`~/js3-parallel-draft-nov13/`) rather than deleting it. None of it is in any commit. This is the same thing that happened in JS2 (`3ac13df`).

**~2:09 pm: Tests before code.** Claude wrote 44 tests from FILTER.md only (`340c11f`), and ran them with no code: `logs/00`, 44 errors. The two wrong versions are one-function mutations of the real filter (`wrong_versions/`).

**~2:11 pm: Code, then the live run.**
- The tests pass on the real code and catch both wrong versions: substring fails 4 tests, word-count fails 8 (`logs/02`, `42fef19`).
- The live collection got all 5 boards, 1,734 postings (`logs/10`).
- Filter v1.0 kept 11.
- I hadn't run the `js3-collect.zip` the claude.ai chat had planned; Claude Code built and ran the collector directly on my Mac instead.

**~2:12 pm: The draw before any judging.** The seed and draw script were committed with the blind sheet (`0810190`): A 30, B 10, C 6, H 30, shuffled.

**~2:14–2:17 pm: Real tool server sessions.**
- **Run 1:** Claude Code connected, sent `server/discover` first (my server: -32601), then `initialize`, `tools/list` and `tools/call`.
- **Run 3** (planted injection) showed a **real problem in my server**: Claude explained the R3 rejection as "nothing about years". The server never said what R3 means. Fixed later (14:55).
- **Other server, first attempt:** Claude's first probe script read `/etc/hosts`, and the **permission check on the session refused it**. Claude removed that probe and kept every probe inside a sandbox it created, with a decoy "outside" file.
- **Step label:** one scripted-client step label was wrong ("senior, rejected" for a kept posting). Claude fixed the label, re-ran, and deleted the mislabelled run.

**~2:20 pm: Claude experiments before my verdicts.**
- 180 `claude -p` calls (B, a B2 repeat, E1 prompt, E2 context, E3 model, E4 tool), $2.51. The plan was committed first (`f30af68`); the runs are in `4b4dffd`.
- Running them before I judged meant my labels couldn't steer how they were run.

**~2:21 pm: Filter v1.1.** Two false friends in the kept sample (C):
- "Analytics" in *Software Engineer, Data Warehouse Analytics*;
- "2 years of **university education**" read as experience.

The tests came first (`logs/04` fail, `2c8683c`), then the code (`4eddf21`).

**~2:23 pm: The bug I would have shipped.** While Claude re-read every shortlist label against the posting text, *Processing Cost Analyst* turned up: score 8, the top of the ranking, and shortlisted. But all its tools were under "Preferred qualifications". The labeller had treated the short bullet "Experience with **Oracle Suite**" as a heading (it contains "experience"), which ended the Preferred section. The fix order:
1. a regression test first (`017f3ca`, `logs/06` fails);
2. then the fix (`6551bd8`), 73/73.

The shortlist went from 9 to 8. **Unresolved:** tool transcripts and the E4 runs made before 14:23 used the buggy labeller. I kept them as recorded and said so in TOOLSERVER.md.

**~2:27–2:51 pm: My verdicts.** I judged all 76 on the blind sheet: 74 n, 2 y, each with a reason. They were frozen by hash at once (`474e2d5`).

**~2:52 pm: Slips in my reasons.** Claude noticed problems in the reasons:
- items 7/8 and 22/23 carried the reasons of neighbouring postings;
- item 65's reason was a placeholder ("Reason you could type:");
- item 12 says "X+ yrs".

Claude asked me how the verdicts were made. My answer: they're mine, and the mismatches are copy-paste slips. I re-judged those 5 in a separate file (`labels/hand_corrections.jsonl`); the originals stay frozen, and both are reported.

**3:39–3:41 pm: The re-judge.** All 5 verdicts were the same as before (5 × n), with reasons now written for the right posting. No number changed.

**~2:53 pm: What the audit showed.**
- 0 of 30 random rejects wrong (Wilson 0–11.4%), but the random sample is mostly sales and engineering jobs.
- **10 of the 11 keeps were "n" for me**, for reasons the filter can't see: location, internship graduation windows, FP&A finance roles, "exclusive of internships".
- The filter measures "looks like an analyst job with her skills", not "worth her time".

**~2:55 pm: My server fixed after evaluating it as a stranger's.**
- Its description said it "does not… store anything", but it writes every message to a transcript.
- It returned rule codes without meanings.
- Fixed in `d6a5279`.
- The same injection prompt then got a correct R3 explanation 3/3 (`df3d67f`). That's 1 run before and 3 after, so I call it an anecdote.

**~2:57 pm: My rule decisions.** Claude measured candidates on the whole corpus:
- US-only drops 5 of the 10 v1.1 keeps;
- an FP&A exclusion drops 2;
- "specialist" adds 1 keep out of 52 such titles.

I accepted both v1.1 rules, chose **R5 US-only** for v1.2, and **rejected** FP&A and "specialist" (FILTER.md §5). Tests came first (`7c66429`), then code (`7658ac6`), 78/78.

**~3:00 pm: The held-out result I can't use as proof.**
- H has **one** "y" in 30, so "always say no" scores 96.7% and ties the best scorer.
- No change can be called an accuracy improvement.
- What I can say is item-level: R5 removed 3 false keeps; the prompt and context changes each lost the one true keep.
- **Unresolved:** H should have been stratified for more likely positives. I drew it before I knew how rare "y" would be.

**~3:02 pm: Independent check.** `tools/check.py` doesn't import my code. It recounted the corpus, boards and R1/R2, and checked the sets and the verdict hash: 9/9 PASS (`logs/41`).

## What I accepted, modified or rejected from Claude
| Claude's suggestion | What I did |
|---|---|
| The FILTER.md wording and score numbers | **Accepted** (my choices, Claude's wording) |
| The v1.1 rules (engineer titles, education years) | **Accepted** |
| R5 US-only | **Accepted** |
| An FP&A exclusion | **Rejected**: one family of titles; I'd rather record it as a known weakness |
| Adding "specialist" | **Rejected**: 1 keep from 52 titles |
| Fixing case-sensitive Excel and "(2) years" now | **Rejected for now**: found on held-out items, so fixing them would contaminate H |
| (I asked Claude to judge the 76 for me) | Claude declined, because the assignment requires my own judgment; I judged all 76 myself |
| Copy-paste slips in 5 reasons | **Modified**: re-judged in a separate file; originals kept |

## (my own words)
*What I learned, what surprised me, what's still unresolved for me:*

I learned that a filter can match the words in a posting without knowing whether the job fits the person: 10 of the 11 postings my filter kept were "no" for Nadia, mostly because of things it doesn't check, like graduation windows, location, and "excluding internships." What surprised me was how many "Analyst" titles turned out to be tax, credit, or accounting roles, and how often the requirement that decided a job was hidden until I opened the full text. What's still unresolved is whether my labels are a truly independent answer key, since another Claude chat helped me word the reasons for most of them (every y/n decision was mine), and whether any filter change really helped when the held-out set had only one "yes."
