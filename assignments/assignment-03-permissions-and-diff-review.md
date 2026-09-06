# Assignment 03 Permissions and Diff Review

**Due:** Canvas · **Points:** 100 · **Assessments:** [Lesson 5](../lessons/05-tools-and-permissions/docs/en.md) and [Lesson 6](../lessons/06-claude-code-and-diff-review/docs/en.md)

Read the [course AI policy](../prerequisites/ai-policy.md) and watch [AI Policy for Professor Bear's Courses | Using AI Responsibly in Class](https://youtu.be/8Ut0Cdl6vMw?si=9w3aEpt1ZyAR4Kiz).

## Implementation 60 points

- Implement resolved-path containment and a separate write-approval gate in Python. **15 points**
- Test traversal, sibling-prefix confusion, symlink escape, permitted reads, and approved writes. **15 points**
- Use Claude Code on a bounded repository change and preserve the issue, plan, commands, tests, and final diff. **15 points**
- Add a second discriminating test that can reject a superficially passing patch. **10 points**
- Record the human merge decision and the evidence used; do not treat Claude's completion claim as approval. **5 points**

## Submit

Ship a permissioned diff-review packet with sanitized evidence. Include [Frictional](../prerequisites/frictional.md) **10 points**, [GitHub posting](../prerequisites/github-submission.md) **10 points**, and [Relative Quartile](../prerequisites/relative-quartile.md) **20 points**. An explainer video is optional.
