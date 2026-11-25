Computed by Claude Code on 2026-11-24 from committed files, after the fact. Not a new measurement. Rebuild: `python3 tools/boilerplate_check.py` from the repo root (`--check` compares without writing).

# Do the score's sentence-based points come from boilerplate?

A diagnostic. It changes no rule, no verdict and no frozen result. Read from `js3/filter-run/2026-11-21T044414Z/verdicts.json`, `js3/filter-run/2026-11-22T084738Z/verdicts.json`, the saved board answers they name (checked against their SHA-256), FILTER.md Section 7 versions 1.0 and 1.1 and `persona/jane-doe.json`.

The score gives points from sentences in two ways (`score()` in `job_agent/filter.py`): a topic group earns +5 when one sentence has a topic word and an action word, and R7 costs -10 when a years sentence names the company (a company word). FILTER.md Section 5 names the risk this checks: a posting can rank high from topic words in an "about us" sentence. A sentence counts as boilerplate when the same normalized sentence (whitespace collapsed, a leading bullet dropped, lower case) is in many postings of the same board: at least 5, or at least 20% of the board's saved postings (rounded up). A point depends on boilerplate when no other sentence of the posting earns it.

## In short

- **v1.0** (145 topic points on 99 kept postings, cutoff 60):
  - at 5 postings: 4 topic points on 2 postings (Software Engineer - Apollo Platform, lever-palantir, 2 copies) depend on boilerplate; without them 2 scores fall from 60 to 50, 2 of them below the cutoff; the top 10 stays the same.
  - at 20% of the board: no point depends on boilerplate.
- **v1.1** (138 topic points on 99 kept postings, cutoff 50):
  - at 5 postings: 4 topic points on 2 postings (Software Engineer - Apollo Platform, lever-palantir, 2 copies) depend on boilerplate; without them 2 scores fall from 60 to 50, none below the cutoff; the top 10 stays the same.
  - at 20% of the board: no point depends on boilerplate.
- The most widely shared sentence that earned a topic point is in 17 of lever-palantir's 307 saved postings.
- Company-word points on kept postings, in both runs: 0, so none can depend on boilerplate.
- No posting in either top 10 depends on boilerplate, at either threshold.

## FILTER.md v1.0: filter run 2026-11-21T044414Z

99 kept postings; 145 topic points (one per topic group a posting earned, +5 each); the shortlist cutoff is 60. Boards: ashby-openai 854 saved postings, greenhouse-verkada 348 saved postings, lever-palantir 307 saved postings.

Company-word points (R7 "cannot tell", -10) on kept postings: 0. The other sentence-based penalty, R6's "cannot tell" for a season start: 0.

How widely each topic point's sentence is shared:

| Postings of the same board with the sentence | Topic points |
|---:|---:|
| 1 | 121 |
| 2 | 14 |
| 3 | 1 |
| 4 | 5 |
| 7 | 2 |
| 17 | 2 |

### Boilerplate: at least 5 postings

The threshold per board: ashby-openai 5, greenhouse-verkada 5, lever-palantir 5.

- Topic points whose recorded sentence is boilerplate: 4.
- Topic points that depend on boilerplate (no other sentence earns the group): 4, on 2 postings.
- Company-word points whose sentence is boilerplate: 0; that depend on it: 0.

| Board | Postings with the sentence | Distinct titles among them | Points it gave | Sentence (first 120 characters) |
|---|---:|---:|---|---|
| lever-palantir | 17 | 7 | Developer tools ("CI/CD") to Software Engineer - Apollo Platform `8f308f3e`; Developer tools ("CI/CD") to Software Engineer - Apollo Platform `afea07a8` | "Experience building high-quality software in a fast-paced CI/CD development environment" |
| lever-palantir | 7 | 3 | Distributed systems ("distributed systems") to Software Engineer - Apollo Platform `8f308f3e`; Distributed systems ("distributed systems") to Software Engineer - Apollo Platform `afea07a8` | "Experience developing and managing highly-available distributed systems" |

Without the points that depend on boilerplate:

| Posting | Score | Rank | Recommended (cutoff 60) |
|---|---|---|---|
| Software Engineer - Apollo Platform (lever-palantir `8f308f3e`) | 60 to 50 | #48 to below the cutoff | yes to no |
| Software Engineer - Apollo Platform (lever-palantir `afea07a8`) | 60 to 50 | a removed duplicate to below the cutoff | yes to no |

