# SCRIPT — Early Bird pitch film (v0.2, 2026-10-14)

Narration exactly as synthesised. Spoken respellings for Kokoro: *Info seventy-three seventy-five* = INFO 7375, *Kuh-mure* = Commure, *Screener* = Screenr, *Fast A P I* = FastAPI, *Lang Graph* = LangGraph.

Measured narration: **218.16 s** (Kokoro `am_onyx`, local).

## B00 · OPEN · 16.1 s
*Cold open: who is speaking, the synthetic-voice disclosure, and the need in one breath.*

> Hi, I'm Vrajesh. This is my final project pitch for Info seventy-three seventy-five, read by a synthetic voice from my own script. I graduate in December, and I'm job hunting right now. In this market, I don't want to skip a single software job. I want to see every new one, early.

## B01 · WHAT · 20.5 s
*Q1. One sentence, then the artifact and its form.*

> My project is Early Bird, a small Python agent. Each time I run it, it checks the job boards of the twenty-five to thirty companies on my list, and reports only the software, full-stack and AI postings that are new since the last run. The finished artifact is a public GitHub repository: a command-line tool with its tests, the saved board responses, and one report per run.

## B02 · EXISTS · 17.3 s
*Exists today: the real probe run of 2026-10-14, numbers from evidence/2026-10-14/summary.json.*

> The agent doesn't exist yet. What exists is one probe I ran this morning, October fourteenth, against five public job boards: Kuh-mure, Stripe, Figma, Databricks and Palantir. These are example companies, not my private list. Two thousand one hundred fifty-six postings came back, and I saved every raw response.

## B03 · WHY · 34.6 s
*Q2. Two real alternatives examined (greenhouse-watch read 2026-10-14; LinkedIn Job Match from launch coverage) and the specific difference.*

> Two things already exist. The course's own greenhouse-watch tool watches one board at a time, and keeps only postings that match my resume keywords. In its demo, Figma posted eleven new jobs in four days, and it kept none. LinkedIn's Job Match compares my profile with a posting, but only for jobs on LinkedIn, and I can't re-run how it decided. Early Bird watches my whole list in one run. It keeps every software job, instead of scoring skill gaps away. It only flags hard blockers, like five years required, and it quotes the line, and code checks that the quote is really in the posting. It never applies for me.

## B04 · WHO · 16.0 s
*Q3. The reader, and their first sixty seconds. Output is CONSTRUCTED (nothing is built).*

> Who opens it? A hiring manager for a full-stack or AI engineering role. In the first sixty seconds, they run one command on labeled sample data, and open the report: new postings, quoted blockers, and the tests that passed. The other user is me, before every application session.

## B05 · PROVES · 18.6 s
*Q4. Course topics tied to the planned evidence for each.*

> What does it prove about me? Prompt contracts: Claude must answer in a fixed format, and a validator rejects anything else. Verification: a rule anyone can recompute, next to a labeled Claude judgment. Agent loops, with budgets and honest exit statuses. And evaluation: twenty postings I label by hand, with ten held back for the final test.

## B06 · SCOPE · 29.9 s
*Q5. One deliberate exclusion, the first piece that runs, and how to verify it.*

> What's out, on purpose: auto-applying, logging in, messaging anyone, and scraping LinkedIn. Companies on their own hiring systems, like Google, will be marked unsupported, not guessed at. The first piece I'll make run is the watcher on one board, Kuh-mure. Run one is a baseline and reports zero new. A later run reports only new posting IDs, and anyone can check that by comparing the two saved files. As a second, independent check, I'll run the course's greenhouse-watch on the same saved data, and compare our lists.

## B07 · RISK · 23.0 s
*Q6. One concrete, project-specific risk (real titles from evidence/2026-10-14) and the mitigation.*

> What could break it? Keeping every software job only works if software job is decided correctly. My probe's simple keyword rule matched seven hundred eighty-nine titles, and some of them are sales jobs, like Account Executive, AI Sales, at Stripe. If the report fills with noise, I'll stop reading it. So I'll write the rule before the code, hand-label real postings, audit thirty random rejects, and only accept a Claude verdict that quotes the posting.

## B08 · WHYME · 31.8 s
*Q7. Existing skills with real evidence (public repos, resume); new skills named honestly.*

> Why this project? Some skills I already have. I've built Python and Fast A P I services, at Duma Info Services and in my public Market Data Service repo. I built Screener, a Chrome extension that filters reposted job listings. And as a software engineer intern at Wave Life Sciences, I built an AI assistant with Lang Graph, and testing agents in Claude Code. What's new for me is the discipline: contracts and tests before code, held-out evaluation, permissions enforced in code, and a human approval gate before anything moves.

## B09 · OUTRO · 10.3 s
*Neutral student outro: title restated, no channel handle, voice disclosed again.*

> Early Bird won't apply for me. It makes sure I see every new job, early, with the evidence in front of me. Then I apply. This was Vrajesh, and this pitch was read by a synthetic voice.
