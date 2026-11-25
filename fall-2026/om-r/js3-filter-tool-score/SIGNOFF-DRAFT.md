# SIGNOFF-DRAFT.md: skeletons for Om to fill in

> Everything in `[[ ]]` is Om's to write. Lines starting `HINT:` point at
> evidence that exists in this repository. They are pointers, not entries:
> delete each one once you have used or rejected it. Nothing here is a claim
> that Om checked anything.

## Sign-off — Job-Search Agent 3

```text
Sign-off — Job-Search Agent 3
Checked:      [[which properties, by which tests or runs — name them]]
How:          [[for each item above: by hand / by a test I wrote myself / by a
              test I specified and ran myself / by reading the diff or output /
              by my own hand judgments / with Claude's help — say which]]
Not checked:  [[at least three real items]]
Not claiming: [[what this agent does not show]]
Signed or withheld: Om Raut, [[date]]
```

### HINT: evidence available for "Checked" (you decide what you checked)

- HINT: **FILTER.md's two wrong versions.** The tests are in
  `tests/test_wrong_versions.py`.
  - Before any implementation they error (`logs/00_tests_before_impl_exists.txt`,
    `FAILED (errors=2)`).
  - Against the deliberately wrong stubs they fail
    (`logs/01_tests_vs_wrong_stubs.txt`, 13 failures). A blank-quote test was
    then added, and the rerun shows 15 failures
    (`logs/01b_tests_vs_wrong_stubs_rerun.txt`; FRICTIONAL.md entry 2).
  - Against the real `js3/filter.py` and `js3/grounding.py` they pass
    (`logs/02_tests_vs_real_impl.txt`, `logs/03_all_tests.txt`).
  - Commits: `0274afb` (tests + stubs), `9e2c27a` (real filter and grounding).
- HINT: **Rule 1 against JS1's original rule.** `tools/rule1_vs_js1.py` runs
  JS1's `agent/rule.py` in a subprocess over the same 1,332 postings. Result:
  "JS1 rule relevant 22, JS3 rule 1 pass 22; disagreements 0"
  (`logs/06_rule1_vs_js1_crosscheck.txt`, `667d6dc`).
- HINT: **The reject audit's hand judgments.** There are 90 labels (88
  distinct postings) across groups A (30), B (40) and C (20), in
  `logs/reject_audit/*_draft.md`.
  - The BLANK worksheets were committed before any judging (`6af4411`).
  - The draws are seeded (20261121) and reproducible
    (`logs/reject_audit/draw_manifest.json`).
  - The report is `3f25469`, REJECT-AUDIT.md.
- HINT: **The Chapter 9 dev/held-out discipline.**
  - The split was committed before rule 4 existed (`277b7d6`, seed 7375,
    `logs/experiment/split.json`).
  - Design problems and two decisions were committed before any rule-4 code
    (`46e7782`).
  - Rule 4 was written test-first: `logs/15` failing against the no-op stub,
    `logs/16` with 2 failures from a real regex bug, `logs/16b` passing.
  - It was locked after the dev measurement (`8650e84`, logs 17/17b).
  - There was a single guarded held-out read: `logs/experiment/heldout_access.log`
    has exactly 1 entry (2026-11-22T01:51:05Z).
  - The raw held-out result was committed before any interpretation
    (`ad9ff05`). The interpretation and promotion came after (`9298665`,
    EXPERIMENT.md sections 7–8).
- HINT: **The source-grounded shortlist.**
  - 5 real Claude calls, 5/5 `end_turn` and valid; 38 claims (29 supported,
    5 contradicted, 4 insufficient); 0 fabricated quotes.
  - Logs: `logs/22_shortlist_live_run.txt`, `logs/shortlist/`.
  - Tests first: `logs/19` erroring, `logs/20` passing.
  - Commit `0fb5cef`, SHORTLIST.md.
  - Log 21 is the run with the invalid key (five 401s), kept.
- HINT: **The MCP tool server.**
  - Real transcripts are in logs 25, 26, 29 and 30. The client's record and
    the server's wire log are identical in each.
  - The audited sessions measured writes, network and process spawns
    (logs 26 and 30).
  - Tests first: `logs/23` failing, `logs/24` passing.
  - Commit `19bba0a`, TOOL-SERVER.md.
- HINT: **The oneOf schema gap, found then fixed.** It was found by probing
  during the self-evaluation. `logs/27_mcp_schema_gap_test_before_fix.txt`
  shows the test failing and `logs/28_mcp_schema_gap_test_after_fix.txt`
  shows it passing (TOOL-SERVER.md 4.1).
- HINT: **The environment-leak fix** (TOOL-SERVER.md 4.3). The fixed hook was
  checked offline with a fake secret. Logs 29 and 30 were checked for key
  material. Both key-leak searches (the full-history `git log --all -p`
  search and the working-tree `grep -rn`, each for the Anthropic key prefix)
  returned nothing after `19bba0a`.
