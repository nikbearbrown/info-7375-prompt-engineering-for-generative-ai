# Approvals for state writes

Each state write in this folder needs the student's approval for its run ID, target path, starting revision and SHA-256 ([PLAN.md](../PLAN.md) v0.2, Approval). This file records each approval as the student sent it, what it answered, and what the write then did. The approvals are the student's; Claude Code keeps this record.

## 2026-11-28: three writes from revision 0

In the chat, at about 08:41 EST, Claude Code's request listed three writes. Each started from revision 0, with sha256 `f046969f9ae59329fe59cd35ae89f2646852312efa07620522efc6416a824f7d`:

| Run ID | Path | Starting revision |
| --- | --- | --- |
| `SEEDED-1-2026-11-08` | `replay/state/state.json` | 0 |
| `PREMORTEM-anthropic` | `replay/premortem/state.json` | 0 |
| `PREMORTEM-databricks` | `replay/premortem/state.json` | 0 |

The student's reply, word for word, received in the chat by 08:44 EST:

> Approved  
> Suketh Produtoor

The reply answers the request above. It does not restate the values or give a date; the date on record is the day the reply arrived.

| Run ID | What the write did (UTC) |
| --- | --- |
| `SEEDED-1-2026-11-08` | 13:44:18: committed revision 1 of `replay/state/state.json`, sha256 `3539364075cf9f1304f73b9604936ce8bd057a051f03c26feba7ed299b4f31e5` (3,258 facts). Evidence: [runs/SEEDED-1-2026-11-08/](runs/SEEDED-1-2026-11-08/) |
| `PREMORTEM-anthropic` | 13:44:30: committed revision 1 of `replay/premortem/state.json`, sha256 `72352a71ed7fb862e8f6bfd0b46a6dba7bb4be6d75927dd5fbdfb0ee3589fda9` (1,350 facts, Anthropic only) |
| `PREMORTEM-databricks` | 13:44:30: refused as a stale write, as the premortem predicted. It expected revision 0 and found revision 1, and the file's bytes did not change. This approval is now void. Record: [premortem/runs/PREMORTEM-databricks/write-refused.json](premortem/runs/PREMORTEM-databricks/write-refused.json) |

## 2026-11-28: the Nov 24 replay, and the premortem's line 5

In the chat, after 08:44 EST, Claude Code's next request asked for two things. The first was approval of `SEEDED-2-2026-11-24` on `replay/state/state.json` at revision 1, sha256 `3539364075cf9f1304f73b9604936ce8bd057a051f03c26feba7ed299b4f31e5`. The second was the student's decision on PREMORTEM.md line 5. One option there was a new run ID approved against `replay/premortem/state.json` at revision 1, sha256 `72352a71ed7fb862e8f6bfd0b46a6dba7bb4be6d75927dd5fbdfb0ee3589fda9`.

The student's reply, word for word, received in the chat by 08:50 EST:

> 1. Approve the Nov 24 replay. The saved state matches revision 1 and the supplied SHA-256. This approval covers the seeded comparison with November 8 and the closure check.
>
> ```
> SEEDED-2-2026-11-24:replay/state/state.json:1:3539364075cf9f1304f73b9604936ce8bd057a051f03c26feba7ed299b4f31e5
> ```
>
> 2. Approve rebuilding the Databricks update. The November 8 capture contains 922 Databricks keys. Rebuild the update against revision 1 so revision 2 preserves the accepted Anthropic records and adds Databricks.
>
> ```
> PREMORTEM-databricks-2:replay/premortem/state.json:1:72352a71ed7fb862e8f6bfd0b46a6dba7bb4be6d75927dd5fbdfb0ee3589fda9
> ```

| Run ID | What the write did (UTC) |
| --- | --- |
| `SEEDED-2-2026-11-24` | 13:50:22: committed revision 2 of `replay/state/state.json`, sha256 `dc40d7b9d7bffe47f876f81ebd017fce6d2b343087e0ef033aa081deb9307a88`. Evidence: [runs/SEEDED-2-2026-11-24/](runs/SEEDED-2-2026-11-24/) |
| `PREMORTEM-databricks-2` | 13:52:44: reread `replay/premortem/state.json` at revision 1, rebuilt the Databricks update on it (the Nov 8 capture's 922 keys) and committed revision 2, sha256 `96016689d3515d54f9326a4196cef77134481610c81c1a2a814c169ab678859c`. The 1,350 Anthropic facts are unchanged. Record: [premortem/resume-PREMORTEM-databricks-2.json](premortem/resume-PREMORTEM-databricks-2.json) |
