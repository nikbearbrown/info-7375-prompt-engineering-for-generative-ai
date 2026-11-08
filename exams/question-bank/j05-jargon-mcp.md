# Jargon test: MCP

## MA-j05.1

A desktop AI assistant (the app a person types into) connects to a small program that offers file-reading tools, using the Model Context Protocol. Name the parts. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The server is the program that exposes tools, resources or prompts.
- [ ] B. The host is the AI application the person runs, and it creates a client for each server connection.
- [ ] C. The client keeps the connection to one server on the host's behalf.
- [ ] D. The host is the remote machine on which the server happens to run.
- [ ] E. The client is the program that offers tools and data to the host.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: A server is the provider side of the connection.
- B: The host is the application that contains the model interface and manages the connections.
- C: Each client is the host's connector to a single server.
- D: Host names the AI application, not a machine.
- E: Offering tools and data is the server's job, not the client's.

**Source:** host, client, server

## MA-j05.2

A student writes in a bug report: "my MCP client lists three tools." Decide which statements use the terms correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The client is built by whoever writes the tools.
- [ ] B. Writing a tool function in Python turns that program into an MCP client.
- [ ] C. A client asks a server for its tools with a tools/list request, and the server's answer names them.
- [ ] D. The server decides which tool the model will call and sends that choice to the client.
- [ ] E. The client and the server are two roles in one connection, and a single application can contain a client without being a server.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: The author of the tools writes the server; the host application supplies the client.
- B: A program that offers tools is acting as a server.
- C: tools/list is how discovery works: the client asks, the server answers.
- D: The model chooses the tool; the client carries the call to the server.
- E: MCP names roles, so the same program is not both by default.

**Source:** MCP server vs MCP client

## MA-j05.3

An MCP connection needs a transport. Decide which statements about transports are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The stdio transport is the usual choice for a server on another machine reached over the internet.
- [ ] B. A transport is the channel that carries the messages; it is separate from the messages themselves.
- [ ] C. With the stdio transport, the client starts the server as a local child process and exchanges messages over its standard input and output.
- [ ] D. An HTTP transport suits a server that runs remotely and is reached over a network.
- [ ] E. Both stdio and HTTP carry JSON-RPC messages.

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: Remote servers use an HTTP transport; stdio is for local processes.
- B: Transport is the pipe, JSON-RPC is the content.
- C: stdio is the local-process channel.
- D: HTTP carries the same messages across a network.
- E: Changing transport does not change the message format.

**Source:** transport: stdio vs HTTP

## MA-j05.4

MCP messages use JSON-RPC. Decide which statements about request, response and notification are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A request carries an id, and the matching response carries the same id.
- [ ] B. A notification has no id and receives no response.
- [ ] C. A response carries either a result or an error.
- [ ] D. A response carries a fresh id that differs from the request's id.
- [ ] E. A notification is a request whose answer arrives later.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: The id lets the sender pair a response with its request.
- B: Notifications are one-way messages.
- C: These are the two shapes of an answer.
- D: A response repeats the request's id.
- E: A notification is not answered at all.

**Source:** JSON-RPC request, response, notification

## MA-j05.5

A new connection starts with a handshake of two messages named initialize and initialized. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. initialize and initialized are two spellings of the same message.
- [ ] B. A tools/call can be sent before initialized, because the server process is already running.
- [ ] C. initialized is a request that the server sends to ask the client for its tool list.
- [ ] D. initialized is a notification that the client sends after receiving the answer, so it gets no reply.
- [ ] E. initialize is a request from the client, and the server answers with its protocol version and capabilities.

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: They are two different steps: capability exchange, then a readiness signal.
- B: Ordinary requests sent too early are rejected.
- C: initialized is sent by the client, and it is not a request.
- D: It signals that the client is ready for ordinary requests.
- E: It opens the session and exchanges what each side supports.

**Source:** initialize vs initialized

## MA-j05.6

A server offers three kinds of thing to a host. Decide which statements about tools, resources and prompts are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Prompts are controlled by the model, which decides when to apply them.
- [ ] B. A tool is described to the model by a name, a description and an input schema.
- [ ] C. A tool is a function the model decides to call, so tools are model-controlled.
- [ ] D. A resource is data such as a file or a schema that the application chooses to attach as context.
- [ ] E. A prompt is a reusable template that the user picks.

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: Prompts are user-controlled templates, such as ones chosen from a slash menu.
- B: Those three parts are what the model reads when choosing a tool.
- C: The model picks tools during its work.
- D: Resources are application-controlled.
- E: Prompts are user-controlled.

**Source:** tools vs resources vs prompts

## MA-j05.7

A server offers three things: the text of a database schema, an action that runs a query, and a saved weekly-report template the user can pick from a menu. Name the primitive for each. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The weekly-report template is a tool.
- [ ] B. The action that runs a query is a resource.
- [ ] C. The query action is a prompt.
- [ ] D. The database schema text is a resource.
- [ ] E. The schema text is a prompt.

**Key:** A=F B=F C=F D=T E=F

**Why:**

- A: A user-picked template is a prompt.
- B: Running something is a tool.
- C: An action the model calls is a tool, not a template.
- D: Data attached as context is a resource.
- E: A prompt is a template, not reference data.

**Source:** tools vs resources vs prompts

## MA-j05.8

