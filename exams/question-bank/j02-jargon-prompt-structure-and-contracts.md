# Jargon test: prompt structure and contracts

## MA-j02.1

Which statements tell a system prompt and a user turn apart correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A system prompt holds standing instructions and a role for the whole conversation.
- [ ] B. A user turn is one message from the person in the conversation.
- [ ] C. The system prompt is the model's reply to the first user turn.
- [ ] D. A user turn is stored in the model's weights once it is sent.
- [ ] E. System prompt and user turn are the same thing because both end up as tokens in the context.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: The system prompt sets the assistant's job before the user speaks.
- B: A turn is a single message in the exchange.
- C: A reply is an assistant turn, not a system prompt.
- D: Messages sit in the context; weights are not changed.
- E: They differ in source and purpose even though both are tokens.

**Source:** system prompt vs user turn

## MA-j02.2

Which statements about role and persona are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. In a chat message list, the role labels who is speaking, such as system, user or assistant.
- [ ] B. The assistant role marks text the model wrote, including earlier replies placed back in the conversation.
- [ ] C. A persona is a character or voice that a prompt asks the model to adopt.
- [ ] D. Giving a persona changes the weights so the model permanently becomes that character.
- [ ] E. Role is another word for persona.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Role is the source label of a message.
- B: Past model replies carry the assistant role.
- C: Persona is a requested character, such as a patient tutor.
- D: A persona is an instruction in the context and leaves the weights alone.
- E: Role names a message's source; persona is a requested character.

**Source:** role vs persona

## MA-j02.3

Which statements about zero-shot, few-shot, instructions and examples are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A zero-shot prompt gives an instruction with no worked examples.
- [ ] B. A few-shot prompt includes a small number of example input-output pairs.
- [ ] C. An instruction says what to do; an example shows what a good result looks like.
- [ ] D. Few-shot examples retrain the model for later conversations.
- [ ] E. A few-shot prompt can anchor a format, but the model may copy surface features of the examples.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: Zero-shot means no examples.
- B: Few-shot shows the pattern by example.
- C: Instruction and example are different kinds of prompt content.
- D: Examples live in the context for that request and do not retrain.
- E: Models imitate the examples, including incidental details.

**Source:** few-shot vs zero-shot

## MA-j02.4

Which statements about delimiters and output schemas are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Delimiters such as triple quotes or XML-style tags mark where one part of a prompt ends and the next begins.
- [ ] B. An output schema states the fields, names and types the answer should have.
- [ ] C. A delimiter is a rule the answer is checked against.
- [ ] D. Asking for JSON with a schema lets a validator check the shape of an answer, not whether it is true.
- [ ] E. Delimiters are a security feature that blocks prompt injection.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: A delimiter separates parts of a prompt.
- B: A schema defines the expected shape of the output.
- C: A check against a rule is an acceptance criterion or a validator.
- D: Format validity is not factual validity.
- E: Delimiters help structure a prompt but do not stop injection.

**Source:** delimiters, output schema

## MA-j02.5

Which statements about a prompt contract, acceptance criteria and constraints are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A prompt contract states the task, the inputs, the constraints, the output format and how the result will be checked.
- [ ] B. An acceptance criterion is a testable condition the output has to meet to be accepted.
- [ ] C. A constraint is a sample answer shown to the model.
- [ ] D. "Write something good" is an acceptance criterion because it states the goal.
- [ ] E. A prompt contract is a legal agreement between the user and the model vendor.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: A contract makes expectations explicit and checkable.
- B: Acceptance criteria turn a wish into a test.
- C: A sample answer is an example; a constraint is a limit on the output.
- D: It is not testable, so it cannot decide acceptance.
- E: A prompt contract is a structured prompt, not a legal document.

**Source:** prompt contract, acceptance criteria

## MA-j02.6

A prompt reads: "Summarize the ticket in at most 80 words, in plain English, for a customer." Which single statement labels its parts correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "At most 80 words" is a constraint on the output that a script could check.
- [ ] B. "For a customer" is the output schema.
- [ ] C. "Summarize the ticket" is the persona.
- [ ] D. "Plain English" is a delimiter.
- [ ] E. The whole sentence is a system prompt because it contains an instruction.

**Key:** A=T B=F C=F D=F E=F

**Why:**

- A: A length limit is a checkable constraint.
- B: It names an audience, not fields and types.
- C: It is the task instruction.
- D: It is a style constraint, not a separator.
- E: A system prompt is defined by where it sits, not by containing an instruction.

