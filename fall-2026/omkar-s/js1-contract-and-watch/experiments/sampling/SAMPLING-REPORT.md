# Sampling report (Chapter 1)

**What ran.** On 2026-10-26, 01:35–01:37 UTC, Claude Code ran this: the agent's prompt contract (`prompts/baseline.txt`), 4 times on each of 5 postings, every call a fresh `claude -p` conversation (no tools, empty folder, no saved session). The model reported was `claude-sonnet-5-5`. That is 20 calls in all, and all 20 passed the validator. Every call is in `verdicts.jsonl`; the raw envelopes are in `claude-raw/`.

**Why these 5.** Claude Code chose them from the development split to mix outcomes: two the rule marks relevant (senior and principal SWE), one engineering title that fails clause A, one near-field title (a Salesforce GTM systems engineer, the kind Omkar's failure sentence is about), and one clear sales role.

**Hand labels.** Omkar labelled these postings on 2026-10-27, after the sampling run, and **without seeing these verdicts**: the summary was held back until his labels were saved.

| posting | title | Claude verdicts (in order) | modal share | rejected | rule (record) | Omkar hand label | modal = hand? |
|---|---|---|---:|---:|---|---|---|
| 7696724003 | Senior Software Engineer - Growth | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 | 0 | relevant | relevant | no |
| 8011054003 | PIPELINE - L5 Principal Software Engineer  | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 | 0 | relevant | relevant | no |
| 7802701003 | Lead Engineer, Applied AI (Customer Agent) | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 | 0 | not_relevant | relevant | no |
| 7806010003 | Senior GTM Partner Systems Engineer (Salesforce) | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 | 0 | not_relevant | relevant | no |
| 7776017003 | Commercial Account Executive (Portuguese Speaking) | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 | 0 | not_relevant | not_relevant | yes |

## What can and cannot be concluded (draft by Claude Code)

- **Spread: none.** 5 of 5 postings got the same verdict 4 of 4 times. Under this setup, which is the CLI's default sampling settings (temperature is not exposed), Claude's verdict on these postings is **repeatable**.
- **Repeatable is not correct.** The modal verdict matched Omkar's hand label on **1 of 5**. On 4 postings Claude said not_relevant 4 times out of 4, and Omkar labelled them relevant. Repeating a verdict 4 times made it no more right.
- **Who is wrong is not settled by this.** Claude's reasons cite seniority and years; Omkar's own written labeling rule says "about 3 years or fewer", but his labels on these 4 senior or lead postings say relevant. The disagreement is between Omkar's labels and Omkar's rule as much as it is between Claude and Omkar.
- **The written rule (the record) disagreed with Claude on 2 of 5**: the senior and principal SWE postings, which the rule passes because it has no seniority gate.
- **Limits:** 5 postings, 4 samples each, one model, one day. Zero spread in 20 calls does not show the spread is zero on harder or borderline postings. Every posting here was either clearly senior or clearly non-SWE.
