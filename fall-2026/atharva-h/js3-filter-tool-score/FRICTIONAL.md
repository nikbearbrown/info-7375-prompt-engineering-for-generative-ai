# FRICTIONAL — Job-Search Agent 3: The Filter, the Tool, and the Score

Dated entries, written as the work happened. Times are local (America/New_York).

Each entry says what I tried, what happened, what I accepted, changed, or rejected from Claude, and the commit, prompt, or test it traces to. This log summarizes my Claude Code sessions. It does not paste transcripts: those stay on my machine, as the brief's privacy rules require.

## 2026-11-17 — Read the brief, started this log
- Pasted the JS3 brief into Claude Code and asked for its reading of the assignment and the next steps.
- **Where JS2 ended:**
  - Submitted 2026-11-10 as branch `atharva-h/js2-loop-tools-diff`, commit `41ae85c`, in `fall-2026/atharva-h/js2-loop-tools-diff/`.
  - It watches Abacus Insights (Greenhouse), Valon (Ashby), and Xsolla (Lever), plus one board misspelled on purpose (`valonn`), and reports new and closed posting ids.
  - It does no judging. Python standard library only, 56 tests.
- **What Claude created:**
  - the local branch `js3-filter-tool-score`, cut from `41ae85c`
  - this folder, `js3-filter-tool-score/`
  - this log
  - a `FILTER.md` with only the section headings the brief asks for, plus a version history
  - a `.gitignore` copied from JS2
- **A check before the interview** (not an agent run, and nothing was saved):
  - JS2's day-2 saved responses hold 233 postings.
  - Only 3 titles contain "analyst", and 2 of those are senior.
  - For the fictional persona Riley Navarro (entry-level data or BI analyst), JS2's boards have almost no relevant postings. That is the problem the JS1 grading flagged ("real relevant cases"), so the board choice comes first.
- **Lectern:**
  - Its watch list (`sources.json` on `main`, probed 2026-09-26) is aimed at education and AI-advocate roles at AI companies, so its boards don't fit this persona.
  - Its idea of a filter as a document, with every added, cut, or rejected word recorded and measured, could still shape `FILTER.md`.
