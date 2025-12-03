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
from pipeline.models.recommender import Recommender
from pipeline.rules_engine import allowed_categories, validate_plan

app = FastAPI(title="Nutrition Digital Twin API")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
recommender = Recommender()

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

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request, "show_nav": True, "active_page": "profile"})

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
        # Generate sample meal plan
        plan = _generate_sample_meal_plan(date)
    
    return plan

@app.post("/api/meal-plan/generate")
def generate_meal_plan(data: Dict[str, Any]):
    """Generate a 14-day meal plan"""
    profile = load_json_file("profile.json")
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    start_date = datetime.strptime(profile["plan_start_date"], "%Y-%m-%d")
    meal_plans = []
    
    for day in range(14):
        date = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
        plan = _generate_sample_meal_plan(date, day + 1, profile)
        meal_plans.append(plan)
    
    save_json_file("meal_plans.json", meal_plans)
    return {"status": "success", "plans": meal_plans}

@app.post("/api/meal-plan/swap")
def swap_meal(data: Dict[str, Any]):
    """Swap a meal with an alternative"""
    date = data.get("date")
    meal_type = data.get("meal_type")
    
    meal_plans = load_json_file("meal_plans.json") or []
    plan_index = next((i for i, p in enumerate(meal_plans) if p.get("date") == date), None)
    
    if plan_index is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    
    # Get profile for preferences
    profile = load_json_file("profile.json")
    
    # Generate alternative meal respecting dietary preferences
    alternative = _generate_alternative_meal(meal_type, profile)
    meal_plans[plan_index][meal_type] = alternative
    meal_plans[plan_index]["is_adjusted"] = True
    
    save_json_file("meal_plans.json", meal_plans)
    return {"status": "success", "meal": alternative}

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
    """Save comprehensive daily feedback with AI insights"""
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Get profile for context
    profile = load_json_file("profile.json")
    
    # Generate AI insight based on feedback
    ai_insight = _generate_ai_insight(data, profile)
    
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
        "timestamp": datetime.now().isoformat()
    }
    
    if log_index is None:
        feedback_data["meals_eaten"] = {}
        logs.append(feedback_data)
    else:
        logs[log_index].update(feedback_data)
    
    save_json_file("daily_logs.json", logs)
    
    return {
        "status": "success",
        "ai_insight": ai_insight
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
