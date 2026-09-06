# Book outline — Prompt Engineering for Generative AI

Final proposed Blueprint outline, reconciled to the approved Vision, Architecture, and Chapter Specifications. Awaiting final Blueprint approval. These are planned manuscript paths, not links to finished chapters.

The optional book has exactly fifteen numbered chapters, each matching one lesson. Front matter introduces how to read and use the companion; it does not add a sixteenth lesson or import NEU grading logistics.

## Act I — Inspect answers

1. **Randomness and first prompts** — `chapters/01-randomness-and-first-prompts.md`; [paired lesson](lessons/01-randomness-and-first-prompts/docs/en.md).

2. **Prompt contracts and evaluation** — `chapters/02-prompt-contracts-and-evaluation.md`; [paired lesson](lessons/02-prompt-contracts-and-evaluation/docs/en.md).

3. **Chat, assistant, and agent** — `chapters/03-chat-assistant-agent.md`; [paired lesson](lessons/03-chat-assistant-agent/docs/en.md).

## Act II — Build the machinery

4. **The agent loop** — `chapters/04-the-agent-loop.md`; [paired lesson](lessons/04-the-agent-loop/docs/en.md).

5. **Tools, permissions, and boundaries** — `chapters/05-tools-and-permissions.md`; [paired lesson](lessons/05-tools-and-permissions/docs/en.md).

6. **Claude Code and evidence-based diff review** — `chapters/06-claude-code-and-diff-review.md`; [paired lesson](lessons/06-claude-code-and-diff-review/docs/en.md).

7. **Context retrieval and Claude Cowork** — `chapters/07-context-retrieval-and-cowork.md`; [paired lesson](lessons/07-context-retrieval-and-cowork/docs/en.md).

8. **MCP from scratch** — `chapters/08-mcp-from-scratch.md`; [paired lesson](lessons/08-mcp-from-scratch/docs/en.md).

9. **Training mechanics and Claude configuration** — `chapters/09-training-and-configuration.md`; [paired lesson](lessons/09-training-and-configuration/docs/en.md).

## Act III — Supervise the system

10. **Planning before acting** — `chapters/10-planning-before-acting.md`; [paired lesson](lessons/10-planning-before-acting/docs/en.md).

11. **Claude tool use and verification** — `chapters/11-tool-use-and-verification.md`; [paired lesson](lessons/11-tool-use-and-verification/docs/en.md).

12. **Memory and multiple agents** — `chapters/12-memory-and-multiple-agents.md`; [paired lesson](lessons/12-memory-and-multiple-agents/docs/en.md).

13. **Evaluation and human approval gates** — `chapters/13-evaluation-and-approval-gates.md`; [paired lesson](lessons/13-evaluation-and-approval-gates/docs/en.md).

14. **Team governance and applied ethics** — `chapters/14-team-governance-and-ethics.md`; [paired lesson](lessons/14-team-governance-and-ethics/docs/en.md).

15. **Supervised agentic capstone** — `chapters/15-supervised-capstone.md`; [paired lesson](lessons/15-supervised-capstone/docs/en.md).

## Shared chapter structure

A concrete opening tension; brief objectives and prerequisites; connected first-principles explanations; a fully worked example; design trade-offs and counterexamples; integration; graduated ungraded Assessments; capabilities gained; and a bridge to the next chapter. Candidate figures and individual examples are specified in [chapters-spec.md](chapters-spec.md).

Use the approved narrative Teardown register, with 5,000–8,000 words of substantive explanation per chapter. Keep source notes selective: Anthropics, Computational Skepticism, Conducting AI, and Irreducibly Human only where supported and relevant. Identify actual human responsibilities rather than claiming that a model can supply judgment or consent on someone's behalf.

## Reconciliation and production boundary

The chapter order, titles, and slugs match course.json. The three acts match [architecture.md](architecture.md). The voice and readership match [vision.md](vision.md). Adoption and delivery controls are in [risks.md](risks.md). The existing six-question lesson quizzes remain the knowledge-check companion; no new graded book assessments are introduced.

After final Blueprint approval: research all fifteen chapters from lesson implementations, actual tests, primary documentation, and relevant companion passages; review those sources before drafting. Human rewrite, fact checking, Cajal production and audits precede the final reading build. Use an explicit ordered manuscript list, not chapters/*.md, so the folder README cannot enter the EPUB. No Kindle validation or publication is implied by this outline.
