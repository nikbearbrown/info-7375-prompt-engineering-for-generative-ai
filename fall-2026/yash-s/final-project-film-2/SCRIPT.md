# SCRIPT — Final Project Film

**Yash Saraf** · INFO 7375 · Fall 2026 · film due 2026-11-23

The narration of my final project film, beat by beat, exactly as the voice reads it, in the professor's four
parts. The film is built with the Brutalist toolkit, the same way as my October pitch: one drawn, moving
picture per beat, and the local Kokoro `am_onyx` voice reading this script (a synthetic voice, not mine).
The source of truth is `youtube/job-search-agent/beat_sheet.json`; every factual claim is checked in
`youtube/job-search-agent/FACTCHECK.md`.

**Past tense only for what ran.** JS1 and JS2 are built and tested; JS3 is in progress; JS4, JS5 and the
final evaluation are plans. Comparison beats are drawn from my dated screenshots in `evidence/`; terminal
beats typeset the recorded output in `youtube/job-search-agent/evidence/terminal-2026-11-23.txt`.

## Opening

### BIDEA · 10.8 s

**On screen:** The writer types 'Can AI find me the right jobs' and corrects it to 'Can AI show me why it picked them'.

> Hi, I'm Yash Saraf. This is my final project film. My first question was whether an AI tool can find me the right jobs. The better question is whether it can show me why it picked them.

## Part 1 — Executive summary: what I am building, and why it matters

### B01 · 9.7 s

**On screen:** Three kraft board boxes sit in a row; a terracotta scan line sweeps across them; posting cards pop up out of each box and a few of them get a terracotta 'new' dot. *Tag: constructed sketch.*

> My final project is a job-search agent that you can check. It watches company job boards, and it only tells you about the jobs that are new since the last time it looked.

### B02 · 7.6 s

**On screen:** A posting card slides onto a rule page; four rule lines get a check or a cross one by one; the card drops into a 'keep' or 'reject' tray with a reason strip attached. *Tag: constructed sketch.*

> For every new job, it says why the job fits the candidate, or why it does not, using written rules that anyone can check again.

### B03 · 7.6 s

**On screen:** A short shortlist page slides up to a gate post where a person waits; then three actions, apply, email and log in, slide in and are each struck through. *Tag: constructed sketch.*

> Then it stops, and a person makes the decision. It never applies for a job, never sends an email, and never logs in anywhere.

### B04 · 11.8 s

**On screen:** A counter of seen postings runs from 924 to 1,004 while new cards pile up beside it; a 'by hand' magnifier scans the pile and misses cards. *Tag: numbers from my JS2 run.*

> Why does this matter? Job boards change all the time. When I ran my agent, one company, Databricks, had eighty new postings in about ten days. Checking that by hand is slow, and it is easy to miss things.

### B05 · 6.2 s

**On screen:** A résumé page drops in with the name Priya Nair; a terracotta 'fictional' stamp presses onto it. *Tag: constructed sketch.*

> The candidate in this project is Priya Nair, a fictional person. I never use my real résumé.

## Part 2 — Introduction: what other people have done

### B06 · 11.5 s

**On screen:** A LinkedIn window fills with result rows and '99+ results'; several rows get a grey 'staff' tag. *Tag: drawn from my 2026-11-23 screenshots.*

> So what already exists? First, I tried LinkedIn. I searched for machine learning engineer jobs at Databricks in the United States, and it showed more than ninety-nine results. Many of them were staff-level roles.

### B07 · 15.1 s

**On screen:** A 'medium' match meter slides in, then a profile card labelled 'my profile, not Priya's' attaches to it; two skill chips light up on a posting card, then a 'senior' bar drops across the card. *Tag: drawn from my 2026-11-23 screenshots.*

> LinkedIn gave a medium match, but that match was based on my own profile, not on Priya's résumé, so I could not compare it with my agent. Its first posting uses skills Priya has, like Python and MLflow, but it is a senior role. Matching skills alone is not enough.

### B08 · 15.8 s

