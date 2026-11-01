# Sampling report (Chapter 1)

**What ran (2026-10-31, 06:32–06:34 UTC):** the baseline prompt contract ([`prompts/baseline.txt`](prompts/baseline.txt))
on 5 dev postings, 4 calls each = 20 calls. Each call was a fresh `claude -p` session (no tools, no history,
empty working directory). Every reply passed the validator. Model reported for every call: `claude-opus-5-5`.
Raw log with every reply and session id: [`experiments/sampling/calls.jsonl`](experiments/sampling/calls.jsonl).

**Why these 5:** all are dev postings (so held-out stayed unseen) and they cover the rule's boundaries: the one
US new-grad SWE posting, a US high-school internship, a US master's ML intern, and two non-US SWE early-career
postings (Singapore, Dublin).

| posting | title | location | 4 verdicts (call order) | agreement | rule (record) | my hand label |
|---|---|---|---|---|---|---|
| 8128744 | Software Engineer, New Grad | SF, Seattle, NY | RELEVANT, RELEVANT, RELEVANT, NOT RELEVANT | **3/4** | RELEVANT | RELEVANT |
| 8241260 | High School Internship, Software Engineering | Seattle, SF | NOT ×4 | 4/4 | NOT RELEVANT | NOT RELEVANT |
| 8333074 | Master's Machine Learning Engineer, Intern | SF, NYC, Seattle | NOT ×4 | 4/4 | NOT RELEVANT | NOT RELEVANT |
| 8160776 | Software Engineer, New Grad | Singapore | NOT ×4 | 4/4 | NOT RELEVANT | NOT RELEVANT |
| 8097801 | Software Engineer, Intern | Dublin | NOT ×4 | 4/4 | NOT RELEVANT | NOT RELEVANT |

**Where the spread came from (from the saved replies).** The split posting says *"We work mostly in Java, Ruby,
JavaScript, Scala, and Go. We believe new programming languages can be learned…"*. Three calls counted Java,
JavaScript and Go as preferred skills; the fourth said they "appear only as Stripe's stack" and called the posting
NOT RELEVANT. All four cited the same three skills — the calls agreed on the *evidence* and disagreed on whether it
meets "requires or prefers". The same sentence split the evidence again in the evidence lists for 8241260
(call 2 cited no skills; calls 1, 3, 4 cited three) without changing that verdict.

**Two more calls on 8128744 outside this table** (prompt-experiment dev runs): baseline said NOT RELEVANT,
revision said RELEVANT. Across all six logged `claude -p` calls on this posting: 4 RELEVANT, 2 NOT RELEVANT. The four
action-surface runs on the same posting (ACTION-SURFACES.md) gave 1 RELEVANT, 3 NOT RELEVANT.

## What I can and cannot conclude

_Written by me, 2026-10-31._

The results showed me that the classification process is not always consistent. The plain-chat and Code tab runs gave different answers for the same posting, and the plain-chat response also had a formatting issue. I also realized that I missed the US-location requirement while labeling postings 14–16. Since I only tested a small sample, I can't say that one approach is more accurate than the other, but the results helped me identify what needs improvement.
