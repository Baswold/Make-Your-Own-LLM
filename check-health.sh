#!/bin/bash

# Health check script for Make Your Own LLM
echo "🏥 Make Your Own LLM - Health Check"
echo "=================================="

# Check if servers are running
echo "📡 Checking server status..."

# Check training server
if curl -s http://localhost:8000/system-info > /dev/null 2>&1; then
    echo "✅ Training server (port 8000): Running"
else
    echo "❌ Training server (port 8000): Not responding"
fi

# Check chat server  
if curl -s http://localhost:8001/system-info > /dev/null 2>&1; then
    echo "✅ Chat server (port 8001): Running"
else
    echo "❌ Chat server (port 8001): Not responding"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend (port 3000): Running"
else
    echo "❌ Frontend (port 3000): Not responding"
fi

echo ""
echo "💾 Checking data directory..."
if [ -d "data" ]; then
    echo "✅ Data directory exists"
    echo "📊 Projects found: $(find data -name "*.json" 2>/dev/null | wc -l | tr -d ' ')"
else
    echo "⚠️  Data directory missing (will be created on first use)"
fi

echo ""
echo "🔧 Environment check..."
echo "Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "Node.js: $(node --version 2>/dev/null || echo 'Not found')"
echo "npm: $(npm --version 2>/dev/null || echo 'Not found')"

if command -v python3 &> /dev/null && python3 -c "import torch" 2>/dev/null; then
    GPU_STATUS=$(python3 -c "import torch; print('✅ Available' if torch.cuda.is_available() else '⚠️  Not available (using CPU)')")
    echo "GPU: $GPU_STATUS"
else
    echo "GPU: ❌ Cannot check (PyTorch not available)"
fi

echo ""
echo "📋 System resources..."
if command -v python3 &> /dev/null && python3 -c "import psutil" 2>/dev/null; then
    python3 -c "
import psutil
print(f'CPU: {psutil.cpu_percent():.1f}%')
print(f'Memory: {psutil.virtual_memory().percent:.1f}%')
print(f'Disk: {psutil.disk_usage(\"/\").percent:.1f}%')
"
else
    echo "⚠️  System monitoring unavailable (psutil not installed)"
fi

echo ""
echo "🔍 Quick tips:"
echo "  • Start servers: ./start.sh"
echo "  • Stop tmux session: tmux kill-session -t llm-dev"  
echo "  • View logs: tmux attach-session -t llm-dev"
echo "  • Full setup: make setup"