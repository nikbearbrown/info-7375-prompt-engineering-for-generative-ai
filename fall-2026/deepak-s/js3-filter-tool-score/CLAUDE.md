# CLAUDE.md: working rules for js3-filter-tool-score

Read before any work: private/ASSIGNMENT.md (brief and rubrics), private/JS2_HANDOFF.md (what JS2 built and what it taught), private/CLAUDE_CODE_PROMPT.md (phase plan with gates).

## Scope
- Work only inside this folder.
- JS1 (../js1-contract-and-watch/) and JS2 (../js2-loop-tools-diff/) are read-only. Never edit, stage or commit anything there. JS2's submitted commit is b2ac533.
- No git push, no class-repo action, no PR change unless Deepak types "push" in this session.

## The spec
- FILTER.md is the spec. If code and FILTER.md disagree, FILTER.md wins. If it is unclear or silent, stop and ask.
- The commit adding FILTER.md (with Deepak's rules and labeling rule) comes before any commit that adds filter, scorer, shortlist, audit or tool-server code.

## Honesty
- Past tense only for what ran in this session and is on disk. Every number in a doc comes from a committed file; cite the path.
- Label every fixture, mock or simulated run SEEDED in its filename, output and docs.
- Any Claude output shown carries the model ID and date. Never state how an endpoint, a spec or a tool server behaves unless it was captured or fetched in this session; cite the capture or URL.
- If live behavior differs from the plan, or a step is impossible, say so and stop. Never substitute silently.
- Never call a file, module or folder "unchanged" without a byte-identity check.

## Deepak's parts: Claude never writes these
- FRICTIONAL.md and SIGNOFF.md (all of them, including the driver's seat table)
- In FILTER.md: section 0, the relevance rules and their reasons, the weights and threshold, and every "decision" cell in the changelog. Claude may propose, as a list in its report, never as text in the file.
- Every hand verdict and hand label: the held-out labels, the audit verdicts, the final claim labels on the shortlist
- Every trust decision in the tool-server evaluations
- The review or acceptance decision on any change
Leave every Deepak marker in place in those files. presubmit fails while any remain, which is intended.

## Labels and measurement
- The held-out set is drawn once, with a recorded seed, and committed before Deepak labels it. It is never used to choose rules, weights, thresholds or prompts. Only the Phase 6 measurements read it.
- Claude never sees or shows the filter's score next to a posting Deepak is labeling blind.
- Report counts with their denominators. Any rate from a sample comes with its exact binomial 95% interval and the sample size.
- A run of the Claude judge is noisy. Never attribute a difference to a change without a repeated baseline.

## Agent safety, enforced in code (carried from JS2)
- HTTP GET only, to exact allow-listed hosts, https on 443, redirects refused. All network and disk access goes through jobwatch/tools.py with policy.check(); the stated exceptions are in JS2 GATE.md A-1 to A-3 and in FILTER.md.
- The tool server is local and read-only. It reads only under this folder's runs/ and data/ through tools.read_file, opens no network, writes only its own transcript under evidence/mcp/.
- The agent never applies, emails, messages or logs in. No non-GET method anywhere.
- Fictional persona only (Riley Okafor, @example.com). No real résumé, contacts or tokens.

## Stack
- Python 3.15.0, stdlib urllib for HTTP, the tool server written from scratch with the stdlib (no MCP SDK). Pinned requirements.txt with only anthropic, jsonschema and pytest unless Deepak approves more. One entry point: python -m jobwatch.
- No Anthropic API key. The Claude judge, where used, is the JS1 Claude Code CLI backend.
- No TODO, FIXME, stub, placeholder pass or "not implemented" path in delivered code.

## Process
- Stop at every GATE and wait for Deepak.
- Commit evidence before writing about it. Small commits, subjects prefixed "js3:". Stage only named files.
- Never weaken, skip, xfail or delete a test to get green. Report failures and stop.
- After every change, list the files touched and the FILTER.md clause or brief requirement it serves.
- After each phase, append factual lines (ET time, command, exit code, commit hash) to private/SESSION_LOG.md, then print 3 short questions for Deepak's FRICTIONAL entry. Deepak writes that entry at the gate, not at the end.
