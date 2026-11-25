# Sign-off: Job-Search Agent 3

## Checked
- The permission policy: tests B01 to B16 in tests/js2/test_boundary.py, written by Claude Code in JS2.
- The filter rules, whole-word matching, boilerplate exclusion, abstention and precedence: tests/js3/test_js3_filter.py, written by Claude Code from my FILTER.md.
- Wrong versions F01 to F09 (F05 in tests/js3/test_js3_shortlist.py): each patched in and shown caught, tests written by Claude Code.
- The tool server's protocol handling, bad input and path traversal: subprocess tests written by Claude Code.
- The audit interval: computed by audit-stats and recomputed independently by scripts/clopper_pearson_check.py.
- Reproducibility: in a fresh clone, the dataset, the filter output, the E1 and E2 decisions, the audit facts, the C1 to C5 measurements and the interval check were rebuilt byte for byte. The collection run, the shortlist claims and judge output, the E3 judge runs and experiments/results.* were not rebuilt. Since f0568bc, audit-stats on the HEAD audit sheet does not reproduce the committed facts, which come from the 65c9863 snapshot (README).

## How
- By hand: my audit verdicts (65c9863), my claim labels (cec6a48), my held-out labels (8625eea), my Gate decisions, and the commands I ran for the claims, the held-out restore (3d130ae) and the held-out report (db0670b).
- Before reading Claude's code: FILTER.md v1 (494cfdd), committed before any filter code.
- With Claude's help: Claude Code wrote the code and nearly all tests; a claude.ai chat drafted FILTER.md sections 3 to 7, formatted sections 0 to 2 from my answers, and drafted these fill-ins from the committed facts.

## Not checked
1. My final audit verdicts contain 15 checklist answers that contradict the question wording; I did not correct them.
2. My held-out labels are my first pass and were never relabeled; their stratum B pattern suggests mis-keys.
3. The title and location gates were never audited independently of the filter's own reading of them.
4. The filesystem server's source commit is inferred, not verified.
5. I did not read the providers' terms of use or the spec pages myself (SOURCES.md).

## Not claiming
- That filter v1 finds relevant postings well: it keeps 3 of 1,285 and missed 9 of 30 audited rejects.
- Anything about postings outside the two held-out strata.
- That any change C1 to C5, E1, E2 or E3 improved anything: none did.
- That the client stayed within the tool server: it read sealed data with its own tools.

## Signed or withheld
Signed with the Not-checked items above: Deepak Kumaran T S, 2026-11-25.

---

# Driver's seat

What Claude should do, what I should do, and why the judgment that a posting is worth my time stays mine. Evidence points to a commit, file or test.

| Part | What Claude did here | What I did here | Why it stays mine | Evidence |
|---|---|---|---|---|
| The filter document | Drafted sections 3 to 7, formatted 0 to 2, reviewed it three times (Claude Code), plus one critique in the claude.ai chat | Chose every rule, weight, threshold and decision | The filter encodes what Riley wants, which only I decide | 494cfdd |
| The held-out labels | Drew and sealed the set | Labeled it | A label is a judgment about Riley, not a computation | 30c52ef, 8625eea, 3d130ae |
| The reject audit verdicts | Drew the samples, computed the interval | Gave the verdicts | The audit checks the filter against my judgment, so the judgment cannot come from the filter's builder | 65c9863, fb02ee4, 520fee6 |
| The shortlist claim labels | Wrote the claims and pre-labels | Labeled every claim | Whether a quote states a claim is the judgment being tested | cec6a48 |
| The tool server and its trust decision | Built it, ran both servers, wrote the declared-versus-actual facts | Made both trust decisions | Trust is accepting a risk on my own machine, which only I can accept | ae74ac0, 4bcabca |
| What moves the score | The claude.ai chat drafted E1 to E3 in the Phase 6 plan; Claude Code chose E2's setting (the location weight instead of the threshold) and E3's arm details, and ran E1 to E3 | Accepted the experiment plan, ran the held-out report, read the results | Deciding what a null result means is interpretation, not arithmetic | fefe60e, db0670b |
| Whether a posting is worth my time | Scores and summarizes | Decides | A posting is worth Riley's time only by her goals, which a score can approximate but not decide | AUDIT.md, SHORTLIST.md |
