# The reject audit

Chapter 7. What the filter threw away, judged by hand, blind.

**F-v2 / S-v5 / E-v1a, threshold 6**, over the 452 postings JS2 captured on
2026-11-11T00:18Z.

```
shortlisted         4
below_threshold    20
gated             417
cannot_score       11     (no body on that board; not a zero, not a rejection)
--------------------
total             452
```

"Rejected" here means **`gated` or `below_threshold`** — 437 postings.
`cannot_score` is not a rejection and is audited separately in §6.

---

## 1. The sample, fixed before it was drawn

`FILTER.md` §6 committed to the shape of this sample before any of it existed.
`tools/make_audit_form.py` drew it with seed **20261123**:

| stratum | n | why |
|---|---|---|
| random rejects | **30** | drawn with the recorded seed from all 417 gated postings, so the audit is not a tour of the cases I found interesting |
| within ±2 of the threshold | **17** | every one of them. The threshold is the number most likely to be wrong and these are the cases that decide it |
| kept | **14** | all of them, so the audit can find false positives and not only false negatives |
| **distinct postings** | **48** | the strata overlap: 13 of the 14 kept also sit within ±2 |

38 of the 48 carry a body. The other 10 are Greenhouse postings with no
description — judged on title, location and department, which is everything
the filter had too.

**The sample was drawn under S-v2 and two amendments have moved the buckets
since**, so before any of it was labelled, `tests/test_audit_sample.py`
checked that it still covers what §6 promised: all 4 postings currently
shortlisted are in it, all 10 currently within ±2 of the threshold are in it,
and 30 gated postings are in it. A sample that silently stopped matching its
own strata would have spent the labelling on the wrong postings, and that is
only worth discovering **before** somebody sits down with the form.

## 2. Blind, by construction

The form showed **no score, no bucket, no gate**, and shuffled the order with
the recorded seed. The filter's own decisions were written to a separate file,
`audit/audit-answer-key.json`, at the same moment the form was generated, and
were not read until the labels came back.

This is a direct fix for a failure in JS1: Claude told me the agent's verdicts
before I labelled, so those four labels were not blind and no number computed
against them could be presented as independent. Nothing was asked of anyone's
self-discipline here — the decisions are simply not in the file I opened, and
`tools/make_audit_form.py` greps its own output to prove it.

The question on every row was the same:

> 这条职位,你希望它出现在你的候选名单里吗?
> *(Would you want this posting on your shortlist?)* — yes / no / unsure

## 3. My verdicts against the filter's

<!-- AUDIT RESULTS -->

## 4. What a sample this size can show — written before the numbers existed

This paragraph is copied from `FILTER.md` §6, which fixed it before any label
was taken, so that no reading of the result could soften it afterwards.

> A hand sample of 30–45 postings out of 452 gives a disagreement **count**,
> not a rate for the corpus. With 30 rejects sampled, one disagreement is a
> point estimate of 3.3% whose 95% interval runs past 17%; the honest sentence
> is "I checked 30 and disagreed with *n* of them", never "the filter's
> false-negative rate is *n*/30". No number in any report here is to be
> written as a rate for all postings.

Three things make this sample weaker than its size suggests, and they are
worth naming before any number is read:

- **The strata are not a random sample of the corpus.** 30 of the 48 are a
  random draw from the gated pile; the other 18 were chosen *because* they sit
  near the threshold or were kept. Anything computed across all 48 mixes a
  random sample with two deliberate ones and is not an estimate of anything.
- **One labeller, no second opinion.** There is no inter-rater agreement to
  report, so "disagreement" means disagreement with *me on that evening*, and
  I have no measurement of how stable that is.
- **I wrote the filter's word lists.** Blindness stops me seeing the verdicts;
  it does not stop me having the same blind spots as the thing I am auditing.
  If `infrastructure` looked like a signal to me when I wrote S1, it may well
  look like one to me when I read a posting.

## 5. The threshold, refit on held-out labels

<!-- THRESHOLD RESULTS -->

## 6. The 157 postings this audit cannot speak to

`cannot_score` holds 11 postings in the current run, but the real number is
larger and worth stating plainly: **157 of 452 postings — 35% of everything
JS2 collected — have no description at all**, because Greenhouse's public
board endpoint does not return one. Most are rejected by F1 or F2 on their
titles before the body matters; 11 clear the gates and then have nothing to
score.

The 10 body-less postings in this sample were judged on title, location and
department. That is a fair test of the *gates*, and no test at all of the
*scorer*, because the scorer never ran on them.

**So nothing in this audit is evidence about how the filter reads a posting it
cannot read.** The honest position is that a third of the corpus is outside
everything measured here, and the fix is not a better filter — it is asking
Greenhouse for the description, which JS2 did not do and JS3 cannot, having no
network.

## 7. The false friends

`FILTER.md` §6 required at least one word that matched for the wrong reason,
found in the real corpus and named. Running every signal word against the 295
postings with text and **reading the sentence each one matched** produced
three. All three were cut in amendment A2.

### `infrastructure` — fired on 206 of 295, and on 177 of 177 at one board

Every single Ramp posting opens with the same sentence:

> ABOUT RAMP — Ramp is building the smart **infrastructure** for finance
> teams, embedded in the transaction flow of every dollar a business spends.

`infrastructure` appears in the first 300 characters of **all 177** Ramp
postings. So Ramp's Sales, Legal, Payroll and People & Talent postings were
each collecting +2 from a sentence about the company, and the signal
distinguished nothing at all on the board that supplies 60% of the scoreable
corpus.

