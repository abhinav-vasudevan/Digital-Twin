
"""
Fine-tuning Script for NutritionVerse on 460 Diet PDFs

This script:
1. Extracts training data from 460 PDFs
2. Formats data for instruction fine-tuning
3. Fine-tunes using LoRA (efficient parameter tuning)
4. Saves the model for production use

Usage:
    python train_nutrition_model.py --base_model fortymiles/Llama-3-8B-sft-lora-food-nutrition-10-epoch --output_dir ./models/nutrition-finetuned
"""

import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NutritionTrainingDataGenerator:
    """Generate training data from 460 diet PDFs"""
    
    def __init__(self, index_path: str = "outputs/pdf_index.json"):
        self.index_path = Path(index_path)
        self.index = None
        self.load_index()
    
    def load_index(self):
        """Load PDF index"""
        with open(self.index_path, 'r', encoding='utf-8') as f:
            self.index = json.load(f)
        logger.info(f"Loaded {self.index['metadata']['total_plans']} plans")
    
    def generate_training_examples(self) -> List[Dict[str, str]]:
        """
        Generate instruction-following examples from PDFs
        
        Format:
        {
            "instruction": "Create a diet plan for...",
            "input": "User profile: ...",
            "output": "Diet plan: ..."
        }
        """
        try:
            import sys
            from pathlib import Path
            # Add parent directory to path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from service.pdf_parser import CompletePDFParser
        except ImportError:
            try:
                from pdf_parser import CompletePDFParser
            except ImportError:
                # Last resort: direct import from service
                import sys
                from pathlib import Path
                service_dir = Path(__file__).parent.parent
                sys.path.insert(0, str(service_dir))
                from pdf_parser import CompletePDFParser
        
        parser = CompletePDFParser()
        examples = []
        
        for idx, plan in enumerate(self.index['plans'], 1):
            logger.info(f"Processing plan {idx}/{len(self.index['plans'])}: {plan.get('title', 'Unknown')}")
            
            pdf_path = plan.get('file_path')
            if not pdf_path:
                continue
            
            # Make path absolute
            if not Path(pdf_path).is_absolute():
                pdf_path = Path(__file__).parent.parent.parent / pdf_path
            
            if not Path(pdf_path).exists():
                logger.warning(f"PDF not found: {pdf_path}")
                continue
            
            # Parse PDF
            result = parser.parse_complete_pdf(str(pdf_path))
            if 'error' in result:
                logger.warning(f"Error parsing: {result['error']}")
                continue
            
            # Create training examples from this PDF
            plan_examples = self._create_examples_from_plan(plan, result)
            examples.extend(plan_examples)
            
            logger.info(f"Generated {len(plan_examples)} examples from this plan")
        
        logger.info(f"Total training examples: {len(examples)}")
        return examples
    
    def _create_examples_from_plan(
        self,
        plan_metadata: Dict[str, Any],
        parsed_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Create multiple training examples from one PDF"""
        examples = []
        
        # Extract plan details
        gender = plan_metadata.get('gender', 'unknown')
        diet_type = plan_metadata.get('diet_type', 'unknown')
        region = plan_metadata.get('region', 'unknown')
        category = plan_metadata.get('category', 'unknown')
        bmi_category = plan_metadata.get('bmi_category', 'unknown')
        activity = plan_metadata.get('activity', 'unknown')
        
        meals = parsed_data.get('meals', [])
        
        if not meals:
            return examples
        
        # Example 1: Full day plan generation
        instruction = "Create a complete daily diet plan for an Indian individual based on their profile and goals."
        
        user_input = f"""User Profile:
- Gender: {gender}
- Diet Type: {diet_type}
- Region: {region}
- BMI Category: {bmi_category}
- Activity Level: {activity}
- Goal: {category}

Create a detailed daily meal plan with all meals from morning to dinner."""
        
        # Format output
        output_lines = [f"Diet Plan for {category} ({gender}, {diet_type}):", ""]
        
        for meal in meals:
            meal_type = meal.get('meal_type', 'Unknown')
            time = meal.get('time', '')
            options = meal.get('options', [])
            
            output_lines.append(f"{meal_type} ({time}):")
            
            for opt in options[:2]:  # Limit to 2 options
                name = opt.get('name', 'Unknown')
                ingredients = opt.get('ingredients', '')
                nutrition = opt.get('nutrition', {})
                
                output_lines.append(f"  • {name}")
                if ingredients:
                    output_lines.append(f"    Ingredients: {ingredients}")
                if nutrition:
                    nutr_parts = [f"{k}: {v}" for k, v in nutrition.items()]
                    output_lines.append(f"    Nutrition: {', '.join(nutr_parts[:3])}")
            
            output_lines.append("")
        
        examples.append({
            "instruction": instruction,
            "input": user_input,
            "output": "\n".join(output_lines)
        })
        
        # Example 2: Meal-specific recommendations (create 2-3 from each PDF)
        meal_types = ['breakfast', 'lunch', 'dinner']
        for meal_type_query in meal_types:
            matching_meals = [m for m in meals if meal_type_query.lower() in m.get('meal_type', '').lower()]
            
            if matching_meals:
                meal = random.choice(matching_meals)
                
                instruction = f"Recommend a healthy {meal_type_query} for an Indian diet plan."
                user_input = f"""User Profile:
- Diet Type: {diet_type}
- Region: {region}
- Goal: {category}

Recommend a nutritious {meal_type_query} option."""
                
                options = meal.get('options', [])[:2]
                output_lines = [f"{meal_type_query.capitalize()} Recommendations:", ""]
                
                for opt in options:
                    name = opt.get('name', 'Unknown')
                    ingredients = opt.get('ingredients', '')
                    nutrition = opt.get('nutrition', {})
                    
                    output_lines.append(f"Option: {name}")
                    if ingredients:
                        output_lines.append(f"Ingredients: {ingredients}")
                    if nutrition:
                        output_lines.append(f"Nutrition: {json.dumps(nutrition, indent=2)}")
                    output_lines.append("")
                
                examples.append({
                    "instruction": instruction,
                    "input": user_input,
                    "output": "\n".join(output_lines)
                })
        
        return examples
    
    def save_training_data(self, examples: List[Dict[str, str]], output_path: str):
        """Save training data in JSONL format"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(examples)} training examples to {output_file}")


