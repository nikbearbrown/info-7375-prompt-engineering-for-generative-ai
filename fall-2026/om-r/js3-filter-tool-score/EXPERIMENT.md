# EXPERIMENT.md — what moves the score (Chapter 9)

Status: **complete. Held-out read once (`ad9ff05`); interpretation in section 7; rule 4 promoted to FILTER.md v1.1.0 in section 8.** (Status line updated 2026-11-22, twice. It was "split fixed; candidate rule 4 not yet designed.", then "split fixed (section 2); rule 4 designed on dev and locked (section 4); held-out not yet read.") Sections are
appended in the order they happen. Nothing above a later section is edited
after the fact, except to fix a typo, and any such fix is noted.

## 1. Every number in the pipeline, and where it came from

None of these were fitted on labels. Until this experiment, no hand labels
existed in JS3.

### Numbers that decide a posting's bucket (filter v1.0.0, `js3/filter.py`)

| Number / list | Value | Origin |
|---|---|---|
| Skill words | 6: Python, RAG, LLM, PyTorch, LangChain, vector databases | **Inherited** from JS1 `CONTRACT.md` / `agent/rule.py`, where they were **hand-set**. They are the first 6 of Priya's 10 `key_skills`; JS1 gives no stated reason for choosing these 6. |
| Skill threshold | `>= 2` of 6 (`SKILL_THRESHOLD = 2`) | **Inherited** from JS1, **hand-set** there. JS1's CONTRACT.md states it without a stated reason. |
| Rule 2 title words | 6: Sales, Account Executive, Solutions Architect, Compensation, Recruiter, HR | **Hand-set** when FILTER.md was drafted. Motivated by JS1's Sampling Report finding (sales/pre-sales false positives), not fitted. |
| Rule 2 AI-building phrases | 5: train, fine-tune, RAG pipeline, build an agent, LLM application | **Hand-set** when FILTER.md was drafted. |
| Rule 3 emptiness | content is "empty" at 0 characters after HTML is stripped and whitespace collapsed | **Hand-set**, implicitly, in FILTER.md rule 3 ("empty or missing"). |
| Match semantics | whole-word, case-insensitive; multi-word phrases match across any whitespace | **Inherited** from JS1 `skill_pattern`. |

### Numbers that change what is shown, not the bucket

| Number | Value | Origin |
|---|---|---|
| `QUOTE_CONTEXT` | 40 characters either side of a matched skill in a quote | **Inherited** from JS1 `rule.py`. Display only. |
| Grounding match | exact, case-sensitive substring after whitespace collapse; a blank quote is never `supported` | **Hand-set** from FILTER.md "Evidence rules". No numeric threshold. |

### Numbers that decide which postings exist to be filtered (JS2 collection, imported unchanged)

| Number | Value | Origin |
|---|---|---|
| `MAX_BOARDS_PER_RUN` | 5 | **Inherited** from JS2 GATE.md, hand-set |
| `MAX_REQUESTS_PER_RUN` | 15 | **Inherited**, hand-set (this run used 6) |
| `MAX_SECONDS_PER_RUN` | 120 | **Inherited**, hand-set (this run took 8.2 s) |
| `MAX_RETRIES` / `BACKOFF_S` | 2 / 1.0 s | **Inherited**, hand-set |
| `TIMEOUT_S` | 30 s | **Inherited** (JS1 → JS2), hand-set |
| `LEVER_PAGE_SIZE` | 100 | **Inherited**, hand-set to Lever's documented maximum |

None of these budgets bound this run: it finished within all of them.

### Numbers that decide which postings were hand-judged (`js3/reject_audit.py`)

| Number | Value | Origin |
|---|---|---|
| Audit seed | 20261121 | **Hand-set** (the date; JS1 convention) |
| Group A size | 30 | **Hand-set** (Om: "at least 30") |
| Group B | 2 forced + 38 sampled; near-threshold = exactly 1 of 6 words, or excluded only by rule 2 | **Hand-set** (Om). Cut from 156 for time (FRICTIONAL.md entry 4). |
| Group C | all 20 | **Hand-set** (census) |

