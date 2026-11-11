# Action-surface comparison: how to run it (Chapter 3)

The same frozen revision-1 rule and schema, and the same development posting **8660923002**, on two
claude.ai surfaces. The `claude -p` run of this posting is already saved in
`experiment/runs/revision1-dev/`. `chat-prompt.md` is byte-for-byte the prompt that run sent.

| Surface | What Claude gets | Files |
|---|---|---|
| Chat | Everything pasted into one message | `chat-prompt.md` |
| File | Two uploaded files plus a short instruction | `file-surface/8660923002.txt`, `file-surface/resume.example.json`, `file-surface/file-prompt.md` |

## Rules for both

1. Use a **new claude.ai chat in an Incognito (private) window**. Do **not** open it inside the course
   Project: Project instructions and files would be in Claude's context.
2. Use **one chat per surface**: one new chat for the chat surface and another new chat for the file
   surface. Never reuse a chat, and send nothing else in it.
3. Write down the date and time when the reply arrives, with your time zone. Note the model name
   claude.ai shows, if it shows one.

## Chat surface

1. Open `chat-prompt.md`, copy all of it and paste it as the only message. Send it.
2. Copy Claude's reply **exactly as shown**, including any code fence or text around the JSON. Paste it
   into a new file `experiment/action-surface/chat-reply.txt` and save it as UTF-8.

## File surface

1. Attach `file-surface/8660923002.txt` and `file-surface/resume.example.json`.
2. Paste the whole of `file-surface/file-prompt.md` as the message. Send it.
3. Paste Claude's reply exactly as shown into `experiment/action-surface/file-reply.txt`.

## Save and check

From the `js1-contract-and-watch` folder:

```bash
python3 experiment/action-surface/check_surface_replies.py save chat experiment/action-surface/chat-reply.txt "2026-10-30 14:05 EDT"
python3 experiment/action-surface/check_surface_replies.py save file experiment/action-surface/file-reply.txt "2026-10-30 14:20 EDT"
python3 experiment/action-surface/check_surface_replies.py
```

Use your real date and time. `save` stores the reply verbatim as a string in `chat-reply.json` or
`file-reply.json`, with the date and time, and refuses to overwrite a saved reply. The last command
reports, for each surface:
- whether the revision-1 validator accepts the reply;
- whether each citation's quote is found in the cited field (the support check, reported
  separately);
- whether the verdict and failed_check match your hand label and the rule judge.

A reply with a code fence or extra prose fails the validator. That is the contract's rule, not a
script bug.

Nothing in this kit sends anything to Claude. Only you do, by pasting.