def train_with_ollama(training_file: str, base_model: str, model_name: str):
    """
    Fine-tune using Ollama's create model feature
    
    Note: Ollama doesn't support traditional fine-tuning, but you can:
    1. Create a Modelfile with system prompts and context
    2. Use external tools like llama.cpp for fine-tuning
    """
    logger.info("Ollama fine-tuning setup:")
    logger.info("1. For Ollama, create a Modelfile with your context")
    logger.info("2. Or use external fine-tuning with llama.cpp/Axolotl")
    logger.info(f"Training data ready at: {training_file}")
    
    # Create a sample Modelfile
    modelfile_content = f"""FROM {base_model}

# System prompt with nutrition context
SYSTEM You are an expert nutritionist specializing in Indian diets and meal planning. You have extensive knowledge of traditional Indian foods, regional cuisines, and dietary patterns. You create personalized diet plans based on individual profiles including their age, gender, BMI, activity level, dietary preferences (vegetarian/non-vegetarian), regional cuisine preferences, and health goals (weight loss, weight gain, muscle building, disease management, etc.). 

Your recommendations always:
- Use authentic Indian meals and ingredients
- Consider regional food availability and preferences (North Indian, South Indian, etc.)
- Respect dietary restrictions (pure veg, vegan, non-veg)
- Provide detailed meal timing and portion guidance
- Include nutritional information when relevant
- Align with the user's specific health and fitness goals

# Training context
SYSTEM Training data: 1777 Indian diet plans covering various goals, regions, and preferences.

PARAMETER temperature 0.7
PARAMETER top_p 0.9
"""
    
    modelfile_path = Path(training_file).parent / "Modelfile"
    with open(modelfile_path, 'w', encoding='utf-8') as f:
        f.write(modelfile_content)
    
    logger.info(f"Created Modelfile at: {modelfile_path}")
    logger.info(f"\nTo create your custom model, run:")
    logger.info(f"  ollama create {model_name} -f {modelfile_path}")


