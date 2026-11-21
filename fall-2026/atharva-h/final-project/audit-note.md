# Audit note

Packet document 9 of 10. Previous: [artifact.md](artifact.md) · Next: [transfer-reflection.md](transfer-reflection.md)

## 1. Predictions before the critique

Written 2026-11-21, before the reviewer saw anything. Kept unedited.

What I expect an independent code-and-evidence reviewer to find:
1. **The text check is regex-based and can be fooled.** For example, identifiers in double quotes or unusual whitespace. I expect this to be a real but contained finding, because the authorizer and the read-only connection are separate layers behind it.
2. **The recorded adapter weakens the "agentic" claim.** The model step was not live inside the loop; replies were obtained from a Claude subagent and replayed. I expect this to be called genuine.
3. **The count-versus-rows check is not independent.** Both queries come from the same model reply, so a consistent mistake passes it. I expect this to be genuine.
4. **The answer key and the agent were both built with Claude.** Independence rests on separate code paths (Python counting versus model SQL), not on separate people. I expect this to be genuine, and it's the main limit of the evaluation.
5. **Small samples.** 10 development and 5 held-out questions can't support a general accuracy claim.

## 2. The reviewer's findings

*To be filled in from the review run (see section 4). Each finding is judged genuine or a false positive. The owner confirms or overrides those judgments.*

## 3. Failed cases

*To be filled in from `evals/results/`.*

## 4. Gap Account

*What a reviewer of that kind could never reach. To be written after the review.*
