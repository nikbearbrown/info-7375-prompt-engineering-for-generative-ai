# Saloni's review decision on patch v1 (2026-11-10, ~19:55 ET, quoted as written in chat)

**1. Decision: Revise**

I would choose to revise the patch. The test results were convincing because they showed that the original defect was reproduced before the patch and all 48 tests passed afterward. However, the second live run revealed something important: OpenAI had added a new job, Account Director, Mid-Market | Korea, but the re-baselining process reported zero new jobs. I don't think we should lose track of a genuinely new job just to avoid false positives.

**2. Was the re-baselining in scope?**

I think handling the old state format was necessary because changing job identity from a bare ID to `system:board:id` would otherwise make all previously saved jobs appear new. However, simply discarding the old IDs and re-baselining everything goes a little too far because it can hide actual new jobs. I'd prefer rebuilding the old history using the raw responses from the previous run so we preserve existing records without missing newly posted jobs.

**3. One case the test would still miss**

If the same job is posted on two different boards but has different IDs on each board, the current identity logic would treat them as two separate jobs. The tests only check whether identical IDs across boards are handled separately, not whether the same underlying job with different IDs can be recognized.
