# Labeling rule — chosen by Omkar BEFORE labeling any posting

The assignment says the 20 hand labels follow "a labeling rule you wrote first". The rule can be the same as CONTRACT.md's rule, or a different, human one (for example: "would Aarav actually want to spend a day applying to this?"). If it differs, say how. **The difference between the two is exactly what the prompt experiment will measure.**

**Written 2026-10-26T16:53:25Z, before any posting was labelled.** Omkar picked each line below from options Claude Code offered in chat. Claude typed his picks; the wording of each option is Claude's.

A posting is labelled **relevant** for Aarav if **all four** hold:

1. **Role:** "SWE + close eng." It is a Software Engineer role, **or** a close engineering role that is mostly writing software (for example "Lead Engineer, Applied AI"). Sales, IT, security-compliance and analyst roles don't count.
2. **Level:** "Years in the posting". Read the posting's "X+ years" requirement. It counts only if it asks for **about 3 years or fewer**. Aarav has about 2 years full-time plus a co-op.
3. **Location:** "Any US location", the same as contract v2.
4. **Skills:** "Most must-haves". Aarav meets **most of the posting's required qualifications**, not just two keywords.

**Where this differs from the contract rule** (factual comparison by Claude Code):
- Role is broader (the contract needs "Software Engineer" in the title).
- Level is checked (the contract has no seniority gate).
- Skills means meeting the must-haves (the contract counts 2 keyword hits).

Location is the same. The prompt experiment therefore measures Claude against a stricter, human standard than the rule the agent records.

## How to label (procedure)

1. Write the rule above first. Date it.
2. Open `labels.csv`. For each row, open the `url` (or read the posting in `postings-20.json`). Then:
   - put `relevant` or `not_relevant` in `omkar_label`;
   - write a few words of your own in `omkar_note`, for example "title is SWE II, Boston, mentions Python + Kafka".
3. Label all 20 **before** any Claude run. The runner refuses to start while any label is blank.
4. **Do not** read Claude's held-out verdicts before running `lock` (the lock step freezes both prompts and the labels).

The 20 postings were selected by `select_postings.py` (seed 7375). It takes 12 engineering and 8 other postings and alternates them dev/held-out. Claude Code wrote that selection procedure, so neither Omkar nor Claude picked individual postings.
