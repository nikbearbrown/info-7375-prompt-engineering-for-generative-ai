"""Validator for a verdict (rule or Claude). Anything not in the fixed format is rejected."""
import re

REQUIRED = {"posting_id": str, "verdict": str, "justification": str, "resume_fields": list, "posting_fields": list}
OPTIONAL = {"title", "kind", "failed_check", "model", "date"}
VERDICTS = {"relevant", "not_relevant"}
_PART = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def get_path(obj, path):
    """Resolve 'education[0].degree' or 'address.postalAddress.addressCountry'; KeyError if absent."""
    for name, index in _PART.findall(path):
        if name:
            if not isinstance(obj, dict) or name not in obj:
                raise KeyError(path)
            obj = obj[name]
        else:
            i = int(index)
            if not isinstance(obj, list) or i >= len(obj):
                raise KeyError(path)
            obj = obj[i]
    return obj


def errors(v, posting, resume):
    if not isinstance(v, dict):
        return ["not a JSON object"]
    errs = []
    for key, typ in REQUIRED.items():
        if key not in v:
            errs.append(f"missing {key}")
        elif not isinstance(v[key], typ):
            errs.append(f"{key} is not {typ.__name__}")
    extra = set(v) - set(REQUIRED) - OPTIONAL
    if extra:
        errs.append(f"unexpected keys {sorted(extra)}")
    if errs:
        return errs
    if v["verdict"] not in VERDICTS:
        errs.append(f"verdict {v['verdict']!r} not in {sorted(VERDICTS)}")
    if v["posting_id"] != posting["id"]:
        errs.append("posting_id does not match the posting it is attached to")
    if not v["justification"].strip():
        errs.append("empty justification")
    for key, source in (("resume_fields", resume), ("posting_fields", posting)):
        if not v[key]:
            errs.append(f"{key} cites nothing")
        for path in v[key]:
            try:
                get_path(source, str(path))
            except KeyError:
                errs.append(f"{key} cites {path!r}, which does not exist")
    return errs
