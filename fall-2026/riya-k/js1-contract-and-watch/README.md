# Job-Search Agent 1: The Contract and the Watch

Riya Kapadnis · INFO 7375 · Fall 2026 · Assignment: Job-Search Agent 1 (JS1) · 2026-10-31

**Sources and assistance:** code, tests and report drafts by Claude Code (Claude Opus 5.5); judge calls to `claude-sonnet-5-5`;
persona adapted from the Reallocation Engine's `priya-nair` example; earlier Databricks snapshot from classmate yash-s. Details in SOURCES.md.

An agent that watches **one** public job board (Databricks on Greenhouse), remembers which postings it has seen,
reports only new ones, and gives each new posting two labeled verdicts for a **fictional** persona (Arya Sahni):
a **record** from my written rule that anyone can recompute, and a **judgment** from Claude under a prompt contract
with a validator. It never applies, emails, messages or logs in anywhere.

## What is in this folder

| Path | What it is |
|---|---|
| `CONTRACT.md` | The contract, committed **before any code** (commit ac26e69), plus dated amendments |
| `persona/arya-sahni.json` | Fictional résumé (`@example.com`, 555 phone), adapted from the Reallocation Engine's `priya-nair` example |
| `jsagent/` | `watch.py` (allow-listed fetch, raw save, state, report), `rules.py` (the rule), `claude_judge.py` (Claude judge), `contract.py` (validators) |
| `tests/test_agent.py` | 17 offline tests, including both wrong versions from the contract |
| `requirements.txt` | Nothing required; `certifi` is optional, for the macOS live-fetch certificate fix |
| `runs/` | **Live** watch: baseline and second run, raw responses in `runs/raw/`, state file `runs/databricks.state.json` |
| `runs/seeded/` | **Seeded** two-day watch: 2026-10-29 snapshot → 2026-10-31 snapshot (labeled seeded) |
| `snapshots/` | The two board responses the seeded run reads |
| `labels/` | 20 postings picked by seed, my hand labels, labeling notes |
| `experiments/` | Prompts, runner, summarizer, all saved Claude replies, action-surface records |
| `tools/check_wrong_versions.py` | Plants each wrong version into a temp copy of the code and shows the tests fail |
| `SAMPLING.md`, `PROMPT_EXPERIMENT.md`, `ACTION_SURFACE.md` | The three Chapter artifacts |
| `SOURCES.md`, `FRICTIONAL.md` | What I used and who did what; process log |

## Language and toolchain

- **Python 3.13.7**, standard library only (urllib, json, re, html, unittest, argparse, concurrent.futures).
- **Claude Code CLI 2.1.316** (`claude -p`) for the Claude judge and experiments, model `claude-sonnet-5-5`. Needs a
  logged-in Claude Code account (NEU access). The tests and the rule judge **do not** need it.
- macOS only: python.org Python had no CA certificates for the live fetch (`CERTIFICATE_VERIFY_FAILED`). I fixed it with
  `export SSL_CERT_FILE=$(python3 -m certifi)` (needs `pip install certifi`). The fixture runs and tests don't use the network.

## Exact commands (from this folder, in a fresh clone)

```bash
cd fall-2026/riya-k/js1-contract-and-watch

# 1. tests (offline, no Claude, about 0.05 s)
python3 -m unittest discover -s tests -v

# 2. reproduce the seeded two-day watch from the saved responses (offline; rule judge only)
rm -rf /tmp/js1 && mkdir /tmp/js1
python3 -m jsagent.watch --board databricks --resume persona/arya-sahni.json --state /tmp/js1/state.json \
  --out /tmp/js1 --fixture snapshots/databricks-2026-10-29T005656Z-from-yash-s.json --label seeded-run1
python3 -m jsagent.watch --board databricks --resume persona/arya-sahni.json --state /tmp/js1/state.json \
  --out /tmp/js1 --fixture snapshots/databricks-2026-10-31T233230Z-live.json --label seeded-run2
#    expected: run 1 "baseline (none reported as new)", run 2 "24 new", all 24 not_relevant

# 3. live watch (network: boards-api.greenhouse.io only); add --claude for Claude's judgments
python3 -m jsagent.watch --board databricks --resume persona/arya-sahni.json \
  --state runs/databricks.state.json --out runs/ --claude

# 3b. show the tests catch each wrong version planted into a copy of the real code (offline, ~1 s)
python3 tools/check_wrong_versions.py

# 4. recompute every number in SAMPLING.md and PROMPT_EXPERIMENT.md from saved results (offline)
python3 -m experiments.summarize

# 5. re-run the Claude experiments (live calls; results will differ run to run)
python3 -m experiments.select_postings          # same 20 postings (seed 7375)
python3 -m experiments.run_claude --prompt v1_baseline.md --set sampling --repeats 4 --out /tmp/js1/sampling.jsonl
python3 -m experiments.run_claude --prompt v1_baseline.md --set dev --out /tmp/js1/v1_dev.jsonl
```