- HINT: **The key incident: who did what, from the record.**
  - Claude's audit wrapper caused the leak, and Claude spotted the key while
    summarizing the first with-key log, before anything was staged.
  - You decided to delete rather than redact, and rotated the key.
  - You caught the corrupted copy of the new key (the stray bracket) by
    checking its prefix before the retry (log 29, TOOL-SERVER.md 4.4).
  - Word "caught" accordingly.
- HINT: Full suite today: 91 tests, OK (`python3 -m unittest`).

### HINT: for "How", one fact to get right

Every test file, tool and script in this repository was **written by
Claude**. That includes the wrong-version tests and stubs, the rule-4 tests,
the shortlist and MCP tests, `tools/rule1_vs_js1.py`, `tools/mcp_client.py`
and `tools/mcp_audit.py`.

- "By a test I wrote myself" applies only to a test you wrote. It does not
  cover tests you *specified*, such as FILTER.md's two wrong versions, the
  B032 must-not-fire check, or the two schema-gap cases.
- Tests you specified and *ran yourself* are a different category, and still
  a legitimate one.
- What is yours by construction: the 90 hand labels and the labeling rule in
  `logs/reject_audit/*_draft.md`, and the runs you executed with your key
  (logs 21, 22, 29, 30).
- Say for each label whether any tool or AI helped. The record here doesn't
  show it either way.

### HINT: candidates for "Not checked" (real gaps found in this build; pick and word your own)

- HINT: **Palantir content.** Lever `descriptionPlain` hides the requirement
  text in `lists`. 26 postings are affected, and it was measured but never
  fixed (FRICTIONAL.md entry 1; the FILTER.md v1.1.0 amendment). Rule 4 is
  largely blind on Palantir for the same reason.
- HINT: **Rule 4's known gaps** (FILTER.md amendment 2026-11-22; EXPERIMENT.md
  section 7, point 3):
  - "Senior" is not in the title-word list (C04, C01);
  - the year threshold is 3, not 2 (C14);
  - there is no detector for experience outside Priya's stack (C06);
  - any qualifying path counts (C20).
- HINT: **The designers had seen every held-out label.** Every held-out label
  was read, by you and by Claude, before rule 4 was designed (EXPERIMENT.md
  section 2, "Prior exposure"; section 3, Problem 1). Held-out was fresh to
  the code, not to the designers.
- HINT: **Held-out precision is degenerate.** It was 0/8 → 0/3: held-out has
  no true positives in the relevant bucket, so false negatives couldn't be
  tested. Only one hand-relevant held-out posting exists (B032), and its pass
  is weak evidence (EXPERIMENT.md section 7, points 1, 2 and 5).
- HINT: **The tool server has no call budget or spending limit,** no size cap
  on ad hoc text, and no host allow-list enforced in its own code
  (TOOL-SERVER.md section 5).
- HINT: **The 00:36Z MCP session's origin is unknown** (TOOL-SERVER.md section
  3; that note is currently an uncommitted edit).
- HINT: **Generalization.** Everything rests on one collection run
  (2026-11-21), one persona (Priya Nair, fictional) and one labeler.
- HINT: **Also on record:**
  - group B is a sample of a sample (38 of 154), and A and B share a seed
    (FRICTIONAL.md entry 4);
  - grounding is exact-substring only, so the curly apostrophe in B003
    "Stripe’s" matters (REJECT-AUDIT.md);
  - the server checks its own output schema with its own `minischema`, so the
    check is circular (TOOL-SERVER.md section 5);
  - the Claude call spawns `uname` and `file`, and both inherit the API key
    from the environment (TOOL-SERVER.md section 5).

### HINT: candidates for "Not claiming"

- HINT: **Persistence is not proof.** Rule 4's behavior carrying into
  held-out does not show it was "trained" or generalizes beyond this dataset,
  this run and this persona (EXPERIMENT.md section 7, point 4).
- HINT: **Relevance is not entailment.** Topical relevance (the filter) does
  not mean candidate fit. On 8704363002 the fit claim is "contradicted" only
  by boilerplate. On 8175656 the verdict is "relevant" over a grounded
  disqualifier (SHORTLIST.md section 4).
- HINT: **The abstention rule's limit.** It surfaces every flagged tension
  but gives boilerplate the same "CONTRADICTION" weight as substance
  (SHORTLIST.md section 5). The flags also vary between runs of the same
  posting (TOOL-SERVER.md section 5, judge transcripts `_1`, `_3` and `_4`).
- HINT: **"supported" means a quote exists in the posting.** It does not mean
  the claim is true, or that it argues for the verdict (SHORTLIST.md section
  2).
- HINT: **The reject audit's findings are sample estimates.** C (19/20) is
  exact for this run only (REJECT-AUDIT.md, sample limits).
