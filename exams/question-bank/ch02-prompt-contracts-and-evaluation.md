# Chapter 2: Prompt contracts and evaluation

## MA-ch02.1

Before writing any prompt, a team writes down the exact shape of output that a downstream program will accept: required keys, value types and allowed values. Code then checks each response against that description. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The code that checks each response against the description is called a validator.
- [ ] B. The code that checks each response against the description is called the prompt template.
- [ ] C. A contract that fixes keys and types also certifies that the claims in the output are true.
- [ ] D. The written description of the accepted output is called an output contract.
- [ ] E. A prompt is a request made to the model, whereas a contract is a requirement on the output that is checked after the response arrives.

**Key:** A=T B=F C=F D=T E=T

**Why:**

- A: A validator is code that tests one response against fixed rules and accepts or rejects it.
- B: A prompt template is the reusable text sent to the model; the checking code is a validator.
- C: A contract describes structure; the truth of a claim is a separate property needing its own check.
- D: An output contract states in advance what the consuming program requires of a response.
- E: The prompt asks and the contract plus validator verify.

**Source:** Output contract and validator

## MA-ch02.2

A prompt tells a model: "Return a JSON object with the keys name and age." The calling code parses the reply and reads both keys. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A reply that parses as JSON has both required keys.
- [ ] B. The runtime enforces the instruction once the model has read it, so replies conform.
- [ ] C. The instruction is a request, and the model can misread or ignore it.
- [ ] D. Schema-constrained decoding restricts which tokens the model may emit so that the reply conforms to a supplied schema.
- [ ] E. Writing the instruction in capital letters with the word REQUIRED removes the need for a validator.

**Key:** A=F B=F C=T D=T E=F

**Why:**

- A: Parsing means the text is syntactically valid JSON; it says nothing about which keys are present.
- B: A prompt is text that conditions generation; nothing in the runtime forces the reply to follow it.
- C: A prompt instruction is a request to a probabilistic generator, not a guarantee.
- D: Constrained decoding enforces structure at generation time instead of hoping the prompt is obeyed.
- E: Emphatic wording lowers the failure rate but does not remove it, and only a check detects what remains.

**Source:** Request versus enforcement

## MA-ch02.3

A provider offers JSON mode (the output is syntactically valid JSON) and schema-constrained output (the output conforms to a supplied JSON schema). Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. JSON mode guarantees that the reply parses, not that it has the keys the consumer needs.
- [ ] B. Using schema-constrained output replaces quality evaluation on held-out cases.
- [ ] C. Schema-constrained output guarantees that the value in a correctly typed field is true.
- [ ] D. JSON mode and schema-constrained output are two names for the same guarantee.
- [ ] E. A validator remains useful after schema-constrained output because it can apply request-specific checks, such as confirming that a quoted span appears in the supplied text.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Valid syntax means the text parses; any object, list or scalar qualifies.
- B: Structure and quality are different properties, and quality still has to be measured on cases the prompt was not tuned on.
- C: A schema constrains types and structure; a correctly typed field can still hold a false value.
- D: The first guarantees syntax; the second guarantees conformance to a particular schema.
- E: A schema judges one document in isolation and cannot refer to external source text.

**Source:** JSON mode, schema, constrained decoding

## MA-ch02.4

A validator reports why it rejected each response, using categories such as parse error, wrong shape, key mismatch, wrong type and bad value. The contract is a JSON object with the keys title (a nonblank string) and tags (a list of strings). Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A reply that is a JSON list when an object was required is a parse error.
- [ ] B. A reply that is missing its closing brace is a parse error.
- [ ] C. A reply with the integer 7 in the title field is a key mismatch.
- [ ] D. A reply that parses successfully has been shown to contain the required keys.
- [ ] E. A reply whose tags entry is a list holding a value outside an allowed set fails on value, as a bad value.

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: A list parses fine; the problem is the wrong shape for the contract.
- B: A syntax error stops processing at the parser, before any rule about keys or types is reached.
- C: The keys are right; a number where a string is required is a wrong type.
- D: Parsing and key checking are separate stages; a parsed object can lack keys.
- E: A value rule checks membership or content of a correctly typed field.

