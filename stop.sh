#!/bin/bash

# Stop script for Make Your Own LLM
echo "🛑 Make Your Own LLM - Stopping Servers"
echo "======================================"

# Kill tmux session if it exists
if tmux has-session -t llm-dev 2>/dev/null; then
    echo "🎯 Stopping tmux session 'llm-dev'..."
    tmux kill-session -t llm-dev
    echo "✅ Tmux session stopped"
else
    echo "⚠️  No tmux session 'llm-dev' found"
fi

# Kill any remaining processes on the ports
echo "🔍 Checking for remaining processes..."

for port in 3000 8000 8001; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "🎯 Killing process on port $port (PID: $PID)"
        kill $PID 2>/dev/null
        sleep 1
        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            echo "💀 Force killing process on port $port"
            kill -9 $PID 2>/dev/null
        fi
    else
        echo "✅ Port $port is free"
    fi
done

echo ""
echo "✅ All servers stopped"
echo "💡 To start again, run: ./start.sh"