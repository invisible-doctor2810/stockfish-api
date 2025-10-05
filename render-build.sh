#!/usr/bin/env bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip

echo "Downloading Stockfish..."
curl -L -o stockfish.zip https://github.com/official-stockfish/Stockfish/releases/download/sf_17/stockfish-ubuntu-x86-64-avx2.zip

echo "Unzipping Stockfish..."
unzip stockfish.zip -d stockfish
chmod +x stockfish/stockfish-ubuntu-x86-64-avx2
mv stockfish/stockfish-ubuntu-x86-64-avx2 stockfish_engine

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build complete."
