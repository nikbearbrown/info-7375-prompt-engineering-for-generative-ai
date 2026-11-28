# Premortem trigger

PREMORTEM TRIGGER (PREMORTEM.md lines 2-4), offline, on a disposable state file.

- Started from revision 0 (sha256 f046969f9ae5…).
- First, `PREMORTEM-anthropic`: committed.
- Second, `PREMORTEM-databricks`: refused (expected revision 0, found revision 1).
- The refusal left the file's bytes unchanged: True (sha256 72352a71ed7f… before and 72352a71ed7f… after).
- The state is at revision 1 with the boards ['greenhouse/anthropic'].
