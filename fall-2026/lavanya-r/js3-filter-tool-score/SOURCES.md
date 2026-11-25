# SOURCES — Job-Search Agent 3

## What I built on

| Source | What I used | Checked |
|---|---|---|
| My JS2 folder, `../js2-loop-tools-diff` (submitted at `a76fc07`) | `agent/`, `tests/`, `check.py`, `config/`, `persona/`, `prompts/`, `state/` and `GATE.md`, copied unchanged (`6f14d20`). The loop collected the JS3 corpus. | 99 JS2 tests pass in this folder; `check.py` 9/9 on the corpus run |
| My JS1 rule, `agent/rule.py` (inside the JS2 copy) | the whole-word matcher, the seniority/role/skill word lists and the sponsorship phrases that FILTER.md starts from | `tests/test_filter.py` |
| Instructor's collector, Lectern (`fall-2026/nik-bear-brown/lectern/sources.json`) | via JS2: the Ashby endpoint pattern. Not its filter or code. | live, 2026-11-24 |
| Greenhouse, Lever and Ashby public job-board APIs | the posting fields named in FILTER.md §3. The Greenhouse `?content=true` parameter is from Claude's knowledge, checked live. | live collection 2, 2026-11-24 |
| Anthropic's Claude Code 2.1.312 (`claude mcp serve`) | the "other" tool server I evaluated (TOOLSERVER.md §3) | probed 2026-11-24, transcripts `03`, `04` |
| Model Context Protocol message shapes (initialize, tools/list, tools/call; error codes; tool annotations) | from Claude's knowledge of the published spec; my server and client were written from scratch | against a real client (Claude Code) and a real server (`claude mcp serve`) |
| Wilson score interval | the formula, from Claude's knowledge | computed in AUDIT.md §2 |
| Course brief `assignments/assignment-js3-the-filter-the-tool-and-the-score.md` | the requirements | — |

The Reallocation Engine was not used. Classmates' JS3 folders were not read.

## What Claude contributed

**Tools:**
- **Claude Code 2.1.312**, model Claude Opus 5.5 (`claude-opus-5-5`), in one desktop session on 2026-11-24, on my NEU login.
- **Claude as a component** (through `claude -p`, saved verbatim with times):
  - 105 scoring calls (`score/runs/`), `claude-sonnet-5-5` and `claude-haiku-5-5`;
  - 10 claim-labelling calls (`out/shortlist/`), `claude-sonnet-5-5`;
  - 1 Claude Code session as an MCP client (`transcripts/02`).

| Part | Claude | Me |
|---|---|---|
| FILTER.md | corpus counts and real example titles; the hard-reject/score/threshold structure; 2–3 options for every rule and every reason; sections 2–4 (evidence rules, sources, wrong versions) | chose every rule and every reason from the options, one rule at a time; accepted sections 2–4; added W6 |
| Hand verdicts | the sampling plan, the seed, the blind sheet, and one-line summaries of each posting's requirement lines | all 71 verdicts |
| The audit | the comparison, the intervals, finding the ", CA" false friend, variants X1–X4 and a recommendation on each | the decisions on X1–X4 (I followed Claude's recommendations) |
| Shortlist | claims built from the filter's matches, the labelling prompt, the quote checker; found its own checker's prefix bug and the Databricks-footer false friend | checked 3 labels (agreed with 2, disagreed with 1); decided to record the footer and not fix it in v1.1 |
| Tool server | the server, tap, client and tests (built by a Claude Code subagent); both evaluations and the probes | both trust decisions |
| What moves the score | the prompts, the context summary, the five experiments, the report | — |
| All code and tests | wrote all of it, including the tests that came before the code | — |
| Documents | first drafts of every document | read, correct, and sign or withhold |

## What I accepted, modified or rejected from Claude

- **Accepted:** every FILTER.md rule (one of Claude's options in each case), sections 2–4 as drafted, and the recommendations on X1–X4 and the footer.
- **Modified:**
  - added W6 ("Sales" as a reject word) to the wrong versions;
  - dropped JS1's "Sales" from R2;
  - added "Head of" to R1.
- **Rejected:** Claude's "insufficient" label on "The role uses Unity Catalog" (SHORTLIST.md §4). My view is that it's supported; Claude's label follows my written rule, and I left the disagreement on record.
- **Also rejected:** the optional extras offered along the way:
  - making the tool server read the newest saved run (I chose to leave it as is);
  - labelling the last 9 held-out postings.
