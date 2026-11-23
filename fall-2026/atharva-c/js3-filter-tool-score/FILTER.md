# FILTER.md — the gate

**Version:** v1.0 · **Written:** Nov 23, 2026 · **Status:** written before any filter code (`agent/filter.py` does not exist at the commit that adds this file).

**Persona:** Sam Rivera (fictional, `examples/persona.example.json`): new grad / early career (0–2 years), wants **software engineering** roles in the **United States** (remote or on-site), skills Python, Go, React, TypeScript, SQL, Java.

**What I looked at before writing this:** the titles, departments, locations and "N years" phrases of the 400 postings in `evidence/run-20261123-185425Z/` (Robinhood 162, Affirm 218, Wealthfront 20, collected Nov 23). I read the data; I did not run any rule on it. Every number below is **hand-set** unless it says otherwise. Where a number came from is tracked again in `score/origins.md`.

---

## 1. The filter

A posting goes through three **hard gates** (any one rejects it), then gets a **score** from 0 to 1. It is **kept if score ≥ 0.50** (the threshold).

The filter reads only these fields from `agent/postings.py`: `title`, `location`, `text` (the posting body, HTML stripped). It never reads `department` (§3 says why).

### Hard gates (reject)

| ID | Rule | Reason |
|---|---|---|
| G1 | **Seniority in the title.** Reject if the title contains, as a whole word, any of: `Senior`, `Sr`, `Staff`, `Principal`, `Lead`, `Manager`, `Director`, `Head`, `VP`, `Vice President`, `Chief`, `President`. | Sam has 0–2 years. These words mean the employer wants more. In the Nov 23 data they are the single biggest group of engineering titles. |
| G2 | **Intern.** Reject if the title contains `Intern` or `Internship` as a whole word. | Sam is looking for a full-time role after graduating, not a summer internship. |
| G3 | **Location outside the US.** Split `location` on `;`. Reject only if **every** part names a place outside the US (e.g. `Remote Canada`, `Toronto, Canada`, `London`, `Remote UK`, `Remote Poland`, `Remote Spain`, `Luxembourg`, `Ljubljana, Slovenia`). If any part is a US place or `Remote US`, the gate passes. | Sam is US-based. A posting listing both New York and Toronto is still open to Sam, so one US part is enough. If `location` is empty, the gate does **not** reject (see §3, "I cannot tell"). |

### Score (only for postings that pass every gate)

| ID | Rule | Points | Reason |
|---|---|---|---|
| R1 | **Role phrase in the title.** The title contains one of: `Software Engineer`, `Software Developer`, `Backend Engineer`, `Back-end Engineer`, `Frontend Engineer`, `Front-end Engineer`, `Full Stack Engineer`, `Fullstack Engineer`, `Web Engineer`, `iOS Engineer`, `Android Engineer`, `Mobile Engineer`, `Machine Learning Engineer`. | +0.50 | This is what "software engineering role" means for Sam. The word `Engineer` alone is **not** enough: the data has `Sales Engineer`, `Partner Engineer`, `IT Engineer` and `Security Engineer`, which are different jobs. `Full Stack` alone is not enough either: Affirm's `Analytics Lead, Full Stack` and `Analyst, Early Career (Full Stack)` are analytics roles. |
| R2 | **Experience the posting asks for.** Find phrases of the form `N+ years`, `N years`, `N-M years`, `N to M years` within 60 characters of `experience`. Take the **smallest** N among them. If N ≤ 2: +0.30. If N = 3: 0. If N ≥ 4: −0.40. If there is no such phrase: 0. | +0.30 / 0 / −0.40 | Title levels do not tell the truth: Affirm's `Software Engineer II, Backend` asks for 5+ years. The years in the body are a better level signal. The 60-character window keeps out `10 years of history` in the company blurb. I take the smallest N because postings often say "4+ years, or 2+ years with a Master's". |
| R3 | **Explicit entry-level signal.** The title or text contains `new grad`, `new graduate`, `early career`, `entry level`, `entry-level`, or the title ends in or contains `Engineer I` (Roman numeral one, as a whole word). | +0.20 | These are the employer saying the role is for someone like Sam. |
| R4 | **At least one of Sam's skills in the text**, using the JS2 skill matcher (`agent/skills.py`, copied unchanged from JS2 `80e4fa1`, which already handles `React` and `Go` as English words). | +0.10 | A small bonus: skills help rank, but a strong role with a different stack is still worth seeing. Kept small on purpose so long postings that list many technologies do not win (see wrong version W3). |

