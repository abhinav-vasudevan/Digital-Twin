# Run Fine-tuned Phi-2 on Google Colab

Follow these steps to run your model on Colab with GPU:

## Step 1: Setup Colab Notebook

Create a new notebook at: https://colab.research.google.com

Make sure to enable GPU:
- Runtime → Change runtime type → Hardware accelerator → **T4 GPU** → Save

## Step 2: Install Dependencies

```python
# Cell 1: Install packages
!pip install -q transformers peft accelerate torch flask flask-cors pyngrok
```

## Step 3: Upload Your LoRA Checkpoint

```python
# Cell 2: Upload checkpoint-224 folder
from google.colab import drive
drive.mount('/content/drive')

# Option A: If checkpoint is in Google Drive
!cp -r "/content/drive/MyDrive/checkpoint-224" /content/

# Option B: Manual upload (slower)
from google.colab import files
import zipfile

# First, zip your checkpoint-224 folder on local machine
# Then upload it
uploaded = files.upload()  # Upload checkpoint-224.zip
!unzip checkpoint-224.zip -d /content/
```

## Step 4: Setup Ngrok (for public API)

```python
# Cell 3: Setup ngrok authentication
# Sign up at https://ngrok.com and get your auth token
!ngrok authtoken YOUR_NGROK_TOKEN_HERE
```

## Step 5: Copy and Run Server Code

```python
# Cell 4: Create server file
%%writefile colab_server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from pyngrok import ngrok
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

model = None
tokenizer = None

def load_model():
    global model, tokenizer
    logger.info("Loading fine-tuned Phi-2 model...")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/phi-2",
            trust_remote_code=True
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model = AutoModelForCausalLM.from_pretrained(
            "microsoft/phi-2",
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        model = PeftModel.from_pretrained(
            model,
            "/content/checkpoint-224",
            is_trainable=False
        )
        model.eval()
        
        logger.info("✅ Model loaded on GPU!")
        return True
    except Exception as e:
        logger.error(f"Failed: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(next(model.parameters()).device) if model else "not loaded"
    })

@app.route('/generate', methods=['POST'])
def generate():
    global model, tokenizer
    
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 800)
        temperature = data.get('temperature', 0.7)
        top_p = data.get('top_p', 0.9)
        
        inputs = tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "### Response:" in response:
            response = response.split("### Response:")[-1].strip()
        
        return jsonify({
            "status": "success",
            "response": response
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if load_model():
        public_url = ngrok.connect(5000)
        print(f"\n🌐 PUBLIC URL: {public_url}")
        print(f"📝 Copy this URL for your local ml_recommender.py\n")
        app.run(host='0.0.0.0', port=5000)
```

## Step 6: Start Server

```python
# Cell 5: Run server (keep this cell running)
!python colab_server.py
```

**IMPORTANT**: Copy the ngrok URL from output (e.g., `https://abc123.ngrok.io`)

## Step 7: Update Local Code

On your local machine, open `service/recommender_ml/ml_recommender.py` and update:

```python
# Add at top of file
COLAB_API_URL = "https://YOUR-NGROK-URL.ngrok.io"  # Paste URL from Colab
USE_COLAB = True  # Set to True to use Colab

# Then update _generate_with_hf() method to call Colab API instead
```

## Benefits:

✅ **10x Faster**: GPU vs CPU
✅ **No Local RAM**: Uses Colab's 12GB RAM
✅ **Free GPU**: T4 GPU on free tier
✅ **Always Available**: Keep Colab session open

## Tips:

- Colab disconnects after 12 hours - just restart
- Can upgrade to Colab Pro for longer sessions
- Ngrok URL changes each restart - update local code
- Test with: `curl https://YOUR-URL.ngrok.io/health`
