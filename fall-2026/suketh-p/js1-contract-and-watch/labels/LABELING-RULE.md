# Labeling rule

_The student's words, sent in chat on 2026-10-31 before 08:49 EDT, before the labels were sent. Saved verbatim by Claude Code; only this italic line was added._

I am focusing on hands-on engineering roles involving machine learning, AI systems, and data infrastructure. I will label a posting `relevant` only if all four conditions pass:

1. The title contains `engineer` and at least one of these terms: `machine learning`, `ml`, `ai`, `data`, or `inference`.
2. The title contains none of these words: `senior`, `sr`, `staff`, `principal`, `lead`, `manager`, `director`, or `head`.
3. The location field contains at least one of these phrases: `boston`, `new york`, `san francisco`, `seattle`, or `united states`.
4. The description mentions `python` and at least one different skill from the fictional résumé: `sql`, `spark`, `pytorch`, `aws`, or `docker`.

For matching, I will decode HTML entities, remove HTML tags while preserving spaces between text blocks, lowercase the text, and split on characters outside `a-z` and `0-9`. Words must match complete tokens; phrases must match consecutive tokens. Skills mentioned under preferred qualifications count.
If any condition fails, the label is `not_relevant`. An empty location fails the location check. Missing required fields or invalid input cause an error.
This is an initial screen. I will not infer sponsorship, remote eligibility, experience requirements, or qualifications that the posting does not state.
