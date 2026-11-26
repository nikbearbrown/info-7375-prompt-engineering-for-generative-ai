# What moves the score (Chapter 9)

*Written by Claude Code on 2026-11-17 from the runs in this folder; where this page says "I", that is Claude Code. Parts marked **[Omkar]** are Omkar's.*

**Summary.** Every number in the scorer is listed below with where it came from: **hand-set**, **inherited**, or **fitted on labels**. **Nothing in force is fitted.** `fit-threshold` was run on Omkar's 49 audit verdicts (the dev set, 2026-11-25): 4.5 and 5.0 tie at 46 of 49 correct (`experiments/FIT-THRESHOLD-dev.md`). Omkar kept 5.0, so the threshold stays hand-set. Then Claude Code made **one change to one object at a time** and measured each on **20 held-out labels**: Omkar's own JS1 labels, never used to set a JS3 number. The **100 held-out Claude calls** (5 Claude conditions × 20) are cached in `experiments/runs/` with their timestamps; the audit's 49 second-rater calls and the 2 tool-server sessions are counted in AUDIT.md and TOOL-SERVER.md.

The results: when *nothing* changed (fresh sessions), **0 of 20** verdicts moved. A filter-file change and a threshold change each moved **1 of 20**, the right way. The prompt change converted 3 errors into "cannot tell". Context and tool-list changes moved **nothing**. The biggest limit is the labels themselves: 9 of Omkar's 11 "relevant" labels get *not_relevant* under every condition except E3, which abstains on 2 of them. These labels contradict his own written labeling rule.

Full table: [`experiments/SCORE-RESULTS.md`](experiments/SCORE-RESULTS.md) (generated). Code: `js3/experiments.py`. Locks: `experiments/lock.json` (batch 1, 06:33:35 UTC) and `experiments/lock-2.json` (batch 2, 06:38:27 UTC).

## 1. Every number, and where it came from