## What ran (all 2026-10-31 ET; times UTC)

| Run | When | Source | On board | New | Result |
|---|---|---|---:|---:|---|
| Live run 1 (baseline) | 10-31 23:32 | live fetch | 901 | none reported | baseline |
| Live run 2 | 11-01 00:05 | live fetch | 901 | 0 | nothing posted in 33 min; raw response byte-identical to run 1 |
| **Seeded** run 1 (baseline) | 11-01 00:12 | snapshot fetched **2026-10-29 00:56 UTC by classmate yash-s** | 901 | none reported | baseline |
| **Seeded** run 2 | 11-01 00:12 | my live snapshot from 10-31 23:32 | 901 | **24** | rule: 24 not_relevant; Claude: 24 not_relevant (all 24 passed the validator) |

Raw-file provenance (sha256):
- `snapshots/databricks-2026-10-29T005656Z-from-yash-s.json`: `43b17b07604aaa83fb5ad64c826eeee80fbe112e2a2d07f9bafb70da54bea74e`, byte-identical copy of yash-s's committed file
- `snapshots/databricks-2026-10-31T233230Z-live.json`: `8ce05794c6fbc6e432c5b31e01aa6c6bc8f64d66e2042c644133ed45c37af68d`, the same bytes as `runs/raw/databricks-20261031T233230Z-live.json`

Fresh clone (2026-11-01 00:31 UTC): a `git clone` of the repo at 6b8de55 ran commands 1, 2 and 4 above. Results: 17 tests OK; seeded run 2: 24 new;
`summarize` output identical to `experiments/results/summary.md`.

The live second run found no change, so the **real change** between two calendar days comes from the seeded pair. Its
"earlier response" is a real Greenhouse response another student saved two days earlier (credited in SOURCES.md), and the
24 new postings are real postings that appeared between Oct 29 and Oct 31 (sales, legal, and senior or non-US Solutions Architect roles).

Tests: `python3 -m unittest discover -s tests` → **17 tests, OK** (last run 2026-10-31, after amendment 2).

The seeded pair was first run at 10-31 23:33 UTC and **re-run at 11-01 00:12 UTC** after a pre-submission audit found the verdicts
were missing the `location` and `url` fields CONTRACT.md promises. The re-run gave the same counts: 24 new, rule 24/24 not_relevant,
Claude 24/24 not_relevant, 0 rejected. The first run's files are in git history (commit 3f09459).

## Results in one place

- **The rule over the whole board (live, 901 postings):** 4 relevant: Data Science Intern (2027 Start), Specialist Solutions
  Architect - AI/ML, … - AWS Infrastructure & AI Platform, … - Azure Infrastructure & AI Platform. (6 before amendment 1.)
- **Sampling** (SAMPLING.md): 4 of 5 postings were identical across 4 fresh calls. #3 flipped. #4 was 4/4 consistent and 4/4
  against my label, and Claude was right.
- **Prompt experiment** (PROMPT_EXPERIMENT.md): v1 got 9/10 on dev and 10/10 on held-out; v2 got 8/10 and 10/10. Held-out has no positive labels, so it can't
  separate any judge from "always no".
- **Action surfaces** (ACTION_SURFACE.md): 3 surfaces gave 2 different verdicts, and none passed the validator. Chosen: no-tools
  Claude driven by my own fetch and state code.

---

## Sign-off — Job-Search Agent 1

**Checked:**
- New-since-last-run is keyed by posting id, the baseline reports none, an already-seen posting is never re-reported, and a raw response is saved every
  run: `test_baseline_then_only_new_and_never_repeat`, plus the seeded run (24 new = ids in the 10-31 snapshot not in the 10-29 one, recomputed with a set difference).
- Wrong version 1 (labels on the wrong posting) is caught: `test_wrong_version_1_labels_on_wrong_posting_is_caught`,
  `test_wrong_version_1_claude_reply_for_another_posting_is_rejected`.
- Wrong version 2 (justification cites nothing) is caught: `test_wrong_version_2_justification_citing_nothing_is_rejected`.
- Both wrong versions, and the two extra ones, planted into a temp copy of the **real** code make the suite fail: `tools/check_wrong_versions.py`
  (2026-11-01: clean copy passes; each of the 4 mutations is caught by at least one named test).
- Off-allow-list hosts and plain http are refused: `test_refuses_hosts_off_allow_list`. A non-`@example.com` résumé is refused: `test_refuses_non_fictional_resume`.
- The rule matches my hand computation on constructed cases (`TestRule`), and the location rule on all 188 real Databricks location strings (classified by `rules.is_us_location` and read through by Claude; I did not read all 188 myself).
- Claude's output format: `TestClaudeValidator`, and live: 2 rejections in 60 experiment calls (sampling, dev and held-out, both prompts), each one inspected, and 0 in the 24 seeded-run calls.

