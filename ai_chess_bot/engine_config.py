import requests
from format import format_move
from commentary import explain_move
from pgn import pgn_to_final_fen

moves_list = []

def get_data(pgn: str, depth: int = 15, topmoves: int = 1):
    fen = pgn_to_final_fen(pgn)
    url = "https://84b18806-ff7e-4a63-9d28-fc49bde547c8-00-3qqw7zn8f2iey.spock.replit.dev/api/eval"
    params = {"fen": fen, "depth": depth, "n": topmoves}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Use top_moves from new API
        top_moves = data.get("top_moves", [])

        pvs = []
        for move_info in top_moves:
            pvs.append({
                "moves": move_info.get("pv", ""),  # PV string
                "cp": move_info.get("eval", 0)     # centipawn eval
            })

        return {"pvs": pvs}

    except requests.RequestException as e:
        print("Error fetching from Stockfish API:", e)
        return {"pvs": []}
        
def get_best_move(pgn: str, depth: int = 15, topmoves: int = 1):
    """
    Query Lichess Stockfish Cloud API for the best move(s) in a given position
    and get commentary from DeepSeek.

    :param fen: Board position in FEN notation
    :param depth: Engine depth (default 15)
    :param topmoves: Number of top moves to return
    :return: List of dicts with keys: move, eval, line, commentary
    """
    
    try:
        data = get_data(pgn, depth, topmoves)
        if "pvs" in data and data["pvs"]:
            for pv in data["pvs"][:topmoves]:
                move_uci = pv["moves"].split()[0]   # first move in the line
                move_san = format_move(move_uci, pgn_to_final_fen(pgn))  # convert UCI → SAN

                # Get evaluation
                eval_cp = pv.get("cp", None)
                if eval_cp is not None:
                    eval_str = f"{eval_cp/100:.2f}"
                elif "mate" in pv:
                    eval_str = f"# {pv['mate']}"
                else:
                    eval_str = "?"

                # Get AI commentary
                commentary = explain_move(pgn, move_san, eval_str)

                moves_list.append({
                    "move": move_san,
                    "eval": eval_str,
                    "line": pv["moves"]
                    ,"commentary": commentary
                })

        return moves_list
    except requests.exceptions.RequestException as e:
        print("Error fetching move:", e)
        return moves_list  # return empty list instead of None
