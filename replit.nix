{ pkgs }: {
  deps = [
    # Python runtime and development tools
    pkgs.python311Full
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.wheel
    
    # System dependencies for GPU support
    pkgs.cudaPackages.cudatoolkit
    pkgs.cudaPackages.cudnn
    
    # Node.js for frontend development
    pkgs.nodejs_18
    pkgs.nodePackages.npm
    
    # Build tools and utilities
    pkgs.gcc
    pkgs.cmake
    pkgs.pkg-config
    pkgs.git
    pkgs.tmux
    
    # System monitoring tools
    pkgs.htop
    pkgs.nvidia-smi
    
    # PDF processing dependencies
    pkgs.poppler_utils
    
    # Additional system libraries
    pkgs.zlib
    pkgs.libffi
    pkgs.openssl
  ];
  
  # Set environment variables for CUDA support
  env = {
    CUDA_HOME = "${pkgs.cudaPackages.cudatoolkit}";
    CUDA_PATH = "${pkgs.cudaPackages.cudatoolkit}";
    LD_LIBRARY_PATH = "${pkgs.cudaPackages.cudatoolkit}/lib:${pkgs.cudaPackages.cudnn}/lib";
    TORCH_CUDA_ARCH_LIST = "6.0;6.1;7.0;7.5;8.0;8.6";
    FORCE_CUDA = "1";
    
    # Python path configuration
    PYTHONPATH = "${pkgs.python311Full}/lib/python3.11/site-packages";
    
    # Node.js configuration
    NODE_ENV = "development";
    
    # Project workspace
    WORKSPACE_DIR = "/workspace/data";
  };
}