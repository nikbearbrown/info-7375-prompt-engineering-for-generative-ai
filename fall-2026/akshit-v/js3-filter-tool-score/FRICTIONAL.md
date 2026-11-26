# FRICTIONAL: Job-Search Agent 3

> **How this file was made:** Claude Code drafted the factual log in sections 1, 3 and 4 from our session (2026-11-24 to 11-25) and checked it against the commits and files it cites. Section 2's reflections are mine, in my own words. Times are ET unless marked UTC.

## 1. What I tried and what happened

- **I started past the deadline.** The assignment was due 11-23, 11:59 pm ET. I began on 11-24.
- **The gate came first.** Claude read my JS1 and JS2 folders, then ran the inherited JS1 rule over the 603 postings my JS2 agent had saved on Nov 10.
  - It kept 51, and 45 of those were on Snowflake: the skill "Snowflake" was matching the employer's name.
  - Claude proposed the filter as numbered rules, and I approved F1–F9, E1–E5 and A1–A3 as drafted.
  - I chose all four wrong versions and 80 labels. FILTER.md was committed alone (`0e4173c`, 21:33).
- **A real second day.** Copying JS2's seen-id state meant the 11-24 live run reported postings genuinely new since 11-10: 19, 24 and 68. Both earlier sign-offs had listed "a real change on the board" as not checked.
- **The second-method recompute found a gap in my spec.** It disagreed on 5 of 714 postings at first. All 5 came from punctuation inside a phrase ("data-quality", "Data & Integration"), which FILTER.md never mentions. With the literal reading it agreed on all 714. I later adopted the loose reading as rule C2 (v1.1).
- **Before labeling, I could have seen filter output.** The v1.0 ranked kept list, and one Claude reply scoring "Data Platform Engineer", appeared in collapsed tool rows in the session before I labeled. The sheet itself was blind.
- **Probing my own MCP server found two gaps.**
  - Version 1.0.0 answered a tool call sent before `initialize`. Fixed in 1.0.1; both transcripts are kept.
  - Claude Code, acting as the client, pointed out that the tool promises an offset for every matched word but gives none for role words. Not fixed.
- **The filesystem server.**
  - Its path boundaries held.
  - It writes by default and accepts arguments no tool declares.
  - A 2025-era client's Roots replaced my allowed directory (it then read `outside/secret.txt`), unless the server ran with `--confine-roots`. On Claude Code's 2026-07-28 connection that did not happen.
  - Pinning 2.2.0 did not pin its dependency, which resolved to 2.4.0.
- **My labels and my rule disagreed.**
  - I labeled 80 postings in 42 minutes. Claude then showed that 44 of my 48 `relevant` labels conflicted with the labeling rule I had adopted in JS1: Account Executives, Staff/Manager/Principal roles, 8+ years, and notes like "partial match".
  - Of three options (revise, keep, change the rule), I chose to change the rule. Claude drafted a definition from my notes and I accepted it as is (`48fc3f9`).
  - At least 18 of my 80 labels still contradict it (`labels/label_noise.md`); 3 of those were found only after the definition-prompt run.
- **Claude's flag script had its own false friend.** It flagged "no direct reports" as people management. Fixed before the flags were committed.
- **Rule changes barely moved anything.** On the 50 audit labels, C2 gave +1. C1 (cut title-level words), C3 (streaming) and C4 (orchestration) each gave +0, and I rejected them. The fitted threshold (6 → 5) moved the held-out filter agreement from 14 to 21 of 30, and I adopted it as v1.2.
- **150 Claude sessions on the held-out 30 changed nothing.** That covered the A–A repeat, an abstain option, the filter's score in context, and the tool offered. Claude said `not_relevant` to all 30, because the inherited prompt still held the old definition.
  - I asked for one more run with only the definition paragraph replaced: 14 verdicts flipped, and agreement went from 12 to 20 of 30.
- **My claim check.** I marked all 69 claims supported in about 10 minutes, mostly with the note "job role is relevant".
  - Claude showed that two of them have no quote, which E3 calls insufficient by definition, and that my notes judged the job, not the claim.
  - I chose to let E4 apply (my labels stand). As a result, A2 never fires on the shortlist.
- **Claude's own mistakes, caught and fixed.**
  - A heredoc turned `\b` into backspace characters and `"\n"` into a real line break, three times.
  - In draft documents it wrote four wrong counts: "7" reject errors in the noise list (actually 6), "9 of 12" scoring 0–3 (11), "five" boilerplate streaming matches (3), and "about 14" checker artifacts (20).
  - A2 as coded checks that a core claim is supported, not what it says. This was found while writing SHORTLIST.md and is not fixed.

## 2. What I checked, changed, or learned, and what is unresolved

**Checked:**
- **By me:** the 80 posting labels, the 69 claim labels, and every decision listed in SOURCES.md.
- **By Claude:**
  - the tests (69 pass);
  - the second-method recompute (714/714 on v1.0 and on v1.1);
  - the probes of both servers;
  - every Claude run.

**Changed:**
- FILTER.md v1.0 → v1.1 (C2) → v1.2 (threshold 5);
- the definition of relevant (labels unchanged);
- MCP server 1.0.0 → 1.0.1.

