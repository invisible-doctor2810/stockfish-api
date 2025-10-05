import chess.pgn
import io
import re

def pgn_to_uci_moves(pgn_text: str) -> str:
    """
    Convert a PGN string to a comma-separated string of UCI moves (PV format).
    
    :param pgn_text: PGN game as string
    :return: UCI moves as a string, e.g., "e2e4,e7e5,g1f3"
    """
    pgn_text = pgn_text.strip().lstrip('"').rstrip('"')
    pgn_io = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_io)

    if game is None:
        return ""

    board = game.board()
    uci_moves = []

    for move in game.mainline_moves():
        uci_moves.append(move.uci())  # UCI format

    moves = ",".join(uci_moves)
    return moves


def pgn_to_final_fen(pgn_text: str) -> str:
    """
    Convert a PGN string to the final FEN position of the game.
    
    :param pgn_text: PGN game as string
    :return: FEN string of final position
    """
    # Clean up messy input (quotes, bytes, etc.)
    pgn_text = pgn_text.strip()
    pgn_text = re.sub(r'^[bB]?["\']', '', pgn_text).strip('"').strip("'")

    # Ensure valid PGN structure
    if not pgn_text.strip().startswith("["):
        pgn_text = "[Event '?']\n\n" + pgn_text
    if not pgn_text.strip().endswith(("*", "1-0", "0-1", "1/2-1/2")):
        pgn_text += " *"

    # Parse PGN
    pgn_io = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_io)
    if game is None:
        return "Invalid PGN"

    # Play all moves to reach final position
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
    
    return board.fen()