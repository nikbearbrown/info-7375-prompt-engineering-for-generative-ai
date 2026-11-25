"""Where each part of a posting's text sits.

The rules read one string per posting, `content` (built exactly as JS2 builds it). This module cuts
that string into blocks (a paragraph, a list item, a line) and says which section each block falls
under: benefits ('perk'), preferred ('pref'), requirements ('req'), responsibilities ('resp'),
about the company ('about'), legal text ('legal'), text before any heading ('intro') or another
heading ('other'). Rule 4 uses it so that a skill named only under a benefits heading does not count
(FILTER.md, wrong version 2).

Every block is a [start, end) slice of `content`, found by searching `content` itself, so a quote
taken from a block is always a real substring of the text the rules read. A block that cannot be
found in `content` is dropped rather than guessed.
"""
import html
import re

BLOCK_TAGS = ("p", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "br", "tr", "td",
              "th", "table", "section", "article", "header", "footer", "blockquote", "pre", "hr")
TAG_RE = re.compile(r"(<[^>]*>)")
TAG_NAME_RE = re.compile(r"<\s*(/?)\s*([a-zA-Z0-9]+)")
BOLD_ONLY_RE = re.compile(r"\s*(?:<(strong|b)\b[^>]*>.*?</\1\s*>\s*)+", re.IGNORECASE | re.DOTALL)

# Heading words, checked in this order; the first that matches names the section.
KINDS = [
    ("perk", re.compile(r"\b(benefits?|perks?|what we offer|we offer|our offer|compensation|salary|pay range|"
                        r"total rewards|why (?:join|work|you'?ll love)|what you(?:'ll| will)? get|"
                        r"what'?s in it for you|life at)\b", re.IGNORECASE)),
    ("legal", re.compile(r"\b(equal (?:employment )?opportunit(?:y|ies)|eeo|privacy|accommodations?|"
                         r"e-verify|disclaimer)\b", re.IGNORECASE)),
    ("pref", re.compile(r"\b(preferred|nice[- ]to[- ]haves?|bonus(?: points)?|pluses|a plus|desired|ideally|"
                        r"what we value)\b", re.IGNORECASE)),
    ("req", re.compile(r"\b(requirements?|qualifications?|what you(?:'ll| will)? bring|what we(?:'re| are)? looking for|"
                       r"what we require|who you are|about you|you have|you(?:'ll| will)? need|must[- ]haves?|"
                       r"skills|experience)\b", re.IGNORECASE)),
    ("resp", re.compile(r"\b(responsibilit(?:y|ies)|what you(?:'ll| will) do|the role|about the role|your role|"
                        r"day[- ]to[- ]day|in this role|the job|the opportunity)\b", re.IGNORECASE)),
    ("about", re.compile(r"\b(about (?:us|the (?:company|team))|who we are|our (?:mission|team|company|story)|"
                         r"the team|world-changing company)\b", re.IGNORECASE)),
]


def squash(s):
    return re.sub(r"\s+", " ", s or "").strip()


def kind_of(heading_text):
    for kind, rx in KINDS:
        if rx.search(heading_text):
            return kind
    return "other"


def looks_like_heading(text, hint=False):
    """A heading is a block the HTML marks as one (h1-h6, or wholly bold), or a short line ending in
    ':', or a line of six words or fewer, without end punctuation, that uses a heading word."""
    t = squash(text)
    if not t:
        return False
    words = t.rstrip(":").split()
    if hint and len(words) <= 12:
        return True
    if t.endswith(":") and len(words) <= 12:
        return True
    if len(words) <= 6 and t[-1] not in ".!?,;" and any(rx.search(t) for _, rx in KINDS):
        return True
    return False


