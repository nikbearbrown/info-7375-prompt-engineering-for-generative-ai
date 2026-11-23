# REJECT-AUDIT.md — what the filter leaves out (Chapter 7)

**Filter:** v1.0.0 (FILTER.md), run over the 1,332 postings collected on
2026-11-21 (`logs/filter_run_20261121T132140Z.json`). The raw evidence is
committed in `evidence/`.
**Persona:** Priya Nair (`resume.json`, fictional).
**Hand judgments:** Om Raut, in `logs/reject_audit/*_draft.md`. The BLANK
worksheets were committed unlabeled first (`6af4411`).

The filter's output for this run: 20 relevant, 1,312 rejected, 0
insufficient_data.

## 1. Labeling rule

Quoted exactly. The same text appears at the top of all three draft
worksheets:

> I mark a job relevant if the posting gives me a concrete reason to think Priya would build, integrate, evaluate, deploy, or run an AI/ML system as part of the job, and someone with about a year of experience and her Python, RAG, LLM, PyTorch, LangChain, and vector database background could realistically be in the running. I look at what she'd actually own and the minimum qualifications. A missing preferred skill is fine, but a clear multi-year minimum, a staff-level scope, or a management requirement rules it out. Using AI to get other work done, selling or supporting an AI product, or mentioning AI in the company blurb doesn't count by itself. I also check for must-have experience outside her stack. If the work and level fit but the profile I have doesn't tell me whether she meets a graduation-date or clearance requirement, I flag that as an open eligibility check.

