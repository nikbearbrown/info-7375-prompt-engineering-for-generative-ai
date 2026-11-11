# Review packet — Job-Search Agent 2

## The change I reviewed

Lever gives location and work arrangement in separate fields. The Patch My PC board says `categories.location: "United States"` and `workplaceType: "remote"` for two software engineer jobs. Before the patch, `parse_lever` copied only `categories.location` into the normalized `location.name`. My existing relevance rule looks for Boston or the word “remote” in `location.name`, so both jobs failed the location condition. I treat that as a provider-mapping defect: the board explicitly says the jobs are remote, and the rule permits remote jobs.

## 1. Defect reproduced before the patch

The live normal run at **2026-11-10 06:33:08 UTC** saved [the Patch My PC response](evidence/js2/2026-11-10T06-33-08Z_patchmypc.body) and [its trace](runs/js2/2026-11-10T06-33-08Z_normal.json). The run was a baseline, so its trace did not score these postings as new. I checked the saved response directly, rather than treating the baseline count as a verdict:

```bash
jq -r '.[] | [.id, .text, .categories.location, .workplaceType] | @tsv' evidence/js2/2026-11-10T06-33-08Z_patchmypc.body
```

Before the patch, evaluating those saved postings through `parse_lever` and `judge_posting` produced:

| Posting ID | Title | Raw location / work arrangement | Rule verdict | Failed condition |
|---|---|---|---|---|
| `a71b827b-c926-4966-9207-dcc4dff7719a` | Software Engineer, AI | `United States` / `remote` | `not_relevant` | `location` only |
| `21f4037e-2b38-4f87-8877-fd4096d36e7f` | Software Engineer, Backend | `United States` / `remote` | `not_relevant` | `location` only |

The two raw fields above are in the saved board response. The pre-patch rule result was also reproduced by the failing test in §2. These are observations about this saved response, not a claim that all remote Lever postings qualify under the rule.

I ran this pre-patch evaluation myself on 2026-11-10, in a worktree checked out at `bfbc822` (the code before patch `06e9257`); the commands and their output, including the failed conditions, are in [post_patch_commands.txt](review_evidence/post_patch_commands.txt).

## 2. Test written and run before the patch

[The regression test](tests/test_js2_remote_review.py) uses **constructed** Lever postings with the same title, skills, and `United States` location. It changes only `workplaceType`. I expected `remote` to pass the location condition and yield `relevant`; I expected `onsite` to fail location and remain `not_relevant`. This control checks that the fix does not make every Lever posting remote.

The test was committed in `d7f1508`, before the implementation patch `06e9257`. The pre-patch failure output was saved in [remote_pre_patch_pytest.txt](review_evidence/remote_pre_patch_pytest.txt) by running:

```bash
.venv/bin/python -m pytest -q tests/test_js2_remote_review.py
```

It returned **1 failed, 1 passed**. The `remote` case failed at `assert location["passed"] is True` because the actual value was `False`; the `onsite` control passed. Commit `bfbc822` saved that failing output before the patch.

## 3. Diff read as a change in behavior

I compared the test commit with patch commit `06e9257` and read the change in `jsloop/providers.py`. `parse_lever` now checks whether `workplaceType` is a string equal to `remote` after trimming whitespace and ignoring case. Only then it appends ` (Lever workplaceType: remote)` to the normalized `location.name`. The text is labeled with its source field, and the original `workplace_type` remains separately available in the posting record.

For a Lever posting whose `categories.location` does not already contain Boston or remote, `workplaceType: "remote"` can now change the **location condition** from fail to pass. Its overall verdict changes only if title, skills, seniority, and role type also pass. On the saved live response, the two software engineer postings above now evaluate as `relevant` with no failed conditions. A non-remote Lever posting keeps its original location text. Greenhouse uses `parse_greenhouse`, which the patch did not change.

## 4. Scope review

`git show --stat 06e9257` reports **one file changed: `jsloop/providers.py`, 7 insertions and 1 deletion**. I read the eight-line diff. It does not change `jsagent/rule.py`, `CONTRACT.md`, `GATE.md`, `jsloop/policy.py`, or the regression test. It does not weaken an assertion or widen the network or file permissions. The change stays in the Lever normalization step where the field was lost.

The appended phrase is derived from the raw Lever `workplaceType` field, but it is still a synthesized `location.name` value. I accept that representation for this adapter because it labels the source field; I do not treat the synthesized text as a verbatim quote from `categories.location`.

## 5. Commands and results checked for this review

| When | Command | Result |
|---|---|---|
| Before patch | `.venv/bin/python -m pytest -q tests/test_js2_remote_review.py` | 1 failed, 1 passed; `remote` failed the location assertion |
| After patch | `.venv/bin/python -m pytest -q tests/test_js2_remote_review.py` | 2 passed |
| After patch | `.venv/bin/python -m pytest -q` | 110 passed |
| After patch | `.venv/bin/python tools/check_wrong_versions_js2.py` | All 17 mutants caught by their named tests |
| After patch | `git show --stat --oneline 06e9257` and `git show 06e9257 -- jsloop/providers.py` | One-file parser change; test and policy untouched |

I also evaluated the two saved live Patch My PC postings again after the patch. Their normalized locations became `United States (Lever workplaceType: remote)`, and both rule verdicts became `relevant`. I did not make a second live network request for this review; this check reused the saved response.

I ran every after-patch command above myself on 2026-11-10; the commands and their output are in [post_patch_commands.txt](review_evidence/post_patch_commands.txt).

## 6. Decision — accept

**Accept patch `06e9257` for the stated defect.** The pre-patch test failed on the remote case and passed its onsite control. The patch makes both cases pass, changes only the Lever parser, and leaves the full suite green. The saved live response confirms that it fixes the two postings that exposed the defect. The 17 wrong-version checks still catch the mutations they were designed to catch.

This decision is limited to the remote-location mapping. Passing tests and this review do not establish that every Lever location restriction is interpreted correctly or that every job marked relevant is a suitable job.

## 7. A case this test still misses

The test does not cover a Lever posting with `workplaceType: "remote"` but a location restricted to another country. The patch would append “remote” and make the location condition pass, even though the candidate may not be eligible to work in that country. That is a real limit of my current relevance rule and test; I am not claiming this patch resolves it.
