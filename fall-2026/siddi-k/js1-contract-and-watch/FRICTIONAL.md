# FRICTIONAL reflection — 31 October 2026

Written by Siddi Kommuri and pasted in chat at about 23:27 ET. Claude saved it verbatim except for five attribution corrections Siddi approved (who saved the snapshot, scanned the boards, fixed wv09, wrote the tests, and which agent judged without reading the posting).

The biggest friction today was that I had a rule for evaluating postings, a persona the rule was supposed to represent, and an experiment that did not consistently connect the three. I made progress on the process, but finishing the workflow did not mean I had validated the result.

## 1. What I tried, and what created friction

I started with the Databricks board, and Claude saved a raw snapshot of it before any code was written. The first base-rate check showed that only 4 of 901 postings fit Jordan, leaving zero of my 20 sampled postings relevant under the rule. That was not a useful board for the experiment, and my contract explicitly required me to change boards. Claude scanned 35 boards, and I chose Stripe after it, Samsara, and Scale AI were the only boards to reach three relevant postings out of 20. Stripe just passed, at 3 of 20. This was a useful constraint: I had to let the data change my plan rather than continue with my initial choice. [Evidence: `evidence/snapshot-morning/`, `evidence/base-rate-databricks/`, `b79c317`, `raw/2026-10-31T10-48-38Z/`]

The rule corrections also created friction before the experiment could run. Splitting on the letters `or` would have broken names such as “New York,” while cutting at “About Databricks” would have removed requirements from 33 postings because that text appeared near the top. I chose to make both fixes. These were not merely coding details: they showed how a plausible text-processing shortcut could silently destroy the information the experiment depended on. [Evidence: `be3b6c8`]

Another friction point was validation. The 36 tests passed initially, but the mutation check revealed that one test, `wv09`, could not catch the wrong version it was meant to detect. Its fixture included “founded 10 years ago” beside “2–4 years,” and the smallest-number rule made the fixture ineffective. Claude fixed the test, and all 37 wrong versions were then caught. This taught me that passing tests are not enough if the tests themselves cannot distinguish correct from incorrect behavior. [Evidence: `7494886`]

Finally, the operational workflow did not line up with the intended experiment. The second live Stripe run found zero new postings on Saturday. The CLI stayed signed out until 22:58, and the sampling and action-surface checks revealed further limitations. I approved a prompt change before seeing results, clicked “labels done” before the labels existed, and the action-surface run showed that an agent given web tools judged a posting without reading its text. These events exposed a gap between believing a step had completed and having evidence that it had. [Evidence: `raw/2026-11-01T02-47-55Z/`, `a6e3aac`, this chat, `SAMPLING.md`, `ACTION-SURFACE.md`]

## 2. What I checked, changed, and learned

The most important result was the disagreement between my labelling rule and Jordan’s persona. My rule accepts roles anywhere in the USA and permits master’s-level roles and internships. Jordan, however, has particular target cities and a bachelor’s degree. In the experiment, all four misses were cases where I labelled a posting relevant and Claude labelled it not relevant. The results were 8/10 for judge_v1, 8/10 for judge_v2, and 8/10 on the held-out set. [Evidence: `PROMPT-EXPERIMENT.md`, `eb80c65`]

I now see this as two different questions that the experiment had treated as one:

* Rule relevance: Does a posting satisfy the written labelling rule?
* Persona fit: Is the posting suitable for Jordan, given Jordan’s actual location, education, and experience constraints?

Those questions can legitimately produce different answers. If the experiment is meant to test whether a judge follows my written rule, then my labels must follow that rule even when I think the role is a poor fit for Jordan. If it is meant to find suitable jobs for Jordan, then the rule must explicitly encode Jordan’s constraints. I should not silently substitute one question for the other.

I would change the contract to state which question is being evaluated, define the relationship between the persona and the rule, and specify how conflicts should be resolved. I would also make the persona and rule consistent before collecting labels, or explicitly preserve their differences if that disagreement is the subject of the experiment. The four misses suggest a systematic mismatch, not just four isolated classification errors. [Evidence: `45fd638`, `PROMPT-EXPERIMENT.md`, `eb80c65`]

