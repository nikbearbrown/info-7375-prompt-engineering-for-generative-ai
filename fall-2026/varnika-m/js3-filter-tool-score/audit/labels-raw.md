# My labels, as I typed them (raw)

Pasted to Claude Code in chat on 2026-11-25 and saved here word for word, typos included. The final labels in
`labels.csv` come from these lines and from any later corrections, which are recorded below each batch.

## Batch 1 (items 1–20), first pass

```text
1  N (needs an active clearance, does not show)
2  N (more than 3+ years of expereicme, shouod be less that or eqial to 3
3  N needs an active clearance, does not show)
4  Y/N not iusre as years of exp is not giuven
5  N (the locatuion is not usa)
6  Y 
7  N (experueinet level does not match , too high
8  Y/N not iusre as years of exp is not giuven
9  Y/N not iusre as years of exp is not giuven
10  N needs an active clearance, does not show)
11 Y/N not iusre as years of exp is not giuven
12  Y/N not iusre as years of exp is not giuven
13  N(not software enegienering role)
14  N(not software enegienering role)
15  N (the job titlke is for engineerng manage)
16  N(the job title is vague , does not specify software engineering)
17 N needs an active clearance, does not show)
18  N(N(not software enegienering role)
19 N needs an active clearance, does not show)
20 N(the job title is vague , does not specify software engineering alos exp is too high)
```

### Batch 1, corrections (2026-11-25)

Claude Code pointed out that items 4, 8, 9, 11 and 12 were "Y/N" (each label must be Y or N; under my rule
"no years given" is not a blocker), and that items 1, 10, 17 and 19 gave "needs an active clearance" although
their postings say "or eligibility / willingness to obtain". I asked Claude Code to do the corrections. It
declined to choose for me, then suggested a label for each of the nine **from my written rules** (JS1 labeling
rule and LABELING-DECISIONS.md), naming the rule and the posting's words. I replied **"confirm all"**.

| # | Label | Suggested reason, confirmed by me |
|---|---|---|
| 1 | Y | new grad infrastructure SWE, Seattle, no years; clearance 'or eligibility and willingness to obtain' -> status unknown |
| 4 | N | must-haves (ChromeOS fleet, Google Admin console, Android device management) not on his résume |
| 8 | N | London, UK only; research role |
| 9 | N | Technical Editor is not engineering |
| 10 | Y | strong coder Python/Java/TypeScript, New York, no years; clearance 'or willingness to obtain' -> status unknown |
| 11 | N | product operations manager: not engineering, manager role |
| 12 | N | developer education lead: not engineering of his kind, lead role |
| 17 | N | must-have 1+ years as mentor or tech lead not shown on his résume |
| 19 | N | internship for students; he has graduated |
