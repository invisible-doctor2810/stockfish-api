# main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import chess
import chess.engine

app = Flask(__name__)
CORS(app)

ROOT = os.path.dirname(__file__)
ENGINE_PATH = os.path.join(ROOT, "stockfish", "stockfish_engine")  # <-- must match your render-build.sh output name

def _exists_and_executable(path: str) -> tuple[bool, str]:
    if not os.path.exists(path):
        return False, "not_found"
    try:
        os.chmod(path, 0o755)  # harmless if already executable
    except Exception as e:
        return False, f"chmod_failed:{e!r}"
    return True, "ok"

@app.get("/health")
def health():
    ok, status = _exists_and_executable(ENGINE_PATH)
    return jsonify(ok=ok, status=status, engine_path=ENGINE_PATH)

@app.get("/debug")
def debug():
    """Tiny engine smoke test at low depth."""
    ok, status = _exists_and_executable(ENGINE_PATH)
    if not ok:
        return jsonify(error="engine_missing", status=status, engine_path=ENGINE_PATH), 500
    try:
        board = chess.Board()  # start position
        with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as eng:
            eng.configure({"Threads": 1, "Hash": 64, "MultiPV": 1})
            info = eng.analyse(board, chess.engine.Limit(depth=6))
            score = info["score"].pov(board.turn)
            pv = " ".join(m.uci() for m in info.get("pv", []))
        return jsonify(ok=True, eval=score.score(mate_score=100000) if score.is_cp() else None, mate=score.mate(), pv=pv)
    except Exception as e:
        print("DEBUG engine error:", repr(e))
        return jsonify(error="engine_failure", detail=str(e)), 500

@app.get("/api/eval")
def api_eval():
    fen = (request.args.get("fen") or "").strip()
    try:
        depth = max(1, min(int(request.args.get("depth", 12)), 20))
        n     = max(1, min(int(request.args.get("n", 1)), 5))
    except ValueError:
        return jsonify({"error": "depth and n must be integers"}), 400

    if not fen:
        return jsonify({"error": "Missing FEN"}), 400

    try:
        board = chess.Board(fen)
    except Exception:
        return jsonify({"error": "Invalid FEN"}), 400

    ok, status = _exists_and_executable(ENGINE_PATH)
    if not ok:
        return jsonify({"error": "engine_missing", "status": status, "engine_path": ENGINE_PATH}), 500

    try:
        with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as eng:
            eng.configure({"Threads": 2, "Hash": 128, "MultiPV": n})
            info_list = eng.analyse(board, chess.engine.Limit(depth=depth), multipv=n)
            out = []
            for item in info_list:
                score = item["score"].pov(board.turn)
                cp = score.score(mate_score=100000) if score.is_cp() else None
                mate = score.mate()
                pv = " ".join(m.uci() for m in item.get("pv", []))
                out.append({"pv": pv, "eval": cp, "mate": mate})
            return jsonify({"top_moves": out})
    except Exception as e:
        print("API engine error:", repr(e))
        return jsonify({"error": "engine_failure"}), 500

import subprocess, json, base64, pathlib

@app.get("/probe/file")
def probe_file():
    p = pathlib.Path(ENGINE_PATH)
    exists = p.exists()
    size = p.stat().st_size if exists else 0
    head = b""
    if exists:
        with open(p, "rb") as f:
            head = f.read(4)  # ELF header should start with 0x7f,'E','L','F'
    return jsonify(
        engine_path=str(p),
        exists=exists,
        size_bytes=size,
        head_hex=head.hex(),  # expect: 7f454c46
        is_elf=head.startswith(b"\x7fELF")
    )

@app.get("/probe/run")
def probe_run():
    # Try to talk UCI to the binary directly (no python-chess involved)
    try:
        proc = subprocess.Popen(
            [ENGINE_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        out, _ = proc.communicate(input=b"uci\nquit\n", timeout=4)
        txt = out.decode("utf-8", "replace")
        return jsonify(ok=True, output=txt[:4000])
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

if __name__ == "__main__":
    # local dev
    app.run(host="0.0.0.0", port=8080)
