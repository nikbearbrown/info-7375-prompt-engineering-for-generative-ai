# FILTER — Job-Search Agent 3

**Version 1.0, 2026-11-17.** Written before the filter, scorer, or tool server is built.

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
| R2 | **Years:** the description requires more than 2 years, meaning the lowest number in a stated requirement is 3 or more ("3+ years", "3-5 years", "at least 4 years of experience") | description | Riley has 0–2 years. An employer's lowest acceptable number is what matters, so "1-3 years" passes and "3-5 years" does not. |
| R3 | **Location:** every location the posting gives is outside the US | location, description | Riley wants any US location or US remote. One US location among several is enough. |
| R4 | **No sponsorship:** the text says the employer will not sponsor ("unable to sponsor", "will not sponsor", "does not sponsor", "no visa sponsorship", "without sponsorship now or in the future") | description | Riley needs sponsorship. A stated "no" settles it. Silence is not a "no". |

**A rule whose field is missing never rejects.** If the description or location is missing, R2–R4 cannot fire. The posting is scored on what is there, and its claims are marked insufficient (see "Evidence rules").

### Score

| Signal | Points | Reason |
|---|---|---|
| The title contains a **role phrase**: "data analyst", "BI analyst", "business intelligence analyst", "business analyst", "reporting analyst", or "analytics analyst" | +4 | Riley's target titles, plus two other names for the same work. This is the clearest signal, so a role phrase alone reaches the threshold. |
| The title contains **"analyst"** but no role phrase | +1 | Bare "analyst" mostly means a different job. In the 2026-11-17 probe it was compliance, tax, fraud, and credit analysts. Such a job reaches the threshold only if it also asks for three of Riley's tools. |
| The title has **neither** | the score is 0, and skill words are not counted | So a "Software Engineer" posting that mentions SQL and Excel is never kept |
| Each distinct **skill word** in the description: SQL, Tableau, Power BI, Excel, Python, dashboard(s), reporting | +1 each, counted once, at most 7 | Each of Riley's tools is equally weak evidence. Each word counts once, so long postings don't win by repetition. |

**Threshold: keep when the score is 4 or more.** A role phrase alone reaches it. "Analyst" alone needs three skill words. I set this by hand for v1.0, and it may be tuned only on the tuning labels.

**Matching:** whole words, case-insensitive, after collapsing whitespace and stripping HTML tags from descriptions.

**Words I expect could be false friends, to check in the reject audit:**
- "excel" as a verb ("excel in a fast-paced team")
- "reporting" in "reporting to the CFO"
- "analyst" in non-data analyst jobs

v1.0 does not special-case any of them. The audit measures them first.

## Evidence rules
Each kept posting gets a justification made of claims, one for each property: role, seniority, years, location, sponsorship, and skills. `claude -p` writes the claims. Each claim must quote the posting's own text. Claude does not decide keep or reject; the rules above do.

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

## Version history
- **v1.0 (2026-11-17, revised 2026-11-18 before it was committed):** first version, from the interview. On 2026-11-18, the boards were re-chosen by a fixed rule over a 116-board probe, raw responses became compressed, and the labeling sample was capped. Nothing measured yet.
