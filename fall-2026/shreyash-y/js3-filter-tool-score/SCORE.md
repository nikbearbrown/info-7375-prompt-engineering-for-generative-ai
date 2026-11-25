# What moves the score (Chapter 9)

*Drafted by Claude Code on 2026-11-25. Sections 1 and 2 are from the code and from runs made before
any hand label existed. The columns that compare with Shreyash's held-out labels are filled in from
`python3 -m js3.score` (results/score-v1.json) once those labels exist.*

The "score" here has two parts:

- **The filter's verdict** on a posting (FILTER.md v1, computed by code): its word lists and numbers
  live in `filter-v1.json`.
- **The Claude judge's verdict**, inherited from JS1: a prompt, a model, a context, a tool list.

## 1. Where every number came from

| Number or object | Value | Where | Origin |
|---|---|---|---|
| Role phrases | 9 phrases | filter-v1.json `rule1_title_phrases` | **Hand-set by Shreyash** (CONTRACT.md, 2026-10-28), kept in FILTER.md answer 4 |
| Departments | 6 names | `rule2_departments` | **Hand-set by Shreyash** (CONTRACT.md), kept in answer 5 |
| Palantir `Dev` = Engineering | 1 alias | `rule2_department_aliases` | **Hand-set by Shreyash** (review/19, 2026-11-10; answer 5) |
| Home city and state | Boston, Massachusetts | `rule3_home_*` | **Inherited** from the persona (Shreyash, CONTRACT.md section 1) |
| Minimum skills | **2** | `rule4_min_skills` | **Hand-set by Shreyash** ("at least TWO", CONTRACT.md; answer 7). Section 2 fits it on the audit labels as a check. |
| Sections whose skills do not count | `perk` | `rule4_ignore_sections` | Shreyash's wrong version 2; the heading word list (`js3/sections.py`) is **hand-set by Claude Code** |
| Maximum years | **3** | `rule5_max_years` | **Inherited** from the persona's `experience_years` (Shreyash); answer 8 |
| Seniority words | 5 words | `rule6_title_words` | **Hand-set by Shreyash** (CONTRACT.md) |
| Not-full-time title words | 9 words | `rule6_not_full_time_title_words` | **Hand-set by Claude Code** from answer 9 and follow-up C |
| Values counted as full-time | 4 spellings | `rule6_full_time_values` | **Hand-set by Claude Code**, from the boards' own values |
| Closest call | fails exactly **1** rule | `closest_call_fails` | **Hand-set by Shreyash** (answer 10) |
| Residence lists count only with **≥ 2** states | 2 | `jsagent/rule.py`, used by Rule 3 | **Inherited**: hand-set by Claude Code in JS2 rev 3 and never reviewed as a number. Measured false friend (AUDIT.md). |
| Experience reader: number words up to fifteen; a 30-character look-back for "founded / over the past"; headings of at most 5 words | | `jsagent/rule.py` | **Inherited**: hand-set by Claude Code in JS1/JS2 |
| Heading length: at most 12 words with ':', at most 6 with a heading word | | `js3/sections.py` | **Hand-set by Claude Code** (JS3) |
| Quote width: 180 characters around a match, at most 300 for a sentence | | `js3/filtering.py` | **Hand-set by Claude Code** (JS3) |
| 30 random rejects | 30 | `js3/audit.py` | **From the brief** ("at least 30") |
| Held-out set: 3 kept + 3 + 8 closest calls + 10 rejects | 24 | `js3/audit.py`, labels/SAMPLE-PLAN.md | **Hand-set by Claude Code** |
| Seed | 7375 | `js3/audit.py` | **Hand-set by Claude Code** (the course number) |
| The judge's prompt | `prompts/baseline-v1.md`, sha256 `60bc794a…` | | **Inherited** from JS1: written by Claude Code in JS1; the same hash as JS1's call records |
| The judge's model | `opus` (claude-opus-5-5) | `js3/experiments.py` | **Inherited** setting from JS1 |
| The judge's tools | none | `--tools ""` | **Inherited** from JS1 |
| Loop budgets: 6 boards, 12 requests, 120 s | | budgets.json | **Hand-set by Shreyash** (GATE.md, JS2) |
| Per-request timeout 20 s, one retry for a timeout or 5xx | | jsagent/loop.py | The retry is Shreyash's (GATE.md section 5); **20 s was hand-set by Claude Code** (JS2) |

**Fitted on labels:** none of these was fitted. Section 2 fits one number, the minimum skills, on the
audit labels and tests it on the held-out set. Whether to adopt the result is Shreyash's call.

## 2. One change to one object at a time

**What was fixed, and when.**

- **Before any hand label existed:** the held-out set (24 postings, `labels/sample.json`, commit
  `e8a9c431`) and every condition below (`js3/experiments.py` and `js3/score.py`, commit `a9e5d445`).
- **What is held out:** no rule, prompt or setting here was designed from these 24.
- **When the Claude conditions ran:** on 2026-11-25. B to T ran 17:28–17:34 EST and B3 ran
  17:38–17:39.
- **How each Claude call ran:** a fresh `claude -p` session from an empty folder, with no settings
  and no saved session.

