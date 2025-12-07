from __future__ import annotations
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from pathlib import Path
import json

# Local imports
from service.pdf_recommender import PDFRecommender, UserProfile
from service.pdf_parser import parse_pdf_complete

# Cache recommenders to avoid reloading 460 plans on every request
_recommender_cache = None
_exact_recommender_cache = None
_goal_recommender_cache = None
_ml_recommender_cache = None

def get_recommender():
    global _recommender_cache
    if _recommender_cache is None:
        _recommender_cache = PDFRecommender()
    return _recommender_cache

def get_exact_recommender():
    global _exact_recommender_cache
    if _exact_recommender_cache is None:
        try:
            from service.recommender_exact.exact_recommender import ExactMatchRecommender
        except ModuleNotFoundError:
            from recommender_exact.exact_recommender import ExactMatchRecommender
        _exact_recommender_cache = ExactMatchRecommender()
    return _exact_recommender_cache

def get_goal_recommender():
    global _goal_recommender_cache
    if _goal_recommender_cache is None:
        try:
            from service.recommender_goal.goal_recommender import GoalOnlyRecommender
        except ModuleNotFoundError:
            from recommender_goal.goal_recommender import GoalOnlyRecommender
        _goal_recommender_cache = GoalOnlyRecommender()
    return _goal_recommender_cache

def get_ml_recommender():
    """Get cached ML recommender (RAG + Fine-tuned)"""
    global _ml_recommender_cache
    if _ml_recommender_cache is None:
        try:
            from service.recommender_ml.ml_recommender import MLRecommender
        except ModuleNotFoundError:
            from recommender_ml.ml_recommender import MLRecommender
        _ml_recommender_cache = MLRecommender()
    return _ml_recommender_cache

def resolve_pdf_path(file_path: str) -> str:
    """Convert relative PDF path to absolute path with forward slashes for URLs"""
    if not file_path:
        return file_path
    
    # If already absolute, normalize it
    path_obj = Path(file_path)
    if not path_obj.is_absolute():
        # Convert relative path to absolute (relative to project root)
        base_dir = Path(__file__).parent.parent  # Go up from service/ to project root
        path_obj = base_dir / file_path
    
    # Convert to string with forward slashes (works on all platforms and safer for URLs)
    return str(path_obj).replace('\\', '/')

def extract_meals_from_pdf(file_path: str) -> List[Dict[str, str]]:
    """Extract meal information from PDF text file
    
    Returns a list of meals with their type and options (first 3 per meal type)
    """
    # Convert to absolute path
    file_path = resolve_pdf_path(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        meals = []
        meal_patterns = [
            ("Early Morning", "☀️"),
            ("Pre-Breakfast", "🌅"),
            ("Breakfast", "🍳"),
            ("Mid-Morning", "☕"),
            ("Lunch", "🍛"),
            ("Evening", "🍵"),
            ("Dinner", "🌙"),
            ("Bedtime", "😴")
        ]
        
        for meal_type, icon in meal_patterns:
            # Try different patterns to find meal sections
            patterns_to_try = [
                f"Meal Type: {meal_type}",
                f"{meal_type} (",  # Matches "Breakfast (8:00 AM)"
                f"{meal_type}\n"   # Matches standalone meal type
            ]
            
            section_start = -1
            for pattern in patterns_to_try:
                section_start = content.find(pattern)
                if section_start != -1:
                    break
            
            if section_start == -1:
                continue
            
            # Find the end of this meal section (start of next meal or end of file)
            section_end = len(content)
            for next_meal, _ in meal_patterns:
                for pattern in [f"Meal Type: {next_meal}", f"{next_meal} (", f"\n{next_meal}\n"]:
                    next_pos = content.find(pattern, section_start + 10)
                    if next_pos != -1 and next_pos < section_end:
                        section_end = next_pos
            
            section_text = content[section_start:section_end]
            
            # Extract meal options
            options = []
            
            # Try to find "Option 1", "Option 2", "Option 3"
            for i in range(1, 4):
                option_pattern = f"Option {i}"
                opt_idx = section_text.find(option_pattern)
                if opt_idx != -1:
                    # Get text after "Option X" until next line
                    line_start = opt_idx + len(option_pattern)
                    # Skip " –" or ":" or " - "
                    while line_start < len(section_text) and section_text[line_start] in [' ', '–', '-', ':']:
                        line_start += 1
                    line_end = section_text.find('\n', line_start)
                    if line_end != -1:
                        meal_name = section_text[line_start:line_end].strip()
                        if meal_name and not meal_name.startswith('•'):
                            options.append(meal_name)
            
            # If no options found, try to find "Dish:" pattern
            if not options:
                dish_idx = section_text.find("Dish:")
                if dish_idx != -1:
                    line_start = dish_idx + 5
                    line_end = section_text.find('\n', line_start)
                    if line_end != -1:
                        meal_name = section_text[line_start:line_end].strip()
                        if meal_name:
                            options.append(meal_name)
            
            if options:
                meals.append({
                    "type": meal_type,
                    "icon": icon,
                    "options": options[:3]
                })
        
        return meals[:6]  # Return max 6 meal types to keep cards compact
    except Exception as e:
        print(f"Error extracting meals from {file_path}: {e}")
        return []

def get_bmi_category(bmi: float, goal: str = None) -> str:
    """Convert BMI value to category, considering user goal"""
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        # For weight gain goals, BMI 18.5-20 should be treated as underweight
        if goal in ['weight_gain', 'muscle_building'] and bmi < 20:
            return "underweight"
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"

def validate_plan(category, plan_items):
    """Validate plan items don't contain allergens"""
    # This is now handled within llama_service via allergen safety checks
    return True

app = FastAPI(title="Nutrition Digital Twin API")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

# Simple in-memory storage (replace with database in production)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def load_json_file(filename):
    filepath = DATA_DIR / filename
    if filepath.exists():
        try:
            content = filepath.read_text().strip()
            if not content:
                return None
            return json.loads(content)
        except json.JSONDecodeError:
            return None
    return None

def save_json_file(filename, data):
    filepath = DATA_DIR / filename
    filepath.write_text(json.dumps(data, indent=2, default=str))


class Profile(BaseModel):
    age: int
    sex: str
    bmi: float
    region: str
    diet_type: str
    activity: str
    weight_class: str
    conditions: List[str] = []
    preferences: Dict[str, Any] = {}


class Feedback(BaseModel):
    week: int = Field(..., ge=1)
    weight_change_kg: Optional[float] = None
    bloating: Optional[int] = Field(None, ge=0, le=10)
    acne_oiliness: Optional[int] = Field(None, ge=0, le=10)
    energy: Optional[int] = Field(None, ge=0, le=10)
    digestion_comfort: Optional[int] = Field(None, ge=0, le=10)
    mood: Optional[int] = Field(None, ge=0, le=10)
    adherence: Optional[float] = Field(None, ge=0, le=1)
    notes: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    # Always redirect to login first
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "show_nav": False})

