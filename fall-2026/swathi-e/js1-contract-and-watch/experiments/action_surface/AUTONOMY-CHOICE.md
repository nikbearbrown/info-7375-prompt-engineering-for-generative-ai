# AUTONOMY-CHOICE.md — least autonomy that suffices

Written by Swathi Baba Eswarappa, 2026-10-27, after the three action-surface
runs on posting 8546367002 (records: runs/action_surface/, comparison:
experiments/action_surface/comparison.md). My words.

I chose the file-based approach because it completed the task correctly without needing extra permissions. It passed my validator, and I could check exactly what Claude had read. My watch already fetches the job postings, so there is no reason to give Claude web access again. The agent approach worked too, but it introduced extra risks that weren't necessary for this task. I felt the simpler approach was easier to control and verify.

I didn't choose the chat approach because its response wasn't in valid JSON format, so my validator couldn't check it properly, while the file-based approach gave me a valid result that I could verify.
