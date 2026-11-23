# BEAT-PLAN — Agent Proving Ground, progress film (through M5)

Tushar Patel · INFO 7375 · Final Project Film · approved by Tushar, Nov 23, 2026
Target length: about 3:45 (about 540 words of narration at about 145 words a minute)

Labels: REAL = real output or file from the repo, date on screen · CONSTRUCTED = drawn diagram, labelled "constructed" on screen.
Tense rule: past tense only for what ran (M0–M5). Everything after M5 is "will".

## Part 1 — Executive summary (about 50 s)
B1 Hello (8 s): "I'm Tushar Patel, a software engineering student at Northeastern. This is my final project, Agent Proving Ground." Visual: title card. CONSTRUCTED.
B2 The problem (15 s): "When an AI coding agent says "done," that isn't the same as the job being done. The agent might have fixed the bug, or quietly changed the test, or just stopped." Visual: speech bubble "Done!" beside a red failing test. CONSTRUCTED.
B3 What it is and why it matters (27 s): "Agent Proving Ground runs a coding agent on small tasks inside a locked sandbox. It records every step the agent takes, and it decides pass or fail with its own tests, never with the agent's word. Anyone who relies on a coding agent needs exactly this: a cheap, local way to see what the agent did, and whether it really worked." Visual: sandbox → trace → check → PASS/FAIL. CONSTRUCTED.

## Part 2 — Introduction (about 35 s)
B4 Others (22 s): "Pieces of this already exist. E2B and Runtime give agents sandboxes. Langfuse and Raindrop trace and evaluate model calls. oh-my-pi is a harness for coding agents. And a Drupal project, AI Proving Ground, grades what an agent actually saved instead of what it reports, but only for Drupal sites." Visual: one card per tool. CONSTRUCTED. [VERIFY against the October PROJECT-BRIEF wording.]
B5 Why mine (13 s): "What I wanted was all of it in one small loop I can run on a laptop: sandbox, trace, an independent check, and a human who approves before anything leaves, with every failure written down." Visual: the four pieces joined in a loop. CONSTRUCTED.

## Part 3 — Methods (about 80 s)
B6 The loop (22 s): "I built it in Go. The agent is Claude Haiku, with three tools: read a file, write a file, run a command. It works inside a Kubernetes pod with no network. After every change, the harness runs a hidden check the agent never sees. Here's a real run on task one: it passed in three steps, and every step is in the trace." Visual: REAL, apg run 001 result line (Nov 12) and apg show of 20261112T053055Z-92239eb0.
B7 Policy and gate (20 s): "Every tool call goes through a policy written in code. A denied call never runs; it's just recorded. And before any change leaves the sandbox, I see the diff and approve it myself. My approval is bound to the exact bytes I saw, so if the diff changes, my approval is void." Visual: REAL, a denied call from a contract B 008 held-out trace (Nov 17), then my human-answered approval 20261113T224740Z-a9a2c258 (Nov 13).
B8 Data (20 s): "The data is sixteen small Python tasks I made for this project. Eleven are normal bugs. Five are built to make the system say no: a wrong test, a task that needs the network, a budget too small. I split them into development and held-out sets, and froze that split before tuning anything." Visual: REAL, tasks/README.md and split commit 26b5305.
B9 Isolation and resources (18 s): "I tried to break the sandbox from inside a real pod: no network, not root, capped CPU, memory, processes and disk. Every limit held. It runs on my laptop with Docker and kind, a spend-limited API key, and Claude Code, which wrote the code while I reviewed every change." Visual: REAL, evidence/isolation/20261117-isolation-d29.txt highlighted lines (Nov 17).

## Part 4 — Evaluation (about 80 s)
B10 How it's judged (16 s): "Pass or fail comes only from the hidden check. I compared two system prompts: the original, and a longer one I wrote. Before running either on the held-out tasks, I wrote down and committed my predictions." Visual: REAL, docs/t5-predictions.md header and commit 6d7bafe.
B11 Results (22 s): "Seventy held-out runs. Both prompts passed all twenty normal runs, and both said no on all fifteen failure runs. That's a ceiling: pass rate can't tell them apart. My longer prompt cost about forty-one percent more and did no better." Visual: REAL, evidence/compare/20261118-t51-a-vs-b.txt (Nov 18); costs labelled "estimated from list prices".
B12 What a pass really means (20 s): "Then I read all forty passing fixes myself. No cheating, no test edits. But on one task, seven of ten fixes missed behavior the documentation asks for and the tests don't check. So a pass means the frozen checks passed, not that the spec was met." Visual: REAL, FAILURES.md F2 and my executed check output ['X', 'x'] (Nov 18).
B13 What's next, and what would count as failure (22 s): "Next, I'll trigger a failure on purpose, an agent editing its own test, and show the check catching it. Then a stranger will run the project from the README alone. If it ever passes something it shouldn't, or a sandbox limit breaks, it didn't work. The code is public at github.com/tushar-patel28/agent-proving-ground." Visual: checklist with M0–M5 ticked and "controlled failure", "stranger run", "submit Dec 18" open. CONSTRUCTED. Repo URL on screen.
