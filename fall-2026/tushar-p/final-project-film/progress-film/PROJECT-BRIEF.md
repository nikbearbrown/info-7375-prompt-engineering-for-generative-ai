# PROJECT-BRIEF — Agent Proving Ground (progress, through M5)

**Drafted by Claude Code for Tushar's review**, Nov 23, 2026. Re-derived from the v2 narration in BEAT-PLAN.md (Tushar, Nov 23) and the evidence captured in `evidence/`. Nothing here goes beyond what the film says or what the captures show.

Tushar Patel · INFO 7375 Final Project · Target role: software engineer, agent infrastructure

## 1. What is it?
Agent Proving Ground is a command-line tool, with its code in a public GitHub repo. You give it a small coding task. It runs an AI agent (Claude Haiku) on that task inside a locked sandbox, records every step the agent takes, and decides pass or fail by running its own tests, never by taking the agent's word for it.

## 2. Why would anyone care?
AI coding agents are good at saying they're finished, but "done" is a claim, not a result. An agent can fix the bug, quietly edit the test so it passes, or just give up, and its message can look the same each time. More and more code is written by agents, and someone has to check it rather than trust it.
Parts of this already exist. E2B provides sandboxes for running AI-generated code, and Langfuse records LLM traces and scores (both as worded in the October brief). Each solves one piece well. But a sandbox doesn't tell you whether the work is right, and a trace doesn't stop an agent from doing what it shouldn't. Agent Proving Ground joins the pieces in one small loop that runs on a laptop: sandbox, trace, an independent check, and a human approval before any change leaves.

## 3. Who opens it, and what do they do in the first minute?
Engineers deciding whether to trust a coding agent, or a change to one. In their first minute they run one command, read one result line (for example `001  PASS  steps=3  reason=check_passed`), and open the trace to see exactly what the agent did.

## 4. What does it prove about me?
- **A working agent harness:** the harness starts a Kubernetes pod with no network, not running as root. The agent gets three tools (read a file, write a file, run a command). Every tool call passes a permission policy written in code first, and a denied call is recorded and never runs.
- **Independent verification:** after every change, the harness runs a hidden check the agent never sees, and pass or fail comes only from that check. Before any change leaves, I see the diff and approve it, and my approval is bound to the exact bytes I saw (`diff_sha256` must equal `recheck_sha256`).
- **Evaluation discipline:** 16 small Python repos I made, 11 ordinary bugs and 5 where the right answer is no (a wrong test, a task that needs the network, a budget too small). I froze a development/held-out split (commit `26b5305`, Nov 13) before tuning anything, and committed my predictions (`6d7bafe`, Nov 17) before the held-out comparison.
- **Honest reading of results:** in 70 held-out runs, both system prompts passed all 20 normal runs and said no on all 15 no-runs. I read all 40 passing fixes myself; on one task, 7 of 10 missed what the documentation asks for. So a pass means the checks passed, not that the spec was met.
- **New skills:** I learned Go and Kubernetes for this project; both were new to me.

## 5. What is in, what is out, what comes first?
- **In:** one small loop on one laptop, with Docker and kind, a spend-limited API key, and Claude Code, which writes the code while I review every change.
- **Out:** it won't be a hosted service or a model benchmark. It's one honest tool.
- **First (next):** a controlled failure. I'll make an agent edit its own test on purpose, show the check catching it, and fix it. Then a stranger run from the README on a clean machine, and a hardened check that confirms every test actually ran.

## 6. What could sink it?
The biggest risk is a pass that isn't real, since code under test can fool a check. That's why I review diffs and write down every known gap (FAILURES.md; F2 is a pass that missed the spec). One known gap is that code under test can end the run with `os._exit(0)`, so exit code 0 alone doesn't prove every test ran; hardening the check is item 3 of "Will exist".

It is judged on three things:
- On normal tasks, it should pass.
- On the five no-tasks, it must say no; a pass on one of those would mean it failed.
- Changes, like two different system prompts, are compared on held-out tasks nobody tuned on, with predictions written down first.

## 7. Why this project?
More and more code is written by agents, and someone has to check it rather than trust it. I built it to do that, and along the way I learned Go and Kubernetes. The target role is software engineer, agent infrastructure.

## Exists today (through M5)
- M0–M5, all logged in the APG PLAN.md (Nov 3 – Nov 18, 2026).
- The Go harness running Claude Haiku with three tools in a Kubernetes pod with no network, not as root. First real run: task 001 PASS in 3 steps, every step in the trace (Nov 12).
- The permission policy: a denied call is recorded and never runs (for example run `20261118T034327Z-b54f5cd6`, Nov 17 ET). The human gate is bound to the diff's SHA-256.
- 16 synthetic Python tasks (11 normal, 5 where the answer is no) and the frozen dev/held-out split (`26b5305`, Nov 13).
- Isolation tests from inside a real pod: every limit held (Nov 17).
- Pre-registered predictions (`6d7bafe`, Nov 17) and 70 held-out runs comparing two system prompts, with `apg compare` output (Nov 18).
- My review of all 40 passing fixes, and FAILURES.md with the known gaps (Nov 18).
- Public repo: github.com/tushar-patel28/agent-proving-ground.

## Will exist
1. **Controlled failure:** an agent edits its own test on purpose, the check catches it, and it is fixed.
2. **Stranger run:** a stranger runs the project from the README on a clean machine.
3. **Hardened check:** a hardened check that confirms every expected test ran, so `os._exit(0)` can't fake a pass. Today, exit code 0 alone doesn't prove every test ran (APG docs/07-evidence.md, Honest limits point 4; docs/03-action-surface-map.md).

All three by Dec 18 (target submit, PLAN.md).