**Source:** Failure categories: parse, shape, type, value

## MA-ch02.5

A consuming function unpacks the two fields answer and sources and raises an exception on any other field. Validator X is strict: it accepts an object only when its keys are exactly answer and sources. Validator Y is lenient: it requires those keys and ignores extra keys. A model returns answer, sources and an extra key named confidence. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Switching from the lenient to the strict validator changes which responses are accepted, so it changes the contract.
- [ ] B. Validator X rejects this response.
- [ ] C. Rejecting a response because of a plausible-looking extra key shows the validator is badly designed.
- [ ] D. Which validator is better depends on what the consuming program does with the object.
- [ ] E. Validator Y accepts this response, so the consumer receives the extra field and raises an exception.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: A change in the accepted set is a change in the specification and should be recorded as a new version.
- B: A strict validator treats an extra key as a violation of the contract.
- C: For a consumer that crashes on extra fields, rejecting at the boundary is the protective behaviour.
- D: Strict versus lenient is a trade-off settled by the consumer's needs.
- E: A lenient validator is silent about additions, so the surprise reaches the consumer.

**Source:** Strict versus lenient validator

## MA-ch02.6

A grounded question-answering system must answer from supplied documents. The document with identifier doc-A reads: "The warehouse opens at 9:00." A validator checks that the reply is a JSON object with the keys answer and cites, that answer is a nonblank string, and that cites lists only supplied identifiers. The model returns {"answer": "The warehouse opens at 7:00.", "cites": ["doc-A"]}. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The reply is structurally valid and passes the validator.
- [ ] B. The reply is grounded in doc-A because it cites doc-A.
- [ ] C. Listing the allowed identifiers as an enumeration in a JSON schema would reject this reply.
- [ ] D. Citing an identifier that exists shows the cited document supports the claim.
- [ ] E. Detecting the contradiction needs a content check that compares the claim with the text of doc-A.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Every rule the validator implements is satisfied: keys, nonblank string and a supplied identifier.
- B: Grounded means supported by the source text, and here the text says 9:00.
- C: The identifier doc-A is on the allowed list, so an enumeration accepts it.
- D: An identifier is an address; whether the text at that address supports the claim is a separate question.
- E: A content-level comparison of claim against source is the check that catches this defect.

**Source:** Structural validity versus grounding

## MA-ch02.7

An answer makes two claims: (1) the refund window is 30 days, and (2) refunds are paid in cash. It cites one supplied document, which reads: "Refunds can be requested within 30 days of purchase." The document does not mention how refunds are paid. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Because the document is about refunds, its topical relevance counts as support for claim 2.
- [ ] B. One valid citation makes the whole answer supported.
- [ ] C. Claim 2 is unsupported by the cited document.
- [ ] D. Support is judged claim by claim against the cited text.
- [ ] E. An answer with one supported and one unsupported claim is partially supported, which differs from fully supported.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: Relevance to a topic is not support; support means the text entails the claim.
- B: A correct citation for one claim does not stand in for support of the others.
- C: Nothing in the document mentions cash or any payment method.
- D: A multi-claim answer can be supported in part, so each claim is compared separately.
- E: Partial support is a distinct outcome, and collapsing it into pass or fail hides the unsupported claim.

**Source:** Claim-by-claim support

## MA-ch02.8

A grounded system's contract requires a nonblank answer string and a nonempty list of supplied source identifiers. A user asks something the sources do not address. The model replies {"answer": "The sources do not say.", "sources": ["doc-2"]}, where doc-2 is a supplied identifier. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A confident invented answer to a question the sources do not address is a hallucination.
- [ ] B. With an answer field and a sources field and nothing more, the consumer has no distinct signal that tells an abstention from an assertion.
- [ ] C. Declining to answer because the evidence is insufficient is called abstaining.
- [ ] D. Adding the line "be accurate" to the prompt gives the output a refusal state.
- [ ] E. Adding a status field to represent abstention changes the contract, so it is recorded as a new version.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: A hallucination is fluent content that the supplied evidence does not support.
- B: Both are a nonblank string plus identifiers, so they look identical downstream.
- C: Abstention is the system's refusal to assert when the sources do not support an answer.
- D: An instruction adds no output field, so the consumer still cannot see a refusal.
- E: A closed contract rejects a new field until the contract itself is changed and retested.

