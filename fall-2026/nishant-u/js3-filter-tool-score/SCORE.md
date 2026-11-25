# SCORE — what moves the score (Job-Search Agent 3, nishant-u)

Chapter 9 asks two things of a scorer: where each number came from, and what happens when one object changes while everything else is held fixed. Written 2026-11-25 from the code at `409b995`.

## Which object this is

Of Chapter 9's five mutable objects (weights, prompt, context, tools, settings), the JS3 scorer has **no weights and no prompt**.
- **No Claude call:** `agent3/` and `audit/make_kit.py` make no Claude call and no network call. They read saved JS2 responses only.
- **Nothing is fitted:** no number in JS3 was fitted by an optimizer on labels.
- **What did change:** the change from v1 to v2 is a change to the **filter file**, a hand-written rule set, which Chapter 9 counts as configuration. It was made by a person after reading audit labels.

The v2 filter persists across runs, but persistence is not training: nothing learned the 45 audit labels. A person read them and edited the rules, and the change lives in `FILTER.md` and `agent3/filter.py`, where it can be diffed and reverted.

## Inventory: every number, list, threshold and prompt in the JS3 path

Origins:
- **Hand-set:** chosen by a person, or by Claude Code while implementing, and written into the code or FILTER.md.
- **Hand-set after measurement:** a person chose it after reading audit labels. No optimizer fitted it.
- **Fitted on labels:** learned by an optimizer from labels. Nothing in JS3 is.
- **Inherited:** copied unchanged from earlier work.

