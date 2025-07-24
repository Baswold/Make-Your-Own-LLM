# Changelog

All notable changes to Make Your Own LLM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Dark/Light mode toggle (in development by Codex team)
- Enhanced installer improvements (in development by Codex team)

## [1.0.0] - 2024-12-19

### Added
- **🎯 One-Click Training**: Complete training pipeline with drag-and-drop file upload
- **📊 Real-time Progress Monitoring**: Live training metrics, loss curves, and system resource monitoring
- **💬 Integrated Chat Interface**: WebSocket-powered streaming chat with token counting
- **🔧 Multiple Model Sizes**: Support for toy (50M), base (150M), and plus (200M) parameter models
- **📁 Project Management**: Organize and switch between multiple training projects
- **⚡ GPU/CPU Auto-detection**: Automatic device detection with graceful CPU fallback
- **🌐 Modern Web UI**: Responsive React interface with Tailwind CSS styling

#### Backend Features
- **FastAPI Training Server** (`train.py`): Asynchronous training with real-time progress updates
- **FastAPI Chat Server** (`serve.py`): Model serving with WebSocket streaming support
- **Multi-format Data Processing** (`data_utils.py`): Support for .txt, .jsonl, .csv, and .pdf files
- **Model Management** (`model_utils.py`): Automated model loading, training, and checkpointing
- **System Monitoring**: Real-time CPU, memory, and GPU utilization tracking

#### Frontend Features
- **Data Upload Component**: Drag-and-drop interface with file validation
- **Training Wizard**: Intuitive configuration with model size selection and advanced settings
- **Progress Dashboard**: Live training metrics with Victory.js charts and system monitoring
- **Chat Interface**: Real-time conversation with streaming responses and metrics display
- **Project Selector**: Easy switching between different training projects
- **System Monitor**: Resource usage visualization

#### Development & Deployment
- **Cross-platform Installers**: Automated setup scripts for Mac/Linux (`install.sh`) and Windows (`install.bat`)
- **Docker Support**: Complete containerization with `replit.nix` configuration
- **Comprehensive Makefile**: Development commands for setup, testing, and deployment
- **Performance Benchmarking**: Automated testing suite with `benchmark.sh`

#### Documentation
- **Complete README**: Comprehensive setup and usage guide
- **Sample Training Data**: Ready-to-use story corpus for testing
- **API Documentation**: Full endpoint documentation for both training and chat APIs
- **Troubleshooting Guide**: Common issues and solutions

### Technical Specifications
- **Backend**: Python 3.8+, FastAPI, PyTorch, Transformers, Uvicorn
- **Frontend**: React 18, Vite, Tailwind CSS, Victory.js for charts
- **ML Framework**: Hugging Face Transformers with support for DialoGPT models
- **Data Processing**: pandas, pdfplumber, custom tokenization pipeline
- **WebSocket**: Real-time communication for streaming chat responses
- **System Requirements**: 4GB+ RAM, optional GPU with 4GB+ VRAM

### Installation Methods
1. **One-line installer (Mac/Linux)**:
   ```bash
   curl -sSL https://raw.githubusercontent.com/Baswold/Make-Your-Own-LLM/main/install.sh | bash
   ```

2. **Windows installer**: Download and run `install.bat`

3. **Manual installation**: Clone repository and run `make setup`

### Usage Workflow
1. Upload training data (stories, articles, documentation)
2. Configure model size and training parameters
3. Monitor real-time training progress with loss curves
4. Chat with trained model through integrated interface
5. Continue training with additional data as needed

### Supported Data Formats
- **Plain Text** (`.txt`): Direct text content
- **JSON Lines** (`.jsonl`): Structured data with `text` or `content` fields
- **CSV** (`.csv`): Tabular data with text columns
- **PDF** (`.pdf`): Automatic text extraction

### Model Configurations
- **Toy Model** (~50M parameters): Quick testing and experimentation
- **Base Model** (~150M parameters): Balanced quality and performance
- **Plus Model** (~200M parameters): Higher quality for complex tasks

### Performance Optimizations
- Automatic GPU detection with CUDA support
- Efficient memory management with gradient accumulation
- Real-time system resource monitoring
- Optimized tokenization and batch processing

### Security Features
- Local data processing (no data sent to external services)
- Secure file upload validation
- Project isolation with workspace management
- Safe model checkpointing and recovery

---

## Future Roadmap

### Planned Features (Stretch Goals)
- **RAG Mode**: Vector store integration for retrieval-augmented generation
- **Hyperparameter Optimization**: Optuna-based grid search with visual comparison
- **Model Resume**: Upload previous checkpoints for incremental learning
- **Export Formats**: ONNX conversion and GGUF quantization for local inference
- **Multi-GPU Training**: Distributed training support for larger models
- **Custom Architectures**: Support for different model architectures beyond DialoGPT

### Community Contributions
We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Version History Notes
- This is the initial release (1.0.0) providing a complete, production-ready LLM training and chat platform
- Future versions will focus on performance improvements, additional model architectures, and advanced features
- All changes are backward compatible unless noted otherwise

---

**Legend:**
- 🎯 = Core Features
- 📊 = Analytics & Monitoring  
- 💬 = Chat & Interface
- 🔧 = Configuration & Tools
- 📁 = Data Management
- ⚡ = Performance & Optimization
- 🌐 = User Interface
- 🛠️ = Development Tools
- 📚 = Documentation
- 🔒 = Security Features