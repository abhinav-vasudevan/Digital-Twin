"""
Goal-Only Recommender System
Matches ONLY Primary Goal + Region
Ignores: Gender, BMI, Activity, Diet, Health conditions, Age, Allergies
"""

import json
from pathlib import Path

class GoalOnlyRecommender:
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
        
        print(f"[GoalOnlyRecommender] Loaded {len(self.plans)} plans")
    
    def detect_primary_goal(self, user_profile: dict) -> str:
        """
        Detect primary goal from profile
        
        Priority:
        1. Explicit goals array (first item)
        2. Weight change direction (current vs target)
        3. Default to 'maintain'
        
        Args:
            user_profile: User profile dictionary
        
        Returns:
            Primary goal string
        """
        # Check explicit goals
        goals = user_profile.get('goals', [])
        if goals:
            return goals[0]
        
        # Check weight change direction
        current_weight = user_profile.get('weight', 0)
        target_weight = user_profile.get('target_weight', 0)
        
        if target_weight > current_weight:
            return 'weight_gain'
        elif target_weight < current_weight:
            return 'weight_loss'
        
        return 'maintain'
    
    def normalize_diet_type(self, diet: str) -> str:
        """Normalize diet type variations to match PDF index"""
        if not diet:
            return 'vegetarian'
        diet_lower = diet.lower()
        if diet_lower in ['non_vegetarian', 'non_veg', 'nonveg', 'non vegetarian', 'non vegeterian']:
            return 'non_veg'
        elif diet_lower in ['vegetarian', 'veg', 'vegeterian']:
            return 'vegetarian'
        elif diet_lower in ['vegan']:
            return 'vegan'
        elif diet_lower in ['eggetarian', 'egg', 'eggeterian']:
            return 'eggetarian'
        return 'vegetarian'
    
    def goal_match(self, user_profile: dict) -> list:
        """
        Find plans matching Primary Goal + Diet Type + Region
        Ignores: Gender, BMI, Activity, Health conditions, Age, Allergies
        
        Args:
            user_profile: User profile dictionary
        
        Returns:
            List of matching plans
        """
        primary_goal = self.detect_primary_goal(user_profile)
        diet = self.normalize_diet_type(user_profile.get('diet_type', ''))
        region = user_profile.get('region', '').lower()
        
        # Map goal to category (must match PDF index categories exactly)
        # Keep in sync with ExactMatchRecommender.GOAL_TO_CATEGORY
        goal_category_map = {
            # Weight goals
            'weight_loss': 'weight_loss',
            'weight_loss_only': 'weight_loss',
            'weight_loss_pcos': 'weight_loss_pcos',
            'weight_loss_type1_diabetes': 'weight_loss_diabetes',
            'weight_gain': 'weight_gain',
            'weight_gain_underweight': 'weight_gain',
            'muscle_building': 'weight_gain',
            'maintain': 'maintenance',
            
            # Skin & beauty
            'clear_skin': 'skin_health',
            'acne_oily_skin': 'skin_health',
            'skin_health': 'skin_health',
            'skin_detox': 'skin_detox',
            'anti_aging': 'anti_aging',
            'anti_aging_sun_damage': 'anti_aging',
            
            # Digestive health
            'gut_health': 'gut_cleanse_digestive_detox',
            'digestive_detox': 'gut_cleanse_digestive_detox',
            'gut_detox': 'gut_detox',
            'gas_bloating': 'gas_bloating',
            'probiotic': 'probiotic',
            'probiotic_rich': 'probiotic',
            
            # Detox
            'detox': 'ayurvedic_detox',
            'ayurvedic_detox': 'ayurvedic_detox',
            'liver_detox': 'liver_detox',
            
            # Other health
            'hair_loss': 'hair_loss',
            'hair_loss_thinning': 'hair_loss',
            'anti_inflammatory': 'anti_inflammatory',
            'pcos': 'weight_loss_pcos',
            'diabetes': 'weight_loss_diabetes',
            
            # Protein/fitness
            'protein_rich_balanced': 'high_protein_balanced',
            'high_protein_high_fiber': 'high_protein_high_fiber',
            
            # Generic
            'energy': 'energy_boost',
            'better_sleep': 'sleep_improvement',
        }
        target_category = goal_category_map.get(primary_goal, primary_goal)
        
        print(f"\n[GoalOnly] Matching on:")
        print(f"  Primary Goal/Category: {target_category}")
        print(f"  Diet Type: {diet}")
        print(f"  Region: {region}")
        print(f"  Ignoring: Gender, BMI, Activity, Health, Age, Allergies")
        
        matches = []
        
        for plan in self.plans:
            plan_category = (plan.get('category') or '').lower()
            plan_diet = (plan.get('diet_type') or 'vegetarian').lower()
            plan_region = (plan.get('region') or '').lower()
            
            # Match goal category + diet type + region
            if plan_category == target_category and plan_diet == diet and plan_region == region:
                matches.append(plan)
        
        print(f"[GoalOnly] Found {len(matches)} matches")
        
        return matches
    
    def recommend(self, user_profile: dict, top_k: int = 10) -> dict:
        """
        Get goal-only recommendations
        
        Args:
            user_profile: User profile dictionary
            top_k: Maximum number of results
        
        Returns:
            Dictionary with 'status' and 'recommendations'
        """
        matches = self.goal_match(user_profile)
        
        if not matches:
            primary_goal = self.detect_primary_goal(user_profile)
            return {
                'status': 'not_available',
                'message': f'No diet plans found for goal "{primary_goal}", diet "{user_profile.get("diet_type")}", region "{user_profile.get("region")}"',
                'recommendations': [],
                'criteria': {
                    'goal': primary_goal,
                    'diet_type': user_profile.get('diet_type'),
                    'region': user_profile.get('region')
                }
            }
        
        return {
            'status': 'success',
            'recommendations': matches[:top_k],
            'total_matches': len(matches),
            'criteria': {
                'goal': self.detect_primary_goal(user_profile),
                'diet_type': user_profile.get('diet_type'),
                'bmi_category': user_profile.get('bmi_category')
            }
        }
