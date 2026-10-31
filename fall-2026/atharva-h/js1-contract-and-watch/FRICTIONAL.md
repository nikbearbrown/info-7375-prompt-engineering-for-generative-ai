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
- **Contract.** I asked an AI chat tool to draft answers to the seven rule questions, two wrong versions, and a failure sentence. I edited the title list and passed the draft to Claude Code, which copied it into `CONTRACT.md`.
- **Title conflict.** Claude Code flagged that the draft title list included "Data Engineer" and "Analytics Engineer," while the persona in the In section targeted analyst titles only. I decided the persona wins and later asked Claude Code to remove those two titles.
- **Mechanical readings.** The code needs a mechanical way to apply the location, sponsorship, and experience checks. Claude proposed phrase lists and I accepted them. They're Claude's operationalization of the written rule, documented in `README.md`.
- **CLI not logged in.** There's no `claude` on my PATH. The copy bundled with the desktop app (2.1.309) exists but returned "Not logged in · Please run /login". I chose not to log in. Claude's verdicts for this assignment will come from fresh Claude Code subagents, and they'll be labeled that way. The `claude -p` path stays in the code for a TA with a logged-in CLI, but it wasn't exercised.
- **Seeded second run.** The baseline never ran on 10-29 or 10-30, so a real second-calendar-day run would land after the deadline. The second run will be seeded and labeled as seeded.
- **Commit.** I committed `CONTRACT.md` and this log on branch `js1-contract-and-watch` before any agent code was written.

## 2026-10-31 — Build, tests, seeded baseline, label pool
- **Code.** After the contract commit (`963f9f1`), Claude wrote the fictional persona `persona/resume.json` (Riley Navarro, `@example.com`, 555 number), `persona.py`, `rule.py`, `judge.py`, `watch.py`, `seed.py`, the prompt `prompts/v1_baseline.txt`, and 43 `unittest` tests.
- **Bugs caught before the first test run.** Claude reviewed its own rule code and fixed three bugs:
  - "New Mexico" would have been read as Mexico (non-US).
  - "1–3 years" would have been read as a 3-year minimum.
  - "we offer visa sponsorship" wasn't recognized as an offer.
- **Tests.** All 43 passed on the first run. That includes mutant versions of both wrong versions in the contract, which the tests catch: the broad-title mutant turns "Payer Analytics Consultant" into `relevant`, and the silence mutant turns a silent posting into `not_relevant`.
- **A real change, but not evidence.** On 10-31 the live Abacus board had 18 postings; when Claude listed it on 10-28 it had 22. "Senior Business Intelligence Analyst (Healthcare)," first published 10-30, wasn't in the 10-28 list. Nothing from 10-28 was saved, so this can't count as evidence.
- **Seeded baseline.** `seed.py` fetched the board once, saved that response, and removed the 5 most recently first-published postings to make `runs/seed/earlier_response_SEEDED.json`. The baseline ran on that file, labeled `SEEDED-baseline`: 13 postings, 0 new.
- **Label pool, attempt 1.** The first five Greenhouse boards had 403 postings, and only 2 titles contained a target phrase, both Senior. Labeled as is, all 20 would have been `not_relevant`.
- **Label pool, attempt 2.** Claude probed Greenhouse for the 1,747 direct employers on my H-1B list and added 14 boards whose slug clearly matches the employer's name. Ambiguous slugs like `mercury`, `rga`, and `abc` were left out. The pool grew to 2,319 postings, 24 with a target phrase.
- **Selection.** I picked 20 by title tier (14 target-title, 4 near-miss, 2 other) with a fixed seed, then split them 10/10 at random. Selection never used the rule's verdicts.
- **Title edit.** At my request, Claude deleted "Data Engineer" and "Analytics Engineer" from rule item 1 and moved the "or" so the list still reads correctly. Nothing else in the rule changed. I decided to leave "Analytics Analyst" out, so Claude changed the In section's persona line to match the rule's four titles.
- **Waiting on me:** the 20 hand labels in `experiments/label_pool/LABELS.md`.

## 2026-10-31 — Second run, first Claude verdicts, sampling
- **Live second run.** `runs/2026-10-31T175126Z` fetched 18 postings and reported exactly the 5 that were seeded out as new. No previously seen posting was reported again. The rule judged all 5 `not_relevant`: four on seniority, one on title.
- **How Claude was asked.** Each Claude verdict came from a fresh Claude Code subagent (general-purpose, same model as this session). Each one read exactly one prompt file and wrote its raw answer to a file. Nothing touched those files afterward.
  - Run 2: 5 calls.
  - Development set with the v1 baseline prompt: 10 calls.
  - Sampling: 5 postings × 4 calls = 20.