A server lists a tool with the description "Reads a file and returns its text." Decide which statements about the tool description are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Descriptions and input schemas take up space in the context window.
- [ ] B. The client checks that the description is accurate before the model sees it.
- [ ] C. The description is text from the server's author that the model reads when deciding whether to call the tool.
- [ ] D. Misleading description text can steer the model, so it is a claim and not a guarantee.
- [ ] E. The description is the code that runs when the tool is called.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: Each connected tool adds tokens to the context.
- B: A client does not verify descriptions; they are the server's own claim.
- C: It is the main signal the model has about what the tool does.
- D: Because the model reads it, hostile text there can influence behaviour.
- E: The code is the tool's implementation; the description is only text about it.

**Source:** tool description

## MA-j05.9

A tool call comes back with a problem. Decide which statements about a JSON-RPC error and a result with isError true are correct. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A result with isError true means the call ran and the tool reported a failure, such as a file not found.
- [ ] B. A query tool that finds no matching rows reports that by returning a JSON-RPC error.
- [ ] C. A JSON-RPC error means the protocol-level request failed, for example an unknown method or a request sent before initialization.
- [ ] D. isError true tells the host that the connection has dropped.
- [ ] E. isError true tells the host to close the connection and start again.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: The protocol worked; the tool's work did not.
- B: An empty answer is a normal result, not a protocol failure.
- C: It reports a failure of the exchange itself.
- D: A dropped connection is a transport problem, not an isError result.
- E: It is information for the model and host, not a command to disconnect.

**Source:** isError vs protocol error

## MA-j05.10

A team says: "The handshake succeeded, so the server is safe to use on customer data." Decide which statements use interoperability and authorization correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Authorization means two programs can parse each other's messages.
- [ ] B. A successful handshake shows that the server is trustworthy.
- [ ] C. Authorization, meaning whether this server and its tools are allowed in this task, is decided by a person.
- [ ] D. Interoperability is whether a host and a server can exchange messages that both understand.
- [ ] E. MCP's standard message format decides which tools the model may call.

**Key:** A=F B=F C=T D=T E=F

**Why:**

- A: That describes interoperability.
- B: A handshake shows only that the messages work, not that the server should be trusted.
- C: Permission to use a server is a human decision.
- D: MCP standardizes the message exchange.
- E: The format does not set policy; the host enforces the person's rules.

**Source:** interoperability vs authorization

## MA-j05.11

A student sends Claude Code this message: "The MCP thing is broken, it gives an error when I ask for files." Decide which statements correctly name the vague parts or improve the message. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Give the transport, stdio or HTTP, because a connection problem is diagnosed differently for each.
- [ ] B. Say "MCP server" for the program that offers the file tools, instead of "the MCP".
- [ ] C. State whether the failure was a protocol error or a result with isError true, because the two have different causes.
- [ ] D. stdio is the name of the error the student is seeing.
- [ ] E. Say "host" for the program that offers the file tools.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: A local process failure and a network failure differ.
- B: MCP is the protocol; the server is a specific program.
- C: They point to different layers of the problem.
- D: stdio is a transport, not an error.
- E: The host is the AI application; the offering program is the server.

**Source:** naming MCP parts in a prompt

## MA-j05.12

During initialize, a server answers with its capabilities. Decide which statements about capabilities and discovery are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Capability negotiation takes place after the first tools/call.
- [ ] B. Capabilities are what each side declares that it supports during the handshake.
- [ ] C. Discovery means the host downloads the server's source code to read it.
- [ ] D. tools/list runs each tool once to test that it works.
- [ ] E. The tools/list request is how a client discovers tools, including ones that appeared after the model was trained.

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: It happens during initialize, before ordinary requests.
- B: They are exchanged in initialize.
- C: The client learns what is offered through messages, not source code.
- D: It returns descriptions; it does not call the tools.
- E: Discovery is runtime, not memorized.

**Source:** capabilities and discovery

## MA-j05.13

In a connected setup, three parties each make a decision. Decide which statements about who decides what are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The model picks the tool, the arguments and the order of calls.
- [ ] B. A person decides which servers are connected.
- [ ] C. The host enforces which tools are allowed and when to ask the person.
- [ ] D. The MCP server enforces the person's allow list before the host calls it.
- [ ] E. Tool annotations such as readOnlyHint are hints that a host treats as untrusted unless the server is trusted.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: These are the agent's choices.
- B: Connecting a server is a human choice.
- C: Enforcement sits in the host.
- D: The host enforces the person's policy.
- E: Annotations are the server's own claim.

**Source:** who decides: person, model, host

## MA-j05.14

A reader asks how MCP relates to function calling and to REST APIs. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Function calling is how a model asks for a tool, and something else still has to run that tool.
- [ ] B. A REST API is a kind of MCP server.
- [ ] C. MCP replaces REST, so servers do not need web APIs.
- [ ] D. A server can send a notification that its list of tools changed.
- [ ] E. MCP servers often wrap existing APIs.

**Key:** A=T B=F C=F D=T E=T

**Why:**

- A: Calling is the request; execution is separate.
- B: They are different things; REST is a web API style, MCP a protocol.
- C: MCP servers often wrap existing APIs.
- D: Change notifications keep the client current.
- E: The server can translate between the protocol and an existing service.

**Source:** MCP vs function calling vs REST
