# Jargon test: evaluation, approval gates and governance

## MA-j06.1

A team has a function that adds tax to a price and a prompt that summarizes support tickets. Decide which statements about a test and an eval are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An eval gives the same pass or fail result on each run, as a sampled model is repeatable.
- [ ] B. Test and eval are two names for the same thing.
- [ ] C. An eval scores the quality of model outputs over a set of cases, often reported as a rate, because the outputs vary.
- [ ] D. A test checks a fixed expectation, such as the function returning 10.50 for a given input, and passes or fails the same way each run.
- [ ] E. Running a prompt once and judging the answer by eye gives a sample, not an eval.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: Sampling means results can differ between runs.
- B: They differ in what is checked and how the result is reported.
- C: Evals measure behaviour that is sampled.
- D: Tests are for deterministic behaviour.
- E: An eval needs a set of cases and a scoring method.

**Source:** eval vs test

## MA-j06.2

Vendors publish scores for their models on public benchmarks, and a company is deciding whether to rely on them. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A benchmark and a rubric differ: the benchmark is the shared set of tasks, and the rubric describes how to score an answer.
- [ ] B. An eval built from cases drawn from the company's own task measures fit to that task better than a public benchmark does.
- [ ] C. A high score on a public benchmark shows the model works for the company's own task.
- [ ] D. A benchmark is a shared, fixed set of tasks with a scoring method, used to compare systems.
- [ ] E. A score the maker reports on its own model is a claim by the maker, not an independent measurement.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: One supplies the cases, the other the scoring criteria.
- B: Own cases match own use.
- C: A benchmark measures its own tasks, which may differ from yours.
- D: Sharing the set is what makes comparison possible.
- E: Independent checking is what turns a claim into evidence.

**Source:** benchmark vs eval

## MA-j06.3

A teacher writes a scoring guide for essay answers: criteria such as accuracy and clarity, each with a description of what a high, middle and low score looks like. Decide which statements about a rubric are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A rubric lists criteria and describes what each score level looks like.
- [ ] B. Applying a rubric changes the weights of the model being graded.
- [ ] C. A vague criterion such as "good" leads to inconsistent scores between graders.
- [ ] D. A rubric is an answer key holding the exact text of the correct answer.
- [ ] E. A rubric needs a language model to apply it.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Level descriptions make scores comparable.
- B: Scoring does not train anything.
- C: Concrete level descriptions reduce disagreement.
- D: A rubric describes quality, not one correct text.
- E: People can apply a rubric, and so can a judge model.

**Source:** rubric

## MA-j06.4

A team uses a second model to score the first model's answers against a rubric. Decide which statements about LLM-as-judge are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Judge models can prefer longer or more fluent answers regardless of whether they are correct.
- [ ] B. A judge model's score is a measurement that needs no check against human labels.
- [ ] C. Using the same model to judge its own output gives errors that are independent of the original.
- [ ] D. An LLM judge is a language model that scores another output against stated criteria.
- [ ] E. Comparing a sample of the judge's scores with human labels shows how far the judge can be trusted.

**Key:** A=T B=F C=F D=T E=T

**Why:**

- A: This is a known bias of automated scoring.
- B: Agreement with people has to be checked.
- C: Errors of the same kind of model are correlated.
- D: It automates scoring at scale.
- E: That comparison is the usual calibration step.

**Source:** LLM-as-judge

## MA-j06.5

A team changes a prompt to fix one complaint, and later finds that answers which used to work now fail. Decide which statements about regression are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A regression means the score went up after the change.
- [ ] B. In this setting, a regression is the fitting of a line to a set of data points.
- [ ] C. A regression eval reruns a fixed set of earlier cases after each prompt or model change to see whether anything got worse.
- [ ] D. A regression is a change that breaks something that worked before.
- [ ] E. Deleting an old failing case after it is fixed prevents it from regressing.

**Key:** A=F B=F C=T D=T E=F

**Why:**

- A: It means behaviour got worse.
- B: That is statistical regression, a different use of the word.
- C: It guards earlier behaviour.
- D: The word marks a step backward in behaviour.
- E: Keeping the case in the set is what catches it if it returns.

**Source:** regression

## MA-j06.6

A model states a refund policy that the company does not have, in fluent and well-formatted text. Decide which statements use hallucination and error correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A wrong arithmetic result from a miswritten program is a hallucination.
- [ ] B. In engineering, an error is a failure the system reports, such as an exception or a tool returning a failure.
- [ ] C. Passing a format check shows the output is not a hallucination.
- [ ] D. A hallucination is fluent output that states something false or unsupported as if it were true.
- [ ] E. A hallucination triggers an error message that the system shows.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: A program bug is a defect; hallucination describes model-generated unsupported content.
- B: An error is a signal, unlike a hallucination, which gives no signal.
- C: A format check tests shape, and false text can have a valid shape.
- D: The text reads well and is wrong.
- E: A hallucination looks like a normal answer.

**Source:** hallucination vs error

## MA-j06.7

An assistant answers using passages that a retrieval step supplied. Decide which statements about groundedness are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Retrieval does not make an answer grounded, since the model can ignore or misstate the passages.
- [ ] B. A grounded answer can still be false when the source passage itself is wrong.
- [ ] C. An answer that cites a source is verified as correct.
- [ ] D. A grounded answer has claims that are supported by the supplied source material.
- [ ] E. Groundedness is checked by comparing each claim with the retrieved passages.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Retrieval supplies text; the answer still has to follow it.
- B: Groundedness is about support, not truth in the world.
- C: A cited answer still needs a check against the source.
- D: Grounding ties claims to sources.
- E: The comparison shows what is supported.

