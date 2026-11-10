# SOURCES — Job-Search Agent 2

## What I built on

| Source | What I used | Checked |
|---|---|---|
| My JS1 folder, `../js1-contract-and-watch` (submitted at `818e00f`) | `agent/`, `tests/`, `persona/`, `prompts/`, copied unchanged (`7e1bacb`); JS1's saved Databricks memory (imported into `state/greenhouse-databricks.json`); a real saved Claude reply and a real saved board response for the reproduction and the demo | `diff -r` of `agent/` was empty at copy time |
| Instructor's collector, Lectern: `fall-2026/nik-bear-brown/lectern/sources.json` | the Ashby endpoint pattern `https://api.ashbyhq.com/posting-api/job-board/{slug}` (Lectern lists Greenhouse, Ashby and SmartRecruiters, **not Lever**) | live: one GET per board on 2026-11-09 (probe) and 2026-11-10 (live run 1) |
| Lever's public postings API | `https://api.lever.co/v0/postings/{slug}?mode=json`: from Claude's own knowledge, not from a document I read | live probe 2026-11-09 (`palantir` 200, `plaid` 404) and live run 1 |
| Greenhouse Job Board API (public) | `GET /v1/boards/{board}/jobs` | live, 2026-11-10 |
| My JS1 grading feedback (99/100, read 2026-11-09) | its three asks: rules in my own words, "fit" labels, the `.0` fix | GATE.md "In my own words"; REVIEW-PACKET.md; "fit" labels **not done** (sign-off, Not checked 2) |
| Course brief `assignments/assignment-js2-the-loop-the-tools-and-the-diff.md` | the requirements | — |

The Reallocation Engine was not used.

## What Claude contributed

**Tool:** Claude Code 2.1.312, model Claude Opus 5.5 (`claude-opus-5-5`), in one desktop session on 2026-11-09 and 2026-11-10, on my NEU login. JS2 itself makes **no** Claude calls. The only Claude replies used as data are JS1's saved ones, from 2026-10-30.

| Part | Claude | Me |
|---|---|---|
| GATE.md | headings, the facts block, every option and its reason text; pointed out 3 conflicts in my first picks; proposed the defaults I accepted | picked every rule; changed 3 picks after the conflicts; wrote the two "In my own words" paragraphs (Claude fixed only grammar) |
| PREDICTIONS.md | listed the 14 inputs; wrote the "Why" column; flagged 4 picks that disagreed with GATE.md | picked every outcome; changed 3, kept case 3 |
| All code and tests | wrote all of it: policy, net, providers, loop, check, the import, 51 new tests | — |
| The `.0` review | reproduced it, chose the expected values (after I delegated), wrote patch 7044eaf, found its regression by reading the diff, wrote the reviewer tests and revision 54b5602, and recommended the decisions | chose this as the change (2026-11-09); handed the remaining decisions to Claude (2026-11-10); approve by signing |
| Runs | ran live run 1, the seeded demo and every logged command | see README, "Commands I ran myself" |
| Documents | first drafts of README, TRACE, REVIEW-PACKET, SOURCES, FRICTIONAL | read, correct and sign |

**What I accepted, modified or rejected from Claude:**
- **Modified:** three of my own first GATE picks, each one an option Claude had offered (retry a 404 three times; hosts "ending in"; 0 jobs = "no new jobs"). I changed them after Claude pointed out that they conflicted.
- **Accepted:** the defaults marked in GATE.md; the review decisions.
- **Claude rejected its own first patch:** it revised `7044eaf` after reading the diff.
