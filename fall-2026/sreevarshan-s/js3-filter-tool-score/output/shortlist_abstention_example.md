# Abstention example and counterexample (reviewed and accepted by Sreevarshan Sathiyamurthy, 2026-11-24)

**Status:** Claude prepared this using `output/shortlist_packet.json` and the JS2 raw postings. I reviewed and accepted it on 2026-11-24. Numbers in parentheses are row numbers in `output/shortlist_packet.md`.

## The case: filter words match, but the key claim isn't established

**Databricks 8692962002 (row 5): "Specialist Solutions Architect - Data Engineering & Warehousing (Financial Services)"**

- **Why it passed:** the title contains "data engineer" (as part of "Data Engineering"), a FILTER.md role word, and no hard-reject word, so it passed as `title_match`.
- **What the posting establishes:** a US location (`location.name: "United States"`) and the Field Engineering posting category.
- **What it doesn't establish:** whether this is hands-on data engineering at all. The title names the topic, but the job function is "Solutions Architect". The description wasn't saved, so the posting gives no responsibilities to settle it. Level, years, Python, degree, sponsorship, and clearance are also missing.

**Proposed abstention:**

> It passed because "data engineering" is in the title, but the job is a solutions architect role and no description was saved, so I cannot tell whether it is hands-on engineering work or whether it suits Priya.

The packet labels `role_type` for this posting as **insufficient**, and every requirement claim (years, Python, sponsorship, clearance, degree) as **insufficient**. Nothing is filled in from what Databricks solutions architects usually do.

## Counterexample: where this abstention rule breaks

**Spotify c73be71c-1a63-4906-9925-95f2115d1f1d (row 42): "Senior Software Engineer - Enterprise AI"** (New York, US)

- **What the rule does:** the `role_type` rule reads the title only. "Senior Software Engineer - Enterprise AI" has no FILTER.md role word ("software engineer" isn't one on its own), so the packet proposes **insufficient** and the rule abstains.
- **But the posting's own text settles it:** this is a Lever posting with a full description. Its "What You'll Do" list says the job is to build platform capabilities that "connect AI models, agents, tools" with Spotify's internal systems, including an MCP gateway. That is hands-on AI platform engineering, close to Priya's primary target (LLM-platform roles).
- **What this exposes:** the rule abstains because of where it looks, not because the evidence is missing. An abstention should mean "the posting doesn't say", not "the field my rule reads doesn't say". A fairer rule would also read the description when one exists, and would label `role_type` **supported** here with the quoted span.

The same row exposes a second limit in the other direction: its `asks_python` label is **supported**, but the span reads "backend languages such as Python, Go, or similar". The posting accepts Python; it doesn't require it. The packet flags this in the note, but the three-way label can't express "accepted, not required".

## A second limitation: a full description doesn't end abstention

The Greenhouse abstention blames the missing description, but a description doesn't guarantee an answer:

- **Sponsorship:** all 14 Spotify postings have full descriptions, and every one is still **insufficient** on sponsorship and clearance, because none of them mentions visas, sponsorship, or clearance. For Priya, who needs sponsorship, that's the most important claim, and fetching Greenhouse descriptions might not answer it either.
- **Title evidence:** the reverse also holds. Stripe 8148653 (row 31), "Staff Machine Learning Engineer, Financial Connections", has no description, yet the title's own word "Staff" contradicts an early-career level. Abstaining on everything because the description is missing would hide that clear no.

**Takeaway for review:** abstention has to be decided one claim at a time, from the fields that actually carry the evidence. It can't be decided once per posting based on whether a description was saved.
