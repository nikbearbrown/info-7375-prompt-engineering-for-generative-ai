# Source-grounded shortlist: filter v1.1, 2026-11-25 snapshot

`python3 make_shortlist.py v1.1` ([log](evidence/logs/12-shortlist-v1.1.txt), `out/v1.1/shortlist.json`). v1.1 kept
**4 of 1,088** postings. Each posting's justification is a set of claims: one "requires <skill>" claim per matched
topic word, plus "early-career level" and "US-based". Every claim has two labels against the posting's own text:

- **auto**: what `jsagent3/evidence.py` decided, using the FILTER.md §5 rules.
- **read**: what the quoted line actually says when you read the whole sentence. Claude Code drafted these on
  2026-11-25. **I checked all six rows where auto and read differ (marked ✎) and agreed with each one, giving my
  reason** ([audit/my-shortlist-checks-2026-11-25.txt](audit/my-shortlist-checks-2026-11-25.txt)). I did not
  separately re-check the 10 rows where auto and read agree.

Labels: S = supported, C = contradicted, I = insufficient.

### 1. stripe:6042172 · Backend Engineer, Core Technology · US-Remote, Chicago, Seattle, San Francisco · rank 3

| claim | auto | read | quoted text (posting) |
|---|---|---|---|
| requires Java | S | **I** ✎ | "Ability to write high-quality code (in programming languages like Go, Java, C/C++ etc.)" |
| requires distributed systems | S | S | "Hands-on experience contributing to or building large-scale distributed systems" |
| early-career | S | **I** ✎ | "2–12+ years of professional hands-on software development experience" |
| US-based | S | S | location field |

### 2. notion:85947779… · Software Engineer, Early Career (AI) · San Francisco (US) · rank 3

| claim | auto | read | quoted text |
|---|---|---|---|
| requires PostgreSQL | S | **I** ✎ | "have some familiarity with relational databases like Postgres or MySQL" (also listed under NICE TO HAVES) |
| requires distributed systems | S | S | "You have solid fundamentals in data structures, algorithms, and distributed systems" |
| early-career | S | S | title, plus "You have less than two years of engineering experience" |
| US-based | S | S | location field |

### 3. notion:0fb1f7e2… · Software Engineer, Collections Infra · San Francisco (US) · rank 3

| claim | auto | read | quoted text |
|---|---|---|---|
| requires microservices | S | **I** ✎ | team description under ABOUT THE ROLE: "you'll help scale the infrastructure behind Notion's database block…" (the word comes later in the paragraph) |
| requires distributed systems | S | **C** ✎ | "Curiosity about distributed systems, microservices, and data-layer trade-offs; experience in these areas is helpful" |
| early-career | I | I | no experience level stated |
| US-based | S | S | location field |

### 4. stripe:8231439 · Software Engineer, Metronome Infrastructure · Toronto, Vancouver, Canada-Remote · rank 2

| claim | auto | read | quoted text |
|---|---|---|---|
| requires Java | S | **I** ✎ | "in programming languages like Go, Java, C/C++, etc." |
| requires distributed systems | S | S | "Hands-on experience contributing to or building large-scale distributed systems" |
| early-career | S | S | "2+ years of experience in backend software development" (2 ≤ the FILTER.md cutoff) |
| US-based | C | C | location field (Canada); kept because US is only a preference |

**Count (labeler before the fix below).** There are 16 claims. Auto: 14 S, 1 C, 1 I. Read: 8 S, 2 C, 6 I. **The labeler was too generous on 6 of
16 claims.** It never failed in the strict direction. All 6 errors come from one blind spot: it checks *which
section* a word is in, but not *what the sentence does with the word* ("like X, Y", "X or Y", "is helpful").

## Relevance is not entailment

**stripe:6042172 (posting 1) matches my words but does not support my claim.** The title matches R1 (Backend
Engineer), and "Java" is in the Minimum requirements section, so the filter counts T1 and the labeler says
"requires Java: supported". But the sentence is "programming languages like Go, Java, C/C++ etc.", which is an
*example list*. The posting requires high-quality code in *some* language. It does not say Java is required, or even
used on this team. The posting is relevant to Rohan's search, but it does not entail "this job requires Java".
Stripe posting 4 has the same sentence.

## Abstention rule and a counterexample that exposes its limits

**Rule (FILTER.md §5, my words):** "If no programming language is mentioned, say 'I cannot tell' rather than
assuming based on the job title." In code, if the body contains no language name, any language claim gets
`insufficient` with the answer `"I cannot tell"` (test `Abstention.test_no_language_says_i_cannot_tell`).

**Counterexample 1: the rule abstains when the posting *does* tell.** stripe:6567104 (held-out #12), Full Stack
Engineer, Developer & End User Experience Platform:
> "Strong coding skills in any programming language (you can learn new languages on the job, and our interview
> process is language agnostic)"

No language is named, so the agent says "I cannot tell" whether Java is required. But the posting answers that
question: Java is **not** required, because any language is fine. The right label for "requires Java" is
*contradicted*, not *insufficient*. My rule treats "no language named" as "no information", and here the absence is
the information.

