# FILTER.md — Job-Search Agent 3: the filter, the evidence rules, and the score

**Version:** v0.2, 2026-11-25 (v0.1 written before any JS3 code; changes in §8). **Status: Claude's draft, not yet
adopted.** Shubham reviews it, changes what he disagrees with, and adopts it as v1.0 (as with
`GATE.md` in JS2). Until then every number below is Claude's proposal.
**Persona:** Kiran Joshi (fictional), the same as in `CONTRACT.md` and `GATE.md`.

`CONTRACT.md` §6 is a yes/no rule for one board. This file replaces it, for JS3 only, with a
**scored filter** over everything the agent has collected from every board, plus the rules for
checking the claims the agent makes about the postings it keeps. The code reads the filter's
numbers from the `toml` block in §1 of this file and from nowhere else, so this document is the
filter, not a description of it. Changing a number means a new version line in §8.

## 1. The filter

A posting is **kept** (reaches me) when its score is at least `threshold`. Otherwise it is
**rejected**. The score is the sum of the rules below; every rule is computed from the posting's
own fields (title, `location.name`, content, department names), never from the company, the
board, or Claude.

<!-- filter:begin -->
```toml
version = "0.2"
threshold = 7

[title]
family_phrase = 4            # R1
generic_words = ["engineer", "developer"]
generic_weight = 2           # R2 (R1 and R2 do not add: the title scores the larger one)
seniority_markers = ["senior", "sr", "staff", "principal", "lead", "manager", "director",
                     "intern", "internship", "iii", "iv", "l3", "l4"]
seniority_weight = -10       # R3

[skills]
per_skill = 1                # R4
cap = 3

[topic]
words = ["web application", "web applications", "backend", "back-end",
         "frontend", "front-end", "full-stack", "full stack", "distributed systems",
         "microservices"]
weight = 1                   # R5 (once, however many words appear)

[location]
us_based = 1                 # R6
not_established = 0
non_us = -10

[exclusion]
weight = -10                 # R7
```
<!-- filter:end -->

| Rule | What it reads | Points | Why (one line) |
|---|---|---:|---|
| R1 role phrase | Title contains a CONTRACT §6.1 role-family phrase for one of `$.target.roles` ("software engineer", "backend engineer", "full stack engineer", …) | +4 | The title is the employer's own name for the job and the strongest single signal of what the work is. |
| R2 generic role word | Title contains the whole word "engineer" or "developer" but no R1 phrase | +2 | Titles like "Product Engineer" or "Engineer, Payments" can be the same job under a different name, so they get a chance but must earn the rest from the text. |
| R3 seniority marker | Title contains a §6.1 marker as a whole word (senior, staff, lead, intern, …) | −10 | Kiran targets new-grad to SWE II; a senior or intern title is a different job however well the stack matches, so this is a veto. |
| R4 résumé skills | Distinct skills from the seven §4 résumé skill arrays found in the title, content or departments with the §6.2 matching (whole words, the special cases for C#, React, REST, …) | +1 each, at most 3 | Shared stack is evidence Kiran could do the work; the cap stops a long technology list from outweighing the title. |
| R5 topic words | Any of the listed topic words as a whole word in the cleaned content | +1 once | These words describe the kind of engineering Kiran has done (web apps, backend, distributed systems); once is enough to show the topic, more would reward wordiness. "api"/"apis" were cut in v0.2 (§8). |
| R6 location | The CONTRACT §6.4 location label of `location.name` (with the US-only rescue phrases) | US +1, unknown 0, non-US −10 | Kiran can only work in the US; an unknown location is not a reason to drop a posting, only to say "I cannot tell" later. |
| R7 exclusion phrase | Any CONTRACT §6.3 phrase (citizenship, clearance, unpaid) in title or content | −10 | Kiran is excluded by these terms outright, so this is a veto. |
| Threshold | Keep at score ≥ 7 | 7 | A role phrase (4) plus two skills (2) plus a US location (1) is the CONTRACT §6 bar; anything weaker must make it up with a third skill or the topic. |

The largest possible score is 9 (4 + 3 + 1 + 1). A posting with a veto (R3, R6 non-US, R7)
cannot be kept. **Close calls** are postings scored 6 or 7: one point either side of the line.

**Unscorable postings.** A posting with no title cannot be scored. It is listed as
`UNSCORABLE` with the reason and counted separately; it is never silently rejected.

## 2. The evidence rules

The agent writes a justification for every posting it keeps. The justification is a fixed list
of claims, so every claim can be checked against the posting's own text:

| Claim | Statement |
|---|---|
| C1 role | "The job is a <role> role, one of the roles Kiran targets." |
| C2 skill (one per skill) | "The posting asks for <skill>, which Kiran has." |
| C3 location | "The job is in the United States." |
| C4 experience | "Kiran's experience (4 years, from the résumé dates 2020-08 to 2024-12) meets the posting's stated minimum." |
| C5 work authorization | "The posting's terms do not rule out a candidate on F-1/OPT who will need sponsorship." |

Each claim gets exactly one label:

- **Supported**: a span of the posting's own text (title, `location.name`, content, department
  names) states it. The span is quoted with its field. For C1, the title has an R1 phrase. For
  C2, the §6.2 match. For C3, location label `US_BASED`. For C4, the highest stated minimum
  years in a sentence that mentions experience is 4 or less. For C5, the text offers sponsorship
  ("visa sponsorship", "will sponsor", "sponsorship is available").
