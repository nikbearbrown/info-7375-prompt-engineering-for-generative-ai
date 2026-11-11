"""Prompt file loading and filling: CONTRACT.md Interfaces › Prompt file, Order step 2b."""
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from jobwatch.errors import REFUSED, Stop

SECTIONS = ("System", "User")
PLACEHOLDERS = ("RESUME_JSON", "POSTING_ID", "POSTING_JSON")
_HEADING = re.compile(r"## (.*?)\s*")
_PLACEHOLDER = re.compile(r"\{\{(" + "|".join(PLACEHOLDERS) + r")\}\}")


@dataclass(frozen=True)
class Prompt:
    path: str
    sha256: str
    system: str
    user: str


def load_prompt(path):
    def refuse(why):
        raise Stop(REFUSED, f"prompt refused ({path}): {why}")

    try:
        raw = Path(path).read_bytes()
        text = raw.decode("utf-8")
    except OSError:
        refuse("cannot read the file")
    except UnicodeDecodeError:
        refuse("not UTF-8")

    sections, current, preamble = {}, None, []
    for line in text.splitlines():
        m = _HEADING.fullmatch(line)
        if m:
            current = m.group(1)
            if current not in SECTIONS:
                refuse(f'unexpected section "## {current}"')
            if current in sections:
                refuse(f'section "## {current}" appears twice')
            sections[current] = []
        elif current is None:
            preamble.append(line)
        else:
            sections[current].append(line)
    if any(line.strip() for line in preamble):
        refuse('text before the first section; the file must start with "## System" or "## User"')
    for name in SECTIONS:
        if name not in sections:
            refuse(f'missing section "## {name}"')

    system = "\n".join(sections["System"]).strip()
    user = "\n".join(sections["User"]).strip()
    for name in PLACEHOLDERS:
        mark = "{{" + name + "}}"
        if mark in system:
            refuse(f"{mark} is in the System section")
        if user.count(mark) != 1:
            refuse(f"{mark} must appear exactly once in the User section")
    return Prompt(str(path), hashlib.sha256(raw).hexdigest(), system, user)


def fill_user(prompt, resume, posting_id, posting_doc):
    """Replace each placeholder literally, in one pass so filled text is never re-scanned."""
    values = {
        "RESUME_JSON": json.dumps(resume, ensure_ascii=False, indent=2),
        "POSTING_ID": posting_id,
        "POSTING_JSON": json.dumps(posting_doc, ensure_ascii=False, indent=2),
    }
    return _PLACEHOLDER.sub(lambda m: values[m.group(1)], prompt.user)
