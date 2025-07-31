# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a browser-based application for training and chatting with custom language models. The system consists of:
- **Backend**: Python FastAPI servers for training (port 8000) and chat inference (port 8001)
- **Frontend**: React/Vite application (port 3000) with real-time training monitoring and chat interface
- **Architecture**: Microservices approach with separate training and inference servers
- **Data Storage**: Local `data/` directory for models, checkpoints, and training data

## Quick Start

The easiest way to run this project:

```bash
./start.sh           # One-command startup with automatic dependency check
# OR
make quick-start     # Full environment check and setup
# OR  
make setup && make dev   # Manual setup then start
```

All servers will be available at:
- Frontend: http://localhost:3000
- Training API: http://localhost:8000  
- Chat API: http://localhost:8001

## Development Commands

### Setup and Installation
```bash
make setup                 # Complete project setup (backend + frontend)
make install-backend       # Install Python dependencies only
make install-frontend      # Install Node.js dependencies only
```

### Development Servers
```bash
make dev                   # Start all servers in tmux session 'llm-dev'
make train                 # Start training server only (port 8000)
make serve                 # Start chat server only (port 8001)
```

### Building and Testing
```bash
make build                 # Build frontend for production
make test                  # Run backend (pytest) and frontend (npm test) tests
make lint                  # Run flake8 (backend) and ESLint (frontend)
make format                # Format with Black (backend) and Prettier (frontend)
```

### Development Workflow
```bash
make benchmark             # Run performance benchmarks
make clean                 # Clean build artifacts and Python cache
make check                 # Check Python, Node.js, and GPU availability
```

### Tmux Session Management
The `make dev` command creates a tmux session named 'llm-dev' with three panes:
- Training server (backend/train.py)
- Chat server (backend/serve.py)  
- Frontend dev server (npm run dev)

Access with: `tmux attach-session -t llm-dev`

## Troubleshooting

### Common Issues

1. **Permission errors**: The project uses local `data/` directory instead of `/workspace/data`
2. **Python command not found**: Use `python3` instead of `python` 
3. **Missing dependencies**: Run `make setup` or `./start.sh` for automatic installation
4. **Servers not starting**: Check that ports 3000, 8000, 8001 are available
5. **Frontend/backend errors**: Run `make test` and `make lint` to check for issues

### System Requirements
- Python 3.11+ (uses `python3` command)
- Node.js 18+ with npm
- 4GB+ RAM (8GB+ recommended)
- Optional: GPU with 4GB+ VRAM (CPU fallback available)
- Optional: tmux for better session management

## Architecture and Key Components

### Backend Architecture
- **train.py**: FastAPI server handling data upload, training orchestration, and progress monitoring
- **serve.py**: FastAPI server with WebSocket support for real-time chat inference
- **model_utils.py**: Core model management, training logic, and checkpoint handling
- **data_utils.py**: Data processing utilities for various formats (txt, jsonl, csv, pdf)

### Frontend Architecture
- **React 18** with Vite build system
- **Components**: Modular UI components in `src/components/`
- **State Management**: React Query for server state, local state for UI
- **Styling**: Tailwind CSS with Radix UI components
- **Real-time Updates**: WebSocket connections for training progress and chat streaming

### Key Integration Points
- Training progress via polling `/api/training-status` endpoint
- Chat via WebSocket at `/chat-stream/{project}/{client_id}`
- System monitoring via `/api/system-info` endpoint
- Model size configurations: toy (~50M), base (~150M), plus (~200M) parameters

### Data Flow
1. **Training**: Upload → Data Processing → Model Training → Checkpoint Saving
2. **Inference**: Model Loading → Chat Interface → WebSocket Streaming → Response Display
3. **Monitoring**: Real-time system metrics, training progress, and error handling

## Dependencies and Environment

### Python Dependencies (requirements.txt)
- **Core ML**: torch, transformers, datasets, tokenizers
- **Training**: accelerate, peft, bitsandbytes
- **API**: fastapi, uvicorn, websockets
- **Data**: pandas, numpy, pdfplumber
- **Monitoring**: psutil, GPUtil

### Frontend Dependencies
- **Core**: React 18, react-dom, react-query
- **UI**: Radix UI components, Tailwind CSS, Lucide icons
- **Charts**: Victory for training metrics visualization
- **Build**: Vite, PostCSS, Autoprefixer

### Environment Requirements
- Python 3.11+
- Node.js 18+
- 4GB+ RAM (8GB+ recommended)
- GPU with 4GB+ VRAM (optional, CPU fallback available)

## Project Structure Conventions

### Backend Code Style
- **Formatting**: Black with 88-character line length
- **Linting**: flake8 with E203,W503 extensions ignored
- **Testing**: pytest with asyncio support
- **Async**: FastAPI async endpoints for non-blocking operations

### Frontend Code Style
- **Components**: Functional components with hooks
- **Styling**: Tailwind utility classes with component composition
- **State**: React Query for server state, useState for local UI state
- **File Structure**: Components organized by feature, shared UI components in `ui/`

### Model and Data Conventions
- **Checkpoints**: Stored in `/workspace/data/{project}/checkpoint/`
- **Configurations**: JSON format with training parameters and model metadata
- **Data Formats**: Support for txt, jsonl, csv, pdf with automatic format detection
- **Model Naming**: Project slug-based naming for organization and isolation