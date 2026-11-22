# Appendix — Fine Print: the detail behind the film

INFO 7375 · Final Project Film · Suketh Reddy Produtoor

*Drafted by Claude Code on 2026-11-21 from the records in [FACTCHECK.md](FACTCHECK.md); the student approved it with the film
on 2026-11-21. The brief asks to keep the detail "here and in your appendix, never in the executive summary". The film's Part 3
and Part 4 are the short version of §4–§8.*

## 1. In one paragraph

Fine Print is an agent, being built for the Final Project (due Dec 20), that reads new-grad machine-learning job
postings for an international student who needs sponsorship. For every requirement that could rule the applicant out, it
will show the posting's exact sentence, checked by code to be really in the posting. It will keep required, preferred
and either/or requirements apart, and mark sponsorship as "unknown" when the posting is silent. Nothing reaches the
shortlist until the student approves it. One piece, the watcher (**jobwatch**), already runs. The piece that
reads postings is built next, through the course's JS3–JS5 assignments.

## 2. What exists today and what doesn't

| | Status | Evidence |
|---|---|---|
| jobwatch: a bounded loop over three public boards, saving raw responses before reading them, with a permission policy enforced in code and approval-gated state | **runs** (164 tests OK on a fresh clone, 2026-11-21) | [tests](evidence/terminal/tests-2026-11-21.txt) |
| A live run on Nov 21, 13.5 days after the Nov 8 baseline: 635 / 895 / 32 postings; 83 / 88 / 1 new (172) | **ran** | [run](evidence/terminal/film-normal-noapproval-2026-11-21.txt) |
| JS1's literal word rule for the fictional persona (Alex Morgan): 172 of 172 new postings `not_relevant`, 0 `relevant` | **ran** | [count](evidence/terminal/film-rule-count-2026-11-21.txt), [relevant](evidence/terminal/film-rule-relevant-2026-11-21.txt) |
| The state is not saved without the student's approval (`incomplete`, state unchanged, independent check PASS) | **ran** | [run](evidence/terminal/film-normal-noapproval-2026-11-21.txt), [check](evidence/terminal/film-normal-noapproval-check-2026-11-21.txt) |
| The student's own approved run on Nov 8 (`finished`, state saved) | **ran** | [log](evidence/terminal/2026-11-08-normal-1-run-by-student.txt) |
| A Claude judge reading postings through the student's Claude Code login (JS1, 27 postings on Oct 31) | **ran** (JS1) | fork `99a7443`, `js1-contract-and-watch/README.md` "What ran" |
| The reader: requirement extraction with quotes, the quote check, required / preferred / either-or, sponsorship "unknown", the comparison with the applicant's background | **not built** | — |
| The evaluation set, the labels, the deliberate failures and the controlled failure | **not built** | — |

## 3. What changed since the October pitch

