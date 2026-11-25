# FILTER — Job-Search Agent 3

**Version 1.2, 2026-11-25** (v1.0 was 2026-11-17).
- **v1.0** was written before the filter, scorer, or tool server was built.
- **v1.1** added supplement boards only.
- **v1.2** adopts three filter changes and one prompt change. Each was measured one at a time against v1.0 on the held-out labels (`SCORE.md`), and I chose them after my reject audit (`AUDIT.md`). They are marked **v1.2** below. Everything not marked is unchanged from v1.0.

- **Where it came from:** an interview on 2026-11-17. Claude gave the questions as one list with options and a recommendation for each, and I chose. The wording is Claude's draft from my answers, and I reviewed it before it was committed.
- **Changes:** a rule, weight, or threshold changes only by a new version in "Version history", with the date, what was added, cut, or rejected, and its measured effect. This changelog style is borrowed from the instructor's Lectern collector.
- **Persona:** Riley Navarro, the fictional persona from JS1 (`../js1-contract-and-watch/persona/resume.json`):
  - entry-level Data, BI, or Business Analyst
  - 0–2 years of experience; MS in Business Analytics (December 2026)
  - any US location, including US remote
  - needs H-1B sponsorship
  - tools: SQL, Python (pandas), Tableau, Excel
- **Starting point:** my JS2 code at commit `41ae85c` (collector, permission policy, tools).

## The filter
The filter is two-valued: **keep** or **reject**. A posting is kept when no reject rule fires and its score reaches the threshold. Kept postings are ranked by score, highest first.

### Reject rules
Any one of these rejects the posting, whatever its score.

| # | Rule | Reads | Reason |
|---|---|---|---|
| R1 | **Seniority:** the title contains Senior, Sr, Lead, Principal, Staff, Manager, Director, Head, VP, Vice President, or Chief, as a whole word anywhere in the title | title | Riley's excluded seniority (JS1 persona). It checks the whole title, so "Data Analyst, Senior" is caught too. |
| R2 | **Years:** the description requires more than 2 years, meaning the lowest number in a stated requirement is 3 or more ("3+ years", "3-5 years", "at least 4 years of experience"). **v1.2:** when there are several stated requirements, each must hold, so the highest of their lowest numbers counts. "6+ years … 2+ years" is 6. | description | Riley has 0–2 years. An employer's lowest acceptable number is what matters, so "1-3 years" passes and "3-5 years" does not. The v1.0 code took the lowest number across *all* requirements, which let a "6+ years" posting through (my audit, #35). |
| R3 | **Location:** every location the posting gives is outside the US | location, description | Riley wants any US location or US remote. One US location among several is enough. |
| R4 | **No sponsorship:** the text says the employer will not sponsor ("unable to sponsor", "will not sponsor", "does not sponsor", "no visa sponsorship", "without sponsorship now or in the future", and in **v1.2** "does not provide sponsorship") | description | Riley needs sponsorship. A stated "no" settles it. Silence is not a "no". v1.2 adds Veeva's wording, which v1.0 missed (my audit, #12). |

**A rule whose field is missing never rejects.** If the description or location is missing, R2–R4 cannot fire. The posting is scored on what is there, and its claims are marked insufficient (see "Evidence rules").

### Score

| Signal | Points | Reason |
|---|---|---|
| The title contains a **role phrase**: "data analyst", "BI analyst", "business intelligence analyst", "business analyst", "reporting analyst", or "analytics analyst" | +4 | Riley's target titles, plus two other names for the same work. This is the clearest signal, so a role phrase alone reaches the threshold. |
| The title contains **"analyst"** but no role phrase | +1 | Bare "analyst" mostly means a different job. In the 2026-11-17 probe it was compliance, tax, fraud, and credit analysts. Such a job reaches the threshold only if it also asks for three of Riley's tools. |
| The title has **neither** | the score is 0, and skill words are not counted | So a "Software Engineer" posting that mentions SQL and Excel is never kept |
| Each distinct **skill word** in the description: SQL, Tableau, Power BI, Excel, Python, dashboard(s), reporting. **v1.2:** "reporting" doesn't count when followed by "to" or "directly to". | +1 each, counted once, at most 7 | Each of Riley's tools is equally weak evidence. Each word counts once, so long postings don't win by repetition. "Reporting to the Senior Manager" is about who you report to, not reporting work (my audit, #27). |