- HINT: **The filesystem-server evaluation** comes from a source reading on
  2026-11-22, not from running it (TOOL-SERVER.md section 6).

## Driver's seat

> Fill or correct every `[[ ]]` cell. The "Claude did" cells are drafted from
> the record and are checkable; edit any you disagree with. "Om did" and "Why
> that part stayed mine" are yours alone.

| Task | Claude did | Om did | Why that part stayed mine | Evidence |
|---|---|---|---|---|
| FILTER.md | Implemented against it. Left it unchanged through the reject audit and the experiment, as instructed. Drafted the 2026-11-22 v1.1.0 amendment to the content and scope you specified: the promotion grounds, the known gaps listed in the file itself, and the Palantir scope left alone. | [[ ]] | [[ ]] | `9426989` (written before any code), `9298665` (amendment). FRICTIONAL.md entry 1 |
| The filter + rule-1 cross-check | Wrote the wrong-version tests and stubs first. Added the blank-quote test after the first stub run showed the gap. Wrote `filter.py`, `grounding.py`, `collect.py` (JS2's loop imported unchanged) and `postings.py`. Fixed the relative-path crash. Wrote the cross-check that runs JS1's rule in a subprocess: 0 disagreements. | [[ ]] | [[ ]] | `0274afb`, `9e2c27a`, `94efb96`, `667d6dc`. Logs 00–06. FRICTIONAL.md entries 2 and 3 |
| Evidence-commit exception | Committed this run's raw evidence as a deliberate exception to JS1/JS2's gitignore convention, with the reason in the commit message. | [[ ]] | [[ ]] | `a1988cb`, `.gitignore` (README.md still to be written) |
| The reject audit (sampling) | Built the seeded draws (A 30, B, C 20) and the BLANK worksheets with no verdicts. Redrew B as 2 forced + 38 sampled on your instruction, and documented the cut. | [[ ]] | [[ ]] | `340dfa9`, `dc47bf1`, `6af4411`. `logs/reject_audit/draw_manifest.json`. FRICTIONAL.md entry 4 |
| The reject audit (hand judgments + report) | Parsed your 90 labels. Checked the quotes it attributed in the report. Drafted REJECT-AUDIT.md in your 7-section structure, shown before saving. | [[ ]] | [[ ]] | `logs/reject_audit/*_draft.md`, `3f25469`, REJECT-AUDIT.md |
| Chapter 9: split | Catalogued every number in the pipeline and where it came from. Computed the stratified 60/40 split with a new seed. Built the guarded, logged held-out reader. Disclosed prior exposure, including its own. | [[ ]] | [[ ]] | `277b7d6`, `logs/13_experiment_split.txt`, EXPERIMENT.md sections 1–2 |
| Chapter 9: rule 4 design | Wrote up Problems 1–3 as you worded them and Decisions A and B. Built rule 4 test-first on dev only, and found its own regex bug through the tests. Added the full-text Palantir diagnostic. Did not add "Senior" after the C01 miss. | [[ ]] | [[ ]] | `46e7782`, `8650e84`. Logs 14–17b. EXPERIMENT.md sections 3–4 |
| Chapter 9: held-out read + decision | Did the single guarded read and committed the raw result before interpreting it. Drafted sections 7–8 and the amendment to your points. Added two items you then confirmed: the overlapping intervals, and that the designers had seen the labels. | [[ ]] | [[ ]] | `ad9ff05`, `9298665`. `logs/18`. `logs/experiment/heldout_access.log` (1 entry) |
| The source-grounded shortlist | Wrote the shortlist-v1 prompt contract, the strict validator, the self-flagged contradiction check and the abstention rendering, test-first. Corrected your planned Case 2 framing against the real output (8738179002's flag came from S1, not the location sentence). Found the 246/246 boilerplate pattern and the C14 instance. | [[ ]] | [[ ]] | `0fb5cef`, `18e8f2a`. Logs 19–22. `logs/shortlist/`. SHORTLIST.md |
| The MCP tool server | Read the MCP spec through a subagent and flagged that 2026-07-28 has no `initialize`. Built the server, the small schema checker, the client and the audit wrapper, test-first. Found the oneOf gap in its own server and fixed it test-first. Had the filesystem server's source read and evaluated. | [[ ]] | [[ ]] | `19bba0a`. Logs 23–30. `logs/mcp/`. TOOL-SERVER.md |
| The key-leak incident + rotation | Caused the leak: its first audit hook recorded child environments. Spotted the key while summarizing the log, before anything was staged, and stopped the commit. Fixed the hook and checked it with a fake secret. Confirmed nothing was staged or in history. Checked logs 29 and 30 before writing them up. | [[ ]] | [[ ]] | TOOL-SERVER.md 4.3–4.4. Logs 29 and 30. Both key-prefix searches empty after `19bba0a` |
| This sign-off | Drafted this skeleton and its hints only. | [[ ]] | [[ ]] | this file; README.md (still to be written) |
