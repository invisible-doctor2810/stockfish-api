from flask import Flask, request, jsonify
from flask_cors import CORS
from stockfish import Stockfish
import os

app = Flask(__name__)
CORS(app)

# Path to your binary built in render-build.sh
ENGINE_BIN = os.path.join(os.path.dirname(__file__), "stockfish", "stockfish_engine")

# Create one Stockfish process; cheap CPU on free tier, keep Hash small
stockfish = Stockfish(path=ENGINE_BIN, parameters={"Threads": 2, "Hash": 64})

@app.route("/", methods=["GET"])
def root():
    return jsonify({"ok": True})

@app.route("/api/eval", methods=["GET"])
def api_eval():
    fen = request.args.get("fen", "").strip()
    try:
        depth = int(request.args.get("depth", 15))
        n     = int(request.args.get("n", 1))
    except ValueError:
        return jsonify({"error": "depth and n must be integers"}), 400

    # Clamp to protect the tiny Render CPU
    depth = max(1, min(depth, 22))
    n     = max(1, min(n, 5))

    if not fen:
        return jsonify({"error": "Missing fen"}), 400

    # Validate FEN with stockfish (returns False on invalid)
    if not stockfish.set_fen_position(fen):
        return jsonify({"error": "Invalid FEN"}), 400

    # Apply MultiPV safely
    stockfish.update_engine_parameters({"MultiPV": n})

    try:
        # This returns a list of dicts with keys Move/Centipawn/Mate/Line
        top = stockfish.get_top_moves(n)
        # Normalize to a stable shape
        norm = []
        for item in top or []:
            pv_line = item.get("Line") or item.get("Move") or ""
            norm.append({
                "pv":   pv_line.strip(),
                "cp":   item.get("Centipawn"),
                "mate": item.get("Mate")
            })
        return jsonify({"top_moves": norm})
    except Exception as e:
        # Log and return 500 with a short reason
        print("Engine error:", repr(e))
        return jsonify({"error": "engine_failure"}), 500