## 2. Dataset and split rule

Written on 2026-11-21, **before** the split was computed.

**Dataset.** The hand-judged postings from the reject audit, with labels
taken from `logs/reject_audit/*_draft.md` (commit `3f25469`). There are 90
labels but **88 distinct postings**: A09 = B034 and A22 = B029 are the same
postings, with one judgment each. The unit is the posting (board, id), so
each of those two counts once. Otherwise the same posting could land in both
dev and held-out, which would leak.

**Split rule.**
1. **Stratify by the filter v1.0.0 bucket.** The strata are "relevant" (the
   20 group-C postings) and "rejected" (the other 68). This uses the
   filter's own output, never a hand label. Without stratifying, a random
   split of 88 could leave held-out with almost no filter-relevant
   postings, and those are the only postings a reject-only rule 4 can
   change.
2. **Shuffle each stratum with a new seed.** Within each stratum, sort by
   (board, str(id)), then shuffle with `random.Random(7375)`. Seed **7375**
   is the course number: new, and not 20261121, so the split is independent
   of the audit draws.
3. **Cut 60/40.** The first `round(0.6 * n)` postings of each stratum are
   **dev**; the rest are **held-out**. That gives relevant 12 dev / 8
   held-out and rejected 41 dev / 27 held-out: 53 dev, 35 held-out.

The split is computed by `js3/experiment.py split` and written to
`logs/experiment/split.json`. That file holds membership only, never
labels.

**Held-out guard.** `js3/experiment.py` returns held-out labels only when
`JS3_FINAL_HELDOUT=1` is set. Every such read is appended to
`logs/experiment/heldout_access.log`. The plan is exactly one read: the
final measurement, after the rule is locked and committed.

**Prior exposure, stated plainly.** The guard controls what the code reads.
It cannot undo what has already been seen:
- **Claude has read every label.** While writing REJECT-AUDIT.md, Claude
  Code read all 90 labels and reasons, including the four group-C reasons
  quoted there (C05, C07, C13, C14) and C03's.
- **The rule's shape came from the full data.** Its outline (year counts,
  seniority words, management scope, graduation/clearance patterns) was
  proposed after reading REJECT-AUDIT.md section 5, and so after seeing
  examples that may land in held-out.

So held-out is fresh to the *code and the tuning* (which words, which
year cutoff), not to the people designing the rule. A held-out result is
therefore weaker evidence than a truly blind one, and section 7 says so. (Cross-reference corrected 2026-11-22: it read "section 6", a section that was never written.)

## 3. Known problems with this experiment's design, stated before rule 4 exists

Written on 2026-11-21, after the split was committed (`277b7d6`) and
before any rule-4 code or design. No held-out label has been read:
`logs/experiment/heldout_access.log` does not exist.

**Problem 1:** the held-out split is a mechanical firewall against the
CODE reading labels prematurely. It is not a guarantee the rule's designer
was blind to them -- Om had already read all 90 hand judgments while
writing REJECT-AUDIT.md, before this split existed. This is disclosed, not
hidden.

*Added fact:* the same is true of Claude Code. It read all 90 labels and
reasons, quoting C05, C07, C13 and C14 and C03's reason in REJECT-AUDIT.md,
before this split existed. REJECT-AUDIT.md also states publicly that group
C is 19/20 not relevant with C03 the only keep. C03 is in dev, so the
labels of all 8 held-out filter-relevant postings can be inferred from
that report alone.

**Problem 2:** because rule 4 only rejects, held-out precision-on-relevant
can only be 0/8 or undefined -- this dataset structurally cannot test
whether rule 4 wrongly rejects a genuinely good posting, only whether it
catches known false positives. This is a real, nameable limit of this
experiment's design, not a result to force into looking more conclusive
than it is.

