# 0002 — Shortlist claims: code proposes the label, a person decides it

## Status
Accepted (JS3).

## Context
FILTER.md §2 says each claim about a kept posting is supported, contradicted or insufficient,
and that missing information must show up as insufficient next to the verdict. Whether a
sentence states a claim "in the sense the claim means" (a requirement, not "you'll learn
Kubernetes") needs judgment that word matching can't give.

## Decision
- `reports/shortlist.py` reads `audit/all_verdicts.json`, keeps only `relevant` postings with
  status `ok`, and re-reads each JD from its saved raw file with the board's adapter (from
  `data/boards.json`). It makes one claim per justification line of rules 1b, 2, 4, 5, 6 and one
  per skill for rule 3. Rule 1a (exclude words) gets no claim.
- Code only proposes `supported` or `insufficient` (`label_by: "code"`). `contradicted` and the
  final label are left to the hand review, so `final_label`, `final_by` and `note` start empty.
- A supported claim carries a verbatim quote: the first sentence of the plain-text JD (split on
  `.`, `!`, `?` and newlines) that contains the matched words; for years the sentence with the
  smallest number, for salary the one with the largest amount (the numbers the rule decided on).
  Title and location claims quote the posting's own title / location field.
- A rule line starting with `skipped:`, and the visa line "no phrase found", give `insufficient`
  with a null quote: not mentioned is not "will sponsor".
- Each posting gets a summary line `relevant — insufficient: <check names>`.

## Consequences
- A code `supported` only means a sentence with the matched words exists; it can be wrong in
  sense (FILTER.md §1.3 "appears ≠ required"). The reviewer is expected to downgrade those.
- Every quote can be checked by searching the plain-text JD for it.

## Alternatives considered
- Let code also propose `contradicted`. A relevant posting has passed every rule, so code has no
  contradiction to report; any contradiction comes from reading the sense, which is the review's job.
- Asking Claude for the labels. It would add a paid, non-reproducible step before the reviewer,
  and the reviewer would still have to check every quote.
