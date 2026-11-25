# COMMIT_MAP

The JS3 work was built in a local repository and copied onto this branch on Nov 25, 2026 with `git cherry-pick -x`. Cherry-picking gives every commit a new hash but keeps its original author date and its content; the folder on this branch is identical to the local one. The documents in this folder (FILTER, FRICTIONAL, SOURCES, SIGNOFF, README, score/, shortlist/, mcp/) cite the **local** hashes. This table maps each one to its commit on this branch, and every commit message on this branch ends with `(cherry picked from commit <local hash>)`.

| Local hash (cited in docs) | This branch | Date | Commit |
|---|---|---|---|
| `0041401` | `a4eacba` | 2026-11-23 | JS3: FILTER.md v1.0 (gates, score, evidence rules, expected sources, wrong versions) before any filter code |
| `b19d5ad` | `4cb2c45` | 2026-11-23 | JS3: Nov 23 collection with posting text, postings loader, seeded 90-posting label sample (unlabeled), FRICTIONAL and SOURCES drafts |
| `0e6ab22` | `a3284ec` | 2026-11-23 | JS3: FRICTIONAL cites the Day 1 commits |
| `c674a91` | `426ced7` | 2026-11-23 | JS3: FRICTIONAL Nov 23 — my account of accepting FILTER.md v1.0 and what stays unmeasured |
| `215f29a` | `6137a2d` | 2026-11-23 | JS3: hand labels for all 90 sampled postings (dev 45: 6 keep; held-out 45: 5 keep), before any filter code |
| `5b192f5` | `0032042` | 2026-11-23 | JS3: FILTER.md v1.1 documentation correction (SWE II asks 1.5+ years, not 5+; no rule changed) and FRICTIONAL entry for labels and the survey error |
| `6cd481c` | `31cbcc8` | 2026-11-23 | JS3: FRICTIONAL cites the v1.1 correction commit |
| `292db34` | `8208a67` | 2026-11-23 | JS3: FRICTIONAL Day 1 and labeling entries rewritten in my words (Claude's actions named, check counts corrected) |
| `3beb6f0` | `1d05d5e` | 2026-11-24 | JS3: tests for the filter, written before agent/filter.py (decimal years, gates, W1-W5, threshold) |
| `342075a` | `518e805` | 2026-11-24 | JS3: agent/filter.py implementing FILTER.md v1.1 (v1.0 rules), wrong-version checker, v1.0 run on 400 (kept 22), unjudged audit sheets |
| `c87c9b6` | `2439e93` | 2026-11-24 | JS3: my hand judgments for the 30 random rejects (filter v1.0): 0 of 30 should have been kept |
| `cd6bfe8` | `21991bc` | 2026-11-24 | JS3: my judgments for the 22 kept and 9 close calls (filter v1.0): 11 of 22 kept should be kept; 1 close-call reject should be kept |
| `6dc9c6a` | `c85adaa` | 2026-11-24 | JS3: FILTER.md v1.2 — R2 scores N >= 3 years at -0.40 (was 0 at N = 3) |
| `bdf8998` | `c8ce1c5` | 2026-11-24 | JS3: held-out run once for v1.0 and v1.2: fp 5 -> 4, tp 5, fn 0 (dev had fixed 6) |
| `f89aef7` | `37b4137` | 2026-11-24 | JS3: shortlist tests, written before agent/shortlist.py (verbatim quotes, labels, relevance vs entailment, abstention) |
| `88c3a94` | `81b5a53` | 2026-11-24 | JS3: source-grounded shortlist from v1.2 (10 ranked, 1 cannot tell, 4 contradicted), relevance vs entailment and abstention counterexample |
| `8458710` | `9641a67` | 2026-11-24 | JS3: MCP server tests, written before agent/mcp_server.py |
| `830966a` | `e79ec66` | 2026-11-24 | JS3: MCP tool server from scratch (stdio JSON-RPC, 4 read-only tools, call log confined to out/) and a scripted raw transcript |
| `3ee665a` | `7e25567` | 2026-11-24 | JS3: real Claude Code transcript against the MCP server (Nov 24, 06:03Z), server log, server runs from any directory |
| `58fba29` | `31ef65f` | 2026-11-24 | JS3: MCP server evaluations: mine (run, probed) and the official Filesystem server (read from source, not run) |
| `e273c8e` | `7c3de8e` | 2026-11-24 | JS3: MCP server checks arguments against each tool's schema; an unknown board is 'did not search', not 0 results |
| `d1f5940` | `68b6f5c` | 2026-11-24 | JS3: EVALUATIONS and FRICTIONAL record the schema fix |
| `2f40542` | `d34cf72` | 2026-11-24 | JS3 Day 3 drafts: score/origins.md, score/report.md, score/recount.py, PERSISTENCE.md, SIGNOFF.md (unsigned), README.md; FILTER.md v1.3 corrects the duplicates count (173 share, 91 extra copies) |
| `703ba85` | `a78ff33` | 2026-11-24 | JS3: README records the fresh-clone check at 2f40542 |
| `c92caaa` | `b399d17` | 2026-11-24 | JS3: Quant Analyst close call corrected to reject with my reason (first recorded keep by misclick); README false friend in my words |
| `f7a000b` | `ee93c42` | 2026-11-24 | JS3: false friend wording matches the code (R1 has no end word boundary; the score is computed, G1 blocks the keep) |
| `3e03662` | `a925011` | 2026-11-24 | JS3: FRICTIONAL entries rewritten in my words, with fact fixes (22 not 23, &amp;, v1.2 tests committed with the rule, exactly 3 years, sample-estimate wording) and all reference commits |
| `8969b7d` | `ff8c14a` | 2026-11-24 | JS3: FRICTIONAL Nov 24 entries revised in my words (hashes inline, 3-year wording, miscount noted, both abstention reasons) |
| `9fd151f` | `6d26d4d` | 2026-11-24 | JS3: FRICTIONAL evaluations and Day 3 entries revised in my words (hashes inline) |
| `17f1a98` | `f6dbaa7` | 2026-11-24 | JS3: shortlist/CASES.md in my words (quotes checked as verbatim substrings) |
| `076308d` | `6a3152e` | 2026-11-24 | JS3: mcp/EVALUATIONS.md in my words |
| `f8e000b` | `9846a14` | 2026-11-24 | JS3: score/report.md in my words |
| `912ad9f` | `d6993d1` | 2026-11-24 | JS3: PERSISTENCE.md in my words |
| `68e221f` | `d59d863` | 2026-11-24 | JS3: README top half in my words (through Commands); MCP server, claude mcp add and live loop restored as separate blocks |
| `4d0c744` | `ac5a5a5` | 2026-11-24 | JS3: README fully in my words |
| `4a947b6` | `56017d4` | 2026-11-24 | JS3: SOURCES.md in my words |
| `ad0a87e` | `d4dda58` | 2026-11-24 | JS3: SIGNOFF.md signed (Atharva C., 2026-11-24) |
| `4387c98` | `66c7e47` | 2026-11-24 | JS3: FRICTIONAL provenance line and 'In my own words' reflection (accepted / modified / rejected / unresolved) |
| `0fcd674` | `5f3b76a` | 2026-11-24 | JS3: Wilson interval printed by score/recount.py; FILTER.md records the two rules rejected after measuring; local paths removed from the client config (noted in the file) |
| `51b9e41` | `f4ea945` | 2026-11-24 | JS3: EVALUATIONS section 4 — declared vs actual, what a client is not entitled to, and my trust decisions for both servers |
| `9a30e25` | `a192ce0` | 2026-11-25 | JS3: SIGNOFF 'How each item was checked' in my words (four categories, tests named, Claude wrote all tests); re-signed 2026-11-25 |
| `0ec6c64` | `2c262f9` | 2026-11-25 | JS3: SOURCES Nov 24-25 row and signed status; fresh-clone re-run at 9a30e25 cited in README and SIGNOFF; SIGNOFF clarifies the 23 'Engineer II' titles |
| `9b9dba8` | `f84b778` | 2026-11-25 | JS3: FRICTIONAL Nov 25 entry (assignment and TA cross-check, fixes, final fresh-clone check, unresolved push); provenance line says it was drafted by Claude and reviewed by me |

**One hash from JS2.** `SOURCES.md` cites `80e4fa1`, the JS2 React/Go skill-match fix that `agent/skills.py` was copied from. It is a JS2 commit, not a JS3 one; on my JS2 branch (`atharva-js2-loop-tools-diff`) it is `3fe8a7d`, as listed in `../js2-loop-tools-diff/COMMIT_MAP.md` on that branch.
