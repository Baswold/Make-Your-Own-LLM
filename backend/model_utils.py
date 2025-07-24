import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoConfig,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from pathlib import Path
import json
import psutil
import GPUtil
from typing import Dict, Any, Optional

class ModelManager:
    MODEL_CONFIGS = {
        "toy": {
            "model_name": "microsoft/DialoGPT-small",
            "max_params": 50_000_000,
            "description": "Tiny model for quick testing (~50M params)"
        },
        "base": {
            "model_name": "microsoft/DialoGPT-medium", 
            "max_params": 150_000_000,
            "description": "Small but capable model (~150M params)"
        },
        "plus": {
            "model_name": "microsoft/DialoGPT-large",
            "max_params": 200_000_000,
            "description": "Larger model with better quality (~200M params)"
        }
    }
    
    def __init__(self, workspace_dir: str = "/workspace/data"):
        self.workspace_dir = Path(workspace_dir)
        self.device = self._get_best_device()
    
    def _get_best_device(self) -> str:
        """Auto-detect best available device"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        info = {
            "device": self.device,
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "gpu_available": torch.cuda.is_available()
        }
        
        if torch.cuda.is_available():
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    info.update({
                        "gpu_memory_used": gpu.memoryUsed,
                        "gpu_memory_total": gpu.memoryTotal,
                        "gpu_utilization": gpu.load * 100
                    })
            except:
                pass
        
        return info
    
    def load_model_and_tokenizer(self, model_size: str, project_slug: Optional[str] = None):
        """Load model and tokenizer, either fresh or from checkpoint"""
        config = self.MODEL_CONFIGS[model_size]
        model_name = config["model_name"]
        
        # Check for existing checkpoint
        if project_slug:
            checkpoint_path = self.workspace_dir / project_slug / "checkpoint"
            if checkpoint_path.exists():
                print(f"Loading from checkpoint: {checkpoint_path}")
                model = AutoModelForCausalLM.from_pretrained(checkpoint_path)
                tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
            else:
                model = AutoModelForCausalLM.from_pretrained(model_name)
                tokenizer = AutoTokenizer.from_pretrained(model_name)
        else:
            model = AutoModelForCausalLM.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model.to(self.device)
        return model, tokenizer
    
    def create_trainer(self, model, tokenizer, train_dataset, project_slug: str, 
                      epochs: int = 1, learning_rate: float = 5e-5):
        """Create Trainer instance with appropriate settings"""
        
        output_dir = self.workspace_dir / project_slug / "checkpoint"
        
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=8,
            learning_rate=learning_rate,
            warmup_steps=100,
            logging_steps=10,
            save_steps=100,
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
            fp16=torch.cuda.is_available(),
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
        )
        
        return trainer
    
    def save_model_config(self, project_slug: str, config: Dict[str, Any]):
        """Save model configuration and metadata"""
        project_dir = self.workspace_dir / project_slug
        project_dir.mkdir(exist_ok=True)
        
        config_file = project_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_model_config(self, project_slug: str) -> Dict[str, Any]:
        """Load model configuration"""
        config_file = self.workspace_dir / project_slug / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}

class TrainingCallback:
    """Callback to track training progress"""
    def __init__(self):
        self.logs = []
        self.current_step = 0
        self.total_steps = 0
    
    def on_step_begin(self, step: int, logs: Dict[str, float]):
        self.current_step = step
        self.logs.append({
            "step": step,
            "loss": logs.get("train_loss", 0),
            "learning_rate": logs.get("learning_rate", 0)
        })
    
    def get_progress(self) -> Dict[str, Any]:
        return {
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "progress_percent": (self.current_step / max(self.total_steps, 1)) * 100,
            "recent_logs": self.logs[-10:] if self.logs else []
        }