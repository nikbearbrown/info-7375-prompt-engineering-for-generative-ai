CONSTRUCTED — drafted with Claude; clause decisions by Aravind, 2026-10-14

# PRD — Meeting Recap (decisions + action items)

**Status:** constructed for the Readback case study. This is a fictional feature. It is my prompt running on Claude, and it is not affiliated with any meeting or video-call product.

## Problem
People who miss a meeting, or who attend it and forget, can't tell what was decided and who owes what. Reading or replaying a 30-minute transcript to find out is slow.

## User
A member of a small product team who needs to act on a meeting they missed or half-remember.

## What the feature does
Given a speaker-labelled meeting transcript, it produces a short recap with three sections:
1. **Decisions**: what the team agreed to.
2. **Action items**: who will do what.
3. **Unresolved**: questions or disagreements the team didn't settle.

Every decision and action item cites the transcript timestamp it comes from, so the reader can check it.

## Non-goals
- No live, during-meeting summaries; the input is a finished transcript.
- No speaker identification; speakers are already labelled by role.
- No sending the recap to anyone; the feature only returns text.

## How we'll know it works
The recap is judged against `rubric-v0.md`, clause by clause. Pass rates will be measured on the AMI sample; no target number is set here, because none exists yet.

## Inputs used in the case study
Ten whole scenario meetings from the AMI Meeting Corpus (CC BY 4.0), in `../data/sample/`. Each comes with a human-written abstractive summary for reference.

**Leakage rule:** the recap feature receives the transcript only and never `summary.txt`. Only the judge for rubric clause C1 gets the AMI DECISIONS list.