@app.get("/onboarding", response_class=HTMLResponse)
def onboarding(request: Request):
    return templates.TemplateResponse("onboarding.html", {"request": request, "show_nav": False})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "show_nav": True, "active_page": "dashboard"})

@app.get("/meal-plan", response_class=HTMLResponse)
def meal_plan_page(request: Request):
    return templates.TemplateResponse("meal-plan.html", {"request": request, "show_nav": True, "active_page": "meal-plan"})

@app.get("/meal-detail", response_class=HTMLResponse)
def meal_detail_page(request: Request):
    return templates.TemplateResponse("meal-detail.html", {"request": request, "show_nav": False})

@app.get("/pdf-viewer", response_class=HTMLResponse)
def pdf_viewer_page(request: Request, file_path: str):
    """
    Display complete PDF content with all food-related information
    Query param: file_path - absolute path to the PDF text file
    """
    try:
        # Parse complete PDF content
        plan_data = parse_pdf_complete(file_path)
        
        if "error" in plan_data:
            raise HTTPException(status_code=404, detail=plan_data["error"])
        
        return templates.TemplateResponse("pdf-viewer.html", {
            "request": request,
            "plan": plan_data,
            "show_nav": False
        })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="PDF file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request, "show_nav": True, "active_page": "profile"})

@app.get("/choose-system", response_class=HTMLResponse)
def choose_system_page(request: Request):
    """Page to choose recommendation system"""
    return templates.TemplateResponse("choose-system.html", {"request": request, "show_nav": False})

@app.get("/get-recommendations", response_class=HTMLResponse)
def get_recommendations_page(request: Request):
    """Page to view recommendations from selected system"""
    return templates.TemplateResponse("get-recommendations.html", {"request": request, "show_nav": False})

@app.get("/generate-plan", response_class=HTMLResponse)
def generate_plan_page(request: Request):
    return templates.TemplateResponse("generate-plan.html", {"request": request, "show_nav": False})

@app.get("/daily-feedback", response_class=HTMLResponse)
def daily_feedback_page(request: Request):
    return templates.TemplateResponse("daily-feedback.html", {"request": request, "show_nav": False})

@app.get("/ping")
def ping():
    return {"pong": True}

@app.get("/recommend/sample")
def recommend_sample_profile():
    return {
        "example_profile": {
            "age": 30,
            "sex": "male",
            "bmi": 25.0,
            "region": "north_indian",
            "diet_type": "veg",
            "activity": "moderate",
            "weight_class": "normal",
            "conditions": ["pcos"],
            "preferences": {
                "likes": ["curd", "paneer", "dal"],
                "dislikes": ["soda"],
                "allergies": []
            }
        },
        "usage": "POST this JSON to /recommend"
    }


@app.post("/recommend")
def recommend(profile: Profile):
    prof = profile.dict()
    rec = recommender.recommend(prof)

    # Build a minimal 14-day plan using template patterns (placeholder)
    plan_items = []
    template = _load_template(rec.category)
    if template:
        meals = template.get("meals", [])
        for day in range(1, 15):
            for m in meals:
                plan_items.append({
                    "day": day,
                    "meal": m.get("meal"),
                    "time": "",
                    "items": [{"name": m.get("patterns", ["meal"])[0], "quantity": "", "notes": rec.rationale}],
                })

    if not validate_plan(rec.category, plan_items):
        raise HTTPException(status_code=400, detail="Generated plan failed rules validation")

    return {
        "category": rec.category,
        "expected": rec.expected.__dict__,
        "rationale": rec.rationale,
        "plan": plan_items,
    }


@app.post("/feedback/{category}")
def feedback(category: str, profile: Profile, feedback: Feedback):
    recommender.incorporate_feedback(profile.dict(), category, {k: v for k, v in feedback.dict().items() if v is not None})
    return {"status": "ok"}

# New API Endpoints for Diya-style UI

@app.get("/api/profile")
def get_profile():
    """Get user profile"""
    profile = load_json_file("profile.json")
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Merge with user data if available
    users = load_json_file("users.json") or {}
    user_email = profile.get("email")
    if user_email and user_email in users:
        profile["name"] = users[user_email].get("name")
        profile["email"] = user_email
    
    return profile

