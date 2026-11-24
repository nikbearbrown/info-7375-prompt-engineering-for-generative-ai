# ProductLens AI: project film narration (approved)

Source: Aditya's `06-Narration-and-Storyboard.md` (Nov 2026). The storyboard is unchanged. Narration edits by Claude Code
for **length** (the original is 904 words, about 6:05 at a natural narrator pace; the target is about 5:00), **tense**
(nothing is built yet, so the system is described as designed and planned), and **verified wording** about other tools.
Approved by Aditya on 2026-11-23; resources in Scene 08 marked pending at his instruction.

---

## 01 · Executive summary

### Scene 01: The problem
Every successful product starts with an idea. But having a good idea and knowing whether it's worth building are two very different things. Before committing resources, product teams need to understand their customers, evaluate competitors, identify risks, and challenge their assumptions. That can take days, and important questions can still go unanswered. What if this process could be more structured, and more evidence-driven?

### Scene 02: Introducing ProductLens AI
That's the problem I'm working on with ProductLens AI, a product research and decision-support platform I'm building for product managers, founders, and business analysts. It will take a product idea or a proposed feature and turn it into a structured assessment: competitors, customer pain points, potential failure scenarios, and ways to validate it. The goal isn't to replace product managers. It's to help them make better-informed decisions before investing time and money in building.

## 02 · Introduction

### Scene 03: What already exists?
Several tools already help with parts of this. General-purpose AI assistants like ChatGPT and Claude can help brainstorm and analyze product ideas. Perplexity answers questions with cited sources. And Productboard helps teams centralize customer feedback and align on priorities. Each one covers a valuable part of the product management process.

### Scene 04: The opportunity
But connecting these activities into one structured assessment still takes a lot of manual work. ProductLens AI explores whether research, competitive analysis, failure analysis, and validation planning can be combined into one coordinated workflow: one that questions assumptions, links claims to evidence, and turns risks into measurable experiments. Whether that actually produces better results is something I'll test as part of the project.

## 03 · Methods

### Scene 05: Starting with a product idea
Here's how it's designed to work. A user enters a product idea, its audience, and some business context. For example: an AI-powered personal finance app for international students in the United States. ProductLens AI will define the research scope and hand it to a team of specialized AI agents, each responsible for one part of the analysis.

### Scene 06: Research and specialized agents
It starts by collecting information from public sources: official product websites, documentation, customer reviews, and industry publications. An orchestrator then coordinates three specialized agents. The Market and Competition Agent examines existing solutions and room for differentiation. The Customer and Adoption Agent looks at user needs, pain points, and barriers to adoption. The Failure and Risk Agent works out how the product could fail, which assumptions are critical, and how to reduce those risks. Each agent has its own system prompt, a defined role, and a structured output format, so one large research problem becomes several focused tasks.

### Scene 07: Verification and self-evaluation
A convincing AI answer isn't necessarily an accurate one. So ProductLens AI adds a dedicated evaluation stage. An Evaluator Agent reviews the findings for unsupported claims, inconsistencies, missing evidence, and recommendations too vague to act on. When it finds an issue, that finding is revised and checked again. And every claim is labelled either supported by evidence, or a hypothesis that still needs validation, so uncertainty becomes an explicit part of the result.

### Scene 08: Technology, resources and final output
The proposed application uses a modern web stack, large language models, structured prompts, and an orchestration layer that manages each stage. Building it needs model API access, token credits, research access, and somewhere to run it. Those are still being confirmed. Token use, cost, and processing time will be tracked throughout. The final deliverable is a Product Decision Brief: competitive insights, customer pain points, ranked failure risks, recommended experiments, and measurable success criteria, each linked to its evidence.

## 04 · Evaluation

### Scene 09: Experimental design
To find out whether ProductLens AI actually adds value, I'll test it on ten standardized product scenarios from different industries, each run three ways. A: a single-prompt baseline. B: the multi-agent workflow without the evaluator. And C: the complete ProductLens workflow, with evaluation and revision. The model, the inputs, and the evidence stay the same, so I can see whether specialization and self-evaluation make a measurable difference.

### Scene 10: Evaluation metrics
I'll measure several things. Factual grounding: are claims actually supported by their cited sources? Relevance: are the risks and customer problems specific to this product? Actionability: can the recommended experiments really be run and measured? I'll also plant deliberate errors to see whether the evaluator catches them, and check that the structured outputs are valid. Finally, I'll compare token use, response time, and cost per report, to see what the extra complexity costs.

### Scene 11: Defining success and failure
The project succeeds if the complete workflow consistently produces more grounded, relevant, and actionable assessments than the baseline, at an acceptable cost. If the extra agents and evaluation don't make a meaningful difference, or cost too much, that's an important finding too. The goal isn't to prove that a multi-agent system works. It's to find out whether it's worth using.

## Closing

### Scene 12: Final message
With ProductLens AI, I'm exploring how prompt engineering and agentic AI can move beyond generating content to support real product decisions. Because building the right product starts with understanding the right problems, questioning our assumptions, and validating before we build.

---

## What changed, and why
| Scene | Change | Why |
|---|---|---|
| All | ~904 → ~800 words | Runtime: ~6:05 → about 5:05 (with a slightly brisker voice setting, 1.08×) |
| 01 | Dropped "faster" | A speed claim with no evidence yet; kept "structured" and "evidence-driven" |
| 02 | "is an intelligent… platform" → "a … platform I'm building"; "takes" → "will take" | Nothing is built yet (honesty rule: past and present tense only for what exists) |
| 03 | Perplexity: "answers questions with cited sources". Productboard: "centralize customer feedback and align on priorities" | Matches each company's own wording (Perplexity help center and blog; productboard.com, read Nov 23). The original "prioritize features" isn't how Productboard puts it. |
| 05 | Adds "Here's how it's designed to work." | One line frames the whole Methods section as the planned design, so its present tense stays honest |
| 07 | "can be revised" → "is revised and checked again" | Matches the docs' one bounded revision; still no claim the evaluator guarantees accuracy |
| 08 | "Those are still being confirmed." | Aditya's instruction: resources pending. The docs say to state confirmed resources or mark them pending. |
| 09 | "examine whether specialization… contribute" kept as "see whether… make a measurable difference" | Your evaluation doc warns that gains may come from extra compute, so the film doesn't promise attribution |
| 12 | "content generation" → "generating content" | Smoother spoken rhythm; meaning unchanged |

## Production notes (from the storyboard)
- **"Actual application screenshots / screen recording":** no app exists yet, so these are concept UIs, labelled **Concept · planned, not built**.
- **Logos (Scene 03):** shown as name cards, not logos. Trademarks aren't ours to reuse without permission, and names are enough.
- **"Actual logo":** there's no ProductLens logo, so the closing uses a wordmark with the storyboard tagline **"Validate before you build."**
- **Music:** none. The brief allows music only if licensed or original, and I don't have a licensed track, so the film ends on silence.
