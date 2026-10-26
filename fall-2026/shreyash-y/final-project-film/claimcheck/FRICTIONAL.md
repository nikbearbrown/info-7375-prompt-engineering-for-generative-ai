# FRICTIONAL.md — ClaimCheck

A dated log written as the work happens. Two kinds of entries, kept apart on purpose:

- **My notes** are written by me (Shreyash): what I decided and why.
- **Claude's build log** is written by Claude (Claude Code) during the session, on my
  instructions. "I" in those entries means Claude. I read them; I did not write them.

---

## 2026-10-25

### My notes

My TA graded the pitch film's Frictional 3/5 and said the next step is to build the first piece:
one synthetic policy, 10 questions, the citation checker, and a committed, dated eval report. I
decided to build exactly that and nothing more, and to freeze the 10 questions before running
Claude on them, which is what my pitch said I would do. I also decided to keep this log as I go
this time, with my own notes separate from what Claude writes.

I don't have a Claude API key, so ClaimCheck can't call Claude yet. I'm submitting the offline
baseline run as the first dated eval report, labelled as a baseline, and the Claude run is the
next step once I have a key.

### Claude's build log

- **Where it lives.** `fall-2026/shreyash-y/final-project-film/claimcheck/`, on the same
  `shreyash-y/final-project-film` branch as the film, so the GitHub link submitted on Canvas shows it.
  (I first put it in a sibling folder on a separate branch, PR #26; Shreyash pointed out the
  submitted link would not show it, so I moved it here the same day.)
- **No key for a live run.** `ANTHROPIC_API_KEY` is not set in the shell I run in, and the `ant`
  CLI isn't installed, so there was no stored login either. I built the live `claude` answerer
  but did not call it. Everything that can run offline did: the course repo's rules require code
  that runs offline by default and stops cleanly without a key, and a test checks that it does.
- **SDK newer than my reference.** The installed `anthropic` package is 2.3.0; my reference
  material describes 1.x. Before writing the live call I checked the installed signatures:
  `beta.messages.create` accepts `output_config`, `betas` and `fallbacks`. Not yet exercised
  against the real API.
- **Frozen first.** Wrote the synthetic policy and the 10 questions, then froze the question file
  (sha256 in `data/FROZEN.md`) before any run. The eval refuses to start if the file changes.
- **Tests.** 17 offline tests, standard library `unittest`, all passing, also under the plain
  system Python with no `anthropic` installed.
- **First eval run (baseline, 22:24 EDT): 5 correct, 1 missed, 4 wrong.** The baseline is not
  Claude: it copies the best-matching document line as both answer and quote. So every quote
  verified, and the checker passed all 9 answers, yet 4 were wrong. It picked exclusion 5(d)
  instead of Endorsement E-2 for the sewer question, answered both not-in-documents questions
  with the endorsement paragraph, and quoted the windstorm peril instead of the deductible row.
  This is the most useful thing the run showed: **the checker proves an answer is traceable, not
  that it is right.** Grading against frozen gold text caught all four. I added a test that pins
  this down (a real quote from the wrong clause passes the checker but grades WRONG).
- **Next.** Shreyash confirmed he has no API key. Run `--answerer claude` once one is available, commit that dated report and the raw
  replies in `runs/` so the run can be replayed, and compare it with the baseline.
