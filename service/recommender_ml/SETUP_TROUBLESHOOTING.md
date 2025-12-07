# Setup & Troubleshooting - NutritionVerse ML Recommender

## ✅ Fixed Issues

### Import Error Fix
**Problem**: `ModuleNotFoundError: No module named 'service'` or `'pdf_parser'`

**Solution**: Updated `train_nutrition_model.py` to handle path imports correctly. The script now works from any directory.

### TensorFlow/Keras Conflict
**Problem**: `Your currently installed version of Keras is Keras 3, but this is not yet supported in Transformers`

**Solution**: Uninstall TensorFlow since we only need PyTorch for NutritionVerse:
```powershell
pip uninstall tensorflow tensorflow-intel keras -y
```

## Installation Steps

### 1. Install Core Dependencies

```powershell
# For CPU (slower)
pip install transformers torch sentence-transformers numpy faiss-cpu accelerate

# For GPU (recommended, much faster)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers sentence-transformers numpy faiss-cpu accelerate
```

### 2. Install Fine-tuning Tools (if training)

```powershell
pip install peft datasets bitsandbytes
```

### 3. Remove Conflicting Packages

```powershell
# Remove TensorFlow (not needed, causes conflicts)
pip uninstall tensorflow tensorflow-intel keras tf-keras -y
```

## Usage

### Generate Training Data

```powershell
cd "d:\Documents\Diet plan"
python service/recommender_ml/train_nutrition_model.py
```

**What it does**:
- Reads 460 PDFs from `outputs/pdf_index.json`
- Parses each PDF to extract meals
- Creates instruction-following training examples
- Saves to `outputs/training_data.jsonl`
- Takes ~5-10 minutes

**Output format**:
```json
{
  "instruction": "Create a diet plan...",
  "input": "User Profile: ...",
  "output": "Diet Plan: ..."
}
```

### Fine-tune Model (GPU Required)

```powershell
python service/recommender_ml/train_nutrition_model.py --epochs 3
```

**Requirements**:
- GPU with 16GB+ VRAM
- ~14GB disk space for model
- 4-8 hours training time

**Parameters**:
- `--epochs 3`: Number of training passes (3-5 recommended)
- `--batch_size 4`: Batch size (reduce if out of memory)
- `--output_dir ./models/nutrition-finetuned`: Output location

### Use Fine-tuned Model

Edit `service/recommender_ml/ml_recommender.py` or pass during init:

```python
from service.recommender_ml import MLRecommender

# Use your fine-tuned model
recommender = MLRecommender(
    model_name="./models/nutrition-finetuned"
)

# Or use base model
recommender = MLRecommender(
    model_name="AweXiaoXiao/NutritionVerse-Real-7B"
)
```

## Common Issues & Solutions

### "CUDA out of memory"

**Solutions**:
1. Reduce batch size:
   ```powershell
   python train_nutrition_model.py --batch_size 2
   ```

2. Enable 8-bit quantization (edit `train_nutrition_model.py` line ~280):
   ```python
   model = AutoModelForCausalLM.from_pretrained(
       base_model,
       load_in_8bit=True,  # Add this
       device_map="auto",
       torch_dtype=torch.float16
   )
   ```

3. Use gradient checkpointing (saves memory):
   ```python
   model.gradient_checkpointing_enable()
   ```

### "No module named 'bitsandbytes'"

```powershell
pip install bitsandbytes
```

### "torch.cuda.is_available() returns False"

**Check GPU**:
```powershell
nvidia-smi
```

**Reinstall PyTorch with CUDA**:
```powershell
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Verify CUDA**:
```python
import torch
print(torch.cuda.is_available())  # Should be True
print(torch.cuda.get_device_name(0))  # GPU name
```

### "File not found: outputs/pdf_index.json"

Make sure you run from project root:
```powershell
cd "d:\Documents\Diet plan"
python service/recommender_ml/train_nutrition_model.py
```

### Training is Very Slow

**Use GPU**: Training on CPU takes days vs hours on GPU

**Check GPU is being used**:
```python
import torch
print(torch.cuda.is_available())  # Must be True
```

**Monitor GPU usage**:
```powershell
nvidia-smi -l 1  # Updates every second
```

### Model Download Fails

**Clear cache and retry**:
```powershell
Remove-Item -Recurse -Force $env:USERPROFILE\.cache\huggingface
python -c "from transformers import AutoModel; AutoModel.from_pretrained('AweXiaoXiao/NutritionVerse-Real-7B')"
```

**Use mirror** (if in restricted region):
```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
```

## Verification

### Check Installation

```powershell
python -c "import transformers, torch, sentence_transformers, numpy, faiss; print('OK')"
```

### Check GPU

```powershell
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### Check Training Data

```powershell
# After running train_nutrition_model.py
Get-Content "outputs\training_data.jsonl" | Select-Object -First 5
```

### Test Inference

```python
from service.recommender_ml import MLRecommender

try:
    recommender = MLRecommender()
    print("✓ MLRecommender initialized")
    
    result = recommender.recommend({
        "gender": "female",
        "age": 28,
        "bmi_category": "overweight",
        "diet_type": "vegetarian",
        "region": "north_indian",
        "goal": "weight_loss"
    }, top_k=3)
    
    print(f"✓ Status: {result.get('status')}")
    print(f"✓ Recommendations: {len(result.get('recommendations', []))}")
except Exception as e:
    print(f"✗ Error: {e}")
```

## Performance Tips

### Inference Optimization

1. **Use GPU**: 3-8 sec vs 15-30 sec on CPU
2. **Batch requests**: Process multiple users together
3. **Cache embeddings**: Pre-compute PDF embeddings once
4. **Use half precision**: `torch_dtype=torch.float16`

### Training Optimization

1. **Use multiple GPUs**: Add `device_map="auto"`
2. **Increase batch size**: If you have VRAM: `--batch_size 8`
3. **Mixed precision**: Automatically enabled with `fp16=True`
4. **Gradient accumulation**: Effective batch size = batch_size * 4

## File Locations

```
d:\Documents\Diet plan\
├── outputs/
│   ├── pdf_index.json           # 460 PDF metadata
│   ├── pdf_embeddings.npy       # Pre-computed embeddings
│   └── training_data.jsonl      # Generated training data
├── models/
│   └── nutrition-finetuned/     # Your fine-tuned model
└── service/
    └── recommender_ml/
        ├── ml_recommender.py    # Main implementation
        ├── train_nutrition_model.py  # Training script
        ├── README.md            # Full documentation
        └── FINE_TUNING_GUIDE.md # Training guide
```

## Next Steps

1. ✅ **Training data generated**: `outputs/training_data.jsonl`
2. **Fine-tune model** (optional, requires GPU):
   ```powershell
   python service/recommender_ml/train_nutrition_model.py --epochs 3
   ```
3. **Use in API**: Model loads automatically when you start the server
4. **Test recommendations**: Navigate to system and select "AI Nutritionist"

## Support

- **Documentation**: `service/recommender_ml/README.md`
- **Fine-tuning Guide**: `service/recommender_ml/FINE_TUNING_GUIDE.md`
- **Quick Reference**: `service/recommender_ml/QUICK_REFERENCE.md`