**On screen:** A ring fills to 57 percent; three bars fill to 30, 40 and 41 percent beside it; a question mark lands between the bars and the ring. *Tag: drawn from my 2026-11-23 screenshots.*

> Next, Jobright. I uploaded Priya's fictional résumé. For an AI Engineer role at Databricks, it gave a fifty-seven percent fair match, split into experience, skills, and industry. That is more explanation than I expected. But I could not see how the fifty-seven was calculated.

### B09 · 12.8 s

**On screen:** Two skill chips, PyTorch and Scikit-learn, get green ticks, then are checked against the résumé page and get crosses; a 'for experienced engineers' bar lands on the posting. *Tag: drawn from my 2026-11-23 screenshots.*

> It also marked PyTorch and Scikit-learn as Priya's skills, and neither one is in her résumé. The posting itself says it is for experienced engineers, and Priya has eight months of experience, so I would label it not relevant.

### B10 · 15.9 s

**On screen:** A Claude window shows an empty list slot labelled 'no verified list'; the AI Engineer card slides in and gets a cross; a thin line links it to the 57 ring from Jobright. *Tag: drawn from my 2026-11-23 screenshots.*

> Third, I asked Claude, Sonnet five point five, to find early-career jobs at Databricks for Priya. It did better than I expected. It did not invent a list, it explained why roles did not fit, and it rejected the same AI Engineer role that Jobright scored fifty-seven percent.

### B11 · 11.0 s

**On screen:** An 'open?' lamp stays unlit over a posting; an arrow draws toward a Greenhouse board box; a small memory bubble pops beside the window with a grey 'not isolated' note. *Tag: drawn from my 2026-11-23 screenshots.*

> But it could not confirm that any posting was still open, and it told me to use the live Greenhouse job board instead. And it read its own memory during my test, so the test was not fully clean.

### B12 · 14.5 s

**On screen:** A grid with four columns, LinkedIn, Jobright, Claude and my agent, and three rows; checks fill the my-agent column one row at a time while the other cells stay as grey dashes. *Tag: constructed sketch.*

> These tools are good at finding jobs, and my agent is not meant to replace them. What I want is different: a decision I can check. My agent reads the company's job board directly, it saves the raw data, and every keep or reject comes from a written rule.

### B13 · 12.8 s

**On screen:** An October pitch card (a docs stack) slides in and is set aside with a cross; a loop arrow draws around the job-search agent's three boards in its place. *Tag: constructed sketch.*

> One more thing. In October, I pitched a question-answering tool for the GitHub Actions docs. The final project has to be agentic, and that tool was not, so I changed my project to this agent, which I have already been building.

## Part 3 — Methods: how I am going to do it

### B14 · 18.9 s

**On screen:** Three layers stack up: JS1 and JS2 as solid kraft blocks with their test counts, JS3 as a grey outline marked 'in progress'; a fence draws around two host posts beside JS2. *Tag: constructed sketch · the tests are real.*

> Here is what I have already built. In JS1, the agent watched one job board and found only the new postings. In JS2, it became one loop over four boards, with limits on time and requests, and a permission policy in the code, so it can only read from two job-board websites. JS3, a filter with written rules, is in progress.

### B15 · 14.0 s

**On screen:** A tall bar of 2,418 postings splits into a long 'rejected' bar and a short 'review' bar; reason strips peel off the rejected bar, the top one reading 'experience above 2 years'. *Tag: numbers from my JS3 run, 2026-11-18.*

> In its first run, the filter looked at two thousand four hundred eighteen saved postings. It rejected two thousand three hundred fifty-five, and it put sixty-three in a review queue, each with a reason. Most were rejected for asking more than two years of experience.

### B16 · 12.2 s

**On screen:** A terminal window types the recorded commands and output line by line: 'Ran 65 tests', 'OK', three 'CAUGHT' lines, then 'every wrong version was caught'. *Tag: recorded output · reconstruction.*

> Here is the agent's own output, recorded today. All sixty-five tests pass, offline. Then I plant three bugs on purpose, in a copy of the code, and the tests catch every one. I will rerun this after every change.

