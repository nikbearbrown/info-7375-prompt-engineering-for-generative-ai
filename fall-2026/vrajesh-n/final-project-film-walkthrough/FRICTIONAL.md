# FRICTIONAL - Early Bird film

Draft recorded on 2026-11-23.

## 2026-11-23 - Catching the toolkit bypass

The first build bypassed brutalist.art. I caught that and asked for the film to be rebuilt through the toolkit. Having a playable video did not establish that it followed the process I had requested.

The rebuild used a Remotion scene rendered through `remotion_scenes.py`, Kokoro narration through `generate_audio_kokoro.py`, and the toolkit's `./art run` and `./art final` commands. `BUILD-PROMPT.md` records that route and the toolkit changes. Rendering at 4K ran into memory limits, so the render scale was made configurable and set to 1 for 1920x1080 output.

## 2026-11-23 - Gate checks and remaining failure

I wanted the film corrected without waiving gates. The build record says no gate was waived and no gate setting was changed. That does not mean every saved report is passing.

The saved Gate V report has zero blocker or major findings. Gate T still reports a failure in B05: a text region has local contrast of 2.94:1, below the check's 3.0:1 threshold. The suggested correction is to move the label off its background, change its color, or add a backing plate. I cannot yet record that correction as completed or claim that all gates passed.

Before submission, I need to confirm the actual film edits for each gate failure and save the passing rerun reports. If the B05 correction has already been rendered, I still need a fresh report that verifies it. The specific edits and their dates belong here once confirmed, rather than a general claim that everything was fixed.

## 2026-11-23 - Missing greenhouse-watch evidence

The film includes a claim that greenhouse-watch kept a marketing job because the posting mentioned Python and SQL. My October 25 feedback describes that result, but the raw run output is still missing from this reel. `FACTCHECK.md` row 6 therefore marks it PER FEEDBACK.

I still need to add the raw output with the command, inputs, and actual run date so someone else can inspect the result. If I rerun it, I need to label that as a new run, not evidence recovered from the original run. If I cannot supply the evidence, I need to soften or remove the film's claim before submitting.

The main lesson for me is to check both the process and the evidence behind an output. A finished-looking film can still have an unresolved gate failure or an unsupported claim.
