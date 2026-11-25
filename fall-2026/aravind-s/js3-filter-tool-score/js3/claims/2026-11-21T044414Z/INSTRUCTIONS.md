# How to label the claims

1. Open LABELS.md. Each posting on the shortlist has one row per claim: what the shortlist claims, and the passages that bear on it, copied word for word from the posting as saved on 2026-11-20. Label from the passages. The link opens today's posting, which may have changed or closed; if you use it, say so in the note.
2. Put an x in one column per row (FILTER.md Section 2):
   - **Supported:** a passage states the claim, within its scope: the same role, the same place, the same time.
   - **Contradicted:** a passage states something that cannot be true at the same time as the claim.
   - **Insufficient:** the passages are on the topic but do not settle the claim, or there are none. The note names what is missing. Silence is never support: "none found" means the posting does not say, so the claim cannot be supported.
   - A row left blank stays **not reviewed**.
3. Jane (fictional) is an F-1 student, not a U.S. person, who will need H-1B sponsorship later; her earliest full-time start is May 2027; she has 3 years of full-time experience. Her areas: California, Austin, Boston, Cambridge, New York, Seattle, Bellevue, Redmond, or US remote ("US - Remote", "Remote - US", "United States - Remote").
4. Claim 5 covers three requirements at once, as Section 5 writes it: Contradicted if the posting states any one of them, Supported only if its text says the role is open on status (for example, that it sponsors visas), otherwise Insufficient. Claims 3 and 4 are about the title's words; claim 8 is about the quoted sentence: does it say this role's work is in that topic group?
5. Only you may mark a claim supported, and you label each row yourself first (chapter 7). Do not open `sealed/checker-labels.json` until your labels are committed.
6. After that commit, Claude Code computes how often the checker agrees with you, by claim type. For each row where you disagree, Claude finds the sentence that would change your label, and you record whether it did.
