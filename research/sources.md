# Primary-source register

Accessed 2026-09-06. These are narrow source-to-claim mappings, not endorsements of every statement on a page. Rolling product documentation is not a permanent version guarantee.

| Source | Supported use | Chapters |
| --- | --- | --- |
| [Python random](https://docs.python.org/3/library/random.html) | Weighted sampling and local seeded generators; not reproducibility across every Python release. | 1 |
| [Building effective agents — Anthropic, 2024-12-19](https://www.anthropic.com/engineering/building-effective-agents) | Distinguish predefined workflows from model-directed agent processes; do not equate the article's taxonomy with the course classifier. | 3, 4 |
| [Claude Code permissions](https://code.claude.com/docs/en/permissions) | Runtime permission rules control tool actions; prompt requests alone are not enforced access controls. | 5 |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | Give work executable checks and separate exploration/planning from implementation when appropriate. | 6, 10 |
| [Introduction to Information Retrieval — dot products, 2008](https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html) | Cosine is normalized dot product; the course's token overlap remains a deliberately limited retrieval model. | 7 |
| [Effective context engineering — Anthropic, 2025-09-29](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Context selection and retrieval are engineering choices. The course does not reproduce Claude Cowork internals. | 7, 12 |
| [MCP lifecycle — specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle) | Initialization, capability exchange, initialized notification, and supported-version fallback. Fallback alone is not nonconformance. | 8 |
| [Jurafsky and Martin, Logistic Regression, September 2021 draft](https://web.stanford.edu/~jurafsky/slp3/old_sep21/5.pdf) | Logistic regression maps a weighted input through a sigmoid. This packet additionally checks the toy gradient numerically. | 9 |
| [Handle tool calls — Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) | Client tools use tool_use identifiers and matching tool_result blocks; runtime execution is separate from the model's request. | 11 |
| [Python pathlib](https://docs.python.org/3/library/pathlib.html) | Path.resolve resolves symlinks and removes parent components; it is not by itself a race-proof authorization boundary. | 5 |

For chapters 2, 13, 14, and 15, the worked counterexamples are supported directly by local source and execution, not by invented empirical studies. Chapter 12's freshness result is likewise a local sequential experiment, not a claim about concurrent production systems.

## Companion-source restraint

Read passages on calibration versus confidence (Computational Skepticism chapter 2), testable handoffs (chapter 9), audit-first review (Conducting AI chapter 5), distinct acceptance criteria (chapter 7), and foundational practice before offloading (Irreducibly Human chapter 1). Attribute these as author frameworks through the repository's companion guides. Do not turn their philosophical or empirical assertions into established facts without independent evidence.

The Conducting AI distinctness discussion contains wording that can be overread: two criteria can both be satisfied by one solution and still be distinct. Prefer the operational counterexample test—an outcome can pass one and fail the other—over claiming shared satisfaction makes criteria identical.

Every Irreducibly Human note must separately name what “AI should” and “Human should” do. Human approval, consent, interpretation, and authorship must never be supplied by a simulated reviewer.

