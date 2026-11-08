# Chapter 9: Training and configuration

## MA-ch09.1

A team uploads policy documents to an assistant product's project store and rewrites the project's system prompt. Answers improve. The product supplies the documents and the prompt to the model at request time and runs no fine-tuning job. A teammate writes: "we trained the model on our policies." Each statement is worth 1 point (5 points total).

- [ ] A. A fine-tuning job is the step that updates weights from training examples.
- [ ] B. "We supplied context and edited the system prompt" is the precise description of what happened.
- [ ] C. Rewriting the system prompt changes the model's weights.
- [ ] D. Supplying documents to the model at request time is context supply (retrieval), not training.
- [ ] E. Because answers improved, the model's parameters changed.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Fine-tuning is continued training that changes the weights.
- B: Naming the changed object (context, prompt) keeps the claim exact.
- C: A system prompt is request text; weights change only through training.
- D: Context is text placed in the request; the weights are untouched.
- E: Better answers can come from better inputs with the same parameters.

**Source:** training vs context supply

## MA-ch09.2

Five kinds of object can be changed to alter an LLM-based system: weights, prompt text, supplied context, tools and permissions, and sampling settings. A team lists edits. Check each statement that classifies the edit correctly. Each statement is worth 1 point (5 points total).

- [ ] A. Lowering the temperature is a change to a sampling setting.
- [ ] B. Enabling a new search tool is a change to the sampling settings.
- [ ] C. Running a fine-tuning job is a change to the prompt.
- [ ] D. Adding a document to a knowledge base is a change to the weights.
- [ ] E. Rewording the instruction at the top of each request is a change to the prompt.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Temperature is a run-time decoding parameter, not a weight.
- B: A tool is a capability, not a decoding setting.
- C: Fine-tuning changes weights, not the prompt text.
- D: A document is supplied context, retrieved into the request.
- E: Prompt text is the instruction the model reads.

**Source:** five changeable objects

## MA-ch09.3

A deployment configuration lists: a system prompt reading "Answer from the provided documents", a temperature of 0.2, allowed tools search_docs and read_file, and a retrieval setting that supplies five passages per question. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The system prompt is an instruction supplied with each request.
- [ ] B. The temperature entry is a retrieval setting.
- [ ] C. Editing this file retrains the model.
- [ ] D. The list of allowed tools is part of the model's weights.
- [ ] E. The five retrieved passages are supplied context.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: The system prompt sets standing behaviour for the conversation.
- B: Temperature is a sampling setting; retrieval supplies passages.
- C: Configuration changes what is sent and allowed, not the weights.
- D: Allowed tools are host configuration, outside the model.
- E: Retrieval selects text and adds it to the context window.

**Source:** configuration anatomy

## MA-ch09.4

An agent host enables a new tool server with read and write access to a project folder, and a developer adds a permission rule requiring human approval before a write. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A tool and a permission are the same thing.
- [ ] B. Requiring approval before writes narrows risk without changing the model.
- [ ] C. A permission rule is a host-side control on what the agent may do.
- [ ] D. An approval gate lets the agent proceed automatically once the action is logged.
- [ ] E. Granting the tool server access teaches the model to edit files.

**Key:** A=F B=T C=T D=F E=F

**Why:**

- A: A tool is a capability; a permission governs whether it may be used.
- B: The control sits around the model, so the model is unchanged.
- C: Permissions are enforced by the host, not by the model's training.
- D: An approval gate waits for a human decision.
- E: Access gives a capability; it does not change the weights.

**Source:** tools, permissions, approval gates

## MA-ch09.5

An assistant product "remembers" that a user prefers metric units. Engineers find that a note is saved in a database and prepended to the prompt of later conversations; no fine-tuning occurs. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. This memory is stored context placed into the prompt.
- [ ] B. "The model learned from me" is an exact description of this mechanism.
- [ ] C. Memory and context window are the same thing.
- [ ] D. Deleting the saved note removes the remembered preference.
- [ ] E. The model's weights were updated from this user's conversations.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Persistence comes from saved text re-supplied each time.
- B: Learning means parameter change; this is stored context.
- C: Memory is a store across sessions; the context window is the text the model reads in one request.
- D: The preference lives in the note, not in the model.
- E: No training took place, so weights are unchanged.

**Source:** memory vs training

## MA-ch09.6

