# Review packet — amendment A2: G4 location (R-v2a → R-v3)

**Subject.** One defect, carried over from JS1 on purpose so that JS2 would have
something real to review: gate G4 treated the substring `"remote"` as though it
were a location.

**Rule versions.** R-v2a → R-v3. **Commits.** `3a0896f` (test, red) →
`7bf3d11` (patch) → this packet.
**Written up as an amendment in** `GATE.md` §8 A2.
**Date of the work.** 2026-11-09.

A note on who did what, before anything else: the patch to `agent/rule.py` was
written by Claude (Opus 5) in a Cowork session. This packet is the review of
that patch. Where it says a command was run, §6 says on which machine and by
whom; nothing in this file is written in past tense unless it ran.

---

## 1. The defect, stated as a property

> **A posting in a location the persona cannot work in must not be judged
> relevant.**

R-v2 (JS1) and R-v2a (JS2 before this patch) both violated it. G4 read:

```python
loc_hit = None
for i, phrase in enumerate(resume["locations_ok"]):
    if phrase in location_cf:
        loc_hit = ...
        break
if loc_hit is None and resume["remote_ok"] and "remote" in location_cf:
    loc_hit = _cite("remote_ok", True, "location.name", "remote", ...)
```

The second branch asks whether the posting is remote. It never asks **remote
where**. So with `remote_ok: true`, `"Remote - Ontario, Canada"` passed the
gate and the posting came out `relevant`, with a justification that cited
`remote_ok` as its evidence — a confident, well-formatted, wrong answer.

This was not found by luck. It was pre-registered in JS1's `CONTRACT.md` §4.2
item 3 on 2026-10-21, as a predicted false positive, before any real data had
been fetched. The real board then produced it.

## 2. Reproduced before anything was changed

`tests/test_review_g4_location.py` was written against the defect and committed
**while it was still failing**, as `3a0896f`. The run that failed is kept
verbatim in `review/before-patch-failure.txt`; its reproduction line:

```
E  AssertionError: 2 posting(s) judged relevant in a location the persona cannot take:
   [('greenhouse:7131934', 'Machine Learning Engineer', 'Remote - Ontario, Canada'),
    ('greenhouse:6512458', 'Software Engineer, Ads',    'Remote - Ontario, Canada')]
```

Counting: `8 failed, 3 passed`.

Two things make this a reproduction rather than an illustration.

- **It runs on real bytes.** The fixture is JS1's live Greenhouse capture of
  2026-10-31, 163 postings, sha256
  `8871e1bb5de49c071f3b661a7d59e5fc879b29c187dd0a90409521aa479b86d5`. The
  assertion prints the postings it fails on, so the failure output *is* the
  evidence.
- **It is guarded.** `test_the_board_really_does_carry_non_us_remote_postings`
  asserts the fixture holds ≥10 non-US remote postings. Without that guard, a
  fixture that happened to contain none would make the main test pass and prove
  nothing. The capture holds 24.

A third thing, which is the part I would not have predicted: those two postings
are two of the four rows Weiting decided herself in JS1's labelling pass
(`experiments/labels/labels-L-v1.json`, `decided: author_first`, 2026-10-26),
and she labelled both **`no`** while R-v2 called them `relevant`. The
pre-registered prediction, the real data, and the human label all land on the
same two rows.

With the caveat JS1 recorded and that does not get to lapse here: **those labels
were not blind.** That file's `provenance.blindness` field states that Claude
had already told her what R-v2 returned for each of the four rows before she
decided them. She disagreed with the agent on all four, which is the opposite of
what anchoring would produce, but a non-blind label is not independent
confirmation and is not offered as any. It is a fourth pointer at the same
defect, not a measurement of it.

## 3. The diff, read as a change in behaviour

`git diff 3a0896f..HEAD -- agent/rule.py` — 34 insertions, 11 deletions, one
function. Behaviourally it is three changes, not one:

| | Before (R-v2a) | After (R-v3) |
|---|---|---|
| remote posting, persona `remote_ok: true`, location **not** in `locations_ok` | **relevant** | not_relevant / G4 |
| remote posting, persona `remote_ok: false` | relevant (flag ignored) | **not_relevant / G4** |
| remote posting, location **in** `locations_ok` | relevant | relevant (unchanged) |
| non-remote posting | decided by `locations_ok` only | decided by `locations_ok` only (unchanged) |

Row 1 is the defect. Row 2 is the one I want to flag, because **it is a
behaviour change that the bug report did not ask for.** Before the patch,
`remote_ok: false` was indistinguishable from `remote_ok: true` — the flag only
ever widened the gate, never narrowed it, so a persona who could not work
remotely was judged exactly like one who could. The patch makes the flag mean
something in both directions.

I am recording that as a *deliberate widening of scope that I checked and
accepted*, not as something I failed to notice. The reasons: it cannot change
any verdict for this persona, who has `remote_ok: true`, so it moves nothing in
the evidence; it is covered by a test
(`test_a_persona_that_cannot_work_remotely_rejects_a_remote_posting`); and the
alternative — a flag that is read but can never reject — is a flag that lies.
A reviewer who wanted the patch kept to exactly the reported defect would be
right to ask for row 2 to be split into its own amendment. I would not argue.

