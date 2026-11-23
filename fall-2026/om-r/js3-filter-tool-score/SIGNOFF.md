# Sign-off — Job-Search Agent 3

## Checked

- **Filter and grounding.** The wrong-version tests failed against both deliberately wrong implementations -- 13 failures on the first run against the stubs, 15 after the blank-quote test was added -- and passed against the real implementation. A separate rule-1 cross-check against JS1's original rule.py ran on all 1,332 postings: both agreed on all 22 relevant matches, zero disagreements. The full suite recorded 91 passing tests. See tests/test_wrong_versions.py, logs 00-03, logs/06_rule1_vs_js1_crosscheck.txt.

- **Reject audit.** I hand-judged 90 rows across groups A, B, and C (88 distinct postings), with no AI assistance on the judgments themselves -- every label and reason is my own. Group B used 38 sampled postings plus 2 forced rule-2 rejects; the BLANK worksheets were committed before any judging. The filter passed all 20 Group C postings as relevant; under my own labeling rule, only C03 held up -- the other 19 were false positives for Priya's specific fit, several of them genuine AI/ML roles whose experience requirements she doesn't meet. See logs/reject_audit/draw_manifest.json and REJECT-AUDIT.md.

- **Rule 4.** The dev/held-out split and the design decisions were committed before rule 4 existed. The tests caught a real regex bug (fixed before any measurement), and rule 4 was locked after dev-only measurement. The held-out label set was read exactly once, logged, and the raw result was committed before any interpretation was written. See EXPERIMENT.md, logs 15-18, commits 277b7d6, 46e7782, 8650e84, ad9ff05.

- **Shortlist.** I ran the live shortlist myself with my own key. The first attempt failed with five 401 errors from an invalid key; the retry, with a working key, returned five valid responses with 38 total claims -- 29 supported, 5 contradicted, 4 insufficient. I checked and confirmed zero fabricated quotes across all five. See SHORTLIST.md and logs 21-22.

- **MCP server.** Client transcripts matched the server's wire logs exactly in every recorded session. The schema regression test failed before the oneOf fix and passed after. During a live audited session, the audit wrapper itself leaked my API key into a local log; Claude caught it before anything was staged. I made the call to delete the affected log and rotate the key, rather than redact it -- and when the replacement key's first copy also failed, I caught the cause myself (a stray bracket character) by checking the key's prefix before retrying. See TOOL-SERVER.md sections 4.1 and 4.3-4.4, logs 25-30.

## How

For the filter, the rule-1 cross-check, and the Chapter 9 experiment, I specified the two wrong versions to test, the B032 must-not-fire case, and the schema-gap cases; Claude wrote the actual test and tool code, and I verified the results against the committed test logs and output. The live runs I personally executed with my own key are logs 21, 22, 29, and 30.

For the reject audit, every one of the 90 hand labels and reasons is my own writing, with no AI drafting -- AI helped only with the labeling rule itself, not with any individual label or reason sentence. That help came from a separate claude.ai chat (as best I recall), not from this Claude Code session, which never saw the worksheets until they arrived already judged. I used Claude to parse the worksheets, check every quote it attributed to me against the committed posting text, and draft REJECT-AUDIT.md's structure. I made the call on how to handle the Group B sample reduction, and I asked specifically for the Group C count to be stated plainly rather than softened.

## Not checked