A team must adapt an assistant to company policies and compares three approaches: editing the prompt, adding retrieval over a policy corpus, and fine-tuning. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Editing the prompt changes behaviour without a training job.
- [ ] B. Fine-tuning changes the weights, so the change is harder to inspect and reverse than a prompt edit.
- [ ] C. Retrieval hides the supplied passage from a reader checking the answer.
- [ ] D. A policy change is easiest to roll out by retraining the model.
- [ ] E. Retrieval changes the weights so the model memorizes the corpus.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Prompt edits are inputs to the model.
- B: Weights are opaque; a prompt is readable text.
- C: Retrieved passages are visible text, so they can be inspected.
- D: Updating a retrieved document or prompt is faster and reversible.
- E: Retrieval fetches passages into context at request time.

**Source:** prompt vs retrieval vs fine-tuning

## MA-ch09.7

A team ranks ways to change an assistant by how easily each change can be inspected and reversed. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A system prompt is hard to inspect because it is stored as numeric weights.
- [ ] B. Version control does not help with rolling back a configuration change.
- [ ] C. A permission rule can be tightened or removed without retraining.
- [ ] D. A fine-tuned weight update is as easy to inspect as a prompt.
- [ ] E. Sampling settings change the weights.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: A prompt is text, not weights.
- B: Recorded versions can be restored.
- C: It is host configuration.
- D: Weight changes are numeric and hard to read.
- E: They alter decoding at run time only.

**Source:** inspectability and reversibility

## MA-ch09.8

A team suspects one saved instruction line makes an assistant refuse off-topic questions. They run the same 30 off-topic questions twice at temperature 0.8, once with the line and once without, keeping the model and the rest of the prompt the same. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. At temperature 0.8 a single run per condition gives a stable answer.
- [ ] B. This is a fine-tuning comparison, not an ablation.
- [ ] C. A difference in refusals shows the line is the single cause of refusing.
- [ ] D. Repeating each condition several times reduces the effect of sampling randomness.
- [ ] E. Keeping the rest of the prompt the same is a control.

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: Sampling varies, so repeated runs are needed.
- B: Removing a component and measuring the effect is an ablation.
- C: It shows an effect of the line, not that no other cause exists.
- D: More runs average out run-to-run variation.
- E: Holding other factors constant supports attribution.

**Source:** ablation and controls

## MA-ch09.9

To test whether an assistant is sensitive to the choice of few-shot example, a team runs each of two prompts 20 times at temperature 0.8 on the same question. Prompt 1 is correct in 11 runs and prompt 2 in 17. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A few-shot example is a worked input and output pair placed in the prompt.
- [ ] B. A fine-tuning job was performed by changing the example.
- [ ] C. Repeating runs is needed because sampling makes single outputs vary.
- [ ] D. The pass counts are a sampling setting.
- [ ] E. The pass counts prove the example is the cause beyond doubt.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Few-shot prompting teaches format by demonstration.
- B: Changing a prompt example does not train the model.
- C: Temperature above zero makes decoding random.
- D: They are evaluation results, not settings.
- E: A measured difference supports sensitivity, not certainty.

**Source:** few-shot sensitivity

## MA-ch09.10

A hosted assistant answers differently on Tuesday than on Monday to the same user question. The only records are the two responses and the model's unchanged display name. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A silent provider update behind the same name is ruled out by the unchanged display name.
- [ ] B. Recording the prompt, settings, and timestamp supports diagnosis.
- [ ] C. The two responses alone identify the cause.
- [ ] D. Sampling randomness is one candidate cause.
- [ ] E. A changed answer shows the weights were retrained that weekend.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: A hosted model can change while its name stays the same.
- B: A replayable record narrows the candidate causes.
- C: Output differences do not reveal why they differ.
- D: With temperature above zero, outputs vary.
- E: Many causes fit, including sampling and context.

**Source:** diagnosing changed outputs

## MA-ch09.11

Three people each call their result reproducible. Person 1 supplies a training script, dataset, hyperparameters, and fixed random seed with deterministic code. Person 2 supplies a recorded prompt and sampling settings to replay against a hosted model. Person 3 supplies a configuration file for a tool-using agent. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A fixed seed makes results differ on each run.
- [ ] B. Replaying a prompt against a hosted model guarantees identical output.
- [ ] C. A temperature of 0 reduces randomness in sampling.
- [ ] D. Reproducibility and correctness mean the same thing.
- [ ] E. Person 1's claim is stronger because inputs and procedure are fully supplied.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: A seed makes pseudo-random choices repeatable.
- B: Hosted models may change and sampling may vary.
- C: It favours the most probable token.
- D: A result can be reproduced and still be wrong.
- E: Complete inputs allow independent re-running.

