"""The labeling helper: python -m jobwatch label <csv>. Deepak runs it; Claude Code never does.

One row at a time, starting at the first row whose answer column is empty (so it resumes):
  - posting sheets (labels/heldout.csv: column "label"; audit sheets: column "verdict"):
    shows the posting's text file (title, location, URL, normalized text), paged, and asks
        r = relevant, n = not_relevant, o = OVERRIDE (asks r or n, then the reason)
    and writes the answer column and override_reason (empty unless o).
  - claims sheets (columns "claim" and "note"): shows the claim, its field and quote, then the
    posting text, paged, and asks s = supported, c = contradicted, i = insufficient, then an
    optional note; writes "label" and "note".
At the top of every posting row it prints RELEVANT_HINT, so r is never read as "reject".
`python -m jobwatch label --clear <csv>` empties the answer and reason columns (label or verdict,
and override_reason or note) after Deepak types the file name to confirm; nothing else changes.
`python -m jobwatch label --checklist <csv>` (posting sheets): after the posting, asks the three
FILTER.md section 0 checks in order (CHECKS), stopping at the first n. The answer is relevant only
if all three are y, otherwise not_relevant; then "Override? (Enter = no, o = yes)", where o asks
the label and a required reason. The answers go into check_family, check_seniority and
check_location (empty where not asked), inserted just before the answer column the first time.
On a claims sheet --checklist is ignored and the s/c/i mode runs. --clear also empties the check
columns when the sheet has them.
`python -m jobwatch label --family <csv>` (posting sheets): seniority and location are applied
mechanically from FILTER.md section 0's wording (SENIORITY_WORDS in the title; LOCATION_TERMS, or
Remote with a US token, in the location field) and recorded as y/n rule results; Deepak is asked
only the job family, and the experience question only when family is y and both rules pass. The
label is relevant only if every check passes. An override needs a reason of at least 15
characters. Columns: check_family, check_seniority_title, check_location, check_experience and
check_source (which checks were mechanical and which were asked).
It saves the sheet after every answer and changes no other column. It never shows a score, a
decision, a matched rule, an audit group, a stratum or a pre-label: it prints only the posting
key, the claim columns named above and the text file. All disk access is through tools.
"""
import textwrap

from jobwatch import sheets
from jobwatch.textmatch import tokens

PAGE_LINES = 30
WIDTH = 100
POSTING_ANSWERS = {"r": "relevant", "n": "not_relevant"}
CLAIM_ANSWERS = {"s": "supported", "c": "contradicted", "i": "insufficient"}
RELEVANT_HINT = "r = RELEVANT to Riley (worth her time), n = NOT relevant. r does not mean reject."
CHECKS = (
    ("check_family", "Job family: is the job itself ML, AI, data science, LLM or applied ML research work? y/n"),
    ("check_seniority", "Seniority: no Intern, Staff, Principal, Director, Lead, Head or Manager in the title, "
                        "and minimum experience 5 years or less? y/n"),
    ("check_location", "Location: Boston, New York/NYC, Seattle, or remote explicitly allowing the US? y/n"),
)
CHECK_COLUMNS = tuple(c for c, _ in CHECKS)

# --family mode. The two mechanical checks use FILTER.md section 0's own words, coded here (not
# imported from the filter): seniority words in the title; the location list in the location field.
SENIORITY_WORDS = ("Intern", "Staff", "Senior Staff", "Principal", "Director", "Lead", "Head", "Manager")
# Added from section 0's meaning, not its literal word list: an internship is an Intern role.
MEANING_WORDS = ("Internship",)
SENIORITY_SOURCE = "seniority_title (section 0 words, plus Internship from section 0's meaning, not its literal word list)"
LOCATION_TERMS = ("Boston", "New York", "NYC", "Seattle")
US_TOKENS = ("us", "usa", "united states", "u s")
FAMILY_Q = "Job family: is the job itself ML, AI, data science, LLM or applied ML research work? y/n"
EXPERIENCE_Q = "Experience: is the minimum required experience 5 years or less, or not stated? y/n"
FAMILY_COLUMNS = ("check_family", "check_seniority_title", "check_location", "check_experience", "check_source")
MIN_OVERRIDE_REASON = 15


def _has_term(term, text):
    t, x = tokens(term), tokens(text or "")
    return any(x[i:i + len(t)] == t for i in range(len(x) - len(t) + 1))


def seniority_title_check(title):
    """y when the title has none of the section 0 seniority words (whole tokens)."""
    hits = [w for w in SENIORITY_WORDS + MEANING_WORDS if _has_term(w, title)]
    return ("n" if hits else "y"), hits


def location_check(location):
    """y when the location field names Boston, New York, NYC or Seattle, or Remote with a US token."""
    if not location or not tokens(location):
        return "n", "missing"
    for term in LOCATION_TERMS:
        if _has_term(term, location):
            return "y", term
    if _has_term("Remote", location):
        return ("y", "Remote + US") if any(_has_term(u, location) for u in US_TOKENS) else ("n", "Remote without a US token")
    return "n", "not in the list"


