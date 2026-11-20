# SHORTLIST-PLAN.md — source-grounded shortlist (Chapter 7)

Written 2026-11-20, before any claims are extracted or labeled. Decisions by
Swathi Baba Eswarappa; drafted by Claude Code from them. Approved by me on
2026-11-20, with the decisions recorded below. Committed alone, before the
claims sheet.

## Purpose
- **What I check.** Each of the four postings that filter v1.1 shortlisted
  in `runs/filter-v1.1-2026-11-17T21-47-06-167440-0500/results.json` gets
  its justification checked against the posting text.
- **What it produces.** It produces an evidence-based recommendation per
  posting. It does not change the filter's verdict.

## Who does what
- **Claude Code prepares the evidence.** It breaks each filter
  justification into atomic claims, and copies the filter's exact quotes and
  the path of the posting's reading file. It does not suggest labels, write
  my quotes or notes, or add claims, requirements, sponsorship assurances or
  evidence the filter did not use.
- **I assign every label.** I read each posting myself and fill in
  `my_label`, `my_quote` and `my_note`.

## Label definitions
- **supported:** the posting text directly supports the claim.
- **contradicted:** the posting text contradicts the claim.
- **insufficient:** the posting text does not establish the claim either way.

## Evidence requirements
- **Supported and contradicted need an exact quote.** `my_quote` must be an
  exact, contiguous quote from the posting's title, location or description,
  as shown in its reading file.
- **Insufficient needs an explanation.** `my_note` must say what evidence is
  missing. A quote is optional when no relevant text exists.
- **Absence is not support.** A claim that rests only on the absence of
  restrictive wording is insufficient.
  - Passing R6 means the filter found no citizenship, clearance or
    "will not sponsor" requirement wording.
  - It does not establish that the employer sponsors visas, or that the role
    is open to F-1 OPT.

## Filter verdict vs evidence-based recommendation
- **Filter verdict:** what filter v1.1 returned ("shortlisted") with its
  score. It is recorded in `results.json` and never edited.
- **Evidence-based recommendation:** decided afterwards from my labels, and
  recorded separately in `shortlist/`. A posting can stay "shortlisted" by
  the filter and still be flagged by the recommendation. The filter verdict
  and score are always reported separately from the recommendation, never
  merged or overwritten.

## Shortlist-level abstention rule (approved 2026-11-20)
Proposed as: "A shortlisted posting with any contradicted claim is flagged
'do not recommend'; with any insufficient claim about a requirement
(experience, location, work authorization), it is flagged 'needs human check'
rather than presented as a confirmed fit." Approved with these decisions.

**Requirement claims** are R4 location, R5 experience and R6 work
authorization. The recommendation is taken from the first row that applies:

| Step | Condition | Recommendation |
|---|---|---|
| 1 | Any claim is contradicted (any rule) | do not recommend |
| 2 | Any R1 role claim is insufficient | needs human check |
| 3 | Any R4, R5 or R6 claim is insufficient | needs human check |
| 4 | Otherwise | evidence-supported fit |

- **Precedence.** "Do not recommend" takes precedence over every other
  recommendation.
- **R3 and R7 do not change the result.** An insufficient R3 (seniority) or
  R7 (topic word) claim is documented as an uncertainty but does not, on its
  own, change the recommendation.
- **Disclose caveats.** When a posting is an "evidence-supported fit" but
  has insufficient R3 or R7 claims, those caveats are disclosed with it.
- **No guarantees.** "Evidence-supported fit" means only that the posting
  text supports the filter's claims. It does not imply guaranteed employment
  eligibility, visa sponsorship or F-1 OPT eligibility.

## The filter's existing abstention conditions
Checked against FILTER.md and `job_filter.py` on 2026-11-20. "I cannot tell"
has no score, so these postings are never shortlisted.

| Condition | Where it is written | Commit |
|---|---|---|
| Description missing or empty: text rules cannot be applied | FILTER.md "Expected sources" and "The evidence rules" | `0f689b8` (v1, 2026-11-17) |
| R5: no experience stated and, after reading the title, skills and description, the evidence is still insufficient | FILTER.md R5 and "The evidence rules" | `0f689b8` |
| D3: early-career words count only in the title or a "counts" section; otherwise R5 stays "I cannot tell" | FILTER.md decisions D1–D7 | `8c7c9b8` (2026-11-17) |
| D2: "Remote" with no country | FILTER.md decisions D1–D7 | `8c7c9b8` |
| D6: description not in English | FILTER.md decisions D1–D7 | `8c7c9b8` |
| R2: an "Analyst" title with no recognized responsibilities or skills section | FILTER.md revision "R2 sections" | `ef8ea9e` (2026-11-17) |
| v1.1 (`4a6dcfb`, code `2c3ef12`, 2026-11-19) | added no abstention condition; it made R5 recognize more experience wordings and "university" count only in the title | — |

Not written in FILTER.md, but present in the code since `6e6b4bf`
(2026-11-17): an empty location makes R4 "cannot tell" ("no location given",
`job_filter.py:259`), and so gives "I cannot tell". Decision (2026-11-20):
this is kept as a documentation gap and a known limitation; FILTER.md and the
filter implementation are not changed.

## Claims sheet (Step 2, after this plan is approved and committed)
- **`shortlist/CLAIMS.csv`** has the columns `posting_id, board, title,
  claim_id, claim, rule, filter_quote, reading_file, my_label, my_quote,
  my_note`.
- **One row per atomic claim** for the rules that apply: R1 role, R3
  seniority, R4 location, R5 experience or early-career evidence, R6
  authorization restrictions, and one row for each matched R7 topic word.
- **`filter_quote`** is the exact quote from `results.json`, or "none" when
  the rule passed by absence (e.g. R3 with no seniority word, R6 with no
  restriction wording).
- **`reading_file`** is the existing `audit/read/<board>-<posting id>.txt`
  file (commit `161ebae`), taken from the same saved Nov 17 raw response.
  Each path is checked to exist and to name the same posting.
- **My columns stay blank.** `my_label`, `my_quote` and `my_note` are left
  for me.
- **Checks before commit:** all four shortlisted postings are present, every
  claim traces to a rule result in `results.json`, and every filter quote
  appears exactly in that posting's reading file.

## Unchanged
FILTER.md, the filter implementation, all recorded results, the human audit
and the held-out files stay unchanged.
