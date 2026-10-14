# Project brief — job-search agent

**1. What is it?** A job-search agent that will watch public job boards at retail and e-commerce
companies and tell a fictional international data-analytics graduate which new postings are worth
their time. It will cite the exact posting text and resume field behind every verdict, and it will
never apply or send anything. The artifact will be a GitHub repo with a Python agent, tests, an
evaluation log, the 10-document evidence packet, and a 5-minute demo.

**2. Why would anyone care?** I looked at two tools I had used: LinkedIn Job Alerts and Jobright.
LinkedIn Job Alerts emailed me new postings that matched a saved search, but it never told me why a
job fit me, or whether the posting said anything about sponsorship. Jobright went further: it gave a
match score, had an H-1B filter, and its AI Agent could submit applications for you. But a 2026
review (careery.pro) said its H-1B filter relied on sponsorship language or the employer's past
sponsorship history, and past sponsorship doesn't guarantee that a specific job will sponsor. My
agent will differ in three ways. (1) It will judge each posting by its own text: every claim such
as "sponsors visas" or "remote" will be labelled supported, contradicted, or insufficient, with the
exact line quoted. (2) When a posting is silent, it will say "insufficient" instead of guessing from
company history. (3) It will never apply: I will approve the shortlist, and nothing will be sent.
*Source note: the Jobright claim comes from a third-party review (careery.pro, 2026); it goes in
SOURCES.md.*

**3. Who opens it, and what do they do?** A hiring manager for data analyst, data scientist, or
analytics engineer roles. In 60 seconds they will open the README, run one command on saved board
data, and see the shortlist with citations, the skipped postings with reasons, and the evaluation
scorecard.

**4. What does it prove?** It will show: prompt contracts (a fixed schema plus a validator);
verification (a recomputable rule verdict beside Claude's judgment); an agent loop with budgets,
designed exits, and a stop condition that doesn't rely on the model saying it's done; tool
permissions enforced in code; versioned memory across days; a human approval gate tied to the exact
shortlist; and source grounding (supported/contradicted/insufficient). The evidence will be tests, a
held-out evaluation with at least 5 deliberate failure cases, a controlled failure that is predicted
and then triggered, and a stranger's run of the README.

**5. What is in, out, and first?** Out: it will never apply, email, message, or log in, and it will
do no LinkedIn scraping. First: one public board plus one fictional resume. The first run will be a
baseline that reports zero new postings; a later run will report only new ones. The proof that it
ran will be the saved raw board response and the state file.

**6. What could sink it?** Many postings never state sponsorship or pay, so the agent could look
confident with nothing behind it. The mitigation will be an "insufficient" label, an abstention
rule, and a measure of how often it abstains.

**7. Why this project?** It's a mix of showing off and learning. I bring Python, SQL, and data
analysis from almost two years as a Data Analyst at Deloitte and my Commercial & Marketing Analyst
co-op at Wayfair. In this course I already submitted two pieces you can open: my Week 1 explainer
film, built from a real Python script (PR #10), and my Reallocation Engine recipe and prototype
(PR #17). New to me will be: building an agent loop with budgets and exits, enforcing permission
rules in code instead of prompts, writing an MCP tool server from scratch, and running a held-out
evaluation that can actually say "no." Why I care: I will graduate in December, and I was already
job-searching when I chose this project. I learned how much time goes into reading postings that
turn out to be a bad fit. My real resume will stay private; the agent will run on a fictional persona.

## Exists today

- Brutalist setup, reused from Week 1; the smoke test passed on 2026-10-14.
- Week 1 explainer film, PR #10 (head commit `aad5723` on `nishant-u-week-01`).
- Reallocation Engine recipe and prototype, PR #17 (head commit `ddcecee`; recipe status DRAFT).
- Nothing of the job-search agent exists yet.

## Will exist

- A GitHub repo with the Python agent, an MCP tool server, and tests.
- An evaluation log and a held-out evaluation with at least 5 deliberate failure cases.
- A predicted and triggered controlled failure, and a stranger's run of the README.
- The 10-document evidence packet.
- A saved raw board response and state file from the first baseline run.
- A 5-minute demo.
