"""
Exact Match Recommender System
Matches ALL fields exactly: Gender, BMI Category, Activity, Diet, Region, Category
Returns "diet not available" if no exact match found.
"""

import json
import os
from pathlib import Path

class ExactMatchRecommender:
    def __init__(self, index_path=None):
        """Initialize with PDF index"""
        if index_path is None:
            # Default path to pdf_index.json
            base_dir = Path(__file__).parent.parent.parent
            index_path = base_dir / "outputs" / "pdf_index.json"
        
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both old format (list) and new format (dict with 'plans' key)
        if isinstance(data, dict) and 'plans' in data:
            self.plans = data['plans']
            self.metadata = data.get('metadata', {})
        else:
            self.plans = data
            self.metadata = {}
        
        print(f"[ExactMatchRecommender] Loaded {len(self.plans)} plans")
    
    def get_bmi_category(self, bmi: float, goal: str = None) -> str:
        """
        Categorize BMI with goal-aware adjustments
        
        Args:
            bmi: Body Mass Index value
            goal: Primary health goal (e.g., 'weight_gain', 'weight_loss')
        
        Returns:
            BMI category string
        """
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            # Goal-aware borderline cases
            if goal in ['weight_gain', 'muscle_building'] and bmi < 20:
                return "underweight"  # Borderline low for weight gain
            elif goal in ['weight_loss'] and bmi > 24:
                return "overweight"  # Borderline high for weight loss
            return "normal"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"
    
    def normalize_diet_type(self, diet: str) -> str:
        """Normalize diet type to match PDF index format"""
        diet_lower = diet.lower()
        # Map variations to PDF index format
        if diet_lower in ['non_vegetarian', 'non_veg', 'nonveg', 'non vegetarian']:
            return 'non_veg'
        elif diet_lower in ['vegetarian', 'veg']:
            return 'vegetarian'
        elif diet_lower in ['eggetarian', 'eggitarian']:
            return 'eggetarian'
        elif diet_lower in ['vegan']:
            return 'vegan'
        return diet_lower
    
    def exact_match(self, user_profile: dict) -> list:
        """
        Find plans that match ALL criteria EXACTLY
        
        Required matches:
        - Gender (exact)
        - Age (exact)
        - Height (exact)
        - Weight (exact)
        - Activity Level (exact)
        - Diet Type (exact)
        - Region (exact)
        - Category/Goal (exact)
        
        Args:
            user_profile: User profile dictionary
        
        Returns:
            List of exactly matching plans (empty if none match)
        """
        # Extract user criteria
        gender = user_profile.get('gender', '').lower()
        age = user_profile.get('age', 0)
        height = user_profile.get('height', 0)
        weight = user_profile.get('weight', 0)
        activity = user_profile.get('activity_level', '').lower()
        diet = self.normalize_diet_type(user_profile.get('diet_type', ''))
        region = user_profile.get('region', '').lower()
        
        # Map goal to category - try multiple related categories
        primary_goal = user_profile.get('goals', ['maintain'])[0] if user_profile.get('goals') else 'maintain'
        medical_conditions = user_profile.get('medical_conditions', [])
        
        # Check if user has PCOS or diabetes in medical conditions
        has_pcos = any('pcos' in str(condition).lower() for condition in medical_conditions) if medical_conditions else False
        has_diabetes = any('diabetes' in str(condition).lower() or 'diabetic' in str(condition).lower() for condition in medical_conditions) if medical_conditions else False
        
        # Build category list based on goal and medical conditions
        goal_category_map = {
            'weight_gain': ['weight_gain'],
            'muscle_building': ['weight_gain', 'high_protein_balanced', 'high_protein_high_fiber'],
            'maintain': ['maintenance'],
            'clear_skin': ['skin_health', 'skin_detox'],
            'skin_health': ['skin_health', 'skin_detox'],
            'gut_health': ['gut_health', 'gut_detox', 'gut_cleanse_digestive_detox', 'probiotic'],
            'energy': ['energy_boost'],
            'better_sleep': ['sleep_improvement'],
            'pcos': ['weight_loss_pcos', 'pcos'],
            'diabetes': ['weight_loss_diabetes', 'diabetes'],
            'hair_loss': ['hair_loss'],
            'anti_aging': ['anti_aging'],
            'detox': ['detox', 'liver_detox', 'ayurvedic_detox', 'skin_detox', 'gut_detox'],
            'anti_inflammatory': ['anti_inflammatory'],
            'probiotic': ['probiotic', 'gut_cleanse_digestive_detox'],
            'gas_bloating': ['gas_bloating', 'gut_cleanse_digestive_detox'],
        }
        
        # Special handling for weight_loss based on medical conditions
        if primary_goal == 'weight_loss':
            target_categories = ['weight_loss']
            if has_pcos:
                target_categories.append('weight_loss_pcos')
            if has_diabetes:
                target_categories.append('weight_loss_diabetes')
        else:
            target_categories = goal_category_map.get(primary_goal, [primary_goal])
            if not isinstance(target_categories, list):
                target_categories = [target_categories]
        
        print(f"\n[ExactMatch] Looking for EXACT match:")
        print(f"  Gender: {gender}")
        print(f"  Age: {age}")
        print(f"  Height: {height} cm")
        print(f"  Weight: {weight} kg")
        print(f"  Activity: {activity}")
        print(f"  Diet: {diet}")
        print(f"  Region: {region}")
        print(f"  Categories: {target_categories}")
        
        exact_matches = []
        
        for plan in self.plans:
            # All fields must match EXACTLY
            plan_gender = (plan.get('gender') or '').lower()
            plan_activity = (plan.get('activity') or plan.get('activity_level') or '').lower()
            plan_diet = self.normalize_diet_type(plan.get('diet_type') or 'vegetarian')  # Normalize and default
            plan_region = (plan.get('region') or '').lower()
            plan_category = (plan.get('category') or '').lower()
            
            # Get plan age from age_info
            plan_age = None
            if 'age_info' in plan and plan['age_info']:
                age_info = plan['age_info']
                # Use exact age if available, otherwise use average
                if age_info.get('age_min') == age_info.get('age_max'):
                    plan_age = age_info.get('age_min')
                elif age_info.get('age_avg'):
                    plan_age = age_info.get('age_avg')
                elif age_info.get('age_min'):
                    plan_age = age_info.get('age_min')
            
            # Activity matching: very_active matches both "very_active" and "heavy"
            activity_match = (plan_activity == activity) or (activity == 'very_active' and plan_activity == 'heavy')
            
            # Check EXACT match on all fields (category can match any in target list)
            # Note: PDFs don't store height/weight, so we match: gender, age, activity, diet, region, category
            # Skip plans without age info
            if (plan_age is not None and
                plan_gender == gender and
                plan_age == age and
                activity_match and
                plan_diet == diet and
                plan_region == region and
                plan_category in target_categories):
                
                exact_matches.append(plan)
        
        print(f"[ExactMatch] Found {len(exact_matches)} exact matches")
        
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