def with_family_columns(columns, answer_col):
    """The family-mode check columns in a fixed order just before the answer column. Older
    checklist columns are dropped (they must already be empty; the caller checks)."""
    columns = [c for c in columns if not c.startswith("check_")]
    i = columns.index(answer_col)
    return columns[:i] + list(FAMILY_COLUMNS) + columns[i:]


def with_check_columns(columns, answer_col):
    """The check columns, inserted just before the answer column if the sheet lacks them."""
    columns = list(columns)
    if all(c in columns for c in CHECK_COLUMNS):
        return columns
    columns = [c for c in columns if c not in CHECK_COLUMNS]
    i = columns.index(answer_col)
    return columns[:i] + list(CHECK_COLUMNS) + columns[i:]


def derive(answers):
    """relevant only if all three checks are y."""
    return "relevant" if len(answers) == len(CHECKS) and all(a == "y" for a in answers) else "not_relevant"


def sheet_kind(columns):
    cols = set(columns)
    if {"claim", "label", "note"} <= cols:
        return "claims", "label", "note"
    if {"verdict", "override_reason"} <= cols:
        return "posting", "verdict", "override_reason"
    if {"label", "override_reason"} <= cols:
        return "posting", "label", "override_reason"
    raise ValueError("not a labeling sheet: need label+override_reason, verdict+override_reason, or claim+label+note")


def pages(text):
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, WIDTH) or [""])
    return [lines[i:i + PAGE_LINES] for i in range(0, len(lines), PAGE_LINES)] or [[]]


def _ask_choice(ask, prompt, choices):
    while True:
        a = ask(prompt).strip().lower()
        if a in choices:
            return a


def _show_and_ask(text, ask, out, prompt_choices, header):
    ps = pages(text)
    for i, page in enumerate(ps, 1):
        out("\n".join(page))
        if i < len(ps):
            a = ask(f"--- page {i}/{len(ps)} of {header}: Enter = next page, or answer {'/'.join(prompt_choices)}, q = quit: ").strip().lower()
            if a in prompt_choices or a == "q":
                return a
    return _ask_choice(ask, f"--- end of {header}: answer {'/'.join(prompt_choices)}, q = quit: ",
                       set(prompt_choices) | {"q"})


def clear(tools, path, ask=input, out=print):
    """Empty the answer and reason columns after the file name is typed to confirm. Returns 0, or 1 if not confirmed."""
    comments, columns, rows = sheets.read_sheet(tools, path)
    _, answer_col, reason_col = sheet_kind(columns)
    cleared = [answer_col, reason_col] + [c for c in columns if c.startswith("check_")]
    cells = sum(bool((r.get(c) or "").strip()) for r in rows for c in cleared)
    name = path.replace("\\", "/").rsplit("/", 1)[-1]
    typed = ask(f"This empties the {', '.join(cleared)} columns of {path} ({cells} non-empty cells in "
                f"{len(rows)} rows). Type the file name ({name}) to confirm: ").strip()
    if typed not in (name, path):
        out(f"Not confirmed; {path} is unchanged.")
        return 1
    for r in rows:
        for c in cleared:
            r[c] = ""
    sheets.write_sheet(tools, path, comments, columns, rows)
    out(f"Cleared {cells} cells ({', '.join(cleared)}) in {len(rows)} rows of {path}.")
    return 0


def _show_pages(text, ask, out, header):
    """Page through the posting; returns "q" if Deepak quits, else None."""
    ps = pages(text)
    for i, page in enumerate(ps, 1):
        out("\n".join(page))
        if i < len(ps):
            if ask(f"--- page {i}/{len(ps)} of {header}: Enter = next page, q = quit: ").strip().lower() == "q":
                return "q"
    return None


def _checklist_row(row, body, ask, out, header, answer_col, reason_col):
    """One row in checklist mode. Returns False if Deepak quit (the row is left unchanged)."""
    out("Checklist (FILTER.md section 0): answer y or n; q = quit. The questions stop at the first n.")
    if _show_pages(body, ask, out, header) == "q":
        return False
    answers = []
    for col, question in CHECKS:
        a = _ask_choice(ask, question + " ", {"y", "n", "q"})
        if a == "q":
            return False
        answers.append(a)
        if a == "n":
            break
    label = derive(answers)
    out(f"From your checks: {label}")
    o = _ask_choice(ask, "Override? (Enter = no, o = yes) ", {"", "o"})
    reason = ""
    if o == "o":
        direction = _ask_choice(ask, "OVERRIDE: your label, r = relevant or n = not_relevant: ", {"r", "n"})
        while not reason:
            reason = ask("OVERRIDE reason (required): ").strip()
        label = POSTING_ANSWERS[direction]
    for (col, _), a in zip(CHECKS, answers + [""] * (len(CHECKS) - len(answers))):
        row[col] = a
    row[answer_col], row[reason_col] = label, reason
    return True


