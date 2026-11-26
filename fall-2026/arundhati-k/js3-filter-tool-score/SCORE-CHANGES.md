# What moves the score: one change at a time, measured on held-out labels

## Where every number came from

Nothing in this agent was **fitted** (no number was computed by optimising against labels). Two rules (B, D) were
**chosen** after seeing their effect on my 54 audit verdicts, so the audit set is a dev set and is not used for the
final measurement.

| number / object | value | where | origin |
|---|---|---|---|
| role phrases R1–R6 | 6 title phrases | `filter/v1.json` | **hand-set** by me (FILTER.md v1 §1) |
| topic words T1–T8 | 8 words | `filter/v1.json` | **hand-set** by me (§2); regexes (whole word, `REST` case-sensitive) by Claude, accepted |
| weight of each topic word | 1 each | `filter.decide` | **hand-set** (§2 "each distinct word adds 1") |
| keep threshold | 2 topic words | `threshold` | **hand-set** by Claude ([Claude, pending]), accepted by me 2026-11-25 |
| close-call band | score 1–2 | `filter.decide` | **hand-set** by Claude (threshold ± 1 word) |
| US preference bonus | +1 rank | `us_bonus` | **hand-set** by Claude from my "prefer US" |
| years cutoff | 3+ required → reject (`max_required_years: 2`) | `filter/v1.1.json`, `evidence.EARLY_MAX_YEARS` | **hand-set**: cutoff by Claude (pending), accepted; rule B chosen by me after the audit |
| requirements-only counting | on | `topic_in_required_only` | **chosen** by me after the audit (rule D) |
| section heading words | regex lists | `evidence.REQUIRED_HEAD`, `PREFERRED_HEAD` | **hand-set** by Claude, never measured on their own |
| audit sample sizes | 32 / 12 / 10 | `run_filter.py` | **hand-set** by Claude (brief: at least 30 rejects) |
| seeds | 7375 (audit), 7376 (held-out) | scripts | **hand-set** |
| Claude prompt `judge_v1.txt` | full text | `prompts/` | **inherited**, copied unchanged from my JS1 `prompts/baseline.txt` (includes JS1's 10-skill list and "at least two" skills) |
| Claude prompt `judge_v2.txt` | condition 2 rewritten | `prompts/` | **hand-set**: Claude rewrote condition 2 from my FILTER.md level/location rules |
| model | `claude-opus-5-5` | `claude -p` default | **inherited** CLI default setting (Claude Code 2.1.316); not chosen |

## Held-out set

There are 20 postings with role titles (seed 7376), none of them in the audit sample. I labeled them blind
([labels/my-heldout-labels-2026-11-25.txt](labels/my-heldout-labels-2026-11-25.txt)): **2 Y, 18 N**. They were not
used to choose any rule. They *were* opened during a bug investigation (#14), which is how the curly-apostrophe parser
bug was found. That fix changed none of the filter held-out numbers below.

**Reference point:** "reject everything" agrees on **18/20** (TP 0). With only 2 positives, agreement is not a useful
score. I report TP and FP alongside it.

## Changes: one object at a time

### Object 1: the filter file (deterministic, [log](evidence/logs/06-filter-heldout.txt))

| filter | held-out agree | TP | FP | FN | disagreements (#) |
|---|---|---|---|---|---|
| v1 baseline | 16/20 | 1 | 3 | 1 | 8, 13, 14, 18 |
| v1 + B only | 17/20 | 1 | 2 | 1 | 13, 14, 18 |
| v1 + D only | 18/20 | **0** | 0 | 2 | 4, 14 |
| v1 + A only (rejected by me) | 18/20 | 1 | 1 | 1 | 14, 18 |
| v1 + C only (rejected by me) | 15/20 | 2 | 5 | 0 | 3, 8, 13, 16, 18 |
| v1.1 = B + D | 18/20 | **0** | 0 | 2 | 4, 14 |

### Object 2: the prompt (LIVE Claude, 2026-11-25, [log](evidence/logs/09-claude-heldout.txt))

Context and setting were held fixed: full posting body, résumé skills JSON, default model, a fresh tool-less session
per call, `--setting-sources ""`, `--no-session-persistence`.

| run | prompt | held-out agree | TP | FP | FN | valid JSON |
|---|---|---|---|---|---|---|
| P1 | judge_v1 (inherited) | 17/20 | 0 | 1 (#18) | 2 (#4, #14) | 20/20 |
| P2 | judge_v2 (my rules) | 17/20 | 0 | 1 (#18) | 2 (#4, #14) | 20/20 |

### Object 3: the context given to Claude (LIVE, 2026-11-25)

| run | prompt | context | held-out agree | TP | FP | FN |
|---|---|---|---|---|---|---|
| P1 | judge_v1 | full posting body | 17/20 | 0 | 1 | 2 |
| C2 | judge_v1 | requirement/responsibility lines only | 17/20 | 0 | 1 | 2 |

C2 was built with the section parser **before** the curly-apostrophe fix (the process had already imported it), so
some Stripe "What you’ll do" lines were left out of its context.

Not changed in this assignment: the **tool list** (each Claude run had no tools) and **settings** (model,
effort). Each is one more object, and I didn't measure them.

## What this shows, and what it doesn't

- **The prompt and context changes moved no verdicts on these 20 postings.** All three Claude runs gave the same
  verdict on every posting. Only the *reasons* changed. P1 failed #4 for "not an internship/new-grad" (the JS1
  prompt's rule), and P2 failed it for "level cannot be verified". C2 said "names none of the listed skills",
  because the skills were outside the requirement lines it was given. Same answer, three different paths: a stable
  verdict is not evidence that the reasoning is stable.
- **v1.1 ties "reject everything" on the held-out set.** It keeps 4 of 1,088 and found neither of my 2 Y postings.
  On this set the improvement I measured on the audit (42 → 49 of 54) did not carry over as better recall. D on its
  own cost the only true positive (#4: its AWS/Postgres mentions are under NICE TO HAVES).
- **Both of my held-out Y labels conflict with my own written rules.** #14 explicitly requires 4+ years, which rule B
  rejects. Claude said the same in all three runs ("it explicitly requires 4+ years"). #4's stack words are
  preferred-only, which rule D rejects. Audit #53 (Y) also requires "three (3) years". So the disagreement is between
  **my labels and my rules**, not between the code and my rules. I have not relabeled the held-out set after seeing
  this, because relabeling it now would make it no longer held out. **My answer (2026-11-25,
  [verbatim](labels/my-label-vs-rule-2026-11-25.txt)):** the labels were wrong, not the rules. "I sometimes used
  general engineering relevance as a substitute for checking the actual requirements." The labels stay as I gave
  them, and the numbers above use them.
- **Claude's one false positive, #18** (a mobile internship), passes every written rule. I marked it N for "not
  backend-focused", and no rule of mine says "backend-focused". That's a judgment I haven't written down.
- Sample size: a difference of one posting out of 20 is within noise. None of these comparisons separates the
  variants statistically.

## What I would do next (my words, 2026-11-25)

If I continue working on this, I would first test the claim labeler on a new set of job postings that I haven't used while making these changes. The 16/16 result looks good, but since I used the same 16 claims to improve the labeler, I can't say yet how well it will work on new postings. I would keep rule D for now because keywords mentioned in team descriptions were creating false matches, even though it also rejected postings like #4 where the skills were only listed as nice-to-have. I would also consider adding a backend-focus rule because #18 was a mobile internship and passed the current filter, even though it wasn't the type of role I was looking for.

## What persistence is not proof of

If a change in behavior survives across sessions, that doesn't mean anything was trained. Claude Code reads
`CLAUDE.md`, memory files, settings and MCP configs at the start of every session. If one of those changes, the next
session behaves differently, with no change to the model's weights. That is a change to **context** (or settings),
not training. For that reason the scorer runs above used `--setting-sources ""`, `--strict-mcp-config`,
`--no-session-persistence` and an empty working directory. Whatever differed between P1, P2 and C2 is in the files
named here, not in hidden state. Likewise, if my filter keeps behaving the same way tomorrow, that's because
`filter/v1.1.json` is on disk, not because anything learned.
