from flask import Flask, request, jsonify
from flask_cors import CORS
from stockfish import Stockfish
import os

# --- create app first ---
app = Flask(__name__)
CORS(app)

# --- engine path from your render-build.sh (placed at stockfish/stockfish_engine) ---
ENGINE_PATH = os.path.join(os.path.dirname(__file__), "stockfish", "stockfish_engine")

if not os.path.exists(ENGINE_PATH):
    raise FileNotFoundError(f"Stockfish binary not found at: {ENGINE_PATH}")
os.chmod(ENGINE_PATH, 0o755)

# --- init stockfish (do NOT set MultiPV here; python-stockfish manages it) ---
stockfish = Stockfish(
    path=ENGINE_PATH,
    parameters={"Threads": 2, "Minimum Thinking Time": 30}
)

@app.get("/")
def health():
    return jsonify(ok=True)

@app.get("/api/eval")
def api_eval():
    fen = (request.args.get("fen") or "").strip()
    try:
        depth = int(request.args.get("depth", 15))
        n     = int(request.args.get("n", 1))
    except ValueError:
        return jsonify({"error": "depth and n must be integers"}), 400

    depth = max(1, min(depth, 22))
    n     = max(1, min(n, 5))

    if not fen:
        return jsonify({"error": "Missing FEN"}), 400
    if not stockfish.set_fen_position(fen):
        return jsonify({"error": "Invalid FEN"}), 400

    try:
        # some versions expose set_depth; if not, it's harmless to skip
        try:
            stockfish.set_depth(depth)
        except Exception:
            pass

        top = stockfish.get_top_moves(n) or []
        out = []
        for it in top:
            pv = (it.get("Line") or it.get("PV") or it.get("Move") or "").strip()
            out.append({
                "pv":   pv,
                "eval": it.get("Centipawn"),
                "mate": it.get("Mate"),
            })
        return jsonify({"top_moves": out})
    except Exception as e:
        print("Engine error:", repr(e))
        return jsonify({"error": "engine_failure"}), 500

# no __main__ block needed on Render (gunicorn runs main:app)
