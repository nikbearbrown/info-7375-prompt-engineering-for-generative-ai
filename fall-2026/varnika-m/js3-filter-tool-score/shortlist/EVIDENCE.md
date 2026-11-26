# The shortlist's evidence: relevance is not entailment, and the abstention rule's limits

[SHORTLIST.md](SHORTLIST.md) lists all 46 jobs FILTER.md v1.1 keeps, with **every claim** labeled supported, contradicted or insufficient against the posting's own text, and the quote that decides it.

| What is counted | Result |
|---|---|
| Claims | 234 supported, 0 contradicted, 99 insufficient |
| Answers | "I cannot tell" 34, "fits by the evidence rules" 12 |

Job numbers below are as in SHORTLIST.md.

## Relevance is not entailment

**Job 1: Palantir, Backend Software Engineer - Application Development.**
- The filter **keeps** it: score 5. R5, the topic-word rule, found five of his skills: Python, Java, Kafka, Kubernetes and Docker.
- The words are relevant. But three of them do not support the claim "the job asks for this skill":

| Claim | Label | The posting's own words |
|---|---|---|
| It asks for Kafka | **insufficient** | "*Distributed systems technologies such as Kafka, Cassandra, Elasticsearch and Spark*" |
| It asks for Kubernetes | **insufficient** | "*Docker and Kubernetes for containerization and orchestration*" |
| It asks for Docker | **insufficient** | same sentence |

Those are lines from a list of technologies the team uses. They describe the job; they do not ask the candidate for anything. The posting **matches my words** and **does not support my claim**. R5 counted all three as matches, and the evidence rules do not.

## The abstention rule

**The rule (my decision D2):** if claim C1 (the role), C3 (US location) or C4 (3 years or fewer) is **insufficient**, the answer is "**I cannot tell** if this fits; here is what is missing", never "fits". 34 of the 46 jobs get "I cannot tell", almost all because no years are stated anywhere (C4).

### A counterexample that exposes its limits: it says "fits" when it should not

**Jobs 5 and 6: Palantir, DevOps Engineer.**
- Answer: **fits by the evidence rules**. C1, C3 and C4 are all supported, so the rule does not abstain.
- C4 ("asks for 3 years or fewer") is **supported** by the quote "*3+ years of professional software development experience on core infrastructure…*". C2 ("open to an early-career engineer") is supported by the same quote.
- But "3+ years" means **at least 36 months**, and Aarav has **29**. The claim is literally true (3 is not more than 3), yet the quote does not show that he qualifies. It shows the opposite.
- The rule only abstains when evidence is **missing**. When evidence **is present but does not support the conclusion**, it answers with confidence. The same weakness is in my JS1 labeling rule ("3+ years" counts as fine), so my own labels would not catch it either (AUDIT.md, limits).

### A second limit: it abstains where the posting is clear

**Job 41: Palantir, Forward Deployed Infrastructure Engineer, New Grad - US Government.**
- C2 is **supported** by "New Grad" in the title.
- But no years are written anywhere, so C4 is insufficient and the answer is "**I cannot tell**", even though "New Grad" plainly means early career.
- The rule counts *phrases*, not meaning, so it abstains on postings where a person would not hesitate. That costs my time, not correctness.

### A third limit: a choice read as a requirement

Several Palantir jobs support "It asks for Python" with "*Strong coding skills … in programming languages, such as Java, C++, Python, Rust, or similar*". That sentence asks for **one** language from a list. It does not ask for Python, yet the label says supported.
