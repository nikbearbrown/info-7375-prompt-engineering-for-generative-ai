# Prompt experiment (Chapter 2)

**Question:** does one sentence in the prompt contract make Claude's verdicts match my hand labels
better, on postings I did not tune it on?

Drafted by Claude Code from the saved data (see SOURCES.md for who did what).

## Bottom line: two results, read separately

| | What it is | baseline-v1 | revision-v2 | Status |
|---|---|---:|---:|---|
| **Original 20** | The split made by seed 2608 before labeling, and labeled blind. This is the experiment the brief asks for | dev 10/10, held-out 10/10 | dev 10/10, held-out 10/10 | **No difference.** All 20 labels are NOT_RELEVANT, so this split cannot show whether the change helps |
| **Supplement 4** | Added after seeing that the original labels were all one class | dev 1/2, held-out 1/2 | dev 2/2, held-out 2/2 | **Exploratory only.** The held-out gain is one posting, already familiar (the worked example, with a smoke call) |

So this experiment does **not** fully meet the brief's "held-out set you did not look at until the end" in the
way that matters: the only held-out case that could show a difference was not unseen. Clean evidence would need a
new evaluation on fresh postings labeled before anyone looked. That was not done.

## Order of events (each step is a commit, so the order can be checked)

| Step | Commit | Who |
|---|---|---|
| Split: seeded shuffle of the 52 engineering-titled postings from run 1, seed **2608** | `9ed2e88` | Ashwin chose the seed; Claude Code ran `select` |
| Labeling protocol, seven decisions, written before seeing the split's postings | `20b01fb` | Ashwin wrote it; Claude Code saved it |
| 20 hand labels, shown in shuffled order without the dev/held-out split | `6773f06` | Ashwin |
| Found: all 20 labels NOT_RELEVANT, so an always-no prompt would pass every case | — | Claude Code reported it; Ashwin chose to add a supplement |
| Supplement tool, and the 4 postings it picked | `dbf0ef4`, `04bcea5` | Claude Code |
| 4 supplement hand labels, same protocol, labeled without seeing their split | `f9bd958` | Ashwin |
| `baseline-v1` on dev | `76bd1ce` | Claude Code ran it |
| `revision-v2`: the one change, chosen from the dev failure | `d932e3b` | Ashwin chose the change; Claude Code wrote the sentence |
| `revision-v2` on dev | `d10abd6` | Claude Code |
| Both prompts on held-out, once each, with `--final` | `914d40d` | Claude Code |

**The supplement.** `python3 -m jobwatch.lab supplement` adds *every* engineering-pool posting that
the contract's seniority check allows and the original split left out. That rule gives exactly 4. The
same seed 2608 splits them 2 dev and 2 held-out. `selection.json`, `labels.json` and the protocol were
left byte-for-byte unchanged. Results always report the original 20 and the supplement separately.

## The one change

`prompts/revision-v2.md` is `prompts/baseline-v1.md` plus this sentence, and nothing else:

```text
Experience: a posting that asks for up to 2 years of experience (including "2+ years") or is titled Engineer II or below is within reach for a New Grad, while a posting that asks for 3 or more years is not.
```

Why this one: the only dev failure was 7855793003 (Software Engineer II), where Claude answered
NOT_RELEVANT in all five calls (four in sampling, one on dev) because "2+ years" is "above a New Grad
level". The protocol's point 3 accepts 2+ years. The baseline never said what "experience level" allows.

## Results

Pass = a valid reply **and** verdict equal to my hand label. An invalid reply counts as a fail.
Every call was a real `claude -p` call (model `claude-opus-5-5`), and every reply is saved in `results/*/replies/`.

| Prompt | Set | Pass | Original 20 | Supplement 4 | Invalid replies |
|---|---|---:|---:|---:|---:|
| baseline-v1 | dev | 11/12 | 10/10 | 1/2 | 0 |
| revision-v2 | dev | 12/12 | 10/10 | 2/2 | 0 |
| baseline-v1 | held-out | 11/12 | 10/10 | 1/2 | 0 |
| revision-v2 | held-out | 12/12 | 10/10 | 2/2 | 0 |

- **Held-out failure under baseline-v1:** 7855798003 (Software Engineer II - Recommendations), with the same
  "2+ years is above New Grad" reason. Under revision-v2 it passes, and no posting that passed before failed.
- **For comparison, the written rule** (CONTRACT.md, deterministic) agrees with my labels on 10/12 dev postings
  and 12/12 held-out postings. On dev it disagreed on 7792539003 (Android/Kotlin, which my protocol excludes
  as mobile) and 8041054003 ("3+ years"). The rule has no experience check.

Regenerate this table with `python3 -m jobwatch.lab summary`.

## How little this shows

- **The held-out improvement is one posting.** Only one held-out posting is RELEVANT by my labels, so
  "11/12 → 12/12" is a single case changing. With 12 cases, one flip is not a measured improvement rate.
- **Without the supplement there would be no comparison.** On the original 20, both prompts score 10/10,
  because every label is NOT_RELEVANT and Claude said NOT_RELEVANT to all of them. Those cases test only
  that Claude rejects senior roles.
- **The supplement was added after looking.** It was added because the first labels were all one class.
  It follows a stated rule and adds every candidate, but the decision to add it came after seeing the labels.
- **The held-out posting was not new to me.** 7855798003 is the contract's worked example. My protocol's
  "2+ years" sentence was written after Claude Code asked how I would treat that posting, before the
  split placed it in held-out. Claude also saw it once in a development smoke test on 2026-10-30. The
  prompt was not tuned on it, but my label for it was not blind. Saying so does not make it unseen: the one
  held-out case that improved is a familiar posting, so this result is **not clean evidence that the revision
  generalizes**. A fair test needs new held-out postings labeled before anyone looks at them.
- **This experiment is kept as it ran.** Nothing was rerun or replaced afterwards. The later seeded watch replay
  (`action-surfaces/3-watch-seeded/`) used a dev posting and is not part of this experiment.
- **The revision tells Claude my rule.** It works because it states protocol point 3. That shows the baseline
  was missing a criterion, not that Claude got better at judging.
- **One labeler, one board, one model, one run per prompt per set.** The sampling report showed verdicts
  were stable on these postings, but each experiment cell is still a single call.
