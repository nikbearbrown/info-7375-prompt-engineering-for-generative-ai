# Labeling rubric v1 (fixed before any posting was read for labeling)

Written by Claude Code on 2026-11-25, from `labels/LABELING_RULE.md`
(Rithika's rule, committed in f3bd1b24) and the fictional persona in
`data/resume.example.json` and `data/target.example.json`. It refines the
rule; it does not replace it. Where they differ, LABELING_RULE.md wins.

The SHA-256 of this file is recorded in every suggestion file, and
`python3 -m js3.batch_label check` fails if this file changes afterwards.
A change to the criteria needs a new rubric version and a fresh labeling
pass, not an edit to this file.

## Question

Is this posting worth Priya Nair's time to look at?

Persona, as far as the data files say: MS Information Systems (completed
2025-12), one AI Engineer co-op (LLM evaluation, inference pipeline with
MLflow tracing, a Databricks Genie/LangGraph agent), skills Python, SQL,
Databricks, MLflow, LangGraph, AWS. Target title keywords: ai engineer,
ml engineer, machine learning, data engineer, ml infrastructure, ml platform.
Excluded: anything requiring a security clearance.

## Evidence allowed

Only the labeling sheet row: board, title, location, url (as text, not
opened) and the first 800 characters of body text. No other file, no web
page, no filter output, no audit key, no general knowledge about the
company's other roles. If the 800 characters stop before the role is
described, that is a limit of the evidence, not a reason to guess.

## Verdicts

**relevant**, only if both hold:
1. *Individual-contributor technical builder.* The title and text describe
   someone who builds software or models (engineer, developer, research
   engineer, or a scientist whose shown text describes building or training
   models). Not a people manager (manager, director, head of, VP, or text
   saying the person leads/manages a team). Senior and Staff still count.
2. *ML/AI or data-platform work is the main work.* The shown text or the
   title says the main work is building, training, fine-tuning, evaluating,
   deploying or serving ML/AI/LLM models, or building the ML or data
   platforms, pipelines or infrastructure that such models run on.

**not**, if the shown evidence places it in any of these:
- sales, account management, solutions architecture, solutions/customer
  engineering, forward-deployed or other customer-facing roles (as
  LABELING_RULE.md says; flagged as borderline when the text also describes
  substantial hands-on ML building);
- recruiting, HR, people, finance, legal, policy, communications,
  marketing, operations, program/project management (including TPM),
  support, facilities, design;
- people management (see 1 above);
- software or infrastructure engineering whose shown main work is not ML
  or data platforms (frontend, mobile, product web, security, IT, generic
  backend, networking, hardware), unless the text ties it to ML training
  or serving as its main purpose;
- data analysis or BI work that does not build models or pipelines;
- any mention of a security clearance being required.

**unsure**, when:
- the title is compatible with relevant but the 800 characters are company
  boilerplate or stop before the role is described, and the title alone
  does not settle condition 2;
- the text is mixed (e.g. part ML building, part customer-facing) with no
  clear main work;
- the text is in a language or form I cannot read with confidence.

`unsure` is used instead of forcing a call. It is not a polite "not".

## Not criteria (deliberately ignored)

Location, remote/on-site, years of experience, degree requirements, visa
or sponsorship, salary, team size, company. None is in LABELING_RULE.md;
the sheet text often does not show them; using them would mean inventing
a preference for Priya. They may be mentioned under "uncertainty".

## Confidence

- **high**: title and shown text agree and clearly fit one verdict.
- **medium**: one of them is clear and the other is neutral, or one
  rubric clause needed judgment.
- **low**: a judgment call that a reasonable reader could make the other
  way.

## Borderline (listed for Rithika's review)

Every `unsure`, every `low`, and every `medium` that touches a flagged
clause: research scientist vs engineer, customer-facing role with ML
building, infrastructure whose link to ML is partial, data science vs
data engineering.

## Output per posting

id, board, title, verdict, confidence, CSV reason (one short phrase, no
commas, as LABELING_RULE.md requires), a specific justification, at least
one evidence quote copied verbatim from that posting's sheet text, and the
uncertainty that affected the decision ("none" if none).
