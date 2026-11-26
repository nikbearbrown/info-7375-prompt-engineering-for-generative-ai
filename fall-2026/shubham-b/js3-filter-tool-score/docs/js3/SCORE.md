# What moves the score (JS3, Chapter 9)

## 1. Where every number came from

"Hand-set" means someone chose it by reasoning, with no labels involved. "Fitted" means it was
chosen because it scored better on labelled data. "Inherited" means it was carried over from an
earlier layer unchanged.

| Number or object | Value | Where it lives | Origin |
|---|---|---|---|
| R1 role phrase | +4 | FILTER.md §1 | Hand-set (Claude, v0.1). The phrases themselves are inherited from CONTRACT §6.1 (Shubham, JS1) |
| R2 generic word | +2, words "engineer", "developer" | FILTER.md §1 | Hand-set (Claude, v0.1) |
| R2 blockers | 14 specialty words | FILTER.md §1 | Hand-set (Claude, v0.3) after counting which kept postings R2 produced, on **unlabelled** corpus data. Not fitted: no label was consulted |
| R3 seniority | −10, 13 markers | FILTER.md §1 | Weight hand-set; marker list inherited from CONTRACT §6.1 |
| R4 skills | +1 each, cap 3 | FILTER.md §1 | Hand-set. The skill list is inherited (persona résumé, CONTRACT §4); the matching rules inherited (CONTRACT §6.2) |
| R5 topic | +1, 10 words (12 in v0.1) | FILTER.md §1 | Hand-set; "api"/"apis" cut in v0.2 after counting matches on unlabelled corpus data |
| R6 location | +1 / 0 / −10 | FILTER.md §1 | Weights hand-set; the US and non-US signal lists inherited from CONTRACT §6.4 |
| R7 exclusion | −10, 11 phrases | FILTER.md §1 | Weight hand-set; phrases inherited from CONTRACT §6.3 |
| Threshold | 7 | FILTER.md §1 | Hand-set to reproduce the CONTRACT §6.5 bar (role + 2 skills + US); the "2 skills" is inherited from CONTRACT §6.5 |
| Kiran's years (C4) | 4 | `claims.py` `KIRAN_YEARS` | Computed by hand from the persona's experience dates (52 months) |
| Short-text cut-off | 200 characters | `claims.py` `MIN_CONTENT_CHARS` | Hand-set |
| Judge prompt | `prompts/judge.v2.md` | JS1 | **Fitted**: chosen over v1 on the 10 JS1 dev labels (dev 7/10 → 10/10), then confirmed on held-out (6/10 → 10/10). The only number-like object in the system chosen on labels |
| Model | `claude-sonnet-5-5` | `config/agent.toml` | Inherited from JS1 |
| Judge timeout | 180 s | `config/agent.toml` | Inherited from JS1 |
| Audit seed and sizes | 20261125; 40 / 8 / 8 / 12 | FILTER.md §5, `audit.py` | Hand-set, pre-registered |
| Interval level | 95% exact (Clopper–Pearson) | `audit.py` | Convention |
| E3 truncation | 1,500 characters | `experiments.py` | Hand-set for this experiment |

## 2. The changes, one object at a time (predictions written before any run)

Held-out labels: the 10 JS1 held-out labels (Shubham, 2026-10-30), on the postings exactly as
labelled (the 2026-10-29 hand-check raw). The 15 JS1 tuning labels (dev 10 + sampling 5) are
reported beside them but are not the test. A label `MATCH` counts as relevant; the filter's
"kept" is compared with it.

| ID | Object | One change | Prediction (before running) |
|---|---|---|---|
| E1a | the filter file | v0.1 → v0.2: cut "api", "apis" from R5 | No held-out decision changes: the held-out postings are mostly role-phrase titles that get R5 from other words, and the cut flipped only generic-title specialty jobs on the corpus |
| E1b | the filter file | v0.2 → v0.3: add the R2 blockers | At most one held-out decision changes (the held-out set has a stratum of title-fail postings, which is where blockers act) |
| E2 | a setting | threshold 7 → 6 on v0.3 | Agreement stays the same or falls by 1–2: a lower bar can only add kept postings, and every extra one is a NO_MATCH under the CONTRACT rule unless it has a role phrase, two skills and a US location |
| E3 | the context given to Claude | judge v2 with the posting content whole vs cut to its first 1,500 characters | Agreement falls from about 10/10 to 7–9/10, and the misses are MATCH postings judged NOT_RELEVANT, because the skills a posting lists sit in its later "what you'll need" section |

