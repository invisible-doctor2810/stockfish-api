#!/usr/bin/env bash
echo "Downloading Stockfish..."
mkdir -p stockfish
cd stockfish

wget https://stockfishchess.org/files/stockfish-ubuntu-x86-64-avx2.zip -O stockfish.zip
unzip stockfish.zip
rm stockfish.zip
chmod +x stockfish-ubuntu-x86-64-avx2

cd ..
