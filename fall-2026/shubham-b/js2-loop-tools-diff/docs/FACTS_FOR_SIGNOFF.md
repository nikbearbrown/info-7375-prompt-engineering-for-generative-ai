# Facts for the sign-off

Candidate items for the README sign-off. Each is a fact about what was or was not tested. The student decides which go in "Not checked" and "Not claiming".

## Not exercised on real data
- **Exclusion phrases (§6.3)** never fired on the 734 real postings of 2026-10-29 (0 exclusion-gate failures). They are tested only on constructed text in `tests/rule/test_exclusions.py`.
- **Location rescue phrases (§6.4)** never fired on the 734 real postings either (0 of 335 US-based labels came from a rescue). They are tested only on constructed text.
- **Sentence-initial "React"** (e.g. "React quickly to incidents") is a known false positive (§6.2). How often it happens on real postings was not measured.
- **Real résumé refusal** is tested with constructed bad fixtures, never with a real résumé file.

## Known limits of the rule
- The title heuristic misses senior roles whose titles have no seniority marker (CONTRACT §2, §6.1). v1's Claude opinion rejected several such MATCH postings on years of experience.
- New location spellings not in the §6.4 lists are `NOT_ESTABLISHED` until the contract is amended.

## Scope of the evidence
- One board (Stripe on Greenhouse), three live runs on three calendar days (Oct 29 baseline, Oct 30 with 21 new, Oct 31 with none new), plus one seeded pair.
- None of the 21 new postings in the day-2 run was a MATCH, so the live pipeline never had a MATCH case to judge.
- Sampling: 5 hand-picked postings × 4 calls. Prompt experiment: 10 postings per cell, one call each.
- The 20 prompt-experiment hand labels were made by applying the CONTRACT §6 rule, with AI help formatting the entries. They measure agreement with the rule, not independent human judgment.
- One model (`claude-sonnet-5-5`) via Claude Code 2.1.314 for all recorded calls. The CLI has since updated (2.1.316); results are not re-run.

## Network and terms
- The `claude` executable's own network destinations are documented from the docs, not observed or enforced (docs/NETWORK.md).
- Use of `claude -p` on a personal subscription matches the docs' "ordinary use" wording; it is not explicitly documented as supported programmatic use.
