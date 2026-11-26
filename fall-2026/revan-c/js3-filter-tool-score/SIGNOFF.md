# Sign-off and driver's seat — Job-Search Agent 3

**Status:** signed for the local JS3 implementation and saved evidence, November 25, 2026 ET. The final archive, GitHub folder, and Canvas upload remain unchecked.

```text
Sign-off — Job-Search Agent 3
Checked:      FILTER.md v1 preceded JS3 implementation (commits 0e15e65,
              08a5cc3, 4be2177); 215 snapshot rows and 149/61/5 board counts
              (runs/js3/filter_v1/summary.json); R1–R6 and score behavior
              (test_js3_filter.py); server lifecycle and read-only behavior
              (test_js3_mcp.py, scripted and real-client transcripts); 11/11 wrong versions
              caught (tools/check_wrong_versions_js3.py); 142 passing project tests;
              47 audit verdicts
              and 50 claim labels confirmed against the saved postings;
              deterministic and Claude development and held-out summaries.
How:          I checked the 47 audit entries in REVIEW_DRAFT.csv and the 50
              claim labels in CLAIMS_REVIEW_DRAFT.csv against the saved postings.
              I accepted the proposed verdicts and labels without changes and
              kept the draft wording where it matched the source. I checked
              code properties with project tests, source inspection,
              transcripts, and recomputation. Claude Code supplied the first
              implementation and scripted tools. Final local check outputs
              are in runs/js3/final_checks/.
Not checked:  whether these November 10 postings are still open; employer
              E-Verify status; performance on other boards or future postings;
              network behavior at the OS level; the model used by the real
              Claude Code client session; final zip contents, public GitHub
              folder, commit parity, and Canvas upload.
Not claiming: that the score predicts interviews or offers; that matched
              words prove job requirements; that 0/30 sampled reject errors
              means the full reject population has no errors; that a saved
              prompt or context changed model weights; full MCP conformance.
Signed or withheld: SIGNED — Revan C., November 25, 2026 ET.
Scope:        local JS3 implementation and saved evidence only; delivery is
              listed under Not checked.
```

## Driver's seat

| Task | Claude should | I should | Why the judgment stays with me |
|---|---|---|---|
| Implement the filter and score | Write code from the gate and expose every score and reject reason. | Specify the target, inspect omissions, decide whether to change weights or rules. | A number orders review; it does not price the time or opportunity cost of pursuing a job. |
| Audit rejected and kept postings | Prepare a reproducible sample and show source text. | Read the postings, confirm verdicts and false friends, and state what the sample can show. | The interpretation of a role and the cost of a missed posting are personal judgments. |
| Explain shortlisted postings | Propose atomic claims and source excerpts. | Label each claim against the original posting, narrow unsupported wording, or abstain. | A plausible sentence can overstate the employer's text. |
| Offer a tool to Claude | Implement and transcript the protocol, test wrong versions, list discrepancies. | Decide whether the capability is permitted and whether its returned content supports an answer. | A valid protocol message grants neither permission nor factual authority. |
| Report experiments and submit | Preserve commands, conditions, outputs, and limits. | Decide whether evidence is sufficient to sign; control any final posting or upload. | The submission and its claims are my responsibility. |

The choice to spend time on a posting remains mine even when the filter keeps it. The four kept postings all scored 7; I judged two not relevant after reading their 5+ year C# requirements. That is direct evidence that equal scores do not settle my decision.
