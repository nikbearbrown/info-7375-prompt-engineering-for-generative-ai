# Book vision — Prompt Engineering for Generative AI

Status: proposed AI+1 Blueprint, Vision step; awaiting Nik Bear Brown's approval. No research, drafting, image, or publication gate is signed.

## The book in one sentence

Take a Claude workflow apart in plain Python, explain what each piece does, and judge which decisions make its output worth trusting.

## Reader and promise

This is the optional reading companion to INFO 7375 for a programmer who wants the explanation behind the exercises, not another checklist of commands. Public readers are welcome and need their own Claude Code access for hands-on work. Students have NEU access. The book should also be readable without running the examples.

By the end, a reader should be able to trace a bounded agent from request to action to evidence, implement its small mechanisms, explain their limitations, and decide where human judgment or authorization must intervene. Claude-only model use and Python-only teaching implementations remain the course boundary. Offline mechanisms precede optional, explicit direct API calls; a Claude Code account is not an API-credit entitlement.

## Form and voice

Fifteen substantial chapters in chapters/, numbered and slugged exactly like the fifteen lessons. This is a narrative companion, not a copy of the lesson instructions with connecting sentences added. Proposed depth: the Teardown /write range of 5,000–8,000 words per chapter, earned through worked examples and explanation rather than padding.

Use ai1-cli/voices/teardown/VOICE.md as the voice source: begin with a concrete problem; expose actual machinery; explain what the design optimizes for and sacrifices; work through a checkable example; return to the opening problem with a more defensible judgment. Narrative momentum comes from inspecting the system, not invented people or classroom anecdotes. Clearly label hypothetical situations. First-person authorial choices must reflect supplied course choices; do not invent Bear's memories, experiments, or opinions.

Each chapter builds toward the matching lesson's capability. Keep short objectives and graduated ungraded Assessments, but let explanatory prose carry the chapter. Link to the runnable lesson instead of duplicating long reference files. Preserve selective Anthropics, Computational Skepticism, Conducting AI, and Irreducibly Human connections only where relevant and sourced. Human/AI responsibility remains explicit where it matters.

## One-to-one scope constraint

The following is the existing course map, not a signed new outline. Architecture and detailed chapter specifications follow Vision approval.

| Chapter / lesson | Subject | Teardown question |
|---|---|---|
| 01 | Randomness and first prompts | What changes when we change a sampling distribution—and what does not? |
| 02 | Prompt contracts and evaluation | Why can an answer satisfy a format contract and still be wrong? |
| 03 | Chat, assistant, and agent | When does a response become an action with consequences? |
| 04 | The agent loop | Who actually runs the loop, and what makes it stop? |
| 05 | Tools, permissions, and boundaries | Why is an available tool not an authorized action? |
| 06 | Claude Code and evidence-based diff review | What would make this patch deserve approval? |
| 07 | Context retrieval and Claude Cowork | What does the retrieval mechanism leave outside the answer? |
| 08 | MCP from scratch | What does a shared protocol standardize, and what does it leave untrusted? |
| 09 | Training mechanics and Claude configuration | Which changes update parameters, and which only change the input? |
| 10 | Planning before acting | What must a plan specify before it can constrain action? |
| 11 | Claude tool use and verification | What bridges a requested tool call and a verified result? |
| 12 | Memory and multiple agents | When does shared context preserve a mistake instead of correcting it? |
| 13 | Evaluation and human approval gates | What evidence is sufficient for this particular decision? |
| 14 | Team governance and applied ethics | Who owns the decision when several people and tools contribute? |
| 15 | Supervised agentic capstone | What separates a working demonstration from a responsible handoff? |

## Comparison with local book examples

These are editorial comparisons from inspected excerpts, not endorsements of their factual claims.

- AI1 CLI, Chapter Specifications: artifact-first learning, worked examples, and explicit bridges. Borrow the capability-led structure; this book explains Claude/Python mechanisms rather than teaching book production.
- Trust the Teacher, chapter 1: a sustained opening tension followed by distinctions and evidence. Borrow that explanatory momentum, not its policy claims or reported statistics; the excerpt contains unresolved fact-check flags.
- The Reallocation Engine, chapter 1, The Fluency Trap: execution versus judgment gives a useful model of conceptual tension. Borrow the discipline of separating terms, not its scenarios or empirical claims without source review.

## Cajal figures and EPUB intent

Use the requested Cajal workflow to identify figures that clarify a mechanism, boundary, comparison, or failure. Full Cajal instructions and the target visual-design rules must be read before figure production; inspected examples are not an approved style specification. Record sources, figure scope, exclusions, captions, and alt text. Do not manufacture observations for charts. Review layout and substantive accuracy separately; test grayscale legibility for e-readers.

Target a reflowable EPUB3 suitable for Kindle review, with navigation, readable code, citations, and embedded static figure assets. The inspected ai1-cli/build.sh uses Pandoc, metadata.yaml, chapters/*.md, cover.jpg, and two Kindle CSS files. Pandoc is locally available. Build integration, cover, styles, figure paths, and device/preview validation still need implementation after the appropriate gates. Do not label a built ZIP as Kindle-validated without preview evidence. No KDP upload is requested.

## Boundaries

NEU grading and account logistics remain in prerequisites/, not the book proper. Assessments are ungraded. The 10-day, 100-point Assignment structure stays separate. Videos are optional and have no separate points. No new quiz bank, Canvas export, website, paid image service, API expenditure, or public publishing is inferred from this book request.

## Approval requested

Approve or revise this reader, promise, narrative depth, and one-to-one scope. AI+1's Blueprint recipe pauses after Vision before Architecture. Approval of this document is not approval of an unwritten manuscript, research, images, or final EPUB.
