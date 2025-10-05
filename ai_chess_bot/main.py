from flask import Flask, request, jsonify
from flask_cors import CORS
from stockfish import Stockfish

app = Flask(__name__)
CORS(app)  # <-- this line enables CORS

# initialize Stockfish (adjust path if needed)
stockfish = Stockfish(path="./stockfish/stockfish", parameters={"Threads": 2, "Minimum Thinking Time": 30})

@app.route("/api/eval", methods=["GET"])
def evaluate():
    fen = request.args.get("fen")
    depth = int(request.args.get("depth", 15))
    n = int(request.args.get("n", 1))
    
    stockfish.set_fen_position(fen)
    stockfish.set_depth(depth)
    stockfish.update_engine_parameters({"MultiPV": n})

    info = stockfish.get_top_moves(n)
    return jsonify(info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)