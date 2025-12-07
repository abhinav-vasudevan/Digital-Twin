# NutritionVerse-Real Quick Reference

## Model Information
- **Name**: AweXiaoXiao/NutritionVerse-Real-7B
- **Type**: Specialized nutrition language model
- **Size**: ~14 GB
- **Source**: HuggingFace

## Installation

```powershell
# Quick install
.\install_nutritionverse.ps1

# Manual install
pip install transformers torch sentence-transformers numpy faiss-cpu accelerate
```

## Usage

### Basic Recommendation
```python
from service.recommender_ml import MLRecommender

recommender = MLRecommender()  # Uses NutritionVerse-Real by default
result = recommender.recommend({
    "gender": "female",
    "age": 28,
    "bmi_category": "overweight",
    "diet_type": "vegetarian",
    "region": "north_indian",
    "goal": "weight_loss"
})
```

### Use Fine-tuned Model
```python
recommender = MLRecommender(
    model_name="./models/nutrition-finetuned"  # Your fine-tuned version
)
```

## Fine-tuning

### Quick Start
```powershell
# Generate training data
python service/recommender_ml/train_nutrition_model.py

# Fine-tune (GPU required)
python service/recommender_ml/train_nutrition_model.py --epochs 3
```

### Full Guide
See: `service/recommender_ml/FINE_TUNING_GUIDE.md`

## API Endpoint

```
POST /api/meal-plan/generate-ml
```

Returns personalized diet plan using RAG + NutritionVerse-Real

## Requirements

**Minimum**:
- RAM: 16 GB
- GPU: 8 GB VRAM (for inference)
- Storage: 20 GB

**Recommended**:
- RAM: 32 GB
- GPU: 16 GB VRAM
- Storage: 50 GB

**Fine-tuning**:
- GPU: 16 GB+ VRAM
- Time: 4-8 hours

## Key Files

- `ml_recommender.py` - Main implementation
- `train_nutrition_model.py` - Fine-tuning script
- `FINE_TUNING_GUIDE.md` - Complete training guide
- `README.md` - Full documentation

## Common Commands

```powershell
# Test setup
python service/recommender_ml/setup_check.py

# Start API server
cd service
python api.py

# Fine-tune with custom config
python service/recommender_ml/train_nutrition_model.py \
  --epochs 5 \
  --batch_size 4 \
  --output_dir ./models/my-model
```

## Troubleshooting

**CUDA out of memory**:
- Reduce batch size: `--batch_size 2`
- Use 8-bit: Edit code to add `load_in_8bit=True`

**Model download slow**:
- First download takes time (~14GB)
- Cached for future use

**No GPU detected**:
- Install CUDA PyTorch: 
  ```
  pip install torch --index-url https://download.pytorch.org/whl/cu118
  ```

## Performance

- **Inference**: 3-8 sec (GPU) / 15-30 sec (CPU)
- **Vector Search**: ~10ms
- **Fine-tuning**: 4-8 hours (GPU)

## Support

- **Documentation**: `service/recommender_ml/README.md`
- **Fine-tuning**: `service/recommender_ml/FINE_TUNING_GUIDE.md`
- **HuggingFace**: https://huggingface.co/AweXiaoXiao/NutritionVerse-Real-7B
