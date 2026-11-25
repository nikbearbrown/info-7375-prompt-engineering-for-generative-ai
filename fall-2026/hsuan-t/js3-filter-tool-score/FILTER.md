# FILTER — what reaches Aarav, and why

**Version:** v2.1 · 2026-11-25 · v2 (rule 4) signed off by Isaac Tai 2026-11-25; v2.1 (rule 5 phrase) decided by Isaac 2026-11-25 (D10)
(v1 · 2026-11-24 · signed off by Isaac Tai 2026-11-24 · code `3f72e7e`, unchanged JS2 rule.)
**Matches code:** `job_agent/judges/checks.py` `CHECKS` and `words.py` and `data/no_sponsorship_phrases.json` (2026-11-25). v2 changed rule 4, v2.1 one rule-5 phrase; `CONTRACT.md` still describes v1.
**Persona:** fictional Aarav Patel: `personas/aarav-patel.profile.json`, `personas/aarav-patel.resume.json`.

How to read this file: §1 is the filter. §2 says when a claim about a posting counts as supported. §3 says what the agent should see. §4 lists wrong versions the tests must catch. §5 records every change after measuring.

I read every reason below and accept them all as mine (signed 2026-11-24). Many come from my JS1 `CONTRACT.md` and `labels/LABELING_RULE.md`; which first drafts came from Claude is listed in `SOURCES.md`.

---

## 1. The filter

### 1.1 How words are matched (applies to every rule)

| Rule | What it does | Why |
|---|---|---|
| M1 word lists | Lowercase, split at every character that is not a letter or digit, drop empty pieces. `"Backend/API Engineer"` → `[backend, api, engineer]` | Companies write the same title many ways; comparing words makes them equal. |
| M2 all words of one phrase | A target phrase matches when **every** word of it is in the text's word list; order and extra words don't matter | Matching on any single word let 163 of 737 Stripe titles through on 2026-10-29 ("Designer, Web Presence & Platform"); requiring every word cut it to 92. |
| M3 whole phrase (visa only) | "No sponsorship" phrases must appear together and in order | "No degree required. Visa sponsorship is available." has both "no" and "sponsorship" but says the opposite. |
| M4 one splitter | Every rule calls the same function in `words.py` | If each rule split on its own, one would drift and give plausible wrong verdicts. |
| M5 HTML removed | Content is unescaped, tags dropped, unescaped again before splitting | Greenhouse escapes its HTML once; without this, tag names become "words". |

### 1.2 The rules, in order — the first rule that fails cuts the posting

| ID | Rule | Reads | Words / threshold (v2) | Cuts when | Why |
|---|---|---|---|---|---|
| 1a | exclude words | `title` | `profile.exclude_title_words`: senior, staff, principal, lead, manager, director, head, quant, sales, intern, frontend, contract | any exclude word is in the title | Aarav has 2 years of experience: senior-and-above titles are out of reach, and sales / quant / frontend / intern / contract are not the job he is looking for. |
| 1b | title (role words) | `title` | `profile.target_roles`: software engineer, backend, platform engineer, devops engineer, site reliability engineer | no target phrase matches | I only read on if the title is an engineering job. These five are the roles Aarav's résumé is built for. |
| 2 | location | every place the board lists (Greenhouse `location.name` + `offices[]`; Ashby `location` + `secondaryLocations[]` + country) | `profile.locations`: boston, us remote, us, united states | a location is written and no phrase matches | Aarav must work in the US (incl. US remote). No location written (empty, `N/A`, `na`) or a bare `Remote` → pass: a field the board left blank is never a reason to cut. All places are read because boards put "Hybrid" or a bare city in the first field (JS2 D7). |
| 3 | skills (topic words) | `content` | résumé `skills[].keywords[]` (17 words) + `data/skill_aliases.json`; **≥ 1** must appear | no résumé keyword or alias appears | Only check that uses the résumé. Greenhouse has no skills field, so "how many skills the JD lists" can't be counted without AI; the check looks each résumé word up in the JD instead. ⚠️ My LABELING_RULE says "two or three" — the code says 1 (ISSUES 1.3, to be measured in §5). |
| 4 | years | `content` | (A) an experience **ceiling** ("no more than 18 months", upper end of "0-1 years") below `years_experience` 2 → cut; otherwise the **largest** number before "year(s)/yrs", brackets included ("six (6) years"), must be ≤ `years_experience` 2 + `years_stretch` 2 = **4** | ceiling < 2, or largest years number > 4 | A requirement clearly beyond Aarav's level (2 years, at most 2 more) doesn't fit. I judge experience mostly as a ratio, and I would still apply when I have about half of what is asked (2 of 4 yes, 2 of 5 no); for Aarav's 2 years that is the same line as 2 + 2. (Isaac 2026-11-25) A new-grad role with a ceiling below Aarav's years is for less experienced people: S01, S20 in the audit. (v2 A) The largest number is the total requirement; the smaller ones are parts of it ("5+ years …, including 3+ years of infra"). (v2 B2, audit S16) No number → pass. |
| 5 | visa | `content` | `data/no_sponsorship_phrases.json` (14 phrases; v2.1: "without sponsorship" → "work without sponsorship" + "without visa sponsorship"), only when `needs_sponsorship` is true | any phrase appears as a whole phrase | Aarav needs sponsorship; a JD that says it won't sponsor doesn't fit, a JD that says nothing → keep reading. |
| 6 | salary | `content` | largest `$NNN,NNN` amount; must be ≥ `min_salary` **$75,000** | largest amount < $75,000 | Below the lowest yearly pay Aarav accepts. Largest amount: the top of a range is what the posting could pay. No salary → pass. |
| E | empty posting | `content` | — | content empty or only tags → `status: error`, not judged | With no JD, rules 3–6 can't run, and "relevant" from the title alone would look right while being unsupported. |

