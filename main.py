from flask import Flask, request, jsonify
from flask_cors import CORS
from stockfish import Stockfish
import os
import threading

app = Flask(__name__)
CORS(app)

# ----- Adjust this if your build script names the file differently -----
# If render-build.sh saves to ./stockfish/stockfish_engine, use that.
ENGINE_PATH = os.path.join("stockfish", "stockfish-ubuntu-x86-64-avx2")
# ENGINE_PATH = os.path.join("stockfish", "stockfish_engine")

# Sanity check: make sure the binary exists at startup (helps catch bad builds)
if not os.path.exists(ENGINE_PATH):
    raise FileNotFoundError(f"Stockfish binary not found at: {ENGINE_PATH}")

# Create one engine instance per process and guard access with a lock.
# (Gunicorn may run multiple workers; each worker gets its own instance.)
stockfish = Stockfish(
    path=ENGINE_PATH,
    parameters={"Threads": 2, "Minimum Thinking Time": 30}
)
engine_lock = threading.Lock()

@app.get("/")
def root():
    return jsonify({"ok": True, "service": "stockfish-api"})

@app.get("/api/eval")
def evaluate():
    fen = request.args.get("fen")
    if not fen:
        return jsonify({"error": "Missing FEN"}), 400

    try:
        depth = int(request.args.get("depth", 15))
        n = int(request.args.get("n", 1))
        if n < 1:
            n = 1
    except ValueError:
        return jsonify({"error": "depth and n must be integers"}), 400

    with engine_lock:
        stockfish.set_fen_position(fen)
        stockfish.set_depth(depth)
        # python-stockfish manages MultiPV; this is the supported way:
        stockfish.update_engine_parameters({"MultiPV": n})
        top = stockfish.get_top_moves(n)

    # Normalize response (ensure list)
    return jsonify(top if isinstance(top, list) else [top])

if __name__ == "__main__":
    # For local testing only; Render will use gunicorn per your Procfile
    app.run(host="0.0.0.0", port=8080)
