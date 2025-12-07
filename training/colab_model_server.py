"""
Flask API Server for Colab to serve fine-tuned Phi-2 model
Upload this file to Colab and run it there
"""
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
CORS(app)  # Enable CORS for all routes

# Global model variables
model = None
tokenizer = None

def load_model():
    """Load fine-tuned Phi-2 model on Colab"""
    global model, tokenizer
    
    logger.info("Loading fine-tuned Phi-2 model on Colab...")
    
    try:
        # Load tokenizer
        logger.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/phi-2",
            trust_remote_code=True
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load base model
        logger.info("Loading base Phi-2 model...")
        model = AutoModelForCausalLM.from_pretrained(
            "microsoft/phi-2",
            torch_dtype=torch.float16,
            device_map="auto",  # Use GPU automatically
            trust_remote_code=True
        )
        
        # Load LoRA adapter from your checkpoint
        logger.info("Loading LoRA adapter...")
        # Note: You'll upload your checkpoint-224 folder to Colab
        model = PeftModel.from_pretrained(
            model,
            "/content/checkpoint-224",  # Path where you upload checkpoint
            is_trainable=False
        )
        model.eval()
        
        logger.info("✅ Model loaded successfully on GPU!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(next(model.parameters()).device) if model else "not loaded"
    })

@app.route('/generate', methods=['POST'])
def generate():
    """Generate diet plan from prompt"""
    global model, tokenizer
    
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 800)
        temperature = data.get('temperature', 0.7)
        top_p = data.get('top_p', 0.9)
        
        logger.info(f"Generating response (max_tokens={max_tokens})...")
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate
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
        
        # Decode
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only response part
        if "### Response:" in response:
            response = response.split("### Response:")[-1].strip()
        
        logger.info("✅ Generation complete")
        
        return jsonify({
            "status": "success",
            "response": response,
            "prompt_length": len(prompt),
            "response_length": len(response)
        })
        
    except Exception as e:
        logger.error(f"Error generating: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Load model on startup
    if load_model():
        # Start ngrok tunnel to expose API
        public_url = ngrok.connect(5000)
        logger.info(f"🌐 Public URL: {public_url}")
        logger.info(f"📝 Copy this URL and use it in your local ml_recommender.py")
        
        # Start Flask server
        app.run(host='0.0.0.0', port=5000)
    else:
        logger.error("Failed to load model. Exiting...")
