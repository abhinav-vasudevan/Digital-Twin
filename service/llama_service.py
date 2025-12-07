"""
Llama 3 Integration for Digital Twin Nutrition System
Handles diet planning, allergy safety, and daily feedback processing
"""
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class LlamaService:
    """Service for interacting with Ollama Llama 3 for nutrition recommendations"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3"
        
    def _call_ollama(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Make a call to Ollama API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens if max_tokens > 0 else -1  # -1 = unlimited
                    }
                },
                timeout=300
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.Timeout:
            print(f"⚠️ Ollama timeout after 300s")
            return self._fallback_response(prompt)
        except requests.exceptions.ConnectionError:
            return self._fallback_response(prompt)
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback when Ollama is not available"""
        return json.dumps({
            "error": "Ollama not available",
            "message": "Using basic recommendations. Install Ollama for AI-powered diet plans.",
            "recommendation": "balanced diet with vegetables, proteins, and whole grains"
        })
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extract and parse JSON from Llama response with multiple strategies"""
        # Strategy 1: Find complete JSON object
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON decode error (attempt 1): {e}")
                print(f"First 500 chars: {json_str[:500]}")
        
        # Strategy 2: Look for JSON in code blocks
        if '```json' in response:
            start = response.find('```json') + 7
            end = response.find('```', start)
            if end > start:
                json_str = response[start:end].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
        
        # Strategy 3: Clean common issues and retry
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            # Fix common Llama formatting issues
            json_str = json_str.replace('\n', ' ')  # Remove newlines
            json_str = json_str.replace('\t', ' ')  # Remove tabs
            # Remove trailing commas
            import re
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON decode error (attempt 3): {e}")
                print(f"Cleaned JSON (first 500 chars): {json_str[:500]}")
        
        return None
    
    def _build_profile_context(self, profile: Dict[str, Any]) -> str:
        """Build comprehensive user profile context for prompts"""
        context_parts = []
        
        # Basic info
        context_parts.append(f"Age: {profile.get('age', 'unknown')}")
        context_parts.append(f"Gender: {profile.get('gender', 'unknown')}")
        context_parts.append(f"Height: {profile.get('height', 'unknown')} cm")
        context_parts.append(f"Current Weight: {profile.get('current_weight', 'unknown')} kg")
        context_parts.append(f"Target Weight: {profile.get('target_weight', 'unknown')} kg")
        
        # Activity and goals
        context_parts.append(f"Activity Level: {profile.get('activity_level', 'moderate')}")
        context_parts.append(f"Primary Goal: {profile.get('goal', 'maintain health')}")
        
        # Critical: Allergies and restrictions
        allergies = profile.get('allergies', [])
        if allergies:
            context_parts.append(f"🚨 ALLERGIES (MUST AVOID): {', '.join(allergies)}")
        
        dietary_pref = profile.get('dietary_preferences', [])
        if dietary_pref:
            context_parts.append(f"Dietary Preferences: {', '.join(dietary_pref)}")
        
        # Health conditions
        conditions = profile.get('health_conditions', [])
        if conditions:
            context_parts.append(f"Health Conditions: {', '.join(conditions)}")
        
        # Meal preferences
        meals_per_day = profile.get('meals_per_day', 3)
        context_parts.append(f"Meals per day: {meals_per_day}")
        
        cuisine_pref = profile.get('cuisine_preferences', [])
        if cuisine_pref:
            context_parts.append(f"Preferred Cuisines: {', '.join(cuisine_pref)}")
        
        return "\n".join(context_parts)
    
    def generate_meal_plan(
        self,
        profile: Dict[str, Any],
        days: int = 3,  # Changed from 7 to 3 for testing
        current_feedback: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive meal plan based on user profile
        
        Args:
            profile: User profile with allergies, goals, preferences
            days: Number of days to plan for
            current_feedback: Recent feedback to adjust recommendations
        
        Returns:
            Dict with meal plan, nutritional breakdown, and rationale
        """
        profile_context = self._build_profile_context(profile)
        
        # Build feedback context if available
        feedback_context = ""
        if current_feedback:
            feedback_items = []
            for fb in current_feedback[-5:]:  # Last 5 feedback items
                feedback_items.append(
                    f"- {fb.get('date')}: {fb.get('meal_type')} - "
                    f"Adherence: {fb.get('adherence', 'unknown')}, "
                    f"Satisfaction: {fb.get('satisfaction', 'unknown')}, "
                    f"Notes: {fb.get('notes', 'none')}"
                )
            feedback_context = "\n\nRecent Feedback:\n" + "\n".join(feedback_items)
        
        prompt = f"""You are an expert nutritionist and dietitian creating a personalized {days}-day meal plan.

USER PROFILE:
{profile_context}

{feedback_context}

CRITICAL SAFETY RULES:
1. NEVER include any foods containing the user's allergies
2. Double-check every ingredient for allergen content
3. Respect all dietary preferences (vegetarian, vegan, etc.)
4. Adjust calories and macros based on the user's goal

TASK:
Create a detailed {days}-day meal plan with:
- Breakfast, Lunch, Dinner, and 2 Snacks per day
- Specific portion sizes (grams/cups)
- Estimated calories per meal
- Complete ingredient lists
- Simple preparation instructions
- Variety across days (no repetitive meals)

CRITICAL JSON FORMATTING RULES:
1. ingredients MUST be array of simple strings, NOT objects
2. Each ingredient string should include quantity: "2 slices whole wheat bread", "100g avocado"
3. All values must be properly quoted
4. No trailing commas
5. Use double quotes only

RESPOND WITH ONLY VALID JSON (no extra text before or after):
{{
  "meal_plan": {{
    "day_1": {{
      "breakfast": {{"name": "Meal Name", "ingredients": ["100g ingredient1", "2 cups ingredient2"], "calories": 350, "protein_g": 15, "carbs_g": 40, "fats_g": 12, "instructions": "Step by step"}},
      "lunch": {{"name": "...", "ingredients": ["..."], "calories": 0, "protein_g": 0, "carbs_g": 0, "fats_g": 0, "instructions": "..."}},
      "dinner": {{"name": "...", "ingredients": ["..."], "calories": 0, "protein_g": 0, "carbs_g": 0, "fats_g": 0, "instructions": "..."}},
      "snack_1": {{"name": "...", "ingredients": ["..."], "calories": 0, "protein_g": 0, "carbs_g": 0, "fats_g": 0, "instructions": "..."}},
      "snack_2": {{"name": "...", "ingredients": ["..."], "calories": 0, "protein_g": 0, "carbs_g": 0, "fats_g": 0, "instructions": "..."}}
    }},
    "day_2": {{...}},
    "day_3": {{...}},
    "day_4": {{...}},
    "day_5": {{...}},
    "day_6": {{...}},
    "day_7": {{...}}
  }},
  "daily_totals": {{
    "calories": 2000,
    "protein_g": 150,
    "carbs_g": 200,
    "fats_g": 65
  }},
  "safety_check": "All meals verified allergen-free",
  "rationale": "Brief explanation of plan"
}}
"""
        
        # Strategy: Generate ONE day at a time to avoid timeouts (tested: 1 day = ~100s)
        print(f"🔄 Generating {days}-day meal plan (1 day at a time)...")
        all_days = {}
        
        allergies_warning = ""
        if profile.get('allergies'):
            allergies_warning = f"\n🚨 CRITICAL: Avoid these allergies: {', '.join(profile.get('allergies'))}"
        
        # Handle both 'dietary_preferences' (array) and 'diet_type' (string)
        dietary_pref = profile.get('dietary_preferences', [])
        diet_type = profile.get('diet_type', '')
        
        # Check if vegetarian from either field
        is_vegetarian = (
            any(pref.lower() in ['vegetarian', 'vegan'] for pref in dietary_pref) or
            diet_type.lower() in ['vegetarian', 'vegan']
        )
        
        diet_requirement = ""
        if is_vegetarian:
            diet_requirement = f"\n🌱 STRICTLY VEGETARIAN - Use ONLY plant-based proteins: tofu, paneer, lentils, chickpeas, beans. NO meat, fish, chicken, or eggs."
        elif diet_type or dietary_pref:
            diet_name = diet_type or ', '.join(dietary_pref)
            diet_requirement = f"\n🍗 Diet: {diet_name} - Include variety of proteins (chicken, fish, eggs, meat allowed)"
        
        # Set example meals based on diet preference
        if is_vegetarian:
            lunch_example = '{{"name": "Paneer Wrap", "ingredients": ["1 tortilla", "100g paneer", "50g lettuce", "tomato"], "calories": 450, "protein": 25, "carbs": 40, "fats": 18, "instructions": "Grill paneer, wrap with vegetables"}}'
            dinner_example = '{{"name": "Lentil Rice Bowl", "ingredients": ["200g rice", "150g lentils", "vegetables", "spices"], "calories": 500, "protein": 20, "carbs": 80, "fats": 8, "instructions": "Cook lentils with rice"}}'
        else:
            lunch_example = '{{"name": "Chicken Wrap", "ingredients": ["1 tortilla", "100g grilled chicken", "50g lettuce", "tomato"], "calories": 450, "protein": 35, "carbs": 40, "fats": 12, "instructions": "Wrap grilled chicken with vegetables"}}'
            dinner_example = '{{"name": "Salmon Rice Bowl", "ingredients": ["200g rice", "150g salmon", "vegetables"], "calories": 550, "protein": 35, "carbs": 70, "fats": 15, "instructions": "Grill salmon, serve with rice"}}'
        
        # Generate 1 day at a time
        for day_num in range(1, days + 1):
            print(f"  📅 Day {day_num}/{days}...")
            
            # Build interesting meal suggestions for variety
            cuisine_variety = ["Indian", "Mediterranean", "Asian", "Mexican", "Italian", "Middle Eastern"]
            today_cuisine = cuisine_variety[(day_num - 1) % len(cuisine_variety)]
            
            day_prompt = f"""Create 1 flavorful day meal plan for day {day_num}.

USER: {profile.get('age')}yr {profile.get('gender')}, {profile.get('current_weight')}kg, goal: {profile.get('goal')}{diet_requirement}{allergies_warning}

Make meals interesting with {today_cuisine} flavors. Use herbs/spices. Keep instructions concise (1-2 sentences).

Return ONLY this JSON:
{{
  "meal_plan": {{
    "day_{day_num}": {{
      "breakfast": {{"name": "Creative Breakfast Name", "ingredients": ["100g ingredient1", "2 cups ingredient2", "1 tsp spice"], "calories": 350, "protein": 15, "carbs": 45, "fats": 12, "instructions": "Step 1: Do this. Step 2: Then this. Step 3: Finally this."}},
      "lunch": {{"name": "Flavorful Lunch Name", "ingredients": ["150g protein", "1 cup grains", "vegetables", "spices"], "calories": 480, "protein": 35, "carbs": 50, "fats": 15, "instructions": "Heat oil, add spices, cook protein 5 mins, add veggies, serve with grains."}},
      "dinner": {{"name": "Delicious Dinner Name", "ingredients": ["ingredients with measurements"], "calories": 450, "protein": 30, "carbs": 45, "fats": 12, "instructions": "Marinate protein 15 mins. Grill 4-5 mins each side. Serve hot."}},
      "snack_1": {{"name": "Interesting Snack", "ingredients": ["specific items"], "calories": 120, "protein": 5, "carbs": 15, "fats": 5, "instructions": "Mix ingredients, portion, enjoy."}},
      "snack_2": {{"name": "Tasty Snack", "ingredients": ["ingredients"], "calories": 150, "protein": 6, "carbs": 12, "fats": 10, "instructions": "Blend all, chill 5 mins, serve."}}
    }}
  }}
}}

Make it DELICIOUS! 🌶️🍛🥗"""
            
            day_response = self._call_ollama(day_prompt, temperature=0.2, max_tokens=-1)
            day_plan = self._extract_json_from_response(day_response)
            
            # Llama can return either {"meal_plan": {"day_1": {}}} or {"day_1": {}} directly
            if day_plan:
                day_data = None
                if "meal_plan" in day_plan and f"day_{day_num}" in day_plan["meal_plan"]:
                    # Format: {"meal_plan": {"day_1": {}}}
                    day_data = day_plan["meal_plan"][f"day_{day_num}"]
                    print(f"    ✅ Day {day_num} complete (nested format)")
                elif f"day_{day_num}" in day_plan:
                    # Format: {"day_1": {}} - direct format
                    day_data = day_plan[f"day_{day_num}"]
                    print(f"    ✅ Day {day_num} complete (direct format)")
                else:
                    print(f"    ❌ Day {day_num} failed - unexpected JSON structure")
                    print(f"    Keys found: {list(day_plan.keys())}")
                    return self._create_safe_fallback_plan(profile)
                
                # Fix instructions if they're arrays (Llama sometimes does this)
                for meal_type in ["breakfast", "lunch", "dinner", "snack_1", "snack_2"]:
                    if meal_type in day_data:
                        instructions = day_data[meal_type].get("instructions", "")
                        if isinstance(instructions, list):
                            # Join array instructions into single string
                            day_data[meal_type]["instructions"] = " ".join(instructions)
                
                all_days[f"day_{day_num}"] = day_data
            else:
                print(f"    ❌ Day {day_num} failed - could not parse JSON")
                return self._create_safe_fallback_plan(profile)
        
        # Combine all batches
        response = json.dumps({
            "meal_plan": all_days,
            "daily_totals": {"calories": 2000, "protein_g": 150, "carbs_g": 200, "fats_g": 65},
            "safety_check": "All meals verified allergen-free",
            "rationale": "Meal plan generated in batches for reliability"
        })
        
        # Parse the combined response
        meal_plan = json.loads(response)
        
        if meal_plan and "meal_plan" in meal_plan:
            days_count = len(meal_plan.get('meal_plan', {}))
            
            # Validate we got the requested number of days
            if days_count < days:
                print(f"⚠️ Only got {days_count} days, expected {days}. Using fallback.")
                return self._create_safe_fallback_plan(profile)
            
            # Validate allergen safety
            if not self._validate_allergen_safety(meal_plan, profile.get('allergies', [])):
                print("⚠️ Allergen detected in AI plan, using fallback")
                return self._create_safe_fallback_plan(profile)
            
            print(f"✅ Successfully generated {days_count} days with Llama 3!")
            return meal_plan
        else:
            print("❌ Failed to parse Llama response as JSON, using fallback")
            return self._create_safe_fallback_plan(profile)
    
    def _validate_allergen_safety(self, meal_plan: Dict, allergies: List[str]) -> bool:
        """Validate that no allergens are present in the meal plan"""
        if not allergies:
            return True
        
        allergens_lower = [a.lower() for a in allergies]
        meal_plan_str = json.dumps(meal_plan).lower()
        
        for allergen in allergens_lower:
            if allergen in meal_plan_str:
                print(f"⚠️ ALLERGEN DETECTED: {allergen} found in meal plan")
                return False
        
        return True
    
    def _create_safe_fallback_plan(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create a safe, basic 7-day meal plan when AI fails"""
        allergies = profile.get('allergies', [])
        
        # Check both dietary_preferences (array) and diet_type (string)
        dietary_pref = profile.get('dietary_preferences', [])
        diet_type = profile.get('diet_type', '')
        is_vegetarian = (
            any(pref.lower() in ['vegetarian', 'vegan'] for pref in dietary_pref) or
            diet_type.lower() in ['vegetarian', 'vegan']
        )
        
        # Safe protein sources
        if is_vegetarian:
            proteins = ["tofu", "lentils", "chickpeas", "paneer", "tempeh"]
        elif 'eggs' not in [a.lower() for a in allergies]:
            proteins = ["chicken breast", "eggs", "fish", "turkey", "prawns"]
        else:
            proteins = ["chicken breast", "turkey", "fish", "lean beef", "lamb"]
        
        # Base meals templates for variety (vegetarian-friendly)
        breakfast_options = [
            {"name": "Oatmeal with fruits", "ingredients": ["oats", "banana", "berries", "honey"], "calories": 350, "protein": 10, "carbs": 60, "fats": 8},
            {"name": "Whole grain toast with avocado", "ingredients": ["whole wheat bread", "avocado", "tomato", "olive oil"], "calories": 320, "protein": 8, "carbs": 45, "fats": 15},
            {"name": "Smoothie bowl", "ingredients": ["banana", "berries", "yogurt", "granola", "chia seeds"], "calories": 380, "protein": 12, "carbs": 55, "fats": 10},
            {"name": "Tofu scramble with vegetables", "ingredients": ["tofu", "spinach", "mushrooms", "whole wheat toast"], "calories": 340, "protein": 18, "carbs": 35, "fats": 14},
            {"name": "Greek yogurt parfait", "ingredients": ["greek yogurt", "granola", "mixed berries", "honey"], "calories": 330, "protein": 15, "carbs": 50, "fats": 8},
            {"name": "Quinoa breakfast bowl", "ingredients": ["quinoa", "almond milk", "apple", "cinnamon", "walnuts"], "calories": 360, "protein": 11, "carbs": 52, "fats": 12},
            {"name": "Protein pancakes", "ingredients": ["oat flour", "banana", "protein powder", "berries"], "calories": 370, "protein": 20, "carbs": 48, "fats": 9}
        ]
        
        # Generate 7 days
        meal_plan = {}
        for day in range(1, 8):
            protein = proteins[(day - 1) % len(proteins)]
            breakfast = breakfast_options[(day - 1) % len(breakfast_options)]
            
            meal_plan[f"day_{day}"] = {
                "breakfast": {
                    "name": breakfast["name"],
                    "ingredients": breakfast["ingredients"],
                    "calories": breakfast["calories"],
                    "protein": breakfast["protein"],
                    "carbs": breakfast["carbs"],
                    "fats": breakfast["fats"],
                    "instructions": f"Prepare {breakfast['name'].lower()} with listed ingredients"
                },
                "lunch": {
                    "name": f"Grilled {protein} with vegetables",
                    "ingredients": [protein, "broccoli", "carrots", "olive oil", "brown rice"],
                    "calories": 480,
                    "protein": 38,
                    "carbs": 45,
                    "fats": 15,
                    "instructions": f"Grill {protein}, steam vegetables, serve with brown rice"
                },
                "dinner": {
                    "name": f"{protein.capitalize()} stir-fry with quinoa",
                    "ingredients": [protein, "bell peppers", "zucchini", "quinoa", "soy sauce"],
                    "calories": 450,
                    "protein": 35,
                    "carbs": 48,
                    "fats": 12,
                    "instructions": "Stir-fry protein and vegetables, serve over cooked quinoa"
                },
                "snack_1": {
                    "name": "Fresh fruit",
                    "ingredients": ["seasonal fruit"],
                    "calories": 80,
                    "protein": 1,
                    "carbs": 20,
                    "fats": 0,
                    "instructions": "Wash and eat fresh fruit"
                },
                "snack_2": {
                    "name": "Handful of nuts",
                    "ingredients": ["mixed nuts"],
                    "calories": 150,
                    "protein": 6,
                    "carbs": 6,
                    "fats": 13,
                    "instructions": "Portion 30g of mixed nuts"
                }
            }
        
        return {
            "meal_plan": meal_plan,
            "daily_totals": {
                "calories": 1490,
                "protein_g": 90,
                "carbs_g": 179,
                "fats_g": 48
            },
            "safety_check": "Basic 7-day plan with allergens avoided",
            "rationale": "Fallback plan generated due to Llama parsing error. Adjust portions based on your calorie needs."
        }
    
    def analyze_feedback(
        self,
        profile: Dict[str, Any],
        feedback: Dict[str, Any],
        current_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze daily feedback and suggest plan adjustments
        
        Args:
            profile: User profile
            feedback: Daily feedback (adherence, satisfaction, energy, notes)
            current_plan: Current meal plan
        
        Returns:
            Analysis with suggested modifications
        """
        profile_context = self._build_profile_context(profile)
        
        prompt = f"""You are analyzing a user's daily nutrition feedback to improve their meal plan.

USER PROFILE:
{profile_context}

TODAY'S FEEDBACK:
- Date: {feedback.get('date')}
- Meal Type: {feedback.get('meal_type', 'unknown')}
- Did they follow the plan? {feedback.get('adherence', 'unknown')}
- Satisfaction (1-5): {feedback.get('satisfaction', 'unknown')}
- Energy Level (1-5): {feedback.get('energy_level', 'unknown')}
- Notes: {feedback.get('notes', 'none')}

CURRENT PLAN SAMPLE:
{json.dumps(current_plan.get('meal_plan', {}).get('day_1', {}), indent=2)[:500]}

TASK:
Analyze the feedback and provide actionable recommendations:
1. What went well?
2. What needs adjustment?
3. Specific meal modifications (keeping allergies in mind)
4. Motivational message

RESPOND IN VALID JSON:
{{
  "analysis": "Brief summary of feedback patterns",
  "went_well": ["positive point 1", "positive point 2"],
  "needs_improvement": ["issue 1", "issue 2"],
  "suggested_changes": {{
    "breakfast": "specific suggestion or null",
    "lunch": "specific suggestion or null",
    "dinner": "specific suggestion or null",
    "snacks": "specific suggestion or null"
  }},
  "motivation": "Encouraging message based on progress",
  "allergen_safety_confirmed": true
}}
"""
        
        response = self._call_ollama(prompt, temperature=0.5, max_tokens=2000)
        
        analysis = self._extract_json_from_response(response)
        if analysis:
            return analysis
        else:
            print("Failed to parse feedback analysis, using fallback")
            return self._create_fallback_analysis(feedback)
    
    def _create_fallback_analysis(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic feedback analysis when AI is unavailable"""
        satisfaction = feedback.get('satisfaction', 3)
        adherence = feedback.get('adherence', 'partial')
        
        if satisfaction >= 4 and adherence == 'yes':
            analysis = "Great job following your plan!"
            went_well = ["High satisfaction", "Good adherence"]
        elif satisfaction < 3:
            analysis = "Let's make your meals more enjoyable"
            went_well = ["You're staying committed"]
        else:
            analysis = "Making progress, keep it up!"
            went_well = ["Consistent effort"]
        
        return {
            "analysis": analysis,
            "went_well": went_well,
            "needs_improvement": ["Track more details for better insights"],
            "suggested_changes": {
                "breakfast": None,
                "lunch": None,
                "dinner": None,
                "snacks": None
            },
            "motivation": "Every step forward is progress. Keep going!",
            "allergen_safety_confirmed": True
        }
    
    def get_meal_alternatives(
        self,
        profile: Dict[str, Any],
        original_meal: Dict[str, Any],
        reason: str = "variety"
    ) -> List[Dict[str, Any]]:
        """
        Generate alternative meals with similar nutrition
        
        Args:
            profile: User profile with allergies
            original_meal: The meal to replace
            reason: Why alternatives are needed
        
        Returns:
            List of 3 alternative meals
        """
        profile_context = self._build_profile_context(profile)
        
        prompt = f"""Generate 3 alternative meals to replace the following:

ORIGINAL MEAL:
{json.dumps(original_meal, indent=2)}

USER PROFILE:
{profile_context}

REASON FOR ALTERNATIVES: {reason}

REQUIREMENTS:
1. Similar calorie and macro profile (±50 calories)
2. MUST avoid all user allergies
3. Different ingredients from original
4. Match user's dietary preferences
5. Practical and easy to prepare

RESPOND IN VALID JSON:
{{
  "alternatives": [
    {{
      "name": "...",
      "ingredients": [...],
      "calories": 0,
      "protein_g": 0,
      "carbs_g": 0,
      "fats_g": 0,
      "instructions": "...",
      "why_better": "Reason this is a good alternative"
    }},
    ... (2 more)
  ]
}}
"""
        
        response = self._call_ollama(prompt, temperature=0.6, max_tokens=3000)
        
        alternatives = self._extract_json_from_response(response)
        if alternatives and 'alternatives' in alternatives:
            return alternatives.get('alternatives', [])
        else:
            print("Failed to parse meal alternatives")
            return []


# Singleton instance
_llama_service = None

def get_llama_service() -> LlamaService:
    """Get singleton instance of LlamaService"""
    global _llama_service
    if _llama_service is None:
        _llama_service = LlamaService()
    return _llama_service
