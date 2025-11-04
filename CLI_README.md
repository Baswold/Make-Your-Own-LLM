# CLI Tool Documentation

## Overview

The Make Your Own LLM project now includes a powerful command-line interface for training, inference, and model export - alongside the existing web dashboard.

## New Features

### 1. Training Data Generator
**File:** `backend/generate_training_data.py`

Generate synthetic conversational training data in multiple formats.

```bash
# Generate 150 samples (default: 100)
python3 backend/generate_training_data.py --output-dir data/generated --num-samples 150

# Generates:
# - qa_pairs.jsonl (Question-answer pairs)
# - text_completions.txt (Text completion samples)
# - conversations.jsonl (Multi-turn conversations)
# - training_data.csv (CSV format data)
```

### 2. CLI Tool
**File:** `backend/cli.py`

Full-featured CLI for all LLM operations.

##  Commands

### Train a Model

```bash
cd backend
python3 cli.py train PROJECT_NAME DATA_FILE [OPTIONS]

# Example:
python3 cli.py train my-chatbot ../data/generated/text_completions.txt \
  --model-size toy \
  --epochs 3 \
  --learning-rate 5e-5 \
  --hardware-profile auto
```

**Options:**
- `--model-size`: Model size (`toy`, `base`, `plus`, `1b`) - default: `toy`
- `--epochs`: Number of training epochs - default: `3`
- `--learning-rate`: Learning rate - default: `5e-5`
- `--hardware-profile`: Hardware profile (`auto`, `apple_silicon`, `windows_nvidia`, `cpu`)

**Model Sizes:**
- `toy`: ~50M params (DialoGPT-small) - Fast training, good for testing
- `base`: ~150M params (DialoGPT-medium) - Better quality
- `plus`: ~200M params (DialoGPT-large) - High quality
- `1b`: ~1.3B params (GPT-Neo) - Best quality, requires more resources

###  Chat with Trained Model

```bash
python3 cli.py chat PROJECT_NAME [OPTIONS]

# Example:
python3 cli.py chat my-chatbot --model-size toy --max-length 100 --temperature 0.7
```

**Options:**
- `--model-size`: Model size used during training
- `--max-length`: Maximum response length - default: `100`
- `--temperature`: Sampling temperature (0.1-1.0) - default: `0.7`
- `--no-interactive`: Single prompt mode instead of interactive chat

**Interactive Mode:**
```
You: Hello!
Bot: Hello! How can I help you today?

You: Tell me about Python
Bot: Python is a versatile programming language...

You: exit
👋 Goodbye!
```

### Export Models

```bash
python3 cli.py export PROJECT_NAME [OPTIONS]

# Example:
python3 cli.py export my-chatbot \
  --model-size toy \
  --formats hf,safetensors \
  --output-dir exports/my-chatbot
```

**Export Formats:**
- `hf` / `huggingface`: HuggingFace format (compatible with transformers library)
- `safetensors`: SafeTensors format (safer, faster loading)
- `onnx`: ONNX format (production deployment - requires additional setup)

**Formats can be comma-separated:** `--formats hf,safetensors,onnx`

###  List Projects

```bash
python3 cli.py list

# Output:
📂 Available Projects:

   • my-chatbot: ✅ Trained
     Model: toy
     Epochs: 3
     Samples: 150

   • experiment-1: ⏳ No checkpoint
```

###  System Information

```bash
python3 cli.py info

# Output:
🖥️  System Information:

   Device: cuda
   Precision: fp16
   CPU Usage: 45.2%
   Memory Usage: 62.1%
   GPU Available: True
   GPU Memory: 2048MB / 8192MB
   GPU Utilization: 12.5%

   Hardware Profiles:
   ✅ auto: cuda
   ❌ apple_silicon: N/A
   ✅ windows_nvidia: cuda
   ✅ cpu: cpu
```

## Complete Workflow Example

```bash
# 1. Generate training data
python3 backend/generate_training_data.py \
  --output-dir data/my-training \
  --num-samples 200

# 2. Train a model
cd backend
python3 cli.py train storyteller data/my-training/text_completions.txt \
  --model-size toy \
  --epochs 5

# 3. Chat with the model
python3 cli.py chat storyteller --model-size toy

# 4. Export the model
python3 cli.py export storyteller \
  --formats hf,safetensors \
  --output-dir ../exports/storyteller

# 5. List all projects
python3 cli.py list
```

## CLI vs Dashboard

**Use the CLI when:**
- Automating training workflows
- Batch processing multiple models
- Running on remote servers via SSH
- Scripting/CI-CD pipelines
- Quick testing and experimentation

**Use the Dashboard when:**
- Visual progress monitoring
- Real-time training metrics/charts
- Interactive exploration
- Comparing multiple training runs
- Preferred GUI experience

**Both tools:**
- Share the same data directory
- Use identical model architectures
- Support the same formats (TXT, JSONL, CSV, PDF)
- Can load each other's checkpoints

## Data Format Support

The CLI supports all formats that the web dashboard does:

