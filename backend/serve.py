import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, AsyncGenerator
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import torch
from transformers import TextGenerationPipeline, AutoTokenizer, AutoModelForCausalLM

from model_utils import ModelManager

app = FastAPI(title="LLM Chat Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
model_manager = ModelManager()
active_models: Dict[str, Dict[str, Any]] = {}

class ChatMessage(BaseModel):
    message: str
    project_slug: str
    temperature: float = 0.7
    max_tokens: int = 150
    top_p: float = 0.9

class ModelLoadRequest(BaseModel):
    project_slug: str

@app.post("/load-model")
async def load_model(request: ModelLoadRequest):
    """Load a trained model for inference"""
    try:
        # Check if model is already loaded
        if request.project_slug in active_models:
            return {"success": True, "message": "Model already loaded"}
        
        # Load model config
        config = model_manager.load_model_config(request.project_slug)
        if not config:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if checkpoint exists
        checkpoint_path = Path(model_manager.workspace_dir) / request.project_slug / "checkpoint"
        if not checkpoint_path.exists():
            raise HTTPException(status_code=404, detail="No trained model found")
        
        # Load model and tokenizer
        model = AutoModelForCausalLM.from_pretrained(str(checkpoint_path))
        tokenizer = AutoTokenizer.from_pretrained(str(checkpoint_path))
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Create text generation pipeline
        pipeline = TextGenerationPipeline(
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1,
            return_full_text=False,
            do_sample=True
        )
        
        # Store in active models
        active_models[request.project_slug] = {
            "pipeline": pipeline,
            "tokenizer": tokenizer,
            "config": config,
            "loaded_at": time.time()
        }
        
        return {"success": True, "message": "Model loaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/unload-model")
async def unload_model(request: ModelLoadRequest):
    """Unload a model from memory"""
    if request.project_slug in active_models:
        del active_models[request.project_slug]
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        return {"success": True, "message": "Model unloaded"}
    else:
        raise HTTPException(status_code=404, detail="Model not loaded")

@app.get("/active-models")
async def get_active_models():
    """Get list of currently loaded models"""
    models = []
    for slug, model_data in active_models.items():
        models.append({
            "project_slug": slug,
            "config": model_data["config"],
            "loaded_at": model_data["loaded_at"]
        })
    return {"models": models}

@app.post("/chat")
async def chat(message: ChatMessage):
    """Generate response for a chat message"""
    try:
        if message.project_slug not in active_models:
            raise HTTPException(status_code=404, detail="Model not loaded")
        
        model_data = active_models[message.project_slug]
        pipeline = model_data["pipeline"]
        
        # Generate response
        start_time = time.time()
        
        response = pipeline(
            message.message,
            max_length=len(message.message.split()) + message.max_tokens,
            temperature=message.temperature,
            top_p=message.top_p,
            do_sample=True,
            pad_token_id=pipeline.tokenizer.eos_token_id
        )
        
        generated_text = response[0]["generated_text"]
        latency = time.time() - start_time
        
        # Count tokens
        input_tokens = len(pipeline.tokenizer.encode(message.message))
        output_tokens = len(pipeline.tokenizer.encode(generated_text))
        
        return {
            "response": generated_text,
            "latency_ms": round(latency * 1000, 2),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))

manager = ConnectionManager()

@app.websocket("/chat-stream/{project_slug}/{client_id}")
async def websocket_chat(websocket: WebSocket, project_slug: str, client_id: str):
    """WebSocket endpoint for streaming chat responses"""
    await manager.connect(websocket, client_id)
    
    try:
        if project_slug not in active_models:
            await manager.send_message(
                {"error": "Model not loaded"}, client_id
            )
            return
        
        model_data = active_models[project_slug]
        pipeline = model_data["pipeline"]
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            temperature = message_data.get("temperature", 0.7)
            max_tokens = message_data.get("max_tokens", 150)
            
            # Send acknowledgment
            await manager.send_message({
                "type": "message_received",
                "message": user_message
            }, client_id)
            
            # Generate streaming response
            start_time = time.time()
            
            try:
                # For now, generate full response (streaming would require custom implementation)
                response = pipeline(
                    user_message,
                    max_length=len(user_message.split()) + max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=pipeline.tokenizer.eos_token_id
                )
                
                generated_text = response[0]["generated_text"]
                latency = time.time() - start_time
                
                # Send response in chunks to simulate streaming
                words = generated_text.split()
                for i, word in enumerate(words):
                    await manager.send_message({
                        "type": "token",
                        "token": word + " ",
                        "is_final": i == len(words) - 1
                    }, client_id)
                    await asyncio.sleep(0.05)  # Simulate streaming delay
                
                # Send final metrics
                input_tokens = len(pipeline.tokenizer.encode(user_message))
                output_tokens = len(pipeline.tokenizer.encode(generated_text))
                
                await manager.send_message({
                    "type": "complete",
                    "latency_ms": round(latency * 1000, 2),
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                }, client_id)
                
            except Exception as e:
                await manager.send_message({
                    "type": "error",
                    "error": str(e)
                }, client_id)
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_models": len(active_models),
        "system_info": model_manager.get_system_info()
    }

# Serve static files for frontend
if Path("../frontend/dist").exists():
    app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)