**Problem 3:** B021 and B032 are already rejected by rule 1 (Palantir
descriptionPlain gap, FRICTIONAL entry 1), so rule 4 cannot change their
bucket. The only testable thing is whether rule 4 WOULD fire on them if it
got the chance.

**What follows from these.** Section 4 adds a standalone diagnostic: rule
4 run alone, ignoring rules 1 and 2, over all 88 judged postings.
- **B032 (held-out, hand-relevant) is the one real pass/fail check.**
  Rule 4 must not fire on it.
- **B021 (dev, hand-relevant but provisional)** is reported as observed,
  without being scored as a pass or a fail, because Om's label is
  provisional on eligibility.
- **Rule 4's overall fire rate** across the 88 is reported as a
  descriptive number, not as a precision claim.

### Two design decisions, fixed before rule 4 exists (2026-11-21)

**Decision A: when the standalone diagnostic runs.** Rule 4's standalone
behavior on the 53 **dev** postings may be inspected during design. Its
behavior on the 35 **held-out** postings, including the B032 pass/fail
check, is computed exactly once, as part of the single guarded final read
(`JS3_FINAL_HELDOUT=1`), after the rule is locked and committed. Looking at
how the rule fires on held-out postings during design would be a peek,
even with their labels locked.

**Decision B: graduation-date and clearance patterns are flagged, never
rejected.** Rule 4 rejects only on explicit year-of-experience minimums,
seniority title words, and management-scope phrases. A graduation-date or
clearance requirement produces a flag (reported in the result, visible to
the user), never a rejection.

- *Made with B032's text already known.* While verifying REJECT-AUDIT.md,
  Claude Code confirmed that B032 (held-out) says "Security clearance or the
  ability to obtain a clearance." and "Graduating in 2028." So it was known
  in advance that a reject-on-graduation/clearance part would fire on B032
  and fail the one real held-out pass/fail check. This decision is not blind
  to that, and it is stated here so nobody has to infer it.
- *Independent justification, which does not depend on B032.* Om's
  labeling rule (REJECT-AUDIT.md section 1), written before this experiment
  existed, already sorts these into different outcomes. A "clear
  multi-year minimum, a staff-level scope, or a management requirement
  **rules it out**", while a graduation-date or clearance requirement that
  "the profile I have doesn't tell me whether she meets" is something Om
  says to "**flag that as an open eligibility check**". Rule 4 mirrors that
  existing split: the "rules it out" items reject, and the "open
  eligibility check" items flag. The reason is also substantive.
  `resume.json` has no graduation date and no clearance field, so a
  mechanical rule cannot know whether such a requirement is met. Rejecting
  would be claiming information the system doesn't have.
- *What this costs the experiment.* Because the choice was made with B032
  known, B032 passing the held-out check is weaker evidence than it looks.
  It shows the rule is consistent with the labeling rule's flag-vs-reject
  split, not that a blind design would have got it right.

## 4. Candidate rule 4 (v1.1.0-candidate): design and dev measurement

Written on 2026-11-22 (UTC), before any held-out read. Everything in this
section is committed **before** `JS3_FINAL_HELDOUT=1` is ever set.

**Design evidence: the dev split only.** `tools/dev_evidence.py` (log 14)
printed every year-count, management and eligibility snippet in the 12 dev
filter-relevant postings, along with their dev labels.

**The rule.** `js3/rule4.py` holds rule 4 and `js3/filter_v110.py` is
v1.0.0 plus rule 4. `js3/filter.py` (v1.0.0) is unchanged, and a test
asserts that. Rule 4 rejects on any of the following:
- **(a) An explicit experience minimum of 3 years or more** in content:
  "N+ years", "N-M years" (taking the lower bound N), "at least N years",
  "minimum (of) N years", or "N or more years". N can be digits or a
  spelled-out number. The spelled-out form is not evidenced in dev, where
  every posting uses digits; it was added as the plain-English equivalent
  before any held-out read.
- **(b) A seniority word in the title:** Staff, Principal, Director,
  Manager, or Head of.
