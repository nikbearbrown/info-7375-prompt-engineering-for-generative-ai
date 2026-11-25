# SHORTLIST.md: the source-grounded shortlist (Chapter 7)

## 1. The shortlists

| File | Filter | Kept | Claims | supported | contradicted | insufficient |
|---|---|---|---|---|---|---|
| `shortlist/shortlist-v1.md` (+ `.json`) | v1 | 55 | 285 | 199 | **29** | 57 |
| `shortlist/shortlist-v1.1.md` (+ `.json`) | v1.1 | 46 | 242 | 188 | 1 | 53 |

Every kept posting has every claim of its justification labeled against **the posting's own fields only**, by the
rules in FILTER.md §2 (`js3/evidence.py`). Every claim carries its quote. Claims: C1 AI/data role (title), C2 one
per persona skill found, C3 US location, C4 early-career fit (years), C5 full-time.

**Checked a second way:** `tools/make_shortlist.py` recomputes every label. Each quoted piece of evidence must occur
verbatim in the posting's title, text, location or employment field. Result: **0 of 285 (v1) and 0 of 242 (v1.1)
quotes not found.** This proves the quotes are real. It does **not** prove the labels are right (see §3).

v1 by claim: C1 55 supported · C2 65 supported · C3 55 supported · **C4 27 contradicted**, 24 insufficient, 4 supported
· C5 20 supported, 33 insufficient, 2 contradicted. Half of v1's shortlist was contradicted by its own text on the
one claim that matters most for Arya. That is why v1.1 added gate G6.

## 2. Relevance is not entailment

**`greenhouse:anthropic 5448481008` "Data Engineer, Product"**, kept by v1 with score 7 (ROLE `Data Engineer` +4,
JOB-TYPE `Engineer` +1, SKILL `Python`, `SQL` +2). Every word the filter looks for is there, so the posting is
*relevant*. But does it support the claim "this fits an early-career candidate"? The text says: "You might be a good
fit if you have: **7+ years of experience** as an Data Engineer or similar role". C4 is **contradicted**. The match
was real, and the claim was false.

Two things make this case useful:
- Claude found it independently, without being asked, in the tool-server session
  (`transcripts/20261124T212725Z-s1-score-three-claude.jsonl`): "the tool kept this posting even though its own C4
  check is contradicted… A `kept` result only means 'passed the written filter,' not 'fits Arya.'"
- It wasn't a one-off: 27 of v1's 55 kept postings had C4 contradicted.

A second kind of case is from my audit, #32 `ashby:openai` "Applied AI Engineer, Codex". The location field says
"London, UK; Remote", which matches the word Remote. The text says "This role is based in our London office" and
"hybrid work model of 3 days in the office per week". The claim "she can work from the US" is contradicted by the text.
I believed the field when labeling blind.

## 3. The abstention rule, and counterexamples that expose its limits

**The rule (FILTER.md §3):** answer `cannot_tell` instead of kept/rejected when A1 the text is under 300 characters,
A2 the location is only "Remote" with no country, or A3 the score is exactly the threshold **and** some claim is
insufficient. A4: with no years stated, C4 says "I cannot tell" (claim level only).

How often it fired: v1: A2 301, A3 8, A1 0 (309 in all). v1.1: A2 14, A3 11 (25 in all).

**Counterexample 1: A2 fired for the wrong reason.** v1 abstained on 301 OpenAI postings like "San Francisco; Remote",
because my code didn't know San Francisco is in the US. The rule did what it says ("no country named"), but the
posting *does* name a US place. The abstention came from the code's ignorance, not from missing evidence in the
posting. In my audit, all 6 sampled abstentions were ones I could decide (5 not, 1 show). Fixed in v1.1 by the US
city list; 14 A2 left.

**Counterexample 2: A3 only looks at the score, so a contradicted claim one point above the threshold sails
through.** "Data Engineer, Product" (§2) scored 7 with C4 *contradicted* and was **kept**. A3 never looked at it,
because it fires only at exactly 6, and only for *insufficient* claims. The rule abstains on weak evidence but not
on contradicted evidence. v1.1's G6 gate now catches this case, but only for years; a posting contradicted on
anything else would still be kept.

**Counterexample 3: A4 reads numbers, not words.** #37 `greenhouse:databricks 8760167002` "AI Engineer – Forward
Deployed Engineering (AI FDE), U.S. Public Sector" says "**Extensive years** of hands-on industry data science
experience". There's no number, so C4 says "I cannot tell". A person reads "extensive years" as clearly not
early-career, and Claude's baseline said Not with that quote. Its twin posting `8546367002` says "It is not intended
for internship, new graduate, or entry-level applicants". There my code also mislabeled **C5** as contradicted,
because the sentence contains "internship". The rule abstains when the evidence is in words it doesn't parse.

**Counterexample 4: the "smallest stated number" rule.** v1.1 keeps `ashby:openai fc5bbc77-…` "Data Engineer" (and its
twin "Data Engineer, Core Experimentation") with C4 **supported**, because the text says "Have **3+ years** of
experience as a data engineer **and 8+**…". The smallest number is 3, but the sentence asks for both. The rule is
written down and followed exactly, and it is still wrong here.

## 4. What I checked, and what I didn't

- Checked by recomputation: every quote is verbatim (0 mismatches, both versions).
- Checked by hand: the claims in the examples above, by reading each posting's text in the label sheet or in chat.
- **Not checked:** I didn't hand-label every claim in the 46-posting v1.1 shortlist. The labels are the rule's output,
  and §3 shows the rule has known holes. No C2 claim is ever "contradicted", because the code never looks for "X is
  not needed".
