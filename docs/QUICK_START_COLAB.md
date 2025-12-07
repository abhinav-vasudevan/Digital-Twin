# 🚀 Quick Start: Run Phi-2 Model on Google Colab

## Why Use Colab?
✅ **FREE GPU** (T4 GPU - 10x faster than CPU)  
✅ **No Local RAM needed** (Colab has 12GB)  
✅ **Faster generation** (3-5 seconds vs 30-60 seconds)  
✅ **Always online** (Keep session open, API always accessible)

---

## Step-by-Step Setup (10 minutes)

### 1️⃣ Upload Checkpoint to Google Drive

1. Open Google Drive: https://drive.google.com
2. Create folder: `My Drive/Diet-Plan-AI/`
3. Upload your `checkpoint-224` folder there (drag & drop the whole folder)
4. Wait for upload to complete (~100MB)

### 2️⃣ Get Ngrok Token (Free)

1. Go to: https://ngrok.com
2. Click "Sign Up" (free account)
3. After login, go to: https://dashboard.ngrok.com/get-started/your-authtoken
4. Copy your authtoken (looks like: `2abcdefg...`)

### 3️⃣ Open Colab Notebook

1. Open: https://colab.research.google.com
2. Click: File → Upload notebook
3. Upload: `notebooks/Colab_Phi2_Server.ipynb` (from your Diet plan folder)

### 4️⃣ Enable GPU

1. In Colab: Runtime → Change runtime type
2. Select: **T4 GPU**
3. Click: Save

### 5️⃣ Run Setup Cells

**Cell 1 - Install packages:**
```python
# Uses latest compatible versions
!pip install -q transformers peft accelerate torch
!pip install -q flask flask-cors pyngrok
```
▶️ Click Run (takes 30 seconds)

**Cell 2 - Mount Drive:**
```python
from google.colab import drive
drive.mount('/content/drive')
!cp -r "/content/drive/MyDrive/Diet-Plan-AI/checkpoint-224" /content/
```
▶️ Click Run → Grant permissions → Select your Google account

**Cell 3 - Setup Ngrok:**
```python
NGROK_TOKEN = "YOUR_TOKEN_HERE"  # ⚠️ Paste your token from step 2
!ngrok authtoken {NGROK_TOKEN}
```
▶️ Replace token → Click Run

**Cell 4 - Create server:**
▶️ Just click Run (creates server code)

**Cell 5 - Start server:**
▶️ Click Run and WAIT for output:

```
🌐 PUBLIC URL (COPY THIS):
   https://abc123.ngrok.io

📝 Update your local ml_recommender.py:
   USE_COLAB = True
   COLAB_API_URL = "https://abc123.ngrok.io"
```

📋 **COPY THE URL!** (e.g., `https://abc123.ngrok.io`)

### 6️⃣ Update Local Code

On your Windows machine:

1. Open: `D:\Documents\Diet plan\service\recommender_ml\ml_recommender.py`
2. Find lines 14-16:
```python
USE_COLAB = False  # Change to True
COLAB_API_URL = "https://YOUR-NGROK-URL.ngrok.io"  # Paste your URL
```
3. Update to:
```python
USE_COLAB = True
COLAB_API_URL = "https://abc123.ngrok.io"  # Your actual URL
```
4. Save file

### 7️⃣ Restart Local Server

In PowerShell:
```powershell
# Stop current server (Ctrl+C)
python -m uvicorn service.api:app --reload --port 8000
```

Watch for this in logs:
```
INFO:service.recommender_ml.ml_recommender:🌐 Using Colab API for model inference
INFO:service.recommender_ml.ml_recommender:📡 Colab URL: https://abc123.ngrok.io
INFO:service.recommender_ml.ml_recommender:✅ Connected to Colab API
INFO:service.recommender_ml.ml_recommender:   Model loaded: True
INFO:service.recommender_ml.ml_recommender:   Device: cuda:0
```

### 8️⃣ Test It!

1. Go to: http://localhost:8000/choose-system
2. Click: **"Use AI Nutritionist"**
3. Fill profile
4. Submit
5. **Generation takes only 5-10 seconds now!** 🚀

---

## 📊 Performance Comparison

| Method | Device | Time | RAM Used |
|--------|--------|------|----------|
| Local CPU | Your PC | 30-60s | 6GB |
| **Colab GPU** | **T4 GPU** | **3-5s** | **0GB (on your PC)** |

---

## 🔧 Troubleshooting

### ❌ "Cannot connect to Colab API"
- Check Cell 5 is still running in Colab
- Verify ngrok URL is correct (no typos)
- Make sure `USE_COLAB = True` in ml_recommender.py

### ❌ "Checkpoint not found"
- Verify checkpoint-224 is in Google Drive
- Check path in Cell 2: `/content/drive/MyDrive/YOUR-FOLDER/checkpoint-224`

### ❌ "Ngrok authentication failed"
- Get new token from: https://dashboard.ngrok.com/get-started/your-authtoken
- Update Cell 3 with new token

### ⏰ Colab disconnects after 12 hours
- Just re-run Cell 5
- Copy new ngrok URL (it changes each time)
- Update ml_recommender.py with new URL
- Restart local server

---

## 💡 Tips

✅ **Keep Colab tab open** - Don't close it while using  
✅ **Upgrade to Colab Pro** ($10/month) for:  
   - 24-hour sessions (vs 12 hours)
   - Faster GPUs (V100/A100)
   - Priority access

✅ **Save Colab notebook** - File → Save a copy in Drive

---

## 🎉 Done!

Your fine-tuned Phi-2 model is now running on FREE Colab GPU!

**Generation is 10x faster and uses 0% of your PC's resources.** 🚀