- **(c) A people-management phrase in content:** "managing managers",
  "lead a team of N", "manage/managing ... team(s)", "own(s) the P&L",
  "P&L ownership/responsibility", "people management", or "direct reports".

Graduation-date and clearance requirements are flagged and never reject
(section 3, decision B).

**Test-first.**
- Log 15: tests against the no-op stub, 19 failures and 4 errors.
- Log 16: the first real run. 2 tests failed because of a bug in my code:
  the "at least N years" regex had no whitespace between "least" and the
  number, so it could never match "At least 4 years" (the C07/C09/C10
  pattern).
- Log 16b: after the fix, all 22 pass.

The bug was found by the tests, before any dev measurement. No design
change followed from seeing a measurement.

### Dev results (logs 17 and 17b, `logs/experiment/dev_measurement.json`)

| Dev, filter-relevant bucket | Kept | Hand-relevant among kept | Precision on relevant |
|---|---|---|---|
| v1.0.0 (rules 1-3) | 12 | 1 (C03) | 1/12 = 0.083 |
| v1.1.0-candidate (+ rule 4) | 2 | 1 (C03) | 1/2 = 0.500 |

- **10 of the 11 dev false positives flip to rejected:** C02 (Staff), C05
  (12+ years, Director, "managing managers"), C07 and C09 (At least 4
  years), C10, C13 (4+ years), C16, C18, C19 and C20.
- **C03, the one real keep, is untouched.** Rule 4 doesn't fire on it and
  raises no flags.
- **C01 is a miss.** *Senior Backend Engineer, AI Engineering: Chat* is
  still kept. Its title word "Senior" isn't on the specified list, and the
  posting states no explicit year count. Om's reason cites "significant
  production Python backend experience", with no number. "Senior" was
  **not** added after seeing this, for three reasons:
  - the word list was specified before the dev measurement;
  - Om's labeling rule names "staff-level scope", not "senior", as ruling
    a posting out;
  - adding a word because of the one dev posting it fixes is exactly the
    fit-to-dev move that held-out is meant to guard against. It would also
    leave no way to see how the rule as specified behaves.
- **C20 is rejected on an alternative path.** Rule 4 counts any qualifying
  mention, so C20 fires on "BS or BA with 4-8 years" even though its PhD
  path is "1-3 years". Om labeled C20 not relevant for experience and degree
  reasons, so the bucket agrees, but the trigger is only part of Om's
  reason. A rule that took the minimum across alternative paths would keep
  C20. "Any qualifying path" was kept as the simpler, more auditable choice,
  and it is recorded here as a known coarse edge.
- **Rule 4 alone (rules 1-2 ignored) fires on 34 of 53 dev postings
  (64.2%).** This is descriptive, not a precision claim: every posting it
  fired on is hand-labeled not relevant, but most of them are already
  rejected by rules 1-2.

### Blind spot found on dev: rule 4 sees only `descriptionPlain` for Palantir

Rule 4 reads the same `content` field as rules 1-3. For Palantir that is
`descriptionPlain` only (FRICTIONAL.md entry 1), and Palantir puts its
requirements in Lever's `lists`.
- **Effect on B021 (dev, hand-relevant, provisional).** Rule 4 neither
  fires nor flags, even though B021 says "Must be graduating in December
  2026 or Spring 2027." That text is in `lists`, out of view.
- **What the full text changes.** With `lists` included, B021 is flagged
  for graduation and rule 4 still doesn't fire, which is decision B working
  as intended. Six other dev Palantir postings change the same way (log 17
  dev check): clearance flags for A02, A10, A11, B012 and B033, and rule-4
  fires for A14, A23 and B004. None of these changes a bucket; rules 1-2
  already reject them.

**Decision, committed before the held-out read.** FILTER.md is not
amended, so rule 4 keeps reading `content` (= `descriptionPlain`). The
`measure` command now also reports a **full-text diagnostic** for every
Palantir posting: rule 4 alone on `descriptionPlain` plus Lever
`lists`/`additionalPlain`. It is diagnostic only and never changes a
bucket. For **B032** and every other held-out Palantir posting, both
results are reported:
- **as-specified**, labeled **VACUOUS** when the full text finds a reason
  or flag that the as-specified run could not see, because the
  requirement text was out of view;
