from opening_name import get_opening_name
from pgn import pgn_to_final_fen, pgn_to_uci_moves

pgn = """"
[Event "?"]
[Site "?"]
[Date "????.??.??"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]
[Link "https://www.chess.com/analysis"]

1. a4 e5 2. e4 Nc6 3. c3 d6 4. d4 f5 5. Bd3 f4 *
"""

sample_pgn = '"\n[Event "?"]\n[Site "?"]\n[Date "????.??.??"]\n[Round "?"]\n[White "?"]\n[Black "?"]\n[Result "*"]\n\n1. a4 e5 2. e4 Nc6 3. c3 d6 4. d4 f5 5. Bd3 f4 *"'
print(pgn_to_final_fen(pgn))
