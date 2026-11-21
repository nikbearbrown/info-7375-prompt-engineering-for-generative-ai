# Sign-off — NOT SIGNED

**Status: withheld until the owner completes this page.** Claude prepared the checklist; nothing below is checked on the owner's behalf. Tick a box only for something you actually did.

## What I checked, and how

- [ ] I read `CONTRACT.md` and `pre-mortem.md` and agree with them as written. Changes I made: ______
- [ ] I ran `python3 -m unittest discover -s tests -t .` myself and saw ___ tests pass.
- [ ] I ran `python3 -m sponsorsql ask ... --gate interactive` on the real data and made a real approve / refuse / defer decision. Run id: ______
- [ ] I read the development and held-out results in `evals/results/` and compared at least ___ answers with the matching rows shown.
- [ ] I reviewed contract v2 (the controlled-failure recovery) against v1, and I accept / reject it: ______
- [ ] I chose the meaning of Q4 (annual wage) and Q6 (BI titles), or I kept the current definitions on purpose.
- [ ] I recounted at least one answer by hand from the workbook (for example, in Excel). Which one, and what I got: ______

## Not checked

Fill these in honestly. The rubric asks for real "Not checked" entries. Candidates:
- whether answers hold for a newer DOL release
- second worksites that aren't in the main file
- the live `claude -p` path (the CLI wasn't logged in on 2026-11-21)
- every one of the 1,114 employer names in D6

## What I am not claiming

- That SponsorSQL is accurate on arbitrary questions. The evaluation covers 10 development and 5 held-out questions on one file.
- That any LCA count says anything about a specific person's visa or a specific employer's willingness to sponsor.

## Decision

- [ ] Signed — ship / narrow / defer / stop (circle one): ______
- [ ] Withheld — because: ______

Name: ______ · Date: ______