def _family_row(row, body, ask, out, header, answer_col, reason_col):
    """One row in family mode. Returns False if Deepak quit (the row is left unchanged)."""
    sen, sen_hits = seniority_title_check(row.get("title", ""))
    loc, loc_why = location_check(row.get("location", ""))
    out("Rule results (mechanical, FILTER.md section 0 wording): "
        f"seniority words in title: {', '.join(sen_hits) or 'none'} -> {sen}; location: {loc_why} -> {loc}")
    if _show_pages(body, ask, out, header) == "q":
        return False
    fam = _ask_choice(ask, FAMILY_Q + " ", {"y", "n", "q"})
    if fam == "q":
        return False
    exp, source = "", f"mechanical: {SENIORITY_SOURCE}, location; asked: family"
    if fam == "y" and sen == "y" and loc == "y":
        exp = _ask_choice(ask, EXPERIENCE_Q + " ", {"y", "n", "q"})
        if exp == "q":
            return False
        source += ", experience"
    label = "relevant" if (fam, sen, loc, exp) == ("y", "y", "y", "y") else "not_relevant"
    out(f"From the checks: {label}")
    o = _ask_choice(ask, "Override? (Enter = no, o = yes) ", {"", "o"})
    reason = ""
    if o == "o":
        direction = _ask_choice(ask, "OVERRIDE: your label, r = relevant or n = not_relevant: ", {"r", "n"})
        while len(reason) < MIN_OVERRIDE_REASON:
            reason = ask(f"OVERRIDE reason (at least {MIN_OVERRIDE_REASON} characters): ").strip()
        label = POSTING_ANSWERS[direction]
    row.update({"check_family": fam, "check_seniority_title": sen, "check_location": loc,
                "check_experience": exp, "check_source": source})
    row[answer_col], row[reason_col] = label, reason
    return True


def run(tools, path, ask=input, out=print, checklist=False, family=False):
    comments, columns, rows = sheets.read_sheet(tools, path)
    kind, answer_col, reason_col = sheet_kind(columns)
    family = family and kind == "posting"
    checklist = checklist and kind == "posting" and not family
    if family:
        old = [c for c in columns if c.startswith("check_") and c not in FAMILY_COLUMNS]
        if any((r.get(c) or "").strip() for r in rows for c in old):
            raise ValueError(f"{path}: older check columns ({', '.join(old)}) are not empty; run label --clear first")
        columns = with_family_columns(columns, answer_col)
        for r in rows:
            for c in old:
                r.pop(c, None)
            for c in FAMILY_COLUMNS:
                r[c] = r.get(c) or ""
    checklist = checklist and kind == "posting"
    if checklist:
        columns = with_check_columns(columns, answer_col)
        for r in rows:
            for c in CHECK_COLUMNS:
                r.setdefault(c, "")
                r[c] = r[c] or ""
    todo = [i for i, r in enumerate(rows) if not (r.get(answer_col) or "").strip()]
    out(f"{path}: {len(rows) - len(todo)} of {len(rows)} rows answered; {len(todo)} to go.")
    done = 0
    for i in todo:
        row = rows[i]
        body = tools.read_file(row["text_path"]).decode("utf-8")
        header = f"row {i + 1} of {len(rows)} ({row.get('posting_key', '')})"
        out(f"\n===== {header} =====")
        if family:
            if not _family_row(row, body, ask, out, header, answer_col, reason_col):
                break
            sheets.write_sheet(tools, path, comments, columns, rows)
            done += 1
            continue
        if checklist:
            if not _checklist_row(row, body, ask, out, header, answer_col, reason_col):
                break
            sheets.write_sheet(tools, path, comments, columns, rows)
            done += 1
            continue
        if kind == "posting":
            out(RELEVANT_HINT)
        if kind == "claims":
            out(f"Claim: {row['claim']}\nField: {row.get('field', '')}\nQuote: {row.get('quote', '')}\n")
            a = _show_and_ask(body, ask, out, list(CLAIM_ANSWERS), header)
            if a == "q":
                break
            row[answer_col] = CLAIM_ANSWERS[a]
            row[reason_col] = ask("Optional note (Enter for none): ").strip()
        else:
            a = _show_and_ask(body, ask, out, ["r", "n", "o"], header)
            if a == "q":
                break
            if a == "o":
                direction = _ask_choice(ask, "OVERRIDE: your verdict, r = relevant or n = not_relevant: ", {"r", "n"})
                reason = ""
                while not reason:
                    reason = ask("OVERRIDE reason (required): ").strip()
                row[answer_col], row[reason_col] = POSTING_ANSWERS[direction], reason
            else:
                row[answer_col], row[reason_col] = POSTING_ANSWERS[a], ""
        sheets.write_sheet(tools, path, comments, columns, rows)
        done += 1
    left = sum(1 for r in rows if not (r.get(answer_col) or "").strip())
    out(f"\nSaved {path}: {done} answered this session; {left} left.")
    return 0
