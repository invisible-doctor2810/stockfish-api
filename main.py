from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import chess
import chess.engine
import concurrent.futures

app = Flask(__name__)
CORS(app)

# Path to the engine that render-build.sh placed
ROOT = os.path.dirname(os.path.abspath(__file__))
ENGINE_PATH = os.path.join(ROOT, "stockfish", "stockfish_engine")

@app.get("/")
def home():
    return "OK"

@app.get("/health")
def health():
    ok = os.path.exists(ENGINE_PATH)
    return jsonify(ok=ok, engine_path=ENGINE_PATH)

@app.get("/debug")
def debug():
    """Tiny self-test on the start position."""
    try:
        board = chess.Board()  # initial position
        with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as eng:
            eng.configure({"Threads": max(1, (os.cpu_count() or 2) // 2), "Hash": 256})
            info = eng.analyse(board, chess.engine.Limit(depth=8))
            score = info["score"].pov(chess.WHITE)
            pv = " ".join(m.uci() for m in info.get("pv", []))
        return jsonify(eval=score.score(mate_score=100000), pv=pv)
    except Exception as e:
        return jsonify(error="engine_failure", detail=str(e)), 500

# --- constants ---
MAX_DEPTH = 20          # hard ceiling if you still want to allow depth
MAX_N = 3               # cap number of lines
MOVE_TIME_MS = 2000     # think ~2s per request on free tier
ENGINE_THREADS = 1
ENGINE_HASH_MB = 64

@app.route("/api/eval", methods=["GET"])
def api_eval():
    fen = request.args.get("fen", type=str)
    req_depth = request.args.get("depth", default=12, type=int)
    req_n = request.args.get("n", default=1, type=int)

    if not fen:
        return jsonify({"error": "missing fen"}), 400

    # Clamp user inputs
    n = max(1, min(req_n, MAX_N))
    depth = max(2, min(req_depth, MAX_DEPTH))

    try:
        board = chess.Board(fen)
    except Exception:
        return jsonify({"error": "invalid_fen"}), 400

    # Spin up engine per request (simple + safe on free tier)
    try:
        with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as eng:
            eng.configure({
                "Threads": ENGINE_THREADS,
                "Hash": ENGINE_HASH_MB,
                # DO NOT set MultiPV here; python-chess manages it when you pass multipv=
            })

            # Prefer time-based limit (more predictable on small machines)
            limit = chess.engine.Limit(time=MOVE_TIME_MS / 1000.0)

            infos = eng.analyse(board, limit, multipv=n)

        top_moves = []
        for info in infos:
            # best line (PV) as space-separated UCI
            pv_moves = " ".join(m.uci() for m in info.get("pv", []))
            
            # centipawn or mate score with a consistent POV
            # Use side-to-move POV: positive means good for the player to move.
            score = info.get("score")
            cp = None
            mate = None
            if score is not None:
                pov = score.pov(board.turn)           # or chess.WHITE if you always want White POV
                mate = pov.mate()
                if mate is None:
                    cp = pov.score(mate_score=100000)
            
            top_moves.append({
                "pv": pv_moves,
                "cp": cp,           # <-- key name your client expects
                "mate": mate
            })

        return jsonify({"top_moves": top_moves})
    except concurrent.futures.TimeoutError:
        return jsonify({"error": "engine_timeout"}), 504
    except Exception:
        # last-resort guard
        return jsonify({"error": "engine_failure"}), 500

if __name__ == "__main__":
    # Local dev only; Render uses Gunicorn with Procfile
    app.run(host="0.0.0.0", port=8080)
