# Case 08: "Read-only", says the server

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Keiko leads security at a research lab. A teammate wants to connect a third-party MCP server called `notes-search` to the Claude host on every staff laptop. Keiko's rule is that only servers that cannot change files may be connected, and she will approve based on your review. You asked Claude to review the server.

### The instruction (what you sent)
> Review the MCP server `notes-search` against our four questions (protocol, capability, permission, evidence). Give me a decision: is it read-only and safe to connect to staff laptops?

### Agent output
```
REVIEW OF notes-search
PROTOCOL   initialize handshake succeeded; tools/list returned 3 tools.
CAPABILITY search_notes, get_note, export_notes.
           Annotations on all three tools: readOnlyHint=true,
           destructiveHint=false.
           Descriptions: "Searches notes. Read-only; never modifies files."
PERMISSION not requested.
EVIDENCE   Annotations and descriptions agree on every tool.

CONCLUSION
The server is read-only and safe to connect to staff laptops.
DECISION: approve. Items not examined: none.
```

### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's conclusion, and what is the exact term for the kind of evidence it relied on?
2. **(2 pts)** What single check would show whether `export_notes` can change files?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Keiko why "the server says it is read-only" is not enough.

---

## TA RUBRIC PAGE (do not hand to students)

### Fixed rubric
| Category | Points | Probe |
|---|---:|---|
| Catches the flaw | 3 | Q1 |
| Exact term | 2 | Q1 |
| Asks for evidence | 2 | Q2 |
| Fix or next step | 2 | Q3 |
| Scope and plain language | 1 | Q4 |

### Case key
**The flaw:** the only evidence is what the server advertises about itself: annotations (readOnlyHint) are advisory metadata, and tool descriptions are the server's claim; neither was inspected or executed, and nothing is enforced outside the model.

**Full-credit terms (2):** advertised evidence (vs source-inspected or executed); annotation is advisory / not enforced; tool description is a claim, not evidence; enforcement outside the model (host allow-list or sandbox); uninspected as the honest label.
**Half-credit (1):** "trusting the server"; "self-reported"; "tool poisoning" (only if tied to descriptions as unverified text); "discovery is not permission".
**Zero:** "protocol version", "JSON-RPC error", "stdio" alone.

**Acceptable evidence requests (any two count):**
- Read the handler source for each tool, or run each tool in a sandbox against a test folder and compare the files before and after (executed evidence).
- Have the host enforce a read-only filesystem or allow-list, so the claim does not need to be trusted.
- Replace "Items not examined: none" with an explicit uninspected list (e.g. export_notes behaviour, network use, versions).

**Unacceptable:** "re-read the descriptions"; "ask the server whether it is read-only"; "ask the agent whether it is sure".

**Traps:**
- Students may fix the missing PERMISSION line and miss the evidence-type issue; credit PERMISSION as Catch 1 at most.
- "Items not examined: none" is itself an overclaim; credit students who flag it.
- `export_notes` is the tool most likely to write; its name is a cue, not proof.

**CAP RULE:** flaw missed (no statement that annotations/descriptions are the server's own advisory claims) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. Every piece of evidence is advertised by the server: readOnlyHint is advisory and not enforced, and the description is a claim. Nothing was inspected or executed, yet the review says "items not examined: none". 2. Run export_notes in a sandbox with a test folder and diff the files before and after, or read its source. 3. "Label each finding advertised, source-inspected, or executed; list export_notes as uninspected until run; recommend a host allow-list and read-only mount." 4. "A server can describe itself however it likes, so we need to test it. Until we do, we cannot call it read-only."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 is plain but states a firm conclusion ("cannot call it read-only") stronger than the evidence, so scope is docked.

**Typical (6/10).**
> 1. The agent only trusted what the server says about itself. 2. Test export_notes to see if it changes anything. 3. Tell the agent to test the tools, not just read the labels. 4. The server could say anything.

Score: C3 T1 E1 F1 P0 = **6**. Reason: sees the self-report problem (C3); no term such as advertised/advisory (T1); "test it" with no method (E1); correction is partial (F1); Q4 is plain but one sentence and no consequence (0).

**Fluent-but-wrong (3/10).**
> 1. The agent skipped the permission question, and a tool poisoning attack could hide instructions in the description; the server needs OAuth and a stdio vs HTTP review. 2. Check whether the transport is stdio or HTTP. 3. "Add a permission section and review the transport and JSON-RPC error codes." 4. The server might be attacked.

Score: C0 T1 E0 F1 P1 = **3**. Reason: lists real MCP topics but never questions that the read-only claim is unverified (flaw missed); "tool poisoning" is a near-miss; transport has no bearing on whether tools write; correction is partly relevant; Q4 is plain.