**Threshold: keep if score ≥ 0.50.** With these points, a posting with a role phrase (R1) and nothing against it is kept; a posting with R1 but asking for 4+ years (0.50 − 0.40 + up to 0.30) is rejected unless something else lifts it; a posting without R1 is kept only if it has both R2 at +0.30 (≤ 2 years) and R3 (an explicit entry signal), so a non-SWE posting gets through only when the employer says entry-level and asks for ≤ 2 years. That is a known hole, and the audit checks whether it lets anything wrong in. I expect the closest calls to be around 0.40–0.60, and the audit (Step 2) looks at those first.

### Duplicates

The same title appears more than once on a board (91 of 400 postings in the Nov 23 data share a board and title with another), usually because Affirm posts one role per country. **Duplicates are not removed before the filter.** Each posting is judged on its own location, so the `Remote US` copy is kept and the `Remote Canada` copy is rejected by G3. The shortlist (Step 2) groups kept postings with the same board and title into one entry.

---

## 2. The evidence rules

The shortlist gives each kept posting a justification. The justification is broken into **claims**, one fact per claim (e.g., "entry-level", "US-based", "uses Python", "backend role"). Each claim is labeled against **the posting's own fields** (`title`, `location`, `text`), never against what I know about the company.

| Label | When | What must be recorded |
|---|---|---|
| **Supported** | A span in the posting states the claim. | The exact quote, copied verbatim (a test checks that the quote is a substring of the posting). |
| **Contradicted** | A span in the posting states something incompatible with the claim (claim "entry-level", text "5+ years of experience"). | The exact quote that contradicts it. |
| **Insufficient** | No span states it or its opposite. | Nothing to quote; say what was looked for. |

Further rules:

1. **A matched keyword is not support.** That a filter rule fired is never evidence for a claim. "The title has `Software Engineer`" supports "this is a software engineering role", but `Python` appearing in a list of "nice to haves" does not support "the role uses Python day to day". Each claim needs a span that **says** the claim.
2. **Company boilerplate does not support role claims.** Text about the company ("we've been around 10 years", benefits lists) cannot support a claim about the role.
3. **Contradicted beats supported.** If one span supports a claim and another contradicts it, the label is contradicted and both quotes are recorded.
4. **A salary, visa or location claim is never inferred.** It is supported only by an explicit statement.

### When the agent must say "I cannot tell"

The agent says **"I cannot tell"** instead of answering for a field when:

- **Level:** R2 found no years phrase **and** R3 found no entry signal **and** G1 did not fire. The title alone (`Software Engineer, Backend`) does not tell you the level. The posting is still scored, but its shortlist entry says "Level: I cannot tell".
- **Location:** `location` is empty or unrecognized (not in the US list or the non-US list in `agent/filter.py`). G3 does not reject, and the entry says "Location: I cannot tell".
- **Text missing:** `text` is empty. R2, R3, R4 cannot run. The posting is scored on the title only and marked "Text missing — I cannot tell level or skills". (In the Nov 23 data no posting has empty text; the JS2 Greenhouse data had empty text for all 380 Greenhouse postings, which is why JS3 re-collected.)

**Abstention rule (whole posting):** if **two or more** of the claims in a kept posting's justification are insufficient, the shortlist does not rank it. It goes in a separate "I cannot tell" list with the missing facts named. (Step 2 shows a counterexample where this rule is wrong.)

