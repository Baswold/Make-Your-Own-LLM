@echo off
REM Make Your Own LLM - Windows Installer
REM One-click setup for Windows
REM Usage: Double-click this file or run from Command Prompt

setlocal EnableDelayedExpansion
title Make Your Own LLM - Installer

REM Colors (using PowerShell for colored output)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "NC=[0m"

echo.
echo %PURPLE%╔══════════════════════════════════════════════════════════════╗%NC%
echo %PURPLE%║                                                              ║%NC%
echo %PURPLE%║           %CYAN%🤖 Make Your Own LLM Installer%PURPLE%                    ║%NC%
echo %PURPLE%║                                                              ║%NC%
echo %PURPLE%║     %YELLOW%Train and chat with custom language models%PURPLE%           ║%NC%
echo %PURPLE%║                                                              ║%NC%
echo %PURPLE%╚══════════════════════════════════════════════════════════════╝%NC%
echo.

echo %BLUE%⚙️ Starting Windows installation...%NC%
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%⚠️ Administrator privileges recommended for best installation experience%NC%
    echo %YELLOW%   Some features may not install correctly without admin rights%NC%
    echo.
    pause
)

REM Check Python installation
echo %BLUE%⚙️ Checking Python installation...%NC%
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%⚠️ Python not found%NC%
    echo %BLUE%📦 Downloading Python 3.11...%NC%
    
    REM Create temp directory
    if not exist "%TEMP%\llm-installer" mkdir "%TEMP%\llm-installer"
    cd /d "%TEMP%\llm-installer"
    
    REM Download Python installer
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe' -OutFile 'python-installer.exe'}"
    
    if exist "python-installer.exe" (
        echo %BLUE%🔧 Installing Python...%NC%
        echo %YELLOW%Please follow the Python installer prompts and make sure to:%NC%
        echo %YELLOW%  ✓ Check "Add Python to PATH"%NC%
        echo %YELLOW%  ✓ Check "Install pip"%NC%
        echo.
        start /wait python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        
        REM Refresh PATH
        call RefreshEnv.cmd >nul 2>&1
        
        REM Verify installation
        python --version >nul 2>&1
        if !errorLevel! equ 0 (
            echo %GREEN%✅ Python installed successfully%NC%
        ) else (
            echo %RED%❌ Python installation failed%NC%
            echo %YELLOW%Please install Python manually from https://python.org%NC%
            pause
            exit /b 1
        )
    ) else (
        echo %RED%❌ Failed to download Python installer%NC%
        echo %YELLOW%Please install Python manually from https://python.org%NC%
        pause
        exit /b 1
    )
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo %GREEN%✅ Python !PYTHON_VERSION! found%NC%
)

REM Check Node.js installation
echo %BLUE%⚙️ Checking Node.js installation...%NC%
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%⚠️ Node.js not found%NC%
    echo %BLUE%📦 Downloading Node.js...%NC%
    
    REM Download Node.js installer
    if not exist "%TEMP%\llm-installer" mkdir "%TEMP%\llm-installer"
    cd /d "%TEMP%\llm-installer"
    
    powershell -Command "& {Invoke-WebRequest -Uri 'https://nodejs.org/dist/v18.18.2/node-v18.18.2-x64.msi' -OutFile 'nodejs-installer.msi'}"
    
    if exist "nodejs-installer.msi" (
        echo %BLUE%🔧 Installing Node.js...%NC%
        start /wait msiexec /i nodejs-installer.msi /quiet
        
        REM Refresh PATH
        call RefreshEnv.cmd >nul 2>&1
        
        REM Verify installation
        node --version >nul 2>&1
        if !errorLevel! equ 0 (
            echo %GREEN%✅ Node.js installed successfully%NC%
        ) else (
            echo %RED%❌ Node.js installation failed%NC%
            echo %YELLOW%Please install Node.js manually from https://nodejs.org%NC%
            pause
            exit /b 1
        )
    ) else (
        echo %RED%❌ Failed to download Node.js installer%NC%
        echo %YELLOW%Please install Node.js manually from https://nodejs.org%NC%
        pause
        exit /b 1
    )
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo %GREEN%✅ Node.js !NODE_VERSION! found%NC%
)

