#!/usr/bin/env python3
"""
Make Your Own LLM - Command Line Interface

CLI tool for training, inference, and model export.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import torch
from transformers import pipeline

# Import project modules
from data_utils import DataProcessor
from model_utils import ModelManager


class LLMCLI:
    """Command-line interface for LLM operations"""

    def __init__(self, workspace_dir: str = "data"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.model_manager = ModelManager(workspace_dir=str(self.workspace_dir))

    def train(
        self,
        project: str,
        data_path: str,
        model_size: str = "toy",
        epochs: int = 3,
        learning_rate: float = 5e-5,
        hardware_profile: Optional[str] = None,
    ):
        """Train a model on provided data"""
        print(f"\n🚀 Starting training for project: {project}")
        print(f"📁 Data: {data_path}")
        print(f"🤖 Model size: {model_size}")
        print(f"📊 Epochs: {epochs}")
        print(f"📈 Learning rate: {learning_rate}\n")

        # Process data
        data_file = Path(data_path)
        if not data_file.exists():
            print(f"❌ Error: Data file not found: {data_path}")
            sys.exit(1)

        project_dir = self.workspace_dir / project
        project_dir.mkdir(parents=True, exist_ok=True)

        print("📚 Processing training data...")
        processor = DataProcessor(project_dir=str(project_dir))

        # Read file content
        with open(data_file, "rb") as f:
            file_content = f.read()

        # Process and save corpus
        corpus_result = processor.process_file(
            filename=data_file.name,
            file_content=file_content,
            project_slug=project
        )

        print(f"✅ Processed {len(corpus_result['corpus'])} text samples")

        # Load model and tokenizer
        print(f"\n🔧 Loading {model_size} model...")
        model, tokenizer, hardware_settings = self.model_manager.load_model_and_tokenizer(
            model_size=model_size,
            project_slug=project,
            hardware_profile=hardware_profile
        )

        print(f"💻 Device: {hardware_settings.device}")
        print(f"⚡ Precision: {hardware_settings.precision}")

        # Prepare dataset
        print("\n📦 Preparing dataset...")
        train_dataset = processor.prepare_dataset(
            project_slug=project,
            tokenizer=tokenizer,
            max_length=128
        )

        print(f"✅ Dataset ready: {len(train_dataset)} samples")

        # Create trainer
        print(f"\n🏋️ Creating trainer...")
        trainer = self.model_manager.create_trainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=train_dataset,
            project_slug=project,
            epochs=epochs,
            learning_rate=learning_rate,
            hardware_settings=hardware_settings
        )

        # Train
        print(f"\n🔥 Starting training...\n")
        try:
            trainer.train()
            print(f"\n✅ Training completed successfully!")

            # Save model
            checkpoint_path = project_dir / "checkpoint"
            print(f"\n💾 Saving model to {checkpoint_path}...")
            trainer.save_model(str(checkpoint_path))
            tokenizer.save_pretrained(str(checkpoint_path))

            # Save metadata
            metadata = {
                "project": project,
                "model_size": model_size,
                "epochs": epochs,
                "learning_rate": learning_rate,
                "device": hardware_settings.device,
                "precision": hardware_settings.precision,
                "data_file": str(data_file),
                "num_samples": len(train_dataset)
            }

            with open(project_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            print(f"✅ Model saved successfully!")
            print(f"\n📊 Training Summary:")
            print(f"   Project: {project}")
            print(f"   Model: {model_size}")
            print(f"   Samples: {len(train_dataset)}")
            print(f"   Epochs: {epochs}")
            print(f"   Device: {hardware_settings.device}")
            print(f"   Checkpoint: {checkpoint_path}")

        except Exception as e:
            print(f"\n❌ Training failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def chat(
        self,
        project: str,
        model_size: str = "toy",
        max_length: int = 100,
        temperature: float = 0.7,
        interactive: bool = True
    ):
        """Chat with a trained model"""
        print(f"\n💬 Loading model for project: {project}\n")

        # Load model
        model, tokenizer, hardware_settings = self.model_manager.load_model_and_tokenizer(
            model_size=model_size,
            project_slug=project,
            hardware_profile=None
        )

        print(f"✅ Model loaded on {hardware_settings.device}")

        if interactive:
            print("\n🤖 Interactive chat mode (type 'exit' or 'quit' to stop)\n")

            while True:
                try:
                    user_input = input("You: ").strip()

                    if user_input.lower() in ['exit', 'quit', 'q']:
                        print("\n👋 Goodbye!")
                        break

                    if not user_input:
                        continue

                    # Generate response
                    inputs = tokenizer.encode(user_input, return_tensors="pt")
                    inputs = inputs.to(hardware_settings.device)

                    with torch.no_grad():
                        outputs = model.generate(
                            inputs,
                            max_length=max_length,
                            temperature=temperature,
                            do_sample=True,
                            pad_token_id=tokenizer.eos_token_id
                        )

                    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    print(f"Bot: {response}\n")

                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {str(e)}\n")
        else:
            # Single prompt mode
            prompt = input("Enter prompt: ")
            inputs = tokenizer.encode(prompt, return_tensors="pt")
            inputs = inputs.to(hardware_settings.device)

            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )

            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"\n{response}")

    def export(
        self,
        project: str,
        model_size: str = "toy",
        output_dir: Optional[str] = None,
        formats: str = "hf"
    ):
        """Export trained model in various formats"""
        print(f"\n📦 Exporting model for project: {project}")

        if output_dir is None:
            output_dir = str(self.workspace_dir / project / "exports")

        export_path = Path(output_dir)
        export_path.mkdir(parents=True, exist_ok=True)

        # Load model
        print("\n🔧 Loading model...")
        model, tokenizer, hardware_settings = self.model_manager.load_model_and_tokenizer(
            model_size=model_size,
            project_slug=project,
            hardware_profile=None
        )

        export_formats = formats.split(',')

        for fmt in export_formats:
            fmt = fmt.strip().lower()

            if fmt == 'hf' or fmt == 'huggingface':
                # HuggingFace format (already saved during training)
                hf_path = export_path / "huggingface"
                hf_path.mkdir(exist_ok=True)
                print(f"\n💾 Exporting to HuggingFace format: {hf_path}")
                model.save_pretrained(str(hf_path))
                tokenizer.save_pretrained(str(hf_path))
                print("✅ HuggingFace export complete")

            elif fmt == 'onnx':
                print(f"\n💾 Exporting to ONNX format...")
                try:
                    from transformers.onnx import export as onnx_export
                    onnx_path = export_path / "onnx"
                    onnx_path.mkdir(exist_ok=True)

                    # Note: ONNX export requires specific pipeline setup
                    print("⚠️  ONNX export requires additional configuration")
                    print("    This is a placeholder - full ONNX export coming soon")

                except ImportError:
                    print("❌ ONNX export requires: pip install onnx onnxruntime")

            elif fmt == 'safetensors':
                print(f"\n💾 Exporting to SafeTensors format...")
                try:
                    st_path = export_path / "safetensors"
                    st_path.mkdir(exist_ok=True)
                    model.save_pretrained(
                        str(st_path),
                        safe_serialization=True
                    )
                    tokenizer.save_pretrained(str(st_path))
                    print("✅ SafeTensors export complete")
                except Exception as e:
                    print(f"❌ SafeTensors export failed: {str(e)}")

            else:
                print(f"⚠️  Unknown format: {fmt}")

        print(f"\n✅ Export complete: {export_path}")

    def list_projects(self):
        """List all available projects"""
        print("\n📂 Available Projects:\n")

        projects = [p for p in self.workspace_dir.iterdir() if p.is_dir() and not p.name.startswith('.')]

        if not projects:
            print("   No projects found.")
            return

        for project_dir in sorted(projects):
            checkpoint = project_dir / "checkpoint"
            metadata_file = project_dir / "metadata.json"

            status = "✅ Trained" if checkpoint.exists() else "⏳ No checkpoint"

            print(f"   • {project_dir.name}: {status}")

            if metadata_file.exists():
                try:
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    print(f"     Model: {metadata.get('model_size', 'unknown')}")
                    print(f"     Epochs: {metadata.get('epochs', 'unknown')}")
                    print(f"     Samples: {metadata.get('num_samples', 'unknown')}")
                except Exception:
                    pass
            print()

    def system_info(self):
        """Display system information"""
        info = self.model_manager.get_system_info()

        print("\n🖥️  System Information:\n")
        print(f"   Device: {info['device']}")
        print(f"   Precision: {info['precision']}")
        print(f"   CPU Usage: {info['cpu_percent']:.1f}%")
        print(f"   Memory Usage: {info['memory_percent']:.1f}%")
        print(f"   GPU Available: {info['gpu_available']}")

        if 'gpu_memory_used' in info:
            print(f"   GPU Memory: {info['gpu_memory_used']:.0f}MB / {info['gpu_memory_total']:.0f}MB")
            print(f"   GPU Utilization: {info['gpu_utilization']:.1f}%")

        print("\n   Hardware Profiles:")
        for profile, settings in info['hardware_profiles'].items():
            status = "✅" if settings['available'] else "❌"
            print(f"   {status} {profile}: {settings.get('device', 'N/A')}")

        if info.get('warnings'):
            print("\n   ⚠️  Warnings:")
            for warning in info['warnings']:
                print(f"      - {warning}")

        print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Make Your Own LLM - CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train a model
  python cli.py train my-bot data/generated/text_completions.txt --model-size toy --epochs 3

  # Chat with a trained model
  python cli.py chat my-bot --model-size toy

  # Export a model
  python cli.py export my-bot --formats hf,safetensors

  # List all projects
  python cli.py list

  # Show system info
  python cli.py info
        """
    )

    parser.add_argument(
        '--workspace',
        type=str,
        default='data',
        help='Workspace directory (default: data)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Train command
    train_parser = subparsers.add_parser('train', help='Train a new model')
    train_parser.add_argument('project', help='Project name/slug')
    train_parser.add_argument('data', help='Path to training data file')
    train_parser.add_argument('--model-size', default='toy', choices=['toy', 'base', 'plus', '1b'])
    train_parser.add_argument('--epochs', type=int, default=3)
    train_parser.add_argument('--learning-rate', type=float, default=5e-5)
    train_parser.add_argument('--hardware-profile', choices=['auto', 'apple_silicon', 'windows_nvidia', 'cpu'])

    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Chat with a trained model')
    chat_parser.add_argument('project', help='Project name/slug')
    chat_parser.add_argument('--model-size', default='toy', choices=['toy', 'base', 'plus', '1b'])
    chat_parser.add_argument('--max-length', type=int, default=100)
    chat_parser.add_argument('--temperature', type=float, default=0.7)
    chat_parser.add_argument('--no-interactive', action='store_true', help='Single prompt mode')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export trained model')
    export_parser.add_argument('project', help='Project name/slug')
    export_parser.add_argument('--model-size', default='toy', choices=['toy', 'base', 'plus', '1b'])
    export_parser.add_argument('--output-dir', help='Output directory for exports')
    export_parser.add_argument('--formats', default='hf', help='Export formats (comma-separated: hf,onnx,safetensors)')

    # List command
    subparsers.add_parser('list', help='List all projects')

    # Info command
    subparsers.add_parser('info', help='Show system information')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    cli = LLMCLI(workspace_dir=args.workspace)

    # Execute command
    try:
        if args.command == 'train':
            cli.train(
                project=args.project,
                data_path=args.data,
                model_size=args.model_size,
                epochs=args.epochs,
                learning_rate=args.learning_rate,
                hardware_profile=args.hardware_profile
            )
        elif args.command == 'chat':
            cli.chat(
                project=args.project,
                model_size=args.model_size,
                max_length=args.max_length,
                temperature=args.temperature,
                interactive=not args.no_interactive
            )
        elif args.command == 'export':
            cli.export(
                project=args.project,
                model_size=args.model_size,
                output_dir=args.output_dir,
                formats=args.formats
            )
        elif args.command == 'list':
            cli.list_projects()
        elif args.command == 'info':
            cli.system_info()

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
