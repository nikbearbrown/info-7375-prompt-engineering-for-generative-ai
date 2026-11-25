# SOURCES: who wrote what, and where facts came from

Claude Code (Claude Opus 5.5, in the Claude Code desktop app) drafted this file on 2026-11-24 from the commit record and the student's answers. The student gave those answers in chat, most of them as choices among options Claude Code wrote. This file quotes the short answers as given, and says which wording was Claude Code's. The brief keeps conversation transcripts on the student's machine, so **the answers themselves cannot be checked from this repository**, only the times their records were committed. Claude Code cannot see how a text was drafted before it arrived, only when it arrived and what it said.

## The student's work

| What | Written or decided by | Claude Code's material it builds on | Record |
| --- | --- | --- | --- |
| [FILTER.md](FILTER.md) v0.1: the filter, the evidence rules, the expected sources, four wrong versions | The student, pasted in chat at about 17:25 EST. Asked who wrote it and Frictional entry 1, the student answered "I wrote both myself" | A worksheet. It held the brief's four headings, the student's own earlier words and choices as facts, and questions. It stays on the student's machine (`Assignment 8/FILTER-WORKSHEET.md`) because it quotes personal details from another record | `03485318`, before any code; the paste is kept privately, byte for byte |
| FILTER.md additions before the build: expected totals, the U.S. test, shortlist size; then the held-out design | The student. The expected totals are in the student's own words. The other answers are choices among Claude Code's options, quoted as options | The four questions and their options | `8dc8e89c` |
| [FRICTIONAL.md](FRICTIONAL.md) entry 1 | The student ("I wrote both myself") | — | `03485318` |
| The 80 hand verdicts and reasons, [labels/hand-labels-as-pasted.tsv](labels/hand-labels-as-pasted.tsv) | The student, pasted in chat at about 19:13 EST. Asked who chose them, the student picked "All mine" (Claude Code's wording: "I read each posting and chose every verdict and wrote every reason myself, outside the page.") | The 80-posting sample and the blind page (score, fate and group hidden). The page's own download at 18:51 held no labels | `1589c6ee` |
| v0.2's one change, how Can’t tell counts, what "unmet requirement" covers, which false friends to name | The student: "Experience-minimum rule", "Leave out, scale to 90%", "Both", "Both" | Four questions, with the development counts in the options | `4fec7d70` |
| The 64 claim labels, [shortlist/v0.1/claim-labels-as-pasted.tsv](shortlist/v0.1/claim-labels-as-pasted.tsv) | The student, pasted in chat on 2026-11-25 (by 08:02 EST): "I reviewed all 64 against the eight saved postings." One label per claim suffix for every rank, with notes for the insufficient claims | The 64 claims Claude drafted and the claims page. The page's own download was not found | `abca3125` |
| The decisions on Claude's challenge: R3-C3 to supported, R4-C4 to insufficient, all eight location claims to insufficient, all eight work-authorization abstentions kept | The student: "Becomes supported", "Becomes insufficient", "All eight insufficient", "All eight stay insufficient" | Four questions and their options. Claude Code also checked and said that two of the challenged sentences are in all eight postings | `f4a08d28` |
| Pending: both trust decisions, Frictional entries 2–4, the sign-off | The student | The evaluation drafts; the facts list in the README | — |

## Claude Code's work

- **The code.**
  - Everything new in `jobwatch/` for JS3: `screen`, `location`, `evidence`, `experience`, `held_out`, `hand_labels`, `sample`, `label_page`, `corpus`, `claims`, `measure`, `variants`, `js3`, and the tool server, tap, harness and host session.
  - The tests: the 115 new JS3 tests. Of the 164 carried over unchanged from JS2, Claude Code wrote 160 there, and the student wrote `tests/test_review_empty_board.py` (4). The cases in `StudentsWrongVersionsTest` and the exact-quote case in `test_evidence.py` follow the student's FILTER.md word for word. The wrong versions C1–C12 are Claude Code's.
- **The drafts:** this file, the [README](README.md), the [reports](reports/), the [evaluations](evaluations/), the [inventory](corpus/INVENTORY.md) and the [transcripts note](transcripts/README.md).
- **The texts sent to Claude:** the claims prompt ([prompts/claims-v1.md](prompts/claims-v1.md)), the challenge prompt ([prompts/flip-v1.md](prompts/flip-v1.md); its label definitions are FILTER.md's, quoted), the host-session message ([transcripts/prompts/](transcripts/prompts/)), the harness scripts ([transcripts/scripts/](transcripts/scripts/)) and the leads prompt (Chapter 8's instruction, quoted in [evaluations/ask_for_discrepancies.py](evaluations/ask_for_discrepancies.py)).
- **The options in every question to the student.**
- **The runs:** the live corpus run and every command in the README's "What ran" table.
- **Three things Claude Code got wrong, and when each was caught:**
  - a test accepted a lowercase quote as exact. It was corrected in `658dab34`, before any filter code;
  - FILTER.md said 19:35 for a choice committed at 19:33. It was corrected in `a5e2d362`;
  - a draft of the reject audit credited the description topic with two keeps that the titles had already decided. It was corrected before the report was committed.

## Claude's responses, each one as received

All came from `claude-opus-5-5` through `claude -p` on the student's Claude Code login, on 2026-11-24 unless marked:

| What | When (UTC) | Saved as |
| --- | --- | --- |
| 64 claims and quotes for the shortlist, 8 calls | 22:56–22:57 | [shortlist/v0.1/claude/](shortlist/v0.1/claude/) |
| Discrepancy leads for both tool servers, 2 calls (13 and 11 leads) | before `ebb30cd9` (23:06) | [evaluations/claude-leads/](evaluations/claude-leads/) |
| The real host session's answer | before `d3fe93e3` (23:03) | [transcripts/2026-11-24-claude-code-session-host.jsonl](transcripts/2026-11-24-claude-code-session-host.jsonl) |
| The challenge to the student's 64 claim labels, 8 calls (2026-11-25) | 13:06:49–13:08:27 | [shortlist/v0.1/flip/](shortlist/v0.1/flip/) |

Claude's leads were checked against the source and the MCP pages before use. One was confirmed and fixed test-first (server 0.1.1). One was partly wrong and one was wrong. The evaluations show each.

## Inherited

- **JS2's code.** `jobwatch/` was copied from JS2 `9c1db18`, unchanged (`ef0e7057`): the loop, the ATS parsers, the permission policy and the tokenizer. Claude Code built it in JS1 and JS2 to the student's CONTRACT.md and GATE.md.
- **The persona.** [persona/alex_morgan.json](persona/alex_morgan.json), fictional, from JS1.
- **The country list.** [jobwatch/data/iso3166.tab](jobwatch/data/iso3166.tab) is from tzdata 2026e, which is public domain, copied unchanged (sha256 `837c8078…aeb2a`).
- **The board endpoints.** They come from the instructor's collector, Lectern (`ATS.md`), through JS2.

## What was read

- **The course.** Chapters [7](../../../chapters/07-retrieval-and-cowork.md), [8](../../../chapters/08-mcp-from-scratch.md) and [9](../../../chapters/09-training-and-configuration.md), and the [JS3 brief](../../../assignments/assignment-js3-the-filter-the-tool-and-the-score.md), at upstream `e27e91fe`.
- **The MCP specification, version 2025-11-25, read 2026-11-24.** Claude Code's evaluations quote the lifecycle, ping and tools rules, including the [tools page](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).
- **The course's teaching server.** That is `lessons/08-mcp-from-scratch/code/main.py` at `a8629ce1` (sha256 `948337af…1769`). Claude Code read Chapter 8's text before building this folder's server. It opened the lesson code only after the server was built and tested (`cc80e659`), and evaluated it without copying from it.

## Other students' work

- Three commit subjects about other students' JS3 work appeared in `git log` output: `821ddee3` ("js3: FILTER.md v0.1 written before any code"), `aa22f375` ("JS3 corpus: one more live run with the unchanged JS2 loop …") and the upstream head `e27e91fe` ("JS3: abstention example status line reviewed").
- The course validator's output lists other folders by name.
- None of those folders was opened.
