# Acceptance cases: turn these into pytest yourself, BEFORE Claude Code writes the agent

These are the tests "I wrote before reading Claude's code". Write them against the interface you
fix in CONTRACT.md, using small hand-made fixtures in tests/acceptance/fixtures/ (label them as
constructed). Commit them in the same commit as CONTRACT.md or the one right after it.

Who writes which (change this line if you write more yourself):
- Cases 9, 10 and 13 (the two wrong versions and the hand-predicted verdicts): written by me in tests/acceptance/.
- All other cases: written by Claude Code in tests/spec/ from this list, committed before any implementation.

Drive every test through the seam in CONTRACT.md Interfaces, using the fakes in tests/conftest.py:
`cli.main(argv, opener=FakeOpener(...), anthropic_client=FakeClient(...), now=fixed_datetime)`,
with `tmp_path` as the working directory. No test touches the network.

Watch
1. No state file: run on fixture A reports 0 new, and the state file then holds every id in A.
2. Run on A, then on B (A minus one id, plus two ids): exactly those two are reported new. The removed id is not reported new.
3. Run on B again: 0 new.
16. Run on A, then B (drops id X), then A again (X is back): X is not reported new on the third run.
4. Duplicate id inside one response is reported once.
5. Integer id 123 and string id "123" are the same posting.
6. Corrupt state file: the run exits non-zero and the state file is unchanged.
7. Board tokens "acme/../x", "acme.evil.com", "ACME", "" are refused before any request is attempted.
8. A URL on any other host, or a redirect response, is refused (mock the opener; no real network).

Judges and validator
9. (catches wrong version: wrong pairing) Shuffling the input postings leaves every posting_id's record verdict unchanged, and every posting citation's value appears in THAT posting.
10. (catches wrong version: cites nothing, or cites what isn't there) A verdict with zero résumé citations, zero posting citations, or a citation whose path or value isn't in the document is rejected.
11. A citation whose path doesn't resolve, or whose value isn't present at that path, is rejected.
12. Claude output wrapped in ```json fences, with extra keys, with a mismatched posting_id, or with verdict "maybe" is rejected, and the raw text is kept.
13. Your rule on 3 hand-made postings gives the verdicts you predicted by hand (write the predictions in the test).
14. Whole-word matching: test the matcher directly. "ML" does not match "HTML Email Developer"; it does match "ML-Ops Engineer".
17. No API key: every judgment has status not_run, reason no_api_key, and the fake client is never called.

Privacy
15. A résumé with an email outside @example.com, or phone 617-555-9999, or no "fictional": true, is refused,
    and the refusal message does not contain the offending value. Build the bad email at runtime
    ("me" + "@" + "gmail.com") so no non-example.com address sits in a tracked file; the presubmit
    check would flag it otherwise.