- **Nothing built yet:** no filter content, no code, no labels, no runs.
- **Due:** Monday 2026-11-23, 11:59 pm ET.
- **Still to decide:** the interview answers (starting point, boards, filter rules, evidence rules, labels, Claude's role, the tool server, and what to change and measure).

## 2026-11-17 — FILTER.md interview and board probe
- **The interview.** Claude gave all 25 `FILTER.md` questions as one list, with options and a recommendation for each. I chose:
  - **Inputs:** start from my JS2 code, with Lectern's changelog style. Keep Riley Navarro. Freeze one fresh collection as the corpus. Read full posting text.
  - **Rules:**
    - a two-valued keep/reject from a score and a threshold
    - reject rules for seniority, more than 2 required years, non-US locations, and a stated refusal to sponsor
    - points for role phrases in the title and Riley's tools in the description
  - **Evidence:** "supported" needs an exact quoted span.
  - **Wrong versions:** substring matching, and a title-only filter.
  - **Measurement:**
    - seeded labels (60 random plus every "analyst" title), split 2:1 into tuning and held-out
    - an audit of 30 random rejects, 10 near the threshold, and 10 kept
    - one change at a time, measured on held-out labels
  - **Claude's part:** Claude writes the claims and does not decide keep or reject.
  - **Tool server:** one read-only `score_posting` tool over MCP on stdio.
- **The board probe** (not an agent run, and nothing was saved):
  - **What was read:** to choose boards with real relevant cases, Claude read 30 boards' public job lists, one GET each, across Greenhouse, Ashby, and Lever.
  - **What it found:**
    - US entry-level data or BI analyst titles were rare. Cloudflare's "Data Analyst" was the clearest.
    - Most "analyst" titles were compliance, tax, fraud, credit, or operations jobs, so a bare "analyst" is likely a false friend.
    - Six slugs returned 404: `draftkings`, `nerdwallet`, `grammarly`, `thumbtack`, and `wayfair` on Greenhouse, and `plaid` on Lever. Two boards returned 0 postings: Ashby `mercury` and Lever `whoop`.
  - **The proposed 10 boards:** JS2's three plus Cloudflare, HelloFresh, Affirm, MongoDB, Gusto, Ramp, and Palantir.
- **Response sizes:** with full descriptions, Cloudflare was 8.5 MB and Palantir 5.8 MB. Both are over JS2's 5 MB approval limit, so the collection run will need my "y" at a real terminal.
- **What Claude flagged in its own recommendation:** "I cannot tell" whenever any required claim is insufficient would abstain on almost every posting, because few postings mention sponsorship. The draft narrows it: abstain when role, seniority, or location is insufficient, or the description is missing. Years and sponsorship reject only when contradicted. This waits for my review.
- **`FILTER.md` v1.0** was drafted from these answers and is not committed yet.

## 2026-11-18 — Boards re-chosen by a fixed rule
- **My proposal:** probe about 100 boards, then keep about 30: mostly boards with relevant postings, plus a few without, so the filter is shown handling both.
- **What Claude added before running it:**
  - The selection rule had to be fixed before any result was seen, so boards couldn't be cherry-picked:
    - A relevant title has a role phrase, no seniority word, and a US-looking location.
    - Up to 22 relevant boards are kept.
    - The contrast boards are JS2's three plus the 5 with the most bare "analyst" titles.
  - A corpus picked this way describes these boards, not the job market.
- **The probe** (`probe/probe_boards.py`, results in `probe/2026-11-18_board_probe.json`):
  - It read 116 candidate boards, one GET each. 87 answered and 29 returned 404.
  - **Only 4 of the 87 had any relevant title:** Stripe (4), Veeva (2), Zoox (1), and SeatGeek (1).
  - So the rule gave 12 boards, not 30, with 4,123 postings.
  - Cloudflare's "Data Analyst" from 11-17 no longer counted. Its location is just "Hybrid".
- **The probe's own false friend:** Veeva's "Israel - Kiryat Ono IL" matched the US check, because "IL" is also the Illinois code. Veeva still has one real US match (New York).
- **What changed in the draft:**
  - The 12 boards replace the 10 from 11-17.
  - The budget is now 15 boards, 35 requests, and 180 s.
  - Raw responses are saved gzip-compressed, because the estimated 60 MB uncompressed is too much for the shared course repo.
  - Labels are now every role-phrase title, plus 30 random bare-"analyst" titles and 40 random others, instead of every "analyst" title (about 130).
  - The reject audit is drawn only from outside the held-out set.
- This waits for my review before it is committed.
- **2026-11-20:** I accepted the 12 boards the rule picked, rather than probing another batch.

## 2026-11-20 — FILTER.md approved and committed before any code
- **I approved `FILTER.md` v1.0, including the two places it differs from my interview answers:**
  - **The narrower "I cannot tell" rule.** The agent abstains on role, seniority, location, or a missing description. Years and sponsorship reject only when contradicted.
  - **The capped label sample.** Every role-phrase title, plus 30 random bare-"analyst" titles and 40 random others.
- **What was committed:** `FILTER.md`, this log, `.gitignore`, and the board probe (`probe/`), all before any filter, scorer, or tool-server code existed.

## 2026-11-20 — Collector, frozen corpus, label sheet
- **What Claude built, starting from my JS2 code:**
  - The adapters now keep each posting's full description as plain text, plus department, every location, country, and workplace where the system gives them (`text.py`, `adapters.py`).
  - Raw 200 responses are saved gzip-compressed.
  - The budget is FILTER.md's: 15 boards, 35 requests, 180 s.
  - A run's summary keeps no posting text.
- **Tests: 62, all passing.**
  - 49 were carried over from JS2. Two changes there: the raw file name is now `.json.gz`, and the board-budget test uses 16 boards instead of 6.
  - 13 are new (`tests/test_collect.py`): the text parsing for each system, the gzip round trip, the frozen corpus, and checks that the code's numbers match FILTER.md.
- **Identity names.** Before the run, Claude read the 7 Greenhouse boards' own names (7 small GETs) and used them as the configured employers, so the identity check could pass.
- **Live collection** (`runs/2026-11-20T131355Z_corpus`):
  - Exit `finished`: 19 requests in 30.2 s, all 12 boards ok, 4,102 postings.
  - The raw responses were 53.5 MB and are stored as 5.0 MB. The largest file is 0.97 MB, so no write needed my approval.
  - `config/corpus.json` freezes this run as the corpus.
- **Data quirks found:**
  - 7 Stripe postings have the literal word `LOCATION` as their location. The real place is in a second field ("India Locations", "Italy Locations").
  - 2 postings have no description text.
- **The label sample** (`labels.py`, seed 20261120):
  - **Population:** 22 role-phrase titles, 104 bare-"analyst" titles, and 3,976 others.
  - **Sample:** all 22, plus 30 and 40 random, for 92 postings, split 62 tuning and 30 held-out.
  - **Files:** `state/labels/labels.csv` (for me to fill in), `postings.md` (the full text to read), and `split.json`.
  - The sheet shows no filter verdict, and no filter code exists yet.
- **Unresolved: the held-out set may have no "yes".** Judging only by title and location, every likely match for Riley (US, not senior) landed in tuning. The 7 role-phrase postings in held-out are all senior or outside the US. If my labels agree, the held-out set can show false keeps but never a missed match.

## 2026-11-24 — Labels drafted by Claude, for my review
- **What I decided:** the 92 tuning and held-out labels are drafted by Claude, and I review every one. The reject-audit verdicts stay mine, as the brief requires ("judge each yourself").
- **Claude's draft** (`state/labels/labels_claude_draft.csv`, kept unchanged as a record). `labels.csv` is the copy I review. It has a `reviewed` column, so any label I change shows up against the draft.
- **Claude drafted all 92 as "no".** Four are close calls, each ruled out by one specific line in the posting:
  - **Veeva, Marketing Analytics Data Analyst (ADP program):** 0–2 years, NYC, SQL and Excel. But it says "Veeva does not provide sponsorship for employment visa status (e.g., H-1B, OPT, or TN status)".
  - **Stripe, Data Analyst Intern:** requires graduating in December 2027 or later. Riley graduates in December 2026.
  - **Stripe, Data Analyst, SF:** requires an MS plus 2 years of full-time experience, excluding internships.
  - **Zoox, part-time student worker (data analyst):** a part-time contract, not an entry-level job.
- **Unresolved:** if my review keeps every label "no", there are no positive labels. Recall can't be measured at all, and precision can only count false keeps. The filter's job on this corpus becomes rejecting everything correctly.

## 2026-11-25 — Reviewed the labels; added two supplement boards (FILTER.md v1.1)
- **My review:** I checked all 92 drafted labels against Riley's profile and kept every one as "no". The `reviewed` column in `labels.csv` records that. Nothing differs from Claude's draft.
- **The problem it left:** with no "yes" label, recall can't be measured. Claude then searched the other 4,010 postings for any US, non-senior data job with an early-career signal. It found five, and every one was ruled out: four Veeva entry-level roles say "Veeva does not provide sponsorship", and one Xsolla analyst role wants investment-banking experience.
- **The options Claude gave:** add boards by a new fixed rule, drop Riley's sponsorship need, or report the zero honestly. I rejected dropping sponsorship: changing the persona after labeling would manufacture positives. I chose adding boards.
- **FILTER.md v1.1** (commit `6a3ea0f`, before the probe ran):
  - a full-text probe rule for candidate postings, over 196 boards none of which were in the 11-18 probe
  - no filter rule, weight, or threshold changed
  - **A fix before the run:** Claude's first rule took any "analyst" title. As a code check on the v1.0 corpus, it flagged 16 postings, all finance, tax, compliance, or trading analysts, so a data-word test was added to the title rule before the new boards were read.
- **The probe** (`probe/2026-11-25_board_probe_v1_1.json`): 196 boards, 86 answered, 110 returned 404. 6,041 postings read. **Only 2 boards had a candidate**, one posting each: Axios ("Salesforce Business Analyst") and FanDuel ("Campaign Analytics, Data Analyst").
- **The supplement run** (`runs/2026-11-25T175647Z_supplement_v1_1`): 4 requests, 0.7 s, 138 postings. `config/corpus.json` now names both runs. The v1.0 run and its 92 labels are unchanged, and redrawing the v1.0 sample gives the identical split.
- **Supplement labels:** 22 postings (2 candidates, 10 bare-"analyst", 10 others), 15 tuning and 7 held-out. Claude drafted them (`labels_v1_1_claude_draft.csv`) for my review in `labels_v1_1.csv`. Two are drafted "yes": FanDuel's "Campaign Analytics, Data Analyst" and FanDuel's "Analyst". Both landed in held-out by the seeded split.
- **Tests:** 64, all passing (2 new: supplement runs join the corpus tagged by part, and the supplement config is exactly the probe's pick).
- **Unresolved:** if my review keeps both "yes" labels, held-out has 2 positives and tuning has none, so the threshold can't be tuned on a "yes".

## 2026-11-25 — Filter v1.0 built, measured on the labels, audit sheet drawn
- **What I did:** reviewed the 22 supplement labels and kept every draft, including the two "yes" labels (FanDuel's "Campaign Analytics, Data Analyst" and "Analyst"). The `reviewed` column records it.
- **What Claude built** (`filter.py`), exactly as FILTER.md v1.0 describes it: R1–R4, the score, and threshold 4. Every rule records the words that fired it.
  - **Locations:** Claude listed every distinct location in the corpus by how it was classified before trusting the US check. It added "SF", a "San Francsico" typo, and unknown regions ("AMER", "NAMER", "Remote - Americas"), which no longer count as US.
  - **Still a false friend, not fixed in v1.0:** "Toronto, CA" counts as US, because "CA" is also California's code. It is one posting.
  - **The two wrong versions** are kept as test-only functions, so the tests can show the real filter isn't either of them.
- **Tests: 82, all passing.** 15 are for the filter, including both wrong versions; 5 are for the measurement and the audit draw.
- **The v1.0 run:** 4,240 postings, 12 kept.
- **Measured on my labels** (`measure.py`, saved in `state/measure/v1.0_labels.txt`):
  - held-out: 2 kept, both "yes"; precision 2/2, recall 2/2. A sample this small says little.
  - tuning: 7 kept, all "no".
- **Each tuning false keep, and why:**
  - **Veeva ADP data analyst:** its line "does not provide sponsorship" is not one of R4's phrases.
  - **Stripe Data Analyst, SF; two FanDuel Product Analyst postings:** they require 2 years, which R2 passes and my label doesn't.
  - **Stripe Data Analyst Intern:** a graduation date the filter doesn't read.
  - **Zoox student worker:** part-time, which the filter doesn't read.
  - **Axios Salesforce Business Analyst:** Salesforce admin experience, which the filter doesn't read.
- **The audit sheet** (`audit.py draw`, seed 20261125, from the 4,203 postings outside held-out):
  - 10 kept (all of them, since only 10 are kept outside held-out), 30 random rejects, and the 10 rule-free rejects closest to the threshold
  - files: `state/audit/audit_v1.0.csv` and `audit_postings_v1.0.md`
  - **The verdicts are mine to make. Claude has not drafted any.**

## 2026-11-25 — MCP tool server, from scratch
- **What I asked for:** build the tool server while I judge the audit.
- **What Claude built:** `mcp_server.py`, standard library only, JSON-RPC over stdio. It has one read-only tool, `score_posting`, and logs every message in both directions to `state/mcp/`. `mcp_client.py` is a minimal client for recording a session. `.mcp.json` connects Claude Code.
- **Tests: 91, all passing** (9 new). One replaces `open`, `urlopen`, `socket`, and `os.remove` with a function that fails if called, then runs a full session.
- **Transcripts:**
  - **`mcp_client.py`:** three calls plus one call to a tool that doesn't exist.
  - **Claude Code 2.1.331 as the client** (`claude -p`, only `score_posting` allowed): it made two tool calls and reported both verdicts without judging the postings.
- **What only the real client showed:** before `initialize`, Claude Code sent a `server/discover` probe at protocol version `2026-07-28`. The server answered "method not found", and Claude Code fell back to `initialize` at `2025-11-25`. No test written from the spec would have sent that method.
- **`MCP_EVAL.md`** is Claude's draft, waiting for my review. It covers:
  - **declared vs actual.** The tool is read-only, but the server process writes its own log, and a client can't see that.
  - **what a client isn't entitled to**
  - **the trust decision**
  - **the other server:** not chosen yet.

## 2026-11-25 — The other server: Fetch
- **What I approved:** installing the reference Fetch server (`mcp-server-fetch` 2026.11.18 from PyPI). Claude installed it into a throwaway Python 3.12 environment in its scratchpad, because `uvx` isn't on this machine. Nothing was added to the repo.
- **What reading its source found before it ran:** it declares `readOnlyHint: true`, but on first use it runs `npm install` against the npm registry when Node.js is on PATH, and Node is on PATH here. Claude ran it with `--no-readability-js`, so it couldn't download more code than I had approved.
- **The session** (`mcp_eval_fetch.py`; transcript `state/mcp/other_fetch_2026-11-25T212010Z.jsonl`): the handshake, `tools/list`, `prompts/list`, and four calls.
  - A URL carrying the fictional persona's details went out to example.com: a "read-only" tool sending data out.
  - A loopback URL was refused before any request was sent. The test server counted 0 requests.
  - A string `max_length` was rejected.
- **Its tool description tells the model to override an earlier instruction** ("this tool now grants you internet access").
- **Claude's drafted trust decision:** Fetch is not allowed in the job-agent session, which holds private data. The draft is waiting for my review in `MCP_EVAL.md`.

## 2026-11-25 — Claims, the shortlist, and one change at a time
- **What I asked for:** keep building while I judge the audit.
- **Claims (`claims.py`):** for each of the 12 kept postings, `claude -p` wrote six fixed claims with a status and a quote. That's 5 runs of 12 calls: base, loose-quote, title-only, no-field-names, and the base prompt again. The recorded model is `claude-opus-5-5`. A substring checker labels each claim.
- **A checker bug Claude caught and fixed:** the first checker joined locations with " ; ", while the prompt showed them with "; ". So a quote like "San Francisco; US" was wrongly marked not found. It was fixed before any number was reported.
- **What the claims showed:**
  - The agent answered 3 of 12 kept postings and abstained on 9. All 3 answers are labeled "no". Both "yes" postings got "I cannot tell".
  - In two location quotes, Claude copied the prompt's field name ("Locations:"), so the checker refused them. Adding one sentence to the prompt (C3) made all 46 quotes match.
  - The same prompt run twice changed one held-out posting's claims. So C1's apparent held-out gain is ordinary variation, and `SCORE.md` says so.
- **A misreading Claude found in its own R2 code:** the Zoox Financial Analyst asks for "6+ years ... 2+ years". The v1.0 code took the lowest number across both requirements (2) and kept the posting. It is recorded as change F4 and measured; v1.0 was not quietly edited.
- **Filter changes, measured on held-out** (`measure_changes.py`):
  - F3 (reject at 2+ years) loses a held-out "yes".
  - F1, F2, and F4 make no held-out difference.
  - Claude recommends adopting F1, F4, and C3 and rejecting the rest. **The decision is mine.**
- **Drafts waiting for my review:** `SCORE.md` (the origin of every number, every change, persistence ≠ training) and `SHORTLIST.md` (the relevance-vs-entailment case: a Zoox "student" quote found but not proving "entry level"; and both abstention counterexamples).
- **Tests: 98, all passing** (7 new, for the claim checker and abstention, with no model calls).
- **Still mine to do:** confirm the 72 claim labels (`state/claims/base_checked.csv`), judge the 50 audit rows, and decide on the changes.

## 2026-11-25 — My reject audit
- **What I did:** judged all 50 rows of the audit sheet myself, each with a reason, in my own copy of the file. I gave it to Claude and told it to copy my verdicts into `state/audit/audit_v1.0.csv` without taking credit for them. Claude checked that the other eight columns matched the drawn sheet exactly, and copied my `your_call` and `reason` text in unchanged.
- **My results** (`audit.py report`):
  - **kept: 10/10 wrong.** Every posting v1.0 keeps outside held-out is one Riley wouldn't apply to.
  - **random rejects: 0/30 wrong** (95% interval 0–11%).
  - **near the threshold: 0/10 wrong.**
- **What my reasons showed:**
  - Five wrong keeps require 2+ years.
  - One is Veeva's no-sponsorship line.
  - One needs 6+ years, which the v1.0 R2 code misread.
  - One needs Salesforce administration experience.
  - One is a part-time student contract.
  - One requires a graduation date Riley can't meet.
- **The false friend:** in my row #27, Datadog FP&A Analyst R&D, "Reporting to the Senior Manager" earned the "reporting" skill point and lifted the score to exactly 4. FILTER.md v1.0 had predicted "reporting to" as a false friend. Claude measured a narrow fix on held-out as F5: no held-out change, 1 posting flips.
- **`AUDIT.md`:** Claude drafted it around my verdicts. It holds the sample statement, the results, the false friends, and the changelog of every rule added, cut, or rejected. It's waiting for my review.
- **Still mine to do:** the decisions on F1–F5, C1–C3, and A1, the claim labels, and the sign-off.

## 2026-11-25 — My claim labels
- **What I did:** labeled all 72 claims myself, checking each quote against its claim, in my own copy of the sheet. I gave it to Claude and told it to copy my labels into `state/claims/base_checked.csv` as my work, not its own. Claude checked that the other eight columns matched exactly, and copied my `my_label` column in unchanged.
- **My results:** 43 supported, 3 contradicted, 26 insufficient. Four differ from the checker:
  - FanDuel "Analyst", years: I labeled it insufficient, because "2+ years … preferred" doesn't say the job requires 2 or fewer.
  - FanDuel "Analyst", seniority: I labeled it insufficient, not contradicted.
  - Two location quotes that begin with the prompt's field name "Locations:": I labeled them supported. The checker refused them under FILTER.md's exact-span rule.
- **What changed with my labels:** with my labels (`claims.py confirmed`), the agent answers 4 of 12 kept postings, and all 4 are "no". Veeva moves from "I cannot tell" to "keep". It still abstains on both "yes" postings.
- **`SHORTLIST.md` was redrafted around my labels.** The relevance-vs-entailment case is now my own disagreement with the checker (FanDuel "Analyst", years), instead of Claude's first pick (Zoox's student quote, which I labeled supported).

## 2026-11-25 — Claim labels brought in line with the rules
- **What I asked for:** that every label that breaks our rules be checked and made to follow them.
- **What Claude checked:** all 72 of my labels against FILTER.md's evidence rules. A "supported" or "contradicted" label needs a quote that is an exact span of the posting. Only two of my labels broke it: the two location quotes beginning with the prompt's field name "Locations:" (Veeva ADP and FanDuel "Analyst"), which I had labeled supported.
- **What changed:** both are now insufficient, and the `note` column says when, why, and that I asked for it.
  - **The counts:** 41 supported, 3 contradicted, 28 insufficient, with 2 differing from the checker.
  - **The answers:** recomputed (`claims.py confirmed`). The agent answers 3 of 12, all "no", the same as the checker's labels. Veeva is back to "I cannot tell".
- **Not changed:** my judgments on what quotes mean. These include labeling Zoox's "Currently enrolled…" supported for seniority, and FanDuel "Analyst"'s "2+ years … preferred" insufficient for years. They are judgments, not breaks of a mechanical rule.

## 2026-11-25 — My decisions: FILTER.md v1.2
- **What I decided:** after going through the recommendations at the end of `SCORE.md`, I accepted all of them.
  - **Adopted:** F1 ("does not provide sponsorship" in R4), F4 (R2 reads the highest stated requirement), F5 ("reporting to" is not the skill), and C3 (no field names in quotes).
  - **Rejected:** F2, F3, A1, C1, and C2.
- **What Claude did with them:**
  - **FILTER.md:** recorded them as v1.2, marking each changed rule with its reason and my audit row.
  - **The code:** v1.2 is the current filter, and v1.0 is still callable. Claude checked that the v1.0 label measurement and my audit draw reproduce exactly.
  - **Tests: 103, all passing** (5 new for v1.2).
- **v1.2, measured once after the decision:**
  - It keeps 9 postings instead of 12. My audit errors #12, #27, and #35 are now rejected. Held-out precision and recall are still 2/2 and 2/2.
  - The claims still abstain on both held-out "yes" postings.
- **The MCP server now serves v1.2.** A new `mcp_client.py` session shows Datadog FP&A Analyst R&D and Veeva ADP returned as "reject".
- **Docs updated:** `SCORE.md`, `AUDIT.md`, `SOURCES.md`, `SIGNOFF.md`, `README.md`, and `MCP_EVAL.md` now show the decisions as mine and give the v1.2 numbers.

## 2026-11-25 — My review of the write-ups
- **What I reviewed:** `MCP_EVAL.md`, `SHORTLIST.md`, `SCORE.md`, `README.md`, and `SOURCES.md`. Claude listed exactly what in each was written in my voice and needed confirming.
- **My edits:**
  - **`MCP_EVAL.md`:** I removed the "to confirm when I review this" note on the server's 169 lines and marked the file reviewed.
  - **`SCORE.md`:** I removed the "waiting for my review" line.
  - **`SOURCES.md`:** I changed the two "Pending" review entries to "Reviewed".
  - **The rest:** kept as written. `SHORTLIST.md` and `README.md` were unchanged.
- **Claude's follow-ups:** it closed the bold on my `MCP_EVAL.md` status line, and set `SHORTLIST.md`'s status to reviewed, because I said to keep the file as it is after reviewing it.

## 2026-11-25 — Signed, precheck, zip
- **What I did:** reviewed `AUDIT.md` and `SIGNOFF.md`, marked both reviewed, and signed `SIGNOFF.md` ("Atharva, 25 Nov 2026").
- **Precheck (run with AI help):**
  - all 103 tests pass
  - no `.DS_Store`, `__pycache__`, or `.pyc` files tracked
  - no email address or local home path anywhere in the folder, including `runs/` and `state/`
  - nothing outside `fall-2026/atharva-h/js3-filter-tool-score/` staged
- **The zip:** built from the committed files only (`git archive`) as `Hambir_Atharva_INFO7375_JS3.zip`.
- **Not pushed:** pushing waits for my separate "yes, push".