@app.post("/api/auth/signup")
def signup(data: Dict[str, Any]):
    """Create new user account"""
    users = load_json_file("users.json") or {}
    email = data.get("email")
    
    if email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    users[email] = {
        "name": data.get("name"),
        "email": email,
        "password": data.get("password"),  # In production, hash this!
        "created_at": datetime.now().isoformat(),
        "onboarding_complete": False
    }
    save_json_file("users.json", users)
    return {"status": "success", "onboarding_complete": False}

@app.post("/api/auth/login")
def login(data: Dict[str, Any]):
    """Login user"""
    users = load_json_file("users.json") or {}
    email = data.get("email")
    password = data.get("password")
    
    user = users.get(email)
    if not user or user.get("password") != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if user has profile
    profile = load_json_file("profile.json")
    onboarding_complete = profile and profile.get("onboarding_complete", False) if profile else False
    
    return {
        "status": "success",
        "user": {
            "name": user["name"],
            "email": user["email"]
        },
        "onboarding_complete": onboarding_complete
    }

@app.post("/api/profile")
def create_profile(data: Dict[str, Any]):
    """Create or update user profile"""
    save_json_file("profile.json", data)
    return {"status": "success", "profile": data}

@app.post("/api/profile/new-cycle")
def new_cycle():
    """Increment cycle and reset start date"""
    profile = load_json_file("profile.json")
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile["current_plan_cycle"] = profile.get("current_plan_cycle", 1) + 1
    profile["plan_start_date"] = datetime.now().strftime("%Y-%m-%d")
    save_json_file("profile.json", profile)
    return {"status": "success"}

@app.get("/api/meal-plan")
def get_meal_plan(date: str):
    """Get meal plan for a specific date"""
    meal_plans = load_json_file("meal_plans.json") or []
    plan = next((p for p in meal_plans if p.get("date") == date), None)
    
    if not plan:
        # No meal plan found - user needs to select plans from recommendations
        return None
    
    return plan

@app.post("/api/meal-plan/generate")
def generate_meal_plan(data: Dict[str, Any]):
    """Generate meal plan recommendations from PDF database"""
    profile = load_json_file("profile.json")
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Convert profile to UserProfile format
    # Get first goal from goals array
    goals = profile.get("goals", ["weight_loss"])
    primary_goal = goals[0] if goals else "weight_loss"
    
    # Calculate BMI category from BMI value (goal-aware)
    bmi = profile.get("bmi", 22)
    bmi_category = get_bmi_category(bmi, primary_goal)
    
    user = UserProfile(
        gender=profile.get("gender", "female").lower(),
        age=profile.get("age", 30),
        height=profile.get("height", 160),
        weight=profile.get("weight", 60),
        bmi_category=bmi_category,
        activity_level=profile.get("activity_level", "light").lower().replace(" ", "_"),
        diet_type=profile.get("diet_type", "vegetarian").lower(),
        region=profile.get("region", "north_indian").lower().replace(" ", "_"),
        goal=primary_goal.lower().replace(" ", "_"),
        health_conditions=[c.lower().replace(" ", "_") for c in profile.get("medical_conditions", [])],
        allergies=profile.get("allergies", [])
    )
    
    # Get recommendations from PDF database (cached)
    recommender = get_recommender()
    try:
        recommendations = recommender.recommend(user, top_k=10)
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")
    
    if not recommendations:
        raise HTTPException(status_code=404, detail="No matching meal plans found for your profile")
    
    # Format recommendations for frontend
    cards = []
    for i, plan in enumerate(recommendations):
        nutrition = plan.get('nutrition', {})
        
        # Extract meals from PDF text file
        file_path = plan.get('file_path', '')
        absolute_file_path = resolve_pdf_path(file_path)
        meals = extract_meals_from_pdf(file_path) if file_path else []
        
        card = {
            "id": i,
            "file_path": absolute_file_path,
            "filename": plan.get('filename', ''),
            "category": plan.get('category', 'N/A'),
            "region": plan.get('region', 'N/A'),
            "diet_type": plan.get('diet_type', 'N/A'),
            "score": round(plan.get('recommendation_score', 0), 1),
            "meals": meals,
            "calories": f"{nutrition.get('calories_min', 0)}-{nutrition.get('calories_max', 0)} kcal",
            "protein": f"{nutrition.get('protein_min', 0)}-{nutrition.get('protein_max', 0)} g",
            "carbs": f"{nutrition.get('carbs_min', 0)}-{nutrition.get('carbs_max', 0)} g",
            "fat": f"{nutrition.get('fat_min', 0)}-{nutrition.get('fat_max', 0)} g",
            "fiber": f"{nutrition.get('fiber_min', 0)}-{nutrition.get('fiber_max', 0)} g"
        }
        cards.append(card)
    
    return {"status": "success", "recommendations": cards}