| Object | Number | Value | Origin | Note |
|---|---|---:|---|---|
| filter (FILTER.md v1.6) | threshold | 5.0 | **hand-set** | = T1 + 2 skills, mirroring JS1's "≥ 2 skills" |
| | T1 role title | +3.0 | **inherited**, Reallocation Engine greenhouse-watch `scheme.default.json` (`title` 3.0) | phrase list hand-set |
| | T2 engineer title | +1.5 | **inherited**, greenhouse-watch (`title_partial` 1.5) | |
| | T3 seniority | −2.0 | **hand-set** | a penalty, not a gate: see the FILTER.md disclosure |
| | K1 shipped skill | +1.0 each, cap 8 | **inherited**, greenhouse-watch (`skill` 1.0, `max_skill_hits` 8) | |
| | K2 unshipped skill | +0.25 | **inherited**, greenhouse-watch (`skill_unshipped`) | |
| | Y1 level evidence | +1.0 | **hand-set** | |
| | G3 max years | 3 | **inherited**, Omkar's JS1 labeling rule ("about 3 years or fewer") | |
| | years window | 60 chars before "experience" | **hand-set** | v1.5 also reads `N+ years` alone |
| | years range read | 0–20 | **hand-set** | |
| | G1 location rule | — | **inherited**, my JS1 contract v2 | v1.1 addition hand-set |
| | G2 excluded words | 11 words | 5 **inherited** (greenhouse-watch `exclude_title_patterns`), 6 **hand-set** | |
| | close-call band | 1.0 | **hand-set** | |
| evidence rules | min content (AB1) | 300 chars | **hand-set** | |
| | min supported skills (AB2) | 2 | **inherited**, JS1 `MIN_SKILLS = 2` | |
| | heading max length | 80 chars | **hand-set** | |
| | negation window | 0–2 words | **hand-set** | |
| Claude prompt P1 (`prompts/judge-P1.txt`) | the 4 conditions | text | **inherited**, Omkar's `LABELING-RULE.md` (2026-10-26), restated | |
| | the rest of P1 | text | **hand-set**, written by Claude Code 2026-11-17 | |
| | posting text cap | 12,000 chars | **hand-set** | |
| settings | model | claude-sonnet-5-5 | **inherited**, the JS1 setting | |
| | temperature | CLI default | **inherited**: `claude -p` has no temperature flag, so it is not set by me | |
| | sessions | fresh, `--no-session-persistence`, `--setting-sources ""` | **hand-set** | |
| audit | random rejects | 30 | **inherited**, the assignment's minimum | |
| | gate near-misses | 8 | **hand-set** | |
| | seed | 7375003 | **hand-set** | |
| | interval | exact 95% (Clopper–Pearson) | convention | |
| collection | max requests / seconds / timeout / bytes | 16 / 120 / 30 s / 10 MB | 10 MB **inherited** (JS2); 16, 120, 30 **hand-set** (JS2 had 12, 90, 20) | 8 sources |
| tool server | message / content / title / location limits | 200 KB / 50,000 / 300 / 300 | **hand-set** | |
| | **fitted on labels** | — | **none** | `python3 -m js3.experiments fit-threshold` fits the threshold on the **dev** set (Omkar's audit verdicts) and only reports it. Nothing is adopted from it, and never from held-out |

## 2. One change at a time, on held-out labels

**Held-out set:** `labels/heldout-js1/`: 20 Klaviyo postings (saved 2026-10-25) that Omkar labelled by hand on 2026-10-27, **11 relevant, 9 not_relevant**. Each condition differs from its baseline in **exactly one object**, and `tests/test_misc.py::OneChangeAtATime` checks this. E5's prompt is byte-identical to C0's; E3 adds only the abstention sentence and the `cannot_tell` option; E4 adds only the filter-result block; each filter variant differs in one field.

| Cond | Object changed | The change | Correct (answered) | Abstained | Verdicts changed vs baseline |
|---|---|---|---:|---:|---:|
| F0 | — | filter v1.4 (in force when batch 1 was locked) | 10/20 | 0 | — |
| **E1** | **filter file** | T3 seniority −2.0 → 0.0 | 11/20 | 0 | **1** (Senior SWE – Growth → relevant, matches Omkar) |
| **E2** | **setting** | threshold 5.0 → 4.0 | 11/20 | 0 | **1** (the same posting) |
| E6 | filter file | v1.4 → v1.5 (`N+ years` alone) | 10/20 | 0 | 0 |
| E7 | filter file | v1.5 → v1.6 (sub-requirements) | 10/20 | 0 | 0 |
| C0 | — | Claude, P1, posting only, no tools | 10/20 | 0 | — |
| **C0b** | **nothing** | C0 again, 20 fresh sessions | 10/20 | 0 | **0**: the noise floor |
| **E3** | **prompt** | + "if the posting does not state its years requirement … answer cannot_tell" | 10/17 | **3** | 3 |
| **E4** | **context** | + the filter's own score lines and claim labels | 10/20 | 0 | **0** |
| **E5** | **tool list** | + `score_posting` offered over MCP | 10/20 | 0 | **0** (Claude called it in **0 of 20** sessions) |

### What each result says, and what it does not

- **C0b, the noise floor.** Re-asking the same 20 prompts in fresh sessions changed 0 verdicts. Any change below is at least not run-to-run noise *on these 20*. But 20 postings are few: one flip of 20 is within what a different sample could easily reverse.
- **E1 and E2** each fix one false negative ("Senior Software Engineer – Growth", score 4.25: SWE title 3 − senior 2 + skills). Neither added a false positive. **Not adopted.** One posting is not evidence for a rule change, and choosing a change *because* it helped on held-out would turn the held-out set into a dev set. It is Omkar's call, on dev evidence (his audit verdicts), with a FILTER.md row.
- **E3, the prompt.** On the three postings where Claude and Omkar disagreed, and the posting states no "X+ years" figure, Claude now says **cannot_tell**. Its reason, 2026-11-17: *"The posting never states an 'X+ years' experience requirement (only 'extensive background' for a Senior role), so the level condition cannot be checked."* Accuracy over answered postings rises to 10/17, but **no error was fixed**: three errors became abstentions. That is the honest kind of improvement: the system now says when it does not know.
- **E4, the context.** Giving Claude the filter's own verdict and claim labels changed **nothing**. On these 20, Claude was not anchored by the filter. Because C0 and F0 already agree on all 20, this set cannot tell "not anchored" apart from "already agreed".
- **E5, the tool list.** Offering the tool changed nothing, because Claude **never called it** (0/20, `transcripts/e5/` holds the 20 server logs: handshake and listing only). A tool that is listed but not needed is not used. Offering a capability is not the same as changing behavior.
- **E6 and E7** fix real errors on the corpus (Toast and Webflow; AUDIT.md), but change **0** held-out verdicts. Every held-out Klaviyo posting writes its requirement as "N+ years of … experience", so this held-out set **cannot see** what v1.5 and v1.6 fix. The fixes rest on the corpus measurement and the second rater, not on held-out evidence.
- **The ceiling is the labels.** 9 of Omkar's 11 *relevant* labels are *not_relevant* under every condition, filter and Claude alike, except that E3 abstains (`cannot_tell`) on 2 of them. They include "PIPELINE – L5 Principal Software Engineer" (Claude: *"requiring 10+ years of experience"*), "Sr. Staff Engineer, Applied AI", "Senior Lead Technical Program Manager", and "Sr. AI Systems & Solutions Architect". Under Omkar's own rule (level ≤ ~3 years; not a program-manager role) these would be not_relevant. And two near-identical postings, "Senior Security Engineer – Detection **and** Response" (7660012003) and "… Detection **&** Response" (7991733003), are labelled **relevant** and **not_relevant**. So what moves this score most is not a weight or a prompt but **the labels**. Re-labelling is a data change only Omkar can make. **[Omkar]** see section 4.

## 3. What persistence is not proof of

From 06:37 UTC on, every new session got the v1.6 answer for the same posting. That holds for `python3 -m js3.run_filter`, for my MCP server, and for any Claude session that calls it. Before 06:20 the same calls got the v1.0 answer. **That behavior change persisted across sessions, and nothing was trained.** The model is `claude-sonnet-5-5` in every row of every run file, and no weights changed. The change lives in files that each session reads at its start: `filter/CURRENT`, `filter/filter-v1.6.json`, `js3/textutil.py`. Delete or revert those files and the "learned" behavior is gone.

The same holds for the things that *look* like memory. Claude Code's memory folder and `CLAUDE.md` files are context loaded at the start of a session, not training. The experiments turned them off on purpose (`--setting-sources ""`, `--no-session-persistence`), and C0b shows that fresh sessions without them gave the same 20 answers. A changed answer next week would prove only that some *input* changed: a file, the prompt, the posting, the tool list, a setting, or the model version behind the name. It would never prove that the model learned from this project. The same was true in JS1: adding Omkar's labeling rule to the prompt changed 0 of 20 verdicts (`../js1-contract-and-watch/experiments/prompt/PROMPT-EXPERIMENT.md`).

## 4. [Omkar] Decisions this leaves

| Decision | Options | Your choice and why | Date |
|---|---|---|---|
| Adopt E1 (no seniority penalty) or E2 (threshold 4.0)? | adopt one with a FILTER.md row / keep v1.6 | **neither**: "I reject senior roles" (Omkar, typed in chat, entered by Claude Code) | 2026-11-25 |
| The held-out labels that contradict your rule (Principal, Sr Staff, TPM, the two Security Engineer postings) | keep as labelled / re-label with a note | **keep as labelled** (Omkar, typed in chat, entered by Claude Code). They stay as the held-out set; their conflict with the rule is reported in §2, not fixed | 2026-11-25 |

## 5. Commands

```bash
python3 -m js3.experiments run       # uses the cache; makes new Claude calls only for missing rows, and refuses if a lock is broken
python3 -m js3.experiments report    # rewrites experiments/SCORE-RESULTS.md
python3 -m js3.experiments fit-threshold   # after `js3.audit label`: dev-only fit, reported, not adopted
```
