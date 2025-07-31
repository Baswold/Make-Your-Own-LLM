#!/bin/bash

# Make Your Own LLM - Easy Startup Script
set -e

echo "🚀 Make Your Own LLM - Easy Setup & Start"
echo "========================================"

# Check if dependencies are installed
echo "📋 Checking environment..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found. Please install Python 3.11+"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ node not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check if this is first run
if [ ! -d "frontend/node_modules" ] || [ ! -d "data" ]; then
    echo ""
    echo "🔧 First-time setup detected. Installing dependencies..."
    make setup
    echo "✅ Setup complete!"
fi

echo ""
echo "🚀 Starting development servers..."
echo ""
echo "This will start:"
echo "  • Training API on http://localhost:8000"
echo "  • Chat API on http://localhost:8001"
echo "  • Frontend on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo "Using tmux session 'llm-dev'..."
    make dev
    echo ""
    echo "✅ All servers started in tmux session 'llm-dev'"
    echo "📱 Open http://localhost:3000 in your browser"
    echo "🔧 Attach to session with: tmux attach-session -t llm-dev"
    echo "🛑 Kill session with: tmux kill-session -t llm-dev"
else
    echo "⚠️  tmux not found. Starting servers individually..."
    echo "Note: Install tmux for better session management"
    echo ""
    
    # Start servers in background
    echo "Starting training server..."
    cd backend && python3 train.py &
    TRAIN_PID=$!
    
    echo "Starting chat server..."
    python3 serve.py &
    SERVE_PID=$!
    cd ..
    
    echo "Starting frontend..."
    cd frontend && npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ All servers started!"
    echo "📱 Open http://localhost:3000 in your browser"
    echo ""
    echo "Press Ctrl+C to stop all servers"
    
    # Wait for interrupt
    trap "echo ''; echo '🛑 Stopping all servers...'; kill $TRAIN_PID $SERVE_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
    wait
fi