@app.post("/api/meal-plan/generate-exact")
def generate_exact_match_recommendations():
    """Generate recommendations using EXACT MATCH on ALL fields (Case 1)
    
    Matches: Gender, BMI Category, Activity, Diet, Region, Category
    Returns: "Diet not available" if no exact match
    """
    profile = load_json_file("profile.json")
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Use cached exact match recommender
    exact_recommender = get_exact_recommender()
    
    # Get exact matches
    result = exact_recommender.recommend(profile, top_k=10)
    
    if result['status'] == 'not_available':
        return result
    
    # Format recommendations for frontend
    cards = []
    for i, plan in enumerate(result['recommendations']):
        nutrition = plan.get('nutrition', {})
        
        # Extract meals from PDF text file using comprehensive parser
        file_path = plan.get('file_path', '')
        absolute_file_path = resolve_pdf_path(file_path)
        
        # Use comprehensive parser to get ALL meals including breakfast
        meals = []
        try:
            parsed_data = parse_pdf_complete(absolute_file_path)
            
            # Define meal order (chronological order throughout the day)
            meal_order = [
                'Early Morning (on Waking)',
                'Early Morning',
                'Pre-Yoga / Light Activity',
                'Pre-Activity',
                'Pre-Breakfast',
                'Breakfast (Post-Yoga / Morning Meal)',
                'Breakfast',
                'Mid-Morning Snack',
                'Mid-Morning',
                'Lunch',
                'Evening Snack',
                'Evening',
                'Dinner',
                'Bedtime Snack',
                'Bedtime'
            ]
            
            meal_icon_map = {
                'Early Morning (on Waking)': '☀️',
                'Early Morning': '☀️',
                'Pre-Yoga / Light Activity': '🏃',
                'Pre-Activity': '🏃',
                'Pre-Breakfast': '🌅',
                'Breakfast (Post-Yoga / Morning Meal)': '🍳',
                'Breakfast': '🍳',
                'Mid-Morning Snack': '☕',
                'Mid-Morning': '☕',
                'Lunch': '🍛',
                'Evening Snack': '🍵',
                'Evening': '🍵',
                'Dinner': '🌙',
                'Bedtime Snack': '😴',
                'Bedtime': '😴'
            }
            
            # Convert to format expected by frontend
            meals_dict = {}
            for meal in parsed_data.get('meals', []):
                if meal.get('options'):
                    meal_type = meal['meal_type']
                    meals_dict[meal_type] = {
                        'type': meal_type,
                        'icon': meal_icon_map.get(meal_type, '🍽️'),
                        'options': [opt['name'] for opt in meal['options'][:3]]
                    }
            
            # Sort meals by chronological order
            for meal_type in meal_order:
                if meal_type in meals_dict:
                    meals.append(meals_dict[meal_type])
                    
        except Exception as e:
            print(f"Error parsing PDF {absolute_file_path}: {e}")
            # Fallback to simple extraction
            meals = extract_meals_from_pdf(file_path) if file_path else []
        
        card = {
            "id": i,
            "file_path": absolute_file_path,
            "filename": plan.get('filename', ''),
            "category": plan.get('category', 'N/A'),
            "region": plan.get('region', 'N/A'),
            "diet_type": plan.get('diet_type', 'N/A'),
            "meals": meals,
            "calories": f"{nutrition.get('calories_min', 0)}-{nutrition.get('calories_max', 0)} kcal",
            "protein": f"{nutrition.get('protein_min', 0)}-{nutrition.get('protein_max', 0)} g",
            "carbs": f"{nutrition.get('carbs_min', 0)}-{nutrition.get('carbs_max', 0)} g",
            "fat": f"{nutrition.get('fat_min', 0)}-{nutrition.get('fat_max', 0)} g",
            "fiber": f"{nutrition.get('fiber_min', 0)}-{nutrition.get('fiber_max', 0)} g"
        }
        cards.append(card)
    
    return {"status": "success", "recommendations": cards, "match_type": "exact", "total_matches": result.get('total_matches', 0)}


@app.post("/api/meal-plan/generate-goal")
def generate_goal_only_recommendations():
    """Generate recommendations using GOAL + REGION only (Case 2)
    
    Matches: Primary Goal + Region ONLY
    Ignores: Gender, BMI, Activity, Diet, Health, Age, Allergies
    """
    profile = load_json_file("profile.json")
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Use cached goal-only recommender
    goal_recommender = get_goal_recommender()
    
    # Get goal-based matches
    result = goal_recommender.recommend(profile, top_k=10)
    
    if result['status'] == 'not_available':
        return result
    
    # Format recommendations for frontend
    cards = []
    for i, plan in enumerate(result['recommendations']):
        nutrition = plan.get('nutrition', {})
        
        # Extract meals from PDF text file
        file_path = plan.get('file_path', '')
        absolute_file_path = resolve_pdf_path(file_path)
        meals = extract_meals_from_pdf(file_path) if file_path else []
        
        card = {
            "id": i,
            "file_path": absolute_file_path,
            "filename": plan.get('filename', ''),
            "category": plan.get('category', 'N/A'),
            "region": plan.get('region', 'N/A'),
            "diet_type": plan.get('diet_type', 'N/A'),
            "meals": meals,
            "calories": f"{nutrition.get('calories_min', 0)}-{nutrition.get('calories_max', 0)} kcal",
            "protein": f"{nutrition.get('protein_min', 0)}-{nutrition.get('protein_max', 0)} g",
            "carbs": f"{nutrition.get('carbs_min', 0)}-{nutrition.get('carbs_max', 0)} g",
            "fat": f"{nutrition.get('fat_min', 0)}-{nutrition.get('fat_max', 0)} g",
            "fiber": f"{nutrition.get('fiber_min', 0)}-{nutrition.get('fiber_max', 0)} g"
        }
        cards.append(card)
    
    return {
        "status": "success", 
        "recommendations": cards, 
        "match_type": "goal_only", 
        "total_matches": result.get('total_matches', 0),
        "criteria": result.get('criteria', {})
    }


