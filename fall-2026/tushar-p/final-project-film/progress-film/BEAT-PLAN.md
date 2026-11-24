# BEAT-PLAN — Agent Proving Ground, progress film (through M5) — v2

Tushar Patel · INFO 7375 · Final Project Film · v2, Nov 23, 2026
Hard cap 4:00, target about 3:50.

> **Note, Nov 23, 2026:** v1 of this beat plan (approved earlier the same day) was superseded on Nov 23, 2026 because it led with implementation and ended without explaining what's left. v2 explains the project first, keeps "built so far" short, and ends on what's left. v1 is kept unchanged in "Superseded: v1" at the bottom of this file.

> **Note, Nov 23, 2026 (later): B10 changed.** One overclaim was fixed; only this sentence changed.
> - Before: "Third, I compare changes, like two different system prompts, on held-out tasks nobody tuned on, and I write my predictions down before every run."
> - After: "Third, I compare changes, like two different system prompts, on held-out tasks nobody tuned on, and I wrote my predictions down before the held-out runs."
>
> The captures show predictions committed before the held-out runs (`6d7bafe`), not before every run. B10's audio and scene were regenerated, and every gate was re-run.

> **Note, Nov 23, 2026 (later still): B12 item 3 changed** from "submission" to a real implementation item. Only the last sentence and card 3 changed; cards 1 and 2 stayed the same.
> - Before: "Third, the full write-up and submission, by December eighteenth." Card 3: "3 Submit — packet + demo, Dec 18".
> - After: "Third, I'll harden the check, so it confirms every test actually ran." Card 3: "Harden the check" / "confirm every test actually ran: a forced exit can't fake a pass", with a footer under all three cards: "All by Dec 18".
>
> Source for the gap: APG docs/03-action-surface-map.md and docs/07-evidence.md Honest limits point 4 name `os._exit(0)` as a cheat the check can't catch (`evidence/B12-v2.txt`). B12's audio and scene were regenerated, and every gate was re-run.

Labels: REAL = real output from the captures in `evidence/`, with source path and date on screen · CONSTRUCTED = drawn, labelled "constructed" on screen.

## PART 1 — EXECUTIVE SUMMARY
B1 (about 8 s) "Hi, I'm Tushar Patel, a software engineering student at Northeastern. This is my final project for INFO 7375: Agent Proving Ground."
   Visual: title card. CONSTRUCTED.
B2 (about 18 s) "AI coding agents are good at saying they're finished. But "done" is a claim, not a result. An agent can fix the bug, or quietly edit the test so it passes, or just give up, and its message can look the same each time."
   Visual: three panels, each ending in the same bubble "Done!": fixed bug ✓ / edited test ✗ / gave up ✗. CONSTRUCTED.
B3 (about 18 s) "Agent Proving Ground is a command-line tool, with its code in a public GitHub repo. You give it a small coding task. It runs an AI agent on that task inside a locked sandbox, records every step it takes, and decides pass or fail by running its own tests. Never by taking the agent's word for it."
   Visual: one command → sandbox → trace → check → PASS/FAIL. CONSTRUCTED.
B4 (about 16 s) "It's for engineers deciding whether to trust a coding agent, or a change to one. In their first minute, they run one command, read one result line, and open the trace to see exactly what the agent did."
   Visual: a terminal mock: one command, one result line, a trace opening. CONSTRUCTED.

## PART 2 — INTRODUCTION
B5 (about 20 s) "Parts of this already exist. E2B provides sandboxes for running AI-generated code. Langfuse records LLM traces and scores. Each solves one piece well. But a sandbox doesn't tell you whether the work is right, and a trace doesn't stop an agent from doing what it shouldn't."
   Visual: two cards (E2B, Langfuse), each with "solves" / "doesn't". CONSTRUCTED.
B6 (about 20 s) "Mine joins the pieces in one small loop that runs on a laptop: sandbox, trace, an independent check, and a human approval before any change leaves. I built it because more and more code is written by agents, and someone has to check it rather than trust it. Along the way I learned Go and Kubernetes, which were both new to me."
   Visual: four pieces joined into a loop. CONSTRUCTED.

## PART 3 — METHODS
B7 (about 30 s) "Here's one run. The harness starts a Kubernetes pod with no network, not running as root. The agent, Claude Haiku, gets three tools: read a file, write a file, run a command. Every tool call passes a permission policy written in code first. After every change, the harness runs a hidden check the agent never sees. Pass or fail comes only from that check. Then I see the diff and approve it, and my approval is bound to the exact bytes I saw."
   Visual: one diagram, built up step by step in sync with the narration: pod → agent + 3 tools → policy → hidden check → trace → human gate. CONSTRUCTED.
