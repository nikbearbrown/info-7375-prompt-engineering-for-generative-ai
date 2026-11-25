# FILTER.md — Job-Search Agent 3

**Version:** v1.1, 2026-11-25 (v1 written before any JS3 code; v1.1 after the audit, see Versions). I read the draft and replied "ok" before it was committed.
**Where it comes from:**
- Rules R1–R5 are my JS1 rules (`../js1-contract-and-watch/CONTRACT.md`, section 4, 2026-10-31), reused unchanged. Their reasons below are from that contract.
- Decisions D1–D3 are mine, made on 2026-11-25. Claude Code recommended each one, and I agreed ("ok as you say").
- Claude Code drafted the rest of this file. `SOURCES.md` records who wrote what.

A posting reaches me only if this file says it should. If the code and this file disagree, the code is wrong. A rule changes only by a new version below, with the date, the reason and the measurement.

## 1. The filter

**Candidate:** Aarav Patel, a fictional persona (`persona/aarav-patel.resume.example.json`). He is in Boston, MA, and has 29 months of software engineering experience. His résumé lists TypeScript, Python, Java, SQL, Node.js, Kafka, Redis, MSSQL, PostgreSQL, AWS, Kubernetes, Docker, Helm, Fluent Bit and Jenkins. Rust and Terraform are listed as *familiar, not shipped*.

Each posting is read in one shape: `title`, `location.name` and `content` (the whole description; for Lever, the description, its requirement lists and its "additional" text).

| Rule | What the posting must have | Reason (one line) |
|---|---|---|
| **R1 role words** | The title contains one of: Software Engineer, Backend Engineer, Infrastructure Engineer, Platform Engineer, Site Reliability Engineer, DevOps Engineer, Data Engineer, Cloud Engineer. Whole words, any case. | These are the kinds of role his résumé shows (he has held "Software Engineer" twice). |
| **R2 seniority words** | The title contains none of: Senior, Sr, Staff, Principal, Lead, Manager, Director, Head, VP, Intern, Internship. | 29 months is early career, and he has graduated, so internships are out too. |
| **R3 location** | At least one location says "United States", or has a US state code or DC after a comma (", CA"). | He is in Boston and looks for US jobs. |
| **R4 experience** | The highest digit-based years phrase in the description ("N+ years", "at least N years", "N–M years", which counts as M) is 3 or less. No such phrase: passes. **v1 counts every phrase, including preferred qualifications (D1).** | His 29 months against a 36-month limit leaves a little room without accepting jobs that want much more. |
| **R5 topic words** | At least **two different** of his 15 skills appear in the title or description, as whole terms (`Java` does not match `JavaScript`). The *familiar, not shipped* skills do not count. | One shared word can be chance. Two shows real overlap with his work. |

**Score:** the number of rules passed, 0 to 5.

| Outcome | When | Reason |
|---|---|---|
| **keep** | score 5 | My JS1 rule: a match passes all five. |
| **close call** | score 4 (one rule short) | Rejected, but these are the first place a wrong rule would show, so the audit samples them. |
| **reject** | score 3 or less | |
| **cannot tell** | the title, location or description is empty or missing | A rule that cannot be checked is neither a pass nor a fail. The posting goes to me, not into "reject". |

**One job, many ids.** Lever lists the same job once per location. On the shortlist, postings from the same company with the same title and the same description are **one job** (all their ids kept). *Reason: 46 postings pass all five rules, and many of them are the same Palantir job.*

**Ranking the shortlist:** by the number of **different** topic words matched, highest first, then by title. *Reason: more of his skills named is a better first read. Counting different words, not repeats, stops a posting from ranking high by saying "Python" ten times.*

## 2. The evidence rules

Each posting on the shortlist gets a justification made of claims. Each claim is labeled against **the posting's own text** (its title, location and description), never against the résumé or Claude's opinion:

- **supported:** a quote from the posting says it.
- **contradicted:** a quote from the posting says the opposite.
- **insufficient:** no quote either way.

| Claim | Supported by | Contradicted by | Otherwise |
|---|---|---|---|
| **C1** "It is a software engineering role of his kind" | the R1 phrase in the title | — | insufficient |
| **C2** "It is open to an early-career engineer" | words like "new grad", "entry level", "early career", "junior", or a years phrase of 3 or less | a years phrase over 3, or a seniority word in the title | insufficient |
| **C3** "It can be done from the United States" | a US place in `location.name` | — | insufficient |
| **C4** "It asks for 3 years or fewer" | a years phrase of 3 or less, and none higher | a years phrase over 3 | insufficient |
| **C5** "It asks for his skills X and Y" (one claim per skill) | the skill appears in a sentence that asks for it ("you have", "experience with", "proficien…", "require…", "must", "strong") and not as a nice-to-have ("plus", "nice to have", "preferred", "bonus") | — | insufficient: the word appears, but not as something the job asks for |

**When the agent must say "I cannot tell" (D2):** if C1, C3 or C4 is insufficient, the posting stays on the shortlist, but its answer is "**I cannot tell** if this fits; here is what is missing", never "fits". The most common case: no years stated anywhere, so nothing in the posting shows that 29 months is enough.

A word that matches is not evidence for a claim. R5 passes when "Kubernetes" appears anywhere. C5 is supported only if the posting **asks** for it.

## 3. The expected sources

| Board | System | Fields read |
|---|---|---|
| Anthropic | Greenhouse | `title`, `location.name`, `content` |
| Palantir | Lever | `text`, `categories.location` / `allLocations`, `description`, `lists`, `additional` |
| Linear | Ashby | `title`, `location`, `secondaryLocations`, `descriptionHtml` |

