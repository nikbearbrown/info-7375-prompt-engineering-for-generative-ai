# Sampling — repeated Claude judgments

On 2026-10-31, five development postings were sent to fresh Claude Code
subagents four times each under the v1 prompt. The prompt files and unedited
answers are in `experiments/sampling/`; `python3 experiments/experiment.py sampling`
recomputes `experiments/sampling/results.json` from those answers. The labels
are in `experiments/label_pool/LABELS.md`.

| Posting id | Posting | Label | Validated outcomes across four runs |
|---|---|---|---|
| 8275927 | Data Scientist | `not_relevant` | 4 × invalid |
| 4388567009 | Microsoft D365 FO ERP Data Analyst II | `not_relevant` | 4 × `not_relevant` |
| 8877421002 | Technical Business Analyst | `needs_human` | 4 × invalid |
| 5212408008 | Data Analyst (CRM) | `not_relevant` | 4 × invalid |
| 8706824002 | Senior Business Intelligence Analyst (Healthcare) | `not_relevant` | 4 × invalid |

Each posting's validated outcome repeated 4/4 times. Sixteen of the 20 outputs
were invalid because their list-index citation paths used dot positions instead
of the validator's square-bracket syntax. The four valid outputs all concerned
one posting and agreed with its hand label. Repetition here shows a
stable formatting failure; it does not establish judgment accuracy.
