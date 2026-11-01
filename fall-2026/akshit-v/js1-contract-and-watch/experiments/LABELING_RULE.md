# Labeling rule for hand labels

Written 2026-10-31, before any posting was hand-labeled.
Drafted by Claude Code at my request; I reviewed it and confirmed the choices marked **[confirm]** before labeling (see SOURCES.md).

## What a label means

`relevant` means: if I were advising Jack Spencer, I would tell him this posting is worth a day of his time to apply. This is a person's judgment from reading the whole posting. It is **not** the contract's rule. The contract's rule counts keywords. This rule asks what the job actually is.

## How I label

Read the full description in `postings_to_label.md`. Do not look at the rule's or Claude's verdicts first. A posting is `relevant` only if **all four** hold:

1. **The work is data engineering at its core.** The main day-to-day work, as the description states it, is building or running data pipelines, data platforms or infrastructure, data integration, or analytics engineering. The title alone does not decide this.
2. **The level fits 5 years as an individual contributor.** Mid-level or Senior is fine. It is **not** relevant if the role:
   - manages people;
   - is Staff, Principal or Director level;
   - asks for clearly more experience than Jack has (roughly 8+ years required);
   - is an internship, a new-grad program or a PhD program.
3. **It is full-time.**
4. **Jack could plausibly be shortlisted.** He meets most of the stated must-haves. No must-have is a whole area he has never worked in, such as C++ graphics, security research, frontend, or an ML research PhD.

Otherwise the label is `not_relevant`.

## What I ignore
Location, visa sponsorship, salary, and the company itself. This matches the contract.

## Close calls
- **[confirm]** **Data scientist and ML engineer roles** are `not_relevant` unless the description says the main work is building pipelines or infrastructure. Modeling, experimentation and research are not Jack's target.
- **[confirm]** **Backend or distributed-systems software engineer roles** are `relevant` only if the description centers on data systems (storage, streaming, pipelines). Otherwise they are `not_relevant`.
- **Anything still unclear after reading:** pick the label I'd stand behind, and write `close call:` plus the reason in the `note` column. Labels stay binary.

## Record
Every label gets a one-line `note` naming what in the posting decided it.
