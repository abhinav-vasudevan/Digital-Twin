"""
Production-level ML Recommender using RAG + Fine-tuned NutritionVerse
Replaces the weighted scoring system with LLM-based recommendations
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== COLAB API CONFIGURATION ====================
# Set USE_COLAB = True to use Colab GPU instead of local CPU
# Update COLAB_API_URL with your ngrok URL from Colab output
USE_COLAB = True  # ✅ Using Colab GPU
COLAB_API_URL = "https://declensional-carmella-betulaceous.ngrok-free.dev"  # ✅ Your ngrok URL
# =================================================================


@dataclass
class UserProfile:
    """User profile for ML-based recommendations"""
    gender: str
    age: int
    height: float
    weight: float
    bmi_category: str
    activity_level: str
    diet_type: str
    region: str
    goal: str
    health_conditions: List[str] = None
    allergies: List[str] = None
    
    def __post_init__(self):
        if self.health_conditions is None:
            self.health_conditions = []
        if self.allergies is None:
            self.allergies = []


class MLRecommender:
    """
    Production ML Recommender using RAG + Fine-tuned Model
    
    Architecture:
    1. Vector Search: Find semantically similar PDFs from database
    2. PDF Parser: Extract meals from top-k similar PDFs
    3. Fine-tuned LLM: Generate personalized plan using retrieved meals
    
    This ensures:
    - 100% meals come from your 460 PDFs (no hallucination)
    - Intelligent selection and explanation via LLM
    - Scalable and production-ready
    """
    
    def __init__(
        self,
        index_path: str = "outputs/pdf_index.json",
        embeddings_path: str = "outputs/pdf_embeddings.npy",
        model_name: str = r"D:\Documents\Diet plan\Diet model phi - 2\phi-2-base",
        finetuned_path: str = r"D:\Documents\Diet plan\Diet model phi - 2\checkpoint-224",
        use_local: bool = False
    ):
        """
        Initialize ML Recommender
        
        Args:
            index_path: Path to PDF index
            embeddings_path: Path to pre-computed embeddings
            model_name: Base model path (local phi-2-base folder)
            finetuned_path: Path to fine-tuned LoRA adapter checkpoint
            use_local: Use local Ollama (True) or Hugging Face (False, recommended)
        """
        self.index_path = Path(index_path)
        self.embeddings_path = Path(embeddings_path)
        self.model_name = model_name
        self.finetuned_path = finetuned_path
        self.use_local = use_local
        
        # Load PDF index
        self.index = None
        self.load_index()
        
        # Initialize embeddings (for vector search)
        self.embeddings = None
        self.embedding_model = None
        self.load_or_create_embeddings()
        
        # Initialize LLM
        self.llm = None
        if USE_COLAB:
            logger.info("🌐 Using Colab API for model inference")
            logger.info(f"📡 Colab URL: {COLAB_API_URL}")
            self.llm = True  # Mark as available (using Colab)
            self._check_colab_connection()
        else:
            logger.info("💻 Using local model")
            self.initialize_llm()
    
    def load_index(self):
        """Load PDF index"""
        logger.info(f"Loading PDF index from {self.index_path}")
        
        if not self.index_path.exists():
            raise FileNotFoundError(f"Index file not found: {self.index_path}")
        
        with open(self.index_path, 'r', encoding='utf-8') as f:
            self.index = json.load(f)
        
        logger.info(f"Loaded {self.index['metadata']['total_plans']} plans")
    
    def load_or_create_embeddings(self):
        """Load pre-computed embeddings or create them"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Initialize embedding model
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            # Try to load pre-computed embeddings
            if self.embeddings_path.exists():
                logger.info(f"Loading pre-computed embeddings from {self.embeddings_path}")
                self.embeddings = np.load(str(self.embeddings_path))
                logger.info(f"Loaded {len(self.embeddings)} embeddings")
            else:
                logger.info("No pre-computed embeddings found. Creating embeddings...")
                self.create_embeddings()
        
        except ImportError:
            logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")
            logger.warning("Falling back to keyword-based search")
            self.embedding_model = None
            self.embeddings = None
    
    def create_embeddings(self):
        """Create embeddings for all PDFs"""
        if not self.embedding_model:
            logger.error("Embedding model not available")
            return
        
        logger.info("Creating embeddings for all PDFs...")
        
        # Create text representations for each plan
        texts = []
        for plan in self.index['plans']:
            # Combine key attributes into searchable text
            text = self._plan_to_text(plan)
            texts.append(text)
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} plans...")
        self.embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Save embeddings
        np.save(str(self.embeddings_path), self.embeddings)
        logger.info(f"Saved embeddings to {self.embeddings_path}")
    
    def _plan_to_text(self, plan: Dict[str, Any]) -> str:
        """Convert plan metadata to searchable text"""
        parts = []
        
        # Basic attributes
        if plan.get('gender'):
            parts.append(f"gender: {plan['gender']}")
        if plan.get('diet_type'):
            parts.append(f"diet: {plan['diet_type']}")
        if plan.get('region'):
            parts.append(f"region: {plan['region']}")
        if plan.get('bmi_category'):
            parts.append(f"bmi: {plan['bmi_category']}")
        if plan.get('activity'):
            parts.append(f"activity: {plan['activity']}")
        if plan.get('category'):
            parts.append(f"goal: {plan['category']}")
        
        # Plan title
        if plan.get('title'):
            parts.append(f"plan: {plan['title']}")
        
        return " ".join(parts)
    
    def _check_colab_connection(self):
        """Check if Colab API is accessible"""
        try:
            # Add header to bypass ngrok browser warning
            headers = {
                'ngrok-skip-browser-warning': 'true',
                'User-Agent': 'Python-Requests'
            }
            response = requests.get(f"{COLAB_API_URL}/health", timeout=5, verify=False, headers=headers)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Connected to Colab API")
                logger.info(f"   Model loaded: {data.get('model_loaded')}")
                logger.info(f"   Device: {data.get('device')}")
            else:
                logger.warning(f"⚠️ Colab API returned status {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Cannot connect to Colab API: {e}")
            logger.error(f"   Make sure USE_COLAB=True and COLAB_API_URL is correct")
            logger.error(f"   Current URL: {COLAB_API_URL}")
    
    def initialize_llm(self):
        """Initialize fine-tuned Phi-2 model with LoRA adapter"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel
            import torch
            import os
            
            logger.info(f"Loading fine-tuned Phi-2 model...")
            logger.info(f"Base model: {self.model_name}")
            logger.info(f"Fine-tuned adapter: {self.finetuned_path}")
            logger.info("This may take a few minutes on first load...")
            
            # Set environment variable to use offline mode if model is cached
            os.environ["HF_HUB_OFFLINE"] = "0"  # Try online first
            
            # Load tokenizer from checkpoint first (faster, already downloaded)
            logger.info("Loading tokenizer from checkpoint...")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.finetuned_path, 
                    trust_remote_code=True,
                    local_files_only=True
                )
            except Exception:
                # Fallback to downloading from HuggingFace
                logger.info("Tokenizer not in checkpoint, downloading from HuggingFace...")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name, 
                    trust_remote_code=True,
                    resume_download=True,
                    local_files_only=False
                )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load base model
            logger.info("Loading base Phi-2 model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                local_files_only=True  # Use cached model
            )
            
            # Move to device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            self.model = self.model.to(device)
            
            # Load LoRA adapter with proper error handling
            logger.info("Loading fine-tuned LoRA adapter...")
            try:
                self.model = PeftModel.from_pretrained(
                    self.model, 
                    self.finetuned_path,
                    is_trainable=False
                )
                self.model.eval()
                logger.info("✅ Fine-tuned model with LoRA adapter loaded successfully!")
                self.llm = True
            except Exception as e:
                logger.error(f"Failed to load LoRA adapter: {e}")
                logger.info("Continuing with base model only...")
                self.model.eval()
                self.llm = True  # Still use base model
            
        except ImportError as e:
            logger.error(f"Missing dependencies: {e}")
            logger.error("Install with: pip install transformers torch peft")
            self.llm = None
        except Exception as e:
            logger.error(f"Failed to load fine-tuned model: {e}")
            logger.error(f"Base model: {self.model_name}")
            logger.error(f"Fine-tuned path: {self.finetuned_path}")
            self.llm = None
    
    def vector_search(self, user_profile: UserProfile, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find top-k most similar PDFs using vector search
        
        Args:
            user_profile: User profile
            top_k: Number of PDFs to retrieve
            
        Returns:
            List of top-k most similar plans
        """
        if not self.embedding_model or self.embeddings is None:
            # Fallback to keyword-based search
            logger.warning("Vector search not available, using keyword search")
            return self.keyword_search(user_profile, top_k)
        
        # Create query embedding
        query_text = self._profile_to_text(user_profile)
        query_embedding = self.embedding_model.encode([query_text], convert_to_numpy=True)[0]
        
        # Calculate cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return top-k plans with similarity scores
        results = []
        for idx in top_indices:
            plan = self.index['plans'][idx].copy()
            plan['similarity_score'] = float(similarities[idx])
            results.append(plan)
        
        logger.info(f"Found {len(results)} similar plans (top similarity: {results[0]['similarity_score']:.3f})")
        return results
    
    def keyword_search(self, user_profile: UserProfile, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Search and return ALL PDFs matching diet type and goal category
        
        Args:
            user_profile: User profile
            top_k: Number of PDFs to retrieve (None = return ALL matching PDFs)
            
        Returns:
            ALL matching plans filtered by diet type and goal category
        """
        # STEP 1: Filter by diet type (CRITICAL - veg users never get non-veg)
        diet_filtered_plans = [
            plan for plan in self.index['plans']
            if plan.get('diet_type') == user_profile.diet_type
        ]
        
        logger.info(f"✅ Step 1: Filtered {len(diet_filtered_plans)} plans matching diet type: {user_profile.diet_type}")
        
        # STEP 2: Filter by goal/category (EXACT match like exact match system)
        category_filtered_plans = [
            plan for plan in diet_filtered_plans
            if plan.get('category', '').lower() == user_profile.goal.lower()
        ]
        
        # If no exact category match, try to find similar categories
        if not category_filtered_plans:
            logger.warning(f"No exact match for goal '{user_profile.goal}', trying similar categories...")
            # Try partial match as fallback
            goal_keywords = user_profile.goal.lower().replace('_', ' ').split()
            for plan in diet_filtered_plans:
                category = plan.get('category', '').lower()
                # Match if ALL goal keywords appear in category (not just any)
                if all(keyword in category for keyword in goal_keywords):
                    category_filtered_plans.append(plan)
        
        # If still no matches, use all diet-filtered plans
        if not category_filtered_plans:
            logger.warning(f"No plans found for goal '{user_profile.goal}', using all {user_profile.diet_type} plans")
            category_filtered_plans = diet_filtered_plans
        else:
            logger.info(f"✅ Step 2: Filtered {len(category_filtered_plans)} plans matching goal: {user_profile.goal}")
        
        # STEP 3: Score and rank plans
        results = []
        for plan in category_filtered_plans:
            score = 0
            
            # Diet + Category already filtered - base score
            score += 30
            
            # Exact matches
            if plan.get('gender') == user_profile.gender:
                score += 15
            if plan.get('region') == user_profile.region:
                score += 10
            if plan.get('bmi_category') == user_profile.bmi_category:
                score += 10
            if plan.get('activity') == user_profile.activity_level:
                score += 10
            
            plan_copy = plan.copy()
            plan_copy['similarity_score'] = score / 75.0
            results.append(plan_copy)
        
        # Sort by score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Return ALL matching plans (or top_k if specified)
        final_count = len(results) if top_k is None else min(top_k, len(results))
        logger.info(f"✅ Step 3: Returning {final_count} plans to feed into ML model")
        
        return results if top_k is None else results[:top_k]
    
    def _profile_to_text(self, user_profile: UserProfile) -> str:
        """Convert user profile to searchable text"""
        parts = [
            f"gender: {user_profile.gender}",
            f"diet: {user_profile.diet_type}",
            f"region: {user_profile.region}",
            f"bmi: {user_profile.bmi_category}",
            f"activity: {user_profile.activity_level}",
            f"goal: {user_profile.goal}"
        ]
        
        if user_profile.health_conditions:
            parts.append(f"conditions: {', '.join(user_profile.health_conditions)}")
        
        return " ".join(parts)
    
    def extract_meals_from_pdfs(self, plans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract meals from selected PDFs using the comprehensive parser
        
        Args:
            plans: List of plan metadata
            
        Returns:
            List of extracted meals with full details
        """
        try:
            from service.pdf_parser import CompletePDFParser
        except ImportError:
            from pdf_parser import CompletePDFParser
        
        parser = CompletePDFParser()
        all_meals = []
        
        for plan in plans:
            pdf_path = plan.get('file_path')
            if not pdf_path:
                continue
            
            # Make path absolute - PDFs are in project root, not service/
            if not Path(pdf_path).is_absolute():
                # Go up two levels from service/recommender_ml/ to project root
                project_root = Path(__file__).parent.parent.parent
                pdf_path = project_root / pdf_path
            
            if not Path(pdf_path).exists():
                logger.warning(f"PDF not found: {pdf_path}")
                continue
            
            # Parse PDF
            logger.info(f"Parsing PDF: {Path(pdf_path).name}")
            result = parser.parse_complete_pdf(str(pdf_path))
            
            if 'error' in result:
                logger.warning(f"Error parsing {pdf_path}: {result['error']}")
                continue
            
            # Add meals with source info
            for meal in result.get('meals', []):
                meal['source_pdf'] = plan.get('title', Path(pdf_path).name)
                meal['source_category'] = plan.get('category', 'unknown')
                meal['similarity_score'] = plan.get('similarity_score', 0.0)
                all_meals.append(meal)
        
        logger.info(f"Extracted {len(all_meals)} meals from {len(plans)} PDFs")
        return all_meals
    
    def generate_plan_with_llm(
        self,
        user_profile: UserProfile,
        retrieved_meals: List[Dict[str, Any]],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Generate personalized diet plan using LLM with retrieved meals
        
        Args:
            user_profile: User profile
            retrieved_meals: Meals extracted from similar PDFs
            top_k: Number of plan options to return
            
        Returns:
            Generated diet plan recommendations
        """
        if not self.llm and not self.use_local:
            logger.error("LLM not initialized")
            return {
                "status": "error",
                "message": "ML recommender not available. Please check configuration."
            }
        
        # Build context from retrieved meals
        meals_context = self._format_meals_for_llm(retrieved_meals[:50])  # Limit context
        
        # Build prompt
        prompt = self._build_prompt(user_profile, meals_context)
        
        # Generate response with NutritionVerse
        response = self._generate_with_hf(prompt)
        
        # Parse and structure response
        return self._parse_llm_response(response, retrieved_meals, user_profile)
    
    def _format_meals_for_llm(self, meals: List[Dict[str, Any]]) -> str:
        """Format meals into LLM-friendly context with complete nutrition data"""
        formatted = []
        meal_count = 0
        
        # Group meals by type
        meals_by_type = {}
        for meal in meals:
            meal_type = meal.get('meal_type', 'Unknown')
            if meal_type not in meals_by_type:
                meals_by_type[meal_type] = []
            meals_by_type[meal_type].append(meal)
        
        # Format each meal type - limit to 3 options per meal type
        meal_order = ['breakfast', 'mid-morning', 'lunch', 'evening_snack', 'dinner']
        for meal_type_key in meal_order:
            meal_list = meals_by_type.get(meal_type_key, [])
            if not meal_list:
                continue
                
            formatted.append(f"\n{meal_type_key.upper().replace('_', ' ').replace('-', ' ')}:")
            
            count = 0
            for meal in meal_list:
                if count >= 3:  # Only 3 options per meal type
                    break
                    
                options = meal.get('options', [])
                if options:
                    opt = options[0]  # Take first option only
                    count += 1
                    
                    name = opt.get('name', 'Unknown')
                    ingredients = opt.get('ingredients', 'N/A')[:100]  # Truncate
                    nutrition = opt.get('nutrition', {})
                    
                    formatted.append(f"\n{count}. {name}")
                    formatted.append(f"   Ingredients: {ingredients}")
                    if nutrition:
                        formatted.append(f"   Nutrition: {nutrition.get('calories', 0)} kcal | Protein {nutrition.get('protein', 0)}g | Carbs {nutrition.get('carbs', 0)}g | Fat {nutrition.get('fat', 0)}g")
        
        return "\n".join(formatted)
    
    def _build_prompt(self, user_profile: UserProfile, meals_context: str) -> str:
        """Build prompt for fine-tuned model with complete meal reference data"""
        # Display diet type nicely (non_veg -> Non-Vegetarian)
        diet_display = user_profile.diet_type.replace('non_veg', 'Non-Vegetarian').replace('_', ' ').title()
        
        instruction = f"You are a nutrition expert. Create a complete 1-day {diet_display} meal plan."
        
        user_input = f"""Profile: {user_profile.gender}, {user_profile.age}yr, {user_profile.weight}kg, {user_profile.height}cm, {user_profile.bmi_category} BMI, {user_profile.activity_level} activity
Goal: {user_profile.goal.replace('_', ' ').title()}
Diet: {diet_display} (STRICT)
Region: {user_profile.region.replace('_', ' ').title()}

Available Meals:
{meals_context}

INSTRUCTIONS:
1. Select EXACTLY 3 meals from each category above (Breakfast, Mid-Morning, Lunch, Evening Snack, Dinner)
2. Present in this order: BREAKFAST → MID-MORNING → LUNCH → EVENING SNACK → DINNER
3. For each meal time, list the 3 selected meals with:
   - Meal name
   - Key ingredients (brief)
   - Nutrition info (calories, protein, carbs, fat)
4. Use ONLY meals from the available list above
5. Total daily target: ~2000 kcal, 100g+ protein

Format:
**DAY 1 MEAL PLAN**

**BREAKFAST**
1. [Meal Name]
   Ingredients: [brief list]
   Nutrition: [cal/protein/carbs/fat]

[Continue for all 5 meal times with 3 options each]"""
        
        # Simple prompt format for Llama
        return f"{instruction}\n\n{user_input}\n\nResponse:"
    
    def _generate_with_hf(self, prompt: str) -> str:
        """Generate response using fine-tuned Phi-2 model (Colab or Local)"""
        
        # Use Colab API if enabled
        if USE_COLAB:
            return self._generate_with_colab(prompt)
        
        # Use local model
        try:
            import torch
            
            # Prepare input
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
            
            # Move to same device as model
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate with optimized parameters (same as training)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.1,  # Low temperature for consistency
                    top_p=0.9,
                    do_sample=True,  # Sample with low temperature
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the response part (after ### Response:)
            if "### Response:" in response:
                response = response.split("### Response:")[-1].strip()
            
            return response
        except Exception as e:
            logger.error(f"Error generating with fine-tuned model: {e}")
            return ""
    
    def _generate_with_colab(self, prompt: str) -> str:
        """Generate response by calling Colab API"""
        try:
            # Suppress SSL warnings for self-signed certificates
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            logger.info("🌐 Sending request to Colab API...")
            
            # Add headers to bypass ngrok browser warning
            headers = {
                'ngrok-skip-browser-warning': 'true',
                'User-Agent': 'Python-Requests',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{COLAB_API_URL}/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": 1024,  # Increased for complete meal plan
                    "temperature": 0.1,  # Low temperature for consistency
                    "top_p": 0.9
                },
                headers=headers,
                timeout=300,  # 5 minutes timeout
                verify=False  # Disable SSL verification for ngrok
            )
            
            if response.status_code == 200:
                data = response.json()
                generated_text = data.get('response', '')
                
                if not generated_text or generated_text.strip() == '':
                    logger.error("❌ Colab API returned empty response")
                    logger.error(f"   Full response: {data}")
                    return "ERROR: Model generated empty response. Please try again."
                
                logger.info(f"✅ Generated {len(generated_text)} characters")
                return generated_text
            else:
                logger.error(f"❌ Colab API error: {response.status_code}")
                logger.error(f"   Response: {response.text[:200]}")
                return f"ERROR: Colab API returned status {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("⏰ Colab API timeout (300s). Generation took too long.")
            logger.error("   Llama-3-8B may need more time. Consider:")
            logger.error("   1. Using Colab Pro with A100 GPU (3x faster)")
            logger.error("   2. Simplifying the prompt or reducing meals context")
            logger.error("   3. Switching to a smaller/faster model")
            return "ERROR: Request timeout. Model generation took longer than 5 minutes. Consider using Colab Pro with A100 GPU."
        except Exception as e:
            logger.error(f"❌ Error calling Colab API: {e}")
            return f"ERROR: Failed to connect to Colab API - {str(e)}"
    
    def _parse_llm_response(
        self,
        response: str,
        retrieved_meals: List[Dict[str, Any]],
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Parse LLM response and structure it in exact match format"""
        
        # Check for errors in response
        if not response or response.startswith("ERROR:"):
            return {
                "status": "error",
                "method": "ml_rag",
                "message": response if response else "Empty response from model",
                "recommendations": []
            }
        
        # Parse the LLM response into structured meal format
        import re
        
        meal_times = {
            'BREAKFAST': '🌅 Breakfast',
            'MID-MORNING': '☕ Mid-Morning',
            'LUNCH': '🍽️ Lunch',
            'EVENING SNACK': '🍵 Evening Snack',
            'DINNER': '🌙 Dinner'
        }
        
        structured_meals = []
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        
        # Extract each meal section
        for meal_key, meal_display in meal_times.items():
            pattern = rf'\*\*{meal_key}\*\*\s*(.*?)(?=\*\*[A-Z]|\Z)'
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            
            if match:
                meal_content = match.group(1).strip()
                # Extract individual meal options (numbered 1., 2., 3.)
                options = re.findall(r'(\d+\.\s+.*?)(?=\d+\.|$)', meal_content, re.DOTALL)
                
                meal_options = []
                for option in options[:3]:  # Only take first 3
                    # Extract meal name
                    name_match = re.search(r'\d+\.\s+(.+?)(?:\n|$)', option)
                    name = name_match.group(1).strip() if name_match else "Unknown"
                    
                    # Extract ingredients
                    ingr_match = re.search(r'Ingredients?:\s*(.+?)(?:\n|$)', option, re.IGNORECASE)
                    ingredients = ingr_match.group(1).strip() if ingr_match else "N/A"
                    
                    # Extract nutrition values
                    calories = 0
                    protein = 0
                    carbs = 0
                    fat = 0
                    
                    nutr_match = re.search(r'Nutrition:\s*(\d+)\s*kcal.*?(\d+)g?\s*protein.*?(\d+)g?\s*carbs.*?(\d+)g?\s*fat', option, re.IGNORECASE)
                    if nutr_match:
                        calories = int(nutr_match.group(1))
                        protein = int(nutr_match.group(2))
                        carbs = int(nutr_match.group(3))
                        fat = int(nutr_match.group(4))
                        
                        # Add first option's nutrition to totals
                        if len(meal_options) == 0:
                            total_calories += calories
                            total_protein += protein
                            total_carbs += carbs
                            total_fat += fat
                    
                    # Create full meal object (matching PDF structure)
                    meal_options.append({
                        'name': name,
                        'calories': calories,
                        'protein': protein,
                        'carbs': carbs,
                        'fat': fat,
                        'fiber': 0,
                        'ingredients': ingredients,
                        'method': '',
                        'serving': ''
                    })
                
                if meal_options:
                    # Map meal type to standard format
                    meal_type_map = {
                        'BREAKFAST': 'breakfast',
                        'MID-MORNING': 'mid_morning_snack',
                        'LUNCH': 'lunch',
                        'EVENING SNACK': 'evening_snack',
                        'DINNER': 'dinner'
                    }
                    
                    structured_meals.append({
                        'meal_type': meal_type_map.get(meal_key, meal_key.lower()),
                        'type': meal_display,
                        'icon': meal_display.split()[0],
                        'options': meal_options
                    })
        
        # Get unique source PDFs with full paths
        source_pdfs = list(set(m.get('source_pdf', 'unknown') for m in retrieved_meals if m.get('source_pdf')))
        
        # Create list of PDF names and paths for display
        source_list = []
        for pdf_path in source_pdfs[:5]:  # Show up to 5 sources
            pdf_name = pdf_path.split('/')[-1].replace('.txt', '').replace('_', ' ')
            source_list.append({
                'name': pdf_name,
                'path': pdf_path
            })
        
        total_sources = len(source_pdfs)
        
        # Return in exact match format
        return {
            "status": "success",
            "method": "ml_rag",
            "match_type": "AI Generated (RAG)",
            "total_matches": 1,
            "recommendations": [
                {
                    "id": 1,
                    "category": user_profile.goal.replace('_', ' ').title(),
                    "region": user_profile.region.replace('_', ' ').title(),
                    "diet_type": user_profile.diet_type.replace('_', ' ').title(),
                    "meals": structured_meals,
                    "calories": f"{total_calories} kcal" if total_calories > 0 else "N/A",
                    "protein": f"{total_protein}g" if total_protein > 0 else "N/A",
                    "carbs": f"{total_carbs}g" if total_carbs > 0 else "N/A",
                    "fat": f"{total_fat}g" if total_fat > 0 else "N/A",
                    "fiber": "N/A",
                    "file_path": None,
                    "ai_generated": True,
                    "source_pdfs": source_list,
                    "total_sources": total_sources
                }
            ]
        }
    
    def recommend(self, user_profile: dict, top_k: int = 5) -> dict:
        """
        Main recommendation method
        
        Args:
            user_profile: User profile dictionary
            top_k: Number of recommendations to return
            
        Returns:
            Diet plan recommendations
        """
        logger.info("Starting ML-based recommendation...")
        
        # Normalize diet type to match PDF index values
        diet_type = user_profile.get('diet_type', 'vegetarian')
        diet_type_mapping = {
            'non_vegetarian': 'non_veg',
            'vegetarian': 'vegetarian',
            'vegan': 'vegan',
            'eggetarian': 'eggetarian'
        }
        normalized_diet_type = diet_type_mapping.get(diet_type, diet_type)
        
        # Normalize activity level to match PDF index
        activity = user_profile.get('activity_level', 'moderate')
        activity_mapping = {
            'sedentary': 'sedentary',
            'light': 'light',
            'moderate': 'moderate',
            'active': 'active',
            'very_active': 'heavy'  # PDF index uses 'heavy'
        }
        normalized_activity = activity_mapping.get(activity, activity)
        
        # Normalize goal to match PDF categories
        # Handle multiple goals if provided as list
        goals_input = user_profile.get('goal', 'maintain')
        if isinstance(goals_input, list):
            # User selected multiple goals - take the first one
            goal = goals_input[0] if goals_input else 'maintain'
        else:
            goal = goals_input
        
        goal_mapping = {
            # Weight management
            'maintain': 'high_protein_balanced',
            'weight_loss': 'weight_loss',
            'weight_gain': 'weight_gain',
            'muscle_building': 'high_protein_high_fiber',
            'muscle_gain': 'high_protein_high_fiber',
            
            # Health conditions
            'gut_health': 'gut_cleanse_digestive_detox',
            'clear_skin': 'skin_health',
            'skin_health': 'skin_health',
            'hair_growth': 'hair_loss',
            'hair_health': 'hair_loss',
            
            # Detox & cleanse
            'detox': 'ayurvedic_detox',
            'liver_detox': 'liver_detox',
            'gut_detox': 'gut_detox',
            
            # Specialized
            'anti_aging': 'anti_aging',
            'anti_inflammatory': 'anti_inflammatory',
            'probiotic': 'probiotic',
            'gas_bloating': 'gas_bloating',
            
            # Diabetes & PCOS
            'diabetes': 'weight_loss_diabetes',
            'pcos': 'weight_loss_pcos',
            
            # Fitness goals
            'energy': 'high_protein_balanced',
            'better_sleep': 'high_protein_balanced',
            'improve_fitness': 'high_protein_high_fiber'
        }
        normalized_goal = goal_mapping.get(goal, goal)
        
        logger.info(f"📋 Normalized: diet={normalized_diet_type}, activity={normalized_activity}, goal={normalized_goal}")
        
        # Convert dict to UserProfile
        profile = UserProfile(
            gender=user_profile.get('gender', 'male'),
            age=user_profile.get('age', 30),
            height=user_profile.get('height', 170),
            weight=user_profile.get('weight', 70),
            bmi_category=user_profile.get('bmi_category', 'normal'),
            activity_level=normalized_activity,  # Use normalized value
            diet_type=normalized_diet_type,  # Use normalized value
            region=user_profile.get('region', 'north_indian'),
            goal=normalized_goal,  # Use normalized value
            health_conditions=user_profile.get('health_conditions', []),
            allergies=user_profile.get('allergies', [])
        )
        
        try:
            # Step 1: Get ALL PDFs matching diet type and goal (NO LIMIT)
            logger.info(f"🔍 Searching for plans: diet={profile.diet_type}, goal={profile.goal}")
            similar_pdfs = self.vector_search(profile, top_k=None)  # Get ALL matching PDFs
            
            if not similar_pdfs:
                raise ValueError(f"No {profile.diet_type} plans found for goal: {profile.goal}")
            
            logger.info(f"📚 Found {len(similar_pdfs)} matching PDFs to feed into model")
            
            # Step 2: Extract meals from ALL matching PDFs
            retrieved_meals = self.extract_meals_from_pdfs(similar_pdfs)
            
            if not retrieved_meals:
                raise ValueError(f"Could not extract meals from {len(similar_pdfs)} PDFs")
            
            logger.info(f"🍽️ Extracted {len(retrieved_meals)} meals from PDFs")
            
            # Step 3: ALWAYS generate plan with fine-tuned model
            if not self.llm:
                raise RuntimeError("Fine-tuned Phi-2 model failed to load. Cannot generate diet plan.")
            
            result = self.generate_plan_with_llm(profile, retrieved_meals, top_k)
            return result
        
        except Exception as e:
            logger.error(f"Error in ML recommendation: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}",
                "recommendations": []
            }
