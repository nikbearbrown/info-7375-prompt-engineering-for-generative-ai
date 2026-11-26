# JS3 — The Filter, the Tool, and the Score (Siddi Kommuri)

This layer decides which collected postings reach the fictional job seeker Jordan Lee, and why. It has three parts:
- a filter written as a document first ([FILTER.md](FILTER.md));
- one capability offered to Claude through a Model Context Protocol tool server written from scratch;
- a score whose every number has a recorded origin.

**Started from my own JS1 and JS2.**
- JS1 gives the Jordan Lee persona, the title, seniority and years rules, the skill vocab, and the Claude judge prompt, which is copied byte-for-byte.
- JS2 gives the three boards, Stripe (Greenhouse), Notion (Ashby) and Canva (SmartRecruiters), and its allow-listed, no-redirect fetch.
- From the instructor's Lectern I took only the *idea* of a filter file that logs every word added, cut or rejected, not its code ([SOURCES.md](SOURCES.md)).

## Language, toolchain, commands

- **Python 3.13.2**, standard library only. Windows 11, Git Bash.
- **Claude Code CLI 2.1.325** (logged in), found through `CLAUDE_BIN` or `PATH`. Every call runs in a new empty temp directory with built-in tools off (`js3/claude_cli.py`).
- **Network:** only `boards-api.greenhouse.io`, `api.ashbyhq.com` and `api.smartrecruiters.com`, GET only (`js3/policy.py`).

```bash
python -m js3 collect                                                    # collect the 3 boards with text (30-request budget)
python -m js3 filter --run 2026-11-26T02-59-56Z --config config/filter.v1.json     # filter v1 as run (v1.1: config/filter.v1.1.json)
python -m unittest discover -s tests -v                                  # 23 tests, no network, no Claude
python tests/mutants.py                                                  # each wrong version put in; its test must fail (7/7)
python -m js3.mcp_server --transcript evidence/mcp/my-session.jsonl      # the tool server on stdio
python tools/probe_server.py --name mine --tool score_posting --good-args '{"board":"stripe","posting_id":"8415333"}' --log evidence/mcp/probe.jsonl -- python -m js3.mcp_server
python tools/mcp_session.py                                              # a real Claude CLI session against the server (needs CLAUDE_BIN)
python tools/other_server_session.py                                     # the same against the course's Ch 8 server (needs the course repo's git history)
python tools/shortlist_claims.py --run 2026-11-26T02-59-56Z              # claims + labels for the shortlist (Claude)
python tools/experiments.py run && python tools/experiments.py score     # Step 2.4 variants on held-out H (run needs Claude)
python tools/audit_report.py && python tools/fit_threshold.py            # audit against Siddi's labels; the fitted number
```

## What ran (2026-11-25 ET; run ids are UTC)

| ET | What | Evidence |
|---|---|---|
| 21:59 | **FILTER.md v1** committed before any filter code. Claude drafted it; Siddi settled the three open questions and approved the rest. | `4e62099c` |
| 22:00 | **Live collection** `2026-11-26T02-59-56Z`: 975 postings. Stripe 772, Notion 174, Canva 29 (27 with text; 2 had no text because the 30-request budget ran out, so the run ended `budget-exhausted`). | `40f9ea3e`, `data/collections/` |
| 22:03 | **Filter v1:** keep 8, reject 967, cannot tell 0 | `2ffbb8f9` |
| 22:05 | Blind labeling sheet: 62 postings, selection frozen by seed | `e958bc43` |
| 22:07 | **Tool server** and a real Claude CLI session. The client probed `server/discover` (2026-07-28), got `-32000`, then used `initialize` 2025-11-25. | `f4fa7aa1`, [TOOL-SERVER.md](TOOL-SERVER.md) |
| 22:09 | Tests for wrong versions 1–5 and the server's declarations; 7/7 mutants caught | `793313ae` |
| 22:12 | **Source-grounded shortlist:** 8 postings, 54 claims, each labelled | `3383e5c5`, [SHORTLIST.md](SHORTLIST.md) |
| 22:15 | Held-out set H, candidate filters, and the **experiment plan, committed before scoring** | `77827f07` |
| 22:18 | Both servers probed with the same 14 messages. Course-server session `03-17-39Z` failed (bug in my tap); `03-18-29Z` worked. | `eb13b533` |
| 22:21 | 150 Claude calls, variants B/P/C/T/S, **before Siddi's new labels existed** | `6dcc3edd` |
| 22:25 | **Siddi's 62 blind labels** read from the page and committed before any comparison | `4d633be9` |
| 22:30 | Audit, scores, fitted threshold. Siddi kept the labels as-is, adopted v1.1 and rejected v1.2. | `f0e755a1` |

## Deliverables

