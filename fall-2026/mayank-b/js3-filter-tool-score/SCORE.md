# SCORE.md: what moves the score

**Mayank Bhadrasen · JS3 · 2026-11-25.** Step 4 of the brief: where every number came from, one change to one object at a time, measured on labels I held out, and what persistence does not prove.

## 1. Where every number came from

| Number or setting | Value | Where it lives | Origin |
|---|---|---|---|
| Role words (title) | 6 terms | `config/filter.json` | **inherited** from my JS1 `search.target_titles` |
| Exclude words (title) | 8 terms | `config/filter.json` | **inherited** from my JS1 `search.exclude_titles` |
| Location pieces | Boston, MA; San Francisco, CA; New York City, NY; remote US | `config/filter.json` | **inherited** from JS1 + one **measured** fix ("Remote - USA", JS2 second check 2026-11-11) |
| Topic words (text) | 6 words (rag cut before v0.1) | `config/filter.json` | **hand-set** by me (answer 4b) |
| Forms of each topic word | e.g. llm, llms, large language model | `config/filter.json` | **hand-set**, proposed by Claude Code, approved by me in FILTER.md |
| Threshold T | 3 distinct topic words | `config/filter.json` | **inherited** from Lectern (`keywords.json` keep rule), not fitted |
| Score | count of distinct topic words, 0–6 | `src/jsa3/filter.py` `score()` | **hand-set** rule (FILTER.md 1.5); WF2 is its wrong version |
| Close call | score = T − 1 = 2 | `config/filter.json` | follows from T |
| Boilerplate line | ≥ 90 % of one board's postings | FILTER.md 1.6 | **hand-set**: Claude's proposal (Q4c), accepted by me |
| Audit sizes | 30 random rejects, ≤ 15 close calls, 10 kept | `config/seeds.json` | 30 is the **brief's minimum**; 15 and 10 are **hand-set** for my labelling time |
| Held-out size | 30 (10 / 10 / 10 by v0.1 fate) | `config/seeds.json` | **hand-set** (Q12a) |
| Seeds | 20261125 (held-out), 7375 (audit) | `config/seeds.json` | **arbitrary**, committed before any draw; they only make draws repeatable |
| Shortlist length N | 10 | the `shortlist` command | **hand-set** for my labelling time (4 claims × 10 postings) |
| Claude model | `claude-haiku-5-5` | `src/jsa3/shortlist.py` | **hand-set** (Q13; the current Haiku, $0.10 per million input tokens on 2026-11-25) |
| Claude effort, max tokens | `low`, 2000 (API route only) | `src/jsa3/shortlist.py` | **hand-set**. `temperature` is not a setting I can use: API version 2026-10-21 rejects it. The run that produced the shortlist used the Claude Code CLI route (`claude -p --model claude-haiku-5-5`), which uses the CLI's own effort default |
| Claude prompt | the text in `shortlist.prompt()` | `src/jsa3/shortlist.py` | **hand-written** by Claude Code, read by me; never tuned on labels |
| Loop budgets | 5 boards, 10 requests, 60 s, 10 s timeout | `config/budgets.json` | **inherited** from JS2 (GATE.md §2) |
| Snippet width | 240 characters | `src/jsa3/filter.py` | **hand-set**, display only (does not change any verdict) |

Nothing in this system was **fitted** on labels. The one change below is chosen from the reject audit (development data) and measured once on the held-out set.

## 2. One change at a time

- **Object changed:** the filter file only (`config/filter-v0.2.json`). **The one change:** the exclude word `Lead` was cut. Why: in my reject audit, the only wrong reject of 30 was R08 "AWS GTM Partnership Lead", rejected by `Lead` alone.
- **Held fixed:** corpus run `2026-11-26T02-20-27Z-content`, persona, code, the prompt, the tool list, every other rule and number.
- **Effect on all 950 postings:** kept 76 → 77, close calls 42 → 49 (`runs/2026-11-26T04-26-02Z-filter-v0.2/summary.md`).
- **Held-out (30 postings, labelled blind before the change, used once):**

| Filter | agree with me | false keeps | false rejects | other | n |
|---|---:|---:|---:|---:|---:|
| v0.1 | 19 | 1 | 9 | 1 | 30 |
| v0.2 | 19 | 1 | 9 | 1 | 30 |

**Result: no measurable change on the held-out set.** None of its 30 postings has `Lead` decide its verdict. The held-out set does show the filter's real weakness: 9 false rejects, postings I would keep that v0.1 rejects. That points at the next change (the role words and the level rules), and it would need a fresh held-out set, because this one is now used.

## 3. What persistence is not proof of

A saved filter file changing later runs is configuration persisting, not training: no weights moved. If the agent behaves differently next week, the explanation is a file I changed (FILTER.md + `config/filter.json`, each change dated in FILTER.md §7) or a board that changed, never that the agent learned. The Claude justifications are not trained either: each call starts from the same prompt, and a re-run of the same prompt can come back different (shortlist §Variation).
