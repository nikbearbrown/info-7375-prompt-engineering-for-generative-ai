# FRICTIONAL — Job-Search Agent 1: The Contract and the Watch

Dated entries, written as the work happened. Times are local (America/New_York).

Each entry says what I tried, what happened, what I accepted, changed, or rejected from Claude, and the commit, prompt, or test it traces to. This log summarizes my Claude Code sessions. It does not paste transcripts: those stay on my machine, as the brief's privacy rules require.

## 2026-10-28 — Read the brief, started this log
- Pasted the JS1 brief into Claude Code and asked: "tell me what you understand from this assignment, and also start a new frictional md to keep track of conversation."
- Claude found my course folder (`fall-2026/atharva-h/`), created `js1-contract-and-watch/`, and started this file in the same format as my final-project-film log.
- Folder choice: the repo's `AGENTS.md` says assignment implementations go in `learning-artifacts/`, but the brief names `fall-2026/first-name-last-initial/js1-contract-and-watch/`. I'm following the brief, which matches where my earlier assignments live.
- Nothing is built yet: no `CONTRACT.md`, no code, no fetch has run.
- Deadline: Saturday 2026-10-31, 11:59 pm ET. A real second-calendar-day run needs the baseline run by 2026-10-30 at the latest.
- Still to decide: which board and host, which persona résumé, and how the Claude judge is called.

## 2026-10-28 — Contract interview, part 1: what goes in
- I chose to be interviewed for `CONTRACT.md` instead of drafting it alone. Claude asks one section at a time, and the answers are mine.
- **Persona.** None of the four fictional personas in the Reallocation Engine's `search/examples/` targets Data Analyst work: Aarav Patel is backend SWE, Maya Sehgal is AI PM, Priya Nair is AI/ML engineering, Rohan Desai is full-stack. I decided to invent one instead:
  - targets Data Analyst, BI Analyst, and Business/Analytics Analyst titles
  - 0–2 years of experience, new MS grad
  - any US location, including remote
  - needs H-1B sponsorship

  The persona JSON isn't written yet.
- **Claude judge.** It will run through `claude -p`: headless, no API key, and every call is a fresh conversation. I chose this over the Anthropic API.
- **Board.** I asked Claude to shortlist from my `h1b_entry_level_data_employers.xlsx`. It probed the public Greenhouse, Lever, and Ashby endpoints for 34 employer slugs and shortlisted 4 public boards with data roles:
  - Abacus Insights (Greenhouse, 22 jobs)
  - Duolingo (Greenhouse, 59 jobs)
  - Beyond Finance (Greenhouse, 25 jobs)
  - Xsolla (Lever, 190 jobs, mostly outside the US)

  I picked Abacus Insights: `boards-api.greenhouse.io`, token `abacusinsights`. It matches "Abacus Insights, Inc." on my list by name, but I haven't confirmed it's the same legal entity.
- These probes ran **before** the contract existed. They were not agent runs, nothing from them was saved, and none of it is evidence. The failure sentence is still unwritten.
- **Churn.** Each shortlisted board had only 2–4 postings dated in the last 7 days, so a real second-day change isn't guaranteed. A seeded second run may be needed.
- **Seen before the rule.** Claude listed all 22 Abacus titles. Under my persona, at most one ("Payer Analytics Consultant") looks plausibly relevant; the rest fail on seniority, title, or location. I saw these titles before writing my labeling rule.
- **Open question.** If all 20 labels come from Abacus, about 95% will be "not relevant," and a prompt that always says no would look excellent. I haven't decided where the 20 labels come from.
- The session was interrupted mid-question and resumed on 2026-10-29.

## 2026-10-29 — Contract interview, part 2: what comes out
- **Label pool.** The 20 hand-labeled postings will come from Abacus plus other Greenhouse boards on my H-1B list. That's the same allowed host, and it keeps the label set from being ~95% "not relevant." The watch itself still reads only Abacus.
- **Verdicts.** A verdict can be `relevant`, `not_relevant`, or `needs_human`. That's one more value than the brief's "relevant or not": a case the rule can't decide gets flagged instead of forced.
- **Scoring.** In the prompt experiment, pass rate covers only the cases where Claude committed to an answer, and it's always reported next to coverage (decided out of total). The trade-off I noted when choosing: a prompt that abstains often looks more accurate, so the two numbers have to be read together.
- **Justifications.** Each one must cite at least one résumé field path and one posting field, each with the value it read. The validator rejects a cite to a field that doesn't exist or a value that isn't there.
- Started `CONTRACT.md` with the In, Out, and Refuses sections. The rule, the wrong versions, and the failure sentence are still blank.

## 2026-10-31 — Contract finished; the Claude CLI isn't logged in
- **Contract.** I gave Claude my rule (seven checks), two wrong versions, and the dated failure sentence as pasted text. Claude copied them into `CONTRACT.md` word for word.
- **Title conflict.** Claude flagged that my rule's title list includes "Data Engineer" and "Analytics Engineer," while the persona in the In section targets analyst titles only. I decided the persona wins, and I'll remove those two titles from the rule myself.
- **Mechanical readings.** The code needs a mechanical way to apply my location, sponsorship, and experience checks. Claude proposed phrase lists and I accepted them. They're Claude's operationalization of my rule, kept apart from my own wording and documented in `README.md`.
- **CLI not logged in.** There's no `claude` on my PATH. The copy bundled with the desktop app (2.1.309) exists but returned "Not logged in · Please run /login". I chose not to log in. Claude's verdicts for this assignment will come from fresh Claude Code subagents, and they'll be labeled that way. The `claude -p` path stays in the code for a TA with a logged-in CLI, but it wasn't exercised.
- **Seeded second run.** The baseline never ran on 10-29 or 10-30, so a real second-calendar-day run would land after the deadline. The second run will be seeded and labeled as seeded.
- **Commit.** I committed `CONTRACT.md` and this log on branch `js1-contract-and-watch` before any agent code was written.
