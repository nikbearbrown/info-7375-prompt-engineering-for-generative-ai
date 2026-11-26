> Inherited unchanged from Job-Search Agent 1 (`experiments/LABELING_RULE.md`, commit `f3bc3e4`) for the JS3 hand labels. The JS3 sheet shows each posting's full text from the saved responses (`out/audit/sheet_blind.json`) through `scripts/label_server.py`, and labels are saved to `labels/hand_labels.csv`.

# Labeling rule for hand labels

Written 2026-10-31, before any posting was hand-labeled.
Drafted by Claude Code at my request. I reviewed it and accepted it unchanged, including both close-call choices, on 2026-10-31, before labeling (see SOURCES.md).

## What a label means

`relevant` means: if I were advising Jack Spencer, I would tell him this posting is worth a day of his time to apply. This is a person's judgment from reading the whole posting. It is **not** the contract's rule. The contract's rule counts keywords. This rule asks what the job actually is.

## How I label

Read the full description on the blind sheet. Do not look at the rule's or Claude's verdicts first. A posting is `relevant` only if **all four** hold:

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
- **Data scientist and ML engineer roles** are `not_relevant` unless the description says the main work is building pipelines or infrastructure. Modeling, experimentation and research are not Jack's target.
- **Backend or distributed-systems software engineer roles** are `relevant` only if the description centers on data systems (storage, streaming, pipelines). Otherwise they are `not_relevant`.
- **Anything still unclear after reading:** pick the label I'd stand behind, and write `close call:` plus the reason in the `note` column. Labels stay binary.

## Record
Every label gets a one-line `note` naming what in the posting decided it.

## Dated entry: 2026-11-25, the JS3 labels use a different definition

**Written after I labeled all 80 JS3 postings** (labels committed in `30eddc9`, 03:04–03:46 UTC) **and after Claude Code flagged** that 44 of my 48 `relevant` labels conflict with the rule above (`labels/label_flags.md`). Claude offered three options: re-read and revise the flagged labels; keep them and report the looser standard; or change the rule to fit them. I chose to change the rule. Claude drafted the wording below from my labels' notes, and I accepted it as is. **My 80 labels are unchanged.** For the JS3 labels, this definition replaces the four criteria above:

> **relevant** means: the technical skills the posting asks for overlap with Jack's skills (Python, SQL, Spark, Airflow, Kafka, dbt, Snowflake, AWS), fully or in part. The job family (data engineering, software engineering, solution or sales engineering, analytics) and the title level (Senior, Staff, Principal, Manager) don't count against it. A posting is **not relevant** if its work isn't technical, if it's an internship or not full-time, or if it requires clearly more experience than Jack's 5 years.

**Labels this definition still contradicts** (Claude's reading of titles, notes and posting text; see `labels/label_noise.md`): about 6 on the "not technical" clause and about 9 on the "clearly more experience" clause. They stay as labeled and are reported as known label noise.
