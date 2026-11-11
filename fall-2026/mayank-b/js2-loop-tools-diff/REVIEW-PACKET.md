# Review packet: the symlink escape (Chapter 6)

## Executive summary

**What this is.** The record of one change I asked Claude Code to make, reviewed as a change in behaviour and not as a pleasant-looking diff. The change fixes a defect inherited from JS1: the file-write guard checked the *spelling* of a path, so a symbolic link inside an allowed folder could send a write anywhere on disk.

**Why read it.** A green test after a patch proves little if the test was written to fit the patch. Here the failing test was committed first, the patch was scoped to one function, and the evidence before and after is saved verbatim.

**What it found.** The patch fixes the reproduced case and passes all 50 tests and all 9 planted wrong versions. A probe shows one escape it still does not cover: if `runs/` itself is a symlink pointing outside the project, writes still land outside.

## The chain (each link is a file or a commit)

| Step | Evidence |
|---|---|
| 1. Defect named in the gate, before any code | `GATE.md` §7 W2 and §8; my answer 9 in `notes/gate-answers-2026-11-10.md` (JS2-CP1 `3ce860b`) |
| 2. First version ports the defect on purpose | `src/jsa/policy.py` `_resolve` = `os.path.abspath(...)`, as JS1's `safeWrite` used `path.resolve` (JS2-CP3 `b8b3fb4`) |
| 3. **Reproduced, with the test written before the patch** | tests `test_B8_symlink_escape_on_write` and `test_B8b_returned_path_is_the_resolved_one` committed in **JS2-CP5 `f2e775e`**, both failing: `review/01-reproduce-before-patch.txt` ("PolicyError not raised"). The harness agrees: `review/01b-wrong-versions-before-patch.txt` |
| 4. The request to Claude Code, with its scope | `review/02-request-to-claude-code.md` |
| 5. The diff | `review/02-patch.diff` (JS2-CP6 `9416437`): 1 file, `_resolve` only, +3 −2 |
| 6. After the patch | `review/03-after-patch.txt`: B8/B8b pass, **50/50** tests, **9/9** wrong versions caught |
| 7. One case the test still misses | `review/04-still-missed-probe.txt`: **ALLOWED, the write landed outside the project** |

## Reading the diff as a change in behaviour

```diff
-    # Ported from JS1's safeWrite: path.resolve(root, target). Cleans "." and ".." textually.
-    return Path(os.path.abspath(os.path.join(root, target)))
+    # Follow symlinks: judge a path by where the filesystem will actually put the bytes (GATE §6).
+    # JS1's safeWrite only cleaned ".." textually, so a link inside an allowed folder could point anywhere.
+    return Path(os.path.join(root, target)).resolve()
```

| Behaviour | Before | After |
|---|---|---|
| `runs/<id>/link/x.json`, where `link` → outside | **allowed**; the write follows the link | refused `outside-write-root` |
| Path returned to the caller | the spelled path (`/var/…` on macOS) | the real path (`/private/var/…`) |
| **Reads** through a link pointing outside a read root | **allowed** (probed on `f2e775e`) | **refused** `outside-read-roots` (probed on `9416437`): a second behaviour change, beyond the write case I asked about. It matches GATE §6 ("paths are judged by where they resolve"). There is no test for it yet. |
| The allowed roots themselves (`runs/<id>`, `config`, …) | spelled | **also resolved**. If a root is itself a symlink, the root moves with it. That's why the probe in step 7 still escapes. |
| A path that doesn't exist yet | cleaned textually | `resolve()` resolves the part that exists and appends the rest (`strict=False`) |
| `..` and sibling-prefix cases (B7, B9) | refused | refused (unchanged) |

## Did the change stay in scope?

Yes. `git diff --stat` shows `src/jsa/policy.py | 5 +++--` and nothing else: no test, allow-list, approval rule, loop or checker was touched, which is what the request said. The read-side change (row 3 above) lives inside the same function, so it's in the *file* scope, but it's a behaviour I didn't ask for by name. I'm recording it rather than treating it as free.

## The commands — to be run by me (Mayank)

```bash
cd fall-2026/mayank-b/js2-loop-tools-diff
git checkout f2e775e -- src/jsa/policy.py && (cd tests && python3 -m unittest test_policy.Paths.test_B8_symlink_escape_on_write)   # expect FAIL
git checkout 9416437 -- src/jsa/policy.py && (cd tests && python3 -m unittest test_policy.Paths.test_B8_symlink_escape_on_write)   # expect ok
python3 -m unittest discover -s tests -p "test_*.py"     # expect: Ran 50 tests ... OK
python3 scripts/wrong_versions.py                         # expect: 9/9 wrong versions caught
python3 review/probe_still_missed.py                      # expect: ALLOWED ... outside the project? True
```

**Ran by me:** _(Mayank: paste the last line of each, or write "ran, matched"; date it)_

## Decision

**Decision (Mayank):** _ACCEPT / REVISE / REJECT, with one sentence of reasons_

*Claude's recommendation:* **Accept, and open the missed case as a follow-up rather than widening this patch.** Reasons:
- the test written first now passes;
- the diff is the smallest one that matches GATE §6's wording;
- nothing outside the requested function changed;
- 9/9 planted wrong versions are still caught.

Fixing the `runs/`-is-a-symlink case needs a different rule: check that each resolved root is still inside the resolved project folder. That's a new decision for GATE.md, not part of this request.

## One case the test would still miss

1. **The write root itself is a symlink** (`runs/` → elsewhere). Probed, not hypothetical: `review/04-still-missed-probe.txt` shows the write landing outside the project.
2. Also untested: a link swapped in **between** the check and the write (time-of-check/time-of-use). `authorize()` returns a path, and the write happens a moment later.