REM Check Git installation
echo %BLUE%⚙️ Checking Git installation...%NC%
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%⚠️ Git not found%NC%
    echo %BLUE%📦 Downloading Git...%NC%
    
    if not exist "%TEMP%\llm-installer" mkdir "%TEMP%\llm-installer"
    cd /d "%TEMP%\llm-installer"
    
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile 'git-installer.exe'}"
    
    if exist "git-installer.exe" (
        echo %BLUE%🔧 Installing Git...%NC%
        start /wait git-installer.exe /VERYSILENT /NORESTART
        
        REM Refresh PATH
        call RefreshEnv.cmd >nul 2>&1
        
        REM Verify installation
        git --version >nul 2>&1
        if !errorLevel! equ 0 (
            echo %GREEN%✅ Git installed successfully%NC%
        ) else (
            echo %RED%❌ Git installation failed%NC%
            echo %YELLOW%Please install Git manually from https://git-scm.com%NC%
            pause
            exit /b 1
        )
    ) else (
        echo %RED%❌ Failed to download Git installer%NC%
        echo %YELLOW%Please install Git manually from https://git-scm.com%NC%
        pause
        exit /b 1
    )
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do set GIT_VERSION=%%i
    echo %GREEN%✅ Git !GIT_VERSION! found%NC%
)

REM Ask for installation directory
echo.
echo %CYAN%📁 Where would you like to install Make Your Own LLM?%NC%
echo %YELLOW%Press Enter for default: %USERPROFILE%\make-your-own-llm%NC%
set /p "INSTALL_PATH=Installation path: "

if "%INSTALL_PATH%"=="" (
    set "INSTALL_PATH=%USERPROFILE%\make-your-own-llm"
)

REM Check if directory exists
if exist "%INSTALL_PATH%" (
    echo %YELLOW%⚠️ Directory %INSTALL_PATH% already exists%NC%
    set /p "OVERWRITE=Remove existing directory and reinstall? (y/N): "
    if /i "!OVERWRITE!"=="y" (
        echo %BLUE%🗑️ Removing existing installation...%NC%
        rmdir /s /q "%INSTALL_PATH%"
    ) else (
        echo %BLUE%ℹ️ Installation cancelled%NC%
        pause
        exit /b 0
    )
)

REM Clone repository
echo %BLUE%📥 Downloading Make Your Own LLM...%NC%
git clone https://github.com/Baswold/Make-Your-Own-LLM.git "%INSTALL_PATH%"

if %errorLevel% neq 0 (
    echo %RED%❌ Failed to clone repository%NC%
    pause
    exit /b 1
)

echo %GREEN%✅ Repository downloaded to %INSTALL_PATH%%NC%

REM Change to installation directory
cd /d "%INSTALL_PATH%"

REM Create Python virtual environment
echo %BLUE%⚙️ Setting up Python virtual environment...%NC%
python -m venv venv