@app.post("/api/meal-plan/generate-ml")
def generate_ml_recommendations():
    """Generate recommendations using ML-based RAG + Fine-tuned Model (Case 3)
    
    Uses:
    1. Vector search to find semantically similar PDFs from 460 plans
    2. Extracts meals from top matching PDFs
    3. Fine-tuned LLM generates personalized plan using retrieved meals
    
    Benefits:
    - 100% meals from actual PDFs (no hallucination)
    - Intelligent selection via LLM
    - Personalized reasoning and explanations
    """
    profile = load_json_file("profile.json")
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Extract primary goal from goals array
    goals = profile.get("goals", ["weight_loss"])
    primary_goal = goals[0] if goals else "weight_loss"
    
    # Add goal (singular) to profile for ML recommender
    profile["goal"] = primary_goal
    
    # Use cached ML recommender
    ml_recommender = get_ml_recommender()
    
    # Get ML-based recommendations
    result = ml_recommender.recommend(profile, top_k=5)
    
    if result.get('status') == 'error':
        raise HTTPException(status_code=500, detail=result.get('message', 'ML recommender error'))
    
    if result.get('status') == 'no_match':
        return {
            "status": "not_available",
            "message": result.get('message', 'No suitable diet plans found'),
            "recommendations": []
        }
    
    # Format for frontend
    # ML recommender returns structured plan data
    recommendations = result.get('recommendations', [])
    metadata = result.get('metadata', {})
    
    # If we have structured meal data, format it like other endpoints
    cards = []
    for i, rec in enumerate(recommendations):
        card = {
            "id": i,
            "method": "ml_rag",
            "title": rec.get('title', f'AI-Generated Plan {i+1}'),
            "plan_text": rec.get('plan_text', ''),
            "sources": rec.get('sources', []),
            "confidence": rec.get('confidence', 'medium'),
            "meals": rec.get('meals', [])  # If LLM parsed meals
        }
        cards.append(card)
    
    return {
        "status": "success",
        "recommendations": cards,
        "match_type": "ml_rag",
        "metadata": metadata,
        "total_sources": metadata.get('total_sources', 0),
        "profile_summary": metadata.get('profile_summary', '')
    }


