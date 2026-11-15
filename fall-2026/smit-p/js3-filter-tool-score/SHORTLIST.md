# The source-grounded shortlist

> **Authorship.** Claude drafted this report and wrote the claim checker. The 18 hand labels
> are Smit's (`audit/shortlist-hand-labels.json`), given without seeing the checker's labels.
> Rebuild: `python3 src/shortlist.py` · compare: `python3 src/shortlist.py --compare` ·
> example: `python3 src/entailment_example.py`.

## Executive summary

Filter version 1.1 keeps three of the 473 postings. This report breaks the reason for each
keep into separate claims ("it is a software role", "it is in the US", "it asks for under 4
years", "it uses TypeScript"…). It then checks each claim against the posting's own words:
does the text **support** it, **contradict** it, or say nothing either way (**insufficient**)?

What it found: matching words is not the same as the text saying what the claim says. The
top-ranked posting (score 5) matched three of Aarav's skills, but only inside "for
example" lists, and it never states a level or a number of years. A mechanical checker
labels 8 of the 18 claims "insufficient". Smit labeled all 18 "supported". The abstention
rule never fired on real data, and the counterexample below shows why: it is built for
unclear numbers, not for silence.

## Run record

| | |
|---|---|
| Postings | the 3 kept by filter v1.1 on `runs/live-20261114` |
| Claims | 18, built by `src/shortlist.py` from the filter's own evidence |
| Checker labels | mechanical rules in `src/shortlist.py` (a record, not a judgment), committed before Smit labeled (`e45695e4`) |
| Hand labels | Smit P., 2026-11-14, one claim at a time with its quote; checker label hidden |

## The evidence rules (from FILTER.md section 3)

**supported**: a quoted sentence of the posting states the claim. **contradicted**: a
quoted sentence states the opposite. **insufficient**: nothing quoted states it, and a word
appearing somewhere is not enough. The checker turns these into rules:

- A skill named only as an example (`e.g.`, `such as`, `like`), as a plus, or as one item in
  an either/or list is insufficient.
- A level claim is supported only by an explicit entry-level phrase.
- No seniority word in the title is an absence, not a statement.

## The shortlist, every claim labeled

| # | Claim | Posting text quoted | Checker | Smit |
|---|---|---|---|---|
| **1** | **Figma · Software Engineer - Full Stack · score 5** | | | |
| 1.1 | Software engineering role | title "Software Engineer - Full Stack" | supported | supported |
| 1.2 | Early-career level | "This opportunity applies to openings at varying seniority levels…" | insufficient | supported |
| 1.3 | In the US | "San Francisco, CA • New York, NY • United States" | supported | supported |
| 1.4 | Under 4 years | (no sentence states a number of years) | insufficient | supported |
| 1.5 | Uses TypeScript | "Strong proficiency in modern front-end frameworks (e.g., React/TypeScript) and back-end technologies (e.g., Ruby, Python, Go, C++, PostgreSQL)" | insufficient | supported |
| 1.6 | Uses Python | same sentence | insufficient | supported |
| 1.7 | Uses PostgreSQL | same sentence | insufficient | supported |
| **2** | **Airbnb · Software Engineer, Profile & Community, Web · score 3** | | | |
| 2.1 | Software engineering role | title | supported | supported |
| 2.2 | Early-career level | "Our job titles may span more than one career level." | insufficient | supported |
| 2.3 | In the US | "Remote, USA" | supported | supported |
| 2.4 | Under 4 years | "3+ years' experience developing Web applications at scale…" | supported | supported |
| 2.5 | Uses TypeScript | "…scalable Web frontend experiences using Javascript/Typescript" | supported | supported |
| **3** | **Spotify · Full Stack Engineer - Music · score 2** | | | |
| 3.1 | Software engineering role | title "Full Stack Engineer - Music" | supported | supported |
| 3.2 | Early-career level | "This range encompasses multiple levels." / "Leveling is determined during the interview process." | insufficient | supported |
| 3.3 | In the US | country "US" | supported | supported |
| 3.4 | Under 4 years | (no sentence states a number of years) | insufficient | supported |
| 3.5 | Uses TypeScript | "Develop and enhance our user-facing layer and frontend SDKs (React/Typescript)" | supported | supported |
| 3.6 | Uses Java | "Design, build and maintain scalable backend services (Java)" | supported | supported |

**Agreement: 10 of 18.** Every disagreement is the checker saying insufficient and Smit
saying supported. After the 18 labels, Smit was asked once about the 2 years claims (no
number in the text) and the 3 level claims (the text says the level is decided later). He
answered "Keep as Supported". Both sets of labels are recorded as given. Note also that
claim 2.4, "3+ years", is supported as a claim about the posting, yet the posting's minimum
is still above Aarav's roughly 2.5 years.

## Relevance is not entailment: one case

**Figma · Software Engineer - Application Platform** (6242561004), `audit/entailment-example.json`.

Filter v1.0 **kept** it, and every rule matched: a role word in the title, a US location, a
"3+ years" requirement, and two résumé skills (AWS, Kubernetes). Read as claims against its
own text:

| Claim | Quote | Label (current checker) |
|---|---|---|
| Under 4 years | "Bring **5+ years** of professional software engineering experience, including 3+ years building production systems with Ruby" | **contradicted** |
| Uses AWS | "Work with cloud and infrastructure technologies **such as** AWS, Kubernetes, Terraform, **or** workflow systems like Temporal" | insufficient |
| Uses Kubernetes | same | insufficient |

The words were relevant and the posting did not entail the claim. Run with the **v1.0** years
logic, the same checker labels the years claim *supported*. A checker that shares the
filter's definitions repeats the filter's mistake. Smit's hand verdict on this posting in the
audit was "not relevant".

## The abstention rule, and a counterexample that exposes its limits

**The rule** (FILTER.md R3, R4, R5): say "I cannot tell" when the posting has no description,
when the location is missing or says only "Remote", or when the years requirement is a range
across the 4-year line or "years of experience" with no number.

**What it did on real data:** across 473 postings it fired **0 times**. Every posting had a
description, a location with a country, and either a clear number or no years sentence at all.

**Counterexample:** **Figma · Software Engineer - Full Stack**, ranked first with score 5.
The posting states no number of years and says it "applies to openings at varying
seniority levels". By the evidence rules, two of the claims the keep rests on are
insufficient (1.2 and 1.4). The agent should have said "I cannot tell" and instead kept it
with the highest score. The abstention rule watches for unclear numbers, but silence and
"level decided later" look like *no problem at all* to it. The same holds for the Spotify posting.

The Claude judge showed the same edge (`WHAT-MOVES-THE-SCORE.md`). On this one posting,
two identical runs answered "keep" and then "cannot_tell", and the prompt sentence that
names this case turned it into "cannot_tell". Smit judged the posting relevant.
