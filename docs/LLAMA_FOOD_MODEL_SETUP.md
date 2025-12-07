# 🦙 Llama Food Model Setup - FortyMiles/Llama-3-Diet-Instruct-8B

## Model Info:
- **Model**: FortyMiles/Llama-3-Diet-Instruct-8B
- **Size**: 8B parameters (~16GB)
- **Specialization**: Diet and nutrition planning
- **URL**: https://huggingface.co/FortyMiles/Llama-3-Diet-Instruct-8B

---

## Quick Setup (15 minutes)

### 1️⃣ Open Colab Notebook

1. Go to: https://colab.research.google.com
2. File → Upload notebook
3. Upload: `notebooks/Colab_Llama_FoodModel.ipynb`

### 2️⃣ Enable GPU

1. Runtime → Change runtime type
2. Select: **T4 GPU** (or **A100** if you have Colab Pro)
3. Click: Save

### 3️⃣ Get Ngrok Token

1. Go to: https://ngrok.com (sign up free)
2. Get token: https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy your authtoken

### 4️⃣ Run Setup Cells

**Cell 1 - Install packages:**
```python
!pip install -q transformers accelerate torch bitsandbytes
!pip install -q flask flask-cors pyngrok
```
▶️ Click Run (takes 30 seconds)

**Cell 2 - Setup Ngrok:**
```python
NGROK_TOKEN = "YOUR_TOKEN_HERE"  # Paste your token
!ngrok authtoken {NGROK_TOKEN}
```
▶️ Update token → Click Run

**Cell 3 - Create server:**
▶️ Just click Run (creates server code)

**Cell 4 - Start server:**
⚠️ **This takes 5-10 minutes on first run** (downloads 16GB model)
▶️ Click Run and WAIT...

You'll see:
```
Loading FortyMiles Llama-3 Diet Model...
Loading tokenizer...
Loading model with 4-bit quantization...
Fetching files...
model-00001-of-00004.safetensors: ...
model-00002-of-00004.safetensors: ...
model-00003-of-00004.safetensors: ...
model-00004-of-00004.safetensors: ...
✅ Llama-3 Diet Model loaded successfully on cuda:0!

🌐 PUBLIC URL (COPY THIS):
   https://abc123.ngrok.io
```

📋 **COPY THE URL!**

---

## 5️⃣ Update Local Code

On your Windows machine:

1. Open: `D:\Documents\Diet plan\service\recommender_ml\ml_recommender.py`
2. Update lines 14-15:
```python
USE_COLAB = True
COLAB_API_URL = "https://YOUR-NGROK-URL.ngrok.io"  # Paste URL from Colab
```
3. Save file

---

## 6️⃣ Restart Local Server

```powershell
# Stop current server (Ctrl+C)
python -m uvicorn service.api:app --reload --port 8000
```

Watch for:
```
INFO:🌐 Using Colab API for model inference
INFO:📡 Colab URL: https://abc123.ngrok.io
INFO:✅ Connected to Colab API
INFO:   Model loaded: True
INFO:   Model name: FortyMiles/Llama-3-Diet-Instruct-8B
INFO:   Device: cuda:0
```

---

## 7️⃣ Test It!

1. http://localhost:8000/choose-system
2. Click: **"Use AI Nutritionist"**
3. Fill profile
4. Submit
5. **Generation takes 10-15 seconds** (larger model, more detailed output)

---

## 📊 Model Comparison

| Model | Size | Speed | Quality | Specialization |
|-------|------|-------|---------|----------------|
| Phi-2 (yours) | 2.7B | ⚡⚡⚡ Fast (5s) | ✅ Good | General + Fine-tuned |
| **Llama-3 Food** | **8B** | **⚡⚡ Medium (15s)** | **✅✅✅ Excellent** | **Diet-specific** |

---

## 🔧 Why Use Llama Food Model?

✅ **Purpose-built for diet planning** - Trained specifically on nutrition data  
✅ **Better meal suggestions** - Understands food combinations and nutrition  
✅ **More detailed responses** - 8B params vs 2.7B  
✅ **4-bit quantization** - Runs on free T4 GPU  
✅ **No fine-tuning needed** - Already specialized for food  

---

## 🎯 Advantages:

1. **Specialized Knowledge**: Model knows about:
   - Indian cuisine
   - Meal timing
   - Portion sizes
   - Nutritional balance
   - Diet types (veg/non-veg/vegan)

2. **Better Structure**: Generates:
   - Complete meal plans
   - Detailed recipes
   - Nutrition breakdowns
   - Cooking instructions

3. **No Training Needed**: Unlike Phi-2, this model is already trained on diet data!

---

## ⚠️ Notes:

- **First load**: 5-10 minutes (downloads 16GB)
- **Subsequent loads**: 2-3 minutes (cached)
- **Colab session**: 12 hours (free tier)
- **Memory**: Uses ~10GB GPU RAM (4-bit quantized)
- **Ngrok URL**: Changes each restart

---

## 💡 Pro Tips:

✅ Use **Colab Pro** ($10/month) for:
- A100 GPU (3x faster)
- 24-hour sessions
- Background execution

✅ Model is **cached** after first download - next restart is fast!

✅ Keep Colab tab **open** and **pinned** to prevent disconnection

---

## 🎉 Done!

Your specialized Llama-3 diet model is now serving your app via Colab GPU!

**Better diet plans, specialized knowledge, zero training required!** 🚀
