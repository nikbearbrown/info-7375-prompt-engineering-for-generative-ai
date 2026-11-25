# Labeling rule (written and committed BEFORE labeling any posting)

Date written: 2026-10-30 (ET)
Provenance: drafted with Claude (chat), then edited and adopted by me. The 20 labels are mine.

## The question
Should the persona in examples/persona_resume.json spend a full day applying to this posting?
The persona has about 3 years of ML engineering, works in Python, PyTorch, LLM evaluation, RAG
and Kubernetes, lives in Boston, and is open to New York, Seattle or remote work.

I read the title AND the full description of each posting.

## relevant: all three must hold
1. **Work.** The core of the job is building, training, evaluating or deploying ML or AI models
   or systems, or applied data science. Sales, marketing, partnerships, program management,
   recruiting and support roles do not count, even with "AI" in the title.
2. **Level.** A realistic step for about 3 years of experience.
   - Not relevant: Staff, Principal, Director, Head of, people managers, interns, PhD-required
     roles, and any posting whose stated minimum experience is more than 5 years.
   - "Senior" counts only if the stated minimum is 5 years or less. If no minimum is stated,
     I decide from the description, and if I still can't tell, the unsure rule applies.
3. **Location.** At least one listed location is Boston, New York (any form), Seattle, or
   remote work that allows someone based in the US. Remote limited to another country does not
   count. If the location is "N/A" or missing, I check the description; if it's still unknown,
   the unsure rule applies.

Otherwise: not_relevant.

## When unsure
Label not_relevant and write "unsure" in the note column. A day of effort needs a clear fit,
and the unsure count shows how many of my labels were borderline.

## How this differs from the contract rule (on purpose)
It reads the description, not just the title. It judges level by stated years, not by title
words alone. It excludes AI-flavoured non-engineering roles. And remote work must allow the US.
Where the rule and my labels disagree, that is a result, not a mistake.

## labels.csv
Columns: posting_id, board, title, hand_label, labeled_on, note. hand_label is relevant or
not_relevant. The note names the criterion that decided it: work, level, location, or unsure.

## Which 20 postings, chosen before any Claude call
All 20 come from the run 1 baseline raw response (evidence/runs/20261030T025837Z_stripe).
- **4:** the postings the contract rule marks relevant.
- **8:** chosen by me from titles containing ML, AI, Machine Learning, Data or Scientist,
  picked before reading their descriptions, to include borderline level and location cases.
- **8:** drawn at random from the remaining postings with Python's random.sample, seed 7375.

The 12 ids excluded from the random draw (the 4 plus my 8), the seed and the exact draw code are
recorded in labels/selection.md, committed before I label anything.

Split into 10 development and 10 held-out by labels/make_split.py --seed 7375. split.json is
committed before any prompt is run on either set.

## What touches which set
- The smoke call uses a posting that is not among the 20.
- The 5 sampling-report postings come from the development ids only.
- No Claude call is made on a held-out posting until the final held-out run, which runs once.
