# PROJECT-BRIEF — Early Bird

**Vrajesh N. · INFO 7375 · Fall 2026 · written 2026-10-14**
Target role: **full-stack software engineer / AI engineer.** Stack: **Python 3.13 (standard library first) + Claude API.**
Status: **proposed.** Only the one-off probe in `evidence/` has run (2026-10-14). Everything else below is future tense.

## 1. What is it?
Early Bird **will be** a small Python agent that, each time I run it, checks the public job boards of the 25–30 companies on my list and reports only the **new** software, full-stack and AI postings since the last run, with any hard blocker quoted from the posting and the GitHub project of mine that best fits each one.
**Artifact:** a public GitHub repository: a Python CLI (`python -m earlybird run`), tests, dated raw board responses, a state file and one Markdown report per run, grown across JS1–JS5 into the final project.

## 2. Why would anyone care?
In a tight market I want to apply to **every** software role I can reach, and early. What I examined:
- **The course's own `greenhouse-watch` skill** (Reallocation Engine, read 2026-10-14): watches **one** Greenhouse, Ashby or SmartRecruiters board per run, reports new postings, and keeps only those whose résumé-keyword score passes a threshold. In its Figma demo, 11 new postings in four days produced **0** kept, and its README itself notes the keyword scheme misses roles a person would want.
- **LinkedIn job alerts / Job Match**: compares a profile with a posting's qualifications, inside LinkedIn. It only covers what is posted on LinkedIn, and I cannot re-run or inspect how it decided.

**Difference:** Early Bird watches **my whole list** (25–30 boards, adding Lever) in one bounded run with a status per board; it **keeps every software, full-stack and AI posting** instead of scoring skill gaps away, and only flags hard blockers, each quoted from the posting and checked by code; it names which of my real GitHub projects fits; it never applies or messages anyone. `greenhouse-watch` will also serve as an **independent check**: same saved snapshot, compare its new-posting list with mine. I do **not** yet know whether Early Bird sees postings earlier than LinkedIn alerts; I will log when each source first shows the same postings (JS2).

## 3. Who opens it, and what do they do?
**Reader:** a hiring manager for a full-stack or AI-engineer role. In the first 60 seconds they will read the README's one-paragraph summary, run `python -m earlybird run --fixtures` (offline, seeded data, labeled), and open the report it writes: new postings, quoted blockers, the tests that passed. **User:** me, before each application session.

## 4. What does it prove about me?
| Course topic | Planned evidence |
|---|---|
| Prompt contracts | Claude returns a fixed JSON schema; a validator rejects anything else (JS1 tests) |
| Verification | a rule **record** anyone can recompute beside a labeled Claude **judgment**; quotes checked against posting text |
| Agent loops | budgets, explicit exits (finished / incomplete / budget-exhausted / error), one deliberate board failure (JS2) |
| Evaluation | 20 hand-labeled postings, 10 held out; a 30-posting reject audit (JS1, JS3) |
| Source grounding | every claim labeled supported / contradicted / insufficient; every remembered fact carries its source file (JS3, JS4) |

## 5. What is in, out, and first?
**In:** public Greenhouse, Lever and Ashby boards; new-posting detection; quoted blockers; project matching; an ordered list (referral, then freshness, then fit) I approve.
**Out (deliberate):** auto-applying, logging in, messaging, and scraping LinkedIn. Companies on their own hiring systems (e.g. Google, Amazon) will be listed as **unsupported**, not guessed at.
**First:** the watcher on one board (Commure, Ashby). **How to verify it ran:** run 1 saves the raw response and reports zero new (baseline); a second run on a later calendar day reports only IDs absent from run 1, and anyone can recompute that list by diffing the two saved raw files.

## 6. What could sink it?
**Keyword matching sends me the wrong jobs.** Today's probe matched 789 of 2,156 titles across five boards with a naive keyword rule, and the matches include sales roles such as "Account Executive, AI Sales" (Stripe). If the filter trusts words, the report fills with noise and I stop reading it. **Mitigation:** write the relevance rule before the code, hand-label 20 real postings (10 held out), audit 30 random rejects, and let Claude judge only with a quote the validator can find in the posting.
Second risk, already met once: **board access differs by platform.** Ashby returned HTTP 403 to Python's default user agent today; sending an identifying user agent fixed it. Each board gets its own failure status, never a silent "no new jobs."

## 7. Why this project?
**Existing skills, with evidence:**
- Python/FastAPI services with PostgreSQL: my public `Market-Data-Service` repo; full-stack engineer role at Duma Info Services (2023–24, on my resume).
- Filtering job listings: my public `Screenr` Chrome extension (last commit 2026-04-02) hides reposted listings and scores a resume against a description.
- Agents and tool use: my public `cli_project` (MCP chat on the Anthropic API); as a software engineer intern at Wave Life Sciences (2026) I built an AI assistant with FastAPI and LangGraph and testing agents in Claude Code (resume; that code is private).
- Ranking against criteria: a lender-matching ranking algorithm at Duma Info Services (resume).

**New for me:** writing the contract and tests *before* the code, held-out evaluation, permission policy enforced in code, versioned memory that rejects stale writes, and an approval gate bound to the exact list I reviewed. **Why it matters:** I graduate in December 2026 and I am job hunting now; I will be the first user.

---
**Exists today (2026-10-14)**
- `evidence/probe.py` and `evidence/2026-10-14/`: one run against five public boards (Commure, Stripe, Figma, Databricks, Palantir; example companies, not my private list). Raw responses + `summary.json`.
- Public repos: `Screenr`, `Market-Data-Service`, `cli_project`, `ai-study-assistant`.

**Will exist**
- Early Bird agent, contract, tests, fixtures, reports (JS1–JS5, final project, Dec 20 2026).
- Lag measurement vs LinkedIn alerts (JS2). Private, local-only LinkedIn connections lookup with a synthetic public demo (final project).
