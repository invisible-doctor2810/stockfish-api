#!/usr/bin/env bash
set -e

echo "Downloading Stockfish binary from GitHub Release..."
mkdir -p stockfish
cd stockfish

# ⬇️ Replace the URL below with the exact asset URL you copied in Step 1
curl -L -o stockfish_engine "https://github.com/invisible-doctor2810/stockfish-api/releases/download/v-sf-bin-1/stockfish-ubuntu-x86-64-avx2"

chmod +x stockfish_engine
cd ..

echo "Installing Python deps..."
pip install -r requirements.txt

echo "✅ Build complete."
