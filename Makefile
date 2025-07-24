# Make Your Own LLM - Development Makefile

.PHONY: help setup install-backend install-frontend build clean train serve dev test lint format benchmark

# Default target
help:
	@echo "Make Your Own LLM - Available Commands:"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  setup                 - Complete project setup (backend + frontend)"
	@echo "  install-backend       - Install Python dependencies"
	@echo "  install-frontend      - Install Node.js dependencies"
	@echo ""
	@echo "Development:"
	@echo "  dev                   - Start development servers (backend + frontend)"
	@echo "  train                 - Start training server only"
	@echo "  serve                 - Start chat server only"
	@echo "  build                 - Build frontend for production"
	@echo ""
	@echo "Quality Assurance:"
	@echo "  test                  - Run all tests"
	@echo "  lint                  - Run linting on all code"
	@echo "  format                - Format code with Black and Prettier"
	@echo ""
	@echo "Utilities:"
	@echo "  clean                 - Clean build artifacts and cache"
	@echo "  benchmark             - Run performance benchmarks"

# Setup targets
setup: install-backend install-frontend
	@echo "✅ Project setup complete!"
	@echo "Run 'make dev' to start development servers"

install-backend:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "✅ Backend dependencies installed"

install-frontend:
	@echo "📦 Installing Node.js dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed"

# Development targets
dev:
	@echo "🚀 Starting development servers..."
	@echo "Training API will be available at http://localhost:8000"
	@echo "Chat API will be available at http://localhost:8001" 
	@echo "Frontend will be available at http://localhost:3000"
	@tmux new-session -d -s llm-dev \; \
		send-keys 'cd backend && python train.py' C-m \; \
		split-window -h \; \
		send-keys 'cd backend && python serve.py' C-m \; \
		split-window -v \; \
		send-keys 'cd frontend && npm run dev' C-m \; \
		select-pane -t 0
	@echo "Development servers started in tmux session 'llm-dev'"
	@echo "Attach with: tmux attach-session -t llm-dev"

train:
	@echo "🧠 Starting training server..."
	cd backend && python train.py

serve:
	@echo "💬 Starting chat server..."
	cd backend && python serve.py

build:
	@echo "🏗️ Building frontend for production..."
	cd frontend && npm run build
	@echo "✅ Frontend built successfully"

# Testing targets
test:
	@echo "🧪 Running backend tests..."
	pytest backend/tests/ -v
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test
	@echo "✅ All tests passed"

# Code quality targets
lint:
	@echo "🔍 Linting Python code..."
	flake8 backend/ --max-line-length=88 --extend-ignore=E203,W503
	@echo "🔍 Linting JavaScript code..."
	cd frontend && npm run lint
	@echo "✅ All code passed linting"

format:
	@echo "🎨 Formatting Python code..."
	black backend/ --line-length=88
	@echo "🎨 Formatting JavaScript code..."
	cd frontend && npm run format
	@echo "✅ Code formatting complete"

# Utility targets
clean:
	@echo "🧹 Cleaning build artifacts..."
	# Python cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	
	# Node.js cache
	cd frontend && rm -rf node_modules/.cache
	cd frontend && rm -rf dist/
	
	# Model checkpoints (optional - uncomment if needed)
	# rm -rf /workspace/data/*/checkpoint/
	
	@echo "✅ Cleanup complete"

benchmark:
	@echo "📊 Running performance benchmarks..."
	cd scripts && bash benchmark.sh
	@echo "✅ Benchmarks complete"

# Environment checks
check-python:
	@python --version || (echo "❌ Python not found. Please install Python 3.11+" && exit 1)
	@echo "✅ Python check passed"

check-node:
	@node --version || (echo "❌ Node.js not found. Please install Node.js 18+" && exit 1)
	@npm --version || (echo "❌ npm not found. Please install npm" && exit 1)
	@echo "✅ Node.js check passed"

check-gpu:
	@python -c "import torch; print('✅ GPU available:', torch.cuda.is_available())" 2>/dev/null || echo "⚠️ GPU not available, will use CPU"

# Combined environment check
check: check-python check-node check-gpu

# Quick start for new users
quick-start: check setup
	@echo ""
	@echo "🎉 Welcome to Make Your Own LLM!"
	@echo ""
	@echo "Quick start guide:"
	@echo "1. Run 'make dev' to start all servers"
	@echo "2. Open http://localhost:3000 in your browser"
	@echo "3. Upload some text files to train your model"
	@echo "4. Configure training settings and start training"
	@echo "5. Chat with your trained model!"
	@echo ""
	@echo "For help: make help"
	@echo "Happy training! 🚀"