The data is what my JS2 agent collected in its last live run, `2026-11-10T215306Z`: 677 + 304 + 33 = **1,014 postings**. The run's raw responses come from `../js2-loop-tools-diff/jobs/raw/`, byte for byte, and their SHA-256 hashes are checked.

**When something is missing:**
- **A board did not answer in that run:** the report says "**not checked**: *board*", never "no matches on *board*".
- **A posting's field is empty:** that posting goes to **cannot tell**.
- **A board's response is not the shape this file expects:** the run stops. It does not guess.

## 4. Wrong versions

Plausible filters or rankings that look right and are wrong. Each one must make a test fail.

| # | Wrong version | Why it is plausible | The test that must catch it |
|---|---|---|---|
| WF1 | Role word "Engineer" alone | Every role in R1 ends in "Engineer" | "Solutions Engineer" and "Sales Engineer" fail R1 |
| WF2 | Skills by substring | Simpler than whole words | A posting with only "JavaScript" does not match Java |
| WF3 | Ranking by how many times skill words appear | "More mentions, better fit" | A posting saying "Python" ten times does not outrank one with four different skills |
| WF4 | No years stated treated as evidence of "3 or fewer" | R4 lets it pass, so the claim looks true | Such a posting's C4 is **insufficient**, and its answer is "I cannot tell" |
| WF5 | No grouping of the same job | Each id is a different posting | The same Palantir job listed in 3 cities is one shortlist entry |
| WF6 | A missing field counted as a fail (or a pass) | Every posting gets a verdict | A posting with an empty location goes to **cannot tell** |

## 5. The audit and the measurements, planned before any label

**The pass line (D3, mine):** **at most 1 of 30** random rejects fits Aarav by my own hand label. This is the line in my final-project plan of 2026-11-23. If 2 or more fit, the report says the filter failed this check.

**My labels:**
- I give them blind: shuffled, with the filter's verdict hidden.
- I follow my JS1 labeling rule (`../js1-contract-and-watch/experiment/LABELING-RULE.md`): must-haves only, and nice-to-haves never count.
- Each posting is one label (**fit** or **not fit**) with a short reason.

**What gets labeled** (drawn with random seed `20261125`, fixed now):

| Set | How many | Drawn from | Used for |
|---|---:|---|---|
| Random rejects | 30 | postings with score 3 or less | the audit and its pass line |
| Close calls | 8 | postings with score 4 | the audit |
| Kept | 8 | the grouped shortlist | the audit |
| Held out | 16 | postings with score 3 to 5, not in the sets above | **only** for measuring changes |

If labels show a rule is wrong, the change becomes a new version here (v1.1, v2…), with what was added, cut or rejected, and the numbers that led to it.

**Changes to measure, one at a time** (each against v1, on the held-out labels only):

| # | Object | The change | Why |
|---|---|---|---|
| M1 | the filter file | R4 counts must-have years only, ignoring years under preferred or nice-to-have headings (D1) | JS1 left this disagreement unresolved |
| M2 | a setting | keep threshold 5 → 4 | do close calls fit more often than the threshold assumes? |
| M3 | the prompt | Claude's judgment prompt: JS1 `baseline-v1` → `revision-v1` | JS1 could not tell them apart on 10 cases |
| M4 | the context | Claude sees the whole posting → the title, location and requirement text only | does less text change its answer? |

M3 and M4 ask Claude, through Claude Code (`claude -p`), for an opinion, which is labeled as one. Its answer never changes the filter's verdict.

## Versions

- **v1, 2026-11-25:** this file. Rules R1–R5 from JS1; D1 (v1 counts every years phrase; must-haves only is tested as M1), D2 ("I cannot tell" when C1, C3 or C4 is insufficient) and D3 (pass line at most 1 of 30) decided by me.
- **v1.1, 2026-11-25, after the reject audit and the measurements (my decisions; Claude Code recommended each, I replied "ok"):**

  | Change | Kind | What changed | Measured evidence |
  |---|---|---|---|
  | **A** | **added** | **R3** also accepts "**D.C.**" (with dots) after a comma, like "DC" | 2 of my 8 close-call labels were fits (items 53, 54) that failed **only** R3, because their location is "Washington, D.C.". On all 1,014 postings, 64 have "D.C." and v1 failed every one of them on R3; 18 of them were close calls that move to keep. |
  | **B** | **added** | **R2** also fails a posting whose description says a candidate "must be graduating" (or "planning on graduating") in December 2026 or a later year. He finished his degree in May 2026. | 1 of my 8 kept labels was N (item 32: "Must be graduating in December 2026 or Spring 2027"). 3 kept postings in v1 say this. |
  | **C** | recorded, **no rule** | False friend: R1's "Platform Engineer" matched "IT Systems Engineer, **Client Platform Engineer**, ChromeOS", which is device administration, not software engineering (item 4, my N) | one example. v1 already rejected it, because R5 failed. A rule from one title would be fitted to one posting. |
  | **D** | **rejected** | M1, R4 counts must-have years only | On my 16 held-out labels: 16/16 with or without it. It moved one held-out posting (43, my N) from reject to close call, which still means not kept. No measurable gain. |
  | **E** | **rejected** | M2, keep at 4 of 5 | On held-out: 10/16, with 6 kept postings I labeled not fit. |
  | **F** | **rejected** | grouping the same title as one job | the "Forward Deployed Software Engineer - US Government" postings share a title but differ in must-haves ("Active … Top Secret" against "or willingness to obtain") |

  A and B were found on the audit labels, so they are **fitted on those labels**. On the held-out labels, v1.1 agrees 16/16, the same as v1. No held-out posting is in "D.C." or asks for a future graduation, so the held-out set cannot show their effect. M3 (prompt) and M4 (context) are not filter rules: M3 was worse on held-out (14/16) and is not adopted, and M4 gave the same answers.
