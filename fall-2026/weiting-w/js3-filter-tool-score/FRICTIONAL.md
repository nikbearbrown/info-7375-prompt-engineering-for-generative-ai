# Friction log

What fought back, what I got wrong, and what is still wrong. Dated. Nothing
here is a near-miss with a happy ending stapled on; where something is still
broken it says so and says why it was left.

---

## 0. A defect in JS2, which I am recording here rather than quietly fixing

**Found 2026-11-23, at the start of this layer.**

JS2's `README.md` tells a TA to verify that the gate was written before the
code by running `git show --stat ce94b1f`. Its review packet cites a
three-commit sequence `3a0896f → 7bf3d11 → 250dff8`, and its FRICTIONAL cites
`12390f4 → d6013a8`.

**None of those commits exists in the repository a TA reads.** Checked:

```
$ for h in ce94b1f 3a0896f 7bf3d11 250dff8 12390f4 d6013a8; do git cat-file -t $h; done
  (all six: not found)
$ git log --oneline -- fall-2026/weiting-w/js2-loop-tools-diff
  1fb701b3 INFO 7375 JS2: job-search agent, the loop, the tools, and the diff
```

The JS2 folder reached GitHub as **one commit**. The history that proved the
ordering was built in a container-local repository that was never pushed, and
JS2's documents cite it as checkable evidence throughout.

The content was never in question — the files, the tests and the evidence are
all real and all there. What is wrong is that JS2 told a reader to check
something they cannot check.

**Not fixed, deliberately.** JS2 was submitted on 2026-11-10 against a named
commit hash. Editing a graded submission after its deadline is worse than the
defect. What I did instead is change the process: **every commit in this
layer was made in a clone of the real repository**, so `git log` on GitHub
shows FILTER.md frozen alone, then the code, then each amendment in order.
README.md §"The gate came first" gives the command, and this time it works.

---

## 1. The filter, as frozen, decided nothing

**2026-11-23.** F-v1 implemented exactly as written, run over all 452
postings: **0 reached the scorer.** Every one of the 295 that carry a body was
stopped by a gate — 167 at F1 and 104 at F2, both correct, and 24 at F3.

The 24 were titles F2 had already accepted: "Software Engineer, Backend,
Developer API", "Machine Learning Engineer", "Backend Engineer - Data
Platform". `target_job_families` is `['software engineering', 'machine
learning', 'data science']` — **Greenhouse's `Job Family` vocabulary**. Ashby
writes `Engineering` in a field called `department`; Lever writes `Platform`.

The gate was testing which applicant-tracking system a company bought.

FILTER.md §5 had said the gates were inherited and not to be re-litigated in
this layer. That sentence was written before I knew the inherited list was
single-board. Amendment A1 inverts F3 to a denylist, and the amendment says
plainly that I built the denylist **after** seeing all 69 distinct family
values and after seeing how many postings each choice admits — which makes it
fitted to this corpus rather than derived from principle.

**What I got wrong inside the fix.** A1 predicted that the 24 would move and
nothing else. **26 moved.** The two extras are Greenhouse postings whose
`job_family` is `null`: A1's own text says an absent family passes F3 because
absence is not denial, and the prediction's arithmetic did not carry it
through. `tests/test_amendment_a1.py` names those two so the miss cannot be
absorbed quietly.

## 2. Three false friends, one of them in 100% of a board

**2026-11-23**, from running every signal word against the 295 postings with
text and *reading the sentence each one matched* — which is cheap and which I
would not have done if FILTER.md §6 had not committed me to it.

- **`infrastructure`** matched 206/295, and **177/177 on `ashby:ramp`**. Every
  Ramp posting opens "Ramp is building the smart **infrastructure** for finance
  teams". Ramp's Sales, Legal and Payroll postings were all scoring +2 on a
  sentence about the company.
- **`go`** matched 55; at most 9 plausibly name the language. The rest: "You'll
  **go** deep on the product" on a Product Marketing posting, "the **go**-to
  technical resource", "**go**-to-market motions". 84% wrong, and whole-word
  matching cannot help, because `go` *is* a whole word.
- **`1-2 years`**, half of the new-graduate bonus, matched exactly one posting:
  "1-2 years of quota-carrying SaaS **sales** experience".

All three cut (A2) — **and one of the three later put back**. A4 taught the
scorer which section a span sits in, and the sentence `infrastructure` fires
on is a company blurb, so with A4 in place the word earns 0 on 20 of its 21
firings and +2 on a real sentence about a real job. A5 reinstated it. A2's
measurement was right and its diagnosis was wrong: **it removed a word to stop
a sentence counting, and A4 made the sentence stop counting.** The other two
did not survive the same question — their wrong matches are in duties and
requirements sections, where A4 gives them full weight.

