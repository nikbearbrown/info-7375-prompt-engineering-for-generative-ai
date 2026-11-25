# Prompt Experiment results: judge-dev-v1 on the DEV set

- pass rate: **9 / 10** (judgment verdict equals the hand label)
- disagreements: 1; unavailable judgments: 0
- hand labels: 2 relevant, 8 not relevant
- model(s) served: claude-opus-5-5
- system prompt sha256: 08202bc08926eb694f18bf7ad06c64c299b74bd28202dc40daad914af24329cc

| posting | title | hand label | judgment | match |
|---|---|---|---|---|
| 8773028002 | Intermediate Backend Engineer, Pipeline Authoring | not relevant | not relevant | yes |
| 8730125002 | Senior Release Engineer | not relevant | not relevant | yes |
| 8895511002 | Strategic Account Executive - Chicago | not relevant | not relevant | yes |
| 8891301002 | Backend Engineer (Ruby), Create: Change Record | relevant | not relevant | NO |
| 8806017002 | Director of Product Management, Agentic Software Delivery | relevant | relevant | yes |
| 8623592002 | Principal Site Reliability Engineer, Platform Engineering: Dedicated | not relevant | not relevant | yes |
| 8860127002 | Strategic Account Executive | not relevant | not relevant | yes |
| 8592555002 | Commercial Account Executive, Named - West | not relevant | not relevant | yes |
| 8706202002 | Strategic Account Executive - Seattle | not relevant | not relevant | yes |
| 8731996002 | Senior Solutions Architect | not relevant | not relevant | yes |

## Disagreements

### 8891301002: Backend Engineer (Ruby), Create: Change Record

| | verdict | stated reason |
|---|---|---|
| Om (hand label) | relevant | Builds records tracking what AI agents changed, why, and who or what made each change, plus workflows for developers working with agents. Production agent-building experience is explicitly a bonus. This is specific engineering support for integrating agents into software development. |
| Claude (JUDGMENT, judge-dev-v1) | not relevant | The core duties in posting.content are conventional backend work: "Develop secure, well-tested, performant features and improvements using Ruby on Rails and GraphQL" and "Design and maintain backend services, APIs, data models, and business logic that support intuitive source code workflows." The AI-related items are about using AI tools, which does not count: "Use AI agents for well-scoped work when they can speed up delivery without sacrificing quality" and "Experience using AI coding agents to speed up software development." The product context is recording changes made by agents, not building or operating the agents themselves: "every change needs a clear, trustworthy record of what changed, why, and who or what made it." Building agents appears only as an optional extra: "Bonus: you've built agents or agent-based workflows that run in production." The company-wide statement "we embrace AI as a core productivity multiplier" is general company messaging and does not count. |

