# FRICTIONAL — Job-Search Agent 2

> Author: Smit P. Part A preserves the original session record. Part B records
> the file-transfer experience documented in this chat and distinguishes it from automated
> technical review. No personal test execution or pre-test prediction is claimed.

## Part A — Session record (written by Claude Code, 2026-11-08)

Facts from the session, each tied to a commit or file. These are not Smit's reflections.

- **Gate first.** GATE.md committed alone (`f150426`), then the 25 boundary predictions
  (`2b3563e`), then the code (`f2c97b4`).
- **Ashby 403.** The first Python request to Ashby got HTTP 403, while curl to the same URL got
  200. Sending an explicit User-Agent fixed it. Evidence: `USER_AGENT` in `agent/fetch.py`.
- **Per-host gap invisible in the trace.** The first live run did wait 1 s between the two
  Greenhouse requests, but only the timestamps showed it. `host_gap_wait_s` was added to the
  trace afterwards, so run `2026-11-08T00-43-54Z` lacks that field and later runs have it.
- **Seeded runs would have overwritten the live baseline.** Noticed while writing the first
  seeded scenario, before running it; fixed in `45480d2` with a separate `jobs/seeded-state/`.
- **Finished wrong answer reproduced on v1.** `seeded-vanish-2` ended `finished` with exit 0;
  `verify_run.py` failed it; `seeded-vanish-3` then reported 145 old postings as new (`337cf1b`).
- **Test before patch.** `66d0cbc` added a test that failed 5 of 7 on v1.
- **First patch passed the suite but was wrong.** 57 tests OK; the independent check failed on
  `count 0` for a suspect board. Traced to two GATE.md tables disagreeing. Revised to
  `count: null` plus `observed_count` (`1b7f999`). REVIEW_PACKET.md section 5.
- **Redirect gap.** Found while writing POLICY.md's "not shown" list; test failed first
  (`evidence/redirect-test-before-fix.txt`), fixed in `1bfbb6d`.
- **Unresolved:** a board collapsing to a small nonzero count is not flagged; an all-suspect
  run ends `error`, which GATE.md did not explicitly decide.
- **No change seen live.** Three live runs minutes apart showed identical counts (145, 85, 32).

## Part B — Smit P

### Entry 1 — Getting the project files — 2026-11-09

I tried sharing the branch name `smit-p/js2-loop-tools-diff`, then the cloud path
`/home/user/course/fall-2026/smit-p/js2-loop-tools-diff/FRICTIONAL.md`. I expected those
references to let this session reach the project. Neither provided the files here.
I asked whether this session had access to my laptop because I did not understand why
the path was unavailable. The distinction was between the separate cloud container
and this session's local workspace. I then supplied
the ZIP from my Downloads folder, which could be opened.

I accepted transferring the ZIP as the way to continue. No GitHub push, merge, or final
repository commit hash was established here. The ZIP also has no Git history, so its
historical commit references cannot be verified from this copy alone.

Evidence: the supplied ZIP, README.md's ZIP instructions, and LOCAL_VERIFICATION.md.
Next step: recover the original repository history before preparing the Canvas commit.

### Entry 2 — Review evidence and limits — 2026-11-09

I requested that the assignment be completed and supplied eight reflection prompts.
I did not supply a prediction before seeing the old-code test result, so no prediction
is recorded. The reported result is five failures and one error when the current tests
run against the old code; the earlier seven-test version had five failures and two
passing controls. I have not reported personally running either version.

The technical reason to use `null` for a suspect count is that zero asserts there are
no postings, while `null` preserves uncertainty. `observed_count: 0` still records the
response. This is the rationale for the technical recommendation, rather than a claim
that I independently reviewed and approved the patch.

The first patch passed all 57 tests while still reporting an untrusted zero as the
count. The independent checker rejected it. The two GATE.md tables had disagreed,
so passing tests did not establish that the requirement was coherent or fully checked.
The revised patch added the missing assertion and separated observation from trust.

Recounting the same empty response produces zero again. That validates the count of
that response, not the completeness of the server's data. Comparing with the earlier
raw response containing 145 postings exposes the suspicious disappearance, although
it cannot determine whether the cause was a real hiring pause or a server fault.

Evidence: REVIEW_PACKET.md sections 2, 5, and 7; WRONG_ANSWER.md;
verify_run.py; evidence/local-verify-seeded-vanish-2.txt; and
evidence/local-verify-seeded-vanishfix-2.txt.

### Entry 3 — Proposed changes and outstanding questions — 2026-11-09

Claude Code built the original code, tests, and documents. The later local suite,
mutation checks, and replay were automated. They do not show that I personally read
the implementation, re-ran the commands, changed the code, or rejected a patch.
Those personal actions have not been reported. I requested completion of the documents;
no independent personal approval is asserted.

The original session record says Ashby blocked Python's default User-Agent while curl
succeeded. Sending an honest descriptive User-Agent may identify the client more clearly,
but a successful request alone does not establish authorization or fair use. API usage
terms and access guidance still need review before drawing that conclusion.

A proposed rule for the unsolved nonzero collapse is to flag drops greater than 80%
when the previous baseline had at least 20 postings. A 145-to-3 drop is about 97.9%,
so it would trigger review. The minimum avoids percentage alerts on very small boards;
the existing zero-after-nonzero rule remains separate. This threshold is a proposal,
not an implemented feature or a personally confirmed policy decision. Historical data
and boundary tests would be needed to assess false alarms and missed truncations.

My understanding of the redirect fix and symlink check has not been demonstrated in
this record. A concrete next step is to read agent/fetch.py with tests/test_redirect.py,
trace how a 302 response is returned without following it, and then read the symlink
boundary test alongside agent/policy.py. I cannot claim to have completed that exercise.

Evidence: SOURCES.md; LOCAL_VERIFICATION.md; agent/fetch.py;
tests/test_redirect.py; tests/test_policy.py; and REVIEW_PACKET.md section 9.
