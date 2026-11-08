# Jargon test: retrieval, fine-tuning and configuration

## MA-j04.1

Which statements tell retrieval and fine-tuning apart? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Retrieval changes what the model sees in a request by adding passages to the prompt.
- [ ] B. Fine-tuning changes the model by continuing training, which updates weights.
- [ ] C. Retrieval updates the model's weights.
- [ ] D. Fine-tuning is the better way to add a large amount of changing facts.
- [ ] E. Retrieval and fine-tuning are two names for training on documents.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Retrieval works on the context.
- B: Fine-tuning works on the weights.
- C: Retrieval leaves weights unchanged.
- D: Changing facts suit retrieval, which can update at once.
- E: Retrieval is not training.

**Source:** retrieval vs fine-tuning

## MA-j04.2

Which statements about RAG and chunks are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. RAG means retrieving relevant passages, adding them to the prompt, then generating.
- [ ] B. A chunk is a piece of a document cut to a size that can be indexed and retrieved.
- [ ] C. Chunking splits the model's vocabulary into groups.
- [ ] D. Chunk size is a trade-off: large chunks dilute the match and use context, and small chunks lose surrounding meaning.
- [ ] E. RAG guarantees correct answers because the source text is supplied.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Retrieval-augmented generation retrieves before it generates.
- B: Documents are split into chunks for retrieval.
- C: Chunking splits documents, not the vocabulary.
- D: Chunk size affects both match quality and context use.
- E: Retrieval can miss or mis-rank, and the model can misread the text.

**Source:** RAG, chunk

## MA-j04.3

Which statements about embeddings and vector search are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. For retrieval, an embedding is a vector that represents the meaning of a chunk or a query.
- [ ] B. Vector search finds chunks whose vectors are nearest to the query's vector.
- [ ] C. Vector search matches the exact words typed, character by character.
- [ ] D. Because results rest on similarity, retrieval is approximate and can miss or mis-rank passages.
- [ ] E. The same embedding model should embed documents and queries so the vectors can be compared.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Embeddings place text in a space where closeness means similarity.
- B: Vector search ranks by closeness.
- C: That describes exact keyword matching.
- D: Similarity is not certainty.
- E: Vectors from different models are not comparable.

**Source:** embedding, vector search

## MA-j04.4

Which statements about grounding and citation are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Grounding is tying an answer to supplied source material.
- [ ] B. A citation points to the source passage behind a claim so a reader can check it.
- [ ] C. A citation proves the claim is true.
- [ ] D. A grounded answer can still misquote or misread its source, so the cited passage is worth checking.
- [ ] E. Grounding means fine-tuning the model on the sources.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: A grounded answer rests on given sources.
- B: Citations make claims checkable.
- C: A citation shows where a claim came from, not that it is correct.
- D: Grounding reduces but does not remove error.
- E: Grounding supplies sources in context; fine-tuning changes weights.

**Source:** grounding, citation

## MA-j04.5

Which statements about pretraining, fine-tuning and inference are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Pretraining learns general language patterns from very large amounts of text.
- [ ] B. Inference is using the trained model to produce output, and the weights stay unchanged.
- [ ] C. Fine-tuning is the first stage, done before pretraining.
- [ ] D. Inference is the stage in which weights are updated from the user's chat.
- [ ] E. Pretraining happens again each time a user sends a prompt.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Pretraining is the broad first stage.
- B: Inference does not update weights.
- C: Fine-tuning follows pretraining.
- D: A chat does not update weights.
- E: A prompt triggers inference, not training.

**Source:** pretraining vs fine-tuning vs inference

## MA-j04.6

Which single statement about base and instruction-tuned models is true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A base model is trained to follow instructions and decline harmful requests.
- [ ] B. An instruction-tuned model is a base model trained further on examples of instructions and good responses.
- [ ] C. A base model is a smaller model made by shrinking a larger one.
- [ ] D. An instruction-tuned model is the same as a base model with a system prompt.
- [ ] E. A base model is a model fine-tuned on a company's own data.

**Key:** A=F B=T C=F D=F E=F

**Why:**