I also learned that prompt changes need to be evaluated against a predeclared criterion. I approved judge_v2’s added seniority sentence before seeing results, but both versions scored 8/10. The change did not improve the measured result. I should have defined what improvement would count and kept the comparison separate from my decision to approve the prompt. [Evidence: `a6e3aac`, `PROMPT-EXPERIMENT.md`]

## 3. What remains unresolved

Several things remain unresolved despite the work completed today.

* No new live posting was judged. The second Stripe run returned zero new postings. The experiment therefore did not establish how the judge performs on newly appearing live postings. [Evidence: `raw/2026-11-01T02-47-55Z/`]
* Judge_v2 did not improve the score. Both versions scored 8/10. The added seniority sentence may still have other effects, but these results do not demonstrate a benefit. [Evidence: `PROMPT-EXPERIMENT.md`]
* Held-out performance was only 8/10. That is useful evidence, but it leaves two held-out cases incorrect and does not establish general performance beyond this sample. [Evidence: `PROMPT-EXPERIMENT.md`, `eb80c65`]
* The action surface was not reliable enough. The agent received about 650 of 745 IDs from a summarized fetch, wrote no state file, and judged without reading the posting. I would not treat those judgments as fully grounded in the source postings. [Evidence: `ACTION-SURFACE.md`]
* The tests were not independent of implementation. Claude wrote the tests after the code existed; I did not write tests before seeing the implementation. The mutation check improved confidence that the tests could catch the 37 defined wrong versions, but it does not establish that those versions cover every meaningful failure mode. [Evidence: `7494886`]
* The labelling process needs a clear completion gate. Clicking “labels done” before the labels existed demonstrated that a status action can get ahead of the actual artifacts. I need to verify the label files and their contents before declaring the task complete. [Evidence: this chat]

I would also want to establish whether the four disagreements are fully explained by the rule/persona mismatch or whether any involve additional interpretation differences. The reported pattern is strong evidence of a mismatch, but I should inspect the individual postings and labels before claiming that every disagreement has been completely explained. [Evidence: `PROMPT-EXPERIMENT.md`, `eb80c65`]

## 4. What I accepted, modified, or rejected

I accepted the move away from Databricks and chose Stripe after the base-rate check failed. I also approved the v2 note and delegated the drafting of the vocabulary additions, Claude prompt, and command file, selecting Sonnet 5.5. These were deliberate decisions, although choosing Stripe meant proceeding with a board that only just met the threshold. [Evidence: `b79c317`, `be3b6c8`, `raw/2026-10-31T10-48-38Z/`]

I made the calls on the two text-processing fixes. I accepted that the original handling of “or” and “About Databricks” was unsafe and chose the corrections before committing. I also wrote the five-answer labelling rule and labelled all 20 postings myself. Those were my contributions rather than work I should attribute to the assistant. [Evidence: `be3b6c8`, `45fd638`, `6bd2b52`]

I accepted the drafted prompt, but the results did not show that the v2 change helped. I should distinguish accepting a proposed change from demonstrating that it works. I also accepted the experiment’s setup before resolving the deeper inconsistency between the persona and the rule. That was the more consequential decision I would revisit.

I do not have a well-supported example in this timeline of rejecting an entire proposed approach. My clearest instances of exercising judgment were changing the board and choosing the two text-processing fixes. I would rather acknowledge that than invent a rejection that the evidence does not show.

## 5. What I would do differently next time

I would start by writing down the experiment’s target: rule compliance or persona suitability. I would resolve the relationship between the two before labelling any postings. Then I would write independent tests before implementation, preserve the full source text used for each judgment, and verify that every posting was actually read. I would require the labels and state artifacts to exist before marking the work complete.

I would also separate operational success from experimental success. A command running is not the same as receiving new data; a test suite passing is not the same as having strong tests; and a prompt change being approved is not the same as demonstrating improvement. Finally, I would define the evaluation criteria before viewing results and inspect every disagreement before explaining it away.

My main takeaway is that today produced useful evidence about weaknesses in the workflow, but not a clean demonstration that the judge reliably identifies suitable jobs for Jordan. The next step is not simply to improve the prompt. It is to make the question, persona, labels, source evidence, and evaluation criteria agree with one another—or explicitly test where they differ.