All rules pass → `relevant`. There is no score or ranking in v1: the filter is pass / cut only.

### 1.3 Known limits (where the filter is known to be wrong)
Kept in `CONTRACT.md` "Known limits"; the ones the reject audit (JS3 2.1) looks at first:
- **Appears ≠ required** (rule 3): "nice to have", "Java or Go", "migrating away from Redis" all count as a match.
- **Company intro matched**: 11 Stripe JDs share "We work mostly in Java, Ruby, JavaScript, Scala, and Go" → Java passes rule 3 on every one.
- **≥ 1 is lenient**: Java, SQL or AWS alone passes rule 3. Requiring ≥ 2 was measured and rejected (v2 C, §5): I count skills by meaning ("CI/CD" for Jenkins, "containers" for Docker), the code counts words, so ≥ 2 cut 5 postings I would apply to. 4 of the 5 audit disagreements left in v2 are this limit (S17, S24, S42, S46: one shared word, but the core of the job is C/C++ or low-level systems).
- **Location read literally**: a place is only matched by the words in `profile.locations`. In JS1, `Seattle, WA` had no "us" and was cut at rule 2. Since JS2 D7 every listed place (and Ashby's country) is read, so most US postings now carry "US" or "United States" somewhere. Measured 2026-11-24 on the 2,046 postings of `evidence/raw/2026-11-08T234257Z/`: 54 pass the title rules but are cut at rule 2; 53 are outside the US (London, Toronto, Dublin, Bengaluru…), **1 is a miss**: Stripe "Backend Engineer, Developer SDKs", location `Toronto, NY, SEA, SF; Canada Locations` (NY / SEA / SF are US cities written as abbreviations). → v2 candidate L1 in §5: measured again on all 2,123 postings under v2 and it changes **no** verdict (that one posting asks for 6 years and is cut at rule 4).
- **Years not about work**: "1 year of university education" is read as a years requirement.
- **Degree alternatives** (v2 B2): "Bachelor's + five (5) years, or Master's + three (3) years" is judged by the 5, so Aarav (MS) is cut although the Master's path fits him (Stripe 8197135 "High Availability and Disaster Recovery"). Left as a limit: only Stripe US-PERM postings write it this way. (Isaac 2026-11-25)
- **Contradicting JDs** (v2 B2): one posting says "7+ years" in one section and "4+ years" in another (openai "Intelligence & Investigations"); v2 takes 7.
- **Exactly half** (rule 4): 2 of 4 years is kept; for someone with 5 years, a 10-year posting would also be kept, although I might skip it. A single line can't follow both.
- **Title list** (rule 1b): "Product Evals Engineer" (S11) is cut although I would apply; the one random reject the audit found wrong.
- **Visa: not mentioned ≠ will sponsor**; **salary rarely given** (24 of 737 Stripe JDs on 2026-10-29).

---

## 2. Evidence rules (for the shortlist, JS3 2.2) — the abstention rule below is my decision (2026-11-24)

**Claim:** one sentence in a kept posting's justification that says something about the posting, e.g. "the JD asks for a skill Aarav has (Python)", "the JD requires ≤ 4 years", "the JD does not refuse sponsorship", "the salary reaches $75,000".

Each claim gets exactly one label, decided **only from the posting's own text** (title, location, content after HTML removal) — never from the company's reputation, other postings, or what Claude knows:

| Label | When |
|---|---|
| **supported** | A sentence in the posting states it, and the sentence is quoted word for word. A matched word alone is not enough: the sentence must say it in the sense the claim means (a requirement, not "you'll learn Kubernetes", not the company intro). |
| **contradicted** | A quoted sentence states the opposite (e.g. "8+ years", "we do not sponsor", "$60,000–$70,000"). |
| **insufficient** | No sentence addresses it, or the only match is a word used in another sense. "Not mentioned" is insufficient, never supported. |

**"I cannot tell" (abstention):** the agent answers "I cannot tell" instead of relevant / not relevant only when there is no text to judge:
1. the content is empty or only tags (rule E), or
2. the posting text it holds can't be traced to a saved raw file (no evidence to quote).

**Missing information is not a reason to abstain** (decided 2026-11-24): when the JD doesn't mention years, visa or salary, rules 4–6 pass as in v1, and the matching claim is labeled **insufficient**. Why: a posting is never cut, or held back, for something the board didn't write; the same lean as rules 2 and 4–6. So a posting can be `relevant` with several claims `insufficient`, and the shortlist must show those labels next to the verdict (e.g. "relevant — years, visa, salary not stated in the JD"), not hide them behind it.

---

## 3. Expected sources (facts from `data/boards.json` and the adapters)

| Board | ATS | Endpoint (public, no login) | Fields the agent reads |
|---|---|---|---|
| stripe | Greenhouse | `boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | `id`, `title`, `location.name`, `offices[].location`, `content`, `meta.total` |
| cloudflare | Greenhouse | same, slug `cloudflare` | same |
| openai | Ashby | Ashby public job-board API, slug `openai` | `id`, `title`, `location`, `secondaryLocations[]` + `addressCountry`, `descriptionHtml` |
| striqe | Greenhouse | slug `striqe` | misspelled on purpose (JS2 GATE): must fail with 404 and be reported, never treated as "0 postings" |

Only boards in `data/boards.json` are fetched (allow-list, JS2 policy). JS3 runs offline on the saved raw files in `evidence/raw/` — it does not fetch again.

**When something is missing:**

| Missing | Answer |
|---|---|
| board unreachable / 404 | board reported `failed` with its code; never "no new postings" (JS2 GATE) |
| job list shorter than `meta.total` | board `failed` 203 (JS2 D21) |
| `title` empty | rule 1b cuts it (no target phrase); the justification says so |
| location empty / `N/A` / bare `Remote` | rule 2 passes, justification `skipped: no location in posting` |
| `content` empty | rule E: `status: error`, "I cannot tell" |
| years / visa sentence / salary not in JD | that rule passes; the matching shortlist claim is **insufficient** |

---

## 4. Wrong versions the tests must catch (W1, W2 chosen by me 2026-11-24)

| # | Wrong version | Why it looks right | What it gets wrong | Test (`tests/test_js3_wrong_*.py`) |
|---|---|---|---|---|
| W1 | **Substring match** for skills (`"java" in jd.lower()`) | Less code; every JD that really says Java still matches | A résumé word hidden inside another word counts. Measured on all 2,046 saved postings: **937** cut at rule 3 by v1 would pass. "AWS" hides in "l**aws**" (the equal-opportunity sentence, 1,231 JDs), "Rust" in "en**trust**ed" / "t**rust**ed" (1,210), "Java" in "**Java**Script" (175). numbers from `reports/filter_v1_measure.py` | `test_js3_wrong_w1_substring.py`: JDs that say only "JavaScript", "applicable laws", "trusted partner" → rule 3 finds no résumé word; the substring version would find Java / AWS / Rust |
| W2 | **Missing field = cut** (no location / years / salary → not_relevant) | "Be safe, only keep what we're sure of" | Cuts postings for what the board left out; 2 of the 5 relevant Stripe postings on 2026-10-29 had location `na`. Also breaks the evidence rule in §2: missing information is a pass + an *insufficient* claim, not a cut. | `test_js3_wrong_w2_missing_field.py`: location `""` / `N/A` / `Remote`, no years, no salary → `relevant`, each skipped rule says `skipped: …` |

Considered and not chosen (2026-11-24): **W3** rank by keyword count (v1 has no ranking, so its test could only check that no score exists); **W4** years `<` instead of `≤` (a typo rather than a filter design mistake).

---

## 5. Changelog (filled after measuring, JS3 2.1)

| Version | Date | Rule | Added / cut / rejected | Measured on | Result |
|---|---|---|---|---|---|
| v1 | 2026-11-24 | all | written down from code `3f72e7e`, no change | — | — |
| v2 | 2026-11-25 | 4 | **A added**: cut when the JD's experience ceiling is below Aarav's years | v1 run of all 2,123 postings + Isaac's 50 hand labels (`audit/AUDIT.md`) | 3 relevant → cut (all new-grad roles); fixes S01, S20, breaks none |
| v2 | 2026-11-25 | 4 | **B1 rejected**: read "six (6) years" but keep the smallest number | same | changes nothing: the smallest number stays ≤ 4 |
| v2 | 2026-11-25 | 4 | **B2 added**: read "(6) years" and decide on the largest number | same | 8 relevant → cut; fixes S16, breaks none; of the 7 unlabeled cuts Isaac reviewed, 5 right, 1 wrong (degree alternative, §1.3), 1 unclear (contradicting JD) |
| v2 | 2026-11-25 | 3 | **C rejected**: require ≥ 2 résumé skills | same | 22 relevant → cut; fixes 4 but breaks 5 (S04, S14, S25, S30, S50): 9 disagreements vs v1's 8 |
| v2 | 2026-11-25 | 2 | **L1 rejected** (city names / abbreviations) | all 2,123 postings re-judged under v2 code | 0 verdicts change |
| v2 | 2026-11-25 | all | **v2 as adopted (A + B2)** | full re-run `reports/audit_run.py` → `audit/` (v1 run kept in `audit/v1/`) | relevant 70 → **59**; disagreements with the 50 hand labels 8 → **5** (S11, S17, S24, S42, S46), none new. Caution: A and B2 were found on these same samples, so this is not an independent test (F5 measures on held-out labels) |

### v2 candidates measured before the audit (2026-11-24)

| ID | Rule | Proposed change | Measured on | Result | Known risk |
|---|---|---|---|---|---|
| L1 | 2 location | add `ny`, `sea`, `sf`, `nyc`, `seattle`, `san francisco`, `new york` to `profile.locations` | all 2,046 postings in `evidence/raw/2026-11-08T234257Z/` (2026-11-24) | 7 postings go from cut to pass at rule 2, **all 7 in the US**, 0 non-US let in. Only 1 also passes the title rules (Stripe "Backend Engineer, Developer SDKs"); the other 6 are Cloudflare `Seattle, WA` postings already cut at 1a (senior / principal / sales). Every location string on these boards containing `sea` / `sf` / `ny` / `nyc` is a US city. | Some companies write **"SEA" for Southeast Asia**; none of these 3 boards does, a new board could. Rule 2 reads only the location field, not the JD, so ordinary-English "sea" is not a risk there. |

Recompute: `.venv/bin/python reports/filter_v1_measure.py` → `reports/filter_v1_measure/result.md` (W1 and the first L1 numbers); `.venv/bin/python reports/filter_v2_measure.py` → `reports/filter_v2_measure/result.md` (A, B1, B2, C, L1 on v2).

### v2.1 (2026-11-25) — rule 5 phrase, found on the F5 held-out set

| Rule | Change | Measured on | Result |
|---|---|---|---|
| 5 | **"without sponsorship" replaced** by "work without sponsorship" and "without visa sponsorship" (Isaac: drop it, use a better one) | all 2,123 postings; audit 50; held-out 20 | All 8 rule-5 cuts were Cloudflare's export-control sentence ("…export laws without sponsorship for an export license", in 464 JDs); none of the 2,123 JDs refuses a work visa. 8 postings cut → relevant (relevant 59 → **67**, the first Cloudflare postings ever kept). Audit 45/50 → 45/50. **Held-out 13/20 → 12/20**: H01 is fixed, but H06 and H16 had been cut *right by accident* (I would skip them for other reasons), and they are now kept. The rule's reason is now true, and the score went down. CONTRACT posting B ("authorized to work without sponsorship") is still cut. |

Caution: this change was found by reading a held-out posting (H01), so the held-out score after it is no longer an unseen measurement.