**Source:** Abstention and contract versions

## MA-ch02.9

Reviewers sort the failures of a grounded assistant into formatting errors and hallucinations. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A confident statement of a policy detail that no supplied document contains is a hallucination.
- [ ] B. Hallucination is the name for a wrong output of whatever kind, including output that fails to parse.
- [ ] C. A fluent, well-organised tone is evidence that the content is grounded.
- [ ] D. A claim that the cited source does not support can be called ungrounded.
- [ ] E. A reply that is missing a required key is a hallucination.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Hallucination is fluent, unsupported content presented as fact.
- B: The term is for unsupported or invented content, not for every defect.
- C: Fluency is a property of the wording, not of whether the content is supported.
- D: Grounded means traceable to supplied evidence, so its absence is ungrounded.
- E: A missing key is a formatting or contract error, not unsupported content.

**Source:** Hallucination versus format error

## MA-ch02.10

Reviewers tend to rate answers that read smoothly and confidently as more trustworthy. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A reviewer who decides what counts as failure after reading the outputs is better protected than one who decides beforehand.
- [ ] B. Fluent text is true more often than awkward text, so fluency can stand in for a content check.
- [ ] C. A green result from an automated structural check removes the need to review content.
- [ ] D. Fluency and factual correctness are separate properties of an output.
- [ ] E. A confident, well-formatted answer deserves more trust than a hesitant one.

**Key:** A=F B=F C=F D=T E=F

**Why:**

- A: A criterion fixed in advance resists being bent by persuasive prose.
- B: Fluency is no substitute for comparing the claim with evidence.
- C: A structural check covers only what it tests; content support needs its own review.
- D: Fluent text can be false, and awkward text can be right.
- E: Confidence of presentation is not evidence of accuracy.

**Source:** Fluency is not correctness

## MA-ch02.11

A team is learning to separate the artefacts used to judge a prompt that makes a model answer questions. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A single passing test case counts as an eval of the prompt.
- [ ] B. A pass rate is a metric: the fraction of cases that meet the acceptance criterion.
- [ ] C. A validator checks one response against fixed rules and returns accept or reject.
- [ ] D. A pass rate is the list of cases a prompt is run on.
- [ ] E. An eval runs a prompt over a set of cases and scores the outputs to estimate quality across inputs.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: One case shows the prompt can succeed once, not how it behaves across inputs.
- B: A metric summarises results; here it is accepted cases divided by cases run.
- C: A validator is a deterministic check on a single response.
- D: The list of cases is the test set; the pass rate is a number computed from the results.
- E: An eval is a measurement over many cases, not one.

**Source:** Validator, eval, test set, metric

## MA-ch02.12

Evaluation methods are grouped as code-graded, model-graded and human-graded. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Checking that a reply parses as JSON with the required keys is code-graded.
- [ ] B. A model grader should be checked against human labels before its scores are trusted.
- [ ] C. Human grading is typically the cheapest and fastest of the three.
- [ ] D. Exact string comparison with a reference is a suitable grader for free-form summaries.
- [ ] E. A model-graded score is ground truth because the grader is a model.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Structure and key presence are deterministic properties a program can test.
- B: Calibrating a grader means measuring its agreement with a standard.
- C: Human review is usually the slowest and most expensive.
- D: Many wordings are equally good summaries, and string equality scores paraphrases as wrong.
- E: A model's verdict is another generation and can be wrong or biased.

**Source:** Code-, model- and human-graded evaluation

## MA-ch02.13