- **Validator rejected every run-2 output.** All 5 of Claude's run-2 outputs were rejected, for one reason: path syntax. Claude wrote list positions as `targets.titles.0` and `offices.0.location`, while the validator only accepts `targets.titles[0]`. The prompt only said "dot path," so Claude's reading is reasonable. The prompt contract was underspecified. The validator did what the contract says: rejected the outputs and didn't repair them. Unvalidated, all 5 rejected outputs said `not_relevant`, same as the rule, but they don't count.
- **Same problem on the development set.** 5 of 10 v1 outputs were rejected, all for the same path syntax. Claude first told me "6 of 10" from a hand count; the validator's count is 5. I chose the v2 change after hearing "6," but the choice doesn't depend on which number is right.
- **Sampling.** All 20 runs gave the same verdict 4 out of 4 times for every posting, and 16 of 20 were rejected for path syntax, also 4 out of 4 per posting. The failure is systematic, not random. The Woolpert posting, which needed no list-index cites, validated all 4 times. Repetition shows the answers are repeatable, not that they're correct; correctness needs independent labels.

## 2026-10-31 — v2, held-out, action surfaces, replay
- **The one change.** I chose to make the prompt specify path syntax. `prompts/v2_path_syntax.txt` is v1 plus one sentence (`diff` shows a single changed line). The validator didn't change, so v1 and v2 are measured against the same yardstick.
- **Development set.** Invalid outputs dropped from 5/10 (v1) to 0/10 (v2).
- **A rule bug Claude's answer exposed.** On Artefact "Data Analyst" (Beirut, Lebanon), v2 Claude said `not_relevant` while the rule said `needs_human`. The cause was in the rule code: Claude's hand-picked country list didn't include Lebanon, so the place read as unknown.
  - **Fix:** Claude replaced the list with every country (Georgia left out, since the US state wins that collision).
  - **Tests added:** "Beirut, Lebanon" is non-US; "Lebanon, NH" is US.
  - **Check:** the saved rule verdicts in both recorded watch runs came out unchanged.
  - **Still open:** a city with no country, like "Bengaluru," still reads as unknown. I didn't add city names, because I had already seen the held-out titles and locations and didn't want to tune the rule to them.
- **Held-out.** Both prompts ran on the held-out 10 only after development was done. Invalid outputs: v1 7/10, v2 0/10. Correctness scores wait on my labels.
  - One v2 held-out judge (posting 6220813004) made 4 tool calls instead of the expected 3. Its answer file looks normal, but I can't see what the extra call was.
  - Two of the replay judges also made 4 calls.
- **Action surfaces.** I ran the same posting (Point72 "Technical Business Analyst") three ways. All three said `needs_human`.
  - **Chat paste (no tools):** 1 call (the hand-back only), about 7 s. Claude's session copied the reply into `answer.txt` verbatim.
  - **File read:** 3 calls, about 12 s.
  - **Agent fetch and state:** 10 calls, about 73 s.
    - It ran `curl` and `python3` in the shell; one `curl` failed on zsh quoting and it retried.
    - It wrote only the two files it was told to; Claude checked `state.json` (206 ids) against `raw.json` (206 jobs).
    - Its allow-list was an instruction, not code.
- **Production prompt and replay.**
  - `watch.py` now uses v2.
  - Run 2 stays as recorded under v1, with 5/5 rejected.
  - An offline replay (`--state state/replay_seen_ids.json`, seeded file first, then run 2's saved raw response) reported the same 5 new postings. With v2, all 5 Claude outputs validated, and all 5 agree with the rule.

## 2026-10-31 — Labels and test check
- **Labels.** An AI chat tool filled the 20 labels from `CONTRACT.md`: 19 `not_relevant`, one `needs_human`, and zero `relevant`. I reviewed the table of labels and deciding checks in chat and replied "looks good."
- **Tests.** The requested `python3 -m unittest discover -s tests` command ran on 2026-10-31: 43 tests, `OK`. Python also emitted ResourceWarnings for unclosed files in `tests/test_watch.py`.
- **Scores.** The sampling result and four prompt score files were recomputed from the saved answers; the counts are in `SAMPLING.md` and `PROMPT_EXPERIMENT.md`.
