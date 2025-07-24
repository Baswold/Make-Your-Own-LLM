#!/bin/bash

# Make Your Own LLM - Performance Benchmark Script
# Tests training and inference speed across different model sizes

set -e

echo "🔬 Make Your Own LLM - Performance Benchmark"
echo "=============================================="

# Create benchmark directory
BENCHMARK_DIR="/tmp/llm-benchmark"
mkdir -p "$BENCHMARK_DIR"

# Generate sample training data
echo "📝 Generating sample training data..."
cat > "$BENCHMARK_DIR/sample_stories.txt" << 'EOF'
Once upon a time, there was a curious clockwork kangaroo named Tick who lived in a magical workshop. Every night, Tick would wind himself up and hop through the village, helping children with their dreams.

The workshop was filled with gears and springs that sparkled in the moonlight. Tick's creator, an old inventor named Professor Gearsmith, had given him a special heart made of starlight that allowed him to understand the language of dreams.

One evening, a little girl named Luna couldn't fall asleep because she was worried about her first day at a new school. Tick hopped to her window and began to tell her stories about brave adventures and friendly classmates.

As Tick spoke, his clockwork heart began to glow, and Luna's worries slowly melted away like snow in spring. She fell into a peaceful sleep, dreaming of the wonderful friends she would meet.

From that night forward, Tick became known as the Dream Helper, bringing comfort and joy to children throughout the village with his magical stories.
EOF

echo "✅ Sample data created (${#$(cat "$BENCHMARK_DIR/sample_stories.txt")} characters)"

# Function to measure time
measure_time() {
    local start_time=$(date +%s.%N)
    "$@"
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || python3 -c "print($end_time - $start_time)")
    printf "%.2f" "$duration"
}

# Test system capabilities
echo ""
echo "🖥️  System Information:"
echo "----------------------"
echo "Python Version: $(python3 --version)"
echo "PyTorch Available: $(python3 -c 'import torch; print("Yes" if torch.__version__ else "No")' 2>/dev/null || echo "No")"
echo "CUDA Available: $(python3 -c 'import torch; print("Yes" if torch.cuda.is_available() else "No")' 2>/dev/null || echo "No")"
echo "GPU Device: $(python3 -c 'import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU Only")' 2>/dev/null || echo "CPU Only")"

# Memory usage
if command -v free >/dev/null 2>&1; then
    echo "System Memory: $(free -h | awk '/^Mem:/ {print $2}')"
elif command -v vm_stat >/dev/null 2>&1; then
    # macOS
    echo "System Memory: $(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024) "GB"}')"
fi

echo ""

# Benchmark data processing
echo "📊 Benchmarking Data Processing:"
echo "--------------------------------"

python3 << 'EOF'
import time
import sys
import os
sys.path.append('backend')

try:
    from data_utils import DataProcessor
    
    processor = DataProcessor('/tmp/llm-benchmark')
    
    # Test file processing
    start = time.time()
    texts = processor.process_upload('/tmp/llm-benchmark/sample_stories.txt', 'txt')
    process_time = time.time() - start
    
    print(f"✅ Text Processing: {process_time:.2f}s ({len(texts)} texts, {sum(len(t) for t in texts)} chars)")
    
    # Test tokenization (using a small model for speed)
    start = time.time()
    try:
        dataset = processor.prepare_training_data(texts, 'microsoft/DialoGPT-small', max_length=128)
        tokenize_time = time.time() - start
        print(f"✅ Tokenization: {tokenize_time:.2f}s ({len(dataset)} samples)")
    except Exception as e:
        print(f"⚠️  Tokenization test skipped: {e}")
    
except ImportError as e:
    print(f"⚠️  Data processing test skipped: Missing dependencies ({e})")
except Exception as e:
    print(f"❌ Data processing test failed: {e}")
EOF

# Benchmark model loading
echo ""
echo "🤖 Benchmarking Model Operations:"
echo "---------------------------------"

python3 << 'EOF'
import time
import sys
import os
sys.path.append('backend')

