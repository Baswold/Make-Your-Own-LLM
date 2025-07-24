import os
import json
import pandas as pd
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any
from transformers import AutoTokenizer
from datasets import Dataset
import torch

class DataProcessor:
    def __init__(self, workspace_dir: str = "/workspace/data"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
    
    def process_upload(self, file_path: str, file_type: str) -> List[str]:
        """Process uploaded file and extract text content"""
        texts = []
        
        if file_type == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                texts = [content]
        
        elif file_type == "jsonl":
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    if 'text' in data:
                        texts.append(data['text'])
                    elif 'content' in data:
                        texts.append(data['content'])
        
        elif file_type == "csv":
            df = pd.read_csv(file_path)
            text_columns = ['text', 'content', 'story', 'message']
            for col in text_columns:
                if col in df.columns:
                    texts.extend(df[col].dropna().tolist())
                    break
        
        elif file_type == "pdf":
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        texts.append(text)
        
        return texts
    
    def prepare_training_data(self, texts: List[str], tokenizer_name: str, max_length: int = 512) -> Dataset:
        """Tokenize and prepare data for training"""
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=max_length,
                return_tensors="pt"
            )
        
        dataset = Dataset.from_dict({"text": texts})
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        return tokenized_dataset
    
    def save_corpus(self, project_slug: str, texts: List[str]):
        """Save processed corpus to workspace"""
        project_dir = self.workspace_dir / project_slug
        project_dir.mkdir(exist_ok=True)
        
        corpus_file = project_dir / "corpus.json"
        with open(corpus_file, 'w', encoding='utf-8') as f:
            json.dump({"texts": texts}, f, indent=2)
    
    def load_corpus(self, project_slug: str) -> List[str]:
        """Load previously saved corpus"""
        corpus_file = self.workspace_dir / project_slug / "corpus.json"
        if corpus_file.exists():
            with open(corpus_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("texts", [])
        return []
    
    def get_project_list(self) -> List[str]:
        """Get list of existing projects"""
        if not self.workspace_dir.exists():
            return []
        return [d.name for d in self.workspace_dir.iterdir() if d.is_dir()]