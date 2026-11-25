# Sign-off: Job-Search Agent 2

## Checked
Which properties, by which tests (name them):
- The permission policy: `test_B01_off_allowlist_host` to `test_B16_ip_literal` in `tests/js2/test_boundary.py`. Claude Code wrote the tests; I wrote the 16 predictions in POLICY.md before they ran.
- The exits and error policy: the exit tests in `tests/js2/test_loop.py` (written by Claude Code).
- The wrong versions: `tests/js2/test_wrong_versions.py`, W01 to W14 (written by Claude Code).
- verify: `tests/js2/test_verify.py` (written by Claude Code).
- Loop-path isolation: `test_loop_closure_excludes_legacy_modules` and `test_legacy_modules_are_byte_identical_to_b91c877` (written by Claude Code).
- Persona parity: `test_persona_agrees_with_js1_inputs` (written by Claude Code).
- The defect: `test_error_exit_does_not_create_state` and `test_error_exit_leaves_existing_state_byte_identical` (drafted in the claude.ai chat, read, run red and committed by me before the patch).
- The state-replace-failure branch: `tests/js2/test_review_state_replace_failure.py` (written by Claude Code during review, after the patch).

## How
By hand / by a test I wrote before reading Claude's code / by recomputation / with Claude's help (say which parts):
- By hand: my curl check (196853e), and the red, green, full-suite and diff commands captured in 7ebb3ba (15:52 ET).
- Before reading Claude's code: my POLICY predictions.
- With Claude's help: Claude Code wrote nearly all the test code and the wrong-version implementations. The review test was drafted in the claude.ai chat, read, run red, and committed by me before the patch.

## Not checked
At least three real items:
1. Forged summaries (UNVISITED, or a budget/repeat reason) pass both replay and verify (candidate 2).
2. Ctrl-C leaves no exit record (candidate 3).
3. Redirects were tested only in-process; only 302 is in the suite, and nothing was tested against a real server.
4. The prior-count rule only flags a drop to 0, so a board that lost half its postings would pass.
5. The W01 to W14 wrong implementations were written by Claude Code from my one-line descriptions.
6. The Lever HTML case was never observed.
7. Windows (b) and (c) after the patch.
8. I did not read the providers' terms of use.

## Not claiming
What this agent does not show:
- The JS2 guarantees (GET only, no delete, writes only under runs/) cover the loop path, not the legacy JS1 subcommands (amendment A-1).
- Nothing about how well RECORD judges jobs.
- The Claude judge was not run in JS2.
- This is a deterministic loop; no model chooses the tools.
- A-3's remaining window: if the state replace fails, trace.md and the trace's exit line still say FINISHED.

## Signed or withheld
Name, date: Deepak Kumaran T S, 2026-11-10, signed with the Not-checked items above. I have not read every GATE.md section line by line.

---

# Driver's seat

For the loop and for the review: what Claude should do, what I should do, and why that part stays mine. Evidence points to a commit, file or test.

| Part | What Claude did here | What I did here | Why it stays mine | Evidence |
|---|---|---|---|---|
| Loop: exits and budgets | Claude Code built the exits and budget checks; the claude.ai chat drafted GATE §1–2 | Approved the values; budget decision B-1 | The brief holds me accountable for budget definitions | 891446a, tests/js2/test_loop.py |
| Loop: boards and the deliberate failure | Claude Code ran the capture; the claude.ai chat recommended boards | Chose the 4 boards and stripe-js2-nonexistent | I am accountable for the targets chosen | c2fd4b3, 891446a (config/boards.json), 6dcb895 |
| Loop: error and repeat policy | The claude.ai chat drafted GATE §3–4; Claude Code flagged 21 gaps and implemented the policy | Decided the 6 open items | The brief holds me accountable for policy decisions | 891446a, tests/js2/test_loop.py |
| Loop: permission policy and predictions | Claude Code wrote B01–B16 and jobwatch/policy.py | Wrote the 16 predictions before the tests ran | The predictions are graded as mine, made before the run | 891446a, 14d906a |
| Review: reproducing the defect | Claude Code found 3 candidates and wrote the repro scripts | Picked candidate 1 | I must verify and pick the true failure candidate | 231bd1f |
| Review: the test before the patch | The claude.ai chat drafted it | Outline attempt, red run, commit | The patch author should not write the test that judges it | 49ce61d, 7309446, 7ebb3ba |
| Review: the patch | Claude Code wrote it | Read the diff, checked scope, found the GATE §3 conflict | I must verify the AI's code against the spec and check for scope creep | 3a4c1fb |
| Review: the accept, revise or reject decision | Claude Code wrote the A-3 suite test | Revise, with the evidence | The brief holds me accountable for the final verdict | 6b12eef, f39ce0d |
