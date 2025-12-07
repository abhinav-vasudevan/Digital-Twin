# Fine-tuning NutritionVerse-Real on Your 460 Diet PDFs

Complete guide to fine-tune NutritionVerse-Real specifically for Indian diet recommendations.

## Overview

**Base Model**: `AweXiaoXiao/NutritionVerse-Real-7B`  
**Method**: LoRA (Low-Rank Adaptation)  
**Dataset**: Your 460 Indian diet PDFs  
**Output**: Specialized model for Indian nutrition  

## Why Fine-tune?

✅ **Domain Adaptation**: Learn Indian food names, ingredients, regional cuisines  
✅ **Pattern Recognition**: Understand meal structures, timing, portions  
✅ **Better Recommendations**: More accurate and contextually appropriate  
✅ **Your Data**: Model learns from your specific diet plans  

## Prerequisites

### Hardware Requirements

**Minimum** (will be slow):
- GPU: 16 GB VRAM (NVIDIA RTX 4080/4090, A100)
- RAM: 32 GB
- Storage: 50 GB free space

**Recommended**:
- GPU: 24+ GB VRAM (NVIDIA RTX 4090, A100, A6000)
- RAM: 64 GB
- Storage: 100 GB free space
- CUDA 11.8 or 12.x

**Can't use GPU?**
- Use Google Colab (free GPU): https://colab.research.google.com
- Or use cloud services (AWS, Azure, Lambda Labs)

### Software Requirements

```powershell
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install fine-tuning dependencies
pip install transformers peft datasets accelerate bitsandbytes

# Install embeddings for RAG
pip install sentence-transformers numpy faiss-cpu
```

## Step 1: Generate Training Data

```powershell
# Navigate to your project
cd "d:\Documents\Diet plan"

# Generate training examples from 460 PDFs
python service/recommender_ml/train_nutrition_model.py
```

**Output**:
- `outputs/training_data.jsonl` (~1500+ examples)
- Each example: Instruction → Input → Output format
- Covers: Full day plans, meal recommendations, nutrition advice

**Example Training Data**:
```json
{
  "instruction": "Create a complete daily diet plan for an Indian individual based on their profile and goals.",
  "input": "User Profile:\n- Gender: female\n- Diet Type: vegetarian\n- Region: north_indian\n- Goal: weight_loss",
  "output": "Diet Plan for Weight Loss (female, vegetarian):\n\nBreakfast:\n  • Oats Porridge with Almonds\n    Ingredients: Oats 50g, Milk 200ml, Almonds 10\n    Nutrition: Calories: 300, Protein: 12g..."
}
```

## Step 2: Fine-tune the Model

### Option A: Full Fine-tuning (Best Quality)

```powershell
python service/recommender_ml/train_nutrition_model.py \
  --base_model AweXiaoXiao/NutritionVerse-Real-7B \
  --method huggingface \
  --output_dir ./models/nutrition-finetuned \
  --epochs 3 \
  --batch_size 4
```

**Parameters**:
- `--epochs 3`: Train for 3 full passes (3-5 recommended)
- `--batch_size 4`: Process 4 examples at once (adjust for your GPU)
- Gradient accumulation: 4 steps (effective batch size = 16)

**Training Time**:
- RTX 4090: ~4-6 hours
- A100: ~2-3 hours
- CPU: Not recommended (days)

### Option B: Quick Test (for verification)

```powershell
python service/recommender_ml/train_nutrition_model.py \
  --base_model AweXiaoXiao/NutritionVerse-Real-7B \
  --method huggingface \
  --output_dir ./models/nutrition-test \
  --epochs 1 \
  --batch_size 2
```

## Step 3: Monitor Training

Training will show progress:

```
Loading NutritionVerse-Real-7B...
✓ Model loaded successfully!
Tokenizing dataset...
100%|████████████| 1500/1500 [00:30<00:00]

Training:
Epoch 1/3: 100%|████████| 375/375 [01:45:00<00:00]
Loss: 0.85
Epoch 2/3: 100%|████████| 375/375 [01:43:00<00:00]
Loss: 0.62
Epoch 3/3: 100%|████████| 375/375 [01:44:00<00:00]
Loss: 0.48

Saving model to ./models/nutrition-finetuned...
✓ Training completed!
```