**Threshold: keep when the score is 4 or more.** A role phrase alone reaches it. "Analyst" alone needs three skill words. I set this by hand for v1.0, and it may be tuned only on the tuning labels.

**Matching:** whole words, case-insensitive, after collapsing whitespace and stripping HTML tags from descriptions.

**Words I expect could be false friends, to check in the reject audit:**
- "excel" as a verb ("excel in a fast-paced team")
- "reporting" in "reporting to the CFO"
- "analyst" in non-data analyst jobs

v1.0 did not special-case any of them, so the audit could measure them first. The audit found "reporting to" (#27), and v1.2 excludes it. "excel" as a verb was not seen. Bare "analyst" is behind 5 of the 10 wrong keeps, but no measured change fixed it without cost, so v1.2 leaves it.

## Evidence rules
Each kept posting gets a justification made of claims, one for each property: role, seniority, years, location, sponsorship, and skills. `claude -p` writes the claims. Each claim must quote the posting's own text. Claude does not decide keep or reject; the rules above do.

- **The prompt (v1.2):** the claims prompt also says never to include the field names "Title:", "Locations:", or "Description:" in a quote. They are not posting text. This is variant `no-field-names` in `claims.py` (C3 in `SCORE.md`).
- **Supported:** the claim quotes an exact span of the posting's title, location, or description (matched after whitespace is collapsed), and that span says what the claim says.
- **Contradicted:** the posting text says the opposite. For example, the claim says "entry level" and the text says "5+ years required".
- **Insufficient:** the text is silent or ambiguous on the point, or the quoted span is not in the text.
- **Labeling:** a substring checker labels each claim first (quote found or not found), and I confirm every label.
- **"I cannot tell":**
  - **When:** the agent answers "I cannot tell" for a kept posting when its role, seniority, or location claim is insufficient, or when its description is missing.
  - **Years and sponsorship** reject only when contradicted (R2, R4). When the text is silent, their claims are shown as insufficient, but they don't force "I cannot tell". Most postings never mention sponsorship, so abstaining on that silence would abstain on nearly everything.
  - **Scoring:** "I cannot tell" answers count as neither keep nor reject. They are reported as coverage (answered out of total), alongside accuracy on the answered postings.

## Expected sources
**Boards:** 12 boards on three systems, picked by a rule I fixed before any probe result was seen. A "board" is one company's job board on one of the three systems.

- **The probe (2026-11-18):**
  - One GET per candidate board to the public board APIs, 116 candidates in all. 87 answered, and 29 returned 404.
  - It read titles and locations only. It saved counts and matched titles, not posting text.
  - The script and its results are in `probe/`.
- **The rule:**
  - A title is *relevant* when it has a role phrase, no seniority word, and a location that looks like the US.
  - **Relevant boards:** up to 22 boards with the most relevant titles.
  - **Contrast boards:** JS2's three, plus the 5 boards with no relevant title and the most bare "analyst" titles, which are the false-friend material.
- **What it found:**
  - Only 4 of the 87 boards that answered had any relevant title, so the rule picked 12 boards, not the roughly 30 I had planned.
  - Matching postings for an entry-level US data or BI analyst are rare on these systems.
- **The probe's own false friend:** Veeva's "Data Analyst - Pioneer | Israel - Kiryat Ono IL" counted as US, because "IL" matched the Illinois code. Veeva still qualifies through its New York posting.
- **This corpus is curated.** Its boards were picked because their titles matched, so analyst titles are over-represented. Every number measured on it describes these 12 boards, not the job market. Relevant roles whose titles don't say "analyst" are under-represented.

| Why it's in | System | Board | Employer | Postings | Relevant titles | Bare "analyst" titles |
|---|---|---|---|---|---|---|
| From JS2 | Greenhouse | `abacusinsights` | Abacus Insights | 18 | 0 | 0 |
| From JS2 | Ashby | `valon` | Valon | 30 | 0 | 0 |
| From JS2 | Lever | `xsolla` | Xsolla | 188 | 0 | 2 |
| Contrast | Greenhouse | `coinbase` | Coinbase | 256 | 0 | 19 |
| Contrast | Lever | `palantir` | Palantir | 306 | 0 | 17 |
| Contrast | Greenhouse | `datadog` | Datadog | 380 | 0 | 13 |
| Contrast | Greenhouse | `okta` | Okta | 364 | 0 | 12 |
| Contrast | Greenhouse | `anthropic` | Anthropic | 648 | 0 | 9 |
| Relevant | Greenhouse | `stripe` | Stripe | 788 | 4 | 20 |
| Relevant | Lever | `veeva` | Veeva Systems | 863 | 1 (plus the Israel false match) | 8 |
| Relevant | Lever | `zoox` | Zoox | 247 | 1 | 5 |
| Relevant | Greenhouse | `seatgeek` | SeatGeek | 35 | 1 | 2 |

Counts are from the 2026-11-18 probe, 4,123 postings in all. The collection run will count again.

### v1.1 supplement boards (2026-11-25)
- **Why:** I labeled all 92 v1.0 postings "no" on 2026-11-24. A search of the other 4,010 v1.0 postings found no US, non-senior data job Riley could apply to. The closest, Veeva's entry-level programs, each say "Veeva does not provide sponsorship". With no "yes" label, recall cannot be measured, so v1.1 looks for boards that hold one.
- **The probe (`probe/probe_v1_1.py`):** one GET per candidate board, to the same three public APIs. Every candidate is new: none was among the 116 boards probed on 2026-11-18. The list is in the script, committed before it ran. Unlike the v1.0 probe, it reads **full posting text**. It saves counts and matched titles, not posting text.
- **The rule, fixed before any result is seen.** A posting is a *candidate* when all of these hold:
  - the title has a role phrase, or "analyst" together with a data word (data, analytics, insights, reporting, BI, metrics). A first draft took any "analyst" title. Run on the v1.0 corpus as a code check, it flagged 16 postings, all finance, tax, compliance, or trading analysts, so the data-word test was added before the probe ran.
  - the title has no seniority word (the R1 list)
  - at least one location is in the US: a country field of US/USA/United States, a US state name, a ", ST" state code after a comma, or a US-remote phrase. A bare two-letter code with no comma no longer counts, which fixes the v1.0 probe's Israel "IL" false match.
  - the text has an early-career signal ("entry level", "new grad", "recent graduate", "early career", "university graduate", "0-2 years", "1-2 years", "up to 2 years"), or its lowest stated required years is 2 or less
  - the text has no refusal to sponsor (the R4 phrases, plus "does not provide sponsorship", "not able to sponsor", "cannot sponsor", "unable to provide sponsorship")
- **Boards picked:** every board with at least one candidate, ranked by candidate count, up to 15 (one run's budget).
- **Corpus:** those boards are collected as a second run, frozen beside the v1.0 run. The v1.0 run is not touched, so the 92 v1.0 labels stay valid. `config/corpus.json` names both runs.
- **This supplement is picked to contain matches, using tests that overlap R1, R3, and R4.** Recall on it is therefore optimistic. Every number is reported for the v1.0 corpus, the supplement, and both together, and it describes these boards, not the job market.
- **If no board has a candidate:** nothing is collected, and the v1.0 result stands: no posting on these boards is one Riley would apply to.

- **Fields read from each posting:** id, title, location, department, full description text, and URL.
  - Greenhouse: `jobs?content=true`
  - Ashby: the job-board API
  - Lever: `?mode=json`
- **When something is missing:**
  - **A board that fails** (404, timeout, unparseable) follows JS2's error policy. Its postings are absent from the corpus, and the report names it. It is never treated as "no matches".
  - **A missing field** never causes a reject (see "The filter").
  - **The board's own name:** on Greenhouse, it must match the employer before its jobs are fetched (JS2's identity check).
- **Corpus:** one fresh live collection of these boards, frozen. Every measurement in JS3 uses the raw responses in that one run folder.
- **Raw responses are saved gzip-compressed** (`.json.gz`). With full descriptions, these 12 boards are an estimated 60 MB uncompressed (from 2026-11-17 sizes of about 11–19 KB per posting), which is too much for the shared course repo.
- **Collection budget:** at most 15 boards, 35 requests, and 180 seconds per run. The 8 Greenhouse boards take two requests each, because of the identity check.
- **Permissions:** JS2's permission policy carries over unchanged:
  - HTTPS GET only, to the three ATS hosts
  - writes only in `runs/` and `state/`
  - no overwrite
  - my approval for any single write over 5 MB. Compressed responses should stay under that. If one doesn't, the run asks me at a real terminal.
- **The tool server** reads only that frozen run folder. It exposes no tool that writes, sends, or fetches anything.

## Wrong versions
1. **Substring match without word boundaries.** Skill and role words are matched as raw substrings. "excellent communication" then earns the Excel point, and "bi" matches inside "mobile" or "ambitious". A test must show the real filter doesn't award these points.
2. **Title-only filter.** Only the title is read. A "Data Analyst" posting whose description requires "5+ years" is kept. A test must show the real filter rejects it through R2.

## How the filter will be measured
- **Labels:**
  - Before I see any filter verdict, Claude draws a seeded sample: every title with a role phrase (at any seniority), 30 random titles with a bare "analyst", and 40 random others. That is about 90–100 postings.
  - Labeling every "analyst" title would have meant about 130 postings on these boards, so the "analyst" titles are sampled instead.
  - I label each "Riley would apply: yes / no".
  - The labels are split 2:1 into tuning and held-out, with the seed recorded.
  - The sample is enriched, so its numbers describe the sample, not all postings.
- **Reject audit:**
  - 30 random rejects, the 10 postings closest to the threshold, and 10 random kept postings, all seeded.
  - They are drawn only from postings outside the held-out set, so rules changed after the audit never see held-out labels.
  - I judge each one with a one-line reason.
  - Errors are reported as k/n with a 95% interval, never as a rate for all postings.
- **What moves the score:** one change at a time, each measured on the held-out labels:
  - a filter word
  - the threshold
  - the Claude prompt's wording
  - the context given to Claude (title only vs full description)

  The metric is precision and recall of "keep", with counts.
- **v1.1 supplement labels:** on the supplement boards only, Claude draws a seeded sample (same seed): every probe-rule candidate, every role-phrase title, 10 random bare-"analyst" titles, and 10 random others. Each stratum is split 2:1 into tuning and held-out, so the held-out set gets candidates too. As with the v1.0 labels, Claude drafts each label against Riley's profile and I review every one. The reject-audit verdicts stay mine alone.

## Version history
- **v1.0 (2026-11-17, revised 2026-11-18 before it was committed):** first version, from the interview. On 2026-11-18, the boards were re-chosen by a fixed rule over a 116-board probe, raw responses became compressed, and the labeling sample was capped. Nothing measured yet.
- **v1.1 (2026-11-25):** added the supplement-board rule ("v1.1 supplement boards") and its label sample, because all 92 v1.0 labels were "no". No filter rule, weight, or threshold changed. Nothing measured yet.
- **v1.2 (2026-11-25):** my decisions after the reject audit, from changes measured one at a time against v1.0 on the held-out labels (`SCORE.md`). None of them changed held-out precision or recall (2/2, 2/2); each is adopted for the reason given.
  - **Adopted:**
    - **F1:** R4 adds "does not provide sponsorship". Flips 1 posting: Veeva ADP, a tuning "no".
    - **F4:** R2 reads the highest of the stated requirements. Flips 1: Zoox Financial Analyst, my audit's wrong keep #35.
    - **F5:** "reporting" before "to" is not a skill word. Flips 1: Datadog FP&A Analyst R&D, my audit's wrong keep #27.
    - **C3:** the claims prompt forbids field names in quotes. Quotes found went from 46/48 to 46/46.
  - **Rejected:**
    - **F2,** threshold 5: tuning evidence only.
    - **F3,** reject at 2+ years: it loses a held-out "yes", recall 2/2 → 1/2.
    - **A1,** no abstention on seniority: 6 tuning answers, all wrong.
    - **C1,** loose quotes: its gain was within run-to-run noise.
    - **C2,** title-only context: fewer quoted claims.
  - **What was not changed:** threshold, weights, R1, R3.