- A: That describes an instruction-tuned model.
- B: Instruction tuning is added after the base model.
- C: Base refers to the stage after pretraining, not to size.
- D: Tuning changes weights; a system prompt changes context.
- E: That is a fine-tuned model; a base model is the starting point.

**Source:** base vs instruction-tuned

## MA-j04.7

Which statements tell parameters and hyperparameters apart? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Parameters, also called weights, are values learned during training.
- [ ] B. Hyperparameters are settings chosen before or around a training run, such as learning rate or batch size.
- [ ] C. The gradient learns the learning rate.
- [ ] D. Generation settings such as temperature are chosen by the user and are not learned weights.
- [ ] E. The number of epochs is a hyperparameter.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Parameters are learned.
- B: Hyperparameters are set by people.
- C: The learning rate is chosen, not learned by the gradient.
- D: Settings differ from weights.
- E: Epochs are chosen for the run.

**Source:** parameters vs hyperparameters

## MA-j04.8

Which statements tell configuration and weights apart? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Weights are the learned numbers saved in the model file.
- [ ] B. Configuration is the settings and files that shape how the model is run, such as a system prompt, temperature, tools and permissions, without changing weights.
- [ ] C. Editing a system prompt changes the weights.
- [ ] D. Changing the weights takes training, such as fine-tuning.
- [ ] E. Configuration is stored inside the weights.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Weights are the model's learned content.
- B: Configuration surrounds the model.
- C: A system prompt is part of the context.
- D: Weights change only through training.
- E: Configuration sits outside the weights.

**Source:** config vs weights

## MA-j04.9

Which pairings of a description and a term are correct? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Looking up passages by similarity and adding them to the prompt: retrieval.
- [ ] B. The stage that teaches general language from huge text: pretraining.
- [ ] C. The learned numbers saved in a model: hyperparameters.
- [ ] D. Using a trained model to produce an output: fine-tuning.
- [ ] E. Linking a claim to its source: chunk.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: That is retrieval.
- B: That is pretraining.
- C: Those are parameters, also called weights.
- D: That is inference.
- E: That is a citation.

**Source:** name the term

## MA-j04.10

A manager tells Claude: "Fine-tune the model on our policy PDFs so it has current policy, and change the parameters like temperature to be accurate." Which statements spot the imprecise wording? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Fine-tune ... so it has current policy" is imprecise: documents that change call for retrieval, since fine-tuned knowledge is hard to update.
- [ ] B. "Parameters like temperature" is imprecise: temperature is a generation setting, not a learned parameter.
- [ ] C. "Policy PDFs" should be "logits".
- [ ] D. "Model" should be "chunk".
- [ ] E. Fine-tuning is the right term for looking up the PDFs at question time.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Retrieval suits changing facts.
- B: Parameters are weights.
- C: Logits are scores, not documents.
- D: A model and a chunk are different things.
- E: Looking up at question time is retrieval.

**Source:** spot the wrong word

## MA-j04.11

A user tells Claude: "Make Claude know our docs better." Which rewrites use the exact terms? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Chunk the docs, embed the chunks, and use vector search to retrieve passages for each question."
- [ ] B. "Ask for a citation to the retrieved passage with each claim."
- [ ] C. "Ground the answers in the retrieved passages and say when they do not contain the answer."
- [ ] D. "Retrain the hyperparameters on the docs."
- [ ] E. "Raise the temperature so it recalls the docs."

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: This names the retrieval steps.
- B: Citations make claims checkable.
- C: Grounding ties answers to sources.
- D: Hyperparameters are chosen, not trained.
- E: Temperature changes sampling randomness, not knowledge.

**Source:** choose the rewrite

## MA-j04.12

A team starts from a pretrained base model, trains it on a few thousand example pairs at a small learning rate for a few epochs, and saves a new file. Which statements name the steps correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The team is fine-tuning the model.
- [ ] B. The learning rate and the number of epochs are hyperparameters.
- [ ] C. The saved file contains updated weights.
- [ ] D. Using the saved file to answer questions is inference.
- [ ] E. The step was pretraining because it began from a base model.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: Continued training on a targeted set is fine-tuning.
- B: They are chosen settings for the run.
- C: Training changes the weights.
- D: Inference is using a trained model.
- E: Starting from a base model describes fine-tuning.

**Source:** fine-tuning scenario