**Text Files (`.txt`)**
```
This is a story about a brave knight.
The knight traveled far and wide.
```

**JSONL (`.jsonl`)**
```json
{"text": "Sample conversation", "metadata": "optional"}
{"text": "Another training example"}
```

**CSV (`.csv`)**
```csv
text,category
"Training sample 1",educational
"Training sample 2",conversational
```

**PDF (`.pdf`)**
- Automatically extracts text content
- Preserves formatting where possible

## Hardware Profiles

The CLI auto-detects your hardware but you can override:

**Apple Silicon (M1/M2/M3)**
```bash
python3 cli.py train my-bot data.txt --hardware-profile apple_silicon
```
- Uses MPS (Metal Performance Shaders)
- Optimized batch sizes for unified memory
- BF16 mixed precision when available

**Windows/Linux with NVIDIA GPU**
```bash
python3 cli.py train my-bot data.txt --hardware-profile windows_nvidia
```
- Uses CUDA
- FP16 mixed precision
- Larger batch sizes

**CPU Only**
```bash
python3 cli.py train my-bot data.txt --hardware-profile cpu
```
- Works on any system
- Slower but reliable
- Smaller batch sizes to conserve memory

**Auto (Recommended)**
```bash
python3 cli.py train my-bot data.txt --hardware-profile auto
```
- Detects best available hardware
- Automatically optimizes settings
- Fallback to CPU if needed

## Tips & Best Practices

###  Training

1. **Start Small**: Use `toy` model size for testing, scale up later
2. **Monitor Progress**: Training logs show loss every 10 steps
3. **Save Often**: Checkpoints saved every 100 steps automatically
4. **Experiment with Epochs**: 3-5 epochs for small datasets, 1-2 for large ones

###  Data

1. **More is Better**: Aim for 100+ samples minimum
2. **Quality Matters**: Clean, relevant data trains better
3. **Mix Formats**: Combine different data sources
4. **Use Generator**: Quick testing with synthetic data

###  Inference

1. **Temperature**: Lower (0.3-0.5) for focused outputs, higher (0.7-0.9) for creative
2. **Max Length**: Balance between detail and speed
3. **Model Size**: Larger models = better quality but slower

###  Export

1. **HuggingFace**: Best compatibility, widely supported
2. **SafeTensors**: Faster loading, safer format
3. **ONNX**: For production deployment (requires additional config)

## Troubleshooting

**"ModuleNotFoundError: No module named 'torch'"**
```bash
pip3 install torch transformers datasets tokenizers
# Or use the project's setup:
make install-backend
```

**"CUDA out of memory"**
- Use smaller `--model-size`
- Reduce batch size (automatic with CPU profile)
- Close other GPU applications

**"Training very slow"**
- Check `--hardware-profile` is set correctly
- Ensure GPU drivers installed (NVIDIA/Metal)
- Consider smaller model size for faster iteration

**"Model not generating good responses"**
- Train for more epochs
- Use larger model size
- Provide more/better training data
- Adjust temperature during inference

## Integration with Web Dashboard

The CLI and web dashboard work together seamlessly:

**Train with CLI, Monitor with Dashboard:**
```bash
# Terminal 1: Train with CLI
python3 cli.py train my-bot data.txt

# Terminal 2: Start dashboard
make dev

# Open browser: http://localhost:3000
# Select "my-bot" project to see training progress
```

**All projects appear in both interfaces:**
- CLI-trained models show up in dashboard
- Dashboard-trained models work with CLI
- Shared checkpoint directory

## Advanced Usage

### Custom Workspace Directory

```bash
python3 cli.py --workspace /path/to/custom/data train my-bot data.txt
```

### Scripting

```python
#!/usr/bin/env python3
import subprocess

projects = ["bot-1", "bot-2", "bot-3"]
data = ["data1.txt", "data2.txt", "data3.txt"]

for proj, data_file in zip(projects, data):
    subprocess.run([
        "python3", "cli.py", "train",
        proj, data_file,
        "--model-size", "toy",
        "--epochs", "3"
    ])
```

### Batch Export

```bash
# Export all trained projects
for project in $(python3 cli.py list | grep "✅" | awk '{print $2}' | tr -d ':'); do
  python3 cli.py export "$project" --formats hf,safetensors
done
```

## Requirements

- Python 3.11+
- PyTorch 2.0+
- Transformers 4.30+
- 4GB+ RAM (8GB+ recommended)
- Optional: GPU with 4GB+ VRAM

Install all dependencies:
```bash
pip3 install -r requirements.txt
# Or
make install-backend
```

## Support

For issues or questions:
1. Check this documentation
2. Review `CLAUDE.md` for project overview
3. Check `Makefile` for additional commands
4. Raise an issue in the GitHub repository

## What's Next?

- **Model Versioning**: Track different training runs
- **Validation Sets**: Monitor overfitting
- **Distributed Training**: Train across multiple GPUs
- **Model Quantization**: Smaller, faster models
- **Full ONNX Export**: Production-ready deployment
- **Custom Architectures**: Beyond DialoGPT/GPT-Neo
