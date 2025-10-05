#!/usr/bin/env bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip

echo "Downloading Stockfish binary..."
mkdir -p stockfish
cd stockfish

# Direct link to binary release (not zip/tar)
curl -L -o stockfish_engine \
  https://stockfishchess.org/files/stockfish-ubuntu-x86-64-avx2

chmod +x stockfish_engine
cd ..

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build complete."
