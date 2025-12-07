"""
Download microsoft/phi-2 base model to local cache

Run this before starting the server to avoid download delays
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

print("=" * 80)
print("DOWNLOADING MICROSOFT PHI-2 BASE MODEL")
print("=" * 80)
print("\nThis is a one-time download (~5.5GB)")
print("The model will be cached for future use\n")

model_name = "microsoft/phi-2"

print("Step 1/2: Downloading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
print("✅ Tokenizer downloaded successfully!")

print("\nStep 2/2: Downloading base model (this may take 10-20 minutes)...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="cpu",  # Use CPU to avoid GPU memory issues
    low_cpu_mem_usage=True,
    trust_remote_code=True
)
print("✅ Model downloaded successfully!")

print("\n" + "=" * 80)
print("DOWNLOAD COMPLETE!")
print("=" * 80)
import os

print("\nThe model is now cached at:")
print(f"C:\\Users\\{os.environ['USERNAME']}\\.cache\\huggingface\\hub\\models--microsoft--phi-2")
print("\nYou can now start the server with:")
print("python -m uvicorn service.api:app --reload --port 8000")