- Rule 4 against the full Palantir text (Lever's lists field, not just descriptionPlain) -- the audit found 26 affected postings where this would matter.
- Rule 4 against a genuinely fresh set of postings whose labels neither Claude nor I had already seen before designing the rule.
- Whether any of these results carry over to a different collection date, a different candidate, or a second, independent labeler.
- The tool server's behavior under a call budget, a spending limit, an input size cap, or a host allow-list -- none of these are enforced in the server itself. The origin of one MCP session (00:36Z) found in the logs is also unresolved.
- The filesystem-server evaluation is based on reading its published source, not on running it myself.

## Not claiming

Held-out precision on the filter's relevant bucket went from 0/8 to 0/3 -- fewer postings passed, but none were true positives before or after, so this isn't evidence the rule improved precision; it's a structural artifact of held-out having zero true positives to begin with. The one hand-relevant posting in held-out (B032) didn't trigger rule 4, but one data point says very little about how often the rule would wrongly reject a good match.

The 19/20 figure in Group C is exact only for this one collection run and this one persona's fit -- Groups A and B are samples with real sampling error, and A and B overlap and share a seed, so none of these numbers generalize into a miss rate for the full reject pool.

A quote taken directly from a posting can still fail to back up the verdict it's attached to. The shortlist shows this both ways: on 8704363002, a generic boilerplate sentence drove a contradiction flag that didn't reflect anything substantive; on 8175656, the verdict stayed "relevant" even though one of its own supported claims quoted a 2-year experience requirement the posting itself states as a gap.

**Signed: Om Raut, 2026-11-23**

## Driver's seat

| Task | Where I had help | What I did | Why I kept that decision | Evidence |
|---|---|---|---|---|
| Filter contract | Claude implemented the contract and drafted the v1.1.0 amendment. | I set what the amendment had to cover, including why rule 4 was promoted, its known gaps, and keeping the Palantir field issue out of scope for this change. | I wanted the rule and its exceptions written down so I could compare them against the output. | 9426989, 9298665, FRICTIONAL.md entry 1 |
| Filter and rule-1 cross-check | Claude wrote the wrong stubs, tests, filter, grounding code, and the JS1 cross-check. | I specified the wrong behaviors the tests had to catch. | Passing the final version only tells me so much if the tests also let the wrong version through. | 0274afb, 9e2c27a, 667d6dc, logs 00-06 |
| Raw evidence | Claude committed this run's raw posting evidence as an exception to the earlier ignore convention. | I used the saved run as the source for the audit. | The exact posting text matters when a label or a quote gets challenged. | a1988cb, .gitignore |
| Reject sampling | Claude generated the seeded draws and blank worksheets and redrew B on my instruction. | I chose the 2 forced + 38 sampled approach and kept the ambiguity in the write-up rather than smoothing it over. | I wanted both rule-2 cases inspected without quietly mixing them into the random draw. | 6af4411, draw manifest, FRICTIONAL.md entry 4 |
| Reject judgments and report | Claude parsed my worksheets, checked every quote attributed to me, and drafted the report structure. | Every one of the 90 labels and reasons is my own writing. I set the task and asked for the exact Group C count to be stated plainly. | I wanted the count to say whose search we were judging. Several of the rejected roles really did involve AI engineering. | logs/reject_audit/*_draft.md, REJECT-AUDIT.md, 3f25469 |
| Experiment split | Claude computed the split and built the guarded held-out reader. | I went through the prior-exposure limitation honestly and kept it in the interpretation rather than hiding it. | I'd already seen the labels, so I couldn't honestly treat the experiment as blind. | 277b7d6, EXPERIMENT.md sections 1-2 |
| Rule 4 design | Claude implemented rule 4 test-first, fixed the regex bug, and added the full-text Palantir diagnostic. | I set the design decisions and specified that B032 must not trigger rule 4. | I wanted to settle the rule before seeing what the locked version did on held-out. | 46e7782, 8650e84, logs 14-17b |
| Held-out decision | Claude ran the guarded read, committed the result, and drafted the interpretation. | I specified what the promotion and amendment had to account for, and confirmed the prior-exposure and overlapping-interval caveats stayed in. | Fewer postings passing was an observable change. Better precision was a separate claim the numbers didn't actually support. | ad9ff05, 9298665, heldout_access.log |
| Shortlist | Claude wrote the prompt contract, validator, and abstention check, and flagged where my planned example didn't match the real output. | I ran the failed attempt and the live retry myself, with my own key. | The live output showed where the model's verdict and the text it quoted could genuinely pull in different directions. | SHORTLIST.md, logs 21-22 |
| MCP server | Claude built the server, client, and audit wrapper, and found and fixed the oneOf gap. | I specified the schema test cases and ran the live sessions in logs 29 and 30 myself. | I wanted to see what actually happened in a live call, including what the audit actually recorded. | TOOL-SERVER.md, logs 27-30 |
| Key incident | Claude's own audit wrapper caused the leak, then spotted it before anything was staged, fixed the hook, and verified the fix with a fake secret. | I chose deletion over redaction, rotated the key, and caught the stray bracket in the replacement key myself before retrying. | It was my key, so the call on what to do with the affected log and credential was mine to make. | TOOL-SERVER.md sections 4.3-4.4, logs 29-30 |
| This sign-off | A claude.ai chat conversation helped draft the wording from a scaffold. It is the same conversation I used to plan and draft this submission's work throughout, separate from the Claude Code sessions that did the actual implementation. | Final review and signature are mine. | The signature is my call. | This document |
