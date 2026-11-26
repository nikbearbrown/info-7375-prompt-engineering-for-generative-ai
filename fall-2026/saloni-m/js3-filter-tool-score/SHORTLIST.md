# The source-grounded shortlist (Chapter 7)

**What ran (2026-11-26, 16:33 UTC):** `python3 scripts/shortlist.py --n 12`.

- **Shortlist:** the filter v1.0 keeps, one per distinct title (location variants dropped),
  highest score first, ties broken by the SHA-256 of the uid. All 12 scored 5.
- **Justifications:** one real Claude call per posting through the Claude Code CLI 2.0.20
  (`claude -p`, model `claude-sonnet-5-5`, every built-in tool disallowed, no MCP servers,
  run from an empty temp dir). Prompt: `prompts/justify_v1.md`. The CLI's metadata also lists
  `claude-haiku-4-5-20251001`, which Claude Code uses internally. All 12 replies parsed.
- **Labels:** every claim was labelled by `js3/evidence.py` against the posting's own text,
  using FILTER.md §3. Raw replies, claims, labels and reasons: `out/shortlist/shortlist.json`.
  For Saloni's agree/disagree review: `labels/claims_sheet.csv` (72 rows, **not yet reviewed**).

## 1. Every claim, labelled (checker labels, pending Saloni's review)

**72 claims: 45 supported, 0 contradicted, 27 insufficient.**

| Posting | Answer | supported | contradicted | insufficient |
|---|---|---|---|---|
| Applied AI Engineer, Cyber \| Tokyo (openai) | keep | 5 | 0 | 1 |
| Applied AI Engineer - Tokyo (openai) | **I cannot tell** | 3 | 0 | 3 |
| Applied AI Architect, Cyber Specialist (anthropic) | keep | 4 | 0 | 2 |
| Applied AI Engineer, Large Enterprise (openai) | **I cannot tell** | 3 | 0 | 3 |
| Applied AI Architect, Education (openai) | keep | 4 | 0 | 2 |
| Applied AI Architect, Large Enterprise (openai) | keep | 4 | 0 | 2 |
| Security Data Engineer (anthropic) | **I cannot tell** | 3 | 0 | 3 |
| Partner Applied AI Engineer, Google Cloud (openai) | keep | 4 | 0 | 2 |
| Applied AI Architect, Government (openai) | keep | 4 | 0 | 2 |
| Applied AI Architect, Beneficial Deployment (anthropic) | **I cannot tell** | 3 | 0 | 3 |
| Applied AI Architect (openai) | keep | 5 | 0 | 1 |
| Applied AI Engineer, Enterprise (openai) | **I cannot tell** | 3 | 0 | 3 |

Every claim, quote, label and reason is in `out/shortlist/shortlist.json`.

**Why 27 are insufficient. Most of it is my checker, not Claude.** 21 of the 27 are claims
Claude tagged `kind: "experience"` in the sense of *relevant work experience* ("fits her A/B
framework"). FILTER.md §3 means *years* by that kind, so the checker demanded a number in the
quote and found none. The prompt never defined the kinds, and the checker assumed a definition.
That is a contract mismatch between two parts I wrote. The remaining six are real or
word-matching cases:

- one claim with no quote ("based in Munich"): correctly insufficient, since the location
  field is not in the text Claude quoted from;
- "visa" against "We do sponsor visas!": the whole-word rule does not match a plural. This is
  a limit of the checker;
- "Bangalore" with the quote "We do sponsor visas!": a wrong quote, correctly insufficient;
- "degree" with the quote "equivalent combination of education, training…": correctly
  insufficient;
- two where the quote really lacks the term ("customer" vs "customers": the plural limit again;
  "evaluation" vs "evaluate").

**0 contradicted.** A contradiction needs a specific conflict. Claude wrote its "5+ years" claims
*against* fit, as true statements ("asks for 5+ years … well above her eight months"). True
statements are supported, not contradicted. Section 3 shows why that matters.

## 2. Relevance is not entailment

**Applied AI Architect** (`ashby:openai:28cd6fe2-…`). Filter v1.0 scored it 5: the title
matches `applied ai` (+3) and the text matches `python` and `evaluation` (+2). By the filter's
words it is as relevant as anything on the board. Every quote Claude gave is really in the
posting, and one of them is:

> "You will act as the “CTO of your book of business”"

Claude's claim from that quote: *"This is a go-to-market customer advisory role … rather than"*
hands-on building. That claim is **supported**. The filter's own implicit claim is that this
title names one of her target roles ("AI Engineer"). The posting text does not entail that
claim; it entails the opposite. The words match and the claim the match stands for is false.
Labeling rule 1 excludes "architecture-for-clients". The same holds for the 34 kept
"Applied AI Architect" postings (AUDIT.md §3).

## 3. The abstention rule and a counterexample that breaks it

**The rule (FILTER.md §3):** say "I cannot tell" if the text is under 300 chars, or half or more
of the claims are insufficient, or a contradicted experience/seniority/degree claim is behind
the keep. On this shortlist it fired on 5 of 12 postings, every time through "half or more
insufficient".

**Counterexample 1: it answers when it should not.** *Applied AI Architect, Cyber Specialist*
(`greenhouse:anthropic:5445806008`). Answer: **keep**, with 4 supported claims, 2 insufficient,
0 contradicted. One of the supported claims is:

> "5+ years in security roles, with hands-on depth in at least two of: application …"

with Claude's sentence: "Her only listed experience is an eight-month co-op". The rule checks
only whether claims are *true*, never which way they *point*. A justification full of true
reasons not to apply passes the rule. The filter's R4 also missed this requirement. R4 needs
the word "experience" within 60 characters, and "5+ years in security roles" lacks it.
Candidate C3 (AUDIT.md §4) would catch the years; nothing in the evidence rules catches the
direction.

**Counterexample 2: it abstains for the wrong reason.** *Applied AI Engineer, Enterprise*
(`ashby:openai:01091aed-…`) got "I cannot tell" because 3 of 6 claims were insufficient. All
three were relevant-experience claims with real, verbatim quotes, failed only by the
kind-means-years mismatch above. The abstention fired from a checker artifact, not from missing
evidence.

**What would fix it (not done):** add a `stance` field (`for` / `against`) to each claim and
abstain when a supported `against` claim concerns experience, seniority or degree. Also define
the kinds in the prompt so they match the checker. That is a prompt change *and* a checker
change at once, so SCORE.md would have to measure the two separately.

## 4. Not checked

- Saloni has not yet reviewed the 72 checker labels (`labels/claims_sheet.csv`). Until she
  does, every label above is the checker's, not a hand label.
- Whether the shortlist postings are worth Priya's time. That is the dev audit's job, and the
  shortlist was not drawn to match the audit sample.
- Claude was called once per posting. A second call could give different claims.
