# SCRIPT — Early Bird pitch film (v1.0, 2026-10-24)

Rebuilt from scratch after grading. **Drafted with Claude from my decisions and my own runs; I approved v1.0.** After approval, Claude shortened B03, B06 and B07 to stay under four minutes and corrected one B02 line after a department check (FACTCHECK #8); the text below is what is voiced.

Every number comes from files I ran or saved: `evidence/commure-new-ids-2026-10-14_to_2026-10-23.txt` (my ID diff, 2026-10-24), `evidence/gw/` (my greenhouse-watch runs, 2026-10-24), `evidence/2026-10-14/summary.json` (probe). Tense rule: past tense only for things that exist; *will* for everything planned.

Spoken respellings for Kokoro (in `build_beats.py`): *Info seventy-three seventy-five* = INFO 7375, *Kuh-mure* = Commure, *I Ds* = IDs, *S Q L* = SQL, *Screener* = Screenr, *Fast A P I* = FastAPI, *Lang Graph* = LangGraph. Voice: Kokoro `am_onyx`, local.

## B00 · OPEN
> Hi, I'm Vrajesh, and this is my final project pitch for INFO 7375. I drafted this script with Claude from my own decisions, and a synthetic voice reads it. I graduate in December, and I'm job hunting right now. In this market, I don't want to skip a single software job. I want to see every new one, early.

## B01 · WHAT (Q1) · PLANNED
> My project is Early Bird, a small Python agent I will build. Each time I run it, it will check the public job boards of the twenty-five to thirty companies on my list, and report only the software, full-stack and AI postings that are new since the last run. The finished artifact will be a public GitHub repository: a command-line tool, its tests, the saved board responses, and one report per run.

## B02 · EXISTS TODAY · REAL
> The agent doesn't exist yet. What exists is real data. I saved Commure's public job board twice: on October fourteenth, and again on October twenty-third. Eighty postings, then eighty-one. I compared the posting IDs: twelve were new, and eleven were gone. Five of the twelve new ones were software engineering roles. Seven were not software: sales, marketing, design, and one partnerships role.

## B03 · WHY (Q2) · REAL run + PLANNED difference
> The closest alternative is the course's own greenhouse-watch. I ran it myself on the same two snapshots, with the course's sample resume. It found the same twelve new postings, and kept all five software roles. But it also kept Head of Performance Creative, a marketing job, because the posting mentions Python and SQL. It watches one board per run, and keeps what passes a resume-word score. LinkedIn's Job Match only covers LinkedIn jobs, and I can't re-run how it decided. Early Bird will watch my whole list in one run, decide what counts as a software job from the role itself, not resume overlap, and keep every one, flagging only hard blockers, quoting the line from the posting.

## B04 · WHO (Q3) · CONSTRUCTED
> Who will open it? A hiring manager for a full-stack or AI engineering role. In the first sixty seconds, they will run one command on labeled sample data, and open the report: new postings, quoted blockers, and the tests that passed. The other user will be me, before every application session.

## B05 · PROVES (Q4) · PLANNED
> What will it prove about me? Prompt contracts: Claude will have to answer in a fixed format, and a validator will reject anything else. Verification: a rule anyone can recompute, next to a labeled Claude judgment. Agent loops, with budgets and honest exit statuses. And evaluation: twenty postings I will label by hand, with ten held back for the final test.

## B06 · SCOPE (Q5) · REAL answer key + PLANNED watcher
> What's out, on purpose: auto-applying, logging in, messaging anyone, and scraping LinkedIn. Companies on their own hiring systems, like Google, will be marked unsupported. The first piece I'll make run is the watcher on Commure, and its check already has an answer key: the twelve new IDs from my two saved files. The watcher will have to report exactly those twelve, and my greenhouse-watch run is a second, independent list.

## B07 · RISK (Q6) · REAL examples
> What could break it? Deciding what counts as a software job. Words mislead both ways. Sales Strategy and Operations, Agents, is a sales job. greenhouse-watch kept a marketing role because the posting said Python. And across five boards, my probe's keyword rule matched seven hundred eighty-nine titles, including Account Executive, AI Sales, at Stripe. So I'll write the rule before the code, hand-label real postings, audit thirty random rejects, and only accept a Claude verdict that quotes the posting.

## B08 · WHY ME (Q7) · REAL evidence
> Why this project? Some skills I already have. I've built Python and FastAPI services, at Duma Info Services and in my public Market Data Service repo. I built Screenr, a Chrome extension that filters reposted job listings. And as a software engineer intern at Wave Life Sciences, I built an AI assistant with LangGraph, and testing agents in Claude Code. What's new for me is the discipline: contracts and tests before code, held-out evaluation, permissions enforced in code, and a human approval gate before anything moves.

## B09 · OUTRO
> Early Bird won't apply for me. It will make sure I see every new software job, early, with the evidence in front of me. Then I apply. This was Vrajesh. The script was drafted with Claude from my decisions, and read by a synthetic voice.