**Source:** reproducibility

## MA-ch09.12

A language model's next-token probabilities come from converting logits with a softmax, optionally divided by a temperature. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A logit is an unnormalized score for a token before softmax.
- [ ] B. Lower temperature makes the distribution sharper, favouring the top token.
- [ ] C. Higher temperature makes the distribution flatter, so unlikely tokens are sampled more often.
- [ ] D. Top-p limits sampling to the smallest set of tokens whose probabilities add up to p.
- [ ] E. Temperature changes the weights during decoding.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: Softmax turns logits into probabilities.
- B: Dividing logits by a small number widens gaps.
- C: Larger values equalize probabilities.
- D: Top-p is nucleus sampling; temperature rescales the distribution.
- E: It rescales logits at sampling time.

**Source:** temperature vs top-p

## MA-ch09.13

A developer tells Claude: "Retrain the model on this PDF so it knows our refund policy, and make the answers more creative by raising the learning rate." The developer actually wants the PDF used when answering, and more varied wording. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Raising the learning rate at request time changes the answer style.
- [ ] B. Learning rate controls randomness during decoding.
- [ ] C. A better rewrite is: "Use the attached PDF as context when answering, and raise the temperature slightly."
- [ ] D. "Retrain" is the wrong word for supplying a PDF at request time; "retrieve from" or "supply as context" is exact.
- [ ] E. "Learning rate" is the wrong term for output variety; the sampling setting is temperature.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: There is no learning step at request time.
- B: It sets update step size in training.
- C: It names context and a sampling setting.
- D: Retraining updates weights; supplying a document is context.
- E: Learning rate is a training hyperparameter.

**Source:** imprecise prompt wording

## MA-ch09.14

Training a model involves quantities learned from data and quantities chosen by people. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Weights and biases are parameters learned from the data.
- [ ] B. A hyperparameter and a parameter are the same.
- [ ] C. The loss function is a design choice made by people.
- [ ] D. The number of training steps is a parameter that gradient descent learns.
- [ ] E. Learning rate is a parameter that training learns from data.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Parameters are fitted during training.
- B: A parameter is learned; a hyperparameter is a setting.
- C: The objective is selected, not learned.
- D: It is a hyperparameter chosen before or during setup.
- E: Learning rate is a hyperparameter chosen by people.

**Source:** parameter vs hyperparameter

## MA-ch09.15

A simple classifier computes a score from a feature using a weight and a bias, passes the score through a sigmoid to get a probability, and predicts label 1 when the probability reaches a threshold. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The weight scales the feature's influence on the score.
- [ ] B. The sigmoid maps a score to a number between 0 and 1.
- [ ] C. Moving the threshold changes the learned weight.
- [ ] D. The probability is the sigmoid of the score.
- [ ] E. The bias shifts the score regardless of the feature.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: A larger weight makes the score react more to the feature.
- B: That output is read as a probability.
- C: The threshold is applied after training; the weight is unchanged.
- D: The sigmoid converts score to probability.
- E: It moves the decision boundary.

**Source:** score, probability, decision

## MA-ch09.16

A classifier is trained with a loss function, and a team compares loss with accuracy. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Accuracy is the loss that gradient descent minimizes directly.
- [ ] B. A loss function turns predictions into a penalty that training tries to reduce.
- [ ] C. Two models with equal accuracy can differ in cross-entropy.
- [ ] D. Cross-entropy penalizes a confident wrong prediction heavily.
- [ ] E. A smooth loss gives gradient descent a direction to move.

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: Accuracy is not smooth, so a smooth loss is used.
- B: Loss measures prediction error.
- C: Confidence changes the loss.
- D: The penalty grows as probability on the true label shrinks.
- E: Differentiability provides a usable gradient.

**Source:** loss vs accuracy

## MA-ch09.17

