# Toolkit changes for this film

One change to brutalist.art (`6a8380a` plus the pitch film's changes, see that film's `toolkit-changes/`):

- `pitch-byline.diff`: `PitchOutro` gains an optional `byline` prop. The default is `"a pitch by"`, so
  the pitch film renders unchanged. This film passes `"a film by"`.

Apply from the brutalist.art root, after the pitch film's changes:

```bash
git apply <this folder>/pitch-byline.diff
```

Not changed: `runtime/scripts/run.sh` and `runtime/scripts/type_check.py`. Changes to both were tried
and reverted (FRICTIONAL Entry 4). Both are byte-identical to the originals.
