import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
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

class ContinueTrainingConfig(BaseModel):
    project_slug: str
    additional_epochs: int = 1

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
                "start_time": time.time()
            }
        }
        
        # Save model config
        model_config = {
            "model_size": config.model_size,
            "epochs": config.epochs,
            "learning_rate": config.learning_rate,
            "use_case": config.use_case,
            "temperature": config.temperature,
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
            temperature=model_config.get("temperature", 0.7)
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
                "start_time": time.time()
            }
        }
        
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
        # Load model and tokenizer
        model, tokenizer = model_manager.load_model_and_tokenizer(
            config.model_size, config.project_slug
        )
        
        # Prepare training data
        train_dataset = data_processor.prepare_training_data(
            texts, model_manager.MODEL_CONFIGS[config.model_size]["model_name"]
        )
        
        # Create trainer
        trainer = model_manager.create_trainer(
            model, tokenizer, train_dataset, config.project_slug,
            config.epochs, config.learning_rate
        )
        
        current_trainer = trainer
        training_callback = TrainingCallback()
        
        # Calculate total steps
        total_steps = len(train_dataset) // trainer.args.per_device_train_batch_size
        total_steps = total_steps // trainer.args.gradient_accumulation_steps
        total_steps *= config.epochs
        
        training_status["progress"]["total_steps"] = total_steps
        
        # Custom training loop with progress updates
        model.train()
        start_time = time.time()
        
        for epoch in range(config.epochs):
            training_status["progress"]["current_epoch"] = epoch + 1
            
            # Run one epoch
            trainer.train()
            
            # Update progress
            elapsed_time = time.time() - start_time
            remaining_epochs = config.epochs - (epoch + 1)
            if epoch > 0:
                avg_time_per_epoch = elapsed_time / (epoch + 1)
                eta_minutes = (avg_time_per_epoch * remaining_epochs) / 60
                training_status["progress"]["eta_minutes"] = eta_minutes
        
        # Save final model
        trainer.save_model()
        tokenizer.save_pretrained(str(Path(trainer.args.output_dir)))
        
        # Update status
        training_status["is_training"] = False
        training_status["progress"]["completed"] = True
        
    except Exception as e:
        print(f"Training error: {e}")
        training_status["is_training"] = False
        training_status["error"] = str(e)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)