Each E3 condition runs once (one `claude` call per held-out posting, no retry), from an empty
directory with no tools, through the JS1 judge path.

## 3. Results

All runs on 2026-11-25 (UTC 05:5x), after the predictions above were committed (`5448d94`).
Files: `data/js3/experiments/e1-e2-filter.json`, `e3-full.json`, `e3-trunc1500.json`; each E3
call's full attempt log (argv, raw stdout, cost) under `data/js3/experiments/e3-*/calls/`.

| ID | Change | Held-out agreement (10) | Tuning agreement (15) | Prediction held? |
|---|---|---:|---:|---|
| baseline | FILTER v0.1 | 9/10 | 11/15 | — |
| E1a | v0.1 → v0.2 (cut "api") | 9/10 → 9/10, no decision changed | 11 → 11 | Yes |
| E1b | v0.2 → v0.3 (R2 blockers) | 9/10 → 9/10, no decision changed | 11 → 12 (8075570 "Integration Engineer, Professional Services" now rejected, as labelled) | Yes (0 changes, at most 1 predicted) |
| E2 | threshold 7 → 6 on v0.3 | 9/10 → 9/10 | 12 → 12 | Yes, at the "stays the same" end: no labelled posting scores exactly 6 |
| E3 | judge v2, full content → first 1,500 characters | **10/10 → 7/10** (all 20 replies valid) | not run | Yes: all three misses are MATCH postings judged NOT_RELEVANT (8039548, 8206731, 8267736) |

**The one held-out disagreement in E1/E2 is by design, not a bug.** 8194606 ("Frontend Engineer,
Data Product Experiences", location "N/A") is NO_MATCH under the JS1 rule because the location is
not established; FILTER.md §1 R6 gives an unknown location 0 instead of a veto, so the filter keeps
it (score 8) and the claim checker then says "I cannot tell" on C3. The labels measure distance
from the JS1 rule, and this is a place where the JS3 filter chose to differ. The three tuning
disagreements left (7476555, 8127182, 8234357) are the same choice (mixed or N/A location) or the
topic word standing in for a second skill.

**E1 and E2 barely move the held-out number because the held-out set is small and was drawn for
a different question.** All 10 are Stripe postings, mostly with role-phrase titles; the v0.2/v0.3
changes act on generic titles at other boards. On the full corpus the same changes flipped 12
postings (FILTER.md §8). Ten labels cannot show that effect, in either direction. The audit
verdicts, once written, measure it on the flipped postings directly
([`audit/AUDIT_REPORT.md`](audit/AUDIT_REPORT.md), "The v0.2/v0.3 changes, judged").

**E3: what changed and what did not.** Same prompt file (SHA-256 `effb1d0b…`), same model
(`claude-sonnet-5-5` served on all 20 calls), same résumé, same postings; only the posting content
in the context was cut. The cut saved about 10% of input tokens (71,228 → 63,902 across the 10
calls; $0.324 → $0.276) and cost three of ten answers. In two of the three truncated misses Claude saw the
problem and said so in `uncertainties` — "The content is truncated mid-sentence, so required
technologies or exclusion phrases may exist in the missing text" (8039548; similar for 8206731) —
and still answered NOT_RELEVANT, because the v2 prompt offers no "cannot tell" label. In the third
(8267736) it did not mention the cut at all; it counted the one skill it could see (AWS). The skill lists sit after the
first 1,500 characters (Stripe's company boilerplate fills the start), so the skill gate failed on
text Claude never received. A context change moved the score more than any filter change, without
touching a word of the prompt.

## 4. What persistence is not proof of

Several things in this project persist across sessions: the agent's seen-ID state
(`data/*/state.json`), `FILTER.md` and its frozen versions, the prompt files, the saved raws, and,
in the Claude Code sessions that built it, memory files that a new session reads at start. When
behaviour changes from one session or run to the next (65 postings kept by filter v0.1, 53 by
v0.3; a different Claude answer on a re-run), the cause is one of those files, the context, or the model service,
never training on the labels. **Nothing in this project trained a model.** `claude-sonnet-5-5`'s
weights were the same for every call; the judge runs with `--no-session-persistence` from an empty
folder, so no call sees another. The filter's "learning" from v0.1 to v0.3 is two edited lines in a
text file, made by Claude after counting, and it can be undone by restoring the file. The reverse
also holds: the same files can give a different answer on another day if the served model changes,
which is why every call records `model_served` and `claude_version`. A behaviour that persists is
evidence that a file persisted, not that anything learned.