The cost of the second cut is stated rather than hidden:
**`golang` appears nowhere in the corpus**, so the Go language is now
undetectable, and I took that over a signal wrong five times in six.

**The consequence of the third is the finding.** With the year ranges gone,
none of S5's remaining phrases — `new grad`, `new graduate`, `entry level`,
`early career`, `university graduate` — occurs in **any** of the 295 postings.
S5 cannot fire at all. The signal FILTER.md called "the single strongest signal
that I am inside the posting's intended audience" is dead here, and the honest
reading is not that it is broken: **none of these four boards published a
posting that says in words that it is open to new graduates.**

## 3. The experience wall was a spelling, not a number

**2026-11-23.** The **top-scoring shortlist entry** — `Machine Learning
Engineer` at ashby:ramp, score 8 — requires "A **minimum of 5 years** of
industry experience". S6 did not fire, because it was a list of literal
strings: `5+ years`, `6+ years`, `7+ years`, `8+ years`, `10+ years`.

So it missed both the other phrasings *and*, which I did not expect when I
started writing the amendment, **other numbers in the same shape**: `3+ years`
and `4+ years` and `9+` were never in the list. Six postings moved, not the
four I predicted.

A3 reads it as a number ≥ 3 in any of four forms, in both places that read
years — S6 and `evidence._YEARS`. The shortlist went 7 → 6 and lost its best
entry, 8 → 2.

**How it was found is the part worth keeping.** I was building
`tools/explain_shortlist.py` for the Chapter 8 deliverable. Rendering the
prompt prints the whole posting body, and that was the first time the
requirements section of the top entry was in front of me. **Writing the tool
server is what found the filter defect.** Nothing in the Chapter 7 work would
have surfaced it, because nothing in the Chapter 7 work prints a whole posting.

### 3b. And A3's own consistency test caught a bug in A3

Applying one rule in two places means they can drift, so a test asserts that
the scorer and `evidence._min_years` agree about every body in the corpus.
They did not, on two postings:

> - **2-5 years** of experience building customer-facing products

The scorer's generic `(\d+) years of experience` alternative grabbed the **5**;
the evidence rules read the range and returned **2**. The evidence rules were
right — a range states its lower bound — so the range alternative now comes
first. **Neither posting was among the 24 scored, so no published number
moved.** The test is the only reason I know about it, which is an argument for
writing the consistency test rather than trusting that one rule stays one rule.

## 4. Two of the six shortlisted postings scored entirely on "nice to have" — fixed, after I rejected the fix

**2026-11-23. Recorded as unfixed, then fixed the same day.**

`Software Engineer, iOS` and `Software Engineer, Android` (ashby:ramp) each
score 6, and **all six of each one's points come from the NICE TO HAVES
section**:

> NICE TO HAVES
> - Experience with backend technologies (Python, Flask, SQL, OpenAPI).
> - Experience with web apps (React, TypeScript).

Their actual requirements are Swift and SwiftUI, a minimum of one year of
mobile development, and a shipped app. The filter matched these postings'
*optional* list and scored nothing from their *required* list.

**I rejected the fix, in writing**, in `reports/reject-audit.md` §8: weighting
spans by section "means parsing each board's heading conventions … and that is
a new subsystem, not an amendment."

**Then I measured, and the reason was wrong.** All 295 postings with text
contain at least one recognised heading, and the vocabulary is about thirty
strings — `WHAT YOU'LL DO`, `What You'll Do`, `WHAT YOU NEED`, `Who You Are`,
`NICE TO HAVES`, `ABOUT RAMP`, `OTHER NOTICES`. It is a table, not a
subsystem. Ten minutes of measuring against an estimate I had made without
any.

A4 weights a positive hit by where it sits: required ×1, duties ×1, optional
×½, company ×0, unknown ×1. Penalties are never scaled, because a rule that
can be evaded by moving a sentence is not a rule. Both postings dropped, 6 →
3, and the shortlist went 6 → 4.

**Both halves stay in the record.** A rejection written down with its
reasoning is a decision that can be revisited; a rejection that was never
written down is just a thing that did not happen. The thing that made the
reversal cheap was having written the bad reason where I could read it.

**What is still not read**: the heading table is thirty strings taken off this
corpus. A board writing "Must haves" falls into `unlabelled` and is scored at
full weight — the safe direction, and still not reading. That is now the
sign-off item in place of this one.