- **Contradicted**: a span states the opposite. C1: the title has a seniority marker or no role
  word. C3: location label `NON_US`. C4: the highest stated minimum is more than 4 years. C5: the
  text says the employer will not sponsor ("unable to sponsor", "not able to sponsor", "will not
  sponsor", "does not sponsor", "without sponsorship", "without the need for sponsorship") or has a
  §6.3 citizenship or clearance phrase.
- **Insufficient**: no span either way, or spans both ways. C1 with only a generic title word.
  C3 `NOT_ESTABLISHED`. C4 with no number of years. C5 when the text says nothing about
  sponsorship, citizenship or clearance.

**Never evidence:** silence, the company's reputation, other postings, the board it came from, the
résumé, or Claude's opinion. Absence of a "no sponsorship" sentence does not support C5.

**When the agent must say "I cannot tell":**

1. For any claim labelled insufficient, the agent writes "I cannot tell" for that claim.
2. For the posting as a whole, if C3, C4 or C5 is insufficient, the agent does not say the
   posting fits. It says "matches the filter; I cannot tell whether it fits on: <claims>".
3. If the cleaned content is shorter than 200 characters, the agent labels every claim except
   C1 insufficient and says "I cannot tell" for the whole posting: there is not enough text to
   check anything against.
4. If any claim is contradicted, the agent says so first, before any supported claim.

Whether a kept posting is worth my time is never decided by these labels. They tell me what
the text does and does not say; the decision stays with me (driver's seat, README).

## 3. The expected sources

| Source | Where it is | Fields read | Expected |
|---|---|---|---|
| Greenhouse `stripe` | latest saved raw in `data/watch/boards/greenhouse-stripe/live/runs/`; earlier JS1 raws in `data/live/runs/` and `evidence/handcheck/` | `title`, `location.name`, `content`, `departments[].name` | Hundreds of postings |
| Greenhouse `figma` | `data/watch/boards/greenhouse-figma/live/runs/` | same | Over a hundred |
| Ashby `ramp` | `data/watch/boards/ashby-ramp/live/runs/` | Ashby `title`, `location`, `descriptionHtml`, `department`, `team`, mapped to the names above (GATE §9) | Over a hundred |
| Ashby `linear` | `data/watch/boards/ashby-linear/live/runs/` | same | A few dozen |

The corpus is every posting in every saved raw response of these four boards. A posting seen in
several raws is counted once, from its newest raw. The filter reads no network: it runs on what
the agent already collected.

**When something is missing:**

- A board with no readable saved raw: reported as `MISSING_SOURCE` with the reason. The run says
  the corpus is incomplete; it never reports that board as "no relevant jobs".
- `ashby/linearapp` (the deliberate 404 in JS2) and `greenhouse/ramp` (the stale wrong board in
  JS2) are **not** expected sources and are listed as excluded, with that reason.
- No title: `UNSCORABLE` (§1). No `location.name`: R6 is 0 and C3 is insufficient. No content or
  under 200 characters: R4 and R5 can only use the title and departments, and the evidence rule
  3 applies. No departments: nothing is lost; departments only feed R4.

## 4. Wrong versions the tests must catch

Each is a plausible filter or ranking that would pass a casual look. The tests in
`tests/js3/test_wrong_versions.py` run the same checks on the real code and on each wrong version;
the real code must pass every check, and each wrong version must fail the check named.

| ID | Wrong version | Why it is plausible | What it gets wrong | Check that must catch it |
|---|---|---|---|---|
| WV1 | Role words anywhere: R1 matched in title **or content** | "The content says software engineer, so it is a software engineering job" | A Sales or Recruiter posting that says "you will partner with software engineers" is kept | `check_role_words_read_title_only` |
| WV2 | Rank by skill count, no cap and no seniority veto | "More matching skills means a better fit" | A Staff posting with ten listed technologies outranks an entry-level one and is kept | `check_seniority_vetoes_any_skill_count` |
| WV3 | Silence is support: a claim with no contradicting span is labelled supported | "Nothing says they won't sponsor" | C5 and C3 are "supported" on postings that say nothing | `check_silence_is_insufficient` |
| WV4 | Substring skill matching | "Java appears in the text" | "Java" matches inside "JavaScript", "SQL" inside "NoSQL", "React" inside "reactive" | `check_skills_are_whole_words` |
| WV5 | Keep only above the threshold (`>` instead of `>=`) | An off-by-one nobody notices | Every posting scored exactly 7, the CONTRACT bar, is dropped | `check_threshold_is_inclusive` |

## 5. The reject audit (pre-registered)

Drawn once from the filter's decisions on the full corpus, with `random.Random(20261125)`:

- **40 rejected postings**, a simple random sample of all rejected postings (not vetoes only).
- **The 8 rejected postings with the highest scores** and **the 8 kept postings with the lowest
  scores**: the closest calls (ties broken by board then ID).
- **12 kept postings**, a random sample of the kept postings not already drawn.

The worksheet shows each posting's board, title, location, departments, link and the start of its
cleaned text, **shuffled, without the filter's score or decision**. I judge each one myself:
`RELEVANT` (a role Kiran targets, at a level and in a place Kiran could take, so I would want to
see it), `NOT_RELEVANT`, or `CANNOT_TELL`.

What the count can show: for the 40 random rejects I report the number I judged relevant and an
exact 95% binomial (Clopper–Pearson) interval for the share of all rejects that are relevant.
With zero misses in 40 the upper bound is about 9%: the sample cannot rule out a miss rate that
size, and 9% of a thousand rejects would be more postings than the filter keeps. The close calls
and the kept sample are not random draws of anything, so I report their counts only, with no rate.

## 6. Held-out labels

- **Held out:** the 10 JS1 held-out labels (`experiments/prompt/labels/heldout.labels.json`,
  labelled by Shubham on 2026-10-30). No JS3 number is set while looking at them.
- **Usable for tuning:** the 10 JS1 dev labels and the 5 JS1 sampling labels.
- **My audit verdicts** are collected after any change made from measuring (§8), so they are
  held out for that change too.

The JS1 labels follow the CONTRACT §6 rule, not this filter, so agreement with them measures how
close this filter stays to the rule I wrote in JS1, not whether a posting is good for Kiran.

## 7. What is not in the filter

No sponsorship gate (most postings say nothing, and silence is not evidence). No years-of-
experience gate (C4 reports it; the filter does not reject on it). No salary, company or team
preference. Claude is not part of the keep/reject decision; the JS1 judge prompt stays an opinion
shown beside the record.

## 8. Versions

| Version | Date | Change | Why | Measured |
|---|---|---|---|---|
| v0.1 | 2026-11-25 | First draft (Claude) | §1 reasons | Not yet: written before the code. On the full corpus (1,235 postings): 65 kept |
| v0.2 | 2026-11-25 | **Cut** "api" and "apis" from R5 | **False friend.** At Stripe, an API company, "API" appears in sales and product postings because of what the company sells, not what the job builds: "preferably at an API-first company", "Ability to understand the Stripe API" (Account Executive postings). 193 of the 984 postings with no role word in the title got R5 from "api"/"apis" alone | Flips 8 kept → rejected, every one a generic-title specialty job held up by R5 (Infrastructure Engineer, Privy; Cloud Security Engineer; Security Engineer, Privy ×2; Solutions Engineer, AI Build Team; Partner Solutions Engineer; Compliance Engineer; Data & Integration Engineer). No role-phrase title flips. 57 kept |
