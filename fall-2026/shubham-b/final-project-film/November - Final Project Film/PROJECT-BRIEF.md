# PROJECT-BRIEF — A11yProof (accessibility repair agent)

*This is the project as pitched in the film on 2026-11-23. Nothing is built yet. ("a11y" is developer shorthand for accessibility.)*

**1. What is it?** A11yProof is an agent that fixes web accessibility bugs in real source code and shows proof for each fix. It loads a site in a real browser and scans it with axe-core. It patches the code in a sandbox, then re-scans to check the patch worked. It opens a pull request only after a person approves the exact diff. "Done" means a pull request with a verified fix, plus the before/after evidence the person saw when they approved it.

**2. Why care?** The WebAIM Million 2026 report found detectable WCAG 2 failures on 95.9% of the top one million home pages (94.8% in 2025), about 56 errors per page. UsableNet counted 5,114 ADA digital accessibility lawsuits in 2025. Alternatives exist, and each misses something:
- Checkers (axe, Lighthouse, WAVE) find problems but do not fix them.
- Overlay widgets promise one-line compliance. In 2025 the FTC ordered accessiBe to pay $1M over that kind of claim.
- Research shows language models can repair violations. AccessGuru (ASSETS '25) cut violation scores by up to 84%. It is a research system, not a shipped tool.

None gives a small team the whole path: fix the source, prove it, and let a person decide.

**3. Who opens it?** The end users are blind and keyboard-only people, and the small web team that merges the fix. In 60 seconds they should see: a scan result, one violation fixed, the diff, before/after screenshots, a re-scan going from violations to zero, and the approve/refuse/defer screen tied to a diff hash.

**4. What does it prove?** Each agentic requirement and where it will live:
- **Loop and budget:** observe (axe scan), decide (one violation), act (sandbox patch), record (ledger), stop. Capped in steps and dollars.
- **Tools and permission policy in code:** scanner limited to an allow-list of URLs, editor writes to a branch in a sandbox and never to main, pull requests need a signed approval. Page text is data, never instructions.
- **Memory:** the run ledger. The agent never retries a fix a person already refused.
- **Stop condition:** clean re-scan, budget exhausted, or refusal. Never "the model said it's done".
- **Human gate:** the person sees the diff, screenshots and re-scan result. Approval is bound to a hash of that diff. Change one line and it no longer counts.
- **Evaluation that can say no:** a development set and a held-out set, with at least 5 planted failure cases, judged by axe and screenshot diffs.
- **Controlled failure:** a page hides an instruction to push straight to main. The model may obey it. The permission check in code catches it and the run stops.

**5. In / out / first.**
- In: scan, patch in a sandbox, re-scan, human gate, pull request, evaluation on held-out pages. Test data is synthetic pages with planted bugs, plus open-source sites whose maintainers say yes.
- Out: no overlay, no auto-merge, no personal data, and no claim of legal compliance. It is not a guarantee against lawsuits.
- First (build plan, step 1): the contract and the tests, written before any code. Then the loop and tools, the gate and GitHub App, the evaluation, and a small pilot on real repositories.

**6. What could sink it?** The biggest risk is a fix that passes axe but breaks the page, or a page instruction that steers the agent. Plan: screenshot diffs check layout, the permission policy is enforced in code rather than the prompt, and planted failure cases test both on purpose. The limit that remains: automated checks see only part of the problem. Alt-text meaning needs a human, so a person will test the held-out pages with a screen reader. A sample of a few dozen sites can show the loop works. It cannot prove it works on every website.

**7. Why this project?** I wanted a portfolio work that solves a real problem and shows he can ship a system with safety and security, not an academic exercise which will also create a impact and smoothen user experience for people with disabilities.

**8. Why this matters to me?** This project matters to me because I believe technology should make the internet more accessible for everyone, not leave people behind. I wanted to build something that solves a real-world problem while making a meaningful difference in the lives of people with disabilities. What makes it especially important to me is the idea of using AI responsibly, where every fix is tested and verified rather than blindly trusted. I hope this can make the web a little more inclusive, one fix at a time.

### Exists today (2026-11-23)
- The 4K project film, `Bagwe_Shubham_INFO7375_A11yProof_FinalProjectFilm.mp4`, about 4 min 39 s.
- `beat_sheet.json` (the film script, 19 beats).
- The fact-check with sources, and the review notes.
- Gate reports.

The agent itself does not exist yet.

### Will exist
- The agent: loop, tools with permission policy, ledger, human gate with GitHub App, sandbox.
- The evaluation: development and held-out sets, at least 5 planted failure cases, the controlled-failure run.
- Targets from the film (targets, not results): at least 80% of held-out violations fixed, zero new violations, zero broken layouts, at least 7 of 10 pull requests accepted by maintainers.
- Runs on Claude API credits, capped per run (credits confirmed).
- The 10-document evidence packet.
