# What moves the score (Chapter 9)

*Drafted by Claude Code on 2026-11-25. Sections 1 to 3 are from the code and from runs made before any
hand label existed. Section 4 and the held-out column in section 2 compare with Shreyash's held-out
labels, from `python3 -m js3.score` (`results/score-v1.json`).*

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
| Rule 3 and Rule 6 patterns: `US_WIDE_RE`, `REMOTE_AD_RE`, `WORKPLACE_CUE`, `NOT_PERMANENT_RE`, and v1.1's `RESIDE_RE`, `STATE_CODES`, `CITY_STATE_CODE_RE` | | `js3/filtering.py` | **Hand-set by Claude Code** (JS3); the 50 postal codes are the standard list |
| The claim patterns: `FULL_TIME_RE`, `PAY_RE`, `LEARNING_RE` and `ASKED_KINDS` (which headings count as "asking for" a skill). They decide the shortlist's labels, for example that all 5 kept postings were "I cannot tell" under v1 | | `js3/claims.py` | **Hand-set by Claude Code** (JS3) |
| The heading words that make a section "benefits" (`perk`) and the rest | | `js3/sections.py` | **Hand-set by Claude Code** (JS3) |
| The context-change prompt (C) | `prompts/context-filter-v1.md` | | **Built by Claude Code** from baseline-v1, with FILTER.md v1's rule section pasted in |
| The independent claim labeler's system prompt | | `js3/claim_judge.py` | **Hand-set by Claude Code** (JS3) |
| What the labeler saw: the label tool shows 700 characters of the ad and 900 of its requirements; the chat summaries cut the requirements at 380 characters, then at 1,400 after the cut hid a requirement from a hand verdict (item 8) | | `js3/label.py` | **Hand-set by Claude Code** (JS3) |
| 30 random rejects | 30 | `js3/audit.py` | **From the brief** ("at least 30") |
| Held-out set: 3 kept + 3 + 8 closest calls + 10 rejects | 24 | `js3/audit.py`, labels/SAMPLE-PLAN.md | **Hand-set by Claude Code** |
| Seed | 7375 | `js3/audit.py` | **Hand-set by Claude Code** (the course number) |
| The judge's prompt | `prompts/baseline-v1.md`, sha256 `60bc794a…` | | **Inherited** from JS1: written by Claude Code in JS1; the same hash as JS1's call records |
| The judge's model | `opus` (claude-opus-5-5) | `js3/experiments.py` | **Inherited** setting from JS1 |
| The judge's tools | none | `--tools ""` | **Inherited** from JS1 |
| Loop budgets: 6 boards, 12 requests, 120 s | | budgets.json | **Hand-set by Shreyash** (GATE.md, JS2) |
| Per-request timeout 20 s, one retry for a timeout or 5xx | | jsagent/loop.py | The retry is Shreyash's (GATE.md section 5); **20 s was hand-set by Claude Code** (JS2) |

**Fitted on labels:** none of these was fitted. Section 4 fits one number, the minimum skills, on the
audit labels and tests it on the held-out set. Shreyash did not adopt it (FILTER.md v1.1, A5).

**Added in v1.1, all hand-set by Shreyash after measuring (FILTER.md):** the title phrase "Product
Engineer"; MySQL, PostgreSQL and Postgres counted as SQL; a one-state residence line as a limit; and
"full-time not stated" as an evidence-rule exception. The state-code list that makes "TX" mean Texas
is **hand-set by Claude Code** (the 50 postal codes).

## 2. One change to one object at a time

**What was fixed, and when.**

- **Before any hand label existed:**
  - the held-out set: 24 postings, `labels/sample.json`, commit `e8a9c431`;
  - the Claude conditions: `js3/experiments.py`, commit `a9e5d445` at 17:28, with B3 added in
    `186d6af6` at 17:38;
  - the filter-file changes F0–F5: `js3/score.py`, commit `a774c4d6` at 17:35.

  The first label was saved at 17:53. Each Claude condition was committed and then run by the same
  command line: B's first call shares the second of its commit, 17:28:48, and so does B3's, 17:38:07.
- **What is held out:** no rule, prompt or setting here was designed from these 24. Later, after
  measuring, Shreyash used them once, to reject A3 (section 4). From then on they are a validation set,
  not an untouched test.