B8 (about 20 s) "The tasks are sixteen small Python repos I made. Eleven are ordinary bugs. Five are designed so the right answer is no: a wrong test, a task that needs the network, a budget too small. I froze a development and held-out split before tuning anything. It runs on my laptop with Docker and kind, a spend-limited API key, and Claude Code, which writes the code while I review every change."
   Visual: 16 task tiles (11 green, 5 red) splitting into "dev" and "held-out" with a lock. CONSTRUCTED.
B9 (about 25 s) "All of that is built and tested now, through milestone five. A real run on task one passed in three steps, with every step in the trace. A denied tool call was recorded and never ran. And when I tried to break the sandbox from inside a real pod, every limit held."
   Visual: REAL, three quick dated frames from the existing captures: the apg run 001 PASS line (Nov 12), the denied call in run 20261118T034327Z-b54f5cd6 (Nov 17 ET), and the isolation results (Nov 17). A small "M0–M5 ✓" strip in the corner.

## PART 4 — EVALUATION
B10 (about 25 s) "It's judged on three things. On normal tasks, it should pass. On the five no-tasks, it must say no. A pass on one of those would mean it failed. Third, I compare changes, like two different system prompts, on held-out tasks nobody tuned on, and I wrote my predictions down before the held-out runs."
   Visual: three checks: "normal → PASS", "no-tasks → must FAIL", "compare on held-out, predictions first". CONSTRUCTED.
B11 (about 20 s) "First results: seventy held-out runs. Both prompts passed all twenty normal runs and said no on all fifteen no-runs. Then I read all forty passing fixes myself. On one task, seven of ten missed what the documentation asks for. So a pass means the checks passed, not that the spec was met."
   Visual: REAL, the apg compare totals (Nov 18), then FAILURES.md F2 with ['X', 'x'] (Nov 18). No costs.

## CLOSE
B12 (about 22 s) "Three things are left. First, a controlled failure: I'll make an agent edit its own test on purpose, show the check catching it, and fix it. Second, a stranger will run the project from the README on a clean machine. Third, I'll harden the check, so it confirms every test actually ran."
   Visual: three numbered cards, each with its one-line explanation on screen: "1 Controlled failure — edit the test → check catches it → recover", "2 Stranger run — README only, clean machine", "3 Harden the check — confirm every test actually ran: a forced exit can't fake a pass". A small footer under all three cards: "All by Dec 18". CONSTRUCTED.
B13 (about 18 s) "The biggest risk is a pass that isn't real, since code under test can fool a check. That's why I review diffs and write down every known gap. It won't be a hosted service or a model benchmark. It's one honest tool. Thanks for watching. The code is at github.com/tushar-patel28/agent-proving-ground."
   Visual: "Risk: a pass that isn't real → diff review + documented gaps", then the repo URL and "Thanks for watching." CONSTRUCTED.

---

## Superseded: v1

Kept unchanged below. v1 was approved by Tushar earlier on Nov 23, 2026, and superseded the same day (see the note at the top).

### v1 — BEAT-PLAN — Agent Proving Ground, progress film (through M5)

Tushar Patel · INFO 7375 · Final Project Film · approved by Tushar, Nov 23, 2026
Target length: about 3:45 (about 540 words of narration at about 145 words a minute)

Labels: REAL = real output or file from the repo, date on screen · CONSTRUCTED = drawn diagram, labelled "constructed" on screen.
Tense rule: past tense only for what ran (M0–M5). Everything after M5 is "will".

### Part 1 — Executive summary (about 50 s)
B1 Hello (8 s): "I'm Tushar Patel, a software engineering student at Northeastern. This is my final project, Agent Proving Ground." Visual: title card. CONSTRUCTED.
B2 The problem (15 s): "When an AI coding agent says "done," that isn't the same as the job being done. The agent might have fixed the bug, or quietly changed the test, or just stopped." Visual: speech bubble "Done!" beside a red failing test. CONSTRUCTED.
B3 What it is and why it matters (27 s): "Agent Proving Ground runs a coding agent on small tasks inside a locked sandbox. It records every step the agent takes, and it decides pass or fail with its own tests, never with the agent's word. Anyone who relies on a coding agent needs exactly this: a cheap, local way to see what the agent did, and whether it really worked." Visual: sandbox → trace → check → PASS/FAIL. CONSTRUCTED.

### Part 2 — Introduction (about 35 s)
B4 Others (22 s): "Pieces of this already exist. E2B and Runtime give agents sandboxes. Langfuse and Raindrop trace and evaluate model calls. oh-my-pi is a harness for coding agents. And a Drupal project, AI Proving Ground, grades what an agent actually saved instead of what it reports, but only for Drupal sites." Visual: one card per tool. CONSTRUCTED. [VERIFY against the October PROJECT-BRIEF wording.]
B5 Why mine (13 s): "What I wanted was all of it in one small loop I can run on a laptop: sandbox, trace, an independent check, and a human who approves before anything leaves, with every failure written down." Visual: the four pieces joined in a loop. CONSTRUCTED.

