# Hand-label revisions (2026-10-31)

I labeled all 20 postings in chat. Claude Code recorded my words in `labels.csv`, then checked each reason against the posting text and my LABELING_RULE.md. It did not suggest labels. I then revised six entries before any experiment ran.

Two labels changed (relevant to not_relevant). Both changes came after Claude pointed out a conflict with the résumé or with my rule, so they are not fully independent of Claude.

| id | posting | first label and note | revised label and note | what was flagged |
|---|---|---|---|---|
| 5551730004 | Software Engineer - AI Product | first "somewhat relevant", then relevant: "candidate has some expeirence with AI tools" | **not_relevant**: "no AI experience" | Jack's résumé has no AI experience; rule criterion 1 |
| 5552580004 | Data Scientist | relevant: "candidate has fluency in SQL, python, distributed data systems" | **not_relevant**: "no data science experience" | conflicts with my rule's close-call line on data scientist roles |
| 6233043004 | AI Engineer, Internal Tools | not_relevant: "AI role, not engineering role" | not_relevant: "no AI experience" | the note said "not engineering", but the posting is an engineering role |
| 6201385004 | HRIS Analyst | not_relevant: "cybersecurity role, not data engineering role" | not_relevant: "no Workday experience, not data engineering role" | the note said "cybersecurity", but the posting is Workday HR systems |
| 6143238004 | Software Engineer Intern | not_relevant: "design role, not data engineering role" | not_relevant: "intern role, candidate looking for full time role" | the note said "design role", but the posting is a software engineering internship |
| 5551697004 | Software Engineer - AI Product (London) | not_relevant: "not open to relocation outside USA" | not_relevant: "no agantic coding experience" | my rule ignores location |

## Sampling labels (`sampling_hand_labels.csv`)

One sampling label changed (relevant to not_relevant) after Claude pointed out that Jack's résumé has no CRM/ERP experience. I had also seen Claude's verdict on this posting earlier, in run 2 and the action-surface runs.

| id | posting | first label and note | revised label and note | what was flagged |
|---|---|---|---|---|
| 5551686004 | Software Engineer - Data Infrastructure | not_relevant: "no AI experience" | not_relevant: "no infrastucture engineering experience" | the posting's must-haves don't ask for AI experience |
| 6233040004 | Data & Integration Engineer, Business Systems | relevant: "candidate knows CRM and ERP systems" | **not_relevant**: "no CRM and ERP experience" | Jack's résumé has no CRM/ERP experience |
