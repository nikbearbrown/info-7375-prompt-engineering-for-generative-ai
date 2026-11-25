# Changes to this set (a dated log)

- **2026-11-24, before any verdict: the chat view.** Claude Code's first chat message with these 20 cards gave every
  fact line word for word but replaced each description with a short summary of its own. Claude Code had built the kit
  and knew each card's stratum, so a summary from it could lean one way; it withdrew that message a few minutes later,
  before Aravind sent any verdict, and sent the view in `CHAT-CARDS.md` instead. That view is made by
  `tools/chat_cards.py` from `CARDS.md` alone: every fact line, and the first 32 words of each description, the method
  of the earlier sets. Typing it into chat, Claude Code changed two dashes in the posting text to a colon or a comma
  (card 10's title, card 18's first words) and curly apostrophes to straight ones; no word differed.
