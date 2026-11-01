# Job-Search Agent 1 — Contract and Watch

INFO7375, fall 2026 · Chethan T

An agent that watches one public Greenhouse job board (Klaviyo), finds
postings new since the last run, and judges each one against a fictional
persona's résumé (Arjun Mehta) with a rule verdict (`record`) and a Claude
verdict (`judgment`). It never applies, emails, or logs in anywhere.

## Language and toolchain
- Python 3 (ran with 3.13.9); the agent uses the standard library only
- pytest (ran with 8.4.2) for tests
- Claude Code CLI in headless mode, `claude -p` (ran with 2.1.316)
- Greenhouse public Job Board API, `boards-api.greenhouse.io` (only host allowed)

## Commands
From this folder:

```bash
python3 -m pytest tests                       # 33 tests, offline, Claude mocked

python3 -m agent.main                         # watch run: defaults from config.json (klaviyo, persona)
python3 -m agent.main --no-claude             # rule verdict only; skip the Claude call
python3 -m agent.main --replay raw/klaviyo_20261031T175121.json \
  --state seeded_run/state/seen_ids.json --out seeded_run --label SEEDED   # SEEDED replay, no fetch

python3 experiment/select_postings.py         # pick 20 postings to hand-label (seed 7)
python3 experiment/rebalance_labels.py        # one-off rebalance (seed 7); refuses to run twice
python3 experiment/run_dev.py                 # rule vs labels, sampling, baseline prompt on dev
python3 experiment/run_revision.py --dev      # revision prompt on dev
python3 experiment/run_revision.py --heldout  # baseline + revision on held-out (once only)
python3 experiment/action_surface/way2_run.py # one claude -p call that reads a file
```

The first run for a board is the baseline: it saves every posting id and
reports 0 new. Every `claude -p` call runs from a fresh empty temporary folder.

## What ran (all 2026-10-31, EDT)

| time | what | result | commit |
|---|---|---|---|
| 17:51 | real baseline run, Klaviyo board | 156 postings, 0 new; raw response saved | `696b7d2` |
| 22:23 | `run_dev.py` part 1: rule vs my labels (20) | 18/20 agree (dev 10/10, held-out 8/10) | `d1b8aa8` |
| 22:23 | `run_dev.py` part 2: sampling, 5 dev postings × 4 calls | same verdict in every valid run; 5/5 match my label; 1/20 invalid (fenced) | `d1b8aa8` |
| 22:23 | `run_dev.py` part 3: baseline prompt on dev | 10/10 | `d1b8aa8` |
| 22:42 | `run_revision.py --dev` | revision 10/10, 0 invalid | `fa48df0` |
| 22:47 | `run_revision.py --heldout` | baseline 8/10 (2 invalid, fenced); revision 10/10 | `7d8a647` |
| 23:05 | SEEDED second run (`--replay`, 3 ids removed from seen file), Claude on | exactly those 3 new; rule: 3 relevant; Claude: 2 relevant, 1 no verdict (fenced) | `396a46e` |
| 23:06 | action surface way 2: one `claude -p` call reading a file | verdict `relevant`, reply fenced | `0d7bd55` |

Reports: `experiment/rule_vs_labels.md`, `experiment/SAMPLING_REPORT.md`,
`experiment/PROMPT_EXPERIMENT.md`, `seeded_run/SEEDED.md`,
`experiment/ACTION_SURFACE.md`.

## Files
- `CONTRACT.md` — contract v2.1 (v2 written before any code, `046b749`); `CONTRACT_v1.md` — first draft
- `persona_arjun_mehta.json` — fictional persona résumé (@example.com, 555 phone)
- `config.json` — default board and résumé path
- `agent/` — `main.py` (run), `fetch.py` (one host, redirects refused), `resume.py` (refuses non-fictional résumé), `watch.py` (new-posting detection), `rule.py` (`record`), `claude_judge.py` (`judgment`)
- `prompts/` — `baseline.txt` (used by the agent), `revision.txt` (one change: no code fences)
- `tests/` — pytest suite; fake Greenhouse postings in `tests/fixtures/`
- `raw/`, `state/`, `results/` — the real baseline run
- `seeded_run/` — the SEEDED second run
- `experiment/` — labeling rule, labels (v1, v2 kept), experiment scripts, reports, raw Claude replies
- `FRICTIONAL.md` — log of what I tried and changed; `SOURCES.md` — sources and contributions

## Driver's seat

| who | what | evidence |
|---|---|---|
| Me | contract decisions: inputs, outputs, refusals, the rule, wrong versions, failure definition | `046b749` (v2), `5893443` (v2.1) |
| Me | hand labels, before any Claude run | `d91854d` (20 rows), `0531149` (3 rebalanced rows, 22:23:32; first Claude run 22:23:34) |
| Me | chose the rebalance option (3 distinct roles: 1 dev, 2 held-out) | `7617ffe` |
| Me | chose the one prompt change (no code fences) | `54d1a26` |
| Me | conclusions in the sampling and prompt reports | `4f62e57` |
| Claude | agent code, tests, experiment scripts, runners | `76f7a9c`, `9df441c`, `a904c4b`, `f26d505`, `54d1a26`, `9d65674` |
| Claude | drafts of README, SEEDED.md, ACTION_SURFACE.md, SOURCES.md, FRICTIONAL entries (I review) | this commit |

## Sign-off

**Checked**
- `tests/test_rule.py` 01–12, 08b, 13a, 13b: rule verdicts, the Brussels and citizenship-status wrong versions, cited fields
- `tests/test_watch.py` 14–15: baseline reports 0 new; only unseen ids are new
- `tests/test_fetch.py` 16, 16b, 16c: other hosts refused before any request; Greenhouse accepted; off-host redirect refused
- `tests/test_resume.py` 17, 17b: real-looking email refused; fictional persona loads
- `tests/test_claude_judge.py` 18, 18b: reply missing `verdict` rejected; complete reply accepted
- `tests/test_claude_wiring.py` 19–22: no personal info sent; `judgment` label; bad replies (missing key, extra key, extra text) → "no Claude verdict"; Claude missing → "Claude verdict: not run", rule still works
- `tests/test_claude_neutral_folder.py` 23–24: Claude runs from a fresh empty folder outside the repo; fenced reply rejected
- `tests/test_replay.py` 25: `--replay` uses the saved file without fetching

**How**: tests written before code (`76f7a9c` before `9df441c`); hand labels
before any Claude run (`d91854d`, `0531149`).

**Not checked**
- "Bangalore, IN" passes the location check as Indiana
- "Leadership" in a title triggers the Senior/Lead experience check
- the rule uses fixed lists from the contract, not values read from the résumé
- years written as words ("three years") are missed
- my personal Claude Code settings still load in every `claude -p` call
- the second run was seeded (replayed), not a second day
- only one board (Klaviyo)
- only 3 relevant postings in the 20 hand labels

**Not claiming**
- that any job is a good fit for anyone
- that the revision prompt is reliably better

**Signed or withheld**: ____ (name, date)
