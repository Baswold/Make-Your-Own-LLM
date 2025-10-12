import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import GPUtil
import psutil
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)


@dataclass
class HardwareSettings:
    """Container for resolved hardware information."""

    device: str
    profile: str
    precision: str
    training_overrides: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device": self.device,
            "profile": self.profile,
            "precision": self.precision,
            "training_overrides": self.training_overrides,
            "warnings": self.warnings,
        }


class ModelManager:
    MODEL_CONFIGS = {
        "toy": {
            "model_name": "microsoft/DialoGPT-small",
            "max_params": 50_000_000,
            "description": "Tiny model for quick testing (~50M params)",
        },
        "base": {
            "model_name": "microsoft/DialoGPT-medium",
            "max_params": 150_000_000,
            "description": "Small but capable model (~150M params)",
        },
        "plus": {
            "model_name": "microsoft/DialoGPT-large",
            "max_params": 200_000_000,
            "description": "Larger model with better quality (~200M params)",
        },
        "1b": {
            "model_name": "EleutherAI/gpt-neo-1.3B",
            "max_params": 1_300_000_000,
            "description": "1B parameter class model for higher quality generations",
        },
    }

    def __init__(self, workspace_dir: Optional[str] = None):
        if workspace_dir is None:
            self.workspace_dir = Path(__file__).parent.parent / "data"
        else:
            self.workspace_dir = Path(workspace_dir)
        self.device = self._get_best_device()

    def _get_best_device(self) -> str:
        """Auto-detect best available device."""
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _available_hardware_profiles(self) -> Dict[str, Dict[str, Any]]:
        has_mps = bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available())
        has_cuda = torch.cuda.is_available()
        return {
            "auto": {"available": True, "device": self._get_best_device()},
            "apple_silicon": {"available": has_mps, "device": "mps"},
            "windows_nvidia": {"available": has_cuda, "device": "cuda"},
            "cpu": {"available": True, "device": "cpu"},
        }

    def get_hardware_settings(self, profile: Optional[str], model_size: str) -> HardwareSettings:
        profile = (profile or "auto").lower()
        available = self._available_hardware_profiles()
        warnings: List[str] = []

        def _fallback_device() -> str:
            best = self._get_best_device()
            if best == "cuda" and not available["windows_nvidia"]["available"]:
                return "cpu"
            if best == "mps" and not available["apple_silicon"]["available"]:
                return "cpu"
            return best

        if profile == "auto":
            if available["windows_nvidia"]["available"]:
                device = "cuda"
                resolved_profile = "windows_nvidia"
            elif available["apple_silicon"]["available"]:
                device = "mps"
                resolved_profile = "apple_silicon"
            else:
                device = "cpu"
                resolved_profile = "cpu"
        elif profile == "apple_silicon":
            if available["apple_silicon"]["available"]:
                device = "mps"
                resolved_profile = "apple_silicon"
            else:
                device = _fallback_device()
                resolved_profile = device
                warnings.append(
                    "Apple Silicon profile requested but Metal (MPS) backend is unavailable. Falling back to"
                    f" {device}."
                )
        elif profile == "windows_nvidia":
            if available["windows_nvidia"]["available"]:
                device = "cuda"
                resolved_profile = "windows_nvidia"
            else:
                device = _fallback_device()
                resolved_profile = device
                warnings.append(
                    "Windows + NVIDIA profile requested but CUDA is unavailable. Falling back to"
                    f" {device}."
                )
        elif profile == "cpu":
            device = "cpu"
            resolved_profile = "cpu"
        else:
            device = _fallback_device()
            resolved_profile = device
            warnings.append(
                f"Unknown hardware profile '{profile}' requested. Using auto-detected device {device}."
            )

        overrides: Dict[str, Any] = {
            "fp16": device == "cuda",
            "bf16": device == "cuda" and bool(getattr(torch.cuda, "is_bf16_supported", lambda: False)()),
            "tf32": device == "cuda",
            "dataloader_pin_memory": device == "cuda",
            "gradient_accumulation_steps": 8,
            "per_device_train_batch_size": 2,
            "gradient_checkpointing": False,
        }

        if device == "mps":
            overrides.update({
                "fp16": False,
                "bf16": False,
                "tf32": False,
                "dataloader_pin_memory": False,
                "gradient_accumulation_steps": 12,
                "per_device_train_batch_size": 1,
                "gradient_checkpointing": True,
            })
        elif device == "cpu":
            overrides.update({
                "fp16": False,
                "bf16": False,
                "tf32": False,
                "dataloader_pin_memory": False,
                "gradient_accumulation_steps": 16,
                "per_device_train_batch_size": 1,
                "gradient_checkpointing": True,
            })

        model_config = self.MODEL_CONFIGS.get(model_size, {})
        if model_config.get("max_params", 0) >= 1_000_000_000:
            overrides["per_device_train_batch_size"] = 1
            overrides["gradient_accumulation_steps"] = max(overrides["gradient_accumulation_steps"], 16)
            overrides["gradient_checkpointing"] = True

        precision = "fp32"
        if overrides.get("bf16"):
            precision = "bf16"
        elif overrides.get("fp16"):
            precision = "fp16"

        self.device = device
        return HardwareSettings(
            device=device,
            profile=resolved_profile,
            precision=precision,
            training_overrides=overrides,
            warnings=warnings,
        )

    def get_system_info(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        auto_settings = self.get_hardware_settings("auto", "toy")
        info = {
            "device": auto_settings.device,
            "precision": auto_settings.precision,
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "gpu_available": torch.cuda.is_available(),
            "hardware_profiles": self._available_hardware_profiles(),
        }

        if torch.cuda.is_available():
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    info.update(
                        {
                            "gpu_memory_used": gpu.memoryUsed,
                            "gpu_memory_total": gpu.memoryTotal,
                            "gpu_utilization": gpu.load * 100,
                        }
                    )
            except Exception:
                # Optional dependency; ignore errors so API continues to function.
                pass

        if auto_settings.warnings:
            info["warnings"] = auto_settings.warnings

        return info

    def load_model_and_tokenizer(
        self,
        model_size: str,
        project_slug: Optional[str] = None,
        hardware_profile: Optional[str] = None,
    ):
        """Load model and tokenizer, either fresh or from checkpoint."""
        config = self.MODEL_CONFIGS[model_size]
        model_name = config["model_name"]

        hardware_settings = self.get_hardware_settings(hardware_profile, model_size)

        if project_slug:
            checkpoint_path = self.workspace_dir / project_slug / "checkpoint"
            if checkpoint_path.exists():
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

        model.to(hardware_settings.device)
        return model, tokenizer, hardware_settings

    def _build_training_arguments(
        self,
        project_slug: str,
        epochs: int,
        learning_rate: float,
        overrides: Dict[str, Any],
    ) -> TrainingArguments:
        output_dir = self.workspace_dir / project_slug / "checkpoint"

        args_kwargs: Dict[str, Any] = {
            "output_dir": str(output_dir),
            "overwrite_output_dir": True,
            "num_train_epochs": epochs,
            "per_device_train_batch_size": overrides["per_device_train_batch_size"],
            "gradient_accumulation_steps": overrides["gradient_accumulation_steps"],
            "learning_rate": learning_rate,
            "warmup_steps": 100,
            "logging_steps": 10,
            "save_steps": 100,
            "save_total_limit": 2,
            "prediction_loss_only": True,
            "remove_unused_columns": False,
            "dataloader_pin_memory": overrides["dataloader_pin_memory"],
            "fp16": overrides["fp16"],
        }

        if "bf16" in overrides:
            args_kwargs["bf16"] = overrides["bf16"]
        if "tf32" in overrides:
            args_kwargs["tf32"] = overrides["tf32"]
        if "gradient_checkpointing" in overrides:
            args_kwargs["gradient_checkpointing"] = overrides["gradient_checkpointing"]

        return TrainingArguments(**args_kwargs)

    def create_trainer(
        self,
        model,
        tokenizer,
        train_dataset,
        project_slug: str,
        epochs: int = 1,
        learning_rate: float = 5e-5,
        hardware_settings: Optional[HardwareSettings] = None,
        model_size: str = "toy",
    ):
        """Create Trainer instance with appropriate settings."""

        hardware_settings = hardware_settings or self.get_hardware_settings("auto", model_size)
        training_args = self._build_training_arguments(
            project_slug=project_slug,
            epochs=epochs,
            learning_rate=learning_rate,
            overrides=hardware_settings.training_overrides,
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
        """Save model configuration and metadata."""
        project_dir = self.workspace_dir / project_slug
        project_dir.mkdir(exist_ok=True)

        config_file = project_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

    def load_model_config(self, project_slug: str) -> Dict[str, Any]:
        """Load model configuration."""
        config_file = self.workspace_dir / project_slug / "config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                return json.load(f)
        return {}


class TrainingCallback(TrainerCallback):
    """Callback to track training progress."""

    def __init__(self, status_ref: Dict[str, Any]):
        super().__init__()
        self.status_ref = status_ref
        self.logs: List[Dict[str, Any]] = []
        self.total_steps: int = 1
        self.start_time: Optional[float] = None
        self.status_ref.setdefault("progress", {})

    def set_total_steps(self, total_steps: int):
        self.total_steps = max(int(total_steps), 1)

    def on_train_begin(self, args, state, control, **kwargs):  # type: ignore[override]
        self.start_time = time.time()
        progress = self.status_ref.get("progress", {})
        progress.setdefault("recent_logs", [])
        self.status_ref["progress"] = progress

    def on_epoch_end(self, args, state, control, **kwargs):  # type: ignore[override]
        progress = self.status_ref.get("progress", {})
        progress["current_epoch"] = int(state.epoch) if state.epoch is not None else 0
        self.status_ref["progress"] = progress
        return control

    def on_log(self, args, state, control, logs=None, **kwargs):  # type: ignore[override]
        if logs is None:
            logs = {}
        if "loss" not in logs:
            return control

        progress = self.status_ref.get("progress", {})
        step = int(state.global_step)
        loss = float(logs["loss"])

        self.logs.append({"step": step, "loss": loss})
        self.logs = self.logs[-200:]

        progress["current_step"] = step
        progress["loss"] = loss
        progress["recent_logs"] = self.logs[-20:]
        progress["progress_percent"] = min(100.0, (step / self.total_steps) * 100.0)

        if self.start_time and step:
            elapsed = max(time.time() - self.start_time, 1e-6)
            steps_per_second = step / elapsed
            remaining_steps = max(self.total_steps - step, 0)
            eta_minutes = (remaining_steps / max(steps_per_second, 1e-6)) / 60
            progress["eta_minutes"] = eta_minutes

        self.status_ref["progress"] = progress
        return control
