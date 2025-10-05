#!/usr/bin/env bash
set -e  # stop on error

echo "=== Starting Render build ==="
echo "Installing dependencies..."

# Make sure we have wget and unzip
apt-get update && apt-get install -y wget unzip

echo "Downloading Stockfish..."
mkdir -p stockfish
cd stockfish

# Download latest Stockfish AVX2 build for Linux
wget https://stockfishchess.org/files/stockfish-ubuntu-x86-64-avx2.zip -O stockfish.zip

echo "Unzipping Stockfish..."
unzip -o stockfish.zip
rm stockfish.zip

echo "Making Stockfish executable..."
chmod +x stockfish-ubuntu-x86-64-avx2

cd ..

echo "=== Stockfish setup complete ==="