| Item | Value | Where | Origin |
| --- | --- | --- | --- |
| F1 role words | data, analytics, analyst, scientist, machine learning, ML | `filter.py` `ROLE_WORDS`; FILTER.md F1 | **Inherited** from JS1 `data/requirements.json` `title_terms` (hand-set in JS1) |
| F2 exclusions, v1 | manager, director, head, lead, intern | `VERSIONS[1]` | **Inherited** from JS1 `exclude_terms` |
| F2 exclusions, v2 | manager, director, head, intern | `VERSIONS[2]` | **Hand-set after measurement**: Nishant cut "lead" after audit row 4 (FILTER.md change 1) |
| F3 state endings | `, AL` … `, WY` (50 states, no DC) | `STATE_ENDINGS`, read from `data/requirements.json` | **Inherited** from JS1 `us_location_markers` |
| F3 "Remote with US" markers | US, USA (exact case), U.S., United States; "remote" any case | `US_MARKER`, `REMOTE` | **Hand-set** by Claude Code as its reading of FILTER.md v1's "says Remote with US"; not yet confirmed by Nishant |
| F3 office form, v2 | `US <State name> (<City>) - Office`, 50 states + DC | `US_OFFICE`, `US_STATE_NAMES` | **Hand-set after measurement**: Nishant's change 7. The pattern comes from Poshmark's location format; the state-name list is the standard one |
| F4 skills | Python, SQL, Databricks, Unity Catalog, Power BI, LangGraph, MLflow, Mem0, Delta Lake, AWS | `shipped_skills()` from `data/resume.example.json` | **Inherited** from the fictional persona résumé (Reallocation Engine `search/examples/priya-nair/`), restricted to the four shipped lists named in JS1's `skill_lists` |
| F4 practices, v2 | A/B testing, A/B test, A/B tests, experimentation, LLM evaluation, LLM-as-judge | `PRACTICES` | **Hand-set after measurement**: Nishant's change 2, drawn from Priya's résumé bullets |
| min skills | 1 | `MIN_SKILLS` | **Inherited** from JS1 `min_skills`, repeated in FILTER.md F4 ("at least 1") |
| Abstention threshold | 300 characters after HTML removal | `MIN_TEXT_CHARS` | **Hand-set** in FILTER.md v1 (drafted with Claude, approved by Nishant). Never fired on real data (shortest posting 2,679) |
| Unverified-empty board | abstain | `evaluate()`, from JS2 `report.json` | **Hand-set** in FILTER.md v1; the status itself is **inherited** from the JS2 loop |
| C3 contradiction patterns | cannot/unable to/will not … sponsor; without … sponsorship; no sponsorship; requires … US citizen(ship); security/secret/TS-SCI clearance | `C3_CONTRADICT` | **Hand-set** by Claude Code from FILTER.md's C3 wording |
| C3 support patterns | will/can/we … sponsor/support … visa/H-1B; visa sponsorship is available; sponsors visas | `C3_SUPPORT` | **Hand-set** by Claude Code from FILTER.md's C3 wording |
| C4 patterns | onsite / on-site / on site, in-office / in office, hybrid; remote | `C4_CONTRADICT`, `C4_REMOTE` | **Hand-set** by Claude Code from FILTER.md's C4 wording |
| C4 schedule words, v2 | office, offices, day, days, schedule | `C4_SCHEDULE` | **Hand-set after measurement**: Nishant's change 8 (audit row 9) |
| C4 order | location before text; contradiction before remote | `label_c4()` | **Hand-set** by Claude Code (an interpretation, recorded in the docstring) |
| Quote window | the sentence, at most 150 characters either side of the match | `sentence_around()` | **Hand-set** by Claude Code |
| Rank order | most supported claims, then fewest contradicted, then posting ID | `rank_key()` | **Hand-set**: FILTER.md wrong version 3 rules out keyword count; Claude Code chose the exact tie-breaks |
| Dedupe | by `system:board:id`, latest `fetched_at` wins | `run.collect()` | **Hand-set** in Nishant's instruction (dedupe key) and by Claude Code (latest copy wins) |
| Audit sample | seed 20261124; 30 random rejects, 5 close calls, 10 accepts | `audit/make_kit.py` | Sizes **hand-set** by Nishant; seed, tier order and the borderline-word list **hand-set** by Claude Code |
| JS2 budgets | 5 boards, 10 requests, 60 seconds per run | JS2 `GATE.md`, `report.json` | **Inherited** from JS2. Not used by JS3 at run time, but they decided which postings exist to score |
| Claude prompt | `prompts/revision-1.md` | used by JS2 `agent/run.py` (`--prompt`) | **Inherited** from JS2 (frozen after JS2's dev experiment). **Not used in the JS3 path**, which makes no Claude call |

## One change at a time, measured on held-out labels

**Labels used:** Nishant's JS1 hand labels, `experiment/labeling/labels.csv`, split by `experiment/heldout_ids.json` (10 held-out) and `experiment/dev_ids.json` (10 dev).
- The seals match `experiment/SPLIT.md`: raw file `3c10b536…`, held-out IDs `1cc26d9d…`, dev IDs `fa756026…`.
- The filter was run on the same posting text the labels were made from (`runs/2026-10-29-1/raw.json`).
- Only the filter version changed; the data, résumé and code path were held fixed.
- The measure is verdict agreement only: filter accept vs label `relevant`. The labels' `my_failed_check` column was not compared.

### Two limits that decide what these numbers mean

1. **The labels apply a different rule.** They were made under the JS1 rule: R1–R4, the same keyword checks as v1, applied by hand ("Ctrl+F each of Priya's 10 shipped skills"). They are not the audit rule's judgment ("would I want Priya to see this?"). So v1 agrees with them almost by construction, and every v2 change that departs from the keyword rule must lose agreement on them, whether or not it is an improvement in the audit rule's sense.
2. **The held-out postings were not untouched when v2 was chosen.**
   - Four of the 10 held-out postings were also in the reject audit that motivated v2: `8801507002` (audit row 44), `8845103002` (row 27), `8804205002` (row 45) and `8806617002` (row 36).
   - Rows 44 and 27 are two of the four postings change 2 was designed to fix.
   - Two dev postings were also audited: `8660923002` (row 12) and `8832899002` (row 8, also targeted by change 2).
   - The JS1 labels themselves were not used to choose v2, but these postings were. Under SPLIT.md's own held-out rule, these four should count as development evidence from now on. **Nishant:** record this in SPLIT.md's exposure log if you agree.

### Results

Agreement = postings where filter accept matches label `relevant`. Intervals are 95% Clopper-Pearson.

| Set | Filter | Agreement | 95% interval |
| --- | --- | ---: | --- |
| Held-out, all 10 | v1 | 10/10 (100%) | 69.2% – 100% |
| Held-out, all 10 | v2 | 8/10 (80%) | 44.4% – 97.5% |
| Held-out, the 6 not in the audit | v1 | 6/6 (100%) | 54.1% – 100% |
| Held-out, the 6 not in the audit | v2 | 6/6 (100%) | 54.1% – 100% |
| Dev, all 10 | v1 | 10/10 (100%) | 69.2% – 100% |
| Dev, all 10 | v2 | 9/10 (90%) | 55.5% – 99.7% |
| Dev, the 8 not in the audit | v1 | 8/8 (100%) | 63.1% – 100% |
| Dev, the 8 not in the audit | v2 | 8/8 (100%) | 63.1% – 100% |

v2 bundles three verdict-changing rule changes, so each was also measured alone. Each row adds one change to v1 and holds everything else fixed:

| Filter | Held-out | Dev |
| --- | ---: | ---: |
| v1 | 10/10 | 10/10 |
| v1 + change 1 only (no "lead" exclusion) | 10/10 | 10/10 |
| v1 + change 2 only (résumé practices count for F4) | 8/10 | 9/10 |
| v1 + change 7 only (US office form) | 10/10 | 10/10 |
| v2 (changes 1 + 2 + 7) | 8/10 | 9/10 |

Change 8 changes C4 quotes, not verdicts, so it cannot move this score.

### What the results show, and what they don't

- **Every v2 disagreement comes from change 2,** on exactly three postings: `8801507002`, `8845103002` and `8832899002`.
  - Each is labeled `not_relevant` (R4: no shipped skill named) under the JS1 rule.
  - Each was judged **yes** in the reject audit under the audit rule.
  - The drop from 10/10 to 8/10 is therefore the two rules disagreeing, which is the change Nishant decided to make. It is not evidence that v2 is worse at finding postings Priya should see.
- **On the postings not touched by the audit, v1 and v2 agree with the labels equally** (6/6 held-out, 8/8 dev). There, the change made no difference that these labels can detect.
- **Ten cases can't show much.** One disagreement moves agreement by 10 points, and every interval above is 30 to 55 points wide. No difference between v1 and v2 here is distinguishable from chance, and "v1 100% vs v2 80%" must not be read as a measured rate for either filter.
- **These labels cannot test v2 fairly.** That would need labels made under the audit rule, on postings not used to choose v2, judged before seeing v2's reasons: for example, a fresh random sample of v2's rejects and accepts.

## Persistence is not proof of training

v2's behavior persists across runs and sessions because the rule text changed in `FILTER.md` and `agent3/filter.py`, which every run reads again.
- **What did not happen:** nothing was trained. No weights exist in this scorer, and no Claude model's parameters were touched.
- **The test that separates the two:** run `python -m agent3.run --filter-version 1`. v1's verdicts come back exactly, because the change lives in the configuration, not in anything that learned.
  - Checked 2026-11-25: the re-run's `results.json` is byte-identical to the committed `out3/filter-run/results.json`.
  - Its `shortlist.md` differs from the committed one by a single quote: the C2 "Uses SQL" quote for `faire:8806617002`, corrected by the quote fix in `409b995`. That is a code fix, not a learned change.
