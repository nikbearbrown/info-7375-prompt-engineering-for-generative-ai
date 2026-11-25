# JS2 — Loop, Tools, Diff (INFO 7375)

Node 20, ESM (.mjs), no runtime dependencies beyond Node built-ins unless I approve one.
Started from my JS1 code (copied into this folder). JS1 entry was src/watch.mjs.

## Source of truth
GATE.md is the spec. If code and GATE.md disagree, stop and tell me. Never edit GATE.md
or test/boundary-cases.md. Those are mine. Propose changes in chat instead.

## Hard rules
- Never weaken, skip, or delete a test to make it pass. If a test looks wrong, stop and say why.
- Permission checks live in code (src/policy.mjs), never in a prompt or comment.
- Network: only hosts on the allow-list in GATE.md. No redirects followed off-list.
- Writes: only inside ./out/ (resolved real path, symlinks resolved). Nothing else.
- The agent never applies, emails, messages, or logs in. Don't write code that could.
- Don't invent values. A failed board reports an error, never "0 jobs".
- No Co-Authored-By or any attribution trailers in commits.
- Small commits, one concern each, imperative messages.

## Commands
- Tests: node --test
- Run: node src/loop.mjs --config boards.json --label <label>

## Layout
src/loop.mjs, src/policy.mjs, src/providers/{greenhouse,lever}.mjs, src/check.mjs
test/*.test.mjs · out/ (traces, raw responses, state) · boards.json
