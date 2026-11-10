// Text normalisation shared by the rule (CONTRACT.md, "The rule"): HTML decoded,
// tags stripped, case lowered. Block-level tags become line breaks so that list
// items and paragraphs stay separate sentences for Gate 3.

const NAMED = { lt: '<', gt: '>', amp: '&', quot: '"', apos: "'", nbsp: ' ', ndash: '–', mdash: '—', rsquo: '’', lsquo: '‘', rdquo: '”', ldquo: '“', hellip: '…' };

export function decodeEntities(s) {
  return String(s ?? '').replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
    if (e[0] === '#') {
      const code = e[1].toLowerCase() === 'x' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      return Number.isFinite(code) ? String.fromCodePoint(code) : m;
    }
    return NAMED[e.toLowerCase()] ?? m;
  });
}

// Greenhouse returns `content` HTML-escaped ("&lt;p&gt;"), so decode first, then strip.
export function plainText(html) {
  let s = decodeEntities(html);
  s = s.replace(/<\s*(br|\/p|\/li|\/div|\/h[1-6]|\/ul|\/ol|li|p|div|h[1-6])\b[^>]*>/gi, '\n');
  s = s.replace(/<[^>]*>/g, ' ');
  s = decodeEntities(s); // entities that were double-escaped
  s = s.replace(/[ \t ]+/g, ' ').replace(/ *\n */g, '\n').replace(/\n{2,}/g, '\n');
  return s.trim();
}

export function contentText(html) {
  return plainText(html).toLowerCase();
}

// Sentences for Gate 3: split on line breaks and on . ! ? followed by whitespace.
export function sentences(text) {
  return text.split(/\n+|(?<=[.!?])\s+/).map(x => x.trim()).filter(Boolean);
}
