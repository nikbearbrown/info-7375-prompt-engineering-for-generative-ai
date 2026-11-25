# The source-grounded shortlist (Chapter 7)

Claude Code drafted this report on 2026-11-25 from the committed records. Every label is the student's. Claude drafted the claims and the challenge; Claude Code wrote the code, the prompts and the questions. The full table, claim by claim: [shortlist/v0.1/EVIDENCE.md](../shortlist/v0.1/EVIDENCE.md).

## What was labelled

- **The shortlist.** It is FILTER.md v0.1's top 8: all Anthropic postings, ranked by score, then board and key ([shortlist.json](../shortlist/v0.1/shortlist.json)).
- **The claims.** There are 64, 8 per posting, written by Claude (`claude-opus-5-5` through the student's Claude Code login, 2026-11-24, 22:56–22:57Z) from [prompts/claims-v1.md](../prompts/claims-v1.md). Each posting got one claim about the work, one about the location, one about new graduates, three qualifications, one about work authorization and one about sponsorship.
- **The quote check.** The code checked only that each quote appears word for word: 49 were found, none was missing, and 15 claims gave no quote because they are abstentions ("I cannot tell …").
- **The student's labels.** They were pasted in chat on 2026-11-25 ([claim-labels-as-pasted.tsv](../shortlist/v0.1/claim-labels-as-pasted.tsv)): "I reviewed all 64 against the eight saved postings. 48 supported, 16 insufficient, 0 contradicted." Each insufficient label carries the student's note on what is missing.

## The challenge, and whether it changed a label

Chapter 7: "Label each row yourself first. Then ask Claude to find the sentence that would change your label, and record whether it did."

For each posting, Claude got the text and every claim with the student's label and note, and was asked for the one sentence that would most change each label ([prompts/flip-v1.md](../prompts/flip-v1.md); 8 calls, 2026-11-25, 13:06–13:08Z; [flip/](../shortlist/v0.1/flip/)). For 59 claims Claude named no sentence. For 5 it named a sentence, found word for word in the posting, that argues for a different label. The student decided each one ([flip-decisions.json](../shortlist/v0.1/flip-decisions.json)). Claude Code worded the questions and options.

| Claim | First label | Claude's sentence | Argued for | The student's decision |
| --- | --- | --- | --- | --- |
| R3-C3, new graduates: "The role does not appear open to new graduates because it asks for 5+ years of experience outside of internships." | insufficient | "Minimum years of experience: Years of experience required will correlate with the internal job level requirements for the position" (the posting names the level as Staff) | supported | **changed to supported** |
| R4-C4, qualification: "A good fit has 4+ years of experience in technical roles such as …" | supported | "Former technical founders are also encouraged to apply." | insufficient | **changed to insufficient** |
| R5-C2 and R7-C2, location | supported | "Currently, we expect all staff to be in one of our offices at least 25% of the time." | insufficient | **changed to insufficient, at all eight ranks** |
| R7-C7: "I cannot tell what this posting says about authorization to work." | insufficient | "But if we make you an offer, we will make every reasonable effort to get you a visa, and we retain an immigration lawyer to help with this." | contradicted | **kept insufficient, at all eight ranks** |

**Result.** The challenge changed 10 labels: R3-C3, R4-C4 and the eight location claims. The final count is 40 supported, 24 insufficient and 0 contradicted.

**What the challenge did not do consistently.** The hybrid sentence and the visa sentence are in all eight postings, word for word. Yet Claude raised the hybrid sentence against only 2 of the 8 location claims, and the visa sentence against 1 of the 8 identical work-authorization abstentions. Claude Code checked and showed this before the student decided. That is why the student's decisions on those two cover all eight ranks. The challenge works as a search aid. It is not a reviewer that treats like cases alike, and spotting the like cases was a person's job.

## Relevance is not entailment: R4-C4

R4 is "Applied AI Engineer, Enterprise".
- **The claim and its quote.** The claim is "A good fit has 4+ years of experience in technical roles such as Forward Deployed Engineer, Product Engineer, Software Engineer, or Technical Product Manager". Its quote, "4+ years of experience in technical roles such as Forward Deployed Engineer, Product Engineer, Software Engineer, or Technical Product Manager", is in the posting word for word. A quote cannot match a claim's words more closely than that.
- **What the claim leaves out.** The posting also says "Former technical founders are also encouraged to apply." That is a second way to meet the criterion.
- **Why the label moved.** FILTER.md's definition of supported is "states the claim for this role and preserves any conditions, exceptions, or alternatives". The student's own evidence rule says: "I'll check the full clause, including any or that changes how a requirement can be met." The claim drops the alternative, so the student moved it to **insufficient**.
- **What this shows.** It is FILTER.md's wrong version 4 in a real posting: an exact quote is not enough. The student's first label missed it, and the challenge found it.

Two more cases from the same table:
- **The eight location claims.** Each quotes the location field exactly ("San Francisco, CA | New York City, NY"). None carries the hybrid condition, so the student labelled all eight insufficient.
- **Every C8.** The quote "We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate." is relevant to Alex's question, whether this role will sponsor. It entails only the company-wide statement. The student: "Each C8 supports the company-wide sponsorship statement as written. Sponsorship for a specific role or candidate remains unresolved."

## The abstention rule, and a counterexample that exposes its limits

**The rule (FILTER.md):** "If the posting is silent about sponsorship, the agent says 'I cannot tell whether this role offers sponsorship.'" The claims prompt also says: "If the text does not settle a kind, write the claim as 'I cannot tell …'". Claude applies the rule, and the code does not detect silence itself.

**Where it held.** 7 of the 8 new-graduate claims and all 8 work-authorization claims are abstentions. The student labelled all of them insufficient: the text leaves the question open, so "I cannot tell" was the right output. Under the challenge, the student kept the work-authorization abstention. The option they chose read: "The sentence describes visa help, not this role's work-authorization requirement, so the abstention stands."

**Counterexample 1: a relevant passage the rule lets through.**
- **Why the rule never fires.** None of the eight postings is silent about sponsorship: every one says "We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate." So the rule never abstains, and Claude wrote eight sponsorship claims, each supported as written.
- **What stays open.** Alex's question, whether this role will sponsor, is still unresolved, in the student's words.
- **The limit.** A rule that abstains only on silence says nothing when the text is relevant but does not entail the answer.

**Counterexample 2: wording a stricter rule would wrongly refuse (CONSTRUCTED).**
- **The stricter rule.** It would decide "silent" by a fixed phrase, as FILTER.md warns: "A fixed phrase check can also miss clear wording such as 'We sponsor H-1B visas for this role.'"
- **Checked with this folder's tokenizer** (`normalize.tokens` and `contains_phrase`, run 2026-11-25):
  - The whole-word phrase "sponsor visas" matches the Anthropic sentence above.
  - It does not match "We sponsor H-1B visas for this role." (tokens: we, sponsor, h, 1b, visas, …).
- **The result.** That posting would look silent, and the rule would answer "I cannot tell" although the sentence answers the question.

**The other side of the boundary: R3-C3.** Here Claude did not abstain. It made a claim from "5+ YOE outside of internships". The student first labelled it insufficient. After the challenge, the student labelled it supported, because the posting ties years to the job level and names the level as Staff. Where "I cannot tell" ends is a reading of the whole posting, not a rule about one sentence.

**What review remains.** A person still has to read each passage for its scope: this role, or the company. For sponsorship, no text check settles the question, and the honest next step is to ask the employer.

## The bar's claim side

The student's bar says the work did not succeed if the reader "misquotes a posting" or "clears even one unmet requirement". The student applied the second part to the claims as well ("Both"). By the student's final labels:
- **No misquotes.** Every one of the 49 quotes is in its posting word for word.
- **No contradicted claims.**
- **No requirement cleared.** No claim says a requirement is met or absent when the posting sets one. The new-graduate claims either abstain or (R3-C3) say the role does not appear open to new graduates.

The claim side therefore holds. The filter side does not: v0.2 keeps P53 ([ONE-CHANGE.md](ONE-CHANGE.md)).

## Cross-check with the filter and the hand labels

- **Five of the eight are also hand-labelled, and none is a Yes.** The student labelled three of them No: R3 (P53), R4 (P69) and R8 (P46). Two are Can’t tell: R1 (P33) and R6 (P64). So the claims say what these postings state; they do not make the postings right for Alex.
- **v0.2 would drop three of the eight.** R2, R4 and R8 state minimums of 4, 4 and 6 years, which Claude's claims also quote.
- **R3 is the held-out posting P53.** Claude's claims read "5+ YOE" as five years, and v0.2's rule does not.
- **The shortlist was not redrafted.** It stays v0.1's, as labelled.

## What this does not show

- **One reader, one sitting.** The labels are the student's alone, and no second reviewer challenged a supported row, as Chapter 7 suggests.
- **One run of each prompt.** The claims and the challenge each ran once, so repeat runs could differ. Claude Code's sampling settings for `claude -p` are unknown to this project ([NUMBERS.md](NUMBERS.md)).
- **One company.** All eight postings are Anthropic's, so the boilerplate repeats. A shortlist from other boards would test the claims differently.
