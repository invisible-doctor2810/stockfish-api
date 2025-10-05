#!/usr/bin/env bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip

echo "Downloading Stockfish (Linux AVX2 build)..."
# Use GitHub API asset endpoint (bypasses HTML redirect issues)
curl -L -o stockfish.tar \
  https://api.github.com/repos/official-stockfish/Stockfish/releases/assets/186873196 \
  -H "Accept: application/octet-stream"

echo "Verifying file size..."
ls -lh stockfish.tar

echo "Extracting Stockfish..."
mkdir -p stockfish
tar -xvf stockfish.tar -C stockfish --wildcards --no-anchored 'stockfish*'

chmod +x stockfish/stockfish*
mv stockfish/stockfish* stockfish_engine

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build complete."
