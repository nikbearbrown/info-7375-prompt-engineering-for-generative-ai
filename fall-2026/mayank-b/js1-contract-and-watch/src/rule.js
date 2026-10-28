// THE RULE (CONTRACT.md, The rule). A record: anyone can recompute it from the posting and the persona.

const escapeRegExp = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const collapse = (s) => String(s).replace(/\s+/g, " ").trim();

// Whole-word, case-insensitive: the characters on either side must not be letters or digits.
// This is what W1 is about: "Intern" must not match "Internal", "Lead" must not match "Leadership".
export function matchesTerm(text, term) {
  const pattern = collapse(term).split(" ").map(escapeRegExp).join(" ");
  return new RegExp(`(?<![\\p{L}\\p{N}])${pattern}(?![\\p{L}\\p{N}])`, "iu").test(collapse(text));
}

export function splitLocations(locationName) {
  return String(locationName ?? "")
    .split(/[|;]/)
    .map((s) => s.trim())
    .filter(Boolean);
}

const sameText = (a, b) => a.toLowerCase() === b.toLowerCase();

function locationCheck(pieces, persona) {
  const { location } = persona.personal;
  const { open_to_relocate, open_to_remote } = persona.search;
  for (const piece of pieces) {
    if (sameText(piece, location)) return { passed: piece, because: `equals personal.location "${location}"` };
    const relocate = open_to_relocate.find((city) => sameText(piece, city));
    if (relocate) return { passed: piece, because: `is in search.open_to_relocate` };
    if (open_to_remote && matchesTerm(piece, "Remote") && matchesTerm(piece, "United States"))
      return { passed: piece, because: `contains "Remote" and "United States" and search.open_to_remote is true` };
  }
  return { passed: null };
}

export function judgeByRule(posting, persona) {
  const title = collapse(posting.title);
  const included = persona.search.target_titles.find((t) => matchesTerm(title, t)) ?? null;
  const excluded = persona.search.exclude_titles.find((t) => matchesTerm(title, t)) ?? null;
  const pieces = splitLocations(posting.location?.name);
  const loc = locationCheck(pieces, persona);
  const relevant = Boolean(included) && !excluded && Boolean(loc.passed);

  const parts = [
    included
      ? `posting title "${title}" matched search.target_titles term "${included}"`
      : `posting title "${title}" matched no search.target_titles term`,
    excluded
      ? `it matched search.exclude_titles term "${excluded}"`
      : `it matched no search.exclude_titles term`,
    loc.passed
      ? `posting location.name piece "${loc.passed}" ${loc.because}`
      : `no posting location.name piece (${pieces.map((p) => `"${p}"`).join(", ") || "none"}) matched personal.location "${persona.personal.location}", search.open_to_relocate, or remote United States`,
  ];

  return {
    kind: "record",
    verdict: relevant ? "relevant" : "not_relevant",
    justification: parts.join("; ") + ".",
    evidence: { include_matched: included, exclude_matched: excluded, locations: pieces, location_passed: loc.passed },
  };
}
