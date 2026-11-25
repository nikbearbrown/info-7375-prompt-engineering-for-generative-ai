"""Hand-labeling sheets shared by the held-out set, the audit and the claims (all through tools).

    write_texts(tools, lines, run_id) -> {key: path}   one plain-text file per posting
    write_sheet(tools, path, comments, columns, rows)  CSV with "# " comment lines first
    read_sheet(tools, path) -> (comments, columns, rows)

A posting's text file holds what a labeler may see: title, location, URL and the normalized
posting text (FILTER.md sections 1 and 5). It never holds a score, a decision or a matched rule.
"""
import csv
import io

TEXT_DIR = "data/texts"


def text_path(run_id, key):
    return f"{TEXT_DIR}/{run_id}/{key.replace(':', '_')}.txt"


def render_text(line):
    loc = line["location"] if line["location"] is not None else "(missing)"
    return (f"Title: {line['title']}\nLocation: {loc}\nURL: {line['url']}\nBoard: {line['board']}\n"
            f"Posting id: {line['posting_id']}\n\n{line['text']}\n")


def write_texts(tools, lines, run_id):
    paths = {}
    for ln in lines:
        p = text_path(run_id, ln["key"])
        tools.write_file(p, render_text(ln).encode("utf-8"))
        paths[ln["key"]] = p
    return paths


def sheet_bytes(comments, columns, rows):
    buf = io.StringIO()
    for c in comments:
        buf.write(f"# {c}\n")
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in columns})
    return buf.getvalue().encode("utf-8")


def write_sheet(tools, path, comments, columns, rows):
    tools.write_file(path, sheet_bytes(comments, columns, rows))


def parse_sheet(data):
    text = data.decode("utf-8")
    lines = text.splitlines(keepends=True)
    comments = []
    while lines and lines[0].startswith("# "):
        comments.append(lines.pop(0)[2:].rstrip("\n"))
    reader = csv.DictReader(io.StringIO("".join(lines)))
    rows = [dict(r) for r in reader]
    return comments, list(reader.fieldnames or []), rows


def read_sheet(tools, path):
    return parse_sheet(tools.read_file(path))


def exists(tools, path):
    try:
        tools.read_file(path)
    except FileNotFoundError:
        return False
    return True
