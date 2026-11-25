Computed by Claude Code on 2026-11-24 from committed files, after the fact. Not a new measurement. Rebuild: `python3 tools/card_rebuild_check.py` from the repo root (`--check` compares without writing).

# The blind cards rebuilt with today's card builder

A diagnostic. It changes no rule, no verdict and no frozen result. The audit's cards were built and committed (`c19dd8e`, 2026-11-20 at 11:49 PM ET), and his verdicts frozen (`45fc2c0`, 2026-11-22 at 1:44 AM ET), before `f629b8c` (2026-11-22 at 2:02 AM ET) changed `tools/audit_kit.py`'s `card()`: lines are kept whole at "U.S.", "e.g." and "i.e.", and every line R5's phrases match is shown. Each kit is rebuilt here by its own `build()` into a temporary folder that is deleted afterwards, from `js3/filter-run/2026-11-21T044414Z/`, with FILTER.md pinned to the run's version; nothing is written next to the committed kits. Both kits' answers were already open; the rebuilt answer files are only compared byte for byte.

## In short

- **Audit:** 49 of 55 cards rebuild byte for byte; 6 differ: 09, 10, 17, 31, 35, 36. Card 17 is the one `AFTER-REVEAL.md` already disclosed. Every difference is in the block "Sentences about status, sponsorship or clearance" (6 cards).
- Besides card 17, none of the 5 changed cards gained a line a rule (R1 to R8) reads that the judged card did not show, so none of these changes could have changed his verdict by a rule's line.
- **Held-out:** 30 of 30 cards rebuild byte for byte, and so do the whole files `CARDS.md`, `INSTRUCTIONS.md`, `README.md` and `sealed/answers.json`, as expected: they were rebuilt with `f629b8c` before he labeled them.

## The audit's cards

Rebuilt by `tools/audit_kit.py` with seed 20261121 (published in `SAMPLE.md`) and FILTER.md v1.0. The rebuilt `sealed/answers.json`, `SAMPLE.md` and `INSTRUCTIONS.md` are byte for byte the committed ones: the same sample in the same order (`sealed/answers.json`, SHA-256 `b812a56034ab763ce429eeef5ff2de40e9d688dc454bcc4a2709709b6b107e86`). The text before the first card is the same.

### Card 09: Enterprise Account Executive (Northern CA - Local Government)

- His verdict: Reject ("Sales position, not engineering, and explicitly does not offer visa sponsorship."). The filter: rejected by R4 (also fails R5). Group: random reject.
- Sentences about status, sponsorship or clearance: lost "You must be independently authorized to work in the U.S."; "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."; gained "You must be independently authorized to work in the U.S. We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time.".
- Words gained: none (the same words as before).
- What reads the gained line: R5: "unable to sponsor", on the old card.
- Could it have changed his verdict? No: every phrase a rule reads here (unable to sponsor) was already on the card he judged; the change is the same words, now on one line.

### Card 10: Design Verification Engineer

- His verdict: Reject ("Hardware design verification role, not the backend or software engineering work Jane is targeting."). The filter: rejected by R4 (its only failed rule). Group: random reject.
- Sentences about status, sponsorship or clearance: lost "export control laws and regulations, candidates for this role may need to meet certain legal status requirements as provided in those laws and regulations."; gained "To comply with U.S. export control laws and regulations, candidates for this role may need to meet certain legal status requirements as provided in those laws and regulations.".
- Words gained: "To comply with U.S.".
- What reads the gained line: R5's caution, never a reason to reject: "export control", on the old card.
- Could it have changed his verdict? No rule (R1 to R8) reads this line to decide. It is R5's caution, which never rejects in v1.0, and "export control" was already on the card he judged; the change adds "To comply with U.S." in front.

### Card 31: Software Engineer, CI/CD & ML Infrastructure

- His verdict: ? ("Relevant CI/CD and ML infrastructure engineering, but the export control requirement makes Jane's eligibility unclear."). The filter: kept, score 55. Group: kept sample.
- Sentences about status, sponsorship or clearance: lost "export control laws and regulations, candidates for this role may need to meet certain legal status requirements as provided in those laws and regulations."; gained "To comply with U.S. export control laws and regulations, candidates for this role may need to meet certain legal status requirements as provided in those laws and regulations.".
- Words gained: "To comply with U.S.".
- What reads the gained line: R5's caution, never a reason to reject: "export control", on the old card.
- Could it have changed his verdict? No rule (R1 to R8) reads this line to decide. It is R5's caution, which never rejects in v1.0, and "export control" was already on the card he judged; the change adds "To comply with U.S." in front.

### Card 35: Host Systems Software Engineer

- His verdict: ? ("Host systems software engineering looks relevant, but the export control requirement makes Jane's eligibility unclear."). The filter: kept, score 55. Group: close call: kept near the cutoff.
- Sentences about status, sponsorship or clearance: lost "export control laws and regulations, candidates for this role may need to meet certain legal status requirements as provided in those laws and regulations."; gained "To comply with U.S. export control laws and regulations, candidates for this role may need to meet certain legal status requirements as provided in those laws and regulations.".
- Words gained: "To comply with U.S.".
- What reads the gained line: R5's caution, never a reason to reject: "export control", on the old card.
- Could it have changed his verdict? No rule (R1 to R8) reads this line to decide. It is R5's caution, which never rejects in v1.0, and "export control" was already on the card he judged; the change adds "To comply with U.S." in front.

### Card 36: Localization Manager

- His verdict: Reject ("Localization management requiring 4+ years, and no visa sponsorship."). The filter: rejected by R3 (also fails R4, R5, R7). Group: random reject.
- Sentences about status, sponsorship or clearance: lost "You must be independently authorized to work in the U.S."; "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."; gained "You must be independently authorized to work in the U.S. We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time.".
- Words gained: none (the same words as before).
- What reads the gained line: R5: "unable to sponsor", on the old card.
- Could it have changed his verdict? No: every phrase a rule reads here (unable to sponsor) was already on the card he judged; the change is the same words, now on one line.

## Card 17, already disclosed

`AFTER-REVEAL.md` records this change and his answer to it; the rebuild shows the same line.

### Card 17: Forward Deployed Software Engineer, New Grad - Warp Speed

- His verdict: Keep ("Forward Deployed Software Engineer, New Grad, in New York; matches Jane's experience level and preferred location."); after the reveal: Reject ("No, reject it"). The filter: rejected by R4 (also fails R5). Group: random reject.
- Sentences about status, sponsorship or clearance: lost nothing; gained "U.S. Person Required".
- Words gained: "U.S. Person Required".
- What reads the gained line: R5: "U.S. person", not on the old card.
- Could it have changed his verdict? Yes: the card he judged did not show a line R5 ("U.S. person") reads.

## The held-out cards

Rebuilt by `tools/heldout_kit.py` with seed 2026112103 (published in its `README.md`), the audit's answers (board and posting id only, as the kit reads them) and FILTER.md v1.0. `CARDS.md`: the same; `INSTRUCTIONS.md`: the same; `README.md`: the same; `sealed/answers.json`: the same. Cards: 30 of 30 the same, byte for byte.