**Source:** groundedness

## MA-j06.8

An agent is set up to edit files in a project. Decide which statements about permission and approval gate are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A permission is a standing rule that says whether an agent may use a tool or reach a path, such as allow, deny or ask.
- [ ] B. An approval gate is a rule written once in a settings file and then left alone.
- [ ] C. A permission is a decision made fresh for each run after reading the output.
- [ ] D. A permission rule set to ask removes the need for the person to approve anything.
- [ ] E. An approval gate is a point where a person reviews and decides before the action goes ahead.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Permissions are set ahead of time.
- B: That describes a permission rule.
- C: That is a gate, not a standing rule.
- D: An ask rule creates a gate, so a person is asked.
- E: A gate stops the flow until a person decides.

**Source:** approval gate vs permission

## MA-j06.9

A company says its agent has a "human in the loop". Decide which statements about that phrase are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A person who approves an action before it proceeds is in the loop, and one who reads a log afterward is not.
- [ ] B. Clicking approve without reading satisfies the purpose of the loop.
- [ ] C. An automatic validator counts as a human in the loop.
- [ ] D. It means a person writes the output by hand.
- [ ] E. A person who reads the final transcript after the action completes is in the loop.

**Key:** A=T B=F C=F D=F E=F

**Why:**

- A: In the loop means able to stop the action.
- B: Rubber-stamping removes the check the loop exists to provide.
- C: A validator is code, not a person.
- D: A person in the loop reviews or approves; writing is a different role.
- E: They can no longer block the action.

**Source:** human in the loop

## MA-j06.10

After an incident, a reviewer asks to see who approved what and which tools ran. Decide which statements about an audit log are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A good audit log records the tool calls, their arguments and results, and who approved them.
- [ ] B. An audit log is a record of who or what did what, and when, kept for later review.
- [ ] C. An audit log is another name for a checkpoint that restores earlier state.
- [ ] D. An audit log lets the system undo the actions it recorded.
- [ ] E. An audit log blocks a bad action before it happens.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Those details let a reviewer reconstruct events.
- B: It supports reconstruction after the fact.
- C: A log records events; a checkpoint holds state.
- D: Recording is not reversing.
- E: It records; a gate is what blocks.

**Source:** audit log

## MA-j06.11

A manager assigns an AI agent to draft customer refunds, and a mistake occurs. Decide which statements about accountability and responsibility are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Delegating a task to another agent does not delegate the answerability for it.
- [ ] B. Responsibility for doing the work and accountability for the outcome are held by the same party in a delegation.
- [ ] C. Accountability means being answerable: able to be asked to explain a result and to put it right.
- [ ] D. Accountability passes to the agent once the task is delegated.
- [ ] E. The agent can be given the work to do, while the person who deployed it stays answerable for the outcome.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: The delegator remains accountable.
- B: Delegation moves the work, not the answerability.
- C: It is about answering for the outcome.
- D: An agent cannot be called to account in the way a person can.
- E: Doing the work and answering for it are separate.

**Source:** accountability vs responsibility

## MA-j06.12

A team reviews risks in a language-model product. Decide which statements about bias, privacy and data leakage are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Bias is a systematic skew in outputs that favours or disadvantages some groups, often inherited from training data or examples.
- [ ] B. In evaluation, data leakage is test examples reaching the training data, which inflates scores.
- [ ] C. Privacy concerns protecting personal information about people, including what is collected and who sees it.
- [ ] D. In a security sense, data leakage is information reaching a person or place it should not, such as a secret that appears in a response or a log.
- [ ] E. Privacy and data leakage are two words for the same problem.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: It is a pattern, not a one-off mistake.
- B: Test data seen in training makes results look better than they are.
- C: It covers collection and sharing.
- D: The information escapes its intended boundary.
- E: Privacy is the aim of protecting personal information; leakage is one way it fails.

**Source:** bias, privacy, data leakage

## MA-j06.13

A company hires a group to try to make its chatbot produce harmful output or follow hidden instructions before launch. Decide which statements about red teaming are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Red teaming differs from ordinary testing because it assumes an adversary who is trying to break the system.
- [ ] B. A red team deliberately attacks a system to find failures before real users do.
- [ ] C. Red-team findings can be added to the eval set as test cases.
- [ ] D. A red team that finds nothing proves the system is safe.
- [ ] E. A red team is the group that approves the release.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Ordinary tests check expected use.
- B: The attitude is adversarial.
- C: Each found failure becomes a case to rerun.
- D: Absence of findings is not proof of safety.
- E: Finding failures is separate from approving release.

**Source:** red team

## MA-j06.14

An agent sent a refund email that described a policy the company does not have. The email was well-formatted. Decide which statements correctly name and handle the situation. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Adding this case to the regression set keeps the failure from returning unnoticed.
- [ ] B. The invented policy is a hallucination.
- [ ] C. Because the email was well-formatted, the format check shows it was correct.
- [ ] D. An audit log would have stopped the email from going out.
- [ ] E. An approval gate before sending would have given a person the chance to block the email.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: Rerunning past failures catches regressions.
- B: Fluent and unsupported content is a hallucination.
- C: Format validity is not factual validity.
- D: A log records after the fact and does not block.
- E: A gate stops the action until a person decides.

**Source:** incident vocabulary