## 5. One year versus three, where the code and the reading disagree

**2026-11-23, unfixed.** P-v3 read "Minimum 1 year of experience in mobile
development" and answered that the posting is not open to a new graduate.
`evidence.py` labels the same posting `insufficient`, because `MIN_WALL_YEARS`
is 3.

Both are defensible — A3 hand-set 3 as "already outside what a new graduate
has" — but they disagree about a real posting, and the disagreement is between
a number I picked and a reading anyone would make.

**Left alone on purpose**, and then the audit answered it.

The audit's **only false positive** — the single posting the filter kept and I
rejected, blind — is `Software Engineer, Backend, Credit`, whose requirements
read "**2+ years** of backend engineering experience". `MIN_WALL_YEARS` is 3,
so S6 never fired and the posting kept its six points.

So the number I hand-set and declined to revisit is wrong, in the direction
two independent things now point: a model reading a posting, and a blind hand
label.

**Still not changed.** One labelled posting is a reason to look, not a mandate
to move a constant, and moving it after seeing which way the audit went is the
one kind of change this whole structure exists to prevent — every other
amendment here predicted its effect before it was applied, and this one would
be fitted to a sample of one. It is named in README.md's sign-off as the
best-evidenced next change, which is what an audit is supposed to produce.

## 6. The strict prompt looked better and was worse

**2026-11-23.** I wrote P-v1 (loose rules, full posting) and P-v2 (strict
rules, only the spans that scored), compared the two answers, and had to throw
the comparison out: **that changes the prompt and the context at the same
time**, which is two objects in a section about changing one. P-v3 — strict
rules, full posting — is what isolates them.

The result that survived the correction is the better finding anyway. P-v2
abstained, which is exactly what the strict rules were written to produce —
**and it abstained because it was starved, not because it was careful.** Given
three spans drawn from the NICE TO HAVES section, it had no way to learn the
posting demands Swift and a year of mobile work. Its "I cannot tell" is right
about the spans and wrong about the job.

Comparing P-v1 to P-v2 would have told me the strict prompt was an improvement.

## 7. Where the evidence rules stop, with a counterexample

`Software Engineer, Backend, Accounting` says "We're looking for a **Senior
Backend Engineer**". E-v1a labels the new-graduate claim `insufficient`,
because its contradiction trigger is a years *number* and the posting said it
in a *word*. A person answers `contradicted` instantly.

