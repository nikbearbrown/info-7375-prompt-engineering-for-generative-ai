# Flip checks: the sentence that would change his label (chapter 7)

After LABELS.md was frozen (commit `1608a04`) and the checker's labels were opened, Claude Code looked in each
disagreeing posting for the sentence that bears most directly on the claim, and Aravind said whether it changed his
label (2026-11-22, about 3:05 AM ET). LABELS.md is not edited; `tools/score_claims.py` reports agreement both ways.

| Claim | Frozen label | Checker | The sentence(s) Claude Code found | Label after | His words |
|---|---|---|---|---|---|
| 04.8a | supported | insufficient | Duties: "Define APIs and resource models that let clients request and track lifecycle operations through consistent interfaces across hardware platforms and providers."; "You might design a lifecycle API". Nothing in the posting points the other way. | supported | "04.8a stays" |
| 04.8c | supported | insufficient | Duty: "Design, build, and operate Kubernetes-based controllers and distributed services that coordinate infrastructure across sites, isolate failures, and scale as GPU capacity grows." | supported | "04.8c stays" |
| 05.8d | supported | insufficient | No sentence says the role works on developer tools: the quoted "We design, provision ..." lists developer tools as one of ten things the team connects, and the other mentions are background ("Have built or operated distributed systems, ..., developer tools, or production systems ..."; "You may not be the strongest in ... developer platforms, tooling ..."). | insufficient | "05.8d → I" |
| 09.8c | insufficient | supported | The closest sentence about tools: "Create tooling and infrastructure that enable operations and policy teams to investigate abuse and make fast, consistent, and explainable decisions." (tooling for operations and policy teams). In the quoted sentence, "build systems" is a verb and a noun. | insufficient | "09.8c stays" |