In gradient descent the gradient gives the direction in which the loss rises fastest for each parameter, and an update steps against it by an amount set by the learning rate. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A learning rate that is too large can make the loss diverge.
- [ ] B. An update moves parameters opposite the gradient.
- [ ] C. A very small learning rate makes the loss diverge.
- [ ] D. An epoch is one update step.
- [ ] E. The gradient is the loss value itself.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Steps overshoot the minimum.
- B: Descending reduces loss.
- C: Small steps make progress slow, not unstable.
- D: An epoch is one pass through the training data.
- E: It is the slope of the loss with respect to parameters.

**Source:** gradient descent and learning rate

## MA-ch09.18

Training can use the whole dataset for each update, a small random subset, or a single example. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Stochastic gradient descent estimates the gradient from a sample, so updates are noisy.
- [ ] B. A minibatch is the whole dataset used for one update.
- [ ] C. Using minibatches changes the loss function.
- [ ] D. Full-batch gradient descent uses the whole dataset to compute each update.
- [ ] E. A batch and an epoch mean the same thing.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Sampling adds variance.
- B: A minibatch is a small subset.
- C: It changes how the gradient is estimated.
- D: Each step is exact but costly.
- E: A batch is the subset for one update; an epoch is a full pass.

**Source:** batch, minibatch, epoch

## MA-ch09.19

A student checks a hand-derived gradient by nudging a parameter slightly up and down, recomputing the loss each time, and comparing the slope estimate with the formula. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Agreement supports the formula against the loss as coded.
- [ ] B. A disagreement points to an error in the formula, the code, or the numerical step.
- [ ] C. This is a numerical gradient check.
- [ ] D. Agreement shows the loss function is the right objective.
- [ ] E. Making the nudge extremely small improves accuracy at each smaller size.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: The check compares formula with the implemented loss.
- B: Any of the three can cause a mismatch.
- C: It approximates the derivative by finite differences.
- D: It verifies the derivative, not the choice of loss.
- E: Floating-point rounding errors grow when the step is too small.

**Source:** numerical gradient check

## MA-ch09.20

A training function runs a fixed number of updates at a fixed learning rate with no stopping test, then returns the final parameters and a low final training loss. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Recording the loss at each step gives the same information as two endpoints.
- [ ] B. Convergence means the loss has stopped improving meaningfully.
- [ ] C. A low training loss shows the fit to the training data, not performance on unseen data.
- [ ] D. A stopping rule defines when training ends, such as a loss change below a tolerance.
- [ ] E. Low training loss alone does not show the model generalizes.

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: A full history shows divergence, plateaus, and oscillation.
- B: Updates become small.
- C: Generalization needs held-out evidence.
- D: It replaces an arbitrary step count.
- E: Held-out evidence is needed.

**Source:** training loss, convergence

## MA-ch09.21

A team uses three data roles: training data, validation data, and test data. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Validation data is used to choose among settings such as learning rate.
- [ ] B. Validation data and test data are the same set.
- [ ] C. Test data should guide the choice of hyperparameters.
- [ ] D. Test data is reused freely during tuning.
- [ ] E. Training data is used to choose among settings such as learning rate.

**Key:** A=T B=F C=F D=F E=F

**Why:**

- A: It guides tuning.
- B: Reusing one set for both defeats the final check.
- C: Using it for choices makes the final estimate optimistic.
- D: Using it in tuning ruins the final estimate.
- E: That is the role of validation data.

**Source:** train, validation, test

## MA-ch09.22

A team trains a classifier, tries 12 combinations of learning rate and step count, picks the combination with the highest accuracy on its single evaluation set, and reports that accuracy as expected performance. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The reported accuracy is optimistically biased.
- [ ] B. This is selection on the evaluation set.
- [ ] C. Trying more combinations reduces the bias.
- [ ] D. A second look at the same evaluation set gives a fairer estimate.
- [ ] E. The reported accuracy is an unbiased estimate of performance on new data.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: The best of many tries partly reflects chance.
- B: The set influenced the choice.
- C: More tries increase the chance of a lucky score.
- D: A fresh set was not used in selection.
- E: The same data chose the winner, so the estimate is inflated.

**Source:** selection bias on evaluation

## MA-ch09.23

Fifty of a team's 200 evaluation examples are accidentally copied into the training set, and the model is retrained. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Accuracy on the leaked examples overstates generalization.
- [ ] B. This is data leakage between training and evaluation.
- [ ] C. A way to prevent it is to split the data before the first training step and keep the test set separate.
- [ ] D. Accuracy on the leaked examples measures generalization.
- [ ] E. The reported accuracy would be inflated.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: The model saw those examples.
- B: Evaluation data influenced training.
- C: A clean split prevents contamination.
- D: The model saw those examples.
- E: Memorized items score high.

