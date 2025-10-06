from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import chess
import chess.engine

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

@app.get("/api/eval")
def api_eval():
    fen = (request.args.get("fen") or "").strip()
    try:
        depth = int(request.args.get("depth", 15))
        n = int(request.args.get("n", 1))
    except ValueError:
        return jsonify(error="bad_query", detail="depth and n must be integers"), 400

    # Clamp to safe bounds on Render free instances
    depth = max(1, min(depth, 22))
    n = max(1, min(n, 5))

    # Validate FEN early
    try:
        board = chess.Board(fen)
    except Exception as e:
        return jsonify(error="bad_fen", detail=str(e), fen=fen), 400

    try:
        # Start a fresh engine for this request (avoids cross-request races/crashes)
        with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as eng:
            eng.configure({
                "Threads": max(1, (os.cpu_count() or 2) // 2),
                "Hash": 256,
                "MultiPV": n
            })
            # Ask for MultiPV lines in a single call
            infos = eng.analyse(board, chess.engine.Limit(depth=depth), multipv=n)

            top = []
            for info in infos:
                sc = info["score"].pov(board.turn)
                cp = sc.score(mate_score=100000)
                pv = " ".join(m.uci() for m in info.get("pv", []))
                item = {"eval": cp, "pv": pv}
                if sc.is_mate():
                    # Report mate distance (positive = mate for side to move)
                    item["mate"] = sc.mate()
                top.append(item)

        return jsonify(fen=fen, depth=depth, top_moves=top)

    except Exception as e:
        # Any unexpected engine/IO error
        return jsonify(error="engine_failure", detail=str(e)), 500

if __name__ == "__main__":
    # Local dev only; Render uses Gunicorn with Procfile
    app.run(host="0.0.0.0", port=8080)
