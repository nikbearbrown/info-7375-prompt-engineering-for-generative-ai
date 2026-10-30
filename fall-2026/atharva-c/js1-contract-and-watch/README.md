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

Each run writes `runs/<UTC timestamp>/raw.json` (the response, byte for byte),
`runs/<UTC timestamp>/report.json` (new postings and the rule's verdicts), and
updates `state/seen_ids.json`.

## What ran

*(Filled in only with runs that actually happened.)*