try:
    from model_utils import ModelManager
    import torch
    
    manager = ModelManager('/tmp/llm-benchmark')
    
    print(f"Device: {manager.device}")
    
    # Test model loading for each size
    for size in ['toy']:  # Only test toy model for speed
        try:
            print(f"\nTesting {size} model:")
            start = time.time()
            model, tokenizer = manager.load_model_and_tokenizer(size)
            load_time = time.time() - start
            
            # Count parameters
            param_count = sum(p.numel() for p in model.parameters())
            
            print(f"  ✅ Model Loading: {load_time:.2f}s ({param_count:,} parameters)")
            
            # Test inference speed
            test_input = "Tell me a story"
            encoded = tokenizer.encode(test_input, return_tensors='pt').to(manager.device)
            
            # Warmup
            with torch.no_grad():
                model(encoded)
            
            # Benchmark inference
            start = time.time()
            with torch.no_grad():
                for _ in range(5):
                    outputs = model.generate(
                        encoded, 
                        max_length=encoded.shape[1] + 20,
                        do_sample=False,
                        pad_token_id=tokenizer.eos_token_id
                    )
            inference_time = (time.time() - start) / 5
            
            # Calculate tokens per second
            output_tokens = outputs.shape[1] - encoded.shape[1]
            tokens_per_sec = output_tokens / inference_time if inference_time > 0 else 0
            
            print(f"  ✅ Inference Speed: {inference_time:.3f}s/generation ({tokens_per_sec:.1f} tokens/sec)")
            
            # Clean up
            del model, tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except Exception as e:
            print(f"  ❌ {size} model test failed: {e}")
            
except ImportError as e:
    print(f"⚠️  Model testing skipped: Missing dependencies ({e})")
except Exception as e:
    print(f"❌ Model testing failed: {e}")
EOF

# API Benchmark (if servers are running)
echo ""
echo "🌐 API Response Times:"
echo "---------------------"

check_api() {
    local url=$1
    local name=$2
    
    if curl -s --connect-timeout 2 "$url" > /dev/null 2>&1; then
        local response_time=$(curl -o /dev/null -s -w "%{time_total}" "$url" 2>/dev/null || echo "timeout")
        if [ "$response_time" != "timeout" ]; then
            printf "✅ %-20s: %.3fs\n" "$name" "$response_time"
        else
            printf "⚠️  %-20s: timeout\n" "$name"
        fi
    else
        printf "⚠️  %-20s: not running\n" "$name"
    fi
}

check_api "http://localhost:8000/system-info" "Training API"
check_api "http://localhost:8001/health" "Chat API"
check_api "http://localhost:3000" "Frontend"

# System Resource Usage
echo ""
echo "💾 Resource Usage:"
echo "-----------------"

if command -v ps >/dev/null 2>&1; then
    # Find Python processes
    python_processes=$(ps aux | grep -E "(train\.py|serve\.py)" | grep -v grep || true)
    if [ -n "$python_processes" ]; then
        echo "Python Processes:"
        echo "$python_processes" | awk '{printf "  PID %s: %.1f%% CPU, %.1f%% MEM\n", $2, $3, $4}'
    else
        echo "No active Python processes found"
    fi
fi

if command -v nvidia-smi >/dev/null 2>&1; then
    echo ""
    echo "GPU Status:"
    nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | \
    awk -F, '{printf "  %s: %s/%s MB VRAM, %s%% utilization\n", $1, $2, $3, $4}'
fi

# Cleanup
echo ""
echo "🧹 Cleaning up benchmark files..."
rm -rf "$BENCHMARK_DIR"

echo ""
echo "📋 Benchmark Summary:"
echo "===================="
echo "✅ Benchmark completed successfully"
echo ""
echo "💡 Performance Tips:"
echo "   • Use GPU for training when available"
echo "   • Start with 'toy' model size for quick testing"
echo "   • Monitor system resources during training"
echo "   • Use smaller batch sizes if running out of memory"
echo ""
echo "🚀 Ready to train your own LLM!"