- **full-text**, which is the meaningful pass/fail for B032: rule 4 must
  not fire.

Dev was re-run with the same diagnostic (log 17b), so both splits are
measured with identical code. The dev bucket results are unchanged from
log 17. In dev, B021's as-specified result is labeled VACUOUS, and its
full-text result is no fire plus a graduation flag. With full text, rule 4
fires on 37 of 53 dev postings (69.8%), and on no hand-relevant posting
under either variant.

**Known cosmetic issue, not fixed.** Lever list items have no sentence
breaks, so some full-text flag quotes (B012, B033, B004) start mid-list and
run long. They are still exact substrings of the text that was checked.

**Locked.** Rule 4 as committed with this section is the rule measured
on held-out. Nothing in `js3/rule4.py` or `js3/filter_v110.py` changes
between this commit and the held-out read.

## 7. What this result can and cannot show

Written on 2026-11-22, after the single held-out read (commit `ad9ff05`,
one entry in `heldout_access.log`). The raw result was committed before
this section existed. Sections 7 and 8 take their numbers from the
assignment's steps 7 and 8, so there are no sections 5 and 6.

**1. The result, metric first.**

| Filter-relevant bucket | Dev | Held-out |
|---|---|---|
| Precision on relevant, v1.0.0 | 1/12 = 0.083 | 0/8 = 0.000 |
| Precision on relevant, v1.1.0-candidate | 1/2 = 0.500 | 0/3 = 0.000 |
| **False positives removed by rule 4** | **10/11 = 90.9%** (95% CI 58.7–99.8%) | **5/8 = 62.5%** (95% CI 24.5–91.5%) |
| Hand-relevant postings rule 4 fired on | 0 | 0 |

Held-out precision stayed 0.000, before and after. That is a structural
artifact: held-out's filter-relevant bucket has no true positives, so no
reject-only rule can move its precision off zero. It is not evidence that
the rule failed. The meaningful metric is the false-positive removal rate:
10/11 on dev and 5/8 on held-out. The intervals are exact binomial
(Clopper-Pearson) intervals, the same method as REJECT-AUDIT.md. With 11 and
8 postings they are wide and overlap heavily, so the drop from 90.9% to
62.5% is not by itself evidence of a real difference.