A team uses a language model as a judge to pick the better of two candidate answers. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Swapping the order of the candidates and checking that the verdict stays the same is a control for verbosity bias.
- [ ] B. Rating text from the judge's own model family more favourably is called self-preference.
- [ ] C. A sampled verdict can differ from run to run, so repeated judging may be needed.
- [ ] D. Favouring whichever candidate is shown first is called position bias.
- [ ] E. Favouring longer answers regardless of quality is called verbosity bias.

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: Order swapping tests position bias; verbosity bias needs length-controlled comparisons.
- B: Self-preference is a documented reason to use a judge from a different family or to calibrate.
- C: Sampling makes judgments non-deterministic, and the variation should be measured.
- D: Position bias is a preference tied to order, not content.
- E: Verbosity bias rewards length.

**Source:** LLM-as-judge biases

## MA-ch02.14

To check a model's answer, a team sends the same model the answer and the source and asks: "Is this answer supported by the source?" The model replies "Yes." Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Calibrating a judge means asking it to rate its own confidence.
- [ ] B. A single "yes" shows the judge is reliable.
- [ ] C. The reply is new model output that itself needs evaluation.
- [ ] D. A model reviewing its own answer is as independent as a second reviewer.
- [ ] E. A check built on a different mechanism, such as matching a quoted span against the source, tends to fail differently from the generator.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: Calibrating a judge means measuring its agreement with a standard such as human labels.
- B: One verdict says nothing about how often such verdicts are wrong.
- C: A verdict from a model is another generation, not ground truth.
- D: The same model shares training and blind spots, so its review is not an independent opinion.
- E: Independence comes from a different failure profile.

**Source:** Independent checks

## MA-ch02.15

A team has 100 labelled questions and splits them into a development set and a held-out set. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Relabelling a used held-out set as untouched restores its status.
- [ ] B. Choosing among many prompt variants by their held-out scores leaves the held-out score an unbiased estimate.
- [ ] C. Development cases may be inspected and used to revise the prompt.
- [ ] D. A held-out case whose failure guided a prompt change has become development evidence.
- [ ] E. A held-out set is kept unseen until the revision is frozen.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: Only fresh data restores an untouched check.
- B: Selecting on the held-out score biases it upward, a form of overfitting.
- C: The purpose of a development set is to learn from it.
- D: Status depends on what influenced decisions.
- E: Early viewing turns held-out cases into development data.

**Source:** Development set versus held-out set

## MA-ch02.16

A team adds three input-output examples to a prompt (few-shot prompting). One of the examples duplicates a question in the held-out set. The revised prompt scores 10/10 on the held-out set and the baseline prompt scores 7/10. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Removing the leaked item and rescoring both prompts on the same remaining questions gives a cleaner, smaller comparison.
- [ ] B. Few-shot prompting means including worked input-output examples in the prompt.
- [ ] C. A held-out item whose answer sits in the prompt still measures generalisation.
- [ ] D. Near-paraphrases of held-out questions placed in the prompt can also contaminate the measurement.
- [ ] E. Putting a held-out question with its answer in the prompt is a form of leakage, also called contamination.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: A like-for-like comparison needs the same cases for both prompts.
- B: Few-shot contrasts with zero-shot, which gives no examples.
- C: It tests recall of the prompt, not skill on unseen cases.
- D: Overlap in content leaks answers even when items are not identical.
- E: Leakage lets information from the evaluation set reach the thing being evaluated.

**Source:** Leakage and few-shot prompting

## MA-ch02.17

A team iterates on a prompt for two weeks until its format validator accepts all 30 of its development cases, and then reports that output quality is excellent. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A measure that becomes the target tends to stop measuring the underlying goal, a pattern known as Goodhart's law.
- [ ] B. A format validator accepting the 30 cases shows the cases contain no unsupported claims.
- [ ] C. A perfect score on the cases used for iteration reliably predicts the score on new inputs.
- [ ] D. Tuning until the development cases pass is called overfitting to those cases.
- [ ] E. A deterministic validator makes overfitting to it impossible.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Optimising against one metric finds prompts that satisfy the checker rather than the goal.
- B: A format check says nothing about whether claims are supported.
- C: Cases used for tuning look good by construction.
- D: Overfitting is fitting the particulars of the tuning data at the expense of new inputs.
- E: Repeated tuning can satisfy a deterministic checker without serving the goal.