The pitch (Oct 14) planned to build the reader first: one loop over one public posting, with a quote check. The course
then assigned the job-search agent in layers (JS1 "The Contract and the Watch", JS2 "The Loop, the Tools, and the
Diff"), and those built the watcher first. The project is the same; the order changed. The pitch brief allows a project
to change if the change is logged in `FRICTIONAL.md`. The student's own account of the change is in
[FRICTIONAL.md](FRICTIONAL.md), Entry 1.

## 4. Data

| Source | Endpoint (from `jobwatch/boards.py`) | Label |
|---|---|---|
| Anthropic jobs (Greenhouse) | `GET https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` | public |
| Databricks jobs (Greenhouse) | `GET https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true` | public |
| Linear jobs (Ashby) | `GET https://api.ashbyhq.com/posting-api/job-board/linear` | public |
| Failure control (a board that doesn't exist) | `GET https://boards-api.greenhouse.io/v1/boards/jobwatch-no-such-board-js2/jobs?content=true` | public (expected 404) |
| The applicant | `persona/alex_morgan.json` | synthetic (fictional) |
| The student's own background | never in the repository | personal: stays on the student's machine |

- **How each response is handled.** It is saved byte for byte, with its SHA-256, before anything reads it. That lets
  `python3 -m jobwatch verify <run>` and the independent check recount from the saved body.
- **Limits on reading.** HTTPS GET only, no redirects followed, no retries. Budgets are 4 boards, 4 requests, 30 s per
  run and 5 s per request (`jobwatch/loop.py`, `Budget`).
- **Postings.** For the reader, postings come from the same public boards, together with others that answered the Nov 8
  probe with HTTP 200 (Greenhouse: Stripe, Figma, HubSpot (`hubspotjobs`), Miro (`realtimeboardglobal`); Ashby:
  OpenAI, Notion). The probe's record is JS2's `evidence/probes/2026-11-08-board-probe.txt`. Adding a board is a dated
  change to the allow-list.

## 5. How it works (target design)

1. **Watch** *(runs).* Fetch each allowed board once, save the raw body, and find posting ids not in the saved state.
2. **Screen** *(runs, crude).* JS1's literal rule. On Nov 21 it rejected all 172 new postings, and the rule cannot say
   whether that was right.
3. **Read** *(JS3).* For each posting, every claim about it is labelled supported, contradicted or insufficient against
   the posting's own text, or "I cannot tell". The model call goes through the student's Claude Code login.
4. **Check** *(JS4).* Every quoted sentence must appear word for word in the saved raw posting, and a test fails if one
   word changes. Each claim has a check that fails differently from the thing that made it.
5. **Remember** *(JS4).* The seen-postings state gets a version and a revision rule, shown with a two-day diff.
6. **Gate** *(JS5).* A shortlist is a proposal. The student's approval binds to a fingerprint of the exact proposal, so a
   changed shortlist can't ride on an old yes. The gate can refuse, defer or escalate.
7. **Never.** Fine Print never applies, emails, messages, logs in, or reads beyond the allow-list, and gives no legal or
   visa advice.

## 6. Step by step, with dates (Canvas)

| Due | Assignment | What it adds to Fine Print |
|---|---|---|
| Nov 25 | JS3 — The Filter, the Tool, and the Score | The filter written as a document (`FILTER.md`, by the student, before any build). A reject audit of at least 30 random rejected postings, judged by hand. The source-grounded shortlist (supported / contradicted / insufficient). The agent offered to Claude as a tool. One change at a time, measured on held-out labels |
| Dec 1 | JS4 — The Plan, the Evidence, and the Memory | A reviewed plan before the run. A tool evidence matrix (the quote check). Memory with a revision rule and a two-day diff. A premortem |
| Dec 13 | JS5 — The Gate, the Register, and the Supervised Run | `APPROVAL.md` and the fingerprint-bound gate. `REGISTER.md` (data and people). The supervised run with a controlled failure. The ship / narrow / defer / stop decision |
| Dec 20 | Final Project — An Agentic System You Choose | The ten-document packet, the held-out evaluation, the stranger run, and a demo of at most five minutes |

## 7. Resources

| Need | Have it? | Evidence |
|---|---|---|
| Model access | Yes, the Claude Code login. No API credits | The student's answer, 2026-11-21. JS1's judge ran 27 calls this way on Oct 31 |
| Accounts for the boards | Not needed (public endpoints) | JS2 runs |
| Compute | A laptop (macOS, Python 3.12, standard library) | JS2 `README.md`; the Nov 21 runs |
| Time | JS3–JS5 deadlines, as in §6 | Canvas |
| Known limits | Boards can refuse automated reads (in A3, OpenAI's Ashby API returned 403), and such postings go to a person. Claude Code usage limits cap how much can be read per day, so reading gets a daily budget. Claude Code adds about 800 tokens of its own context to each `claude -p` call; the agent cannot inspect that context (JS1 `README.md`) | — |

## 8. Evaluation

- **Labels.** Real public postings, labelled by hand by the student. They include a random sample of the postings the
  word rule rejected, as JS3's reject audit requires.
- **Sets.** Development and held-out. The held-out set is set aside before any prompt, rule or threshold is tuned.
- **What is measured:**
  1. **Quote found:** each quoted sentence appears word for word in the saved posting, after whitespace normalization.
  2. **Misreads:** required, preferred or either-or recorded differently from the student's label.
  3. **Unsupported clearances:** a requirement marked as met without support in the applicant's documented background.
  4. **False exclusions:** a posting ruled out although the applicant qualifies.
  5. **Abstentions:** how often the reader says "I cannot tell".

  Unsupported clearances and false exclusions are counted apart, because they cost different things. The first wastes
  an application; the second loses a real opening.
- **Deliberate failure cases (at least five):**
  - a quote with one word changed;
  - "5+ years preferred" read as required;
  - an either/or pathway (for example a master's + 2–4 years, or a PhD + 0–2) read as one requirement;
  - a posting silent on sponsorship;
  - a board that answers 404 or 403;
  - a posting that matches keywords but does not support the claim.
- **The controlled failure.** Predicted now (the pitch's named risk): **a true quote read the wrong way**. The quote check
  passes, but the interpretation is wrong. It will be triggered on purpose with a seeded posting and caught by an
  independent check, the student's hand label. The recovery is reviewed by the student.
- **Success bar** (the student's own words, 2026-11-21, film beat B17):
  - It worked if at least 27 of 30 held-out decisions match my labels and my checks catch every deliberate failure.
  - It didn't work if the reader misquotes a posting, clears even one unmet requirement, or wrongly rules out more than
    one eligible posting, regardless of the overall score.
  - I'll label about 60 postings by hand, including 30 randomly picked rejects, and set 30 aside before tuning.
  - Why these thresholds, in the student's words, are in [FRICTIONAL.md](FRICTIONAL.md), Entry 2. Zero false
    clearances, because a wrong green light costs a tailored application; at most one wrong rejection, because one
    isolated miss can be reviewed against the posting, while a second would send the student back to the filter.
- **Honest limits.** A set of a few dozen postings can show where Fine Print fails. It cannot show that it works on every
  posting, every board, or every applicant.

## 9. Prior work (Part 2 of the film)

Each example was checked on its own page on 2026-11-21. Full notes, quotes and confidence levels are in
[evidence/prior-art/PRIOR-ART.md](evidence/prior-art/PRIOR-ART.md); the research was done by a Claude Code subagent.
"Not mentioned" means only that the pages read didn't mention it.

| Example | What it gives back | Closest to Fine Print, and what's different |
|---|---|---|
| USCIS H-1B Employer Data Hub (official) | Counts of first decisions on H-1B petitions, by employer and fiscal year | Sponsorship history per employer. Job title is not a query field, and nothing links to a posting |
| h1bdata.info (built on Labor Department LCA data) | One row per filing: employer, job title, salary, location | Per-title history. The site warns the data "does not indicate the employer's intended use for the LCA" |
| Jobscan (commercial) | A match rate and missing keywords for a résumé against a pasted posting. It highlights keywords in both; its Auto Apply has a review step | Highlighting and human review already exist. Required vs preferred, quote checking and sponsorship are not mentioned on the pages read |
| SkillSpan (NAACL 2022) | 14.5K job-posting sentences with over 12.5K skill spans, annotated by experts | Skill spans, not the requirements that rule an applicant out. No required/preferred label described |
| Nguyen et al. (NLP4HR 2024) | Prompted LLMs for skill extraction: "not on par" with supervised models | The models find skills but miss the exact wording, which is why Fine Print checks every quote with code |
| Thakrar & Young (arXiv 2025) | An LLM pipeline flagging whether experience and education are required or preferred | **Required vs preferred is not new.** Their output is structured fields, not quoted sentences. Medium confidence |

The film therefore claims only the combination, for one applicant's decision. Every requirement gets the posting's own
sentence, checked word for word by code, with required and preferred kept apart, sponsorship marked "unknown" when the
posting is silent, and a person's approval before the shortlist.

## 10. Evidence index

- `evidence/terminal/`: the exact captures from Nov 21 and the student's Nov 8 log, listed in its
  [README](evidence/terminal/README.md), with hashes in `SHA256SUMS`.
- `evidence/state-before-film-normal-noapproval.json` and `evidence/state-after-film-normal-noapproval.json`, which are
  identical.
- [FACTCHECK.md](FACTCHECK.md): every sentence in the film and its record.
- [SOURCES.md](SOURCES.md): who did what, and the licences.