What the diff is *not*: it is not a filter bolted on in front of the gate, and
it is not a new `locations_ok` entry for Canada. Either would have made these
two postings go away without making the gate correct.

## 4. Did the change stay in scope?

The amendment claimed, in `GATE.md` §8 A2 and in `EXPECTED_MOVES` in
`tests/test_rule_carried_over.py`, **before** the diff was reviewed:

> exactly 2 of JS1's 163 postings move, both `relevant → not_relevant /
> G4_location`, both `"Remote - Ontario, Canada"`; the other 161 are unchanged.

Checked by recomputing R-v3 over all 163 postings and comparing against the
committed R-v2 verdicts in `evidence/fixtures/js1-rv2-verdicts.json`:

```
total=163  moved=2
  7131934  Machine Learning Engineer  Remote - Ontario, Canada  relevant/None -> not_relevant/G4_location
  6512458  Software Engineer, Ads     Remote - Ontario, Canada  relevant/None -> not_relevant/G4_location
R-v3 tally: {'G1_title_block': 143, 'relevant': 9, 'G2_discipline': 8, 'G4_location': 2, 'G3_job_family': 1}
```

R-v2's tally for the same bytes was
`{'G1_title_block': 143, 'relevant': 11, 'G2_discipline': 8, 'G3_job_family': 1}`.
Relevant 11 → 9; the two that left went to G4; nothing else moved.

**In scope.** And the claim is now a test rather than a paragraph:
`test_rv3_moves_exactly_the_verdicts_the_amendment_claimed` fails if a third
verdict ever moves, and `test_the_other_161_verdicts_are_untouched` states it as
a count.

Two further scope checks, because "exactly two verdicts moved" is not the same
as "the patch did only what it said":

- **The patch did not touch the test file.** `git diff 3a0896f..7bf3d11 --
  tests/test_review_g4_location.py` is empty — 0 lines. The same file that
  produced 8 failures produced 11 passes with not one character changed. This
  is the check that a green report was earned rather than arranged, and it is
  the one I care most about, because weakening a test is the easiest way to
  make this whole exercise worthless.

  The review step then *added* 70 lines to that file, recording §7's finding as
  a strict-xfail test, and removed none:
  `git diff 7bf3d11..HEAD -- tests/test_review_g4_location.py | grep '^-[^-]'`
  is empty. The two ranges are quoted separately on purpose. `3a0896f..HEAD`
  would read better and would be false — which is the exact move this bullet
  exists to catch, so getting it wrong here first was instructive.
- **The other known defect is still there.** JS1 documented two defects. A2
  fixed one. `test_the_g1_defect_is_still_present` asserts the other is still
  standing, so the patch cannot have quietly fixed two things in one commit, and
  G1 cannot drift out of the record by being silently repaired where no review
  covers it.

## 5. Where the patch was wrong on the first attempt

Nowhere in `agent/rule.py`. But the first run after the patch was **not** green,
and the two failures were real:

```
FAILED tests/test_rule_carried_over.py::test_rv2a_reproduces_every_rv2_verdict
FAILED tests/test_rule_carried_over.py::test_the_two_js1_defects_are_still_present
```

Those two tests encoded amendment A1's promise that the rule reproduced *every*
R-v2 verdict, and A2 breaks that promise on purpose. This is the moment where
the honest move and the convenient move diverge, so it is worth naming what each
would have been. Convenient: delete the two tests, or loosen the first to "most
verdicts match". Honest: a letter bump promises no verdict moves and a number
bump owes a list of the ones that do — so the equivalence test became a
**pinned-difference** test with the two postings named in `EXPECTED_MOVES`, and
the defects test was split into one assertion that G4 is fixed and one that G1 is
not. The suite is strictly stronger afterwards than it was before: it now
constrains *which* verdicts may move, which "all verdicts match" never did once
any verdict was allowed to move at all.

## 6. Commands, and who ran them

Claude ran these in the Cowork cloud container on 2026-11-09, in
`fall-2026/weiting-w/js2-loop-tools-diff/`:

```
python3 -m pytest -q tests/test_review_g4_location.py   # before patch: 8 failed, 3 passed
python3 -m pytest -q                                    # after patch, first run: 2 failed, 70 passed
python3 -m pytest -q                                    # after the two tests were rewritten: 74 passed
python3 -m pytest -q                                    # after §7's xfail record was added: 75 passed, 2 xfailed
git diff 3a0896f..HEAD -- agent/rule.py
git diff 3a0896f..7bf3d11 -- tests/test_review_g4_location.py | wc -l  # 0
```

Everything above ran in the cloud container, which is Claude's machine.

I ran the following myself, on my own Mac, in my own Terminal, on
**2026-11-11T00:18Z** (2026-11-10, 7:18pm ET). The verbatim output is in
`README.md` under "What I ran myself".

```
cd ~/Downloads/js2-final
python3 -m pytest -q
SSL_CERT_FILE=$(python3 -m certifi) python3 -m agent watch
python3 tools/crosscheck.py
python3 tools/boundary_table.py --check
```

What that does and does not establish for *this* review:

- `pytest -q` gave **104 passed, 2 xfailed** on my machine, so the suite that
  holds R-v3 — including the two tests this packet turns on,
  `test_review_g4_location.py` and `test_rule_carried_over.py` — passes outside
  the container it was written in.
- The two xfailed are §7's recorded defect. They are expected failures, not
  skips: if someone fixes the substring matching, `strict=True` turns them into
  errors and this packet has to be revisited.
- `boundary_table.py --check` reported all 19 cases matching, recomputed on my
  machine against the predictions frozen in `ce94b1f`.
- `agent watch` exercised **R-v3 against four live boards**, which is the only
  part of this review that used data the patch had never seen. It exited
  `incomplete` because of the deliberate failure, as predicted.

What I did **not** do myself: I did not write the patch, and I did not
re-derive the 2-of-163 scope figure by hand — I read it from
`test_rv3_moves_exactly_the_verdicts_the_amendment_claimed`, which recomputes
it from JS1's committed baseline every time the suite runs. The decision in §7
is mine; the arithmetic under it is the test's.

## 7. The decision — accept, with one defect recorded rather than fixed

**Accept.**

| | |
|---|---|
| Property holds on real data | `test_no_posting_outside_the_personas_locations_is_relevant` passes on all 163 real postings, test unchanged from when it failed |
| Fix is at the cause | `remote_ok` became a filter; the bypass branch is gone, not special-cased around |
| Scope claimed in advance, then checked | 2 of 163 moved, both as named in `GATE.md` §8 A2; 161 untouched |
| No test weakened | 0-line diff on the test file that reproduced the defect; the rewritten tests in `test_rule_carried_over.py` constrain more than they did before |
| Nothing else quietly fixed | G1 defect asserted still present |
| Suite | 75 passed, 2 xfailed |

### The case this test would still miss

The patch is right and the test is still blind, in the same place, for the same
reason the original bug existed.

`test_no_posting_outside_the_personas_locations_is_relevant` asks whether every
relevant posting sits in an allowed location, and it decides that with
`any(phrase in loc for phrase in allowed)` — **the same substring comparison G4
itself performs.** The oracle and the implementation share a criterion, so the
test can only confirm that G4 agrees with G4. If the criterion is wrong, both
are wrong together and the suite stays green.

It is wrong in exactly the way A2 just repaired: a substring of a location
string is being read as the identity of a place. Checked against the patched
R-v3:

| location | R-v3 verdict | should be |
|---|---|---|
| `Boston, Lincolnshire, United Kingdom` | **relevant** | not_relevant — Boston is also a town in England, and `locations_ok` contains `"boston"` |
| `Remote - anywhere outside the United States` | **relevant** | not_relevant — a negation that contains the very phrase it negates |
| `New York, Ontario, Canada` | **relevant** | not_relevant |

None of these appear in the 2026-10-31 capture, so the property test passes on
real data while the criterion underneath it is unsound. The first row is not a
contrivance: `"London, United Kingdom"` is in the real capture (3 postings), and
a persona whose `locations_ok` included `"london"` instead of `"new york"` would
have the bug today, on this board, on real bytes.

**Not fixed in R-v3, deliberately.** Fixing it is a change of *comparison* —
parsing a location into place and region and country and comparing structured
fields, or requiring a full-segment rather than substring match — not a change
of control flow, and it needs its own prediction of which verdicts move, its own
diff, and its own review. One change per version. Doing it in the same commit
would have made this packet's scope finding meaningless, and doing it the night
before a deadline, on the rule that produces every verdict in the evidence,
would be the kind of change I would reject if someone handed it to me.

It is recorded as `test_substring_matching_still_admits_places_the_persona_cannot_take`,
marked `xfail(strict=True)` so that the two rows above run on every suite and
**whoever fixes it is forced back here to update this record** — a strict xfail
that starts passing turns the suite red. That is the point: a known defect
written only in prose rots, and one written as a skipped test disappears.

### Two further things not checked

- **R-v3 was validated on one board.** All 163 postings are Greenhouse, one
  company, overwhelmingly US locations. Lever and Ashby write locations
  differently (`categories.location`, free text), and G4's behaviour on those
  shapes is covered only by constructed cases in
  `tests/test_review_g4_location.py`, not by real captures.
- **A null or empty location** falls through to the `locations_ok` branch and is
  rejected with the justification "no allowed location phrase occurs in this
  location". That is the safe direction, but the justification describes a
  location that was present and unmatched, not one that was missing. Arguably
  it should be distinguishable. Not changed here.

---

**Patch authored by** Claude (Opus 5), Cowork session, 2026-11-09.
**Findings in §3 row 2, §5 and §7 raised by** Claude, reviewing its own patch —
which is a real limitation of this packet and is stated here rather than in a
footnote: a self-review catches what the reviewer thought to look for.
**Decision** accept, with the substring-identity defect recorded as a
strict-xfail test and carried to the next version.
**Signed off by** Weiting W. — see `README.md`; her sign-off, not this line, is
the one that counts for the submission.