def train_with_huggingface(
    training_file: str,
    base_model: str,
    output_dir: str,
    epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 2e-4
):
    """
    Fine-tune using Hugging Face with LoRA
    
    Requires: transformers, peft, datasets, accelerate, bitsandbytes
    """
    try:
        # Disable TensorFlow to avoid Keras 3 conflict
        import os
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
        os.environ['USE_TF'] = 'NO'
        
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            TrainingArguments,
            Trainer,
            DataCollatorForLanguageModeling,
            BitsAndBytesConfig
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from datasets import load_dataset
        import torch
        
        logger.info("Starting Hugging Face fine-tuning with LoRA...")
        
        # Quantization config
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
            bnb_8bit_compute_dtype=torch.float16
        )
        
        # Load model and tokenizer
        logger.info(f"Loading base model: {base_model}")
        try:
            tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
        except KeyError:
            # Fallback for tokenizer with missing 'added_tokens'
            tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=False, trust_remote_code=True)
        
        # Set pad token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        
        # Prepare for training
        model = prepare_model_for_kbit_training(model)
        
        # LoRA configuration
        lora_config = LoraConfig(
            r=8,  # Rank
            lora_alpha=16,
            target_modules=["q_proj", "v_proj"],  # Which layers to fine-tune
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
        
        # Load dataset
        logger.info(f"Loading training data from: {training_file}")
        dataset = load_dataset('json', data_files=training_file)
        
        # Tokenize
        def tokenize_function(examples):
            # Format: instruction + input -> output
            texts = []
            for i in range(len(examples['instruction'])):
                text = f"### Instruction:\n{examples['instruction'][i]}\n\n### Input:\n{examples['input'][i]}\n\n### Response:\n{examples['output'][i]}"
                texts.append(text)
            
            return tokenizer(texts, truncation=True, max_length=2048, padding='max_length')
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=dataset['train'].column_names)
        
        # Training arguments - Optimized for A100 GPU
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=2,  # Reduced for A100 (more VRAM)
            learning_rate=learning_rate,
            fp16=False,  # Use bf16 for A100
            bf16=True,  # Better for A100 Ampere architecture
            save_strategy="epoch",  # Save after each epoch
            eval_strategy="epoch",  # Evaluate each epoch (renamed from evaluation_strategy)
            logging_steps=10,
            save_total_limit=3,  # Keep best 3 checkpoints
            load_best_model_at_end=True,  # Load best model after training
            metric_for_best_model="loss",  # Use loss to determine best model
            greater_is_better=False,  # Lower loss is better
            push_to_hub=False,
            report_to="none",  # Disable wandb/tensorboard
            # Early stopping via callback (defined below)
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
        
        # Early stopping callback - stop if no improvement for 7 epochs
        from transformers import EarlyStoppingCallback
        early_stopping = EarlyStoppingCallback(
            early_stopping_patience=7,  # Stop after 7 epochs with no improvement
            early_stopping_threshold=0.0  # Any improvement counts
        )
        
        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset['train'],
            eval_dataset=tokenized_dataset['train'],  # Use train as eval (no separate validation set)
            data_collator=data_collator,
            callbacks=[early_stopping]
        )
        
        # Train
        logger.info("Starting training on A100 GPU...")
        logger.info("Early stopping enabled: will stop if no improvement for 7 epochs")
        trainer.train()
        
        # Save best model (already loaded due to load_best_model_at_end=True)
        logger.info(f"Saving best model to: {output_dir}")
        trainer.save_model(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        # Save training metrics
        import json
        metrics_path = Path(output_dir) / "training_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(trainer.state.log_history, f, indent=2)
        logger.info(f"Training metrics saved to: {metrics_path}")
        
        logger.info("Fine-tuning completed successfully!")
        
    except ImportError as e:
        logger.error(f"Missing dependencies: {e}")
        logger.error("Install with: pip install transformers peft datasets accelerate bitsandbytes")
    except Exception as e:
        logger.error(f"Error during training: {e}", exc_info=True)


def main(
    base_model="microsoft/phi-2",  # 2.7B params - fast, reliable, instruction-tuned
    output_dir="./models/nutrition-finetuned",
    training_file="./training_data.jsonl",
    method="huggingface",
    epochs=8,
    batch_size=32,
    skip_data_gen=True
):
    """
    Main training function - can be called directly or via command line
    
    Args:
        base_model: HuggingFace model name
        output_dir: Output directory for fine-tuned model
        training_file: Path to training data JSONL file
        method: Training method ('ollama' or 'huggingface')
        epochs: Number of training epochs
        batch_size: Batch size for training
        skip_data_gen: Skip data generation step
    """
    # Create args object for compatibility
    class Args:
        pass
    
    args = Args()
    args.base_model = base_model
    args.output_dir = output_dir
    args.training_file = training_file
    args.method = method
    args.epochs = epochs
    args.batch_size = batch_size
    args.skip_data_gen = skip_data_gen
    
    # Step 1: Generate training data
    if not args.skip_data_gen:
        logger.info("=" * 60)
        logger.info("STEP 1: Generating Training Data from 460 PDFs")
        logger.info("=" * 60)
        
        generator = NutritionTrainingDataGenerator()
        examples = generator.generate_training_examples()
        generator.save_training_data(examples, args.training_file)
    else:
        logger.info("Skipping data generation (using existing file)")
    
    # Step 2: Fine-tune
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Fine-tuning Model")
    logger.info("=" * 60)
    
    if args.method == 'ollama':
        train_with_ollama(args.training_file, args.base_model, "nutrition-expert")
    else:
        train_with_huggingface(
            args.training_file,
            args.base_model,
            args.output_dir,
            args.epochs,
            args.batch_size
        )
    
    logger.info("\n" + "=" * 60)
    logger.info("TRAINING COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"Training data: {args.training_file}")
    logger.info(f"Model output: {args.output_dir}")


if __name__ == "__main__":
    # Command line mode with argparse
    import sys
    
    # Filter out Jupyter/Colab kernel arguments
    clean_args = [arg for arg in sys.argv if not arg.endswith('.json') and not arg.startswith('-f')]
    
    if len(clean_args) > 1:
        # Command line with arguments
        parser = argparse.ArgumentParser(description="Fine-tune nutrition model on diet PDFs")
        parser.add_argument("--base_model", default="fortymiles/Llama-3-8B-sft-lora-food-nutrition-10-epoch", help="Base model name (HuggingFace)")
        parser.add_argument("--output_dir", default="./models/nutrition-finetuned", help="Output directory")
        parser.add_argument("--training_file", default="./training_data.jsonl", help="Training data file")
        parser.add_argument("--method", choices=['ollama', 'huggingface'], default='huggingface', help="Training method")
        parser.add_argument("--epochs", type=int, default=20, help="Number of epochs")
        parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
        parser.add_argument("--skip_data_gen", action='store_true', help="Skip data generation")
        
        parsed_args = parser.parse_args(clean_args[1:])
        main(
            base_model=parsed_args.base_model,
            output_dir=parsed_args.output_dir,
            training_file=parsed_args.training_file,
            method=parsed_args.method,
            epochs=parsed_args.epochs,
            batch_size=parsed_args.batch_size,
            skip_data_gen=parsed_args.skip_data_gen
        )
    else:
        # Notebook/direct call mode - use defaults
        main()