This is the most instructive of the three, because it is not a word with two
meanings. It is a word used correctly, in a sentence that is simply not about
the job. **A span can be real, quotable, and still evidence about nothing.**

`reports/what-moves-the-score.md` §2 measured what putting it back did under
S-v3: the shortlist went from 6 to 11. A constant added to most of the corpus
is a threshold change wearing a word list's clothes.

**And then the cut was undone.** Amendment A4 taught the scorer which section
a span sits in, and the sentence this word fires on is a company blurb. With
that in place the word fires 21 times across the 24 scored postings, **20 of
them earning 0**, and the 21st is

> The work runs from video pipelines and serving **infrastructure** through
> mobile and web clients

— a true statement about a real job, in that posting's own description of the
work. A5 reinstated the word on that measurement.

So this entry is a false friend that **stopped being one** when the filter
learned to read structure. The cut was the right response to the measurement
and the wrong response to the problem: A2 removed a word to stop a sentence
counting, and A4 made the sentence stop counting. The other two below did not
survive the same question — their wrong matches are in duties and requirements
sections, where A4 gives them full weight.

### `go` — 55 matches, at most 9 of them the language

| the match | what it was |
|---|---|
| "You'll **go** deep on the product, define positioning and messaging" | a Product Marketing posting |
| "Act as the **go**-to technical resource for high-priority accounts" | a Solutions Engineer posting |
| "building firm-specific **go**-to-market motions" | a Channel Partner Manager posting |
| "you can **go** deep on a finding rather than just…" | a Security Engineer posting |

Roughly 46 of the 55 are the English verb or a compound. Whole-word matching
does not help, because `go` **is** a whole word — the defence that stops `api`
firing on "rapid" is structurally unable to stop this.

**There was no narrower replacement available.** `golang` appears **nowhere**
in the corpus, so cutting `go` makes the Go language undetectable. That cost
is recorded in `FILTER.md` §7 A2 and in README.md's sign-off rather than
quietly absorbed.

### `1-2 years` — the new-graduate bonus, landing on a sales job

S5 was worth +4, the largest positive signal, described in FILTER.md §1 as
"the single strongest signal that I am inside the posting's intended
audience". In the whole corpus it fired **once**:

> - **1-2 years** of quota-carrying SaaS **sales** experience in an SMB,
>   transactional, or high-velocity closing role.

A year range states how much experience is wanted. It says nothing about
whether a new graduate may apply, and here it attached +4 to a job requiring
sales experience.

**And cutting it exposed something larger.** With the ranges gone, S5's
remaining phrases are `new grad`, `new graduate`, `entry level`,
`entry-level`, `early career`, `university graduate` — and **not one of them
occurs in any of the 295 postings**. S5 cannot fire at all. That is not a
broken signal; it is a fact about these four boards, and it is pinned by
`test_s5_cannot_fire_on_this_corpus` so that the day a board does say it, the
test fails.

## 8. Every rule added, cut, or rejected after measuring

| | rule | measured before the change | outcome |
|---|---|---|---|
| **A1** | F3 required a positive match against Greenhouse's `Job Family` vocabulary | F-v1 put **0** of 452 postings in front of the scorer; 24 with bodies died at F3 on titles F2 had accepted | **replaced** by a denylist of non-engineering functions |
| **A2** | `infrastructure` in S1 | 206/295, 177/177 on one board, from boilerplate | **cut** |
| **A2** | `go` in S2 | 55 matches, ≤9 the language | **cut**, with the cost stated |
| **A2** | `0-2 years`, `1-2 years` in S5 | 1 match, a sales job | **cut** |
| **A3** | S6 as a list of literal strings | missed "a minimum of 5 years" on the **top-scoring shortlist entry**, and missed `3+ years` entirely | **rewritten** as a number ≥ 3 in four forms |
| **A3** | `evidence._YEARS` | same two phrasings missing, so a five-year posting came back `insufficient` instead of `contradicted` | **rewritten** to match S6 exactly |
| **A4** | spans were scored the same wherever they sat | 2 of the 6 shortlisted scored **all** their points from a NICE TO HAVES block; across the 24 scored, `company` sections held 14 hits | **accepted** after the rejection below was re-examined: required/duties ×1, optional ×½, company ×0, unknown ×1, penalties never scaled |
| **A5** | `infrastructure`, cut by A2 | with A4 in place it fires 21 times and earns 0 on 20 of them | **reinstated** |
| — | ~~weight a span by the section it sits in~~ | — | **rejected, then reversed.** The rejection said it needed a per-board heading parser and was "a subsystem, not an amendment". I had not measured. All 295 postings with text carry a recognised heading and the vocabulary is about thirty strings. The reason was wrong, so the rejection went, and both halves stay in this table |
| — | `MIN_WALL_YEARS` from 3 to 1 | P-v3 read "Minimum 1 year" as disqualifying; `evidence.py` abstains | **rejected**: a fourth amendment on the last evening, and the audit should decide it |
| — | "body says senior → contradicted" | would mislabel "Partner closely with **senior** and staff ML engineers" | **rejected**: the difference is grammatical and E-v1a has no grammar |

Five rules changed and two rejected, with one rejection reversed after it was
measured rather than estimated. The two that stand — `MIN_WALL_YEARS` 3 → 1,
and "body says senior → contradicted" — are in README.md's sign-off as things
this filter does not do.

The reversal is the entry I would point at. I rejected section weighting on a
guess about how much work it was, wrote the rejection down with its reasoning,
and the written reasoning is what made it cheap to check later and obvious
that it was wrong. A rejection recorded with a reason is a decision that can
be revisited; a rejection that never got written down is just a thing that
did not happen.