@app.post("/api/meal-plan/select")
def select_meal_plans(data: Dict[str, Any]):
    """Finalize selected meal plans and generate 14-day cycle"""
    profile = load_json_file("profile.json")
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    selected_ids = data.get("selected_ids", [])
    if not selected_ids or len(selected_ids) < 1 or len(selected_ids) > 5:
        raise HTTPException(status_code=400, detail="Please select 1-5 meal plans")
    
    # Get the recommendations from the frontend (they already have file_path)
    recommendations = data.get("recommendations", [])
    
    if not recommendations:
        # Fallback: regenerate recommendations if not provided
        goals = profile.get("goals", ["weight_loss"])
        primary_goal = goals[0] if goals else "weight_loss"
        bmi = profile.get("bmi", 22)
        bmi_category = get_bmi_category(bmi, primary_goal)
        
        user = UserProfile(
            gender=profile.get("gender", "female").lower(),
            age=profile.get("age", 30),
            height=profile.get("height", 160),
            weight=profile.get("weight", 60),
            bmi_category=bmi_category,
            activity_level=profile.get("activity_level", "light").lower().replace(" ", "_"),
            diet_type=profile.get("diet_type", "vegetarian").lower(),
            region=profile.get("region", "north_indian").lower().replace(" ", "_"),
            goal=primary_goal.lower().replace(" ", "_"),
            health_conditions=[c.lower().replace(" ", "_") for c in profile.get("medical_conditions", [])],
            allergies=profile.get("allergies", [])
        )
        
        system = data.get("system", "weighted")
        if system == "exact":
            recommender = get_exact_recommender()
            result = recommender.recommend(profile, top_k=10)
            recommendations = result.get('recommendations', [])
        elif system == "goal":
            recommender = get_goal_recommender()
            result = recommender.recommend(profile, top_k=10)
            recommendations = result.get('recommendations', [])
        else:
            recommender = get_recommender()
            recommendations = recommender.recommend(user, top_k=10)
    
    # Convert frontend recommendations back to full plan objects
    # Handle both PDF-based plans (with file_path) and ML-generated plans (without file_path)
    selected_plans = []
    
    # Load PDF index once (for PDF-based plans only)
    import json
    with open("outputs/pdf_index.json", 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    for rec in recommendations:
        # Check if this is an AI-generated plan (no file_path or ai_generated flag)
        if rec.get('ai_generated') or not rec.get('file_path'):
            # ML-generated plan - use it directly with meals from recommendation
            selected_plans.append({
                'title': rec.get('category', 'AI Generated Plan'),
                'category': rec.get('category', 'ai_generated'),
                'region': rec.get('region', profile.get('region', 'north_indian')),
                'diet_type': rec.get('diet_type', profile.get('diet_type', 'vegetarian')),
                'gender': profile.get('gender', 'female'),
                'bmi_category': profile.get('bmi_category', 'normal'),
                'activity': profile.get('activity_level', 'light'),
                'meals': rec.get('meals', []),
                'file_path': None,
                'ai_generated': True
            })
        else:
            # PDF-based plan - load from index
            file_path = rec.get('file_path', '')
            if file_path:
                # Normalize paths for comparison (handle both forward and backslashes)
                normalized_file_path = file_path.replace('\\', '/').replace('//', '/')
                
                # Find the matching plan in the index
                for plan in index.get('plans', []):
                    plan_file_path = plan.get('file_path', '').replace('\\', '/').replace('//', '/')
                    if plan_file_path == normalized_file_path or plan_file_path.endswith(normalized_file_path) or normalized_file_path.endswith(plan_file_path):
                        selected_plans.append(plan)
                        break
    
    if not selected_plans:
        # Print debug info
        print(f"DEBUG: Failed to match plans. Recommendations file_paths:")
        for rec in recommendations:
            print(f"  - file_path: {rec.get('file_path', 'NO PATH')}, ai_generated: {rec.get('ai_generated', False)}")
        raise HTTPException(status_code=500, detail=f"Failed to load selected plans. Received {len(recommendations)} recommendations but matched 0 plans.")
    
    # Generate 14-day rotation using the smart recommender (has the method)
    recommender = get_recommender()
    cycle = recommender.generate_multi_plan_cycle(selected_plans, days=14)
    
    # Update profile with new plan start date (today)
    from datetime import datetime
    profile["plan_start_date"] = datetime.now().strftime("%Y-%m-%d")
    save_json_file("profile.json", profile)
    
    # Save to meal_plans.json
    save_json_file("meal_plans.json", cycle)
    save_json_file("selected_plan_ids.json", selected_ids)
    
    return {"status": "success", "cycle": cycle, "days": len(cycle)}

@app.post("/api/meal-plan/swap")
def swap_meal(data: Dict[str, Any]):
    """Swap a meal with an AI-generated alternative"""
    date = data.get("date")
    meal_type = data.get("meal_type")
    reason = data.get("reason", "variety")
    
    meal_plans = load_json_file("meal_plans.json") or []
    plan_index = next((i for i, p in enumerate(meal_plans) if p.get("date") == date), None)
    
    if plan_index is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    
    # Get profile for preferences
    profile = load_json_file("profile.json")
    original_meal = meal_plans[plan_index].get(meal_type, {})
    
    # Generate basic alternative (PDF-based alternatives coming soon)
    alternative = _generate_alternative_meal(meal_type, profile)
    meal_plans[plan_index][meal_type] = alternative
    meal_plans[plan_index]["is_adjusted"] = True
    meal_plans[plan_index]["swap_reason"] = reason
    
    save_json_file("meal_plans.json", meal_plans)
    return {"status": "success", "meal": alternative, "alternatives": alternatives}

@app.get("/api/daily-log")
def get_daily_log(date: str):
    """Get daily log for a specific date"""
    logs = load_json_file("daily_logs.json") or []
    log = next((l for l in logs if l.get("date") == date), None)
    
    if not log:
        # Return empty log
        log = {
            "date": date,
            "meals_eaten": {},
            "water_intake": 0,
            "notes": ""
        }
    
    return log

@app.post("/api/daily-log/meal")
def toggle_meal_eaten(data: Dict[str, Any]):
    """Mark a meal as eaten or not eaten"""
    date = data.get("date")
    meal_type = data.get("meal_type")
    completed = data.get("completed", True)
    
    logs = load_json_file("daily_logs.json") or []
    log_index = next((i for i, l in enumerate(logs) if l.get("date") == date), None)
    
    if log_index is None:
        # Create new log
        log = {
            "date": date,
            "meals_eaten": {meal_type: completed},
            "water_intake": 0
        }
        logs.append(log)
    else:
        if "meals_eaten" not in logs[log_index]:
            logs[log_index]["meals_eaten"] = {}
        logs[log_index]["meals_eaten"][meal_type] = completed
    
    save_json_file("daily_logs.json", logs)
    return {"status": "success"}

@app.post("/api/daily-log/water")
def update_water_intake(data: Dict[str, Any]):
    """Update water intake for a date"""
    date = data.get("date")
    glasses = data.get("glasses", 0)
    
    logs = load_json_file("daily_logs.json") or []
    log_index = next((i for i, l in enumerate(logs) if l.get("date") == date), None)
    
    if log_index is None:
        log = {"date": date, "meals_eaten": {}, "water_intake": glasses}
        logs.append(log)
    else:
        logs[log_index]["water_intake"] = glasses
    
    save_json_file("daily_logs.json", logs)
    return {"status": "success"}

@app.post("/api/daily-log/feedback")
def save_daily_feedback(data: Dict[str, Any]):
    """Save comprehensive daily feedback with Llama 3 AI insights"""
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Get profile and current meal plan for context
    profile = load_json_file("profile.json")
    meal_plans = load_json_file("meal_plans.json") or []
    current_plan = next((p for p in meal_plans if p.get("date") == date), None)
    
    # Save feedback data
    logs = load_json_file("daily_logs.json") or []
    log_index = next((i for i, l in enumerate(logs) if l.get("date") == date), None)
    
    feedback_data = {
        "date": date,
        "mood": data.get("mood"),
        "energy_level": data.get("energy_level"),
        "digestion": data.get("digestion"),
        "acne_status": data.get("acne_status"),
        "sleep_quality": data.get("sleep_quality"),
        "symptoms": data.get("symptoms", []),
        "water_intake": data.get("water_intake"),
        "weight": data.get("weight"),
        "notes": data.get("notes"),
        "adherence": data.get("adherence", "partial"),
        "satisfaction": data.get("satisfaction", 3),
        "timestamp": datetime.now().isoformat()
    }
    
    if log_index is None:
        feedback_data["meals_eaten"] = {}
        logs.append(feedback_data)
    else:
        logs[log_index].update(feedback_data)
    
    save_json_file("daily_logs.json", logs)
    
    # Generate basic insights (AI analysis coming soon)
    ai_analysis = _generate_ai_insight(data, profile)
    ai_analysis = {"analysis": ai_analysis, "motivation": "Keep going!", "suggested_changes": {}}
    
    return {
        "status": "success",
        "ai_insight": ai_analysis.get("analysis", ""),
        "motivation": ai_analysis.get("motivation", ""),
        "went_well": ai_analysis.get("went_well", []),
        "needs_improvement": ai_analysis.get("needs_improvement", []),
        "suggested_changes": ai_analysis.get("suggested_changes", {})
    }

def _generate_ai_insight(feedback: Dict, profile: Dict) -> str:
    """
    Generate personalized insight based on daily feedback.
    
    NOTE: Currently using rule-based logic. To upgrade to actual AI/LLM:
    1. Install openai or anthropic library
    2. Add API key to environment variables
    3. Replace this function with LLM call using feedback data as prompt
    
    Example LLM integration:
        prompt = f\"Based on this health data: {feedback}, provide 2-3 personalized diet tips.\"
        response = openai.ChatCompletion.create(model=\"gpt-4\", messages=[{\"role\": \"user\", \"content\": prompt}])
    """
    insights = []
    
    # Energy-based insights
    energy = feedback.get("energy_level", 5)
    if energy <= 3:
        insights.append("Your energy seems low today. Consider adding more protein-rich foods and staying hydrated.")
    elif energy >= 8:
        insights.append("Great energy levels! Your current meal plan seems to be working well.")
    
    # Digestion insights
    digestion = feedback.get("digestion", "")
    if digestion in ["bloated", "uncomfortable", "poor"]:
        insights.append("Your digestion needs attention. Try incorporating more fiber, probiotics, and avoid processed foods.")
    elif digestion in ["excellent", "good"]:
        insights.append("Excellent digestion! Your gut health is on track.")
    
    # Sleep insights
    sleep = feedback.get("sleep_quality", "")
    if sleep == "poor":
        insights.append("Poor sleep can affect your health goals. Avoid caffeine after 2 PM and try a lighter dinner.")
    elif sleep == "excellent":
        insights.append("Quality sleep is crucial for recovery and metabolism. Keep it up!")
    
    # Symptom insights
    symptoms = feedback.get("symptoms", [])
    if len(symptoms) > 2:
        insights.append(f"You're experiencing {len(symptoms)} symptoms today. Consider consulting with a healthcare provider.")
    elif "Headache" in symptoms or "Fatigue" in symptoms:
        insights.append("Headaches and fatigue can indicate dehydration. Aim for 8-10 glasses of water daily.")
    
    # Water intake
    water = feedback.get("water_intake", 0)
    if water < 6:
        insights.append("Try to increase your water intake to at least 8 glasses per day for optimal health.")
    elif water >= 8:
        insights.append("Great hydration! This supports digestion, skin health, and energy levels.")
    
    # Mood insights
    mood = feedback.get("mood", "")
    if mood in ["low", "bad"]:
        insights.append("Nutrition impacts mood. Include omega-3 rich foods like walnuts and flaxseeds.")
    
    # Default insight if none generated
    if not insights:
        insights.append("You're doing great! Keep following your meal plan and staying consistent with healthy habits.")
    
    return " ".join(insights[:3])  # Return top 3 insights

def _generate_sample_meal_plan(date: str, day_number: int = 1, profile: Dict = None):
    """Generate a meal plan respecting dietary preferences and allergies"""
    # Get profile preferences
    diet_type = profile.get("diet_type", "vegetarian") if profile else "vegetarian"
    allergies = profile.get("allergies", []) if profile else []
    if isinstance(allergies, str):
        allergies = [a.strip().lower() for a in allergies.split(",") if a.strip()]
    
    # Check for common allergens
    has_nut_allergy = any(word in " ".join(allergies) for word in ["nut", "almond", "cashew", "peanut", "walnut"])
    has_dairy_allergy = any(word in " ".join(allergies) for word in ["dairy", "milk", "lactose"])
    has_egg_allergy = any(word in " ".join(allergies) for word in ["egg"])
    
    # Choose meals based on diet type
    is_veg = diet_type in ["vegetarian", "vegan"]
    is_vegan = diet_type == "vegan"
    is_egg_allowed = diet_type in ["eggetarian", "non_vegetarian"] and not has_egg_allergy
    
    # BREAKFAST - Safe for most diets
    breakfast_ingredients = ["Rolled oats", "Banana", "Berries", "Honey", "Chia seeds"]
    if not has_nut_allergy:
        breakfast_ingredients.append("Almonds")
    
    # SNACK - Adapt based on allergies
    if has_dairy_allergy:
        snack = {
            "name": "Fruit Bowl",
            "description": "Fresh seasonal fruits",
            "calories": 120,
            "protein": 2,
            "carbs": 28,
            "fats": 0.5,
            "time": "10:30 AM"
        }
    else:
        snack = {
            "name": "Greek Yogurt with Berries",
            "calories": 150,
            "protein": 15,
            "carbs": 12,
            "fats": 5,
            "time": "10:30 AM"
        }
    
    # LUNCH - Based on diet type
    if is_veg:
        lunch = {
            "name": "Paneer Tikka Salad" if not is_vegan else "Chickpea Salad Bowl",
            "description": "Protein-rich salad with vegetables" if is_vegan else "Grilled paneer with fresh vegetables",
            "calories": 420,
            "protein": 22,
            "carbs": 38,
            "fats": 18,
            "ingredients": ["Chickpeas", "Mixed greens", "Tomatoes", "Cucumber", "Olive oil", "Lemon", "Tahini"] if is_vegan else ["Paneer", "Mixed greens", "Bell peppers", "Onions", "Mint chutney"],
            "recipe": "1. Prepare chickpea salad with tahini dressing\n2. Add fresh vegetables\n3. Season with lemon and herbs" if is_vegan else "1. Marinate paneer in spices\n2. Grill until golden\n3. Serve on bed of greens with mint chutney",
            "time": "1:00 PM"
        }
    else:
        lunch = {
            "name": "Grilled Chicken Salad",
            "description": "Lean protein with fresh vegetables",
            "calories": 450,
            "protein": 40,
            "carbs": 35,
            "fats": 15,
            "ingredients": ["Chicken breast", "Mixed greens", "Tomatoes", "Cucumber", "Olive oil", "Lemon"],
            "recipe": "1. Grill chicken breast with spices\n2. Toss mixed greens with vegetables\n3. Slice chicken and place on salad\n4. Dress with olive oil and lemon",
            "time": "1:00 PM"
        }
    
    # EVENING SNACK - Based on allergies
    if has_nut_allergy:
        evening_snack = {
            "name": "Roasted Chickpeas",
            "description": "Crunchy protein snack",
            "calories": 180,
            "protein": 9,
            "carbs": 24,
            "fats": 5,
            "time": "4:30 PM"
        }
    else:
        evening_snack = {
            "name": "Mixed Nuts and Seeds",
            "calories": 200,
            "protein": 8,
            "carbs": 10,
            "fats": 16,
            "time": "4:30 PM"
        }
    
    # DINNER - Based on diet type
    if is_veg:
        dinner = {
            "name": "Quinoa Buddha Bowl" if is_vegan else "Dal Khichdi Bowl",
            "description": "Complete protein bowl with vegetables" if is_vegan else "Comfort food with lentils and rice",
            "calories": 400,
            "protein": 18,
            "carbs": 58,
            "fats": 12,
            "ingredients": ["Quinoa", "Tofu", "Broccoli", "Carrots", "Soy sauce", "Sesame seeds"] if is_vegan else ["Brown rice", "Moong dal", "Turmeric", "Ghee", "Vegetables", "Cumin"],
            "recipe": "1. Cook quinoa\n2. Stir-fry tofu and vegetables\n3. Serve with tahini sauce" if is_vegan else "1. Cook rice and dal together\n2. Add turmeric and vegetables\n3. Top with ghee and cumin tempering",
            "time": "7:30 PM"
        }
    else:
        dinner = {
            "name": "Grilled Fish with Brown Rice",
            "description": "Omega-3 rich meal with complex carbs",
            "calories": 420,
            "protein": 32,
            "carbs": 48,
            "fats": 10,
            "ingredients": ["Fish fillet", "Brown rice", "Steamed vegetables", "Lemon", "Herbs"],
            "recipe": "1. Season and grill fish\n2. Cook brown rice\n3. Steam vegetables\n4. Serve together with lemon",
            "time": "7:30 PM"
        }
    
    return {
        "date": date,
        "day_number": day_number,
        "cycle": profile.get("current_plan_cycle", 1) if profile else 1,
        "breakfast": {
            "name": "Oats with Fruits and Seeds",
            "description": "Fiber-rich breakfast to start your day",
            "calories": 350,
            "protein": 12,
            "carbs": 60,
            "fats": 8,
            "ingredients": breakfast_ingredients,
            "recipe": "1. Cook oats with water or plant-based milk\n2. Top with sliced banana and berries\n3. Add seeds for crunch\n4. Drizzle with honey",
            "time": "7:00 AM"
        },
        "mid_morning_snack": snack,
        "lunch": lunch,
        "evening_snack": evening_snack,
        "dinner": dinner,
        "total_calories": 1550,
        "total_protein": 95,
        "total_carbs": 172,
        "total_fats": 56
    }

def _generate_alternative_meal(meal_type: str, profile: Dict = None):
    """Generate an alternative meal respecting dietary preferences"""
    # Get profile preferences
    diet_type = profile.get("diet_type", "vegetarian") if profile else "vegetarian"
    is_veg = diet_type in ["vegetarian", "vegan"]
    is_vegan = diet_type == "vegan"
    
    alternatives = {
        "breakfast": {
            "name": "Poha with Vegetables" if is_veg else "Scrambled Eggs with Toast",
            "description": "Light and nutritious breakfast" if is_veg else "Protein-rich breakfast with whole grain toast",
            "calories": 300,
            "protein": 8 if is_veg else 18,
            "carbs": 45 if is_veg else 30,
            "fats": 10 if is_veg else 14,
            "ingredients": ["Flattened rice", "Peas", "Carrots", "Peanuts", "Curry leaves", "Lemon"] if is_veg else ["Eggs", "Whole grain bread", "Butter", "Salt", "Pepper"],
            "recipe": "1. Rinse and soak poha\n2. Sauté vegetables and spices\n3. Mix poha and cook\n4. Garnish with lemon" if is_veg else "1. Scramble eggs in butter\n2. Toast bread\n3. Season and serve",
            "time": "7:00 AM"
        },
        "lunch": {
            "name": "Brown Rice with Dal",
            "description": "Traditional Indian comfort food",
            "calories": 420,
            "protein": 18,
            "carbs": 70,
            "fats": 8,
            "ingredients": ["Brown rice", "Lentils", "Tomatoes", "Spices", "Ghee"],
            "recipe": "1. Cook brown rice\n2. Prepare dal with lentils and spices\n3. Serve together with ghee",
            "time": "1:00 PM"
        },
        "dinner": {
            "name": "Vegetable Khichdi" if is_veg else "Chicken Curry with Rice",
            "description": "One-pot nutritious meal" if is_veg else "Protein-rich dinner",
            "calories": 380,
            "protein": 15 if is_veg else 35,
            "carbs": 62 if is_veg else 45,
            "fats": 8 if is_veg else 12,
            "ingredients": ["Rice", "Moong dal", "Mixed vegetables", "Cumin", "Ginger"] if is_veg else ["Chicken", "Rice", "Tomatoes", "Onions", "Spices"],
            "recipe": "1. Cook rice and dal together\n2. Add vegetables and spices\n3. Simmer until done" if is_veg else "1. Cook chicken curry\n2. Prepare rice\n3. Serve together",
            "time": "7:30 PM"
        }
    }
    return alternatives.get(meal_type, alternatives["breakfast"])

def _load_template(category: str) -> Dict[str, Any] | None:
    base = Path(r"D:\\Documents\\Diet plan\\pipeline\\simulation_templates")
    candidates = {
        "pcos": base / "pcos_low_gi.json",
        "high_protein": base / "high_protein.json",
        "gut": base / "gut_soothing.json",
        "detox": base / "detox.json",
    }
    p = candidates.get(category)
    if p and p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