| The brief asks for | Where |
|---|---|
| FILTER.md: filter, evidence rules, sources, wrong versions, versioned | [FILTER.md](FILTER.md) (v1 + v1.1; log in §E) |
| Reject audit with hand verdicts, what a sample can say, false friend, rule log | [AUDIT.md](AUDIT.md), [output/audit/AUDIT-TABLES.md](output/audit/AUDIT-TABLES.md), [labels/](labels/) |
| Source-grounded shortlist and its labels | [SHORTLIST.md](SHORTLIST.md), [output/shortlist/SHORTLIST-CLAIMS.md](output/shortlist/SHORTLIST-CLAIMS.md) |
| Tool server, transcripts, both evaluations | [js3/mcp_server.py](js3/mcp_server.py), [TOOL-SERVER.md](TOOL-SERVER.md), `evidence/mcp/`, `evidence/other-server/` |
| One change at a time on held-out labels; origin of every number; persistence | [WHAT-MOVES-THE-SCORE.md](WHAT-MOVES-THE-SCORE.md), [experiments/PLAN.md](experiments/PLAN.md) |
| Code and tests | `js3/`, `tools/`, `tests/`, `evidence/tests/` |
| Sign-off and driver's seat | below |
| SOURCES, FRICTIONAL | [SOURCES.md](SOURCES.md), [FRICTIONAL.md](FRICTIONAL.md) |

## Results in one paragraph

- **The filter does what FILTER.md says:** 23 tests, and 7 of 7 wrong versions caught.
- **FILTER.md and Siddi's labels today don't agree.** Of 30 random rejects, Siddi labelled 18 relevant (exact 95% interval 41–77%). 12 of those 18 are outside the US or have an excluded title, which the written rules rule out on purpose.
- **Measuring every location found a real bug:** 111 postings with bare US city names were read as foreign. Fixed in v1.1, which took held-out agreement from 15 to 17 of 29.
- **The false friend is "ai",** from Notion's company blurb.
- **The shortlist showed relevance without entailment,** and an abstention rule that checks support but not meaning.
- **Five one-at-a-time Claude changes moved no verdict on H.** The context and tool changes moved only the reasons.

## Sign-off — Job-Search Agent 3

> Lines drafted by Claude. Siddi reviewed them and chose to sign them as they stand (2026-11-25, about 22:43 ET).

```text
Sign-off — Job-Search Agent 3
Checked:      FILTER.md wrong versions 1-5, each by its own test (tests/test_filter.py WV1-WV5) and each
              caught when put into the code (tests/mutants.py, 7/7 including two server lies);
              what my server declares vs does (tests/test_mcp_server.py; probe P1-P14 on both servers);
              filter v1 and v1.1 against my 62 blind labels (AUDIT.md; H in WHAT-MOVES-THE-SCORE.md);
              every shortlist quote is verbatim in its posting (js3/evidence.py quote_check: 47 found, 7 empty);
              the saved labels equal the page (byte length and all 62 labels compared).
How:          by hand: the 62 blind labels, my FILTER.md answers, keeping the labels, adopting v1.1,
              rejecting v1.2, the two trust decisions.
              by recomputation: the audit intervals (exact Clopper-Pearson, checked against 0/30 -> 11.6%);
              the held-out scores recomputed from saved Claude output.
              with Claude's help: all code, tests, mutants, probes and reports were written by Claude;
              none was written by me before reading Claude's code. The claim labels are a second Claude call.
Not checked:  1. The 54 shortlist claim labels by hand.
              2. Whether my labels follow one standard: 25 of 39 "relevant" conflict with LABELING.md, and one
                 posting got opposite labels on Oct 31 and Nov 25.
              3. A live timeout, 404 or pagination during this collection (only the budget stop happened).
              4. MCP 2026-07-28, or any client other than Claude Code 2.1.325.
              5. Borderline postings for the Claude variants: H had almost none.
Not claiming: that the filter finds the jobs I want (by my labels it wrongly rejects 41-77% of a sample);
              that the agent's "relevant" is reliable (the abstention rule checks support, not meaning);
              that annotations or a server's name prove it is safe;
              that a change which moved no verdict on H has no effect.
Signed or withheld: Signed, Siddi Kommuri, 2026-11-25
```

## Driver's seat

| Part | Claude should | Siddi should | Why it stays Siddi's | Evidence |
|---|---|---|---|---|
| The filter's rules | Draft from Siddi's earlier decisions; flag open questions; implement literally; measure | Settle the open questions, approve, and adopt or reject each measured change | The rules encode what Siddi wants. A measured improvement is still a choice of what to want. | `4e62099c`; FILTER.md §E |
| What counts as relevant | Build a blind sheet; show no verdicts; save labels byte-for-byte; report conflicts without changing labels | Label every posting; decide which standard is real | If Claude labelled, the filter would be graded by its own side. | `labels/`, `labels/DECISION.md` |
| Shortlist claims | Write claims with quotes; label them in a separate call; check quotes mechanically | Decide whether the answer is worth acting on | Supported claims are not worth: the Security Engineer's claims were all supported, and Siddi says not relevant. | SHORTLIST.md |
| The tool server | Write it; test what it declares against what it does; keep transcripts | Make the trust decision | Compatibility is not permission. Whoever lets it run unattended answers for it. | TOOL-SERVER.md |
| The experiments | Pre-register; run; report results that change nothing as results | Decide adoption | A change is a decision about the agent Siddi uses, not a statistic. | `77827f07`, `f0e755a1` |

**Why the judgment that a posting is worth Siddi's time stays Siddi's:**
- The agent can show that a posting matches words and that its claims are in the text. It cannot know which standard Siddi actually holds.
- This assignment proved the point. Siddi's blind labels today accept roles that Siddi's own written rule excludes, and only Siddi can say which of the two is right.
- The cost of a wrong "worth your time" falls on Siddi's time, not on the agent.
