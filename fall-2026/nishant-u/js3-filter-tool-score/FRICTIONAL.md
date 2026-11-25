# FRICTIONAL — Job-Search Agent 2 (nishant-u)

An honest log of what went wrong, what I checked, and what I accepted, changed or rejected. JS1's log
is in `fall-2026/nishant-u/js1-contract-and-watch/FRICTIONAL.md` at `d63ee48`.

## 2026-11-10 — The gate had three gaps before any code

After I committed `GATE.md` (`58d6431`), Claude Code's review found three problems in it:

1. **The demo couldn't happen.** `finished` required every planned board to parse, and board 5 always
   returns 404, so a full run could never show a finished wrong answer.
2. **Case 9 didn't fit.** Boundary case 9 was a read, but there was no read operation in the vocabulary.
3. **Merge vs replace.** Nothing distinguished a merging `update_state` from a replacing one.

I fixed all three in an amendment before any code (`c5ee0fe`): the `full` and `demo` profiles with the
outcome-check thresholds, a `read_file` operation, merge-only `update_state`, wrong version 6 and
boundary case 15. **What I learned:** I had written the exits and the demo plan separately and never
checked them against each other.

## 2026-11-10 — Eight implementation decisions accepted after the code

While implementing (`5e3e3d0`), Claude Code made 8 decisions the gate didn't cover:

1. https only, and no username or password in a URL;
2. a retry blocked by a budget means `budget-exhausted`;
3. other HTTP codes fail with no retry;
4. refused or repeated boards count against the board budget and make the run `incomplete`;
5. the baseline is per board;
6. redirects are re-checked up to 3 hops, but the hops are not counted against the budget;
7. the Claude judge doesn't run on Ashby postings;
8. the check matches companies by the profile's `company` field.

It listed them instead of hiding them. I reviewed them and accepted all 8 in a dated amendment
(`d5640de`), marked as coming after the implementation. **Unresolved:** decision 6 means the request
budget doesn't bound redirect hops (it's in the sign-off's "Not checked").

## 2026-11-10 — Boundary case 8 skipped; a junction check instead

The real-symlink test (case 8) is skipped on my machine. Windows refused to create the symlink with
WinError 1314 ("A required privilege is not held by the client"), and the test records that reason.
Claude Code ran a one-off check with a directory junction, which needs no privilege: the policy refused
the write through it, and nothing reached the outside folder. That check is not a committed test, so
case 8 is still "not checked" in my sign-off. **What would settle it:** Windows Developer Mode, or
running the suite on macOS or Linux.

## 2026-11-10 — The first regression test was too weak

For the review packet, Claude Code's first draft of `tests/test_js2_review.py` built a state in which
Greenhouse poshmark had never been seen. On the unpatched code that board is reported as "baseline",
not "0 new", so the assertion `"0 new" not in report.md` would have passed without any fix. Claude Code
caught this itself, by printing what the unpatched code did for each property before committing. It then
split the test into a "seen" case (like my second live demo run, which said "0 new") and a "fresh" case
(like the first, which saved the empty board as seen), plus the control. Both regression cases failed in
my own run on `bccbc41`. **What I learned:** a test that fails for one reason (the exit) can still have
assertions that would pass on broken code. Check what each assertion sees on the old code.

## 2026-11-10 — Scope widened before the patch

The allowed-file list for the patch was `agent2/loop.py` and the new test file. Before the patch, Claude
Code predicted that 4 existing tests encoded the old behaviour (an empty 200 board counted as clean) and
would fail. I widened the scope before the patch (`bccbc41`) to those 4 tests only, and wrote down for
each the exact planned change and why it isn't a weakening. After the patch, the 4 changes matched the
table and the prediction held: 131 tests, 1 skip.

## 2026-11-10 — An unplanned docstring edit

The patch also changed the module docstring of `agent2/loop.py`, which wasn't in my table. The old text
called the demo profile "the finished-wrong-answer run", which the patch made false. Claude Code flagged
the edit when it showed me the diff. I accepted it because it is inside the allowed file and corrects a
false statement (`REVIEW-PACKET.md`, Scope check).

## 2026-11-10 — The CLI has no state flag

To give each live run its own state, I expected a `--state` flag. There isn't one: the state lives
inside the output root. Separate `--out` roots were used instead (`out/demo`, `out/full`,
`out/demo-postpatch`), with no code change. **Accepted** rather than adding a flag mid-assignment.

## 2026-11-10 — Instacart changed during the day

Instacart's Greenhouse board had 88 postings in the morning runs and 92 at 18:02 UTC. The second full
run (`98ae593`) reported 4 new ids against the morning's state. All four were judged `not_relevant` by
the JS1 rule: two failed R1 (no title term) and two failed R3 (no US location part). That is a real new
posting being detected, not a constructed one. It also means the board counts in my docs are snapshots,
not constants.

## 2026-11-10 — After the patch, the demo no longer reproduces the wrong answer

The post-patch live demo (`c51b1af`) ended `incomplete`, with Greenhouse poshmark `unverified-empty`.
That is the fix working, but it means the finished-wrong-answer can no longer be shown by running the
current code. The evidence is the pre-patch runs `out/demo/runs/2026-11-10-1` and `-2`, made by
`5e3e3d0` and quoted in `FINISHED-WRONG.md`. **Unresolved:** the patch also makes a company that
genuinely isn't hiring end every run `incomplete`, and the agent can't tell that apart from a wrong board.
