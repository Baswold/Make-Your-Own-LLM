# Make Your Own LLM

**A browser-based application for training and chatting with custom language models**

Train your own small language model on custom text data with one-click simplicity, then chat with your freshly trained model through an integrated web interface.

![Make Your Own LLM Demo](https://via.placeholder.com/800x400/4F46E5/FFFFFF?text=Make+Your+Own+LLM+Demo)

## ✨ Features

- **🎯 One-Click Training**: Upload text files and start training with minimal configuration
- **📊 Real-time Progress**: Live training metrics, loss curves, and system monitoring
- **💬 Integrated Chat**: Chat interface with streaming responses and token counting
- **🔧 Multiple Model Sizes**: Choose from toy (50M), base (150M), or plus (200M) parameter models
- **📁 Project Management**: Organize multiple training projects with easy switching
- **⚡ GPU/CPU Support**: Automatic device detection with graceful fallback to CPU
- **🌐 Modern Web UI**: React-based interface with responsive design

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- 4GB+ RAM (8GB+ recommended for larger models)
- GPU with 4GB+ VRAM (optional, will use CPU if not available)

### Installation

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd make-your-own-llm
   make setup
   ```

2. **Start development servers:**
   ```bash
   make dev
   ```

3. **Open your browser:**
   - Frontend: http://localhost:3000
   - Training API: http://localhost:8000
   - Chat API: http://localhost:8001

### First Training Session

1. **Upload Data**: Drag and drop text files (.txt, .jsonl, .csv, .pdf) into the upload area
2. **Configure Training**: Select model size, use case, and training parameters
3. **Start Training**: Click "Start Training" and monitor progress in real-time
4. **Chat**: Once training completes, switch to the Chat tab to converse with your model

## 📖 Usage Guide

### Supported Data Formats

| Format | Description | Example |
|--------|-------------|---------|
| `.txt` | Plain text files | Stories, articles, documentation |
| `.jsonl` | JSON Lines with `text` or `content` fields | `{"text": "Your content here"}` |
| `.csv` | CSV with text/content/story/message columns | Structured datasets |
| `.pdf` | PDF documents (text extraction) | Books, papers, reports |

### Model Sizes

| Size | Parameters | Use Case | Training Time |
|------|------------|----------|---------------|
| **Toy** | ~50M | Quick testing, experimentation | 1-2 minutes |
| **Base** | ~150M | Good quality for most tasks | 3-5 minutes |
| **Plus** | ~200M | Higher quality, complex tasks | 8-12 minutes |

### Training Configuration

- **Use Cases**: General conversation, creative storytelling, Q&A, casual chat, task assistance
- **Epochs**: Number of training passes (1-5 recommended)
- **Temperature**: Response creativity (0.1 = focused, 1.0 = creative)
- **Learning Rate**: Training speed (5e-5 recommended)

## 🛠️ Development

### Project Structure

```
make-your-own-llm/
├── backend/                 # Python FastAPI backend
│   ├── train.py            # Training server and API
│   ├── serve.py            # Chat server with WebSocket support
│   ├── data_utils.py       # Data processing utilities
│   └── model_utils.py      # Model management and training
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main application component
│   │   └── components/     # UI components
│   └── package.json
├── scripts/
│   └── benchmark.sh        # Performance benchmarking
├── requirements.txt        # Python dependencies
└── Makefile               # Development commands
```

### Available Commands

```bash
# Setup and installation
make setup              # Complete project setup
make install-backend    # Install Python dependencies
make install-frontend   # Install Node.js dependencies

# Development
make dev               # Start all development servers
make train             # Start training server only
make serve             # Start chat server only
make build             # Build frontend for production

# Quality assurance
make test              # Run all tests
make lint              # Run linting
make format            # Format code
make benchmark         # Run performance benchmarks

# Utilities
make clean             # Clean build artifacts
make check             # Check environment
make quick-start       # Setup + guidance for new users
```

### API Endpoints

#### Training API (Port 8000)

- `GET /system-info` - System resource monitoring
- `GET /projects` - List existing projects
- `POST /upload-data` - Upload training data
- `POST /start-training` - Start model training
- `POST /continue-training` - Continue training with additional epochs
- `GET /training-status` - Get real-time training progress

#### Chat API (Port 8001)

- `POST /load-model` - Load trained model for inference
- `POST /chat` - Generate chat response
- `WebSocket /chat-stream/{project}/{client_id}` - Streaming chat
- `GET /health` - Health check and system status

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Custom workspace directory
export WORKSPACE_DIR="/custom/path/to/data"

# Optional: CUDA configuration
export CUDA_VISIBLE_DEVICES="0"
export TORCH_CUDA_ARCH_LIST="8.0;8.6"
```

### Replit Configuration

This project is optimized for Replit with GPU support:

- `replit.nix` - System dependencies and CUDA setup
- Automatic workspace directory creation
- GPU detection and fallback to CPU

## 📊 Monitoring and Debugging

### System Monitoring

The application provides real-time monitoring of:
- CPU and memory usage
- GPU utilization and VRAM
- Training progress and metrics
- Token generation speed

### Debugging Training Issues

1. **Out of Memory**: Reduce model size or batch size
2. **Slow Training**: Check GPU availability, reduce sequence length
3. **Poor Quality**: Increase training epochs, check data quality
4. **Connection Issues**: Verify all three servers are running

### Log Analysis

Training logs are available through:
- Web UI progress dashboard
- TMux session: `tmux attach-session -t llm-dev`
- Direct server output in terminal

## 🎯 Example Workflows

### Story Generation Model

1. Upload fairy tales, short stories, or creative writing samples
2. Select "Creative storytelling" use case
3. Use "Base" or "Plus" model size for better quality
4. Set temperature to 0.8-1.0 for creativity
5. Train for 2-3 epochs
6. Chat: "Tell me a bedtime story about a clockwork kangaroo"

### Q&A Assistant

1. Upload FAQ documents, knowledge base articles
2. Select "Question answering" use case
3. Use "Base" model with temperature 0.3-0.5
4. Train for 1-2 epochs
5. Chat: "What is the company policy on remote work?"

### Personal Chat Bot

1. Upload chat logs, personal notes, diary entries
2. Select "Casual chat" use case
3. Start with "Toy" model for testing
4. Adjust temperature based on desired personality
5. Continue training as you add more data

## 🚧 Stretch Goals & Future Features

The following features are planned for future releases:

- **RAG Mode**: Vector store integration for retrieval-augmented generation
- **Hyperparameter Sweep**: Optuna-based optimization with visual comparison
- **Fine-tune Resume**: Upload previous checkpoints for incremental learning
- **Export Formats**: ONNX conversion and GGUF quantization
- **Multi-GPU Training**: Distributed training support
- **Custom Architectures**: Support for different model architectures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `make test`
4. Run linting: `make lint`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Training fails to start:**
- Check that you've uploaded training data
- Verify Python dependencies are installed
- Check available disk space and memory

**Model loading fails:**
- Ensure training completed successfully
- Check that checkpoint files exist in `/workspace/data/{project}/checkpoint/`
- Verify model is compatible with serving infrastructure

**Chat interface not responding:**
- Confirm chat server is running on port 8001
- Check WebSocket connection in browser dev tools
- Ensure model is loaded before attempting to chat

**Performance is slow:**
- Use GPU-enabled environment when possible
- Reduce model size for faster iteration
- Monitor system resources during training

### Getting Help

- Check the [Issues](https://github.com/user/make-your-own-llm/issues) page for known problems
- Run `make benchmark` to diagnose performance issues
- Use `make check` to verify environment setup
- Join our [Discord community](https://discord.gg/make-your-own-llm) for support

## 🙏 Acknowledgments

- [Hugging Face Transformers](https://huggingface.co/transformers/) for the ML infrastructure
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) and [Vite](https://vitejs.dev/) for the frontend
- [Victory](https://formidable.com/open-source/victory/) for data visualization
- The open source ML community for inspiration and tools

---

**Made with ❤️ for the AI community**

Start training your own LLM today! 🚀