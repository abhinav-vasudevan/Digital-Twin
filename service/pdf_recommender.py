"""
PDF-based diet plan recommendation system.
HIERARCHICAL EXACT MATCH - matches in order:
1. GOAL (primary filter)
2. Region (north_indian/south_indian)
3. Diet Type (vegetarian/vegan/non_vegetarian)
4. Gender (male/female)
5. BMI Category (underweight/normal/overweight/obese)
6. Activity Level (sedentary/light/moderate/heavy)
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from service.pdf_parser import parse_pdf_complete
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile for diet plan recommendations."""
    gender: str  # 'male' or 'female' ONLY
    age: int
    height: float  # cm
    weight: float  # kg
    bmi_category: str  # 'underweight', 'normal', 'overweight', 'obese'
    activity_level: str  # 'sedentary', 'light', 'moderate', 'heavy'
    diet_type: str  # 'vegetarian', 'vegan', 'non_vegetarian' ONLY
    region: str  # 'north_indian', 'south_indian' ONLY
    goal: str  # One of the 20 allowed goals
    health_conditions: List[str] = None
    allergies: List[str] = None
    
    def __post_init__(self):
        if self.health_conditions is None:
            self.health_conditions = []
        if self.allergies is None:
            self.allergies = []


class PDFRecommender:
    """Hierarchical Exact Match Recommender - Goal first, then 5 other factors."""
    
    # Goal to category folder mapping (18 folders available)
    GOAL_TO_CATEGORY = {
        'ayurvedic_detox': 'ayurvedic_detox',
        'digestive_detox': 'gut_cleanse_digestive_detox',
        'gut_detox': 'gut_detox',
        'hair_loss_thinning': 'hair_loss',
        'liver_detox': 'liver_detox',
        'probiotic_rich': 'probiotic',
        'skin_detox': 'skin_detox',
        'skin_health': 'skin_health',
        'weight_gain_underweight': 'weight_gain',
        'anti_inflammatory': 'anti_inflammatory',
        'anti_aging_sun_damage': 'anti_aging',
        'gas_bloating': 'gas_bloating',
        'protein_rich_balanced': 'high_protein_balanced',
        'high_protein_high_fiber': 'high_protein_high_fiber',
        'acne_oily_skin': 'skin_health',  # Maps to skin_health
        'weight_loss_pcos': 'weight_loss_pcos',
        'weight_loss_only': 'weight_loss',
        'weight_loss_type1_diabetes': 'weight_loss_diabetes',
        # Skip: edema, insulin_resistance_obesity (no folders)
    }
    
    def __init__(self, index_path: str = "outputs/pdf_index.json"):
        """Initialize recommender with PDF index."""
        self.index_path = Path(index_path)
        self.index = None
        self.load_index()
    
    def load_index(self):
        """Load PDF index from file."""
        logger.info(f"Loading PDF index from {self.index_path}")
        
        if not self.index_path.exists():
            raise FileNotFoundError(f"Index file not found: {self.index_path}")
        
        with open(self.index_path, 'r', encoding='utf-8') as f:
            self.index = json.load(f)
        
        logger.info(f"Loaded {self.index['metadata']['total_plans']} plans")
    
    def hierarchical_exact_match(self, user: UserProfile) -> List[Dict[str, Any]]:
        """
        Hierarchical filtering in exact order:
        1. GOAL → category folder
        2. Region → north_indian or south_indian
        3. Diet Type → vegetarian/vegan/non_vegetarian
        4. Gender → male or female
        5. BMI Category → underweight/normal/overweight/obese
        6. Activity Level → sedentary/light/moderate/heavy
        """
        matched = []
        
        # Step 1: Map goal to category
        category = self.GOAL_TO_CATEGORY.get(user.goal)
        if not category:
            logger.warning(f"Goal '{user.goal}' has no matching category folder")
            return []
        
        logger.info(f"\n{'='*80}")
        logger.info(f"HIERARCHICAL EXACT MATCH")
        logger.info(f"{'='*80}")
        logger.info(f"Step 1: GOAL = '{user.goal}' → Category = '{category}'")
        logger.info(f"Step 2: Region = '{user.region}'")
        logger.info(f"Step 3: Diet = '{user.diet_type}'")
        logger.info(f"Step 4: Gender = '{user.gender}'")
        logger.info(f"Step 5: BMI = '{user.bmi_category}'")
        logger.info(f"Step 6: Activity = '{user.activity_level}'")
        logger.info(f"{'='*80}\n")
        
        # Filter through index
        for plan in self.index['plans']:
            plan_category = plan.get('category', '')
            
            # ALL 6 factors must match EXACTLY in hierarchy
            if (plan_category == category and
                plan.get('region') == user.region and
                self._normalize_diet(plan.get('diet_type')) == self._normalize_diet(user.diet_type) and
                plan.get('gender') == user.gender and
                self._normalize_bmi(plan.get('bmi_category')) == self._normalize_bmi(user.bmi_category) and
                self._normalize_activity(plan.get('activity')) == self._normalize_activity(user.activity_level)):
                
                matched.append(plan)
        
        logger.info(f"✓ Found {len(matched)} plans matching ALL 6 factors (goal + 5 others)")
        return matched
    
    def _normalize_diet(self, diet: str) -> str:
        """Normalize diet type variations in PDF filenames."""
        if not diet:
            return 'vegetarian'
        diet_lower = diet.lower()
        # Handle variations: "vegeterian", "veg", "non veg", "non_veg", "non vegeterian"
        if diet_lower in ['vegeterian', 'vegetarian', 'veg']:
            return 'vegetarian'
        elif diet_lower in ['non_veg', 'non veg', 'non vegeterian', 'non_vegetarian', 'non vegetarian']:
            return 'non_veg'
        elif diet_lower == 'vegan':
            return 'vegan'
        return 'vegetarian'
    
    def _normalize_bmi(self, bmi: str) -> str:
        """Normalize BMI category variations in PDF filenames."""
        if not bmi:
            return ''
        bmi_lower = bmi.lower()
        # Handle variations: "normal weight", "normal", "over weight", "overweight"
        if bmi_lower in ['normal', 'normal weight', 'normal_weight']:
            return 'normal'
        elif bmi_lower in ['overweight', 'over weight', 'over_weight']:
            return 'overweight'
        elif bmi_lower in ['obese']:
            return 'obese'
        elif bmi_lower in ['underweight', 'under weight', 'under_weight']:
            return 'underweight'
        return bmi_lower
    
    def _normalize_activity(self, activity: str) -> str:
        """Normalize activity level variations in PDF filenames."""
        if not activity:
            return ''
        activity_lower = activity.lower()
        # Handle variations: "heavy active", "heavy activity", "heavy"
        if 'heavy' in activity_lower or activity_lower == 'very_active':
            return 'heavy'
        elif 'moderate' in activity_lower:
            return 'moderate'
        elif 'light' in activity_lower:
            return 'light'
        elif 'sedentary' in activity_lower:
            return 'sedentary'
        return activity_lower
    
    def recommend(self, user: UserProfile, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get hierarchical exact matched plans for user.
        
        Args:
            user: UserProfile with all preferences
            top_k: Number of recommendations to return (default 10)
        
        Returns:
            List of plan dicts (exact matches only)
        """
        logger.info(f"Starting hierarchical exact match for user: {user.goal}")
        
        # Get hierarchical exact matches
        matched_plans = self.hierarchical_exact_match(user)
        
        if not matched_plans:
            logger.warning(f"❌ No plans match ALL 6 factors for goal='{user.goal}'")
            return []
        
        # Return matched plans (shuffle for variety)
        random.shuffle(matched_plans)
        
        logger.info(f"✓ Returning {min(top_k, len(matched_plans))} exact matches")
        return matched_plans[:top_k]
    
    def generate_multi_plan_cycle(
        self, 
        selected_plans: List[Dict[str, Any]], 
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Generate a 7-day meal cycle from selected plans with variety.
        
        Args:
            selected_plans: List of diet plans selected by user
            days: Number of days to generate (default 7)
        
        Returns:
            List of daily meal plans with rotation
        """
        if not selected_plans:
            raise ValueError("Must select at least 1 plan")
        
        logger.info(f"Generating {days}-day cycle from {len(selected_plans)} plans")
        
        # Parse meal options from all selected plans
        plans_with_meals = []
        for plan in selected_plans:
            # Check if this is an AI-generated plan
            if plan.get('ai_generated') or (plan.get('meals') and not plan.get('file_path')):
                # ML plan - convert meals array to meal_options format
                meal_options = {
                    'early_morning': [],
                    'pre_activity': [],
                    'breakfast': [],
                    'mid_morning_snack': [],
                    'lunch': [],
                    'evening_snack': [],
                    'dinner': [],
                    'bedtime': []
                }
                
                for meal_group in plan.get('meals', []):
                    meal_type = meal_group.get('meal_type', '').lower()
                    meal_options_list = meal_group.get('options', [])
                    
                    if meal_type in meal_options and meal_options_list:
                        meal_options[meal_type].extend(meal_options_list)
                
                plans_with_meals.append({
                    'plan': plan,
                    'meals': meal_options
                })
            else:
                # PDF plan - parse from file
                file_path = plan.get('file_path')
                if file_path:
                    meal_options = self._parse_meal_options_from_pdf(file_path)
                    plans_with_meals.append({
                        'plan': plan,
                        'meals': meal_options
                    })
        
        if not plans_with_meals:
            raise ValueError("Could not parse meal options from selected plans")
        
        # Create rotation schedule
        schedule = []
        plan_index = 0
        
        from datetime import datetime, timedelta
        start_date = datetime.now()
        
        for day in range(1, days + 1):
            current_plan_data = plans_with_meals[plan_index]
            current_plan = current_plan_data['plan']
            meal_options = current_plan_data['meals']
            current_date = (start_date + timedelta(days=day-1)).strftime("%Y-%m-%d")
            nutrition = current_plan.get('nutrition', {})
            
            option_index = (day - 1) % 3
            
            def get_meal_for_option(meal_type: str, option_idx: int):
                options = meal_options.get(meal_type, [])
                if not options:
                    return {
                        'name': f"{meal_type.replace('_', ' ').title()}",
                        'calories': 0,
                        'protein': 0,
                        'carbs': 0,
                        'fat': 0,
                        'fiber': 0,
                        'ingredients': [],
                        'method': '',
                        'serving': ''
                    }
                selected_option = options[option_idx % len(options)]
                return selected_option
            
            daily_plan = {
                'date': current_date,
                'day': day,
                'day_name': self._get_day_name(day),
                'plan_id': current_plan.get('relative_path'),
                'plan_category': current_plan.get('category'),
                'plan_file': current_plan.get('file_path'),
                'nutrition': nutrition,
                'early_morning': get_meal_for_option('early_morning', option_index),
                'pre_activity': get_meal_for_option('pre_activity', option_index),
                'breakfast': get_meal_for_option('breakfast', option_index),
                'mid_morning_snack': get_meal_for_option('mid_morning_snack', option_index),
                'lunch': get_meal_for_option('lunch', option_index),
                'evening_snack': get_meal_for_option('evening_snack', option_index),
                'dinner': get_meal_for_option('dinner', option_index),
                'bedtime': get_meal_for_option('bedtime', option_index)
            }
            
            schedule.append(daily_plan)
            plan_index = (plan_index + 1) % len(plans_with_meals)
        
        logger.info(f"Generated {days}-day cycle")
        return schedule
    
    def _get_day_name(self, day: int) -> str:
        """Get day name for cycle."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[(day - 1) % 7]
    
    def _parse_meal_options_from_pdf(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse meal options from PDF using comprehensive parser."""
        try:
            parsed_data = parse_pdf_complete(file_path)
            meals_data = {
                'early_morning': [],
                'pre_activity': [],
                'breakfast': [],
                'mid_morning_snack': [],
                'lunch': [],
                'evening_snack': [],
                'dinner': [],
                'bedtime': []
            }
            
            meal_type_mapping = {
                'Early Morning (On Waking)': 'early_morning',
                'Early Morning (on Waking)': 'early_morning',
                'Early Morning': 'early_morning',
                'Pre-Workout (Heavy Training Fuel)': 'pre_activity',
                'Pre-Workout (Heavy Training – Fat Loss Focus)': 'pre_activity',
                'Pre-Workout': 'pre_activity',
                'Pre-Yoga / Light Activity': 'pre_activity',
                'Pre-Activity': 'pre_activity',
                'Pre-Breakfast': 'pre_activity',
                'Breakfast (Post-Workout)': 'breakfast',
                'Breakfast (Post-Yoga / Morning Meal)': 'breakfast',
                'Breakfast': 'breakfast',
                'Mid-Morning Snack': 'mid_morning_snack',
                'Mid-Morning': 'mid_morning_snack',
                'Lunch': 'lunch',
                'Evening Snack': 'evening_snack',
                'Evening': 'evening_snack',
                'Dinner': 'dinner',
                'Bedtime Snack': 'bedtime',
                'Bedtime': 'bedtime'
            }
            
            for meal in parsed_data.get('meals', []):
                meal_type_key = meal_type_mapping.get(meal.get('meal_type'), None)
                if meal_type_key and meal.get('options'):
                    for option in meal['options']:
                        nutrition = option.get('nutrition', {})
                        
                        def safe_int(value, default=0):
                            if isinstance(value, (int, float)):
                                return int(value)
                            if isinstance(value, str):
                                try:
                                    return int(float(value))
                                except (ValueError, TypeError):
                                    return default
                            return default
                        
                        meals_data[meal_type_key].append({
                            'name': option.get('name', 'Unnamed meal'),
                            'calories': safe_int(nutrition.get('calories'), 0),
                            'protein': safe_int(nutrition.get('protein'), 0),
                            'carbs': safe_int(nutrition.get('carbs'), 0),
                            'fat': safe_int(nutrition.get('fat'), 0),
                            'fiber': safe_int(nutrition.get('fiber'), 0),
                            'ingredients': option.get('ingredients', ''),
                            'method': option.get('method', ''),
                            'serving': option.get('serving', ''),
                            'time': option.get('time', '')
                        })
            
            return meals_data
            
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {e}")
            return {}
    
    def get_plan_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get full details for a specific plan by ID."""
        for plan in self.index['plans']:
            if plan.get('relative_path') == plan_id or plan.get('file_path') == plan_id:
                return plan
        return None
    
    def get_category_stats(self) -> Dict[str, int]:
        """Get statistics on available categories."""
        return self.index['metadata']['category']
    
    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Search plans by keyword in filename or content."""
        keyword_lower = keyword.lower()
        results = []
        
        for plan in self.index['plans']:
            if (keyword_lower in plan.get('filename', '').lower() or
                keyword_lower in plan.get('category', '').lower() or
                keyword_lower in plan.get('content_preview', '').lower()):
                results.append(plan)
        
        return results


# Example usage
if __name__ == "__main__":
    recommender = PDFRecommender()
    
    user = UserProfile(
        gender='female',
        age=30,
        height=160,
        weight=78,
        bmi_category='obese',
        activity_level='light',
        diet_type='vegetarian',
        region='north_indian',
        goal='weight_loss',
        health_conditions=[],
        allergies=[]
    )
    
    recommendations = recommender.recommend(user, top_k=10)
    
    print(f"\nFound {len(recommendations)} EXACT matches:\n")
    for i, plan in enumerate(recommendations[:5], 1):
        print(f"{i}. {plan['filename']}")
        print(f"   Category: {plan.get('category', 'N/A')}")
        print()
    
    def generate_multi_plan_cycle(
        self, 
        selected_plans: List[Dict[str, Any]], 
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Generate a 7-day meal cycle from 2-5 selected plans with variety.
        
        Args:
            selected_plans: List of 1-5 diet plans selected by user
            days: Number of days to generate (default 7)
        
        Returns:
            List of daily meal plans with rotation
        """
        if not (1 <= len(selected_plans) <= 5):
            raise ValueError("Must select between 1-5 plans")
        
        logger.info(f"Generating {days}-day cycle from {len(selected_plans)} plans")
        
        # Parse meal options from all selected plans
        plans_with_meals = []
        for plan in selected_plans:
            # Check if this is an AI-generated plan (has meals array already)
            if plan.get('ai_generated') or (plan.get('meals') and not plan.get('file_path')):
                # ML plan - convert meals array to meal_options format
                # Initialize all meal types (ML only has 5, but dashboard expects 8)
                meal_options = {
                    'early_morning': [],
                    'pre_activity': [],
                    'breakfast': [],
                    'mid_morning_snack': [],
                    'lunch': [],
                    'evening_snack': [],
                    'dinner': [],
                    'bedtime': []
                }
                
                # Group meals by type
                # ML meals come as array of objects with 'meal_type', 'type', 'icon', 'options'
                for meal_group in plan.get('meals', []):
                    meal_type = meal_group.get('meal_type', '').lower()
                    meal_options_list = meal_group.get('options', [])
                    
                    if meal_type in meal_options and meal_options_list:
                        # Each option should be a full meal object with name, calories, etc.
                        meal_options[meal_type].extend(meal_options_list)
                
                logger.info(f"Using ML-generated plan with meals:")
                for meal_type, options in meal_options.items():
                    if len(options) > 0:
                        logger.info(f"  {meal_type}: {len(options)} options")
                        logger.info(f"    First option: {options[0].get('name', 'NO NAME')}")
                
                plans_with_meals.append({
                    'plan': plan,
                    'meals': meal_options
                })
            else:
                # PDF plan - parse from file
                file_path = plan.get('file_path')
                if file_path:
                    meal_options = self._parse_meal_options_from_pdf(file_path)
                    # Debug: Log how many options were found for each meal type
                    logger.info(f"Parsed meals from {Path(file_path).name}:")
                    for meal_type, options in meal_options.items():
                        logger.info(f"  {meal_type}: {len(options)} options")
                        if len(options) > 0:
                            logger.info(f"    First option: {options[0].get('name', 'NO NAME')}")
                    plans_with_meals.append({
                        'plan': plan,
                        'meals': meal_options
                    })
        
        if not plans_with_meals:
            raise ValueError("Could not parse meal options from selected plans")
        
        # Create rotation schedule
        schedule = []
        plan_index = 0
        
        from datetime import datetime, timedelta
        start_date = datetime.now()
        
        for day in range(1, days + 1):
            # Rotate through plans
            current_plan_data = plans_with_meals[plan_index]
            current_plan = current_plan_data['plan']
            meal_options = current_plan_data['meals']
            current_date = (start_date + timedelta(days=day-1)).strftime("%Y-%m-%d")
            nutrition = current_plan.get('nutrition', {})
            
            # Determine which option to use (cycle through options across days)
            # Day 1: Option 0, Day 2: Option 1, Day 3: Option 2, Day 4: Option 0, etc.
            option_index = (day - 1) % 3  # Assuming 3 options per meal
            
            # Helper function to get meal data for specific option
            def get_meal_for_option(meal_type: str, option_idx: int):
                options = meal_options.get(meal_type, [])
                if not options:
                    # Fallback if no options found
                    return {
                        'name': f"{current_plan.get('category', 'Meal').replace('_', ' ').title()} - {meal_type.replace('_', ' ').title()}",
                        'calories': 0,
                        'protein': 0,
                        'carbs': 0,
                        'fat': 0,
                        'fiber': 0,
                        'ingredients': [],
                        'method': '',
                        'serving': ''
                    }
                
                # Use modulo to cycle through available options
                selected_option = options[option_idx % len(options)]
                return selected_option
            
            # Create daily plan with actual meal names and details
            daily_plan = {
                'date': current_date,
                'day': day,
                'day_name': self._get_day_name(day),
                'plan_id': current_plan.get('relative_path'),
                'plan_category': current_plan.get('category'),
                'plan_file': current_plan.get('file_path'),
                'nutrition': nutrition,
                'early_morning': get_meal_for_option('early_morning', option_index),
                'pre_activity': get_meal_for_option('pre_activity', option_index),
                'breakfast': get_meal_for_option('breakfast', option_index),
                'mid_morning_snack': get_meal_for_option('mid_morning_snack', option_index),
                'lunch': get_meal_for_option('lunch', option_index),
                'evening_snack': get_meal_for_option('evening_snack', option_index),
                'dinner': get_meal_for_option('dinner', option_index),
                'bedtime': get_meal_for_option('bedtime', option_index)
            }
            
            schedule.append(daily_plan)
            
            # Move to next plan
            plan_index = (plan_index + 1) % len(plans_with_meals)
        
        logger.info(f"Generated {days}-day cycle")
        return schedule
    
    def _get_day_name(self, day: int) -> str:
        """Get day name for cycle."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[(day - 1) % 7]
    
    def _parse_meal_options_from_pdf(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse meal options from PDF text file using comprehensive parser.
        Returns dict with meal types as keys and list of options as values.
        Each option includes: name, ingredients, method, time, serving, nutritive_values
        """
        try:
            # Use comprehensive parser
            parsed_data = parse_pdf_complete(file_path)
            meals_data = {
                'early_morning': [],
                'pre_activity': [],
                'breakfast': [],
                'mid_morning_snack': [],
                'lunch': [],
                'evening_snack': [],
                'dinner': [],
                'bedtime': []
            }
            
            # Convert comprehensive parser output to expected format
            meal_type_mapping = {
                'Early Morning (On Waking)': 'early_morning',
                'Early Morning (on Waking)': 'early_morning',
                'Early Morning': 'early_morning',
                'Pre-Workout (Heavy Training Fuel)': 'pre_activity',
                'Pre-Workout (Heavy Training – Fat Loss Focus)': 'pre_activity',
                'Pre-Workout (Heavy Training Fuel – Controlled Calories)': 'pre_activity',
                'Pre-Workout': 'pre_activity',
                'Pre-Yoga / Light Activity': 'pre_activity',
                'Pre-Activity': 'pre_activity',
                'Pre-Breakfast': 'pre_activity',
                'Breakfast (Post-Workout)': 'breakfast',
                'Breakfast (Post-Yoga / Morning Meal)': 'breakfast',
                'Breakfast (High-Calorie)': 'breakfast',
                'Breakfast': 'breakfast',
                'Mid-Morning Snack': 'mid_morning_snack',
                'Mid-Morning': 'mid_morning_snack',
                'Lunch (High-Calorie Balanced Meals)': 'lunch',
                'Lunch': 'lunch',
                'Evening Snack': 'evening_snack',
                'Evening': 'evening_snack',
                'Dinner': 'dinner',
                'Bedtime Snack': 'bedtime',
                'Bedtime': 'bedtime'
            }
            
            for meal in parsed_data.get('meals', []):
                meal_type_key = meal_type_mapping.get(meal.get('meal_type'), None)
                if meal_type_key and meal.get('options'):
                    for option in meal['options']:
                        # Get nutrition dict (parser uses 'nutrition' not 'nutritive_values')
                        nutrition = option.get('nutrition', {})
                        
                        # Convert string values to integers
                        def safe_int(value, default=0):
                            if isinstance(value, (int, float)):
                                return int(value)
                            if isinstance(value, str):
                                try:
                                    return int(float(value))
                                except (ValueError, TypeError):
                                    return default
                            return default
                        
                        meals_data[meal_type_key].append({
                            'name': option.get('name', 'Unnamed meal'),
                            'calories': safe_int(nutrition.get('calories'), 0),
                            'protein': safe_int(nutrition.get('protein'), 0),
                            'carbs': safe_int(nutrition.get('carbs'), 0),
                            'fat': safe_int(nutrition.get('fat'), 0),
                            'fiber': safe_int(nutrition.get('fiber'), 0),
                            'ingredients': option.get('ingredients', ''),
                            'method': option.get('method', ''),
                            'serving': option.get('serving', ''),
                            'time': option.get('time', '')
                        })
            
            return meals_data
            
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {e}")
            logger.exception("Full traceback:")
            return {}
        
        # OLD FALLBACK CODE BELOW (will be removed)
        meals_data = {
            'early_morning': [],
            'pre_activity': [],
            'breakfast': [],
            'mid_morning_snack': [],
            'lunch': [],
            'evening_snack': [],
            'dinner': [],
            'bedtime': []
        }
        
        # Meal type mappings
        meal_patterns = {
            'Breakfast': 'breakfast',
            'Mid-Morning Snack': 'mid_morning_snack',
            'Lunch': 'lunch',
            'Evening Snack': 'evening_snack',
            'Dinner': 'dinner'
        }
        
        current_meal_type = None
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Detect meal section - handle multiple formats:
            # Format 1: "Breakfast (8:00 AM)"
            # Format 2: "Meal Type: Breakfast"
            # Format 3: "Meal Type: Breakfast (Morning Meal)"
            for pattern, meal_key in meal_patterns.items():
                # Check for "Meal Type: Breakfast" or "Meal Type:Breakfast"
                if 'Meal Type:' in line and pattern in line:
                    current_meal_type = meal_key
                    logger.info(f"[DEBUG] Detected meal type: {meal_key} from line: {line}")
                    break
                # Check for "Breakfast (time)" format (with time or description in parentheses)
                if pattern in line and '(' in line and ')' in line and 'Option' not in line:
                    current_meal_type = meal_key
                    logger.info(f"[DEBUG] Detected meal type: {meal_key} from line: {line}")
                    break
            
            # Parse options
            if current_meal_type and line.startswith('Option '):
                logger.info(f"[DEBUG] Parsing option for {current_meal_type}: {line}")
                option_data = self._parse_meal_option(lines, i)
                if option_data:
                    logger.info(f"[DEBUG] Successfully parsed: {option_data.get('name', 'NO NAME')}")
                    meals_data[current_meal_type].append(option_data)
                else:
                    logger.warning(f"[DEBUG] Failed to parse option from: {line}")
            
            i += 1
        
        return meals_data
    
    def _parse_meal_option(self, lines: List[str], start_idx: int) -> Optional[Dict[str, Any]]:
        """Parse a single meal option from PDF lines."""
        option_line = lines[start_idx].strip()
        
        # Extract option name (e.g., "Option 1 – Ragi Dosa + Coconut Chutney + Green Tea")
        # Handle multiple separators: –, -, :
        if '–' in option_line:
            name = option_line.split('–', 1)[1].strip()
        elif ' - ' in option_line:
            name = option_line.split(' - ', 1)[1].strip()
        elif ': ' in option_line:
            # Handle "Option 1: Vegetable Poha + Curd"
            parts = option_line.split(':', 1)
            if len(parts) > 1:
                name = parts[1].strip()
            else:
                name = option_line
        else:
            name = option_line
        
        # Parse subsequent lines for details
        ingredients = []
        method = ""
        time = ""
        serving = ""
        nutritive_values = {}
        
        i = start_idx + 1
        while i < len(lines) and not lines[i].strip().startswith('Option '):
            line = lines[i].strip()
            
            if line.startswith('• Ingredients:') or line.startswith('Ingredients:'):
                ingredients_text = line.replace('• Ingredients:', '').replace('Ingredients:', '').strip()
                # Also check next lines for continuation
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('•') and not lines[j].strip().startswith('Serving') and not lines[j].strip().startswith('Time') and not lines[j].strip().startswith('Method'):
                    if lines[j].strip() and not lines[j].strip().startswith('Option '):
                        ingredients_text += ' ' + lines[j].strip()
                    else:
                        break
                    j += 1
                ingredients = [ing.strip() for ing in ingredients_text.split(',')]
            
            elif line.startswith('• Method:') or line.startswith('Method:'):
                method = line.replace('• Method:', '').replace('Method:', '').strip()
            
            elif line.startswith('• Time:') or line.startswith('Time:'):
                time = line.replace('• Time:', '').replace('Time:', '').strip()
            
            elif line.startswith('• Serving Size:') or line.startswith('Serving:'):
                serving = line.replace('• Serving Size:', '').replace('Serving:', '').strip()
            
            elif line.startswith('• Nutritive Values:') or line.startswith('Nutritive Values:'):
                # Parse "430 kcal | 15 g protein | 50 g carbs | 10 g fat | 5 g fiber"
                # or "230 kcal, 6 g protein, 38 g carbs, 7 g fat, 3 g fiber"
                values_text = line.replace('• Nutritive Values:', '').replace('Nutritive Values:', '').strip()
                # Handle both | and , as separators
                if '|' in values_text:
                    parts = [p.strip() for p in values_text.split('|')]
                else:
                    parts = [p.strip() for p in values_text.split(',')]
                    
                for part in parts:
                    try:
                        if 'kcal' in part:
                            nutritive_values['calories'] = int(part.replace('kcal', '').strip())
                        elif 'protein' in part:
                            nutritive_values['protein'] = int(part.replace('g', '').replace('protein', '').strip())
                        elif 'carbs' in part:
                            nutritive_values['carbs'] = int(part.replace('g', '').replace('carbs', '').strip())
                        elif 'fat' in part and 'fiber' not in part:
                            nutritive_values['fat'] = int(part.replace('g', '').replace('fat', '').strip())
                        elif 'fiber' in part:
                            nutritive_values['fiber'] = int(part.replace('g', '').replace('fiber', '').strip())
                    except (ValueError, AttributeError):
                        # Skip if can't parse the number
                        pass
            
            # Stop if we hit a new meal section or option
            if any(meal in line for meal in ['Breakfast (', 'Lunch (', 'Dinner (', 'Snack (']):
                break
            
            i += 1
        
        return {
            'name': name,
            'ingredients': ingredients,
            'method': method,
            'time': time,
            'serving': serving,
            'calories': nutritive_values.get('calories', 0),
            'protein': nutritive_values.get('protein', 0),
            'carbs': nutritive_values.get('carbs', 0),
            'fat': nutritive_values.get('fat', 0),
            'fiber': nutritive_values.get('fiber', 0)
        }
    
    def get_plan_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get full details for a specific plan by ID."""
        for plan in self.index['plans']:
            if plan.get('relative_path') == plan_id or plan.get('file_path') == plan_id:
                return plan
        return None
    
    def get_category_stats(self) -> Dict[str, int]:
        """Get statistics on available categories."""
        return self.index['metadata']['category']
    
    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Search plans by keyword in filename or content."""
        keyword_lower = keyword.lower()
        results = []
        
        for plan in self.index['plans']:
            # Search in filename
            if keyword_lower in plan.get('filename', '').lower():
                results.append(plan)
                continue
            
            # Search in category
            if keyword_lower in plan.get('category', '').lower():
                results.append(plan)
                continue
            
            # Search in content preview
            if keyword_lower in plan.get('content_preview', '').lower():
                results.append(plan)
                continue
        
        return results


# Example usage
if __name__ == "__main__":
    # Initialize recommender
    recommender = PDFRecommender()
    
    # Create sample user profile
    user = UserProfile(
        gender='female',
        age=30,
        height=160,
        weight=78,
        bmi_category='obese',
        activity_level='light',
        diet_type='vegetarian',
        region='north_indian',
        goal='weight_loss',
        health_conditions=['pcos'],
        allergies=[]
    )
    
    # Get recommendations
    recommendations = recommender.recommend(user, top_k=10)
    
    print(f"\nFound {len(recommendations)} recommendations:\n")
    for i, plan in enumerate(recommendations[:5], 1):
        print(f"{i}. {plan['filename']}")
        print(f"   Category: {plan.get('category', 'N/A')}")
        print(f"   Score: {plan['recommendation_score']}")
        print(f"   Nutrition: {plan.get('nutrition', {})}")
        print()
