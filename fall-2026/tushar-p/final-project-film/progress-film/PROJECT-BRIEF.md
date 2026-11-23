# PROJECT-BRIEF — Agent Proving Ground (progress, through M5)

**Drafted by Claude Code for Tushar's review**, Nov 23, 2026, from the facts in BEAT-PLAN.md (approved by Tushar, Nov 23) and the evidence captured in `evidence/`. Nothing here goes beyond what the film says or what the captures show.

Tushar Patel · INFO 7375 Final Project · Target role: software engineer, agent infrastructure

## 1. What is it?
Agent Proving Ground runs a coding agent on small tasks inside a locked sandbox. It records every step the agent takes, and it decides pass or fail with its own tests, never with the agent's word. It is built in Go. The agent is Claude Haiku (`claude-haiku-5-5`) with three tools: read a file, write a file, run a command. It works inside a Kubernetes pod with no network, and after every change the harness runs a hidden check the agent never sees.

## 2. Why would anyone care?
When an AI coding agent says "done," that isn't the same as the job being done. The agent might have fixed the bug, quietly changed the test, or just stopped. Anyone who relies on a coding agent needs a cheap, local way to see what the agent did, and whether it really worked.
Pieces of this already exist. E2B provides sandboxes for running AI-generated code, and Langfuse records LLM traces and scores (both as worded in the October brief). A Drupal project, AI Proving Ground, grades what an agent actually saved instead of what it reports, but only for Drupal sites. What I wanted was all of it in one small loop I can run on a laptop: sandbox, trace, an independent check, and a human who approves before anything leaves, with every failure written down.

## 3. Who opens it, and what do they do?
Someone who relies on a coding agent, or an engineer reviewing my work. They read the README, run the project, and look at a run's trace step by step (`apg show`). Before any change leaves the sandbox, a human sees the diff and approves it. A stranger running the project from the README alone is the test of this, and it hasn't happened yet (see "Will exist").

## 4. What does it prove about me?
- **Agent loop and tools:** a Go harness that runs Claude Haiku with three tools, and records every step in a trace.
- **Policy and human gate:** every tool call goes through a policy written in code. A denied call never runs and is recorded. My approval is bound to the exact bytes of the diff I saw: `diff_sha256` must equal `recheck_sha256`, or the approval is void.
- **Isolation:** tested from inside a real pod: no network, not root, capped CPU, memory, processes and disk. Every limit held (Nov 17).
- **Evaluation discipline:** 16 tasks I made, 11 normal and 5 built to make the system say no. The development/held-out split was frozen (commit `26b5305`) before tuning, and predictions were committed (`6d7bafe`) before the held-out runs.
- **Honest reading of results:** both prompts passed 20/20 normal runs and said no on 15/15 failure runs, so pass rate hit a ceiling. My longer prompt cost about 41% more (estimated from list prices) and did no better. I read all 40 passing fixes: no cheating and no test edits, but on one task 7 of 10 fixes missed behaviour the documentation asks for and the tests don't check. A pass means the frozen checks passed, not that the spec was met.

It runs on one laptop with Docker and kind. Claude Code wrote the code while I reviewed every change.

## 5. What is in, what is out, what comes first?
- **In (done):** the Go harness, the sandbox on kind, the policy and human gate, traces, the 16-task suite with hidden checks, the frozen split, the held-out comparison of two system prompts, and a failure log (FAILURES.md).
- **Out:** anything beyond one laptop. It runs locally with Docker and kind and a spend-limited API key.
- **Next:** trigger a failure on purpose (an agent editing its own test) and show the check catching it. Then a stranger runs the project from the README alone. Target submit: Dec 18.

## 6. What could sink it?
If it ever passes something it shouldn't, or a sandbox limit breaks, it didn't work. A known limit is already written down: the checks are frozen and do not cover everything the documentation asks for (FAILURES.md F2), so a pass is not proof the spec was met. Pass rate also can't tell the two prompts apart, because both were at the ceiling.

## 7. Why this project?
I wanted sandbox, trace, an independent check and a human approval in one small loop I can run on a laptop, with every failure written down. The target role is software engineer, agent infrastructure.

## Exists today (through M5)
- M0–M5, all logged in the APG PLAN.md (Nov 3 – Nov 18, 2026).
- The Go harness running Claude Haiku with three tools in a Kubernetes pod with no network (first real run: task 001 PASS in 3 steps, Nov 12).
- The policy (denied calls recorded, not run) and the human gate bound to the diff's SHA-256 (approved by me, Nov 13).
- 16 synthetic Python tasks (11 normal, 5 failure cases) and the frozen dev/held-out split (`26b5305`, Nov 13).
- Isolation evidence from inside a real pod; every limit held (Nov 17).
- Pre-registered predictions (`6d7bafe`, Nov 17) and 70 held-out runs comparing two system prompts (Nov 17–18 ET), with `apg compare` output (Nov 18).
- My review of all 40 held-out PASS diffs, and FAILURES.md (F1–F3) (Nov 18).
- Public repo: github.com/tushar-patel28/agent-proving-ground.

## Will exist
- A controlled failure: an agent editing its own test, caught by the check.
- A stranger run of the project from the README alone.
- The final submission (target Dec 18).
