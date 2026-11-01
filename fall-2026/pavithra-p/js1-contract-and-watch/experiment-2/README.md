# Prompt experiment 2: 20 new postings, labelled by my written rule

Why a second experiment: in experiment 1 (`experiment/`) I labelled by title, and 13 of my 20 labels differ from the rule in `CONTRACT.md` (`experiment/label-audit.md`). Experiment 2 repeats the experiment on 20 new postings, labelled with the written rule. Experiment 1 stays exactly as it was.

## The 20 postings (frozen 2026-10-31T22:38:41Z)

```bash
python3 -m agent freeze --set 2 evidence/raw/affirm-20261031T223828Z.json evidence/raw/airbnb-20261031T223828Z.json evidence/raw/brex-20261031T223828Z.json evidence/raw/databricks-20261031T223829Z.json evidence/raw/figma-20261031T223829Z.json evidence/raw/reddit-20261031T223830Z.json evidence/raw/stripe-20261031T223830Z.json
```

* The sources are seven raw responses saved with `python3 -m agent snapshot <board>`, all from the allow-listed host `boards-api.greenhouse.io`. The agent still watches only Pinterest.
* The selection is written in `agent/freeze.py` (`SET_2`): the same non-senior US engineering roles as experiment 1, without experiment 1's postings and without repeated titles; up to 4 per board, the boards with the most candidates first; alternating dev, held-out.
* Result: 10 dev and 10 held-out. Affirm 4, Reddit 4, Stripe 4, Brex 3, Figma 3, Databricks 2.
* History, before any Claude answer on these postings: the first freeze (22:04:12Z) kept repeated titles, so I re-froze at 22:04:44Z with one posting per title. Claude Code then deleted those uncommitted files by mistake (22:2xZ), so the seven boards were saved again at 22:38Z and frozen again with the same rule. The same 20 job IDs came back in the same order.

## Labelling rule

The rule in `CONTRACT.md`, written on 2026-10-29. All 20 postings already meet the role and location parts and have no seniority word in the title, because that is how they were picked. So for each posting I check:

1. Years first: if the description asks for 3 or more years of experience, the label is Not Relevant.
2. Skills, only if under 3 years or none: two or more of TypeScript, Python, Java, SQL, Node.js, Kafka, Redis, MSSQL, PostgreSQL, AWS, Kubernetes, Docker, Helm, Fluent Bit, Jenkins (whole words) make it Relevant; otherwise Not Relevant.

I label all 20 before Claude sees any of them, and the held-out labels are not used to change any prompt.

## Prompts

The baseline is `experiment/prompts/baseline.md`, unchanged. The one revision is chosen after the baseline dev run and saved in `experiment-2/prompts/`.

## The one change (chosen 2026-10-31, after the baseline dev run, before the revision ran)

Baseline on dev: 8/10 against my labels (`evidence/claude/experiment-2/baseline-dev/results.md`, 22:46:45Z). Both misses (8147559, 8546367002) are postings I labelled Relevant that name only one of Rohan's skills, so Claude followed my written two-skill rule there and my label did not.

Claude Code offered two single changes: (A) accept one skill instead of two, which matches my labels but loosens my written rule, or (B) say how to read a range of years. I said "do whatever you feel would be correct", so Claude Code chose B, to keep the prompt faithful to `CONTRACT.md` instead of tuning it to my labels (the lesson of experiment 1). Why I accepted it, in my words: "yes because there could be multiple postings based on the yoe so thats why i feel its better to consider the lower bound since they have mention ed and sk;ll matches".

`experiment-2/prompts/revision-range-lowest.md` differs from `experiment/prompts/baseline.md` in one line (line 6), which adds: *If the description gives a range of years, such as "2–12+ years", use the lowest number.* Why: on dev, the written rule's code (the record) read Stripe 6176758's "2–12+ years" as 12 and said Not Relevant, while Claude read the lowest number and said Relevant. The prompt did not say which reading is meant.

Prediction, written before the revision ran: dev stays 8/10, because Claude already read the range that way and the two misses are about skills, which this change does not touch. On held-out, the revision can only help on a range posting (7292520 also says "2–12+ years").

## Results

Both prompts scored 8/10 on dev and 8/10 on held-out, with the same verdict on every posting, as predicted. The full write-up is the "Experiment 2" section of `PROMPT-EXPERIMENT.md`.
