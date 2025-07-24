#!/bin/bash

# Make Your Own LLM - Easy Installer
# One-click setup for Mac/Linux
# Usage: curl -sSL https://raw.githubusercontent.com/Baswold/Make-Your-Own-LLM/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis for visual appeal
ROCKET="🚀"
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
GEAR="⚙️"
SPARKLES="✨"

print_banner() {
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                                                              ║${NC}"
    echo -e "${PURPLE}║           ${CYAN}🤖 Make Your Own LLM Installer${PURPLE}                    ║${NC}"
    echo -e "${PURPLE}║                                                              ║${NC}"
    echo -e "${PURPLE}║     ${YELLOW}Train and chat with custom language models${PURPLE}           ║${NC}"
    echo -e "${PURPLE}║                                                              ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

log_info() {
    echo -e "${BLUE}${GEAR} $1${NC}"
}

log_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}${WARNING} $1${NC}"
}

log_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

check_system() {
    log_info "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        log_success "Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_success "macOS detected"
    else
        log_error "Unsupported operating system: $OSTYPE"
        log_info "Please use Windows installer (install.bat) or install manually"
        exit 1
    fi
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This is not recommended for development."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled"
            exit 1
        fi
    fi
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [[ $PYTHON_MAJOR -ge 3 && $PYTHON_MINOR -ge 8 ]]; then
            log_success "Python $PYTHON_VERSION found"
        else
            log_error "Python 3.8+ required, found $PYTHON_VERSION"
            install_python
        fi
    else
        log_warning "Python 3 not found"
        install_python
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_warning "pip3 not found, installing..."
        install_pip
    else
        log_success "pip3 found"
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
        
        if [[ $NODE_MAJOR -ge 16 ]]; then
            log_success "Node.js $NODE_VERSION found"
        else
            log_warning "Node.js 16+ recommended, found $NODE_VERSION"
            install_node
        fi
    else
        log_warning "Node.js not found"
        install_node
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_warning "npm not found, installing..."
        install_node
    else
        log_success "npm found"
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        log_warning "git not found"
        install_git
    else
        log_success "git found"
    fi
}

