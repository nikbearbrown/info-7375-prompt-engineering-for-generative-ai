# Prompt experiment: postings, split and hand labels

## The 20 postings (frozen 2026-10-30T13:21:08Z)

```bash
python3 -m agent freeze evidence/raw/pinterest-20261030T121808Z.json evidence/raw/figma-20261030T132100Z.json evidence/raw/twilio-20261030T132100Z.json
```

The selection is written in `agent/freeze.py`. It computes no verdicts.

* The sources are the Pinterest baseline run and one saved response each from Figma and Twilio (`python3 -m agent snapshot figma`, `... twilio`, 2026-10-30T13:21:00Z). All three come from the allow-listed host `boards-api.greenhouse.io`.
* The agent still watches one board, Pinterest (`python3 -m agent watch`). `snapshot` only saves a raw response for this experiment: it keeps no state and reports nothing as new.
* A posting qualifies if its title has "Engineer" plus a role word (rule 1), its location has United States, USA or US (rule 4), and its title has no experience word (rule 3). These are the jobs a reader could not settle from the title alone.
* All qualifying Pinterest jobs (6) come first, by job ID, then Twilio and Figma together, by job ID, until there are 20. Walking that list in order, they alternate dev, held-out.
* Result: 10 dev and 10 held-out, with Pinterest 3 + 3, Twilio 3 + 3 and Figma 4 + 4.

`postings.json` lists the 20 with their split and a fingerprint of each description. `postings/<id>.txt` holds each description as plain text, for labelling.

### Change on 2026-10-30, before any label or Claude answer

The first freeze (commit `5b130b8`, 12:21:15Z) used the Pinterest baseline only. Pinterest had just 25 US engineering jobs that day, and only 6 without a seniority word, so 14 of the 20 were Staff, Principal or Intern roles that the title alone settles. That would have left the experiment with 6 real cases. I re-froze at 13:21:08Z with 20 non-senior roles from three boards. No posting had been labelled and Claude had not seen any of them.

## Hand labels

The labelling rule is the rule in `CONTRACT.md`, written on 2026-10-29. I label all 20 by hand in `labels.csv` before Claude sees any of them, and the held-out labels are not used to change any prompt.

For each posting I open `postings/<id>.txt` and check:

1. Role: does the title have "Engineer" and one of Software, Backend, Back-end, Full-stack, Full Stack, Fullstack, Cloud, AI?
2. Skills: which of these appear in the description as whole words? TypeScript, Python, Java, SQL, Node.js, Kafka, Redis, MSSQL, PostgreSQL, AWS, Kubernetes, Docker, Helm, Fluent Bit, Jenkins. Two or more is a Y.
3. Experience: does the title have none of Senior, Sr, Staff, Principal, Lead, Manager, Director, Head, Distinguished, Intern, and does the description ask for no 3+ years?
4. Location: does the location have United States, USA or US?

The label is Relevant only if all four are Y.

### Change to my labelling rule on 2026-10-30, before any Claude answer

While labelling, I decided that only plain Software Engineer roles count for Rohan. Roles that are senior-level or ML-related are Not Relevant, because they are not his background. In my words: "I would consider only the software engineer roles", and then "I would consider all the SE roles". My hand labels follow this, so they can differ from the written rule in `CONTRACT.md`, which the agent's rule judge still uses unchanged. Where they differ is part of the results.

I decided the labels from the title and role type. Skills, years and location were mostly not checked by hand: `labels.csv` says "not checked" for each one I skipped. Result: 11 Relevant and 9 Not Relevant (dev 5 and 5, held-out 6 and 4).

### Label audit on 2026-10-31, after the experiment

A ChatGPT cross-check, then `python3 -m agent audit`, compared my 20 labels with the written rule in `CONTRACT.md`. They agree on 7 of 20 (3 dev, 4 held-out). Of the 13 that differ, 9 are Relevant by my label but fail the rule (all 9 ask for 3 or more years; 5551730004 also has too few skills), and 4 are Not Relevant by my label but pass it (8213988, 8026211, 7838591, 8026207). The note on 7838591 ("senior and ML related") does not describe its title, University Grad Software Engineer 2027. The labels and notes stay as committed in `7327ccd`. Full table: `label-audit.md`; what it means for the experiment: `PROMPT-EXPERIMENT.md`.