if %errorLevel% neq 0 (
    echo %RED%❌ Failed to create virtual environment%NC%
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo %BLUE%📦 Upgrading pip...%NC%
python -m pip install --upgrade pip

REM Install Python dependencies
echo %BLUE%📦 Installing Python dependencies...%NC%

REM Check for NVIDIA GPU
nvidia-smi >nul 2>&1
if %errorLevel% equ 0 (
    echo %BLUE%🎮 NVIDIA GPU detected, installing PyTorch with CUDA support...%NC%
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
) else (
    echo %BLUE%💻 No GPU detected, installing CPU-only PyTorch...%NC%
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
)

REM Install other requirements
pip install -r requirements.txt

if %errorLevel% neq 0 (
    echo %RED%❌ Failed to install Python dependencies%NC%
    pause
    exit /b 1
)

echo %GREEN%✅ Python dependencies installed%NC%

REM Install Node.js dependencies
echo %BLUE%📦 Installing Node.js dependencies...%NC%
cd frontend
call npm install

if %errorLevel% neq 0 (
    echo %RED%❌ Failed to install Node.js dependencies%NC%
    pause
    exit /b 1
)

cd ..
echo %GREEN%✅ Node.js dependencies installed%NC%

REM Create startup script
echo %BLUE%⚙️ Creating startup script...%NC%

(
echo @echo off
echo REM Make Your Own LLM - Startup Script
echo title Make Your Own LLM
echo cd /d "%INSTALL_PATH%"
echo call venv\Scripts\activate.bat
echo echo.
echo echo 🚀 Starting Make Your Own LLM...
echo echo.
echo echo Starting servers...
echo start "Training Server" cmd /k "cd backend && python train.py"
echo timeout /t 3 /nobreak ^>nul
echo start "Chat Server" cmd /k "cd backend && python serve.py"
echo timeout /t 3 /nobreak ^>nul
echo start "Frontend" cmd /k "cd frontend && npm run dev"
echo echo.
echo echo ✅ Servers started! Open these URLs:
echo echo    🌐 Frontend: http://localhost:3000
echo echo    🧠 Training API: http://localhost:8000
echo echo    💬 Chat API: http://localhost:8001
echo echo.
echo echo Press any key to exit...
echo pause ^>nul
) > start.bat

REM Create desktop shortcut
echo %BLUE%🔗 Creating desktop shortcut...%NC%
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Make Your Own LLM.lnk'); $Shortcut.TargetPath = '%INSTALL_PATH%\start.bat'; $Shortcut.WorkingDirectory = '%INSTALL_PATH%'; $Shortcut.Description = 'Train and chat with custom language models'; $Shortcut.Save()}"

REM Test installation
echo %BLUE%🧪 Testing installation...%NC%
call venv\Scripts\activate.bat
python -c "import torch; import transformers; import fastapi; print('✅ Python dependencies OK')" >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%⚠️ Python dependency test failed%NC%
    echo %YELLOW%Installation may have issues, but you can still try running it%NC%
) else (
    echo %GREEN%✅ Python dependencies test passed%NC%
)

cd frontend
call npm run build >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%⚠️ Frontend build test failed%NC%
    echo %YELLOW%Installation may have issues, but you can still try running it%NC%
) else (
    echo %GREEN%✅ Frontend build test passed%NC%
)
cd ..

REM Clean up temp files
if exist "%TEMP%\llm-installer" rmdir /s /q "%TEMP%\llm-installer"

REM Show completion message
echo.
echo %GREEN%✨═══════════════════════════════════════════════════════════════✨%NC%
echo %GREEN%✨                                                               ✨%NC%
echo %GREEN%✨    🎉 Make Your Own LLM installed successfully! 🎉          ✨%NC%
echo %GREEN%✨                                                               ✨%NC%
echo %GREEN%✨═══════════════════════════════════════════════════════════════✨%NC%
echo.
echo %CYAN%📁 Installation location: %YELLOW%"%INSTALL_PATH%"%NC%
echo.
echo %CYAN%🚀 Quick Start:%NC%
echo %GREEN%   1. Double-click the desktop shortcut "Make Your Own LLM"%NC%
echo %GREEN%   2. Or run: "%INSTALL_PATH%\start.bat"%NC%
echo.
echo %CYAN%🌐 After starting, open: %YELLOW%http://localhost:3000%NC%
echo.
echo %CYAN%📚 Next steps:%NC%
echo %GREEN%   1. Upload some text files (stories, articles, etc.)%NC%
echo %GREEN%   2. Choose model size and start training%NC%
echo %GREEN%   3. Chat with your custom trained model!%NC%
echo.
echo %CYAN%📖 Documentation: %YELLOW%"%INSTALL_PATH%\README.md"%NC%
echo %CYAN%🆘 Need help? Visit: %YELLOW%https://github.com/Baswold/Make-Your-Own-LLM/issues%NC%
echo.
echo %PURPLE%Happy training! 🤖✨%NC%
echo.
pause