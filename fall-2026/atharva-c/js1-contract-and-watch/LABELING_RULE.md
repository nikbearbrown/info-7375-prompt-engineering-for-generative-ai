# Labeling rule — hand labels for the prompt experiment

Written by Atharva C on 2026-10-30, before reading or labeling any of the 20
postings in `labels/`. Recorded from an interview with Claude Code: Claude
wrote the answer options, I chose among them. The choices are mine.

This is my judgment of whether a posting is worth Rohan Desai's time (fictional
new-grad software developer, Boston, 0 years of work experience). It is the
ground truth the written rule and Claude are compared against. It is not the
rule in CONTRACT.md.

## A posting is "relevant" if

1. **Core test:** it is an entry-level software engineering role that a new
   grad could realistically be hired into, using skills he has.
2. **Internships:** university internships count. The high-school internship
   does not.
3. **Seniority:** Senior, Staff, Principal, Lead, and Manager titles are not
   relevant. Required years of experience are ignored.
4. **Location:** it must be in the US or remote in the US.
5. **Unsure:** if I can't decide, the label is "not relevant".

## How I record a label

In `labels/sheet.csv`: `my_label` is `relevant` or `not relevant`, and
`my_reason` names the numbered point above that decided it.

## Clarification added during labeling (2026-10-30)

While labeling, I had answered two postings with mixed US and Canada locations
differently (7557899 relevant, 8212314 not). I settled it as: **a location
must be purely US**; any non-US place fails point 4. I changed 7557899 to
"not relevant (4)". This was decided after I had seen the postings, not before.