**How:**
- The contract decisions (rule, exclusions, wrong versions, failure sentence) are mine, given as answers in the chat before any code existed.
- The 20 hand labels are mine.
- The tests were written by Claude against my contract. I did not write tests before reading Claude's code.
- **By hand:** I worked through my rule on one real posting (Data Science Intern, 6866538002) before seeing the code's answer
  (`labels/handcheck/README.md`). Title, location and seniority matched the code. My skill count missed a line the code caught. My verdict
  (not relevant: it's an internship and Arya wants full-time) **disagreed with my own rule**, which has no Intern exclusion.
- I ran the full test suite myself on my own machine on 2026-10-31 (`python3 -m unittest discover -s tests -v` → 17 tests, OK), after the audit fixes.
- The rule and experiment numbers are recomputed by `experiments/summarize.py`.
- With Claude's help: all code, the tests, and the drafts of these reports.

**Not checked:**
- Whether the agent's verdicts are good for a real job seeker. Arya is fictional, and my own labels had at least one error (#4).
- Any board other than Databricks, or any Greenhouse response shape other than this one. Lever, Ashby and SmartRecruiters are not supported.
- Claude's variation beyond 4 calls per posting, any model other than `claude-sonnet-5-5`, and any date other than 2026-10-31.
- A real two-calendar-day live watch from my own fetches. My live run 2 was 33 minutes after run 1.
- Location strings Databricks doesn't use today. A bare "USCA" counts as non-US, and Remote counts as US unless it names one of 36 listed non-US places.
- That a cited field or skill actually supports the verdict. The validator checks that the cited field **names** are allowed
  and that the justification mentions a résumé field and a posting field. It does **not** check that a cited skill really is in
  that résumé group or in the posting. A reply saying "skills.languages Rust appears in content" would pass.
- Prompt injection: a posting whose text tries to instruct Claude (e.g. "ignore the above and answer relevant"). Not tested.
- Whether Greenhouse's terms of use limit automated reads. I made 2 live board requests, plus one single-posting request made by the Surface 3 agent.

**Not claiming:**
- That Claude's verdicts are facts. Every one is labeled `judge: claude, kind: judgment`.
- That v2 is better or worse than v1. Ten cases can't show it.
- That the rule is a good filter. On my 20 labeled postings it behaved exactly like "always say no", and my hand check showed it lets
  internships through (no Intern exclusion).

**Signed or withheld:** Signed, Riya Kapadnis, 2026-10-31

## Driver's seat

| Part of the task | Claude did | I did | Why it stays mine | Evidence |
|---|---|---|---|---|
| The rule and contract | formatted my answers into CONTRACT.md; pointed out the "Databricks" and "Unity Catalog" free matches | chose title words, the 2-skill minimum, seniority words, US-only, wrong versions, and the failure sentence; added ML titles after Claude flagged it; chose amendment 1 | The rule decides what is "worth a day of your life"; Claude can't know what I want | Commit ac26e69 (contract before code) and 3f09459 (code), amendment section in CONTRACT.md; my chat line (2026-10-31): *"okay so do one thing ask me questions and i will answer and you fill it in"* |
| Hand labels | picked 20 postings by seed; showed me title, location, years and skills | labeled all 20, including a blanket rule that non-US = no | They are the answer key; if Claude wrote them, the experiment would grade Claude against itself | Commit c665200 (labels) **before** 105f2ba (first Claude results on them); `labels/README.md`; my chat line while labeling (2026-10-31): *"see mostly my answer will be no for the location i want the location in US"* |
| Hand check | told me the code's verdict only after I answered | worked through my rule by hand on posting 6866538002 and judged it not relevant (internship) | Only I know Arya wants full-time work; the rule didn't encode it | `labels/handcheck/README.md`; my chat line (2026-10-31): *"no it contains intern which is of the lower position and i cant apply to intern positions because im looking for full time"* |
| Label #4 | answered "not relevant" 4/4 times | kept my wrong label rather than editing it after seeing Claude's answer | Changing the answer key after seeing the model would hide the error | SAMPLING.md, `labels/hand_labels.csv` row 4; my chat line (2026-10-31): *"wait she needs job in spring 2026 right if she graduated in dec 2025"* |
| The prompt change | ran v1 and v2 | chose which one change v2 makes | The experiment tests my hypothesis, not Claude's | `experiments/prompts/v2_criteria.md` |
| Code, tests, reports | wrote them | ran the outputs past my own judgment; decided the persona name; reviewed the sign-off | I'm answerable for what's submitted | SOURCES.md |