Held-out removals: C08 ("At least 4 years"), C11 ("at least 4 years",
"Manager" in title, "managing ML teams"), C12 ("10+ years"), C15 ("6+
years") and C17 ("3+ years"). Four of the five fired on the year count
alone.

**2. What this design cannot test.** It cannot test whether rule 4 wrongly
rejects a genuinely good posting. Held-out contains exactly one
hand-relevant posting, B032, and that posting is not even in the
filter-relevant bucket: rules 1-2 already reject it, so rule 4 could only
be checked on it through the standalone diagnostic, where it passed (see
point 5). One data point does not support a false-negative-rate claim in
either direction. This was predicted in section 3, problem 2, before the
rule was designed.

**3. The three held-out misses: known gaps, left unfixed.** Rule 4 kept
C04, C06 and C14, and all three are hand-labeled not relevant.
- **C04, *Senior Software Engineer, Security Factory: Code Security*.**
  "Senior" is not on the title-word list. Dev had already missed the same
  way with C01, and section 4 explains why the word was not added after
  that. One caveat about C04: Om's reason does not mention seniority. It
  is "substantial production Go or Rust experience and demonstrated
  application security work". Adding "Senior" would get C04's bucket right
  for a reason Om didn't give, the same partial-reason pattern as C20 in
  section 4. By Om's own reason, C04 belongs at least as much to the third
  gap below.
- **C14, *Software Engineer, Security Business Enablement*.** The year
  threshold is 3, but C14's stated floor is "2+ years building production
  software", which Om's reason cites directly. A threshold of 3 cannot
  catch it, by design.
- **C06, *Threat Research Engineer, Security Factory: Threat Research*.**
  Om's reason is "hands-on security research, analysis, or tooling
  experience is a core qualification outside Priya's stated background".
  Rule 4 has no detector for experience outside Priya's stack, and never
  attempted that category.

**4. Persistence is not proof.** As the assignment instructs, it is stated
plainly: the pattern seen on dev (mostly year-count triggers, with seniority
words and management phrases co-firing) carried into held-out. That
persistence is not proof the rule was "trained". It is also not proof that
it generalizes beyond this dataset of 88 hand-judged postings, this one
collection run (2026-11-21, run `20261121T132140Z`) and this one persona
(Priya Nair, `resume.json`).
- **What it is evidence for:** the *mechanism*, rejecting on an explicit
  experience floor, seniority scope or management scope, is sound enough to
  keep.
- **What it is not evidence for:** that the *parameters* are complete. The
  word list, the threshold of 3 and the phrase list each missed something
  on held-out (point 3).
- **What weakens even this:** both the rule's shape and its parameters were
  chosen by people who had already read every held-out label (section 2;
  section 3, problem 1). Held-out was fresh to the code, not to the
  designers.

**5. The B032 pass is weak evidence.** On the full-text diagnostic (Palantir
`descriptionPlain` plus `lists`), rule 4 does not fire on B032. It flags
graduation ("Graduating in 2028.") and clearance ("Security clearance or
the ability to obtain a clearance."). On the as-specified run it is
VACUOUS: the requirement text was out of view. The decision to flag rather
than reject graduation and clearance was made **with B032's text already
known** (section 3, decision B). So this pass shows the rule is consistent
with Om's flag-vs-reject labeling rule. It is not a clean confirmation. Any
later citation of the B032 result must carry this disclosure.

**6. What was not measured at all:**
- a different persona;
- a different collection run (boards drift between fetches, per JS2's own
  documented findings);
- any posting collected after 2026-11-21;
- whether rule 4 wrongly rejects good postings at any useful sample size
  (point 2).

## 8. Decision: promote rule 4 to FILTER.md v1.1.0

Decided on 2026-11-22, after section 7. **Promoted, as a partial,
honestly scoped improvement.** The dated amendment is in FILTER.md
("Amendment 2026-11-22: v1.1.0, rule 4").

- **Promoted on:**
  - the false-positive removal rate, 10/11 (90.9%) on dev and 5/8 (62.5%)
    on held-out;
  - zero fires on hand-relevant postings in either split, which is weak
    evidence, per section 7 points 2 and 5;
  - the mechanism being sound.
- **Not promoted on:**
  - bucket precision, which stayed 0.000 on held-out and structurally
    could not move;
  - any claim that rule 4 catches every experience or eligibility mismatch.
    It missed 3 of 8 on held-out.
- **The field scope is unchanged.** Rule 4 reads `content`, which for
  Palantir is `descriptionPlain` only. The Palantir limitation (FRICTIONAL.md
  entry 1) stays as documented, and this amendment does not quietly fix
  it. On the full text, rule 4 would see requirements it cannot see now
  (section 4).
- **The known gaps are written into FILTER.md itself:** "Senior" (C04 and
  C01), the threshold of 3 against a 2-year floor (C14), no out-of-stack
  experience detector (C06), any qualifying path counts (C20), and the
  Palantir field scope. A reader of FILTER.md sees the scope without
  needing this file.
- **Not done now: the natural next dev-set experiment.** It would expand
  the title-word list (for example "Senior"), lower the year threshold to
  2, and try an out-of-stack experience detector. It needs a fresh split
  or freshly judged postings: this held-out set has now been read once and
  cannot honestly be used to tune those changes.
- **The code is unchanged by this decision.** `js3/filter_v110.py` still
  carries `VERSION = "1.1.0-candidate"`, the label every measurement in
  this file was recorded under.