In all, 2 kept postings change rank: 2 of the postings above, and no other.
The top 10 is unchanged, in the same order; none of its postings depends on boilerplate.

### Boilerplate: at least 20% of the board's saved postings

The threshold per board: ashby-openai 171, greenhouse-verkada 70, lever-palantir 62.

- Topic points whose recorded sentence is boilerplate: 0.
- Topic points that depend on boilerplate (no other sentence earns the group): 0, on 0 postings.
- Company-word points whose sentence is boilerplate: 0; that depend on it: 0.

Without the points that depend on boilerplate, no score changes, so no rank or recommendation changes.
The top 10 is unchanged, in the same order; none of its postings depends on boilerplate.

## FILTER.md v1.1: filter run 2026-11-22T084738Z

99 kept postings; 138 topic points (one per topic group a posting earned, +5 each); the shortlist cutoff is 50. Boards: ashby-openai 854 saved postings, greenhouse-verkada 348 saved postings, lever-palantir 307 saved postings.

Company-word points (R7 "cannot tell", -10) on kept postings: 0. The other sentence-based penalty, R6's "cannot tell" for a season start: 0.

The caution (-10 for a sentence with "export control") is on 9 kept postings, through 1 sentence, shared by 27 postings of ashby-openai (boilerplate at 5 postings, not at 20% of the board). It is not a topic or company word, and it is a legal statement about the role, so it is counted here and never removed below.

How widely each topic point's sentence is shared:

| Postings of the same board with the sentence | Topic points |
|---:|---:|
| 1 | 114 |
| 2 | 14 |
| 3 | 1 |
| 4 | 5 |
| 7 | 2 |
| 17 | 2 |

### Boilerplate: at least 5 postings

The threshold per board: ashby-openai 5, greenhouse-verkada 5, lever-palantir 5.

- Topic points whose recorded sentence is boilerplate: 4.
- Topic points that depend on boilerplate (no other sentence earns the group): 4, on 2 postings.
- Company-word points whose sentence is boilerplate: 0; that depend on it: 0.

| Board | Postings with the sentence | Distinct titles among them | Points it gave | Sentence (first 120 characters) |
|---|---:|---:|---|---|
| lever-palantir | 17 | 7 | Developer tools ("CI/CD") to Software Engineer - Apollo Platform `8f308f3e`; Developer tools ("CI/CD") to Software Engineer - Apollo Platform `afea07a8` | "Experience building high-quality software in a fast-paced CI/CD development environment" |
| lever-palantir | 7 | 3 | Distributed systems ("distributed systems") to Software Engineer - Apollo Platform `8f308f3e`; Distributed systems ("distributed systems") to Software Engineer - Apollo Platform `afea07a8` | "Experience developing and managing highly-available distributed systems" |

Without the points that depend on boilerplate:

| Posting | Score | Rank | Recommended (cutoff 50) |
|---|---|---|---|
| Software Engineer - Apollo Platform (lever-palantir `8f308f3e`) | 60 to 50 | #47 to #89 | yes to yes |
| Software Engineer - Apollo Platform (lever-palantir `afea07a8`) | 60 to 50 | a removed duplicate to a removed duplicate | yes to yes |

In all, 43 kept postings change rank: 1 of the postings above, and 42 others that move up.
The top 10 is unchanged, in the same order; none of its postings depends on boilerplate.

### Boilerplate: at least 20% of the board's saved postings

The threshold per board: ashby-openai 171, greenhouse-verkada 70, lever-palantir 62.

- Topic points whose recorded sentence is boilerplate: 0.
- Topic points that depend on boilerplate (no other sentence earns the group): 0, on 0 postings.
- Company-word points whose sentence is boilerplate: 0; that depend on it: 0.

Without the points that depend on boilerplate, no score changes, so no rank or recommendation changes.
The top 10 is unchanged, in the same order; none of its postings depends on boilerplate.

## What this does not change

No rule changes. Whether a shared requirement line should earn topic points, or count once per board, is the owner's call, in a later FILTER.md version; v1.0 and v1.1 stay as they are.
