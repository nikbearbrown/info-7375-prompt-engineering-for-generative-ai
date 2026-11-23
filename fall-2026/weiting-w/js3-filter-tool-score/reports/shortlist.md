# The shortlist, and what its text actually supports

Chapter 7. Seven postings, 29 claims, every claim labelled against the
posting's own text under E-v1.

Generated from `../js2-loop-tools-diff/evidence/raw/` (JS2's live capture of
2026-11-11T00:18Z) by `python3 -m jobfilter run` and
`python3 tools/make_shortlist.py`. The machine-readable version with every span
is `reports/shortlist.json`.

**F-v2 / S-v5 / E-v1a, threshold 6.** (First written under S-v2 and rewritten
twice since, after A3 and after A4/A5; every version of the table is in §6.)

| | |
|---|---|
| postings in the corpus | 452 |
| reached the scorer | 24 |
| shortlisted | **4** |
| claims made about them | 18 |
| supported | **14** |
| contradicted | **0** on the shortlist; **10 of 24** across everything scored |
| insufficient | **4** |

Every one of the 4 `insufficient` labels is the same claim, on all 4 entries:
**"this posting is open to someone with no professional experience."** The
shortlist cannot answer, for a single one of its entries, the question that
decides whether I can apply. That is the honest state of the evidence and §4
is about why.

---

## 1. The shortlist

Scores are S-v2 after A2. Each entry lists the claims and the span behind each.

| # | score | board | title | supported | insufficient | every point from |
|---|---|---|---|---|---|---|
| 1 | 8 | lever:spotify | Full Stack Engineer - Music | 4 | 1 | duties, unlabelled |
| 2 | 6 | ashby:ramp | Software Engineer, Backend, Credit | 3 | 1 | duties, required |
| 3 | 6 | lever:spotify | Backend Engineer - Data Platform | 3 | 1 | required, unlabelled |
| 4 | 6 | lever:spotify | Machine Learning Engineer - Subscriptions | 3 | 1 | required, unlabelled |

The last column is new in A4 and is the point of it: **no entry on this list
scores a single point from a company blurb or a "nice to have" block any
more.**

### Entry 1 — Full Stack Engineer - Music (lever:spotify), score 8

| claim | label | span | section |
|---|---|---|---|
| the posting mentions backend | supported | «Design, build and maintain scalable backend services (Java)» | duties |
| the posting mentions java | supported | «Design, build and maintain scalable backend services (Java)» | duties |
| the posting mentions typescript | supported | «Develop and enhance our user-facing layer and frontend SDKs (React/Typescript)» | duties |
| the posting mentions infrastructure | supported | «The work runs from video pipelines and serving infrastructure through mobile and web clients» | unlabelled |
| open to someone with no professional experience | **insufficient** | the body states no experience requirement and does not say it is open to new graduates |

Note what the four `supported` labels say and do not say. They say the posting
*mentions* these things. Not one of them says this is a job I can get, and
E-v1a has no rule that would get there from these spans.

The other three entries have the same shape: three `MENTIONS` claims supported
by a quoted sentence, and the new-graduate claim `insufficient`.
`reports/shortlist.json` carries all of them with full spans.

**Two entries that used to be on this list are the reason A4 exists**:
`Software Engineer, iOS` and `Software Engineer, Android` each scored 6, and
every one of those points was inside a `NICE TO HAVES` block while their
requirements asked for Swift and a year of mobile development. §3 and §6.

---

## 2. Relevance is not entailment — a posting that matched for the wrong reason

**`Software Engineer, Backend, AI Spend Management` (ashby:ramp), score 4.**

S4, the machine-learning signal, fired on `inference` and awarded +2. The
sentence it matched:

> You will be involved in key company initiatives such as **inference
> accounting**, and figuring out new and novel ways to help companies not just
> manage, but think about their AI Spend.

Ramp sells expense management. "Inference accounting" here means *accounting
for what a company spends on AI inference* — it is a line item on an invoice.
The word is the machine-learning word; the job is a finance-product backend
job.

So:

| claim | label under E-v1 | and that is correct |
|---|---|---|
| the posting mentions inference | **supported** | the span contains the word |
| this is a machine-learning job | **insufficient** | E-v1 has no rule that gets from this span to that claim |

**The filter still gave it +2.** This is the gap the assignment is pointing at:
the *scorer* matched a word and the *evidence rules* correctly refused to turn
that match into a claim about the job. Relevance put the posting on the list;
entailment was never established and E-v1 does not pretend otherwise.

What I take from it: the score is a ranking heuristic and the claim labels are
the thing with integrity. A reader who sorts by score and stops reading has
been told +2 for a word about invoices.

### A second one, cheaper to miss

**`Software Engineer, Backend, Growth` (ashby:ramp), score −2.** The +2 for
Python and the −6 experience wall came from **the same sentence**:

> - **5+ years** of software engineering experience building production backend
>   systems, with strong proficiency in **Python** or another modern
>   server-side language

"The posting mentions python" is `supported`, and the span supporting it is the
requirement that disqualifies me. A word match carries no sign.

---

## 3. What the gates could not see, because they read the title

Four of the 24 scored postings have a title with no seniority word in it and a
**body that says "senior"**:

| score | title | the body says |
|---|---|---|
| 4 | Software Engineer, Backend, AI Spend Management | «We're looking for a **senior** backend engineer to build the systems behind that experience.» |
| 2 | Software Engineer, Backend, Accounts Receivable | «We're looking for a **senior** backend engineer to own core pieces of that system.» |
| 2 | Software Engineer, Backend, Accounting | «We're looking for a **Senior Backend Engineer** to build across that accounting experience.» |
| 6 | Machine Learning Engineer - Subscriptions | «Partner closely with **senior** and staff ML engineers, and be part of an…» |