**Source:** Overfitting and Goodhart's law

## MA-ch02.18

Prompt v1 scored 5/10 on a question set and prompt v2 scored 8/10. Between the runs, the developer added two examples, switched the model version, rewrote the task description and replaced several questions with easier ones. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A controlled comparison changes one identifiable feature and holds the rest fixed.
- [ ] B. Replacing questions with easier ones makes the two scores not like for like.
- [ ] C. Because the score rose, the added examples are shown to be the cause.
- [ ] D. Several simultaneous changes are confounded, so the effect of a single change is not identifiable.
- [ ] E. A baseline is the unchanged prompt run on the same cases that revisions are compared against.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Isolating one change is what lets a difference be attributed to it.
- B: Question difficulty moves scores independently of the prompt.
- C: A rise accompanied by several changes cannot be pinned on one.
- D: A confound is a second explanation that cannot be separated from the first.
- E: Without a baseline there is nothing to compare a change to.

**Source:** Controlled comparison and confounds

## MA-ch02.19

A developer runs a prompt once at temperature 0.8 on ten questions and reports 9/10 correct. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Setting temperature to 0 guarantees identical outputs from a hosted model on each run.
- [ ] B. A single run on a small set is enough to compare two prompts.
- [ ] C. At a nonzero temperature the model samples tokens, so a second run can give different outputs.
- [ ] D. Run-to-run variation from sampling is a form of noise in the score.
- [ ] E. Repeating the run shows how much of a score is noise.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: Greedy decoding reduces variation, but hosted systems do not promise identical outputs.
- B: One run mixes the prompt's effect with sampling noise.
- C: Temperature controls how random the sampling is; above zero, outputs vary.
- D: Noise from sampling can be as large as the effects being compared.
- E: Repeated runs estimate the spread caused by sampling.

**Source:** Temperature and sampling noise

## MA-ch02.20

Prompt A scored 7/10 and prompt B scored 8/10 on the same ten questions, each question being a pass-or-fail trial. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Thirty passes in thirty trials show the failure rate is zero.
- [ ] B. A one-question difference on ten cases establishes that the higher-scoring prompt is better.
- [ ] C. A random sample of reviewed answers gives an exact count of unsupported answers in the whole set.
- [ ] D. Evaluating on more cases narrows the uncertainty of a measured pass rate.
- [ ] E. A validator accepting the unreviewed answers shows they are not contradicted by their sources.

**Key:** A=F B=F C=F D=T E=F

**Why:**

- A: A short run with no failures only bounds the failure rate from above.
- B: A difference smaller than the sampling noise cannot show which prompt is better.
- C: A sample gives an estimate with uncertainty, not an exact count.
- D: Uncertainty in a proportion shrinks as the number of trials grows.
- E: A structural check carries no information about whether a claim is contradicted.

**Source:** Sample size and uncertainty

## MA-ch02.21

A teammate claims that starting a prompt with "You are an expert analyst" makes answers more accurate. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The claim is a hypothesis until the prompt is compared with and without the line on fixed cases.
- [ ] B. The role line supplies new facts that the model can use.
- [ ] C. A persona line changes what a validator checks about the output.
- [ ] D. The opening line is a role prompt, also called a persona line.
- [ ] E. A gain found on one model and one test set carries over to other models and tasks.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: A prompt change is a hypothesis, and a comparison on fixed cases is what can support it.
- B: A role label adds no source passages or facts.
- C: A validator applies fixed rules to the returned object whatever text produced it.
- D: A role prompt assigns the model a role or identity in the prompt text.
- E: Effects found under one set of conditions need not transfer.

**Source:** Role prompt as hypothesis

## MA-ch02.22

