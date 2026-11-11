# FRICTIONAL.md: Job-Search Agent 2

Deepak Kumaran T S · INFO 7375 · fall 2026

I wrote these entries retrospectively, on 2026-11-10 after the work, from private/SESSION_LOG.md and the git commits. The claude.ai chat helped me organize my notes and phrase some reflections, and in a final pass it checked my facts against the commit record and corrected wrong hashes, times and attributions. Claude Code did not write in this file.

## Entries

### 2026-11-10, before 13:40 ET: planning the architecture (retrospective)
- Tried / expected: I planned the assignment flow in a claude.ai chat before the first capture.
- What happened: we discussed board choices and execution design.
- What I did: I accepted the claude.ai chat's recommendations for the board choice and for keeping the LLM out of the loop. I also accepted the GATE draft without reading all of it.
- What Claude contributed, and what I accepted, changed or rejected: the claude.ai chat provided the GATE draft and the architecture recommendations, which I accepted.
- What I understand now / still do not understand: I understand the importance of isolating planning logic from mechanical execution. With a deterministic loop, the permission policy is enforced by code, not by a prompt.
- Evidence and next step: the GATE.md provenance line in the starter commit 72ebcfe. Next: setup and Gate 0.

### 2026-11-10 13:40 to 14:03 ET: Gate 0 and repository state (retrospective)
- Tried / expected: I expected to commit the starter files smoothly for Gate 0.
- What happened: Claude Code held the starter commit because .gitignore was missing (likely a hidden dotfile not copied from the zip), which meant private/ would have been committed. In the capture, the Lever US endpoint returned [] for a board hosted in the EU, while the EU host returned 6 postings.
- What I did: I had Claude Code create the .gitignore and check it with git check-ignore before committing. I accepted the chat's recommendation to use the EU host for Phase 3 and the US host for Phase 4.
- What Claude contributed, and what I accepted, changed or rejected: Claude Code protected the repo by refusing to commit without a .gitignore. I accepted that.
- What I understand now / still do not understand: a 200 OK response with an empty list is not proof that there are no jobs; here it meant querying the wrong regional endpoint.
- Evidence and next step: c2fd4b3 and 79c6644 (capture), 72ebcfe (starter files with .gitignore). Next: Gate 1.

### 2026-11-10, Gate 1 (committed in 891446a): predictions and the spec review (retrospective)
- Tried / expected: I expected to pass Gate 1 with my POLICY predictions.
- What happened: all 16 prediction cells were still empty, so Claude Code blocked the commit twice. The claude.ai chat's draft contained a wrong W12 example and an unsourced Lever claim.
- What I did: I picked my 16 predictions in the claude.ai chat, and Claude Code inserted them verbatim. I wrote in the provenance line that I had not read all 21 answers.
- What Claude contributed, and what I accepted, changed or rejected: Claude Code ran a 21-item review and flagged the unsourced Lever claim (item 12). In its second round it flagged the wrong W12 example (item 5). I accepted both corrections. For B11, I kept DENY while Actual is ALLOW, and the mismatch stands.
- What I understand now / still do not understand: predictions and specs get checked line by line. My B11 guess was wrong against my own spec.
- Evidence and next step: 891446a. Next: Gate 2.

### 2026-11-10 14:38 ET: Gate 2 boundary and test violations (retrospective)
- Tried / expected: I expected clean boundaries between JS1 imports and JS2 logic.
- What happened: 4 JS1 tests needed a JS1 capture that the import had left out. The full pytest then showed 17 source-scan failures, all in JS1 modules. A closure check found inputs.py on the loop path. Claude Code had described the JS1 modules as "imported unchanged", which was false for inputs.py and cli.py. The max_seconds test had a wrong expectation. The commit that reverted inputs.py (539af84) is broken on its own, because loop.py still imported a function it removed, a result of the commit order the chat asked for.
- What I did: I chose option A for the capture (331f4f2). I chose the chat's stricter version of Claude Code's option (a): a named legacy list, a closure test and a byte-identity test. I approved restoring inputs.py and moving the checks into persona.py (9d5f957). I had the max_seconds test's old and new assertions checked against GATE §2.
- What Claude contributed, and what I accepted, changed or rejected: Claude Code proposed option (a), and corrected its own max_seconds test before it was committed.
- What I understand now / still do not understand: visual checks are not enough for "imported unchanged" claims; they need byte-identity checks.
- Evidence and next step: d3ae571, a4b6be7, 331f4f2, 539af84, 9d5f957, ebd5f33, 0add776, cbee62b. Resolved before Gate 2 closed.

### 2026-11-10 15:07 to 15:10 ET: Gates 3 and 4 (retrospective)
- Tried / expected: I ran the real jobs for Gates 3 and 4.
- What happened: the real run ended INCOMPLETE, exit 3 (6dcb895). The finished-wrong-answer run ended FINISHED while verify flagged SUSPECT, exit 2 (b568846, 5aef78e). Stripe had 776 postings in the 13:40 capture and 775 in both runs. The claude.ai chat had wrongly called the capture "my own manual curl".
- What I did: Claude Code's README attributed the curl to Claude Code and asked me to confirm. I accepted its wording, then ran my own curl check.
- What Claude contributed, and what I accepted, changed or rejected: Claude Code handled the attribution of the manual curl correctly.
- What I understand now / still do not understand: live boards change counts during test windows, so a prior count is only a rough reference.
- Evidence and next step: 6dcb895, b568846, 5aef78e, 196853e. Next: Gate 5a.

### 2026-11-10 15:37 to 15:52 ET: Gate 5 patch scope and testing (retrospective)
- Tried / expected: I needed a test for the defect review and a clean patch.
- What happened: my first commit (49ce61d) held only the test outline as comments, with no Python, so pytest ran no tests. The Python test was then drafted in the claude.ai chat. Claude Code's patch (3a4c1fb) exceeded scope by adding a summary rewrite branch.
- What I did: I read the drafted test, ran it red and committed it (7309446) before the patch. I read the diff, ran my own red and green commands (7ebb3ba), and chose Revise. I kept the extra branch and made it legitimate with amendment A-3 (6b12eef).
- What Claude contributed, and what I accepted, changed or rejected: Claude Code wrote the patch, and during review the suite test (f39ce0d) that covers the scope expansion.
- What I understand now / still do not understand: the patch author should not write the test that judges it.
- Evidence and next step: 49ce61d, 7309446, 3a4c1fb, 7ebb3ba, 6b12eef, f39ce0d.

### 2026-11-10 16:02 ET: unresolved edge cases (retrospective)
- Tried / expected: I evaluated edge cases to see what remained unchecked.
- What happened: candidates 2 and 3 remained unresolved. Redirects were never tested against a real server, and the prior-count heuristic only checks for drops to 0, so a board losing half its postings would pass.
- What I did: I documented these unresolved states as known gaps in my sign-off.
- What Claude contributed, and what I accepted, changed or rejected: Claude Code highlighted the redirect gap, which I accepted.
- What I understand now / still do not understand: in-process testing is not enough to verify actual network behavior like live HTTP redirects.
- Evidence and next step: SIGNOFF.md, "Not checked".
