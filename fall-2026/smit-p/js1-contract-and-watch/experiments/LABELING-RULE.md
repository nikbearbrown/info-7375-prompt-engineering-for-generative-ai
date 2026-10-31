# Hand-labeling rule

## Executive summary

This is the rule Smit P. used to hand-label 20 real Airbnb postings as worth (or not
worth) a day of the fictional candidate's time. It was chosen on 2026-10-24, before any
posting was labeled and before any prompt was run. The labels it produced are the answer
key for the sampling report and the prompt experiment. It is a human judgment rule, and it
is deliberately not the same as the agent's rule in CONTRACT.md. The agent's rule never
looks at location or years of experience, and part of the point is to see what that costs.

## The rule

A posting is **RELEVANT** to Aarav Patel (fictional F-1 STEM OPT new-grad backend/platform
engineer in Boston, open to remote) if and only if **all** hold:

1. It is an individual-contributor engineering role, not a manager role.
2. The title is not Senior, Staff, or Principal.
3. The experience it requires is 5 years or less.
4. The location is in the United States or remote-US. OPT work has to be in the US.

Otherwise it is **NOT RELEVANT**.

Chosen by Smit P., 2026-10-24, from options Claude offered in the build session (the
"IC + early-career + US" option).

## Amendment — rule v2 (2026-10-24, during labeling)

While labeling the held-out set, Smit answered with a narrower rule than the one above:
*"Software Engineer or Cloud Engineer or Full Stack Engineer under 3 to 4 years."* That
answer conflicted with v1: it made «Operations Engineer, BizTech» (3+ years, remote-US) not
relevant, where v1 says relevant. Asked to choose, Smit amended the rule rather than
relabel. **All 20 labels follow v2.**

**v2.** RELEVANT if and only if:

1. The title is a Software, Cloud, or Full-Stack engineering role, individual contributor.
2. The title is not Senior, Staff, Principal, or Manager.
3. The experience it requires is at most 4 years.
4. The location is in the United States or remote-US.

The amendment came after the 10 development labels were given. Re-checked under v2, all
10 development labels stay NOT RELEVANT, because v2 is narrower than v1 and cannot create
a positive. No model output had been seen when the rule was amended. **Limitation:**
the rule changed mid-labeling. That is recorded here and in FRICTIONAL.md, not hidden.