- **When the Claude conditions ran:** on 2026-11-25. B to T ran 17:28–17:34 EST and B3 ran
  17:38–17:39.
- **How each Claude call ran:** a fresh `claude -p` session from an empty folder, with no settings
  and no saved session.

| Condition | The one change | Object |
|---|---|---|
| B | — (JS1's judge: baseline-v1, CONTRACT.md's rule, opus, no tools) | baseline |
| B2, B3 | none: B again, in new sessions. B3 ran after every other condition. | noise floor and persistence |
| P | prompt `revision-1-quote-evidence.md` (JS1): one instruction added, quote the words behind each failure | the prompt |
| C | the rule Claude is given is FILTER.md v1 (Shreyash's words) instead of CONTRACT.md. **This is a two-part change:** the rule text, and the output format's verdict list ("I cannot tell") and `failed_conditions` definition, which FILTER.md's rules need. | the context |
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
| Cost (USD) | 0.88 | 0.38 | 0.38 | 0.97 | 0.98 | 0.03 | 1.01 |

**What these show, before any hand label:**

- **No change moved Claude's verdict on these 24.**
  - Prompt (P), context (C), tool list (T) and two reruns: Claude agreed with filter v1 on 24 of 24
    each time.
  - Haiku (S) agreed on all 21 valid answers. Its 3 invalid answers wrote JSON arrays without
    quotes, and the validator rejected them; they were not repaired.
- **The context change moved the reasons, not the verdicts.**
  - With FILTER.md v1 in the context, Claude stopped failing the department rule on all **9**
    held-out Palantir postings whose department is `Dev`. B fails it on all 12 Palantir postings.
    Their "failed conditions" went from [2, 3] to [3]. That is Shreyash's answer 5, applied by a model
    that read it.
  - In all, 12 postings changed their failed conditions: those 9, plus 3 where Claude added condition
    3 or 6 (`results/whatif-v1.json`, `_more.claude_conditions_vs_B`).
  - Those postings still fail location, so no verdict moved.
- **The tool was never used.** In T, Claude had `score_posting` and was allowed to call it, but made
  0 calls in 24 sessions. The prompt never mentions it. Offering a tool is not the same as the tool
  being used.
- **The quotes flagged as not found were punctuation or an extractor misread, not invention.** 6 quotes were flagged by
  the strict check: a comma inside the closing quote, curly quotes turned into single quotes. After
  normalizing quote marks and end punctuation, 1 flag is left. It is text between two of Claude's
  quotes, which the extractor misread. By Claude Code's reading of all 6, Claude made up no quote in
  the 165 valid answers.

**Filter-file changes, one at a time** (deterministic; corpus counts need no labels):

| Change | Postings kept in the corpus | Closest calls | Held-out agreement with Shreyash |
|---|---|---|---|
| F0 filter v1 as written | 5 | 44 | 24 / 24 (audit 43 / 46) |
| F1 min skills 2 → 1 | 6 (+ Klaviyo "Software Engineer II - Recommendations") | 52 | 24 / 24 (audit 44 / 46) |
| F2 min skills 2 → 3 | 5 (no change: all 5 kept name 3 skills) | 25 | 24 / 24 (audit 43 / 46) |
| F3 + title phrase "Product Engineer" | 6 (+ Linear "Product Engineer") | 43 | 24 / 24 (audit 44 / 46) |
| F4 max years 3 → 5 | 6 (+ Klaviyo "Senior Software Engineer - Profiles, Lists and Segments") | 62 | 24 / 24 (audit 42 / 46: +1 false positive) |
| F5 no Palantir `Dev` alias (JS2's reading) | 5 | 9 | 24 / 24 (audit 43 / 46) |
| (measured too) drop Rule 2, department | 5 | 84 | — |

- Three of these changes (F2, F5 and dropping Rule 2) move **no** verdict in 789 postings.
- Each of the other three (F1, F3, F4) adds exactly one posting.
- The source of these counts is `results/whatif-v1.json`, `_more.filter_changes_corpus`.
- Location does the work: 537 postings fail Rule 3, 476 of them because the job is neither in Boston
  nor remote (`results/whatif-v1.json`, `_more.rule3_fail_v1`). *(Corrected after the re-grade: this
  line first said "476 postings fail it outright".)*

## 3. What persistence is not proof of

- **B, B2 and B3** ran with the same prompt, model and inputs, in new sessions. They gave the **same
  24 verdicts and the same failed conditions**, and their wording differed on **24 of 24**.
  - Same decisions across sessions are not something the model learned. They come from the same
    context.
  - Different wording is not forgetting. It is sampling.
- **C changed what Claude did** on 12 postings, because FILTER.md was in its context.
- **B3 ran after C, and C's behavior was gone.** B3 failed the department rule on all 12 Palantir
  postings again, including all 9 `Dev` ones, exactly as B did. Nothing was trained between the runs. The change lived in the text Claude was given, and
  went away with it.
- **The same is true of Claude Code across this assignment.** Claude Code "remembered" JS1 and JS2
  across days because it reads saved memory files and the repository at the start of a session:
  that is context. The judge runs used an empty folder and `--setting-sources ""` so that none of it
  reached them.
- **A behavior that persists across sessions** proves only that something it reads persists: a file,
  a prompt, a setting.

## 4. Against Shreyash's held-out labels

The labels are Shreyash's 24 held-out verdicts, frozen before this comparison: commit `667a2932`,
sha256 `c678ec0e…`. Source: `python3 -m js3.score`, which writes `results/score-v1.json`.

| | B | B2 | B3 | P | C | S | T | filter v1 | filter v1.1 |
|---|---|---|---|---|---|---|---|---|---|
| Agree with Shreyash | 24 | 24 | 24 | 24 | 24 | 21 (+3 invalid) | 24 | 24 | 24 |
| Misses / false positives | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

**What the held-out set can and cannot show:**

- **No change separated itself on these 24.** Every Claude condition and every one-entry filter change
  agrees with Shreyash on all 24. The exception is S, whose 3 invalid answers count as invalid, not
  wrong.
  - That does not show the changes are harmless. These 24 postings do not sit where the changes act.
    The 3 kept ones are clear fits. Of the 21 rejects, 8 fail only location, 3 fail only experience
    (7 years) and 10 fail several rules (`_more.held_out_rejects_by_failed_rules`). No single change in
    this table moves any of them.
  - With every condition at 24 of 24, a real difference of a few postings would not show up here.
- **The one change the held-out set did catch is A3**, "count a skill only where the ad asks for it".
  - It was designed from the audit's false positive, and on the audit it looks better: 44 of 46
    instead of 43.
  - On the held-out set it is **worse: 22 of 24**. It drops Growth and Flows, which Shreyash labeled
    yes.
  - Shreyash rejected it for exactly that reason (FILTER.md v1.1). This is what the held-out set is
    for: a change fitted to one mistake broke two cases it was never shown.
  - **The cost:** having been used to decide, the held-out set is spent. It is now a validation set,
    and v1.1's 24 of 24 on it is not an untouched result. An untouched test of v1.1 would need new
    labels; none were made.
  - A3 was proposed because of the Android false positive. That false positive exists only in
    Shreyash's final answer for item 39, given after the double-check
    (`labels/hand-verdicts-provenance.md`).
- **The one number fitted on labels:**
  - Rule 4's minimum, fitted on the audit labels, picks **1**: 44 of 46 against 43 for the hand-set 2.
    The difference is one posting, Recommendations (item 31, whose final answer came after the
    double-check).
  - On the held-out set, 1, 2 and 3 tie at 24 of 24, and 4 drops to 21.
  - Shreyash kept 2 (A5 rejected). The miss that 1 would fix is fixed by A2 instead, for the reason
    Shreyash gave ("MySQL and PostgreSQL should count towards Alex's SQL skill"), not by letting any
    single skill through.
  - A fitted number is only as good as the labels it was fitted on, and here that is one posting.
- **Filter v1.1** agrees with Shreyash on 45 of 46 audit postings (v1: 43) and on 24 of 24 held-out.
  It changes exactly 2 verdicts in the corpus.
  - The audit figure is in-sample: A1 and A2 were designed from those audit misses.
  - The held-out figure is no longer untouched (above).
