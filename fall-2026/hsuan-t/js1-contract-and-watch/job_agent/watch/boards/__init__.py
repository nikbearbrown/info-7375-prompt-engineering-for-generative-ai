"""Board adapters: each module turns one job board's JSON into Postings (common/posting.py).

Supporting another public board (Ashby, Lever...) means adding one module here that offers
board_url(board) and parse(body); the watch and the judges don't change.
"""