**Unresolved:**
- At least 18 labels contradict my own definition.
- The claim check did not test claims against quotes.
- A2 checks support, not fit.
- The role-word offset promise is unfixed.
- `streaming` and `orchestration` are unguarded.
- The held-out set has now been used for decisions.
- The agent's judge is still `judge_v1.md`.

**What surprised me, and what I learned (my own words):**
The most surprising aspect was where the problems occurred. I thought the filter would be the weak link and the second method recompute and the tests were mostly good. The truth is it had very little to no real skill gaps: the name of the employer as a skill and punctuation within phrases. I felt that the weak link was myself. In 42 minutes, I labeled 80 postings and in about 10, I labeled 69 claims. Both occasions Claude told me that I had been evaluating one of the other things the rule was used to evaluate: the relevance of a job, not how closely it fit my definition or I think it fit; the validity of a quote, not whether it was saying what I thought it was saying. I didn't see either time until it was pointed out to me.

One of the shocks was the extent to which the outcome was a function of the location where the criterion was written down. Four sets of experiments didn't shift anything since the definition was in a prompt I had inherited and never read. There were 14 verdicts changed in one paragraph. The note loaded was like a memory file and made Claude call a presales role to its attention, even though it had just written the word presales. I took away the understanding the criterion, and anything in the context, is the instrument. Without being able to refer to where the criterion is found in each component, I don't know what I am measuring.

I also learned about some tools that I thought were safe. The filesystem server allowed my client's version of the root to overwrite my allowed root and pinning of a version did not pin its dependency. PINNED and CONFINED were not as bad as I thought when tested.

The thing I struggle to write in part I is a pattern in my decisions. Two times I was told to redo my own work by Claude, which included editing the labels and editing the claim check. On both occasions, I selected the "Change Definition" option and then left E4 in place. All of my choices were recorded in a truthful manner, but when taken together, they tell us that the weakest link in this project was the one that I protected.

**What I would do differently next time (my own words):**
I'd be on time; the late start is a reason I rushed the two hand checks which needed the most attention. I would write the definition of relevant first, work it through on 10 postings and then make the changes later, rather than making changes to the definition when I wrote the labels. I would call it slower and then have each note indicate which portion of the definition it is placed on. I would also not use the output from the filter in the current session until I had labeled the filter, not until I had finished working on the sheet.

I would trace all objects that I was inheriting for what it is representing, before experimenting, before I started writing code. I would plan out all the runs that I had held out for and do them once and not add another run after seeing results. I would consider memory files, notes and prompts as versioned elements of the instrument, and depend on a lockfile, not a single version number. When Claude says to redo the work that I've done and I want to say, "No," I would view that same "no" as an "okay".

## 3. What I accepted, modified, or rejected from Claude

| Item | Accepted, modified, or rejected | Where |
|---|---|---|
| FILTER.md proposals F1–F9, E1–E5, A1–A3 | accepted as drafted | `0e4173c` |
| Wrong versions WV1–WV4 | accepted, all four | FILTER.md section 4 |
| The label flags (44 of 48) | heard; chose to change the rule, not the labels | `48fc3f9` |
| Revising my labels (Claude's recommended option) | **rejected** | LABELING_RULE.md dated entry |
| Claude's drafted definition of relevant | accepted as is | LABELING_RULE.md |
| Candidate rules C1, C2, C3, C4 | accepted C2; **rejected** C1, C3, C4 | FILTER.md section 7 |
| The fitted threshold | accepted (v1.2) | FILTER.md section 7 |
| Redoing the claim check (Claude's recommended option) | **rejected**; let E4 apply | SHORTLIST.md |
| Trust decisions proposed by Claude | **modified**: accepted both with additions. js3-filter: three amendments (fix the role-word offset claim, disclose that sessions are recorded, state that answers are stable only for a fixed corpus) before anyone else relies on it. Filesystem server: accepted Claude's conditions and went further: not registered with the agent at all; re-evaluate on any change to the server, its dependency tree, or the client | mcp/EVALUATION.md |
| Drafts of the documents | accepted without editing Claude's drafted text; I wrote the "My view" lines, the section 2 reflections, the two trust decisions, and the signature | git diff after `27ce26b` |

## 4. Traceability

| Commit | What it fixes in time |
|---|---|
| `0e4173c` | FILTER.md v1.0 alone, before code |
| `d6225f6` | live run, corpus, filter v1.0, tests, recompute, the sample drawn, before any label |
| `4c1ec0b`, `530de6a` | MCP server, probes, transcripts, prompts, analysis scripts written before labels |
| `e5a2c47` | shortlist checker output, before my claim check |
| `30eddc9` | my 80 labels, before any audit number |
| `48fc3f9` | the definition change, before the audit was computed |
| `b5859ce` | v1.1 and v1.2 with their measurements |
| `39052f4`, `aa3c1fb`, `5daf151` | held-out Claude runs; the v3 prompt committed before its run |
| `cab4c42` | my claim check, before comparison |
| `6c11b93`, `27ce26b` | the shortlist write-up |

- **Prompts:** `prompts/`.
- **Tests:** `tests/`.
- **Raw results:** `out/` (runs, evidence, filter, audit, shortlist, experiments, mcp).
