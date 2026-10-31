# Job-Search Agent 1 — The Contract and the Watch

Watches Stripe's public Greenhouse board, reports only postings new since the
last run, and judges each one against a fictional persona's résumé using the
rule in [CONTRACT.md](CONTRACT.md).

*Work in progress. Sections still to come: the Claude judge, sampling report,
prompt experiment, action-surface comparison, sign-off, and driver's seat.*

## Language and toolchain

- Python 3.12.7 (standard library only, nothing to install)
- Tests: `unittest` (standard library)
- Board: `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`
  (the only host on the allow-list)
- Résumé: `examples/rohan-desai.resume.example.json`, a fictional persona from
  The Reallocation Engine's `search/examples/` (`@example.com`, 555 number)

## Commands (from this folder)

Every command must run from this folder. From anywhere else, Python can pick up
an unrelated installed package named `tests` (Anaconda ships one) and fail with
`TypeError: expected str, bytes or os.PathLike object, not NoneType`.

```bash
cd fall-2026/atharva-c/js1-contract-and-watch
```

Run the tests:

```bash
python3 -m unittest discover -s tests -t . -v
```

Check that the tests catch the three wrong versions from CONTRACT.md:

```bash
python3 -m tests.mutants
```

Run the watch (the first run is the baseline and reports 0 new):

```bash
python3 -m agent.watch --resume examples/rohan-desai.resume.example.json
```

Fallback if no real second-day run is possible (output labeled SEEDED):

```bash
python3 -m agent.watch --resume examples/rohan-desai.resume.example.json --replay runs/<earlier-run>/raw.json
```

With `--claude`, each new posting also gets a Claude verdict (a model
judgment, not a fact) from `prompts/revision.txt`. That prompt was chosen on
2026-10-30 *after* the prompt experiment: it lists the valid résumé field
names, and it produced 0 invalid outputs in 20 calls versus 2 in 20 for
`prompts/baseline.txt`. Claude calls use the logged-in `claude` CLI in
headless mode (`claude -p`, tools off, model `claude-sonnet-5-5`); no API key
is stored anywhere.

Each run writes `runs/<UTC timestamp>/raw.json` (the response, byte for byte),
`runs/<UTC timestamp>/report.json` (new postings and the rule's verdicts), and
updates `state/seen_ids.json`.

## What ran

Every run below is real: a live fetch from Stripe's Greenhouse board, not a
replay. Nothing in this folder is seeded. Times are UTC, with US Eastern in
brackets.

| run | when | postings | new | notes |
|---|---|---|---|---|
| `2026-10-30T063746Z` | Fri 30 Oct 06:37 (02:37 ET) | 738 | 0 | **Baseline.** All 738 ids recorded. Started by Claude in my Terminal panel; I watched. |
| `2026-10-30T070159Z` | Fri 30 Oct 07:01 (03:01 ET) | 738 | 0 | Same-day re-run that I ran myself, 24 min after the baseline. Not the second-day run. |
| `2026-10-30T075724Z` | Fri 30 Oct 07:57 (03:57 ET) | 738 | 0 | Another same-day re-run (mine), with `--claude`; no new postings, so no Claude calls. |
| `2026-10-31T040628Z` | Sat 31 Oct 04:06 (00:06 ET) | 746 | **18** | **Second calendar day.** Run by me with `--claude`. |

**Run 2, checked against the raw responses:**
- **Counts:** 18 ids were added and 10 removed between the baseline and run 2
  (738 → 746). The report lists exactly the 18 added ids. Removed postings
  are not reported, as the contract requires.
- **Rule verdicts (records):** 0 of 18 relevant. Most were not engineering
  roles (sales, legal, design, strategy). The four ML-engineer internships
  passed the title check but failed on skills: only Python matched.
- **Claude verdicts (judgments, not facts):** all 18 outputs from
  `prompts/revision.txt` passed the validator, and all 18 said "not
  relevant". They agree with the rule 18/18.

**What run 2 showed that I hadn't caught before:**
- **Skill matching counts ordinary English words.** "React" matched "react
  well under pressure" in an admin posting, and "Go" matched "go-to-market"
  in three sales and product postings. The contract says whole word, any
  case, so the rule applied the contract as written. The contract's skill
  check is weaker than it looks. It didn't change any verdict here, because
  each of those postings already failed on title.
- **An unexplained second model.** In run 2, each Claude call's usage report
  listed `claude-haiku-4-5-20251001` alongside the requested
  `claude-sonnet-5-5`. Earlier calls listed only Sonnet. I don't know which
  model wrote each run-2 verdict.

## Sign-off — Job-Search Agent 1

**Checked:**
- **The allow-list:** `tests/test_contract.py::TestRefuses`. It refuses
  LinkedIn, stripe.com, http, and a look-alike host.
- **Baseline and new-since-last by id:** `TestWatch`, plus
  `python3 -m tests.mutants`, which reports all three contract wrong versions
  as `CAUGHT`.
- **Whole-word skill matching:** `test_wrong_version_substring_go_good`.
- **The Claude output contract:** `tests/test_claude_validator.py`, which
  rejects prose, fences, extra keys, invented fields, and empty citations.
- **Run 2's 18 new postings:** recomputed against the two raw responses
  (18 added, 10 removed).

**How:**
- Claude wrote the tests from my contract; I did not write them before
  reading its code.
- I ran the unit tests on 2026-10-30 and reported 30 passing.
- Claude ran the full suite (37 tests) and the mutant check again on the
  pushed branch on 2026-10-31. All passed, and all 3 wrong versions were
  `CAUGHT`.
- The run-2 recomputation was done by Claude, from the committed raw files.

**Not checked:**
- **Skill matching counts ordinary English words.** "React" matched "react
  well under pressure", and "Go" matched "go-to-market". It's known, and not
  fixed.
- **Which model wrote the run-2 verdicts.** `claude-haiku-4-5` appeared next
  to `claude-sonnet-5-5` in run 2's usage, unexplained.
- **Whether the validator's citations are the right fields.** It checks that
  cited fields exist, not that they are what the reason depends on.
- **Other boards, other days, and pagination.** Only Stripe was run, only on
  2026-10-30 and 2026-10-31.

**Not claiming:**
- That the agent finds good jobs.
- That Claude's judgment is accurate. Its pass rates equal an
  always-"not relevant" guesser on my imbalanced labels.
- That the revision prompt is better in general.
- My own label on 7776179 was wrong. By my later judgment, Claude was right
  about it (see `FRICTIONAL.md`).

**Signed:** Atharva C, 2026-10-31

### Driver's seat

| Part of the task | Claude did | I did | Evidence |
|---|---|---|---|
| Contract | asked questions, formatted my answers | made every decision | `CONTRACT.md` header; first commit |
| Hand labels (20) | showed title and location, flagged contradictions | chose every label, re-answered the flagged ones | `labels/sheet.csv`; "hand labels" commit |
| Prompt experiment | proposed four possible changes, ran the calls | chose the one change (list valid field names) | `EXPERIMENT.md`; `prompts/revision.txt` |
| Imbalanced data | laid out two options | chose to keep the set and report it honestly | `EXPERIMENT.md` limits |
| Code, tests, report drafts | wrote them | approved each commit, ran the tests | `SOURCES.md` |

**Why the decisions stay mine** (my words):
> i took all the decision and it was me who did all the decision making claude was the one to gave me the plan