Note that this rule judges two things: topical fit ("build ... an AI/ML
system") and level and eligibility fit ("about a year of experience", "a
clear multi-year minimum ... rules it out"). The filter judges only the
first. Section 5 follows from that difference.

## 2. Method

All draws use seed `20261121`, are made by `js3/reject_audit.py`, and are
recorded in `logs/reject_audit/draw_manifest.json`. Each pool was sorted by
(board, id) before drawing, so every draw can be reproduced from the
committed evidence.

- **A: 30 random rejected.** `random.Random(20261121).sample(pool, 30)`
  over all 1,312 postings in the rejected bucket. It is a simple random
  sample over the three boards pooled, not stratified, and it drew gitlab
  7, stripe 16, palantir 7. insufficient_data postings are excluded from
  the pool by construction, but there were none in this run.
- **B: near-threshold rejects, 2 forced + 38 seeded-random.** Because the
  filter is pass/fail on discrete rules, the "closest calls" are defined
  as rejected postings that either matched exactly 1 of the 6 skill words,
  or passed rule 1 and were excluded only by rule 2. That population is
  156 postings (154 + 2).
  - The 2 rule-2-only postings (both "Solutions Architect, Metronome (AI
    Native)") are forced includes and were not sampled.
  - The other 38 are `random.Random(20261121).sample(pool, 38)` over the
    154 exactly-1-word postings.
  - B was cut down from the full population **for time**, before any
    judging (FRICTIONAL.md entry 4; commits `340dfa9` and `dc47bf1`).
- **C: all 20 relevant.** No sampling. Every posting the filter kept was
  judged, so C's result is exact for this run.
- **Overlap.** A09 = B034 and A22 = B029. Each was judged once, in A, and
  that label counts in both groups.

## 3. Results

| Group | What was judged | Filter said | Om agreed | Om disagreed | Disagreements provisional | Kind of number |
|---|---|---|---|---|---|---|
| A | 30 random of 1,312 rejected | rejected | 30 | **0 / 30** | — | sample estimate |
| B (forced) | 2 of 2 rule-2-only rejects | rejected | 2 | **0 / 2** | — | all of them (exact for this run) |
| B (sampled) | 38 of 154 exactly-1-word rejects | rejected | 36 | **2 / 38** | 2 of 2 | sample of a sample |
| C | all 20 relevant | relevant | 1 | **19 / 20** | — | **exact for this run** |

**The two B disagreements are both provisional.** Om labeled both
relevant for the work and the level. Each posting also has an eligibility
requirement that Priya's profile (`resume.json`) doesn't answer:

- **B021**, *Forward Deployed Software Engineer, New Grad - Commercial*
  (palantir). The posting says: "Must be graduating in December 2026 or
  Spring 2027." `resume.json` has no graduation date.
- **B032**, *Forward Deployed Software Engineer, Internship - UK
  Government* (palantir). The posting says: "Security clearance or the
  ability to obtain a clearance." and "Graduating in 2028." `resume.json`
  has neither a graduation date nor a clearance status.

**Both B disagreements come from FRICTIONAL.md entry 1, not from rule 1's
logic.** Both postings are among the 26 Palantir postings whose bucket
would change if Lever's `lists` field were counted as content. The filter
read only `descriptionPlain`, as FILTER.md specifies. There it found
`LLM` (1 of 6). Python appears only in the `lists` section ("...
programming languages, such as Python, Java, C++, TypeScript/JavaScript,
or similar."), which the filter never saw. Om's note on the B worksheet
says the same: "the Python qualification was in a separate section it
didn't read."

## 4. The false friend: B003

**B003**, *Solutions Architect, Enterprise (French Speaking)* (stripe),
matched exactly one skill word, Python, in this sentence from its
requirements (quoted exactly, including the posting's curly apostrophe):

> "A background in writing code in any of Stripe’s primary deployment languages (Ruby, Python, JavaScript, Java, Go, etc.) is a plus."

The match is real, and it is the right word for the wrong reason:

- **What Python means here.** It is one of five languages a customer's
  Stripe integration might be written in. It describes implementing
  payments, not building AI systems.
- **What the role is.** An Enterprise Solutions Architect role, which is
  presales. Om's label: "Python is listed as a language for Stripe
  deployments, while the job owns enterprise payments strategy and
  presales and asks for 10+ years of customer-facing engineering." The
  posting's minimum is "10+ years of experience in a similar
  customer-facing engineering role".
- **Why it matters.** The filter rejected B003 correctly, twice over:
  only 1 of 6 words, and rule 2 fired on "Solutions Architect" with no
  AI-building phrase. But the one word it did match was evidence of
  nothing. Rule 1 counts words, not what they're doing in the sentence. If
  a second incidental word appeared, say "LLM" in the company blurb, a
  presales role like this would pass rule 1 on two words that say nothing
  about the job. Rule 2 is what would catch it.

The same pattern shows up elsewhere:

- **B011.** Om notes that "LLMs are tools the engineer might use to
  automate infrastructure work".
- **Inside the relevant bucket.** In C15/C16 and C19/C20, the LLM match
  comes from using coding assistants, not from building with LLMs (Om's
  notes on C).

## 5. The Group-C finding: 19 of 20 kept postings are not relevant for Priya

**This does not mean the filter is broken.** The filter correctly
identifies topical relevance (rules 1 and 2). Of the 20 postings it kept,
most really are AI-building work: agent flows, RAG copilots, retrieval and
evaluation platforms, LLM-powered data access. Om's own reasons concede
this repeatedly ("fits the AI work", "is real AI work", "The job builds a
grounded answer platform and owns retrieval and evaluation").

What the filter lacks is any rule that checks experience level,
seniority, or eligibility requirements: years of experience, staff or
management scope, degree or graduation dates, clearance. That is a
different axis, and **FILTER.md v1.0.0 never attempted to measure it.**
Its three rules are about topic (skill words), role type (sales/GTM
titles), and missing data. Om's labeling rule, by contrast, explicitly
includes level ("about a year of experience"; "a clear multi-year minimum,
a staff-level scope, or a management requirement rules it out"). The 19
disagreements measure that gap between the two definitions of "relevant".
They don't measure topic-matching mistakes.

Four of Om's Group-C "not relevant" reasons that cite experience or
seniority, quoted exactly:

> **C13** (*AI Engineer*, stripe): "It builds and deploys AI agents and LLM tools, but the minimum is four years as an engineer shipping production systems."

> **C14** (*Software Engineer, Security Business Enablement*, stripe): "The job builds a grounded answer platform and owns retrieval and evaluation, but it asks for 2+ years building production software."

> **C07** (*Technical Solutions Engineer*, stripe): "Maintaining a RAG Copilot is part of the support tooling work, but this role requires at least four years of full-stack development."

> **C05** (*Director, Analytics Engineering*, gitlab): "The director really does build LLM-powered data access and a model-selection harness, but the role requires 12+ years in data or BI and experience managing managers or senior leads."

Each requirement cited above appears in the posting's own text: C13 "4+
years of experience as an engineer shipping production systems"; C14 "2+
years of software engineering experience building production systems";
C07 "At least 4 years of full-stack software development experience"; C05
"12+ years in analytics engineering, data engineering, or BI".

The one posting Om kept, **C03** (*Backend Engineer (Python), AI
Engineering: Agent Foundations*, gitlab), was kept because it "asks for
relevant backend experience without setting a years minimum".

Not every C disagreement is purely about level. C06 turns on "hands-on
security research ... experience", outside Priya's stack, and C18 is
penetration testing, with LLM tools only supporting the work. But these
also fall under the labeling rule's "must-have experience outside her
stack" clause, which no FILTER.md rule checks either.

## 6. What a sample this size can and cannot show

**A (0/30) is a sample estimate, not proof of zero misses.**
- **What it shows.** Finding no disagreements in 30 random rejects is
  consistent with a low miss rate.
- **What it doesn't rule out.** The exact 95% interval for 0/30 runs from
  0% to about 11.6%. Applied to 1,312 rejected postings, a miss count
  anywhere from 0 to roughly 150 is consistent with this sample.
- **What it doesn't tell us.** How misses are spread across boards.

**B (2/38, provisional) is a sample of a sample.**
- **The interval.** The exact 95% interval for 2/38 is about 0.6% to
  17.7%. Over the 154 exactly-1-word postings, that is roughly 1 to 27
  misses.
- **The undrawn postings.** 116 of the 154 were never hand-judged.
- **The 2 disagreements are provisional.** They could become agreements
  once eligibility is known.
- **The rule-2 result rests on only two postings.** B's forced 0/2 is the
  entire rule-2-only population for this run, but two postings are not
  enough to support any claim about rule 2 in general.
- **A and B are not independent.** They share a seed and two postings, so
  their results shouldn't be combined as if they were.

**C (19/20) is exact for this collection run, and only for it.**
- **For this run.** Every relevant posting was judged, so there is no
  sampling error: for the 2026-11-21 collection, 19 of the filter's 20
  kept postings fail Om's labeling rule.
- **It does not carry over to future runs.** Live boards drift: JS2's
  README documents gitlab going from 251 to 254 and stripe from 771 to
  773 within a day, and this run saw gitlab 246, stripe 778 and palantir
  308. A future collection will have a different relevant bucket, and its
  disagreement rate could differ. What C does show about the mechanism is
  more durable than the number: no FILTER.md rule reads experience or
  eligibility requirements.

**What none of A, B or C can show:**
- **How the judgments would change for a different persona.** They are
  judgments for Priya's search. A senior candidate would agree with far
  more of C.
- **Whether a second labeler would agree with Om.** There is one labeler,
  and no inter-rater check was done.

## 7. What happens next

The Group-C finding is **not** being fixed by a quiet edit to FILTER.md.
v1.0.0 stays as written, and so does the Palantir `descriptionPlain`
choice (FRICTIONAL.md entry 1). Instead, "does accounting for experience
level, seniority, or eligibility change which postings are relevant for
Priya?" becomes the subject of the **Chapter 9 "what moves the score"
experiment**. It will be measured on a dev split and confirmed on a
held-out split before any change to the filter or the spec is proposed.
Until that measurement exists, the 19/20 is a documented finding about
this run, not a justification for a new rule.