---

## 3. Expected sources

| Board | System | Endpoint (GET only) | Fields the filter reads |
|---|---|---|---|
| robinhood | Greenhouse | `boards-api.greenhouse.io/v1/boards/robinhood/jobs?content=true` | `title`, `location.name`, `content` → `text` |
| affirm | Greenhouse | `boards-api.greenhouse.io/v1/boards/affirm/jobs?content=true` | same |
| wealthfront | Lever | `api.lever.co/v0/postings/wealthfront?mode=json` | `text` → `title`, `categories.location`, `descriptionPlain` + `lists` + `additionalPlain` → `text` |

The allow-list is the JS2 policy (`agent/policy.py`, copied from JS2): hosts `boards-api.greenhouse.io` and `api.lever.co`, GET over HTTPS only.

**`department` is not read** because it describes the org chart, not the role: Affirm files `Technical Account Manager I` and `Senior Sales Engineer` under `Infrastructure Platform Eng`, and `Software Engineer II - CIAM` under `Information Security`.

**What the answer must be when something is missing:**

| Missing | The agent's answer |
|---|---|
| A board failed or returned 0 jobs | "I did not see board X in this run." Never "no matches on X". The run status from the JS2 loop (`incomplete`) is carried into the filter report. |
| A board not in this list | Not searched. The report lists the three boards it searched, so "no match" is never read as "no such job anywhere". |
| `text` empty | Title-only score, marked as above. |
| `location` empty | G3 skipped, "Location: I cannot tell". |
| `title` empty | Rejected with reason "no title — cannot judge". It is counted separately in the report, not mixed with ordinary rejects. |

---

## 4. Wrong versions my tests must catch

Each is a plausible filter or ranking that is wrong in a way the Nov 23 data would actually show. Each gets a test in `tests/test_filter.py` that **passes on the real filter and fails on the wrong version**.

| ID | Wrong version | Why it looks right | What it gets wrong (real example) | Test that catches it |
|---|---|---|---|---|
| W1 | **`Engineer` anywhere in the title counts as a role match** (substring, any case). | "Software engineering roles have Engineer in the title." | Gives role points to `Offensive Security Engineer` (Robinhood, passes G1–G3) and would do the same for `Sales Engineer` / `Partner Engineer` titles without a seniority word. | A title-only fixture set: `Sales Engineer` and `Partner Engineer` must score 0 on R1. |
| W2 | **Trust the title level: `Engineer I` / `II` = entry level**, ignore the years in the body. | "II is the second level, so it's junior." | Keeps Affirm's `Software Engineer II, Backend`, which asks for "5+ years". | A fixture with title `Software Engineer II` and body "5+ years of experience" must be rejected. |
| W3 | **Rank by the number of keyword and skill hits.** | "More matches = better fit." | Long postings that list many technologies outrank short, better-fitting ones; a Staff role that mentions all six skills beats an entry role that mentions one. | A ranking test: a short entry-level posting with 1 skill must outrank a long 4+-years posting with 6 skills. |
| W4 | **Remove duplicates by title before filtering.** | "They're the same job." | Affirm lists `Software Engineer I, Fullstack (Search)` as `Remote Canada` and `Remote US`. If the Canada copy comes first, the dedup keeps it and G3 then rejects the only copy, so the US role is lost. | A fixture with the same title twice, Canada first: the US copy must be kept. |
| W5 | **Reject if any location part is outside the US** (instead of every part). | "Sam can't work in Canada." | `Menlo Park, CA; New York, NY; Toronto` would be rejected though two of the three places are in the US. | A fixture with mixed US and Canada locations must pass G3. |

---

## Changelog

| Version | Date | Change | Measured? |
|---|---|---|---|
| v1.0 | Nov 23, 2026 | First version, written before the filter code. | No — nothing has been run yet. |

Every later change records the rule added, cut or rejected, the reason, and the measurement that led to it (Step 2 reject audit, Step 2d held-out labels).