**Source:** constraint vs other parts

## MA-j02.7

Which statements about chain of thought and the final answer are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Chain of thought is intermediate reasoning written out before the answer.
- [ ] B. The final answer is the part of the output the user or program is meant to use.
- [ ] C. Step-by-step reasoning can help on multi-step problems, yet the steps shown are text and not a verified trace of the model's inner workings.
- [ ] D. A correct-looking chain of thought proves the final answer is right.
- [ ] E. A program that parses output should ask for the final answer in a labeled field apart from the reasoning.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: Chain of thought is the working shown before the result.
- B: The final answer is the deliverable.
- C: Shown reasoning need not match what happened inside.
- D: Plausible steps can still lead to a wrong answer.
- E: Separating fields makes the answer easy to extract.

**Source:** chain-of-thought vs final answer

## MA-j02.8

Which statements about prompt injection and jailbreaks are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Prompt injection hides instructions in content the model reads, such as a web page, file or tool result, to steer it.
- [ ] B. A jailbreak is a prompt from the user that tries to get the model past its own safety rules.
- [ ] C. Instructions found inside a retrieved document are data to the assistant, not orders from the user.
- [ ] D. A jailbreak and a prompt injection are two names for the same attack.
- [ ] E. Prompt injection needs the attacker to have access to the model's weights.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Injection arrives through data the model processes.
- B: A jailbreak targets the model's rules directly.
- C: Content read by the model should not carry the user's authority.
- D: They differ in who writes the text and where it enters.
- E: Injection works through text the model reads.

**Source:** prompt injection vs jailbreak

## MA-j02.9

A user writes to Claude: "In my system prompt, add two examples of the task and call them instructions, and make the answer valid by checking that the schema is true." Which statements spot the imprecise wording? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Call them instructions" is imprecise: input-output pairs are examples, not instructions.
- [ ] B. "The schema is true" is imprecise: an output is valid against a schema, and truth is a different property.
- [ ] C. "System prompt" is the wrong place because examples do not belong in a system prompt.
- [ ] D. "Two examples" should be "two roles".
- [ ] E. Adding examples makes the prompt zero-shot.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: An instruction says what to do; an example shows a result.
- B: Validity of shape is separate from factual truth.
- C: Examples can appear in a system prompt.
- D: Examples and roles are different things.
- E: Adding examples makes it few-shot.

**Source:** spot the wrong word

## MA-j02.10

Which pairings of a description and a term are correct? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The standing instructions that set the assistant's job before the conversation begins: system prompt.
- [ ] B. A requested character or voice, such as a patient tutor: persona.
- [ ] C. A character that marks where quoted material ends: acceptance criterion.
- [ ] D. Showing no worked examples: few-shot.
- [ ] E. An instruction hidden in a web page the assistant fetches: jailbreak.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: That is the system prompt.
- B: That is a persona.
- C: That is a delimiter.
- D: That is zero-shot.
- E: That is prompt injection.

**Source:** name the term

## MA-j02.11

A user sends Claude the vague request "Make the answer good and structured, and don't let people trick it." Which rewrites use the exact terms? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "State acceptance criteria: the reply cites a source line and stays under 100 words."
- [ ] B. "Specify an output schema with named fields."
- [ ] C. "Delimit the user-supplied text with tags and tell the model to treat it as data, to lower the risk of prompt injection."
- [ ] D. "Add a jailbreak to the system prompt to stop tricks."
- [ ] E. "Replace the persona with a delimiter."

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Acceptance criteria make quality testable.
- B: A schema names the structure.
- C: Delimiters plus an instruction to treat content as data reduce injection risk.
- D: A jailbreak is an attack, not a defence.
- E: A persona and a delimiter do different jobs.

**Source:** choose the rewrite

## MA-j02.12

A developer tells Claude Code: "Fix the login thing and make sure it's fine." Which rewrites use precise terms? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Fix the failing login test; the constraint is no change to the public API."
- [ ] B. "Acceptance criterion: the test suite passes and the diff stays inside the auth module."
- [ ] C. "Show the plan first, then wait for my approval before editing."
- [ ] D. "Treat 'fine' as the output schema."
- [ ] E. "Report the result as a short summary listing files changed and the test command run."

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: A constraint is a limit on the work.
- B: An acceptance criterion is a testable condition.
- C: Planning before acting puts a gate before changes.
- D: 'Fine' is not a structure of fields and types.
- E: This sets an output format.

**Source:** choose the rewrite