### Part 3 — Methods (about 80 s)
B6 The loop (22 s): "I built it in Go. The agent is Claude Haiku, with three tools: read a file, write a file, run a command. It works inside a Kubernetes pod with no network. After every change, the harness runs a hidden check the agent never sees. Here's a real run on task one: it passed in three steps, and every step is in the trace." Visual: REAL, apg run 001 result line (Nov 12) and apg show of 20261112T053055Z-92239eb0.
B7 Policy and gate (20 s): "Every tool call goes through a policy written in code. A denied call never runs; it's just recorded. And before any change leaves the sandbox, I see the diff and approve it myself. My approval is bound to the exact bytes I saw, so if the diff changes, my approval is void." Visual: REAL, a denied call from a contract B 008 held-out trace (Nov 17), then my human-answered approval 20261113T224740Z-a9a2c258 (Nov 13).
B8 Data (20 s): "The data is sixteen small Python tasks I made for this project. Eleven are normal bugs. Five are built to make the system say no: a wrong test, a task that needs the network, a budget too small. I split them into development and held-out sets, and froze that split before tuning anything." Visual: REAL, tasks/README.md and split commit 26b5305.
B9 Isolation and resources (18 s): "I tried to break the sandbox from inside a real pod: no network, not root, capped CPU, memory, processes and disk. Every limit held. It runs on my laptop with Docker and kind, a spend-limited API key, and Claude Code, which wrote the code while I reviewed every change." Visual: REAL, evidence/isolation/20261117-isolation-d29.txt highlighted lines (Nov 17).

### Part 4 — Evaluation (about 80 s)
B10 How it's judged (16 s): "Pass or fail comes only from the hidden check. I compared two system prompts: the original, and a longer one I wrote. Before running either on the held-out tasks, I wrote down and committed my predictions." Visual: REAL, docs/t5-predictions.md header and commit 6d7bafe.
B11 Results (22 s): "Seventy held-out runs. Both prompts passed all twenty normal runs, and both said no on all fifteen failure runs. That's a ceiling: pass rate can't tell them apart. My longer prompt cost about forty-one percent more and did no better." Visual: REAL, evidence/compare/20261118-t51-a-vs-b.txt (Nov 18); costs labelled "estimated from list prices".
B12 What a pass really means (20 s): "Then I read all forty passing fixes myself. No cheating, no test edits. But on one task, seven of ten fixes missed behavior the documentation asks for and the tests don't check. So a pass means the frozen checks passed, not that the spec was met." Visual: REAL, FAILURES.md F2 and my executed check output ['X', 'x'] (Nov 18).
B13 What's next, and what would count as failure (22 s): "Next, I'll trigger a failure on purpose, an agent editing its own test, and show the check catching it. Then a stranger will run the project from the README alone. If it ever passes something it shouldn't, or a sandbox limit breaks, it didn't work. The code is public at github.com/tushar-patel28/agent-proving-ground." Visual: checklist with M0–M5 ticked and "controlled failure", "stranger run", "submit Dec 18" open. CONSTRUCTED. Repo URL on screen.

### Note on B4, added Nov 23, 2026 (the beat text above is unchanged)

B4 was changed twice on Nov 23, 2026, before the film was submitted. The film uses the final text.

1. **Brief-only cut** (step 4 [VERIFY]; Tushar chose "brief only"). The October PROJECT-BRIEF.md names only E2B and Langfuse, so its wording replaced the E2B/Runtime and Langfuse/Raindrop sentences, and the oh-my-pi sentence was removed. The Drupal sentence stayed.
   - Before: "Pieces of this already exist. E2B and Runtime give agents sandboxes. Langfuse and Raindrop trace and evaluate model calls. oh-my-pi is a harness for coding agents. And a Drupal project, AI Proving Ground, grades what an agent actually saved instead of what it reports, but only for Drupal sites."
   - After: "Pieces of this already exist. E2B provides sandboxes for running AI-generated code. Langfuse records LLM traces and scores. And a Drupal project, AI Proving Ground, grades what an agent actually saved instead of what it reports, but only for Drupal sites."
2. **Drupal removal** (Tushar's instruction). The Drupal sentence and its card were removed, so B4 names only E2B and Langfuse, as the October film did.
   - Before: "Pieces of this already exist. E2B provides sandboxes for running AI-generated code. Langfuse records LLM traces and scores. And a Drupal project, AI Proving Ground, grades what an agent actually saved instead of what it reports, but only for Drupal sites."
   - After: "Pieces of this already exist. E2B provides sandboxes for running AI-generated code. Langfuse records LLM traces and scores."

The visual is now two cards: E2B and Langfuse.
