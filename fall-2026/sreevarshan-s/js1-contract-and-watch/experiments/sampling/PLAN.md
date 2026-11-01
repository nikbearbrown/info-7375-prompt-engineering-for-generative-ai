# Sampling plan (2026-10-30)

- **Postings:** 5 development-split postings, chosen by me: 8546367002, 8921476002, 8401114002, 8648494002, 8847738002.
- **Prompts:** `prompts/<posting_id>.txt`, the full baseline prompt for each posting, built with `python3 -m experiments.sampling build` from `evidence/raw/2026-10-30T23-59-22Z.json`, `prompts/baseline.txt` and the judge's own prompt-building code, exactly as the judge would send it.
- **Runs:** 4 fresh conversations per posting (20 in all), run manually in the Claude app in an incognito chat with Sonnet 4.6, because the CLI hit its usage limit. Each conversation gets the prompt file's full text and nothing else.
- **Replies:** saved verbatim in `replies/<posting_id>-<n>.txt` (n = 1 to 4), unedited.
- **Checking:** each reply is checked with the same JSON validator the judge uses:
  `python3 -m experiments.sampling check experiments/sampling/replies/*.txt`
  It prints valid or invalid, plus the verdict for a valid reply.
- **Difference from the judge:** the Claude app is not the CLI subprocess. Tools are not disabled the same way, and there is no retry. A reply the validator rejects counts as invalid.