A team wants a prompt experiment that another person could audit. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The baseline prompt is overwritten by each revision so that a single current file remains.
- [ ] B. Scoring a hand-cleaned version of a fenced reply, and nothing else, measures something different from what the model produced.
- [ ] C. The raw response is saved before editing or repair.
- [ ] D. The record contains the exact prompts, the source materials, the model identifier and the date.
- [ ] E. Hand-written test strings are labelled separately from responses actually returned by a model.

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: An intact baseline is what each revision is compared against.
- B: The cleaned string reflects a human repair, so its pass says nothing about unrepaired output.
- C: Edits made before saving destroy the observation that was actually made.
- D: Without the inputs and conditions a result cannot be reproduced or interpreted.
- E: The two kinds of data support different claims.

**Source:** Audit trail and provenance

## MA-ch02.23

A team hand-writes 20 responses, some malformed and some contradicting their sources, to exercise a validator. The validator rejects 7. A report then states: "The model fails the format requirement 35% of the time." Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The 35% would stay the same whatever mix of malformed and valid strings the author chose.
- [ ] B. If the strings resemble real outputs, the report may call them observed model outputs.
- [ ] C. The 35% describes the hand-written set, not the behaviour of a model.
- [ ] D. Hand-constructed cases are useful for checking that a validator catches specific defects.
- [ ] E. A defensible report says that the model fails the format requirement 35% of the time.

**Key:** A=F B=F C=T D=T E=F

**Why:**

- A: The author sets the rate by choosing how many malformed items to include.
- B: Resemblance does not change provenance.
- C: No model produced these strings, so no model rate can be read from them.
- D: Constructed cases test the checker, not the model.
- E: The supportable statement is that the validator rejected 7 of 20 constructed responses.

**Source:** Constructed versus observed data

## MA-ch02.24

A team ran the same prompt against a hosted model alias in March and again in June. Acceptance by its validator on the same 40 cases fell from 36 to 31. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Recording the date and exact model identifier lets a later reader interpret a change.
- [ ] B. The drop shows that the prompt got worse.
- [ ] C. A hosted model keeps fixed behaviour, so naming the alias is enough for reproducibility.
- [ ] D. A dated snapshot identifier pins a specific model version.
- [ ] E. A model alias can be re-pointed to a newer snapshot, so the same alias can behave differently later.

**Key:** A=T B=F C=F D=T E=T

**Why:**

- A: Conditions of the run are part of the result.
- B: The model behind the alias may have changed, and sampling noise is also possible.
- C: Hosted models are updated, so an alias alone does not fix the version.
- D: Pinning means naming a version that does not change under you.
- E: An alias is a moving name for whichever version the provider currently assigns.

**Source:** Model alias, pinning and drift

## MA-ch02.25

After testing a revised prompt on 10 development cases, a developer writes up only the 8 cases that improved and omits the 2 that did not. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A documented negative result is informative because it tells others what did not help.
- [ ] B. Disclosing failed cases is what makes reported successes credible.
- [ ] C. An entry that names the specific instruction changed lets a later reader see what could explain a difference.
- [ ] D. A log entry such as "v3, better" is enough for another person to reconstruct the change.
- [ ] E. Reporting the improved cases and leaving out the rest is selective reporting and overstates the result.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: A revision that fails to help is still evidence when the trail is intact.
- B: A reader needs the failures to judge which risks remain.
- C: Specific entries make candidate explanations visible.
- D: A useful entry names the instruction that changed and why.
- E: Omitting failures inflates apparent effectiveness.

**Source:** Change log and negative results

## MA-ch02.26

A report says 90 of 100 cases pass. Of the 10 failures, 8 are cosmetic (a stray space in a field) and 2 tell a customer a wrong refund amount. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Severity-weighted scoring treats a stray space and a wrong refund amount as equally costly.
- [ ] B. The pass rate hides the difference in severity between cosmetic and harmful failures.
- [ ] C. A first-attempt pass rate and a final pass rate after retries answer different questions.
- [ ] D. A response that passes after a retry is thereby shown to be supported by its sources.
- [ ] E. A pass rate does not say which cases were used while the prompt was being revised.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: Severity weighting gives harmful failures more weight than cosmetic ones.
- B: A single rate counts a stray space and a wrong refund amount the same.
- C: The first measures single-try reliability; the second includes recovery by resending.
- D: A structural pass after retry says nothing about support.
- E: Cases used in tuning inflate the rate, so their status matters.

