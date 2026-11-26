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

**Count.** There are 16 claims. Auto: 14 S, 1 C, 1 I. Read: 8 S, 2 C, 6 I. **The labeler was too generous on 6 of
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

## What I would change next (not done)

- Treat "like X, Y, Z", "X or Y", "any of", "is helpful", "curiosity about" and "can be learned" as **not
  required**. Then re-measure the auto-vs-read agreement on these 16 claims, since they are now the labeled set for
  that change.
- Replace the abstention rule with three answers: required / explicitly not required / cannot tell.
