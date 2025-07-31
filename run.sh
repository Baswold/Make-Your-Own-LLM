#!/bin/bash

# Super Simple LLM Launcher
# Just double-click this file or run: ./run.sh

echo "🚀 Starting your LLM project..."

# Kill any existing servers first
echo "🧹 Cleaning up any existing servers..."
pkill -f "train.py" 2>/dev/null || true
pkill -f "serve.py" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

# Start everything
echo "🚀 Starting all servers..."
./start.sh

echo "✅ Done! Your LLM is ready at http://localhost:3000"
