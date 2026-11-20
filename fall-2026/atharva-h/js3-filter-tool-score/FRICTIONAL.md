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
