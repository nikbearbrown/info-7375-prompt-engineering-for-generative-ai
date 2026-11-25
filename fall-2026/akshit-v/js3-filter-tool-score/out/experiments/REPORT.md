# One change at a time: results on the 30 held-out labels

## the filter file (filter_v1.0_vs_v1.1.json)
- A: v1.0 (threshold 6): agrees with my labels on 14/30 = 47% (95% CI 28%–66%); kept 4 (relevant 3), missed relevant 15
- B: v1.1 (threshold 6): agrees with my labels on 14/30 = 47% (95% CI 28%–66%); kept 4 (relevant 3), missed relevant 15

## a setting (threshold) (setting_threshold_v1.1.json)
- A: v1.1 (threshold 6): agrees with my labels on 14/30 = 47% (95% CI 28%–66%); kept 4 (relevant 3), missed relevant 15
- B: v1.1+t5 (threshold 5): agrees with my labels on 21/30 = 70% (95% CI 51%–85%); kept 17 (relevant 13), missed relevant 5

## Claude judge conditions

| condition | object changed | valid | answered | agrees with my label | cannot_tell | tool calls | verdicts that differ from baseline |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline | (none: reference) | 30/30 | 30 | 12/30 = 40% (95% CI 23%–59%) | 0 | 0 | - |
| baseline_repeat | (none: A-A control) | 30/30 | 30 | 12/30 = 40% (95% CI 23%–59%) | 0 | 0 | 0 |
| prompt_v2 | the prompt | 30/30 | 30 | 12/30 = 40% (95% CI 23%–59%) | 0 | 0 | 0 |
| prompt_v3_definition | the prompt (definition paragraph only) | 30/30 | 30 | 20/30 = 67% (95% CI 47%–83%) | 0 | 0 | 14 |
| context_score | the context | 30/30 | 30 | 12/30 = 40% (95% CI 23%–59%) | 0 | 0 | 0 |
| tools_score | the tool list | 30/30 | 30 | 12/30 = 40% (95% CI 23%–59%) | 0 | 0 | 0 |