**The obvious repair is wrong**, which is why it is not made: "body says
senior → contradicted" would mislabel `Machine Learning Engineer -
Subscriptions`, where the sentence is "Partner closely with **senior** and
staff ML engineers" — the colleagues, not the role. The difference is
grammatical and E-v1a has no grammar. An `insufficient` sends me to read the
posting; a wrong `contradicted` drops it silently, so abstention is the safer
failure and the one I kept.

## 8. My own mistakes, which are a different category

- **Three numbers in `reports/tool-evaluation.md` were wrong when I wrote
  them.** I said the filesystem server declares 17 tools, 11 of them
  `readOnlyHint`, with 16 descriptions mentioning allowed directories. Parsing
  the transcript gives **16, 10 and 15**. I had counted by eye. Corrected
  before committing, and the only reason it was caught is that I parsed the
  transcript to check rather than re-reading my own sentence.
- **I claimed `inherited/` was byte-identical to JS2** in its own `__init__`
  docstring, minutes after rewriting its import lines myself. Corrected the
  same hour, and the claim is now a test that compares line by line.
- **The first version of the "nothing is trained" test failed on its own word
  list.** It searched every shipped module for the substrings `torch` and
  `tensorflow`; `jobfilter/score.py` contains `pytorch` and `tensorflow` as
  **signal words in S4**. A substring check mistaking a word list for a
  dependency — the false friend problem turning up inside the test suite that
  exists to catch false friends. Fixed to check imports.
- **I found `api` does not match "APIs" by writing a broken test fixture.**
  A test of mine said "We build APIs in Python" and expected 4 points; it
  scored 2. Whole-word matching makes the plural a different word. Across the
  corpus `api` matches 29 postings and misses **42** that write only "APIs",
  10 of them among the 24 that get scored. Not fixed — a word-list change
  needs its own amendment and its own prediction — but the test now asserts
  the gap at 42 so it cannot be forgotten.
- **A GitHub fetch I assumed would work, didn't.** The plan for the second
  tool-server evaluation was to read the official servers repository through
  `gh`; this session has no access to it. npm did work, and running the server
  turned out to be far better evidence than reading it would have been, so the
  obstacle improved the deliverable. Recorded because it was luck, not
  judgement.

## 8b. The measurement I added last was the one that undercut the rest

**2026-11-23, after the labels came back**, checking the submission against
the assignment rather than against my own plan.

The requirement is to change one object at a time and **measure on labels you
held out**. I had measured each change's effect on the *bucket counts*, which
is a description of the filter and not a measurement of whether a change is
an improvement. So I wrote `tools/measure_one_change.py` to score each change
against the held-out half of the labels.

The baseline came out **21 of 21**. That looked like a good result for about
a minute, until I added the row that had to be there: **a filter that rejects
every posting without reading it scores 20 of 21.** On the training half mine
is worse than that — 18/21 against 19/21.

Three of 42 decided labels are `yes`. One of them is in the held-out half.

So the measurement I added to satisfy a requirement is the one that says the
rest of the measurements cannot distinguish this filter from pessimism. I
would rather have found this in week one than at 18:10 on the due date, and
the only reason I found it at all is that adding a trivial-baseline row is
cheap and I have been asking all day what each number has to be read against.

**Not fixed, and not fixable here.** More postings sampled the same way give
the same 93% "no". It would need labels stratified on my own verdict — which
cannot be done before labelling — or a corpus with more postings this persona
would want, and A2 already established that none of these four boards
publishes one that says so in words.

What survives: the labels can still see the three changes that make things
*worse* (undoing A4, W3, dropping Lever's `lists`), and those are in
`reports/what-moves-the-score.md` §4b.

## 9. What is still unresolved

| | where |
|---|---|
| The heading table is ~30 strings read off this corpus; another board's wording lands in `unlabelled` | §4 |
| `api` does not match "APIs" — 42 postings missed, 10 of them among the 24 scored | §8 |
| `MIN_WALL_YEARS = 3` disagrees with an ordinary reading of "Minimum 1 year" | §5 |
| E-v1a cannot read "Senior" as a contradiction, and the obvious fix is wrong | §7 |
| 157 postings (35%) have no text at all, so nothing here speaks to them | FILTER.md §3 |
| The Go language is undetectable, and A4 does not rescue it | §2 |
| A1's denylist is fitted to this corpus, not derived | §1 |
| The labels cannot distinguish the filter from "reject everything" | §8b |

**Resolved since the first draft of this file:** section weighting (§4, by A4)
and the `infrastructure` cut (§2, reversed by A5).

## 10. Traceability

One Cowork session with Claude (Opus 5) on **2026-11-23**. The first column
describes what each commit was for; it is **not** a quotation of anything I
said, because I approved a plan rather than dictating steps, and the session
transcript stays on my machine per the assignment's privacy rule.

| what the commit was for | commit |
|---|---|
| FILTER.md frozen alone, before any code | `921e590b` |
| F-v1 implemented as frozen, plus the measurement showing it is inert | `abd696c1` |
| A1 written up, document first | `1d5d9255` |
| A2 written up, with the predicted effect computed first | `6b091ee6` |
| A1 and A2 applied, both predictions pinned as tests | `f70afda1` |
| the tool server, both transcripts, both evaluations | `eb1248d1` |
| the source-grounded shortlist | `a3d9068d` |
| A3 written up, document first | `6d41e44a` |
| A3 applied, and the range bug its own test found | `81e7c001` |
| what moves the score, four objects one at a time | `455d7519` |
| SOURCES, FRICTIONAL, and the audit analyser written before the labels | `fbdf076d` |
| README, sign-off, driver's seat | `a9ab3e39` |
| a script so this submission does not repeat JS2's §0 defect | `3770f333` |
| the reject audit, everything not needing the labels | `107b1c37` |
| A4 written up, document and heading table first | `5eeb0599` |
| A5 written up, document first | `38e18db7` |

Each amendment is **document before code**, in two commits, so the order is
checkable: `git log --oneline -- fall-2026/weiting-w/js3-filter-tool-score`.
That this works at all is the fix for §0.

## 11. What I would do differently

Every finding in §1 to §4 came from the same move: **writing a claim down and
then running it instead of shipping it.** F-v1's emptiness came from running
the frozen filter before believing it. The false friends came from printing the
sentence behind every match. A3 came from pasting a whole posting into a
prompt. The range bug came from a test asserting that one rule stayed one rule.

The mistakes in §8 came from the opposite: counting by eye, and describing code
I had just changed from memory of what it used to be.