F1 passed all four, correctly by its own terms: it reads `title`, and the title
does not say senior. This is the inherited gate doing exactly what JS1 wrote it
to do, on postings where the board put the seniority somewhere else.

**The fourth row is why this is not a one-line fix.** "Partner closely with
senior and staff ML engineers" describes the *colleagues*, not the role — it is
arguably a point in the posting's favour. A rule that said "body mentions
senior → reject" would be wrong on it. The first three rows and the fourth
differ in who the adjective attaches to, which is a question about grammar, and
F1 is a word-matcher. Recorded, not fixed.

---

## 4. The abstention rule, and a counterexample that exposes its limit

**The rule (FILTER.md §2).** The agent must answer "I cannot tell" when the
posting has no body, when the claim needs a field the posting does not carry,
when the only support is markup or boilerplate, or when the spans conflict and
nothing resolves them. For the new-graduate claim, E-v1 decides only two ways:
`contradicted` if the span states ≥3 years, `supported` if it says "new grad",
"entry level" or similar in words. Otherwise `insufficient`, because **absence
is not denial** (E3).

That is why all 7 shortlist entries abstain: **none of the 295 postings with
text contains any of those phrases** (FILTER.md §7 A2), and the 7 shortlisted
ones state no years number either.

### The counterexample

**`Software Engineer, Backend, Accounting` (ashby:ramp).** E-v1 labels "open to
someone with no professional experience" **`insufficient`**, with the reason
"the span neither says the posting is open to new graduates nor states an
experience requirement; absence is not denial".

The posting says:

> We're looking for a **Senior Backend Engineer** to build across that
> accounting experience.

A person reading that sentence would answer the question immediately, and would
answer **contradicted**. E-v1 abstains, because its contradiction trigger is a
*number* and this posting said it in a *word*.

**This is a limit of the rule, not a bug in the code.** E-v1 was written to be
mechanically decidable — §2's whole design is that a claim is decided by a rule
anyone can check, not by a judgement the program makes. The cost of that choice
is visible right here: a rule that only counts years cannot read "Senior".

**And the obvious repair is wrong**, which is the part worth keeping. "If the
body says senior, label contradicted" would mislabel `Machine Learning Engineer
- Subscriptions`, where "senior" describes the people I would work with. The
distinction is grammatical, E-v1 has no grammar, and I would rather it abstain
than guess — an `insufficient` sends me to read the posting, a wrong
`contradicted` drops it silently.

**Not fixed.** Recorded here, in FILTER.md §2's "known limit" paragraph, which
predicted a boilerplate-shaped version of this before measuring, and in
README.md's sign-off as a thing this agent does not do.

---

## 5. What this section does not establish

- **Seven entries is not a validated shortlist.** No claim here is that these
  are good jobs, or the best seven. The claim is that 22 statements about their
  text are supported by quoted spans and 7 are not answerable from the text.
- **`contradicted` fires nowhere on the shortlist** — zero of 24 claims — but
  it does fire, on **10 of the 24 scored postings**, all of them below the
  threshold. That is the right shape: a posting that states an experience wall
  gets −6 and falls off the list, so the shortlist is the place where
  `contradicted` should be rare. Before A3 the count across everything scored
  was lower, because the rule could not read half the phrasings.
- **The claims are about the text, not the job.** Every `supported` label means
  "a quoted span says this". None means "this is true of the job", and E2 is
  the rule that keeps those apart.
- **157 postings are not represented here at all.** Greenhouse sends no
  description, so no claim about them can be supported or contradicted by text
  that does not exist. They are in `cannot_score`, counted separately, and they
  are 35% of the corpus.

---

## 6. What amendment A3 did to this section

This section was first written under S-v2, and then rewritten. The change was
not cosmetic, so the before is kept rather than overwritten silently.

| | S-v2 | S-v3 (A3) | S-v5 (A4, A5) |
|---|---|---|---|
| shortlisted | 7 | 6 | **4** |
| top entry | ML Engineer, **8** | SWE Android, 6 | Full Stack Engineer - Music, **8** |
| claims | 29 | 24 | 18 |
| supported | 22 | 18 | 14 |
| insufficient | 7 | 6 | 4 |
| `contradicted` across all 24 scored | not computed | 10 | 10 |
| entries scoring only from `optional` or `company` | 2 | 2 | **0** |

A3 came out of writing §2 of this very file: rendering the explanation prompt
for the top entry meant printing its whole body, and its requirements say
**"A minimum of 5 years of industry experience"**. S6 was a list of literal
strings and could not read that, nor `3+ years`, which was never in the list
either. The number one entry on my shortlist was a five-year role.

The honest summary is that **the shortlist got shorter by reading more
carefully**, and the thing that made me read more carefully was being forced to
paste a full posting into a prompt. Writing the Chapter 8 deliverable is what
found the Chapter 7 defect.

**A4 and A5 did the other half.** A3 made the filter read requirements
properly; A4 made it read *where a sentence sits*, which removed the two
entries whose every point came from a NICE TO HAVES block. A5 then put back a
word A2 had cut as a false friend, because with sections in place 20 of its 21
firings score nothing and the 21st is a true sentence about a real job.

The shortlist has gone 7 → 6 → 4 across three amendments, and not one of those
steps was a tuning decision: each came from reading something the filter had
been scoring without looking at.
