# Frictional log — Job-Search Agent 2

1. I committed Claude Code's unedited draft gate by mistake (aedc7034), then replaced it
   with my revised gate (359ee568). Both came before any code; I didn't rewrite history.
2. I told Claude Code "committed, build it" before committing. It checked git, refused,
   and gave me the commands. That's why the gate-first order holds.
3. The first workspace was outside my course repo; I moved it before any code, so every
   hash here exists on GitHub.
4. My first replay command selected `attempt1`, but the live request had timed out
   and the only saved response body was `attempt2`. The resulting empty `--replay`
   argument was refused as `error` (exit 12) with zero requests (`215039252Z`).
   That alone proves only this invalid-input path had no network fallback; replay
   path tests 38–41 test the broader guarantee. I corrected the fixture path for
   the labeled `215313703Z` replay instead of counting the failed command as a demo.
5. The checker printed PASS for that errored run with zero observations, a vacuous
   pass. I had it fixed test-first (41029237).
6. The trace stamped events at write time and wrote the retry after request 2. Fixed in
   85657387; the pre-fix traces keep the defect, and I left them as evidence.
7. The corruption mutates: [null] after the baseline, [0, null] after the normal run
   reloaded it. I found this in the snapshots; it's why my regression test covers two
   save/load cycles.
8. I re-ran the demo at 22:00 from already-corrupted state. The demo I cite is the 21:50
   chain; the 22:00 runs are labeled supplementary in the README.
9. Mutants wv01-host-endsWith and wv07-404-retried survived my tests. I added boundary
   rows 42–43, labeled as post-implementation (4c7ab6b2); 19/19 killed, no test weakened.
10. A defect message reached Claude Code truncated, so it fixed the wrong thing. It still
    found that the loop's timeout path had never been exercised (677b54a8).
11. I referenced boundary rows and a Decision before committing them. Claude Code refused
    to invent them. The replay Decision therefore landed after its code (e871e90d); the
    Decision says so.
12. The first `state.mjs` patch tried ATS-specific validation from board prefixes,
    which broke inherited JS1 tests 20 and 25. I declined to weaken those tests;
    the revised validator preserves generic board compatibility (`c04d1ecf`).
    An earlier recovery Decision also incorrectly proposed an agent-side
    `--approve` rewrite. There is no implemented guarded rewrite route, so I
    superseded that Decision and quarantined the corrupt Lever state by hand
    (`c4f9b555`) instead of claiming the approval path had been exercised.
13. state.mjs and check.mjs disagreed on Greenhouse id 0 and negatives; aligned in
    c04d1ecf and 15ae4789.
14. A null raw id could crash the loop with no run_end; fixed test-first (377fd51c), with
    the interim spec mismatch recorded in GATE.md.
15. Claude Code's first patch test run was against unpatched code because its write had
    been rejected; it reported this itself.
16. An audit found that a Greenhouse response listing ID `101` twice finished as
    `observed` and saved one ID, even though GATE.md required `error: malformed`.
    The independent checker flagged the duplicate (rule 1), but the loop had
    already claimed success. Provider/loop regression tests failed before the
    change and passed after the provider-level fix in `42c9bc52`; I accepted
    that bounded fix. Null raw IDs remain a separate run-level integrity error.
17. A snapshot permission test initially relied on an OS refusing a write to a
    read-only file. Administrator privileges invalidate that assumption. The
    revised test in `ea5e0198` checks permission bits; a mutant without
    `chmodSync` still fails. The complete Node suite was reported 123/123
    in `evidence/node-test-final.txt`.

Accepted from Claude: the GET-only path allow-list (it found that both hosts accept
applications), the header allow-list, the mutant runner, the case-3 regression design
(a NaN-based Set would hide the bug in memory). Modified: the prefix rule, the recovery
Decision, the duplicate-scope wording. Rejected: editing JS1's tests, retiring JS1.

Unresolved: **per-board handling of null raw IDs only** (currently run-wide error 12),
load-before-fetch, the error-run report gaps, the checker vs. the migration
Decision, and UUID case variants. **Duplicate raw IDs are handled per board**
since `42c9bc52` and are no longer an unresolved item.
