"""
Training Data Generator for Custom LLM

Generates synthetic conversational data for training language models.
Supports multiple formats: JSONL, TXT, CSV
"""

import json
import random
import argparse
from pathlib import Path
from typing import List, Dict


class TrainingDataGenerator:
    """Generate synthetic training data for conversational AI"""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.conversation_templates = self._load_templates()

    def _load_templates(self) -> Dict[str, List[str]]:
        """Load conversation templates by category"""
        return {
            "greetings": [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Good day! How may I assist you?",
                "Hey! What's on your mind?",
                "Welcome! How can I be of service?"
            ],
            "questions": [
                "What is the capital of France?",
                "How does photosynthesis work?",
                "Can you explain quantum computing?",
                "What's the difference between AI and ML?",
                "How do I learn programming?",
                "What are the benefits of exercise?",
                "Why is the sky blue?",
                "How does the internet work?",
                "What is climate change?",
                "Can you recommend a good book?"
            ],
            "responses": [
                "The capital of France is Paris, a beautiful city known for art, culture, and the Eiffel Tower.",
                "Photosynthesis is the process where plants convert sunlight, water, and CO2 into glucose and oxygen.",
                "Quantum computing uses quantum bits (qubits) that can exist in multiple states simultaneously, enabling parallel processing.",
                "AI is the broader field of creating intelligent machines, while ML is a subset focused on learning from data.",
                "To learn programming, start with Python or JavaScript, practice daily, build projects, and use resources like freeCodeCamp.",
                "Exercise improves cardiovascular health, strengthens muscles, boosts mood, and enhances cognitive function.",
                "The sky appears blue because molecules in the atmosphere scatter shorter wavelengths of light (blue) more than longer wavelengths.",
                "The internet is a global network of computers that communicate using standardized protocols like TCP/IP.",
                "Climate change refers to long-term shifts in temperatures and weather patterns, primarily caused by human activities.",
                "I'd recommend 'Sapiens' by Yuval Noah Harari for thought-provoking insights into human history and evolution."
            ],
            "instructions": [
                "Write a poem about the ocean",
                "Summarize the benefits of meditation",
                "Create a to-do list for starting a business",
                "Explain recursion like I'm five",
                "Give me tips for better sleep",
                "Describe the process of making coffee",
                "List the planets in our solar system",
                "Tell me about the history of computers",
                "Provide a recipe for chocolate chip cookies",
                "Suggest ways to reduce stress"
            ],
            "stories": [
                "Once upon a time, in a land far away, there lived a curious fox who loved to explore.",
                "The ancient tree stood tall in the forest, its branches reaching toward the sky like outstretched arms.",
                "In the depths of the ocean, a young dolphin discovered a mysterious underwater cave.",
                "The old lighthouse keeper had seen many storms, but none quite like the one approaching tonight.",
                "A small seed fell from a tree and landed in the most unexpected place - a crack in the sidewalk."
            ]
        }

    def generate_conversation(self, num_turns: int = 3) -> List[Dict[str, str]]:
        """Generate a multi-turn conversation"""
        conversation = []

        # Start with greeting
        conversation.append({
            "role": "user",
            "content": random.choice(self.conversation_templates["greetings"])
        })

        for turn in range(num_turns):
            # Alternate between questions and responses
            if turn % 2 == 0:
                user_msg = random.choice(
                    self.conversation_templates["questions"] +
                    self.conversation_templates["instructions"]
                )
                conversation.append({"role": "user", "content": user_msg})
            else:
                assistant_msg = random.choice(self.conversation_templates["responses"])
                conversation.append({"role": "assistant", "content": assistant_msg})

        return conversation

    def generate_qa_pairs(self, num_pairs: int = 100) -> List[Dict[str, str]]:
        """Generate question-answer pairs"""
        pairs = []

        questions = self.conversation_templates["questions"]
        responses = self.conversation_templates["responses"]

        for i in range(num_pairs):
            q_idx = i % len(questions)
            r_idx = i % len(responses)

            pairs.append({
                "question": questions[q_idx],
                "answer": responses[r_idx],
                "id": f"qa_{i:04d}"
            })

        return pairs

    def generate_text_completions(self, num_samples: int = 50) -> List[str]:
        """Generate text completion samples"""
        completions = []

        prompts = [
            "The best way to learn is",
            "In the future, technology will",
            "When faced with challenges, remember to",
            "The key to success is",
            "Nature teaches us that",
            "Innovation comes from",
            "The most important thing in life is",
            "To achieve your goals, you must",
            "Science shows us that",
            "History has taught us"
        ]

        endings = [
            " practice consistently and never give up on your dreams.",
            " transform how we live, work, and communicate with each other.",
            " stay calm, think clearly, and trust in your abilities.",
            " persistence, hard work, and a willingness to learn from failures.",
            " patience and adaptation are essential for survival and growth.",
            " combining creativity with knowledge and taking calculated risks.",
            " building meaningful relationships and contributing to others.",
            " set clear objectives, stay focused, and take consistent action.",
            " curiosity and experimentation lead to groundbreaking discoveries.",
            " those who ignore the past are doomed to repeat its mistakes."
        ]

        for i in range(num_samples):
            prompt = random.choice(prompts)
            ending = random.choice(endings)
            completions.append(f"{prompt}{ending}")

        return completions

    def save_as_jsonl(self, data: List[Dict], output_path: Path):
        """Save data in JSONL format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"✅ Saved {len(data)} items to {output_path}")

    def save_as_txt(self, data: List[str], output_path: Path):
        """Save data in plain text format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(data))
        print(f"✅ Saved {len(data)} items to {output_path}")

    def save_as_csv(self, data: List[Dict], output_path: Path):
        """Save data in CSV format"""
        if not data:
            return

        import csv

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Saved {len(data)} items to {output_path}")

    def generate_all(self, output_dir: Path, num_samples: int = 100):
        """Generate all types of training data"""
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n🔥 Generating training data in {output_dir}...\n")

        # Generate Q&A pairs (JSONL)
        qa_pairs = self.generate_qa_pairs(num_samples)
        self.save_as_jsonl(qa_pairs, output_dir / "qa_pairs.jsonl")

        # Generate text completions (TXT)
        completions = self.generate_text_completions(num_samples)
        self.save_as_txt(completions, output_dir / "text_completions.txt")

        # Generate conversations (JSONL)
        conversations = []
        for i in range(num_samples // 2):
            conv = self.generate_conversation(num_turns=random.randint(2, 5))
            conversations.append({
                "id": f"conv_{i:04d}",
                "messages": conv
            })
        self.save_as_jsonl(conversations, output_dir / "conversations.jsonl")

        # Generate CSV format data
        csv_data = []
        for i in range(num_samples):
            csv_data.append({
                "text": random.choice(completions),
                "category": random.choice(["educational", "conversational", "informative"]),
                "length": random.randint(50, 200)
            })
        self.save_as_csv(csv_data, output_dir / "training_data.csv")

        print(f"\n✨ Generated {num_samples * 3} total training samples!")
        print(f"📁 Output directory: {output_dir.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic training data for LLM fine-tuning"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/generated",
        help="Output directory for generated data (default: data/generated)"
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=100,
        help="Number of samples to generate per format (default: 100)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )

    args = parser.parse_args()

    output_path = Path(args.output_dir)
    generator = TrainingDataGenerator(seed=args.seed)
    generator.generate_all(output_path, num_samples=args.num_samples)


if __name__ == "__main__":
    main()
