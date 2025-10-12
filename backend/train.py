import asyncio
import json
import math
import time
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from data_utils import DataProcessor
from model_utils import ModelManager, TrainingCallback

app = FastAPI(title="LLM Training API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
data_processor = DataProcessor()
model_manager = ModelManager()
training_status = {"is_training": False, "project": None, "progress": {}}
current_trainer = None
training_callback = None

class TrainingConfig(BaseModel):
    project_slug: str
    model_size: str
    epochs: int = 1
    learning_rate: float = 5e-5
    use_case: str = "general"
    temperature: float = 0.7
    hardware_profile: str = "auto"

class ContinueTrainingConfig(BaseModel):
    project_slug: str
    additional_epochs: int = 1
    hardware_profile: Optional[str] = None

@app.get("/system-info")
async def get_system_info():
    """Get current system resource usage"""
    return model_manager.get_system_info()

@app.get("/projects")
async def get_projects():
    """Get list of existing projects"""
    return {"projects": data_processor.get_project_list()}

@app.post("/upload-data")
async def upload_data(project_slug: str, file: UploadFile = File(...)):
    """Upload and process training data"""
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Determine file type
        file_type = file.filename.split('.')[-1].lower()
        if file_type not in ['txt', 'jsonl', 'csv', 'pdf']:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Process the file
        texts = data_processor.process_upload(temp_path, file_type)
        
        if not texts:
            raise HTTPException(status_code=400, detail="No text content found in file")
        
        # Save corpus
        data_processor.save_corpus(project_slug, texts)
        
        return {
            "success": True,
            "texts_count": len(texts),
            "total_chars": sum(len(text) for text in texts)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start-training")
async def start_training(config: TrainingConfig):
    """Start model training"""
    global training_status, current_trainer, training_callback
    
    if training_status["is_training"]:
        raise HTTPException(status_code=400, detail="Training already in progress")
    
    try:
        # Load corpus
        texts = data_processor.load_corpus(config.project_slug)
        if not texts:
            raise HTTPException(status_code=400, detail="No training data found")
        
        # Resolve hardware profile early so the UI can display the plan
        hardware_settings = model_manager.get_hardware_settings(
            config.hardware_profile, config.model_size
        )

        # Initialize training status
        training_status = {
            "is_training": True,
            "project": config.project_slug,
            "progress": {
                "current_epoch": 0,
                "total_epochs": config.epochs,
                "current_step": 0,
                "total_steps": 0,
                "loss": 0.0,
                "eta_minutes": 0,
                "start_time": time.time(),
                "progress_percent": 0.0,
                "model_size": config.model_size,
                "hardware": hardware_settings.to_dict(),
            }
        }

        # Save model config
        model_config = {
            "model_size": config.model_size,
            "epochs": config.epochs,
            "learning_rate": config.learning_rate,
            "use_case": config.use_case,
            "temperature": config.temperature,
            "hardware_profile": config.hardware_profile,
            "resolved_device": hardware_settings.device,
            "precision": hardware_settings.precision,
            "hardware_warnings": hardware_settings.warnings,
            "created_at": time.time()
        }
        model_manager.save_model_config(config.project_slug, model_config)

        # Start training in background
        asyncio.create_task(run_training(config, texts))
        
        return {"success": True, "message": "Training started"}
    
    except Exception as e:
        training_status["is_training"] = False
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/continue-training")
async def continue_training(config: ContinueTrainingConfig):
    """Continue training with additional data/epochs"""
    global training_status
    
    if training_status["is_training"]:
        raise HTTPException(status_code=400, detail="Training already in progress")
    
    try:
        # Load existing model config
        model_config = model_manager.load_model_config(config.project_slug)
        if not model_config:
            raise HTTPException(status_code=400, detail="Project not found")
        
        # Create training config from existing settings
        training_config = TrainingConfig(
            project_slug=config.project_slug,
            model_size=model_config["model_size"],
            epochs=config.additional_epochs,
            learning_rate=model_config.get("learning_rate", 5e-5),
            use_case=model_config.get("use_case", "general"),
            temperature=model_config.get("temperature", 0.7),
            hardware_profile=(
                config.hardware_profile
                if config.hardware_profile is not None
                else model_config.get("hardware_profile", "auto")
            ),
        )

        hardware_settings = model_manager.get_hardware_settings(
            training_config.hardware_profile, training_config.model_size
        )

        # Load corpus
        texts = data_processor.load_corpus(config.project_slug)
        if not texts:
            raise HTTPException(status_code=400, detail="No training data found")

        # Initialize training status
        training_status = {
            "is_training": True,
            "project": config.project_slug,
            "progress": {
                "current_epoch": 0,
                "total_epochs": config.additional_epochs,
                "current_step": 0,
                "total_steps": 0,
                "loss": 0.0,
                "eta_minutes": 0,
                "start_time": time.time(),
                "progress_percent": 0.0,
                "model_size": training_config.model_size,
                "hardware": hardware_settings.to_dict(),
            }
        }

        # Persist potential hardware override for future sessions
        model_config.update(
            {
                "hardware_profile": training_config.hardware_profile,
                "resolved_device": hardware_settings.device,
                "precision": hardware_settings.precision,
                "hardware_warnings": hardware_settings.warnings,
                "updated_at": time.time(),
            }
        )
        model_manager.save_model_config(config.project_slug, model_config)

        # Start training in background
        asyncio.create_task(run_training(training_config, texts))
        
        return {"success": True, "message": "Continue training started"}
    
    except Exception as e:
        training_status["is_training"] = False
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/training-status")
async def get_training_status():
    """Get current training status and progress"""
    return training_status

async def run_training(config: TrainingConfig, texts):
    """Background training task"""
    global training_status, current_trainer, training_callback
    
    try:
        # Load model, tokenizer, and resolve hardware
        model, tokenizer, hardware_settings = model_manager.load_model_and_tokenizer(
            config.model_size, config.project_slug, config.hardware_profile
        )

        # Prepare training data
        train_dataset = data_processor.prepare_training_data(
            texts, model_manager.MODEL_CONFIGS[config.model_size]["model_name"]
        )

        # Create trainer with hardware-specific arguments
        trainer = model_manager.create_trainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=train_dataset,
            project_slug=config.project_slug,
            epochs=config.epochs,
            learning_rate=config.learning_rate,
            hardware_settings=hardware_settings,
            model_size=config.model_size,
        )

        current_trainer = trainer

        progress: Dict[str, Any] = training_status.setdefault("progress", {})
        progress.update(
            {
                "hardware": hardware_settings.to_dict(),
                "model_size": config.model_size,
                "precision": hardware_settings.precision,
                "total_epochs": config.epochs,
                "start_time": time.time(),
            }
        )

        # Calculate total steps with gradient accumulation accounted for
        batch_size = max(trainer.args.per_device_train_batch_size, 1)
        grad_accum = max(trainer.args.gradient_accumulation_steps, 1)
        dataset_length = max(len(train_dataset), 1)
        steps_per_epoch = math.ceil(dataset_length / (batch_size * grad_accum))
        total_steps = max(steps_per_epoch * config.epochs, 1)

        progress["total_steps"] = total_steps
        training_status["progress"] = progress

        training_callback = TrainingCallback(training_status)
        training_callback.set_total_steps(total_steps)
        trainer.add_callback(training_callback)

        # Execute training
        trainer.train()

        # Save final model
        trainer.save_model()
        tokenizer.save_pretrained(str(Path(trainer.args.output_dir)))

        # Update status
        training_status["is_training"] = False
        training_status.setdefault("progress", {})
        training_status["progress"].update(
            {
                "completed": True,
                "progress_percent": 100.0,
                "eta_minutes": 0,
            }
        )

    except Exception as e:
        print(f"Training error: {e}")
        training_status["is_training"] = False
        training_status["error"] = str(e)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
