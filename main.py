@app.route("/api/eval", methods=["GET"])
def api_eval():
    fen = (request.args.get("fen") or "").strip()

    # Parse & clamp
    try:
        depth = int(request.args.get("depth", 15))
        n     = int(request.args.get("n", 1))
    except ValueError:
        return jsonify({"error": "depth and n must be integers"}), 400

    depth = max(1, min(depth, 22))
    n     = max(1, min(n, 5))

    if not fen:
        return jsonify({"error": "Missing fen"}), 400

    if not stockfish.set_fen_position(fen):
        return jsonify({"error": "Invalid FEN"}), 400

    # DO NOT set MultiPV here with 3.28+ (it will raise)
    # stockfish.update_engine_parameters({"MultiPV": n})  # <-- remove this

    try:
        # Optional: honor requested depth (python-stockfish supports set_depth)
        try:
            stockfish.set_depth(depth)
        except Exception:
            pass  # harmless if this build doesn't expose set_depth

        top = stockfish.get_top_moves(n)  # python-stockfish sets MultiPV itself

        out = []
        for it in top or []:
            # Keys vary across versions: Line or PV, Move present for first move
            pv = (it.get("Line") or it.get("PV") or it.get("Move") or "").strip()
            out.append({
                "pv":   pv,
                "cp":   it.get("Centipawn"),
                "mate": it.get("Mate"),
            })
        return jsonify({"top_moves": out})
    except Exception as e:
        print("Engine error:", repr(e))  # shows exact reason in Render logs
        return jsonify({"error": "engine_failure"}), 500
