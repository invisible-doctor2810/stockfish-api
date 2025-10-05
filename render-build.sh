#!/usr/bin/env bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip

echo "Downloading Stockfish..."
# Official GitHub asset direct link (works with curl on Render)
curl -L -o stockfish.zip \
  https://github.com/official-stockfish/Stockfish/releases/download/sf_17/stockfish-ubuntu-x86-64-avx2.zip

echo "Verifying file size..."
ls -lh stockfish.zip

echo "Unzipping Stockfish..."
unzip stockfish.zip -d stockfish
chmod +x stockfish/stockfish*
mv stockfish/stockfish* stockfish_engine

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build complete."