### B17 · 12.6 s

**On screen:** The terminal types the independent check: one row per board with its recount and 'consistent', then 'Nothing flagged.' *Tag: recorded output · reconstruction.*

> A separate checker recounts every board from the saved raw data, without using the agent's code. Databricks nine hundred fifteen, Anthropic six hundred seventy-five, OpenAI eight hundred twenty-five. Nothing flagged.

### B18 · 8.2 s

**On screen:** The terminal types the reset command and a terracotta 'REFUSED … needs explicit approval' line; then the approved command and its 'reset' line. *Tag: recorded output · reconstruction.*

> And this is a human gate. Resetting what the agent remembers is refused, unless a person approves it. With my approval, it is allowed.

### B19 · 20.7 s

**On screen:** A six-step track: steps one and two solid with checks, step three half filled, steps four to six grey outlines with their dates; a fingerprint mark joins a shortlist to an approval and breaks when one line changes. *Tag: constructed sketch · plan.*

> Here is the plan. In JS4, the agent will write a plan before each run, check what it claims, and remember across days. In JS5, I will add an approval gate tied to the exact shortlist I saw, so if one posting changes, the old approval no longer counts. Then, for the final project, I will evaluate it on data I set aside, break it on purpose, and ask someone else to run it from my README.

### B20 · 17.2 s

**On screen:** Three board boxes feed one line into a laptop; a Python file and a university Claude Code card land on the laptop; a coin labelled 'paid API' slides in and is crossed. *Tag: constructed sketch.*

> The data comes from the public job-board APIs of Databricks, Anthropic, and OpenAI, with a fictional candidate. I need no paid API and no token credits. It is plain Python, with nothing to install, and I use Claude Code, which my university provides, to help me write code that I review.

## Part 4 — Evaluation: how I will know it did a good job

### B21 · 16.3 s

**On screen:** A deck of posting cards splits: most go to a 'development' tray, some are sealed in a 'held-out' box; a few cards get a terracotta 'relevant' dot; a grey card reads 'JS1: 25 of 25 not relevant'. *Tag: constructed sketch · plan.*

> How will I know it did a good job? Before I tune anything, I will set aside a held-out set of postings and label them myself, including jobs I think are relevant. In JS1, all twenty-five of my labels were not relevant, so I could not count missed jobs. My reviewer pointed that out, and I will fix it.

### B22 · 17.1 s

**On screen:** Three measure gauges appear; then five failure cards drop one by one into a net, and each is caught with a check. *Tag: constructed sketch · plan.*

> I will measure how many relevant jobs it misses, how many wrong jobs it keeps, and whether every decision has a reason. And I will test at least five failures on purpose: a board that does not exist, a removed posting, a job outside the US, too much experience required, and a job that only matches keywords.

### B23 · 16.0 s

**On screen:** Two columns: under 'worked if' four checks land in turn; under 'did not work if' two crosses land. *Tag: constructed sketch · plan.*

> It worked if no relevant job is silently rejected, every decision has a reason, the recount agrees, and nothing reaches the shortlist without my approval. It did not work if a relevant job is rejected without a reason, or if an old approval is accepted for a changed shortlist.

## Close

### BOUT · 6.0 s

**On screen:** The three board boxes settle small above the title; the title and 'Yash Saraf' sit under them; one terracotta dot lands.

> A job-search agent you can check. A final project film, by Yash Saraf.

**Total narration: 322.4 s (5 min 22 s).**

## What is completed and what is planned

| Status | What |
|---|---|
| **Completed, with evidence** | JS1 watcher (77 tests, two live runs); JS2 loop, policy and independent check (65 tests, two live runs, three planted bugs caught); the comparison of LinkedIn, Jobright and Claude (10 screenshots, 2026-11-23) |
| **In progress** | JS3 filter (63 tests, first run 2026-11-18, due 2026-11-23) |
| **Planned** | JS4 plan, verification and memory; JS5 approval gate, register and supervised run; the held-out evaluation, five deliberate failures, the stranger run and the final demo |