**Source:** data leakage

## MA-ch09.24

A team compares 30 prompt variants on the same 100 questions, and every variant has the same true accuracy. The best observed score still looks clearly higher than the rest. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. More variants tested raises the chance of an impressive but spurious best score.
- [ ] B. A higher score on one set proves the variant is better.
- [ ] C. Using the same questions is a way to avoid overfitting to them.
- [ ] D. Chance alone can make the best of many variants look better.
- [ ] E. The best variant's score should be re-checked on fresh questions.

**Key:** A=T B=F C=F D=T E=T

**Why:**

- A: More draws raise the maximum.
- B: Noise can explain it.
- C: Repeated use of one set invites overfitting to it.
- D: Maximum of noisy scores is biased upward.
- E: Fresh data removes selection effects.

**Source:** multiple comparisons

## MA-ch09.25

A classifier outputs probabilities, and the decision is label 1 when the probability passes a threshold the team picks. A false negative is a positive case predicted negative; a false positive is a negative case predicted positive. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Recall is the share of predicted positives that are correct.
- [ ] B. Raising the threshold tends to reduce false positives and increase false negatives.
- [ ] C. Lowering the threshold usually produces more positive predictions.
- [ ] D. The threshold is learned by gradient descent.
- [ ] E. A missed escalation is a false negative.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: That is precision; recall is the share of actual positives found.
- B: Fewer cases are called positive.
- C: More cases pass a lower bar.
- D: It is chosen after training.
- E: A true positive case was predicted negative.

**Source:** threshold, false positives and negatives

## MA-ch09.26

A model assigns probability 0.9 to each of 1,000 test items, and 600 of those items are actually positive. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Probability 0.9 means the model is right on 90 percent of runs of a sampling process.
- [ ] B. Calibration and accuracy are the same measure.
- [ ] C. The model is overconfident.
- [ ] D. A calibrated model's stated probabilities match observed frequencies.
- [ ] E. Group-by-predicted-probability checks compare predicted with observed rates.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: It states belief about the label, which calibration tests.
- B: A model can rank well and still be miscalibrated.
- C: Stated probability exceeds the observed rate.
- D: Calibration is agreement between probability and frequency.
- E: A reliability check bins predictions.

**Source:** calibration

## MA-ch09.27

A fitted classifier has a positive weight on feature x, and an analyst reads it as evidence about causes. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Confounding is a variable that influences both x and the label.
- [ ] B. A positive weight describes an association in the training data.
- [ ] C. Prediction and intervention are different questions.
- [ ] D. A randomized experiment helps separate cause from association.
- [ ] E. A positive weight shows that changing x causes the label to change.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: A confounder creates a misleading association.
- B: It reflects correlation.
- C: Predicting under observation differs from acting on x.
- D: Random assignment breaks links to confounders.
- E: Association does not establish intervention effects.

**Source:** association vs cause

## MA-ch09.28

The ladder of causation has three rungs: association, intervention, and counterfactual. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "What happens to wages if we require training?" is an intervention question.
- [ ] B. "Do students who open reminders pass more often?" is an association question.
- [ ] C. "Would this student have passed without the reminder?" is a counterfactual question.
- [ ] D. A standard supervised classifier answers counterfactual questions.
- [ ] E. Association, intervention, and counterfactual are three names for the same rung.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: It asks about acting on a variable.
- B: It asks about co-occurrence.
- C: It asks about a different history.
- D: It models association.
- E: They are distinct levels.

**Source:** ladder of causation

## MA-ch09.29

Two treatments were assigned by clinicians. Within mild cases and within severe cases, treatment Y did better in one group and X in the other, yet pooled results favour Y; the pooled and group-wise comparisons point different ways because severe cases mostly received X. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Severity here is a confounder related to treatment assignment and outcome.
- [ ] B. Random assignment would have made treatment independent of severity.
- [ ] C. Simpson's paradox is a reversal when groups are combined.
- [ ] D. Stratifying by severity compares like with like.
- [ ] E. Pooled results are the better guide because they use more data.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: It affects both who got X and how they fared.
- B: Randomization balances confounders on average.
- C: Aggregation can flip a trend.
- D: It controls for the confounder.
- E: More data does not remove confounding.