def html_chunks(markup):
    """Split HTML at block-level tags. Returns [(text, heading_hint)], where text is made the way JS2
    makes `content` (tags become spaces, entities unescaped, whitespace squashed) so it can be found in
    `content`. markup must already be unescaped once (Greenhouse content is escaped once)."""
    chunks, cur, in_h = [], [], False

    def flush(hint):
        raw = "".join(cur)
        cur.clear()
        text = squash(html.unescape(re.sub(r"<[^>]+>", " ", raw)))
        if text:
            chunks.append((text, hint or bool(BOLD_ONLY_RE.fullmatch(raw))))

    for tok in TAG_RE.split(markup or ""):
        if not tok:
            continue
        m = TAG_NAME_RE.match(tok) if tok.startswith("<") else None
        if m and m.group(2).lower() in BLOCK_TAGS:
            flush(in_h)
            name = m.group(2).lower()
            if name.startswith("h") and len(name) == 2:
                in_h = not m.group(1)  # opening h-tag starts a heading, closing ends it
            continue
        cur.append(tok)
    flush(in_h)
    return chunks


def heading_texts(markup):
    return {t for t, hint in html_chunks(markup) if hint}


def plain_lines(text):
    return [line for line in re.split(r"\n+", text or "") if line.strip()]


def locate(content, pieces):
    """pieces: [(text, is_heading)]. Finds each piece in content, in order. Returns blocks as
    [start, end, is_heading] with content[start:end] == the piece (after whitespace squashing both)."""
    out, pos = [], 0
    norm_content = content
    for text, is_heading in pieces:
        t = text.strip()
        if not t:
            continue
        i = norm_content.find(t, pos)
        if i < 0:
            i = norm_content.find(t)  # out of order, still a real substring
        if i < 0:
            continue  # not found: dropped, never guessed
        out.append([i, i + len(t), bool(is_heading)])
        pos = i + len(t)
    return out


def classify(content, blocks):
    """Adds the section kind to each block: [start, end, kind, is_heading]."""
    kind, out = "intro", []
    for start, end, is_heading in sorted(blocks):
        if is_heading:
            kind = kind_of(content[start:end])
        out.append([start, end, kind, is_heading])
    return out


def blocks_for(ats, job, content):
    """The blocks of one raw job, for the content JS2 built from it."""
    if ats == "greenhouse":
        pieces = [(t, looks_like_heading(t, hint)) for t, hint in html_chunks(html.unescape(job.get("content") or ""))]
    elif ats == "ashby":
        heads = heading_texts(job.get("descriptionHtml") or "")
        if job.get("descriptionPlain"):
            pieces = [(line, squash(line) in heads or looks_like_heading(line)) for line in plain_lines(content)]
        else:
            pieces = [(t, looks_like_heading(t, hint)) for t, hint in html_chunks(job.get("descriptionHtml") or "")]
    elif ats == "lever":
        heads = heading_texts(job.get("description") or "")
        pieces = [(line, squash(line) in heads or looks_like_heading(line))
                  for line in plain_lines(job.get("descriptionPlain"))]
        for item in job.get("lists") or []:
            pieces.append((f"{item.get('text', '')}:", True))
            body = squash(html.unescape(re.sub(r"<[^>]+>", " ", item.get("content") or "")))
            pieces.append((body, False))
        heads_add = heading_texts(job.get("additional") or "")
        pieces += [(line, squash(line) in heads_add or looks_like_heading(line))
                   for line in plain_lines(job.get("additionalPlain"))]
    else:
        pieces = [(line, looks_like_heading(line)) for line in plain_lines(content)]
    return classify(content, locate(content, pieces))


def blocks_for_plain(content):
    """For a posting whose content is plain text with one block per line (tests, Ashby-like)."""
    return classify(content, locate(content, [(line, looks_like_heading(line)) for line in plain_lines(content)]))


def text_outside(content, blocks, kinds):
    """The content with every block of the given section kinds blanked out (same length, so
    positions still line up with content)."""
    chars = list(content)
    for start, end, kind, _ in blocks:
        if kind in kinds:
            chars[start:end] = " " * (end - start)
    return "".join(chars)
