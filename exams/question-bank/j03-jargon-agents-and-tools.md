# Jargon test: agents and tools

## MA-j03.1

Which statements tell chat, assistant and agent apart? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A chat is a back-and-forth of messages in which the model returns text.
- [ ] B. An agent can take actions through tools and use the results to decide the next step.
- [ ] C. A system that returns text alone becomes an agent when it uses a larger model.
- [ ] D. An assistant is a chat model given a role and instructions to help with tasks, and it may or may not use tools.
- [ ] E. An agent is a chat with a longer context window.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Chat is message exchange with text output.
- B: Acting and observing is what makes a system an agent.
- C: Agency comes from tools and a loop, not model size.
- D: Assistant describes the helper role, not the ability to act.
- E: Context length does not give a system the ability to act.

**Source:** chat vs assistant vs agent

## MA-j03.2

Which statements tell an agent loop and a workflow apart? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. In an agent loop the model chooses the next step based on what it observes.
- [ ] B. A workflow follows steps fixed in advance by code, though a step may call a model.
- [ ] C. A workflow decides at run time which tool to call next.
- [ ] D. An agent loop ends when the model runs out of tokens in a single reply.
- [ ] E. A workflow and an agent loop are the same because both call a model more than once.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: The path is decided at run time.
- B: A workflow has a predetermined path.
- C: That is the agent loop; a workflow's path is fixed.
- D: The loop ends at a stop condition, not at one reply's length.
- E: Who chooses the next step differs.

**Source:** agent loop vs workflow

## MA-j03.3

Which statements about a tool definition and a tool schema are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A tool definition gives the model a tool's name, a description and the parameters it takes.
- [ ] B. A tool schema describes the shape of the arguments, such as field names and types.
- [ ] C. The model runs the tool itself inside its weights.
- [ ] D. The description is text the model reads when deciding whether to call the tool.
- [ ] E. A clear tool description helps the model pick the right tool and fill in arguments.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: The definition tells the model what the tool is.
- B: The schema constrains the call's arguments.
- C: A program outside the model runs the tool.
- D: Descriptions steer tool choice.
- E: Precise descriptions improve calls.

**Source:** tool definition, tool schema

## MA-j03.4

Which statements tell tool_use and tool_result apart? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. tool_use is the model's request to call a named tool with arguments.
- [ ] B. tool_result is what the program sends back after running the tool.
- [ ] C. tool_result is written by the model before the tool runs.
- [ ] D. tool_use means the tool has already finished.
- [ ] E. tool_use and tool_result are two names for a single message.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: It is the proposal to act.
- B: It carries the outcome to the model.
- C: The result comes from running the tool.
- D: tool_use is a request; finishing produces a result.
- E: They are separate messages in opposite directions.

**Source:** tool_use vs tool_result

## MA-j03.5

Which statements about permissions and sandboxes are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A permission says whether the agent may use a tool or take an action, often as allow, ask or deny.
- [ ] B. A sandbox is a restricted environment where actions run with limited access to files, network or system.
- [ ] C. A sandbox makes a tool call correct.
- [ ] D. A permission rule is enforced by the host program around the model, not by the model's goodwill.
- [ ] E. Sandbox and permission mean the same thing: both are a list of allowed commands.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: A permission governs what is allowed.
- B: A sandbox limits the reach of an action.
- C: A sandbox limits damage but does not check correctness.
- D: Enforcement sits in the controller or host.
- E: One restricts the environment; the other is a rule about actions.

**Source:** permission vs sandbox

## MA-j03.6

Which single statement about observation, stop condition and step budget is true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An observation is the agent's plan for the next step.
- [ ] B. A step budget is the largest number of tokens in one reply.
- [ ] C. A stop condition is a rule that ends the loop, such as the goal being met, an error, or the step budget being reached.
- [ ] D. A step budget lets the agent keep looping with no limit.
- [ ] E. An observation is the model's final answer.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: An observation is a result coming back, not a plan.
- B: A step budget caps loop steps, not reply length.
- C: A stop condition defines when the loop halts.
- D: The budget is the limit.
- E: An observation is what the controller feeds back after an action.

**Source:** observation, stop condition, step budget

## MA-j03.7