**Counterexample 2: the rule doesn't abstain when it should.** stripe:8128744 (Software Engineer, New Grad; audit
#13, which I marked Y):
> "We work mostly in Java, Ruby, JavaScript, Scala, and Go. We believe new programming languages can be learned if
> the fundamentals and general knowledge are present."

Languages are named, so the rule never abstains, and because the line is in the requirements list the labeler says
"requires Java: supported". The second sentence says the opposite: the languages are not required. A rule keyed on
"is a language word present?" can't see either case. It would need to read what the sentence says about the
language.

## Improvement: the labeler now reads what the sentence does (2026-11-25, after the first submission build)

The "auto" columns above are the labeler **before** this fix. The same blind spot caused both counterexamples, so I
fixed it test-first:

1. **Measured before** (`python3 measure_claims.py`, [log 14](evidence/logs/14-claims-before-fix.txt)): auto agreed
   with my checked labels on **10/16** claims.
2. **Tests written first** (`tests/test_evidence.py`, classes `SentenceMeaning` and `AbstentionCounterexamples`):
   7 of 8 new tests failed ([log 15](evidence/logs/15-labeler-tests-before-fix.txt)).
3. **The fix** is in `jsagent3/evidence.py`, and it changes the labeler only. `sections()` and the years parser are
   untouched, so filter v1.1 still keeps the same 4 postings and every filter number in SCORE-CHANGES.md stands.
   - "like / such as / e.g. / including / one of …" next to a list (`X, Y`, `X or Y`) → **insufficient**: one example
     among alternatives, not required.
   - "helpful / curiosity about" → **preferred**.
   - A prose paragraph inside a requirements-type section (for example ABOUT THE ROLE) → **insufficient**: a
     description, not a listed requirement.
   - **Contradicted** now applies only when the skill is listed *only* as preferred, matching FILTER.md §5's
     "only as optional".
   - An open years range such as "2–12+" → **insufficient** for early-career.
   - "any programming language / language agnostic / languages can be learned" → **contradicted**, with the answer
     "not required" instead of "I cannot tell". This closes both abstention counterexamples. stripe:6567104 and
     stripe:8128744 now both give `contradicted / not required`.
4. **Measured after** ([log 17](evidence/logs/17-claims-after-fix.txt)): **16/16**. All 57 tests pass
   ([log 16](evidence/logs/16-tests-after-labeler-fix.txt)).

**What 16/16 does and does not show.** These 16 claims are a **dev set**. The rules were written while looking at
these exact sentences, so 16/16 shows the fix does what I designed it to do. It does not show the labeler is right
on postings it hasn't seen. Two things make it weaker still:

- 10 of the 16 "my label" values are rows where Claude's reading matched the old auto label, and I did not
  re-check those separately (the `source` column in [labels/shortlist-claims-dev.csv](labels/shortlist-claims-dev.csv)).
- Getting 16/16 took three tries. The first version scored 12/16, because a bare "or" ("contributing to *or*
  building") counted as a list, and "familiarity" counted as preferred. The second version scored 14/16. Both
  problems were found by looking at these same 16 claims, which is overfitting risk in plain sight.

**Effect on claims nobody checked by hand** ([log 18](evidence/logs/18-labeler-change-on-v1-shortlist.txt)). On the
25-posting v1 shortlist (112 claims), the fix changed **16** labels: 15 supported → insufficient and 1 supported →
contradicted. 4 of those 25 postings are the dev set. Whether the other changes are right is **not checked**.
Every change went in the strict direction, which fits the bias found above (too generous), but is not proof.

Not re-run after the fix: the tool-server transcripts (01, 02) and the Claude scorer runs. They show the labeler as it
was when they ran.

## Held-out check of the fix (my blind labels, 2026-11-25)

The fix changed 16 labels on the v1 shortlist ([log 18](evidence/logs/18-labeler-change-on-v1-shortlist.txt)). 6 of
them are dev-set claims, which leaves **10 that were never used to design the fix**. I labeled those 10 **blind**,
with both the old and the new labels hidden ([sheet](labels/changed-claims-to-check.md),
[my answers](labels/my-changed-claims-labels-2026-11-25.txt), `python3 make_label_check.py
evidence/old/evidence_before_fix_401cacdb.py`):

| | agreed with my blind labels |
|---|---|
| labeler before the fix | **1/10** |
| labeler after the fix | **9/10** ([log 21](evidence/logs/21-labeler-fix-heldout-check.txt)) |

**The one miss is a new defect the fix introduced.** On stripe:7277110 (claim 1, "requires SQL") I said
*supported*, and the fixed labeler said *insufficient*. That bullet starts with "•" instead of "-", so the new
"prose is not a requirement" rule treated a real requirement as a description. I have **not** fixed it: these 10
claims are the held-out check, and tuning on them would use them up.

**Limits.** All 10 changes went in the same direction (supported → insufficient), so this tests the fix's strictness,
not its whole behaviour. 10 claims is a small sample: 9/10 is consistent with a true agreement rate anywhere from
about 55% to 99.7% (exact binomial, 95%). The claims the fix did **not** change were not re-checked here.

## What I would change next (not done)

- Treat "•" (and other bullet characters) like "-", then re-check on a *new* set of claims, not these 10.
- Re-record transcript 01, so the tool's claims reflect the fixed labeler.
