# Case 09: The tutor effect

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Dean Wu is deciding whether to buy a campus-wide licence for an AI tutoring app. The app was optional this year: students signed up at orientation if they wanted it. The dean wants to know whether the tutor *raises exam scores*, because that is what the licence fee would be for. You gave Claude the data file and a Python environment.

### The instruction (what you sent)
> Analyze `usage.csv` (2,000 students: tutor use, hours studied per week, exam score). Tell me whether the AI tutor improves exam scores so the dean can decide on the licence.

### Agent output
```
ANALYSIS (pandas, scipy)
Group sizes: tutor users n=1200, non-users n=800
Mean exam score: users 81.4, non-users 72.9
Difference: 8.5 points; Welch t-test p < 0.001
Side facts: users average 14.2 study hours/week vs 8.1 for
non-users; 70% of users signed up voluntarily at orientation.

CONCLUSION
The tutor raises exam scores by about 8.5 points (p < 0.001).
The effect is statistically significant and large.
Recommendation: buy the campus-wide licence.
```

### Questions (10 points)
1. **(5 pts)** What is wrong with the conclusion, and what are the exact terms for what the data can and cannot show?
2. **(2 pts)** What single design or check would let the dean claim the tutor raises scores?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain to the dean why 8.5 points does not mean the tutor adds 8.5 points.

---

## TA RUBRIC PAGE (do not hand to students)

### Fixed rubric
| Category | Points | Probe |
|---|---:|---|
| Catches the flaw | 3 | Q1 |
| Exact term | 2 | Q1 |
| Asks for evidence | 2 | Q2 |
| Fix or next step | 2 | Q3 |
| Scope and plain language | 1 | Q4 |

### Case key
**The flaw:** the data show an association; the claim ("raises scores") is about an intervention, and study hours and self-selection are confounders that affect both who uses the tutor and the score; a small p-value does not fix that.

**Full-credit terms (2):** association vs intervention (rungs of the ladder of causation); confounder (study hours / self-selection) named; counterfactual (what would these students have scored without the tutor).
**Half-credit (1):** "correlation is not causation" with no confounder named; "selection bias"; "Simpson's paradox" (only if they explain the reversal on pooling, otherwise near-miss).
**Zero:** "overfitting", "sample size", "p-hacking", "t-test assumptions / normality / non-parametric test / effect size" alone (these tidy the statistics, not the causal claim).

**Acceptable evidence requests (any two count):**
- Randomized pilot: assign tutor access at random and compare scores.
- Compare users and non-users within the same study-hours bands (or adjust for prior GPA and study hours) and report the difference per band.
- Pre-specify the comparison and the outcome before running it.

**Unacceptable:** "collect more data of the same kind"; "get a smaller p-value"; "run the t-test again"; "ask Claude if it is causal".

**Traps:**
- Students who attack the p-value or sample size miss the point; n=2,000 is plenty.
- "Correlation is not causation" alone is the common half-answer; it needs the specific confounders from the output for full catch.
- Students who say "the tutor does nothing" overclaim in the opposite direction; deduct the scope point.

**CAP RULE:** flaw missed (no statement that the comparison cannot support a causal claim, or no mention of the differing study hours/self-selection) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The data show an association, not an intervention effect. Users study 14.2 vs 8.1 hours and most volunteered, so study hours and motivation are confounders: they raise both tutor use and scores. The 8.5 points cannot be read as what the tutor adds. 2. Randomly assign tutor access to half of a cohort, or compare within study-hour bands. 3. "Restate as an association; compare within study-hour bands and report the gap; propose a randomized pilot before any causal claim." 4. "Students who chose the tutor were already studying more, so they might have scored higher anyway. A fair test gives the tutor to some students at random."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete and plain; docked one point because Q4 uses three sentences and "at random" is unexplained.

**Typical (6/10).**
> 1. Correlation does not mean causation; the users studied more. 2. Do a proper experiment. 3. Tell the agent not to say the tutor raises scores. 4. The students who use the tutor may just be better students.

Score: C3 T1 E1 F1 P0 = **6**. Reason: right idea with the study-hours cue (C3); no exact term (T1); "proper experiment" is vague (E1); correction is only a softening of the claim (F1); Q4 is plain but gives no alternative (0).

**Fluent-but-wrong (3/10).**
> 1. The p-value is misleading because of multiple comparisons and the unequal group sizes, so the t-test is biased; the effect may be an artifact of the sample. 2. Run a bootstrap on the difference. 3. "Use a permutation test and report a 99% confidence interval." 4. The result may not be statistically reliable.

Score: C0 T1 E0 F1 P1 = **3**. Reason: attacks the statistics, never the causal claim or the confounders (flaw missed); "multiple comparisons" is a listed term but misapplied; bootstrap repeats the same unconfounded comparison; fix is a valid but irrelevant step; Q4 is plain.
