import requests
import chess
from engine_config import get_data
from pgn import pgn_to_uci_moves

def uci_to_san(fen: str) -> str:
    """
    Convert a space-separated UCI move string to SAN moves.
    :param pv_uci: e.g., "e2e4 e7e5 g1f3"
    :param fen: starting FEN (default start position)
    :return: list of SAN moves
    """
    board = chess.Board(fen)
    san_moves = []
    pv_uci = get_data(fen)["pvs"][0]["moves"]
    for uci_move in pv_uci.split():
        move = board.parse_uci(uci_move)
        san = board.san(move)
        san_moves.append(san)
        board.push(move)
    return san_moves

import requests

def get_opening_name(pgn: str) -> str:
    """
    Query Lichess Opening Explorer to get opening/variation name.
    """
    moves = pgn_to_uci_moves(pgn)
    base_url = f"https://explorer.lichess.ovh/masters?play={moves}"

    try:
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return (data.get("opening") or {}).get("name", "Unknown Opening")
    except requests.RequestException as e:
        print("Error querying opening API:", e)
        return "Unknown Opening"