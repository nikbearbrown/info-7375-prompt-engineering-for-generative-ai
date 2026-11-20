# MEASURE.md — Job-Search Agent 3: what moves the score

**Author:** Prasad Shinde
**Written:** 2026-11-20, after the held-out measurement (SEAL.md §10)
**Version:** v1 — 2026-11-20
**Rests on:** FILTER.md v2.1, AUDIT.md v1.3 and SEAL.md v1.7; the measurements in output/measure_2026-11-20T205049Z/ (development, pass 5) and output/measure_heldout_2026-11-20T205452Z/ (held-out).

## 1. Every number in the scorer, and where it came from
(Brief: "Your scorer has numbers in it: weights, thresholds, a Claude prompt. For each, say where it came from: hand-set, fitted on your labels, or inherited.")

| What | Value | Where it lives | Origin |
|---|---|---|---|
| Role words (C1) | Associate Product Manager, Product Manager, Product Analyst | resume_persona.json | inherited: JS1's persona, fixed before any run (CONTRACT §1) |
| Location words (C2) | New York, NYC, Remote | resume_persona.json | inherited: JS1, chosen after reading Stripe's location spellings, before any labeling (CONTRACT §1) |
| Skill words (C3, the score) | Python, SQL, A/B testing, roadmapping, user research | resume_persona.json | inherited: JS1 |
| Skill weights | 1 each; repeats count once | agent/rule.py; FILTER F5 | hand-set in JS1; never fitted |
| v1 skills threshold | 2 | agent/rule.py (SKILLS_NEEDED) | hand-set in JS1 (CONTRACT v0.3), to match the persona's minimum of 2 skills |
| v2 skills threshold | 0 | agent/filter.py (V2_OPTIONS) | fitted on my labels: chosen by measuring 9 variants on the 94 audited development postings (FILTER.md §6) |
| Seniority words (F9) | Senior, Staff, Lead, Group, Principal, Director, Head of | agent/filter.py (SENIORITY_WORDS) | hand-set: FILTER.md §5's level words, written 2026-11-15, before any data |
| Years limit (F10) | 3 | agent/filter.py (V2_OPTIONS) | inherited: the persona's max_years_required (JS1), unused until v2 |
| Years pattern (F10) | YEARS | agent/filter.py | hand-set: written by Claude Code to my list of phrases, reviewed by me; not fitted |
| Ranking (F8) | score, then board key, then id | agent/filter.py (rank) | hand-set in FILTER.md v1, before any data |
| A Claude prompt | none in JS3's scorer | — | JS1's prompt is inherited but not run in JS3: no Claude judgment enters any JS3 verdict. Claude is the scorer's client through the MCP tool (TOOLSERVER.md), not part of it |

The numbers around the scorer, for completeness: the audit's 30 random rejects (the brief's minimum); the sealed sets' 22 + 8 and 15 + 5 (hand-set, SEAL.md §4); the seeds, each fixed before its draw (SEAL.md §5, AUDIT.md §3); and the exact 95% interval (convention).

## 2. One change at a time, measured on the labels held out
(Brief: "make one change to one object at a time ... and measure on labels you held out.")

**The object changed** is the filter file only: FILTER.md, through agent/filter.py's options. Everything else stayed fixed: the same frozen corpus copy, the same persona, the same code path, no prompt, the same tool list, the same settings. The prompt, the context given to Claude, the tool list and the settings were never changed, so nothing here measures them.

**The labels held out** are JS3's 30 held-out postings (SEAL.md), labeled on 2026-11-16 and sealed by SHA-256 before any filter change existed. They are scored twice (SEAL.md §9): as sealed (3 worth), and after the §5 re-check (1 worth: posting 23). Each cell is kept worth / kept not_worth / missed worth, from output/measure_heldout_2026-11-20T205452Z/:

| Step | Change | As sealed | Re-checked |
|---|---|---|---|
| v1 | — | 0/0/3 | 0/0/1 |
| T0 | skills threshold 2 → 0 | 3/2/0 | 1/4/0 |
| T0 + F9 | + seniority words | 2/0/1 | 1/1/0 |
| T0 + F9 + F10 (v2) | + years rule | 0/0/3 | 0/0/1 |

Each change on its own, from v1, as sealed and re-checked: T1 (threshold 1) 1/1/2 and 0/2/1; F9 alone and F10 alone 0/0/3 and 0/0/1, because C3 still rejects everything; T0 + F10 0/1/3 and 0/1/1.

**What it shows:**
- Only lowering the threshold finds anything, and on its own it also keeps wrong postings (4, against the re-checked labels).
- F9 removes 3 of those 4 and loses no right one against the re-checked labels. Against the sealed labels it drops one posting marked worth, 24, whose title is "Staff Product Manager, Billing". The sealed label had missed "Staff", the same misread the audit found (AUDIT.md §7), and the re-check found that 24 asks for 10+ years besides. F9 was right; the sealed label was wrong.
- F10 removes the last wrong keep, and with it the one worth posting, 23, whose 5+ years are only preferred. That is the limit recorded before scoring (FILTER.md §5 v2.1, and §6's row of 2026-11-20).
- So on the held-out set, v2 keeps nothing. Against my re-checked labels, that is one miss and no wrong keep; T0 + F9 would have kept the one worth posting and one wrong one.
- I chose v2 on the development data before scoring, and I do not change it now: switching after seeing these numbers would turn the held-out set into a second development set. What the held-out set adds is the price of F10's limit: 1 of 1 worth postings held out, against 1 of 3 on the development set (pass 5).
- The numbers are small: 30 postings, with 1 or 3 worth. They show the direction of each change; they support no rate.

## 3. What persistence is not proof of
(Brief: "State what persistence is not proof of: a changed behavior across sessions does not mean anything was trained.")

- FILTER v2 behaves differently from v1 because agent/filter.py changed (V2_OPTIONS, JS3-CP8b): a committed code change. Nothing was trained or fine-tuned anywhere in JS3, and no model's weights changed.
- Claude Code got the same verdict from score_posting that filter_run wrote (TOOLSERVER.md) because both read the same committed code and the same frozen files. The agreement across sessions is the files, not learning.
- Claude.ai and Claude Code carried this work across sessions through the repository, the Project's files and the prompts I pasted. A behavior that persists across sessions is that context; a fresh session without it would not show it.
- My own labels changed across passes because I re-read the postings under a written standard, not because any part of the agent learned from them.

## Changelog
- **v1 — 2026-11-20.** Written after the held-out measurement. Claude (Claude.ai) typed it at my request from the committed files; the facts and decisions are mine.