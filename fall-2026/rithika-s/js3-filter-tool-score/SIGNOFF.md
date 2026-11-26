# Sign-off — JS3

## What I checked, with evidence
- The filter matches FILTER.md: config transcribed and read against section 1; W1–W5 mutant tests fail on the wrong versions and pass on the real filter.
- The frozen corpus is hash-checked on every load (CORPUS.sha256).
- Reject audit (AUDIT.md): 50 rows, false friend found, v1.1 recorded in the FILTER.md change log.
- Held-out measurement (SCORE.md): drawn first, never used for tuning.
- MCP server (TOOLSERVER.md): scripted client 8/8; Claude Code as client; the server log matched Claude's report.
- Third-party server probed: 10 requests plus 1 malformed line, all answered.
- Full test suite passes (count in README).

## Not checked
- **Label independence:** audit and held-out verdicts were suggested by Claude Code and reviewed by me; the claim labels were drafted by Claude Code in auto mode. None are blind hand labels.
- **Whether v1.1 is better on unseen postings:** the held-out set (2 relevant, 0 kept by any version) cannot tell the versions apart.
- **Generic titles:** ML/data work behind plain "Software Engineer" titles is missed by every version (both held-out positives).
- **Plurals and compounds:** whole-word matching misses `models`, `LLMs`, `machine-learning`.
- **Curly vs straight apostrophes:** a correct quote can fail the quote check, giving a false "I cannot tell".
- **One date only:** every posting is from 2026-11-10.
- **MCP:** concurrent clients, remote transport, very long or non-ASCII ids; my server refuses `ping` before `initialize` (spec allows it) and does not gate on `notifications/initialized`.
- **A JS2 test leaves an unclosed-file ResourceWarning**; it does not fail.

## Driver's seat
| Decision | Who decided | Who did the work |
|---|---|---|
| Persona, targets, labeling rule | Me (inherited from JS1, rule written before labeling) | Me |
| FILTER.md v1.0 rules, threshold, Senior/Staff kept | Me (Claude proposed, I confirmed) | Claude drafted the wording |
| Frozen corpus over a fresh live run | Me | Me (commands) |
| Accepting Claude Code's build ambiguities | Me | Claude Code wrote the code and tests |
| Audit and held-out verdicts | Me, by reviewing and correcting each suggestion | Claude Code suggested them |
| v1.1 changes, rejecting `software engineer` | Me (Claude proposed after the audit) | Claude drafted AUDIT.md |
| Step 9 design (rule-based changes, not a Claude scorer) | Me | Claude proposed |
| Trust decisions on both servers | Me | Me |
| Claim labels | Me, by review | Claude Code drafted |

Signed:Rithika (25th Nov, 2026)
