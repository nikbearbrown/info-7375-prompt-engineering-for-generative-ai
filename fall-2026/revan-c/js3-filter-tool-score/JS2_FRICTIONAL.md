# FRICTIONAL — Job-Search Agent 2

This is my account of what got in the way of Job-Search Agent 2, what I changed, and what I still cannot claim. The times below are UTC on November 10, 2026 unless I say otherwise. I point to saved traces and commits where I have them; an unsaved endpoint probe is only a recollection, not run evidence.

## 1. Writing the gate exposed choices I had not made

I committed [GATE.md](GATE.md) in `f3072e5` before the JS2 tests (`e7493d7`) and implementation (`ac2827a`). Claude's review caught three gaps in the first draft. Requiring `--approve-state-write` before *any* observation meant I could not look without changing state. I changed the default to an observation-only run. I also accepted the 10-second admission rule: with an 8-second request timeout and 2 seconds reserved for the trace, a request proposed at second 40 must not start under a 45-second limit. I added the look-alike host B03a and time-boundary B16 predictions. [BOUNDARY_TESTS.md](BOUNDARY_TESTS.md) names the tests for those cases.

Claude suggested Vercel on Greenhouse and Supabase and Linear on Ashby. I rejected those board choices and selected Duolingo on Greenhouse and Patch My PC on Lever alongside my existing Klaviyo board; the exact URLs are in `f3072e5`.

I left baseline behavior out of the gate. That was an omission, not a deliberate exception. The code follows JS1's convention and labels the first valid observation of a board as `baseline`; [README.md](README.md) says so. If I rewrote the gate, I would decide that behavior there before writing the loop, rather than leaving it for the implementation.

## 2. My first finished-wrong plan stopped fitting my own policy

Claude found Webflow's empty Greenhouse board on November 9 and proposed it; I first chose it for the clean-but-wrong result. Once I decided in GATE.md that an empty board must be `incomplete` with `unknown` counts, JS2 could not honestly finish on that input. I dropped that plan and used my unchanged JS1 agent for the wrong answer. With the explicitly seeded empty response in [fixtures/js2/PROVENANCE.md](fixtures/js2/PROVENANCE.md), JS1 exited 0 and reported 0 new postings; the separate checker reported `FAIL empty-response-claimed-as-no-new-jobs` in [demo/finished_wrong/independent_check.txt](demo/finished_wrong/independent_check.txt). JS2 on the same seeded Klaviyo bytes ended `incomplete` in [its trace](runs/js2/2026-11-10T06-34-30Z_normal.json). The earlier Webflow probe was not saved, so I do not use it as evidence for the submitted run.

## 3. The old Python environment broke the fresh-clone story

JS1's README named Python 3.14.5, but that interpreter was no longer installed here, and the old `.venv` could not run its commands. Claude rebuilt the environment with Python 3.12.14; the JS2 [README toolchain](README.md) now names that version. I checked the rebuilt environment by running the full suite after the review patch: **110 passed** in [my terminal record](review_evidence/post_patch_commands.txt). That is evidence for this machine and environment, not a claim that I tested every operating system or Python version.

## 4. The first two live runs failed

At **06:32:28**, all three board requests in [the first trace](runs/js2/2026-11-10T06-32-28Z_normal.json) failed at DNS resolution. I do not know the root cause from the trace; it records the resolver error, not why the resolver failed. At **06:32:42**, [the second trace](runs/js2/2026-11-10T06-32-42Z_normal.json) saved valid Klaviyo and Duolingo responses but Patch My PC timed out after 8 seconds. Both runs ended `incomplete` and left state unchanged. I started a separate run; the agent itself did not retry a failed board inside either run, which is the zero-retry rule in GATE.md. The [06:33:08 trace](runs/js2/2026-11-10T06-33-08Z_normal.json) finished with 149, 61, and 5 postings as baselines. The [deliberate-failure trace](runs/js2/2026-11-10T06-33-21Z_demo.json) then recorded the fourth board's HTTP 404, kept its counts `unknown`, and ended `incomplete` without changing state. I kept the failed traces rather than presenting only the successful one.