**Source:** What a pass rate leaves out

## MA-ch02.27

A service asks a model for a JSON object with a long free-text field. About 6% of replies fail to parse. Each failing reply ends in the middle of a string, and the API response reports that generation stopped because the maximum output length was reached. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Recording the stop reason lets the pipeline separate truncated replies from complete but malformed ones.
- [ ] B. Rewording the schema description in the prompt is the remedy for these failures.
- [ ] C. A reply that stops at the output limit is a complete reply that contains a syntax mistake.
- [ ] D. These failures show that the model does not understand JSON.
- [ ] E. Raising the maximum output length would have no effect on this failure.

**Key:** A=T B=F C=F D=F E=F

**Why:**

- A: The stop reason says whether generation finished or was cut off.
- B: The cause is length, not wording.
- C: A truncated reply is incomplete, which is a different failure from a complete malformed one.
- D: The same model produces valid JSON on shorter replies; the failure is mechanical.
- E: Giving the answer room addresses the mechanism cutting the reply.

**Source:** Truncation and stop reason

## MA-ch02.28

An agent emits the tool call {"tool": "delete_file", "path": "/data/reports"}, and the call validates against the tool-call schema. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Least privilege means granting broad access and trusting the model to refrain.
- [ ] B. Limits on what the agent may do are enforced by permissions and an allowlist outside the model's output.
- [ ] C. Passing schema validation shows the call is well formed.
- [ ] D. A human approval gate before a destructive action addresses consequences a schema does not judge.
- [ ] E. Passing schema validation establishes that the agent is permitted to delete that path.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: Least privilege grants the narrowest access the task needs.
- B: Enforcement outside the model holds whatever the model emits.
- C: The call has the expected fields and types.
- D: An approval gate pauses execution until a person confirms.
- E: A schema describes shape; permission is a separate policy.

**Source:** Tool calls, permissions and approval gates

## MA-ch02.29

Two plans are proposed for judging whether answers are supported by their sources. Plan 1 fixes the definition of supported, including how to treat insufficient sources, before any output is seen. Plan 2 defines it after seeing which prompt produced the more fluent answers. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A third outcome such as undetermined keeps unverifiable answers from being forced into pass or fail.
- [ ] B. A pre-fixed definition removes disagreement between reviewers.
- [ ] C. A criterion written after tuning the prompt is independent of the outputs.
- [ ] D. Counting undetermined answers as supported when they read fluently is acceptable.
- [ ] E. Fixing the definition before reading outputs limits drift toward a preferred prompt.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: An unknown outcome is more honest than a forced verdict.
- B: It reduces ambiguity, but reviewers can still read a case differently.
- C: Such a criterion describes the outputs, so passing it is close to circular.
- D: Fluency is not evidence; unverified answers are reported as unverified.
- E: A criterion set in advance can fail an output; one fitted afterward cannot.

**Source:** Criteria fixed before outputs

## MA-ch02.30

Two reviewers independently label 20 answers as supported or contradicted against their sources. They agree on 17 of the 20. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Agreement between independent reviewers is called inter-rater agreement.
- [ ] B. High agreement between reviewers shows the labels are correct.
- [ ] C. A chance-corrected statistic such as kappa adjusts agreement for what chance alone would produce.
- [ ] D. Raw agreement can look high by chance when one label is much more common than the other.
- [ ] E. Cases where the reviewers disagree are best left out of the report.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: It measures how consistently two people apply the same labels.
- B: Two reviewers can agree and both be wrong; agreement measures consistency.
- C: Kappa compares observed agreement to expected agreement.
- D: Chance agreement inflates raw percentages for unbalanced labels.
- E: Disagreements show where the criterion is ambiguous and belong in the record.

**Source:** Inter-rater agreement

## MA-ch02.31

