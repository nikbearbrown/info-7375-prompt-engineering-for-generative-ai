# FRICTIONAL — Final Project Film

Arundhati Kandelkar · my own dated entries, in my own words. (Claude's technical log is in [BUILD-LOG.md](BUILD-LOG.md); the code changes below were written by Claude Code on my instruction — see [SOURCES.md](SOURCES.md).)

## November 23, 2026

### Predictions vs. Results

#### What I tried

I tested the brand-name matching problem using Robinhood, SoFi, and Chime. I also explored OpenSanctions and GLEIF to see how existing tools handle brand names and legal company names.

#### What happened

OpenSanctions returned multiple related entities for Robinhood and SoFi, but my Chime search did not show Chime Financial Inc. in the results I reviewed.

GLEIF returned ROBINHOOD MARKETS, INC. for Robinhood and SOCIAL FINANCE, LLC for SoFi. It also showed SOCIAL FINANCE, INC. as a previous legal name.

For my own tool, I predicted that first-word matching would find Robinhood and Chime, while SoFi would need an alias. That prediction was correct.

I also predicted that there might be a few extra candidates. The actual result was exactly three additional companies: Plaid, Ramp, and Coinbase. All were sent for human review without automatic approval.

#### What I changed

* Added first-word candidate matching. If a search term matches the first whole word or words of a company name, the company is listed as a candidate. For example, searching for Chime now lists CHIME FINANCIAL INC and CHIME INC. Whole-word matching prevents unrelated matches such as ARCHIMEDES.
* Added `inputs/brand-aliases.json` with a SoFi → Social Finance alias to handle brands that do not appear in their legal company names.
* Added human verification for every non-exact match. The tool no longer automatically selects a candidate, even when there is only one result.
* Added a match explanation for each candidate: exact name, first word, or alias.

#### Testing and results

I added 8 new tests and rewrote one existing test. The old ACME test expected no results, but the updated behavior lists matching ACME companies for human review.

Before the fix, 9 tests failed. After the fix, all 26 tests passed.

On the same 25-company evaluation set:

* Strong sponsors missed: 3 → 0
* Wrong automatic answers: 1 → 0
* Companies sent for human review: 0 → 6

The results matched my main predictions. The extra candidates were exactly three, rather than just an estimated few, and all required human approval.

## November 23, 2026 — Brand Search Improvements

#### What I predicted and decided

I answered the five prediction questions in my own words rather than selecting predefined options. I reviewed the proposed brand-search improvements and accepted the two-part design:

* First-word candidates: Search terms matching the first complete word(s) of a company name should return that company as a candidate. For example, searching `Chime` should return CHIME FINANCIAL INC and CHIME INC, without incorrectly matching ARCHIMEDES.
* Alias list: Use a separate alias list to support alternative company names, such as SoFi and Social Finance.

I also agreed that non-exact matches should require human verification rather than being treated as confirmed matches.

#### What I changed after reviewing Claude's suggestions

Claude pointed out that my original Chime explanation was stronger than what my search notes actually demonstrated. The first-word matching change also surfaced three additional companies for human review: Plaid, Ramp, and Coinbase. None was automatically approved. These results show that the search can discover more possible matches, but they do not confirm that each legal entity is the same employer represented by the corresponding brand or hub entry.

I accepted the proposed implementation but retained responsibility for reviewing the reasoning and the resulting changes.

#### Unresolved

Still unresolved: The USCIS hub join has not been run. The Plaid mapping (PLAID TECHNOLOGIES INC vs. PLAID INC) also remains unconfirmed. Ramp and Coinbase have stronger public legal-entity matches, but their equivalence to the specific hub records still needs human confirmation.