**Source:** confounding and Simpson's paradox

## MA-ch09.30

A model that flags at-risk students was fit on a year in which nobody acted on its flags. The next year advisors contact every flagged student, and the model is refit on that year's outcomes. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Acting on predictions can create a feedback loop.
- [ ] B. The new year's data come from a changed situation, a distribution shift.
- [ ] C. The first model's predictions describe outcomes without intervention.
- [ ] D. Refitting on the new data restores the original meaning of the flags.
- [ ] E. Predicting an outcome and changing it are the same question.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Deployment changes the data the next model sees.
- B: Acting on predictions alters outcomes.
- C: They were fitted when no one acted.
- D: The flags now reflect the effect of advising.
- E: Prediction is association; changing is intervention.

**Source:** distribution shift and feedback

## MA-ch09.31

An analyst asks a language model for help with a causal question about an observational dataset. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Identification is the argument that a causal effect can be estimated from the data.
- [ ] B. The model's fluent answer establishes the causal effect.
- [ ] C. The model can suggest candidate confounders and ways to check them.
- [ ] D. A well-worded prompt removes the need for design assumptions.
- [ ] E. The analyst keeps the identification judgment about which assumptions are credible.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: It rests on assumptions about confounding.
- B: Fluency is not evidence.
- C: This is brainstorming support.
- D: Assumptions come from design and domain knowledge.
- E: The accountable person decides.

**Source:** delegation of causal analysis

## MA-ch09.32

A team writes down the objective, held-out evaluation set, and stopping rule before running an experiment, and a developer writes a dated prediction of the first update before running AI-written training code. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Writing the plan first is pre-specification.
- [ ] B. A pre-specified plan makes the result correct.
- [ ] C. A dated, falsifiable prediction can show the code is wrong if reality disagrees.
- [ ] D. A prediction written after seeing results has the same value as one written before.
- [ ] E. The stopping rule states when the run ends.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: It fixes the test before seeing results.
- B: It limits bias but does not guarantee correctness.
- C: A failed prediction flags a defect.
- D: Hindsight can fit any outcome.
- E: It prevents ending training only when results look good.

**Source:** pre-specification

## MA-ch09.33

An AI assistant writes a training function and, in the same session, a unit test comparing the function's output with its own earlier output. A reviewer asks what has been verified. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A test that checks the loss decreased establishes correct gradients.
- [ ] B. A diff review adds nothing once tests pass.
- [ ] C. A passing test written by the same assistant proves the code is correct.
- [ ] D. Comparing code to its own earlier output shows consistency, not correctness.
- [ ] E. A numerical gradient check shares the same assumptions as the code under test.

**Key:** A=F B=F C=F D=T E=F

**Why:**

- A: A buggy update can still reduce loss.
- B: Reading the change is a human check.
- C: The test can share the same mistake.
- D: A wrong result repeats.
- E: It is an independent check against another method.

**Source:** verifying AI-written code

## MA-ch09.34

A report says: "the model learned", "the model fits its training data", "the model generalizes", and "the model is useful." Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An accuracy rise after adding a PDF to the prompt shows the model learned the PDF.
- [ ] B. Low training loss supports the claim that the model generalizes.
- [ ] C. "Generalizes" requires evidence from held-out data.
- [ ] D. "Fits its training data" is supported by low training loss.
- [ ] E. "Useful" needs evidence about the real task and cost of errors.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: It shows better answers with the document as context; weights are unchanged.
- B: It supports only the fit claim.
- C: Unseen data tests transfer.
- D: It describes the training set only.
- E: Usefulness depends on use.

**Source:** claims ladder

## MA-ch09.35

A team asks an AI assistant to help change a classifier that escalates messages to a human. They discuss which tasks to delegate and which to keep with the accountable engineer. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Planning before acting means stating the approach before the assistant edits files.
- [ ] B. Choosing the cost of a missed escalation relative to a false alarm stays with the accountable person.
- [ ] C. Drafting boilerplate code is a task suited to delegation.
- [ ] D. The assistant carries the accountability for the decision.
- [ ] E. Accepting the assistant's summary in place of a diff review is adequate.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: A plan can be reviewed.
- B: It is a value judgment about harm.
- C: Output can be checked.
- D: People remain accountable.
- E: A diff review shows what changed.

**Source:** delegation and judgment
