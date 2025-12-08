"""
Hierarchical Exact Match Recommender System
Matches in hierarchical order:
1. GOAL (primary filter - maps to category folder)
2. Region (north_indian/south_indian)
3. Diet Type (vegetarian/vegan/non_vegetarian)
4. Gender (male/female)
5. BMI Category (underweight/normal/overweight/obese)
6. Activity Level (sedentary/light/moderate/heavy)

Returns empty list if no exact match found on ALL 6 factors.
"""

import json
import os
from pathlib import Path

class ExactMatchRecommender:
    
    # Goal to category folder mapping
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
        'acne_oily_skin': 'skin_health',
        'weight_loss_pcos': 'weight_loss_pcos',
        'weight_loss_only': 'weight_loss',
        'weight_loss_type1_diabetes': 'weight_loss_diabetes',
    }
    
    def __init__(self, index_path=None):
        """Initialize with PDF index"""
        if index_path is None:
            base_dir = Path(__file__).parent.parent.parent
            index_path = base_dir / "outputs" / "pdf_index.json"
        
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'plans' in data:
            self.plans = data['plans']
            self.metadata = data.get('metadata', {})
        else:
            self.plans = data
            self.metadata = {}
        
        print(f"[ExactMatchRecommender] Loaded {len(self.plans)} plans")
    
    def get_bmi_category(self, bmi: float) -> str:
        """Categorize BMI"""
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"
    
    def normalize_diet_type(self, diet: str) -> str:
        """Normalize diet type variations"""
        if not diet:
            return 'vegetarian'
        diet_lower = diet.lower()
        if diet_lower in ['non_vegetarian', 'non_veg', 'nonveg', 'non vegetarian', 'non vegeterian']:
            return 'non_veg'
        elif diet_lower in ['vegetarian', 'veg', 'vegeterian']:
            return 'vegetarian'
        elif diet_lower in ['vegan']:
            return 'vegan'
        return 'vegetarian'
    
    def normalize_bmi(self, bmi: str) -> str:
        """Normalize BMI category variations"""
        if not bmi:
            return ''
        bmi_lower = bmi.lower()
        if bmi_lower in ['normal', 'normal weight', 'normal_weight']:
            return 'normal'
        elif bmi_lower in ['overweight', 'over weight', 'over_weight']:
            return 'overweight'
        elif bmi_lower in ['obese']:
            return 'obese'
        elif bmi_lower in ['underweight', 'under weight', 'under_weight']:
            return 'underweight'
        return bmi_lower
    
    def normalize_activity(self, activity: str) -> str:
        """Normalize activity level variations"""
        if not activity:
            return ''
        activity_lower = activity.lower()
        if 'heavy' in activity_lower or activity_lower == 'very_active':
            return 'heavy'
        elif 'moderate' in activity_lower:
            return 'moderate'
        elif 'light' in activity_lower:
            return 'light'
        elif 'sedentary' in activity_lower:
            return 'sedentary'
        return activity_lower
    
    def exact_match(self, user_profile: dict) -> list:
        """
        Find plans matching EXACTLY on 6 factors in hierarchical order:
        1. GOAL → category
        2. region
        3. diet_type
        4. gender
        5. bmi_category
        6. activity_level
        
        Args:
            user_profile: User profile dictionary
        
        Returns:
            List of exactly matching plans (empty if none match)
        """
        # Extract user criteria
        goal = user_profile.get('goal', '')
        if not goal and user_profile.get('goals'):
            goal = user_profile['goals'][0] if isinstance(user_profile['goals'], list) else user_profile['goals']
        
        gender = user_profile.get('gender', '').lower()
        diet = self.normalize_diet_type(user_profile.get('diet_type', ''))
        region = user_profile.get('region', '').lower()
        bmi_category = self.normalize_bmi(user_profile.get('bmi_category', ''))
        activity = self.normalize_activity(user_profile.get('activity_level', ''))
        
        # Map goal to category
        category = self.GOAL_TO_CATEGORY.get(goal)
        if not category:
            print(f"\n[HIERARCHICAL EXACT MATCH] ❌ Goal '{goal}' has no matching category")
            return []
        
        print(f"\n[HIERARCHICAL EXACT MATCH] Matching on 6 factors:")
        print(f"  1. GOAL: '{goal}' → Category: '{category}'")
        print(f"  2. Region: {region}")
        print(f"  3. Diet: {diet}")
        print(f"  4. Gender: {gender}")
        print(f"  5. BMI: {bmi_category}")
        print(f"  6. Activity: {activity}")
        
        exact_matches = []
        
        for plan in self.plans:
            plan_category = plan.get('category', '')
            plan_gender = (plan.get('gender') or '').lower()
            plan_diet = self.normalize_diet_type(plan.get('diet_type') or 'vegetarian')
            plan_region = (plan.get('region') or '').lower()
            plan_bmi = self.normalize_bmi(plan.get('bmi_category') or '')
            plan_activity = self.normalize_activity(plan.get('activity') or '')
            
            # ALL 6 factors must match EXACTLY
            if (plan_category == category and
                plan_region == region and
                plan_diet == diet and
                plan_gender == gender and
                plan_bmi == bmi_category and
                plan_activity == activity):
                
                exact_matches.append(plan)
        
        print(f"[HIERARCHICAL EXACT MATCH] ✓ Found {len(exact_matches)} plans matching ALL 6 factors")
        
        return exact_matches
    
    def recommend(self, user_profile: dict, top_k: int = 5) -> dict:
        """
        Get exact match recommendations
        
        Args:
            user_profile: User profile dictionary
            top_k: Maximum number of results (not used, returns all exact matches)
        
        Returns:
            Dictionary with 'status' and 'recommendations' or 'message'
        """
        matches = self.exact_match(user_profile)
        
        if not matches:
            return {
                'status': 'not_available',
                'message': 'No diet plan available for your exact requirements.',
                'recommendations': [],
                'criteria': {
                    'gender': user_profile.get('gender'),
                    'age': user_profile.get('age'),
                    'height': user_profile.get('height'),
                    'weight': user_profile.get('weight'),
                    'activity_level': user_profile.get('activity_level'),
                    'diet_type': user_profile.get('diet_type'),
                    'region': user_profile.get('region'),
                    'goal': user_profile.get('goals', ['maintain'])[0] if user_profile.get('goals') else 'maintain'
                }
            }
        
        return {
            'status': 'success',
            'recommendations': matches[:top_k],  # Limit to top_k
            'total_matches': len(matches)
        }