Which statements about orchestrators and subagents are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An orchestrator assigns work to other agents and combines what comes back.
- [ ] B. A subagent is an agent given a narrower task by another agent, often with its own context.
- [ ] C. A subagent is a smaller model with fewer parameters.
- [ ] D. The orchestrator is the permission rule that approves tools.
- [ ] E. Handing work to a subagent hands off responsibility for the result.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: The orchestrator coordinates.
- B: A subagent works on a delegated piece.
- C: Subagent describes the role, not the model size.
- D: A permission rule is not an orchestrator.
- E: The delegator still owns checking the outcome.

**Source:** orchestrator vs subagent

## MA-j03.8

An agent runs the test suite, the output reports two failures, and the agent then edits a file. Which statements name the parts correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The test output is the observation.
- [ ] B. The decision to edit the file is the model's next proposed action.
- [ ] C. The program that runs the tests and passes the output back is the controller.
- [ ] D. The edit is the observation.
- [ ] E. The test run is the stop condition.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: An observation is the result fed back to the model.
- B: The model proposes; the controller runs.
- C: The controller executes actions and feeds back results.
- D: The edit is an action; its result would be the next observation.
- E: A stop condition ends the loop; a test run does not by itself.

**Source:** observation, controller

## MA-j03.9

Which pairings of a description and a term are correct? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The maximum number of steps the loop may take: step budget.
- [ ] B. The result of an action returned to the model: observation.
- [ ] C. The program around the model that runs tools and feeds back results: controller.
- [ ] D. A fixed pipeline of steps set in code: agent loop.
- [ ] E. A restricted environment where commands run: sandbox.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: A step budget caps loop steps.
- B: Observation is the feedback from acting.
- C: The controller turns proposals into actions.
- D: That is a workflow.
- E: A sandbox limits access.

**Source:** name the term

## MA-j03.10

A student writes to Claude Code: "Make an agent for my repo. It should be a workflow where it decides for itself which tool to use, give it unlimited permission, and run in my real home folder." Which statements spot the imprecise wording? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Workflow" conflicts with "decides for itself"; a loop in which the model chooses is an agent loop.
- [ ] B. "Unlimited permission" is imprecise and risky; name the tools and set allow, ask or deny.
- [ ] C. "Real home folder" suggests running outside a sandbox; a sandbox or limited project folder is the safer term.
- [ ] D. "Tool" is the wrong word; it should be "subagent".
- [ ] E. "Repo" should be "orchestrator".

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Fixed paths are workflows; model-chosen paths are agent loops.
- B: Permissions should be stated per tool or action.
- C: A sandbox restricts reach.
- D: Tool is correct for a callable capability.
- E: A repo is a code repository, not a coordinating agent.

**Source:** spot the wrong word

## MA-j03.11

A user tells Claude: "Go fix everything and keep going till it works." Which rewrites use the exact terms? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Run the failing tests, keep edits inside the src folder, and stop after a fixed number of steps or when the tests pass."
- [ ] B. "Ask me before running a command that deletes files."
- [ ] C. "Set the temperature to zero so the loop ends sooner."
- [ ] D. "Send the tool_result before the tool_use so it is faster."
- [ ] E. "Give the sandbox permission to approve its own steps."

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: This names a scope, a step budget and a stop condition.
- B: An approval gate before a risky action is a permission set to ask.
- C: Temperature does not control when a loop ends.
- D: A result cannot precede the request it answers.
- E: A sandbox does not hold permissions; the host enforces the user's policy.

**Source:** choose the rewrite

## MA-j03.12

A model is given a tool named get_weather with a description and a schema asking for a city as a string. A user asks about the weather in one city. Which statements describe what happens? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The model replies with a tool_use naming get_weather and a city argument.
- [ ] B. The program runs the function and returns a tool_result.
- [ ] C. The model reads the tool_result and writes the final answer.
- [ ] D. The schema is what contains the live temperature.
- [ ] E. If the model puts a number where the schema asks for a string city, the call does not match the schema.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: The model proposes the call.
- B: The controller executes and reports back.
- C: The loop returns to the model with an observation.
- D: The schema describes arguments; the temperature comes in the result.
- E: A schema defines types that arguments are checked against.

**Source:** tool call sequence