## 5. I did not accept every green test or convenient command

One Claude-written state-write failure test initially passed for the wrong reason: its fixture made the state path a directory, so preflight failed before the intended write. Claude tightened the test so failure occurs after the three boards are fetched, and recorded the change in `ac2827a`. While building the wrong-version checker, Claude also found that its state write passed a hard-coded approval value of `True`; it changed the call to use the run's actual flag. I accepted those corrections after the boundary and full-suite results, including `test_B13_run_without_approval_observes_but_never_writes_state` and the 17 caught mutants in [my terminal record](review_evidence/post_patch_commands.txt). I did not weaken a test to make it green.

In Claude's fresh-clone check, `ls | tail -1` picked the wrong JS1 run file. Two seeded runs landed in the same second; the second filename got `-1`, which sorts before the first filename. Claude changed the README to require the exact path printed by step 2 (`bf53a2c`). I followed that path in my own run, recorded in [review_evidence/post_patch_commands.txt](review_evidence/post_patch_commands.txt).

## 6. I accepted a narrow review patch

The saved Patch My PC response has two remote software engineer postings with `categories.location: "United States"` and `workplaceType: "remote"`. Before the patch, they failed only my location condition. The constructed remote case in `test_lever_workplace_type_controls_remote_location` failed before the patch; the onsite control passed. The test entered Git in `d7f1508`, and [the failing output](review_evidence/remote_pre_patch_pytest.txt) was committed in `bfbc822`, both before Claude's parser patch `06e9257`.

I accepted `06e9257` after reading its one-file diff, rerunning the two-case test (**2 passed**), the full suite (**110 passed**), and the wrong-version checker (**17 of 17 caught**). My [terminal record](review_evidence/post_patch_commands.txt) includes a before-and-after evaluation of the same saved Patch My PC response. The patch constructs `location.name` by adding a labeled reference to Lever's `workplaceType`, rather than quoting `categories.location` alone. I accepted that representation because it identifies the raw field it uses and changes only Lever normalization; [REVIEW_PACKET.md](REVIEW_PACKET.md) explains the decision and scope. I am not treating the constructed string as a verbatim location from Lever.

## 7. I corrected the ownership of my evidence

An earlier review draft presented two evaluations of the saved Patch My PC response, before and after the patch, as mine when Claude had run them. I re-ran both myself, the pre-patch one in a worktree at `bfbc822`. The post-patch test, full suite, and mutation check were already in my earlier terminal log; they were not the ownership correction. The commands and outputs of my before-and-after evaluations are in [review_evidence/post_patch_commands.txt](review_evidence/post_patch_commands.txt), committed with the review packet in `9ec1695`. I also kept the earlier run traces, including the failures, in `d7f1508`.

The test-first history is less tidy than I wanted: the new regression test was staged when I committed the run artifacts, so `d7f1508` contains both. The separate `bfbc822` commit saved the failing output, but it did not introduce the test. Both commits precede patch `06e9257`, so the order is still checkable. I will not describe `bfbc822` as a standalone test commit.

## 8. What I have not resolved

- My test does not cover a Lever job marked `remote` but restricted to another country. The patch could make its location condition pass even if the fictional candidate could not work there. [REVIEW_PACKET.md §7](REVIEW_PACKET.md) names this limit; I did not change the relevance rule to handle it.
- One live board request really did hit the 8-second timeout, but the **45-second run deadline**, a slow stream, and budget-edge behavior were tested only with a fake clock (`test_B16_request_not_started_with_under_10_seconds_left` and related tests in `tests/test_js2_loop.py`). I have not shown that every real network pattern stays under 45 seconds.
- The independent checker recounts saved bytes. It catches an empty response reported as “no new jobs,” but cannot tell whether the employer truly has no jobs or moved to another ATS. [tools/independent_check.py](tools/independent_check.py) and [fixtures/js2/PROVENANCE.md](fixtures/js2/PROVENANCE.md) show the boundary of that check.
- The regression test's placement in `d7f1508` makes the test-first evidence harder to read than a dedicated test commit. I kept the actual history rather than rewriting it after the patch.
