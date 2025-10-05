from engine_config import get_best_move
from opening_name import get_opening_name
import google.generativeai as genai
from pgn import pgn_to_final_fen
from typewriter import typewriter

pgn = """"
[Event "?"]
[Site "?"]
[Date "????.??.??"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]
[Link "https://www.chess.com/analysis/game/pgn/5TNi6ErpPY/analysis?move=8"]

1. e4 Nf6 2. e5 Nd5 3. c4 Nb6 4. c5 Nd5 5. Bc4 *
"""
fen = pgn_to_final_fen(pgn)
moves = get_best_move(pgn, 10, 1)
for m in moves:
    typewriter(f"Move: {m['move']}, Eval: {m['eval']}" , 0.009)
    print()
    typewriter(f"Opening: {get_opening_name(pgn=pgn)}" , 0.009)
    print()
    typewriter(f"Commentary: {m['commentary']}\n" , 0.009)