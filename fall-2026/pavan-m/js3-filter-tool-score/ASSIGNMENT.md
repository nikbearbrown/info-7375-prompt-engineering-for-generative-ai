What this assignment is
Your agent now collects from several boards. Most of what it collects is not for you. This layer decides what reaches you and why: a filter you can read, a way to offer the agent to Claude as a tool, and a score whose numbers you can account for. It applies Chapters 7–9: retrieval and what it leaves out (Chapter 7), a tool protocol from scratch (Chapter 8), and what changes a system's behavior: training, prompts, context, tools, or settings (Chapter 9).

Build on your earlier work, the Reallocation EngineLinks to an external site. (its role scorer and recipes), or the instructor's LecternLinks to an external site., whose filter is a document with every added, cut, and rejected word recorded and measured. Say what you started from.

Use any programming language you like. Name it, give exact commands, and list your toolchain.

Step 1 — The gate: write the filter and the evidence rules first
Before you build, write FILTER.md:

The filter, as a document. What makes a posting relevant: role words, topic words, any rule about the posting text. For every rule, one line of reasoning. Version it.
The evidence rules. When a claim in your shortlist counts as supported, contradicted, or insufficient against the posting's own text, and when your agent must say "I cannot tell" instead of answering.
The expected sources. Which boards and fields your agent should see, and what its answer should be when something is missing.
Wrong versions. At least two plausible-but-wrong filters or rankings your tests must catch.
Step 2 — Build
The filter and the reject audit (Chapter 7). Run your filter on everything your agent collected. Then audit it: draw a random sample of at least 30 rejected postings and judge each yourself, plus the closest calls near your threshold, plus a sample of what you kept. Report how many you got wrong and what you can honestly say about that number from a sample this size. Find and name at least one "false friend", a word that matched for the wrong reason (for example, "training" in a machine-learning posting). Record every rule you added, cut, or rejected after measuring.
A source-grounded shortlist (Chapter 7). For each posting on your shortlist, label every claim in its justification supported / contradicted / insufficient against the posting text. Show one case where relevance is not entailment: a posting that matches your words but does not support the claim. Show your abstention rule and one counterexample that exposes its limits.
Your agent as a tool (Chapter 8). Offer one capability (for example, "search new postings" or "score this posting") to Claude through a small tool server that speaks the Model Context Protocol, or the same message shape: initialize, list tools, call a tool. Write it from scratch in any language. Preserve the real transcript in both directions. Then evaluate it the way you would a server someone else wrote: what it declares versus what it does, what a compatible client is not entitled to, and your trust decision about it. Evaluate one other tool server from a source you can name the same way.
What moves the score (Chapter 9). Your scorer has numbers in it: weights, thresholds, a Claude prompt. For each, say where it came from: hand-set, fitted on your labels, or inherited. Then make one change to one object at a time (the filter file, the prompt, the context you give Claude, the tool list, a setting) and measure on labels you held out. State what persistence is not proof of: a changed behavior across sessions does not mean anything was trained.
Step 3 — The sign-off
Sign-off — Job-Search Agent 3
Checked: which properties, by which of my own tests (name them)
How: by hand / by a test I wrote before reading Claude's code /
by recomputation / with Claude's help (say which parts)
Not checked: at least three real items
Not claiming: what this agent does not show
Signed or withheld: ____________ (name, date)
Add a driver's seat table: what Claude should do, what you should do, and why the judgment that a posting is worth your time stays yours.

What to submit
Canvas file name: LastName_FirstName_INFO7375_JS3.zip GitHub folder: fall-2026/first-name-last-initial/js3-filter-tool-score/

README.md (language, toolchain, exact commands, what ran) · FILTER.md · the code and tests · the reject audit with your hand verdicts · the source-grounded shortlist and its labels · the tool server, its transcripts, and both evaluations · the one-change-at-a-time report · the sign-off and driver's seat · SOURCES.md · FRICTIONAL.md. Include the GitHub folder link and final commit hash in Canvas. Leave out caches, credentials, and your real résumé.

Grading — 100 points
Component	Points
Implementation and explanation	60
FrictionalLinks to an external site. (honest log)	10
GitHub version postingLinks to an external site. matching Canvas	10
Relative QuartileLinks to an external site.	20
Total	100
Implementation and explanation (60) — the filter as a versioned document with reasons, written before the build (10) · the reject audit: at least 30 random rejects judged by hand, an honest statement of what the sample can show, a named false friend (12) · the source-grounded shortlist: every claim labeled, relevance-versus-entailment shown, an abstention rule (12) · the tool server and two evaluations: real transcripts, declared versus actual, a trust decision (12) · what moves the score: origin of every number, one change at a time, held-out measurement (8) · sign-off with real "Not checked" entries, and the driver's seat (6).

Frictional (10) — specific, honest accounts (3) · what you checked, changed, or learned, including what is unresolved (3) · what you accepted, modified, or rejected from Claude (2) · traceability to commits, prompts, and tests (2). An unsuccessful attempt can earn full credit.

GitHub posting (10) — source and documentation posted in your folder (4) · Canvas names the exact commit and run instructions (3) · what you submit matches what is posted (3).

Relative Quartile (20) — an overall quality score compared with the whole class: specificity, real improvement, demonstrated understanding, evidence, honesty about verification, and usability. Top 25%: 16–20 · Second 25%: 10–15 · Third 25%: 5–9 · Bottom 25%: 0–4. Meeting the criteria earns the other 80 points; it does not guarantee these 20.