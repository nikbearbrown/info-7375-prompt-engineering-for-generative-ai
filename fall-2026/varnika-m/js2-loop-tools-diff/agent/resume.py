"""Refuse anything that is not a fictional persona (JS1 CONTRACT.md sections 1 and 3).

Adapted from JS1's resume.py: the same two checks, but on text the loop has already
read through the policy, so this file never opens a file itself.
"""

import json


class ResumeRefused(ValueError):
    pass


def check_resume(text):
    resume = json.loads(text)
    personal = resume.get("personal") or {}
    email, phone = personal.get("email"), personal.get("phone")
    # The messages never repeat the email or phone, so a real résumé is not echoed to the screen.
    if not isinstance(email, str) or not email.lower().endswith("@example.com"):
        raise ResumeRefused("refused: the résumé's email must end in @example.com (fictional personas only)")
    if not isinstance(phone, str) or "555" not in phone:
        raise ResumeRefused("refused: the résumé's phone must contain 555 (fictional personas only)")
    return resume
