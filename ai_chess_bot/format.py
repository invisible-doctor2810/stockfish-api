import chess

def format_move(uci_move: str, fen: str) -> str:
    """
    Convert a UCI move into human-readable SAN (algebraic chess notation).
    Handles pawn moves, piece moves, captures, castling, promotions, etc.

    :param uci_move: Move in UCI notation (e.g., 'e2e4', 'g1f3')
    :param fen: Current board position in FEN format
    :return: Move in SAN notation (e.g., 'e4', 'Nf3', 'O-O', 'e8=Q')
    """
    board = chess.Board(fen)
    move = chess.Move.from_uci(uci_move)

    if move not in board.legal_moves:
        return uci_move  # fallback if invalid or unknown

    return board.san(move)
