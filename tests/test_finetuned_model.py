"""
Test script for fine-tuned Phi-2 nutrition model

Tests the model with various diet plan scenarios to verify quality
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_finetuned_model(checkpoint_path: str):
    """Load fine-tuned LoRA model"""
    logger.info(f"Loading fine-tuned model from: {checkpoint_path}")
    
    # Load base model
    base_model = "microsoft/phi-2"
    
    logger.info("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    logger.info("Loading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    
    logger.info("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(model, checkpoint_path)
    model.eval()
    
    logger.info("✅ Model loaded successfully!")
    return model, tokenizer


def generate_diet_plan(model, tokenizer, instruction: str, user_input: str, max_length: int = 1024):
    """Generate diet plan using the fine-tuned model"""
    
    # Format prompt (same as training)
    prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{user_input}\n\n### Response:\n"
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    
    # Decode
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the response part
    if "### Response:" in response:
        response = response.split("### Response:")[-1].strip()
    
    return response


def test_model():
    """Test model with various scenarios"""
    
    checkpoint_path = r"D:\Documents\Diet plan\Diet model phi - 2\checkpoint-224"
    
    print("\n" + "="*80)
    print("LOADING FINE-TUNED PHI-2 NUTRITION MODEL")
    print("="*80 + "\n")
    
    model, tokenizer = load_finetuned_model(checkpoint_path)
    
    # Test cases
    test_cases = [
        {
            "name": "Weight Loss - Vegetarian - North Indian",
            "instruction": "Create a complete daily diet plan for an Indian individual based on their profile and goals.",
            "input": """User Profile:
- Gender: Female
- Diet Type: Pure Veg
- Region: North Indian
- BMI Category: Overweight
- Activity Level: Moderate
- Goal: Weight Loss

Create a detailed daily meal plan with all meals from morning to dinner."""
        },
        {
            "name": "Muscle Gain - Non-Veg - South Indian",
            "instruction": "Create a complete daily diet plan for an Indian individual based on their profile and goals.",
            "input": """User Profile:
- Gender: Male
- Diet Type: Non-Veg
- Region: South Indian
- BMI Category: Normal
- Activity Level: Very Active
- Goal: Muscle Building

Create a detailed daily meal plan with all meals from morning to dinner."""
        },
        {
            "name": "PCOS Management - Vegetarian",
            "instruction": "Create a complete daily diet plan for an Indian individual based on their profile and goals.",
            "input": """User Profile:
- Gender: Female
- Diet Type: Pure Veg
- Region: North Indian
- BMI Category: Normal
- Activity Level: Light
- Goal: PCOS Management

Create a detailed daily meal plan with all meals from morning to dinner."""
        },
        {
            "name": "Breakfast Recommendation",
            "instruction": "Recommend a healthy breakfast for an Indian diet plan.",
            "input": """User Profile:
- Diet Type: Pure Veg
- Region: South Indian
- Goal: Weight Loss

Recommend a nutritious breakfast option."""
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print("\n" + "="*80)
        print(f"TEST CASE {i}: {test_case['name']}")
        print("="*80 + "\n")
        
        print("📋 USER QUERY:")
        print(test_case['input'])
        print("\n" + "-"*80 + "\n")
        
        print("🤖 MODEL RESPONSE:")
        response = generate_diet_plan(
            model, 
            tokenizer, 
            test_case['instruction'], 
            test_case['input'],
            max_length=800
        )
        print(response)
        print("\n")
    
    print("="*80)
    print("✅ ALL TESTS COMPLETED!")
    print("="*80)


if __name__ == "__main__":
    test_model()