| Condition | The one change | Object |
|---|---|---|
| B | — (JS1's judge: baseline-v1, CONTRACT.md's rule, opus, no tools) | baseline |
| B2, B3 | none: B again, in new sessions. B3 ran after every other condition. | noise floor and persistence |
| P | prompt `revision-1-quote-evidence.md` (JS1): one instruction added, quote the words behind each failure | the prompt |
| C | the rule Claude is given is FILTER.md v1 (Shreyash's words) instead of CONTRACT.md. The verdict list gains "I cannot tell", which FILTER.md defines. | the context |
| S | `--model haiku` | a setting |
| T | the `score_posting` MCP tool offered and allowed | the tool list |
| F1–F5 | one entry of `filter-v1.json` changed (no Claude) | the filter file |

**Claude conditions on the 24 held-out postings** (no hand labels needed for these columns):

| | B | B2 | B3 | P | C | S | T |
|---|---|---|---|---|---|---|---|
| Valid answers | 24 | 24 | 24 | 24 | 24 | **21** | 24 |
| Relevant / Not Relevant | 3 / 21 | 3 / 21 | 3 / 21 | 3 / 21 | 3 / 21 | 3 / 18 | 3 / 21 |
| Verdict differs from B | — | 0 | 0 | 0 | 0 | 0 of 21 | 0 |
| Failed conditions differ from B | — | 0 | 0 | 0 | **12** | 1 | 0 |
| Justification wording differs from B | — | 24 | 24 | 24 | 24 | 21 | 24 |
| Quotes not in the posting: strict / normalized | 1 / 0 | 1 / 0 | 0 / 0 | 3 / 1 | 0 / 0 | 1 / 0 | 0 / 0 |
| Tool calls | — | — | — | — | — | — | **0** |
| Cost (USD) | 0.88 | 0.38 | 0.38 | 0.98 | 0.98 | 0.03 | 1.01 |

**What these show, before any hand label:**

- **No change moved Claude's verdict on these 24.**
  - Prompt (P), context (C), tool list (T) and two reruns: Claude agreed with filter v1 on 24 of 24
    each time.
  - Haiku (S) agreed on all 21 valid answers. Its 3 invalid answers wrote JSON arrays without
    quotes, and the validator rejected them; they were not repaired.
- **The context change moved the reasons, not the verdicts.**
  - With FILTER.md v1 in the context, Claude stopped failing Palantir's `Dev` department in 9 of the
    12 Palantir postings that had failed it: "failed conditions" went from [2, 3] to [3]. That is
    Shreyash's answer 5, applied by a model that read it.
  - Those postings still fail location, so no verdict moved.
- **The tool was never used.** In T, Claude had `score_posting` and was allowed to call it, but made
  0 calls in 24 sessions. The prompt never mentions it. Offering a tool is not the same as the tool
  being used.
- **The quotes flagged as not found were punctuation, not invention.** 6 quotes were flagged by
  the strict check: a comma inside the closing quote, curly quotes turned into single quotes. After
  normalizing quote marks and end punctuation, 1 flag is left. It is text between two of Claude's
  quotes, which the extractor misread. By Claude Code's reading of all 6, Claude made up no quote in
  the 165 valid answers.

**Filter-file changes, one at a time** (deterministic; corpus counts need no labels):

| Change | Postings kept in the corpus | Closest calls | Held-out agreement with Shreyash |
|---|---|---|---|
| F0 filter v1 as written | 5 | 44 | *(after labels)* |
| F1 min skills 2 → 1 | 6 (+ Klaviyo "Software Engineer II - Recommendations") | 52 | *(after labels)* |
| F2 min skills 2 → 3 | 5 (no change: all 5 kept name 3 skills) | 25 | *(after labels)* |
| F3 + title phrase "Product Engineer" | 6 (+ Linear "Product Engineer") | 43 | *(after labels)* |
| F4 max years 3 → 5 | 6 (+ Klaviyo "Senior Software Engineer - Profiles, Lists and Segments") | 62 | *(after labels)* |
| F5 no Palantir `Dev` alias (JS2's reading) | 5 | 9 | *(after labels)* |
| (measured too) drop Rule 2, department | 5 | 84 | — |

- Four of these changes move **no** verdict in 789 postings.
- Each of the other three adds exactly one posting.
- Location does the work: 476 postings fail it outright.

## 3. What persistence is not proof of

- **B, B2 and B3** ran with the same prompt, model and inputs, in new sessions. They gave the **same
  24 verdicts and the same failed conditions**, and their wording differed on **24 of 24**.
  - Same decisions across sessions are not something the model learned. They come from the same
    context.
  - Different wording is not forgetting. It is sampling.
- **C changed what Claude did** on 12 postings, because FILTER.md was in its context.
- **B3 ran after C, and C's behavior was gone.** Palantir `Dev` failed again in 12 of 12, exactly as
  in B. Nothing was trained between the runs. The change lived in the text Claude was given, and
  went away with it.
- **The same is true of Claude Code across this assignment.** Claude Code "remembered" JS1 and JS2
  across days because it reads saved memory files and the repository at the start of a session:
  that is context. The judge runs used an empty folder and `--setting-sources ""` so that none of it
  reached them.
- **A behavior that persists across sessions** proves only that something it reads persists: a file,
  a prompt, a setting.

## 4. Against Shreyash's held-out labels

*(Filled in from `results/score-v1.json` once `labels/hand-verdicts.jsonl` holds the 24 held-out
answers.)*
