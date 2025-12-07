# Google Colab Fine-tuning Guide

## Files to Upload to Google Drive

Upload **ONLY** this file to your Google Drive folder `/MyDrive/dd/`:

1. **`outputs/training_data.jsonl`** (1777 examples, ~5MB)

**No need to upload the Python script** - you'll paste it directly into Colab.

## Google Colab Notebook Setup

### Step 1: Create New Colab Notebook
Go to: https://colab.research.google.com

### Step 2: Enable GPU
- Click **Runtime** → **Change runtime type**
- Select **A100 GPU** (Colab Pro required)
- Click **Save**

### Step 3: Run These Cells

#### Cell 1: Mount Google Drive & Install Dependencies
```python
from google.colab import drive
drive.mount('/content/drive')

!pip install -q transformers peft datasets accelerate bitsandbytes sentencepiece protobuf
```

#### Cell 2: Login to HuggingFace
```python
from huggingface_hub import login
login()  # Paste your HuggingFace token when prompted
```

#### Cell 3: Paste Training Script Directly
**Copy the entire content of `train_nutrition_model.py` and paste it into a Colab cell.**
The script is at: `D:\Documents\Diet plan\service\recommender_ml\train_nutrition_model.py`

Or download it from here: [Direct link to script - copy all 449 lines]

#### Cell 4: Copy Training Data from Drive to Colab
```python
import shutil
import os

# Copy training data from Drive to Colab's fast local storage
shutil.copy('/content/drive/MyDrive/dd/training_data.jsonl', './training_data.jsonl')
print("✅ Training data copied to Colab")
```

#### Cell 5: Run Training (A100 Optimized - saves to Drive)
```python
# Train on Colab's fast local storage, save checkpoints to Drive
!python train_nutrition_model.py \
  --base_model fortymiles/Llama-3-8B-sft-lora-food-nutrition-10-epoch \
  --epochs 20 \
  --batch_size 8 \
  --training_file ./training_data.jsonl \
  --output_dir /content/drive/MyDrive/dd/models/nutrition-finetuned \
  --skip_data_gen
```

**What happens automatically:**
- ✅ Trains on Colab's **fast local SSD** (much faster than Drive)
- ✅ Saves checkpoint after **every epoch** to Google Drive (persistent)
- ✅ Keeps **best 3 models** based on lowest loss
- ✅ **Early stopping**: exits if no improvement for 7 consecutive epochs
- ✅ Loads and saves **best model** at end
- ✅ Saves **training metrics** (loss history) as JSON
- ✅ Uses **bf16** (optimal for A100 Ampere GPU)
- ✅ Batch size 8 (A100 has 40GB VRAM)

#### Cell 6: Monitor Training Progress
```python
# Check saved checkpoints in Drive
!ls -lh /content/drive/MyDrive/dd/models/nutrition-finetuned/

# View training metrics
!cat /content/drive/MyDrive/dd/models/nutrition-finetuned/training_metrics.json | head -50
```

### Step 4: Model Already Saved to Google Drive!

**No download needed!** All checkpoints and the best model are automatically saved to:
```
/content/drive/MyDrive/dd/models/nutrition-finetuned/
```

The folder contains:
- `adapter_config.json` - LoRA configuration
- `adapter_model.safetensors` - Fine-tuned weights
- `training_metrics.json` - Loss history and metrics
- `checkpoint-X/` - Intermediate checkpoints (best 3 kept)

#### Optional: Download to Local Computer
```python
# Only if you want a local copy
!zip -r nutrition-finetuned.zip /content/drive/MyDrive/dd/models/nutrition-finetuned
from google.colab import files
files.download('./nutrition-finetuned.zip')
```

## Expected Training Time (A100 GPU)

- **1 epoch**: ~8-12 minutes (A100)
- **10 epochs**: ~80-120 minutes (A100)
- **Early stopping**: Exits automatically after 7 epochs with no improvement
- **Colab Pro limit**: 24 hours/session (enough for full training)

## After Training

### Option 1: Use from Google Drive
Update `ml_recommender.py` to load from Drive path:
```python
recommender = MLRecommender(
    model_name="/content/drive/MyDrive/dd/models/nutrition-finetuned"
)
```

### Option 2: Download and Use Locally
1. Download `nutrition-finetuned.zip` from Colab
2. Extract to `D:\Documents\Diet plan\models\nutrition-finetuned`
3. Update `ml_recommender.py`:
```python
recommender = MLRecommender(
    model_name="./models/nutrition-finetuned"
)
```

## Troubleshooting

### "Out of Memory" Error
A100 has 40GB VRAM, but if issues occur, reduce batch size:
```python
!python train_nutrition_model.py \
  --batch_size 4 \
  --epochs 1 \
  --skip_data_gen
```

### Check GPU Type
```python
!nvidia-smi
# Should show: Tesla A100-SXM4-40GB
```

### "Session Disconnected"
Colab times out after ~12 hours. For longer training:
1. Use **Colab Pro** ($10/month, 24h sessions)
2. Or run in multiple sessions (model saves checkpoints)

### "Token Not Valid"
Get new token from: https://huggingface.co/settings/tokens
- Must have **Write** access
- Must have accepted Llama-3 license

## Complete Colab Notebook (Copy-Paste Ready)

### Cell 1: Setup
```python
# Mount Drive and Install
from google.colab import drive
drive.mount('/content/drive')

!pip install -q transformers peft datasets accelerate bitsanybytes sentencepiece protobuf

from huggingface_hub import login
login()  # Paste your HF token
```

### Cell 2: Copy Training Data
```python
import shutil
shutil.copy('/content/drive/MyDrive/dd/training_data.jsonl', './training_data.jsonl')
print("✅ Training data copied to Colab local storage")
```

### Cell 3: Paste Full Training Script
```python
# PASTE THE ENTIRE train_nutrition_model.py CONTENT HERE
# Then run this cell to save it
%%writefile train_nutrition_model.py

# [PASTE ALL 449 LINES FROM train_nutrition_model.py HERE]
```

### Cell 4: Run Training
```python
# Train on Colab's fast local storage, save checkpoints to Drive
!python train_nutrition_model.py \
  --base_model fortymiles/Llama-3-8B-sft-lora-food-nutrition-10-epoch \
  --epochs 20 \
  --batch_size 8 \
  --training_file ./training_data.jsonl \
  --output_dir /content/drive/MyDrive/dd/models/nutrition-finetuned \
  --skip_data_gen

# Training automatically:
# ✓ Trains on fast Colab SSD
# ✓ Saves checkpoints to Drive after each epoch
# ✓ Keeps best 3 models
# ✓ Stops early if no improvement for 7 epochs
# ✓ Final model saved to Drive
```

### Cell 5: Check Results
```python
!ls -lh /content/drive/MyDrive/dd/models/nutrition-finetuned/
!cat /content/drive/MyDrive/dd/models/nutrition-finetuned/training_metrics.json
```

## Alternative: Use Pre-trained fortymiles Model (No Fine-tuning)

The fortymiles model is already trained on food/nutrition. You can use it directly without additional training:

```python
from service.recommender_ml import MLRecommender

recommender = MLRecommender(
    model_name="fortymiles/Llama-3-8B-sft-lora-food-nutrition-10-epoch"
)

result = recommender.recommend({
    "gender": "female",
    "age": 28,
    "bmi_category": "overweight",
    "diet_type": "vegetarian",
    "region": "south_indian",
    "goal": "weight_loss"
})
```

This will download and use the model directly from HuggingFace (one-time ~8GB download).