**Good Loss Values**:
- Start: 1.5-2.5
- End: 0.4-0.8 (lower is better, but don't overfit)

## Step 4: Use Your Fine-tuned Model

Update `service/recommender_ml/ml_recommender.py`:

```python
recommender = MLRecommender(
    model_name="./models/nutrition-finetuned",  # Your fine-tuned model
    use_local=False
)
```

Or pass it when initializing:

```python
from service.recommender_ml import MLRecommender

recommender = MLRecommender(
    model_name="d:/Documents/Diet plan/models/nutrition-finetuned"
)
```

## Step 5: Test Your Model

```python
from service.recommender_ml import MLRecommender

# Load your fine-tuned model
recommender = MLRecommender(
    model_name="./models/nutrition-finetuned"
)

# Test recommendation
profile = {
    "gender": "female",
    "age": 28,
    "bmi_category": "overweight",
    "activity_level": "moderate",
    "diet_type": "vegetarian",
    "region": "north_indian",
    "goal": "weight_loss"
}

result = recommender.recommend(profile, top_k=3)
print(result)
```

## Optimization Tips

### Reduce Memory Usage

**8-bit Quantization** (half the memory):

Edit `train_nutrition_model.py`, line ~260:

```python
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    load_in_8bit=True,  # Enable 8-bit
    device_map="auto",
    torch_dtype=torch.float16
)
```

**Smaller Batch Size**:
```powershell
python train_nutrition_model.py --batch_size 2
```

### Speed Up Training

**Increase Batch Size** (if you have VRAM):
```powershell
python train_nutrition_model.py --batch_size 8
```

**Mixed Precision** (already enabled):
- Uses float16 for faster computation
- Automatic with `fp16=True`

### Better Quality

**More Epochs**:
```powershell
python train_nutrition_model.py --epochs 5
```

**Lower Learning Rate** (more stable):
```powershell
# Edit train_nutrition_model.py
learning_rate=1e-4  # Default is 2e-4
```

## Using Google Colab (Free GPU)

1. **Upload Files to Google Drive**:
   - Upload `train_nutrition_model.py`
   - Upload `outputs/training_data.jsonl`

2. **Create Colab Notebook**: https://colab.research.google.com

3. **Run in Colab**:

```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Install dependencies
!pip install transformers peft datasets accelerate bitsandbytes

# Navigate to your files
%cd /content/drive/MyDrive/diet-project

# Run training
!python train_nutrition_model.py \
  --base_model AweXiaoXiao/NutritionVerse-Real-7B \
  --epochs 3 \
  --batch_size 4
```

4. **Download Fine-tuned Model**:
   - Model saved in `models/nutrition-finetuned/`
   - Download to your local machine

## Upload to HuggingFace (Optional)

Share your fine-tuned model:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load your model
model = AutoModelForCausalLM.from_pretrained("./models/nutrition-finetuned")
tokenizer = AutoTokenizer.from_pretrained("./models/nutrition-finetuned")

# Login to HuggingFace
from huggingface_hub import login
login()  # Enter your token

# Push to HuggingFace
model.push_to_hub("your-username/nutritionverse-indian-diet")
tokenizer.push_to_hub("your-username/nutritionverse-indian-diet")
```

Then use it:
```python
recommender = MLRecommender(
    model_name="your-username/nutritionverse-indian-diet"
)
```

## Troubleshooting

### "CUDA out of memory"

**Solution 1**: Reduce batch size
```powershell
python train_nutrition_model.py --batch_size 1
```

**Solution 2**: Enable 8-bit quantization (see above)

**Solution 3**: Use gradient checkpointing
```python
# In train_nutrition_model.py
model.gradient_checkpointing_enable()
```

### "Model download failed"

```powershell
# Clear cache
rm -Recurse -Force $env:USERPROFILE\.cache\huggingface

# Set mirror (if in restricted region)
$env:HF_ENDPOINT="https://hf-mirror.com"

# Retry
python train_nutrition_model.py
```

### "Training is slow"

- **Check GPU usage**: Task Manager → Performance → GPU
- **Use GPU**: Ensure PyTorch detects CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
- **Install CUDA version of PyTorch**: See prerequisites

### "Loss not decreasing"

- **Learning rate too high**: Reduce to 1e-4 or 5e-5
- **Not enough epochs**: Train for 5-10 epochs
- **Data quality**: Check training_data.jsonl format

## Advanced: Custom Training Configuration

Edit `train_nutrition_model.py` for advanced control:

```python
training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=epochs,  # 3-5 recommended
    per_device_train_batch_size=batch_size,  # 2-8 depending on GPU
    gradient_accumulation_steps=4,  # Effective batch size multiplier
    learning_rate=2e-4,  # 1e-4 to 5e-4
    fp16=True,  # Use mixed precision
    save_steps=100,  # Save checkpoint every 100 steps
    logging_steps=10,  # Log every 10 steps
    save_total_limit=3,  # Keep only 3 checkpoints
    warmup_steps=100,  # Warmup for stable training
    weight_decay=0.01,  # Regularization
)
```

## LoRA Configuration

Adjust LoRA parameters in `train_nutrition_model.py`:

```python
lora_config = LoraConfig(
    r=8,  # Rank (4-16, higher = more parameters)
    lora_alpha=16,  # Scaling factor (usually 2*r)
    target_modules=["q_proj", "v_proj"],  # Which layers to adapt
    lora_dropout=0.05,  # Dropout for regularization
    bias="none",
    task_type="CAUSAL_LM"
)
```

## Best Practices

1. **Start Small**: Test with 1 epoch first
2. **Monitor Loss**: Should decrease steadily
3. **Save Checkpoints**: Don't lose progress if training crashes
4. **Test Frequently**: Validate on sample profiles
5. **Version Control**: Keep multiple versions (epoch1, epoch3, epoch5)
6. **Document Changes**: Note which config produced best results

## Next Steps

After fine-tuning:

1. ✅ **Test thoroughly** with various user profiles
2. ✅ **Compare** with base model (is fine-tuned better?)
3. ✅ **Collect feedback** from users
4. ✅ **Re-train** periodically with new PDFs or feedback
5. ✅ **Share** your model on HuggingFace (optional)

## Support

- **HuggingFace Forums**: https://discuss.huggingface.co
- **Transformers Docs**: https://huggingface.co/docs/transformers
- **PEFT Docs**: https://huggingface.co/docs/peft

Your fine-tuned NutritionVerse-Real will be a specialized expert in Indian diet recommendations! 🎉
