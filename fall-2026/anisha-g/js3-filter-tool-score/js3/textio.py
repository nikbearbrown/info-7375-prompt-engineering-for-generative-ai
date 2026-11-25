"""HTML -> plain text. Greenhouse 'content' is HTML that is itself HTML-escaped, so it is unescaped, stripped, unescaped again."""
import html, re
_BLOCK = re.compile(r"</?(p|div|br|li|ul|ol|h[1-6]|tr|section|header)\b[^>]*>", re.I)
def html_to_text(s):
    if not s: return ""
    s = html.unescape(s)
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.I | re.S)
    s = _BLOCK.sub("\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", l).strip() for l in s.splitlines()]
    return "\n".join(l for l in lines if l)