A team requires that each rule in its contract has a test that fails if that rule is deleted from the validator. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A mutant that still passes the test suite reveals a rule that no test defends.
- [ ] B. Deleting a rule to see whether a test notices is a form of mutation testing.
- [ ] C. An edge case such as an empty list or a blank answer needs a test of its own.
- [ ] D. One happy-path example exercises the edge cases of the contract.
- [ ] E. A suite that passes shows the validator implements the specification.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: A surviving mutant marks an untested behaviour.
- B: A mutant is a deliberately altered copy of the code used to probe test coverage.
- C: A happy-path example exercises none of the edge cases.
- D: A typical example does not touch the boundaries.
- E: Tests defend only the behaviours they exercise.

**Source:** Mutation testing and edge cases

## MA-ch02.32

A developer asks Claude Code to implement a validator from one line: "the output must have an answer and a list of sources." The line does not say whether extra keys are allowed, whether the list may be empty, or what to do with a whitespace-only answer. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The assistant may silently choose an interpretation for each unspecified case.
- [ ] B. Asking the assistant to propose a plan before it edits files is planning before acting.
- [ ] C. Tests that the assistant wrote itself are independent evidence that its code is correct.
- [ ] D. The acceptance decision belongs to the person who bears the consequences.
- [ ] E. Reading the changes the assistant made before accepting them is diff review.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Generators fill gaps with something plausible instead of flagging them.
- B: A plan lets the person correct a wrong interpretation before code exists.
- C: Tests from the same party share its assumptions.
- D: The consumer and the stakes sit outside what the assistant reads.
- E: A diff shows exactly what was added, removed or altered.

**Source:** Delegating to a coding assistant

## MA-ch02.33

A contract asks the model to include a self-reported confidence number between 0 and 1 with each answer. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A validator can check that the field is present, numeric and within range.
- [ ] B. A validator can check that the stated confidence is calibrated.
- [ ] C. Calibration means that stated confidence matches the observed frequency of being right.
- [ ] D. A confidence number that is correctly formatted is evidence that it is meaningful.
- [ ] E. A model's stated confidence is a measurement of its internal probability of being right.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Those are structural properties of the value.
- B: Calibration depends on how often answers are right, which a validator of one response cannot see.
- C: A calibrated 0.8 is correct about four times in five.
- D: Format says nothing about meaning; that has to be tested against correctness labels.
- E: It is generated text and not a readout of internal state.

**Source:** Self-reported confidence and calibration

## MA-ch02.34

A team is building evaluation cases for a grounded question-answering feature. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A set drawn from the hardest cases estimates typical production behaviour.
- [ ] B. Boundary cases and a random sample of live traffic answer the same question, so their pass rates can be pooled.
- [ ] C. Including questions the supplied documents do not answer tests whether the system abstains instead of inventing.
- [ ] D. A set of easy, clean cases gives a pass rate that predicts real use.
- [ ] E. Dozens of near-duplicate cases carry as much information as the same number of varied cases.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: Typical behaviour needs a sample that resembles typical use.
- B: Boundary cases probe worst-case behaviour while a traffic sample estimates typical behaviour.
- C: Unanswerable questions are how abstention behaviour is observed.
- D: Easy cases overstate reliability.
- E: Near-duplicates repeat the same test.

**Source:** Evaluation case design

## MA-ch02.35

Two teams build checks for model answers shown to customers. One answers movie trivia and the other answers questions about drug interactions. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Both teams should use the same acceptance rule, since the output format is the same.
- [ ] B. The acceptance threshold is a decision for the person who bears the consequences, not for the assistant that drafts the checks.
- [ ] C. Layering cheap programmatic checks for form with judged or human review of content is a standard approach.
- [ ] D. A passing structural check is enough for the higher-stakes team.
- [ ] E. The higher-stakes team should plan more human review of content.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: The acceptance rule follows the cost of being wrong, not the format.
- B: Ownership follows who answers for the outcome.
- C: Cheap checks filter first, and costly review is spent on content.
- D: Structure says nothing about whether the claims are supported.
- E: Cost of error sets how much checking is justified.

**Source:** Stakes and acceptance rules