install_python() {
    log_info "Installing Python 3..."
    
    if [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install python@3.11
        else
            log_error "Homebrew not found. Please install Python 3.11+ manually from https://python.org"
            exit 1
        fi
    elif [[ "$OS" == "linux" ]]; then
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        elif command -v pacman &> /dev/null; then
            sudo pacman -S python python-pip
        else
            log_error "Package manager not found. Please install Python 3.8+ manually"
            exit 1
        fi
    fi
}

install_pip() {
    log_info "Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
}

install_node() {
    log_info "Installing Node.js..."
    
    if [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install node
        else
            log_error "Homebrew not found. Please install Node.js 18+ manually from https://nodejs.org"
            exit 1
        fi
    elif [[ "$OS" == "linux" ]]; then
        # Install Node.js via NodeSource repository
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
}

install_git() {
    log_info "Installing git..."
    
    if [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install git
        else
            log_error "Homebrew not found. Please install git manually"
            exit 1
        fi
    elif [[ "$OS" == "linux" ]]; then
        if command -v apt &> /dev/null; then
            sudo apt install -y git
        elif command -v yum &> /dev/null; then
            sudo yum install -y git
        elif command -v pacman &> /dev/null; then
            sudo pacman -S git
        fi
    fi
}

clone_repository() {
    log_info "Downloading Make Your Own LLM..."
    
    # Ask for installation directory
    echo -e "${CYAN}Where would you like to install Make Your Own LLM?${NC}"
    echo -e "${YELLOW}Press Enter for default: $HOME/make-your-own-llm${NC}"
    read -p "Installation path: " INSTALL_PATH
    
    if [[ -z "$INSTALL_PATH" ]]; then
        INSTALL_PATH="$HOME/make-your-own-llm"
    fi
    
    # Expand tilde to home directory
    INSTALL_PATH="${INSTALL_PATH/#\~/$HOME}"
    
    # Check if directory exists
    if [[ -d "$INSTALL_PATH" ]]; then
        log_warning "Directory $INSTALL_PATH already exists"
        read -p "Remove existing directory and reinstall? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_PATH"
        else
            log_info "Installation cancelled"
            exit 1
        fi
    fi
    
    # Clone repository
    git clone https://github.com/Baswold/Make-Your-Own-LLM.git "$INSTALL_PATH"
    cd "$INSTALL_PATH"
    
    log_success "Repository cloned to $INSTALL_PATH"
}

setup_python_environment() {
    log_info "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    log_success "Virtual environment created and activated"
}

install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Install PyTorch with CUDA support if available
    if command -v nvidia-smi &> /dev/null; then
        log_info "NVIDIA GPU detected, installing PyTorch with CUDA support..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    else
        log_info "No GPU detected, installing CPU-only PyTorch..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    fi
    
    # Install other requirements
    pip install -r requirements.txt
    
    log_success "Python dependencies installed"
}

install_node_dependencies() {
    log_info "Installing Node.js dependencies..."
    
    cd frontend
    npm install
    cd ..
    
    log_success "Node.js dependencies installed"
}

create_startup_scripts() {
    log_info "Creating startup scripts..."
    
    # Create activation script
    cat > start.sh << 'EOF'
#!/bin/bash

# Make Your Own LLM - Startup Script
# This script activates the environment and starts all servers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Make Your Own LLM..."

# Activate virtual environment
source venv/bin/activate

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo "📱 Starting servers in tmux session..."
    make dev
    echo ""
    echo "✅ Servers started! Open these URLs:"
    echo "   🌐 Frontend: http://localhost:3000"
    echo "   🧠 Training API: http://localhost:8000"
    echo "   💬 Chat API: http://localhost:8001"
    echo ""
    echo "📺 To view server logs: tmux attach-session -t llm-dev"
    echo "🛑 To stop servers: tmux kill-session -t llm-dev"
else
    echo "⚠️  tmux not found. Starting servers individually..."
    echo "📖 See README.md for manual startup instructions"
    
    echo ""
    echo "🔧 Quick start commands:"
    echo "   Backend training: cd backend && python train.py"
    echo "   Backend chat: cd backend && python serve.py"  
    echo "   Frontend: cd frontend && npm run dev"
fi
EOF
    
    chmod +x start.sh
    
    # Create desktop shortcut for Linux
    if [[ "$OS" == "linux" ]]; then
        cat > "Make Your Own LLM.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Make Your Own LLM
Comment=Train and chat with custom language models
Exec=$INSTALL_PATH/start.sh
Icon=$INSTALL_PATH/frontend/public/favicon.ico
Path=$INSTALL_PATH
Terminal=true
Categories=Development;Education;
EOF
        chmod +x "Make Your Own LLM.desktop"
    fi
    
    log_success "Startup scripts created"
}

run_tests() {
    log_info "Running installation tests..."
    
    # Test Python imports
    source venv/bin/activate
    python3 -c "import torch; import transformers; import fastapi; print('✅ Python dependencies OK')" || {
        log_error "Python dependency test failed"
        return 1
    }
    
    # Test Node.js setup
    cd frontend
    npm run build > /dev/null 2>&1 || {
        log_error "Frontend build test failed"
        return 1
    }
    cd ..
    
    log_success "All tests passed"
}

show_completion_message() {
    echo ""
    echo -e "${GREEN}${SPARKLES}═══════════════════════════════════════════════════════════════${SPARKLES}${NC}"
    echo -e "${GREEN}${SPARKLES}                                                               ${SPARKLES}${NC}"
    echo -e "${GREEN}${SPARKLES}    🎉 Make Your Own LLM installed successfully! 🎉          ${SPARKLES}${NC}"
    echo -e "${GREEN}${SPARKLES}                                                               ${SPARKLES}${NC}"
    echo -e "${GREEN}${SPARKLES}═══════════════════════════════════════════════════════════════${SPARKLES}${NC}"
    echo ""
    echo -e "${CYAN}📁 Installation location: ${YELLOW}$INSTALL_PATH${NC}"
    echo ""
    echo -e "${CYAN}🚀 Quick Start:${NC}"
    echo -e "   ${GREEN}cd $INSTALL_PATH${NC}"
    echo -e "   ${GREEN}./start.sh${NC}"
    echo ""
    echo -e "${CYAN}🌐 After starting, open: ${YELLOW}http://localhost:3000${NC}"
    echo ""
    echo -e "${CYAN}📚 Next steps:${NC}"
    echo -e "   1. Upload some text files (stories, articles, etc.)"
    echo -e "   2. Choose model size and start training"
    echo -e "   3. Chat with your custom trained model!"
    echo ""
    echo -e "${CYAN}📖 Documentation: ${YELLOW}$INSTALL_PATH/README.md${NC}"
    echo -e "${CYAN}🆘 Need help? Visit: ${YELLOW}https://github.com/Baswold/Make-Your-Own-LLM/issues${NC}"
    echo ""
    echo -e "${PURPLE}Happy training! 🤖✨${NC}"
}

# Main installation flow
main() {
    print_banner
    
    log_info "Starting installation..."
    
    check_system
    check_dependencies
    clone_repository
    setup_python_environment
    install_python_dependencies
    install_node_dependencies
    create_startup_scripts
    
    if run_tests; then
        show_completion_message
    else
        log_error "Installation completed with warnings. Check the logs above."
        log_info "You can still try running: ./start.sh"
    fi
}

# Handle interrupts
trap 'echo -e "\n${RED}Installation cancelled by user${NC}"; exit 130' INT

# Run main function
main "$@"