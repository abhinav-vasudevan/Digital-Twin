"""
Test PDF recommender with actual user profile
"""
import json
from service.pdf_recommender import PDFRecommender, UserProfile

# Load actual profile
with open('service/data/profile.json', 'r') as f:
    profile = json.load(f)

print("="*80)
print("PROFILE MATCHING DIAGNOSTICS")
print("="*80)
print()

# Show profile data
print("ACTUAL PROFILE DATA:")
print("-"*80)
print(f"Gender: {profile.get('gender')}")
print(f"Age: {profile.get('age')}")
print(f"Height: {profile.get('height')} cm")
print(f"Weight: {profile.get('weight')} kg")
print(f"BMI: {profile.get('bmi')}")
print(f"Activity: {profile.get('activity_level')}")
print(f"Diet: {profile.get('diet_type')}")
print(f"Region: {profile.get('region')}")
print(f"Goals: {profile.get('goals')}")
print(f"Conditions: {profile.get('medical_conditions')}")
print(f"Allergies: {profile.get('allergies')}")
print()

# Convert BMI to category (goal-aware)
def get_bmi_category(bmi, goal=None):
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

goals = profile.get("goals", ["weight_loss"])
primary_goal = goals[0] if goals else "weight_loss"
bmi = profile.get("bmi", 22)
bmi_category = get_bmi_category(bmi, primary_goal)

print("CONVERTED TO RECOMMENDER FORMAT:")
print("-"*80)
print(f"Gender: {profile.get('gender', 'male').lower()}")
print(f"Age: {profile.get('age', 20)}")
print(f"BMI Category: {bmi_category} (from BMI {bmi})")
print(f"Activity: {profile.get('activity_level', 'light').lower()}")
print(f"Diet: {profile.get('diet_type', 'vegetarian').lower()}")
print(f"Region: {profile.get('region', 'south_indian').lower()}")
print(f"Primary Goal: {primary_goal.lower().replace(' ', '_')}")
print(f"Conditions: {profile.get('medical_conditions', [])}")
print(f"Allergies: {profile.get('allergies', [])}")
print()

# Create UserProfile
user = UserProfile(
    gender=profile.get("gender", "male").lower(),
    age=profile.get("age", 20),
    height=profile.get("height", 178),
    weight=profile.get("weight", 60),
    bmi_category=bmi_category,
    activity_level=profile.get("activity_level", "light").lower().replace(" ", "_"),
    diet_type=profile.get("diet_type", "vegetarian").lower(),
    region=profile.get("region", "south_indian").lower().replace(" ", "_"),
    goal=primary_goal.lower().replace(" ", "_"),
    health_conditions=[c.lower().replace(" ", "_") for c in profile.get("medical_conditions", [])],
    allergies=profile.get("allergies", [])
)

print("TESTING RECOMMENDER:")
print("-"*80)
recommender = PDFRecommender()

print(f"Total plans in database: {len(recommender.index['plans'])}")
print()

# Test filtering step by step
print("STEP-BY-STEP FILTERING:")
print("-"*80)

# Filter by gender
gender_matches = [p for p in recommender.index['plans'] if p.get('gender', '').lower() == user.gender]
print(f"1. Gender ({user.gender}): {len(gender_matches)}/{len(recommender.index['plans'])} plans")

# Filter by BMI
bmi_matches = [p for p in gender_matches if p.get('bmi_category', '').lower() == user.bmi_category]
print(f"2. BMI ({user.bmi_category}): {len(bmi_matches)}/{len(gender_matches)} plans")

# Filter by activity
activity_matches = [p for p in bmi_matches if p.get('activity', '').lower().replace(' ', '_') == user.activity_level]
print(f"3. Activity ({user.activity_level}): {len(activity_matches)}/{len(bmi_matches)} plans")

# Filter by diet
def is_diet_compatible(plan_diet, user_diet):
    plan_diet = plan_diet.lower()
    user_diet = user_diet.lower()
    
    if user_diet == 'vegan':
        return plan_diet == 'vegan'
    elif user_diet == 'vegetarian':
        return plan_diet in ['vegan', 'vegetarian']
    elif user_diet == 'eggetarian':
        return plan_diet in ['vegan', 'vegetarian', 'eggetarian']
    else:  # non-veg
        return True

diet_matches = [p for p in activity_matches if is_diet_compatible(p.get('diet_type', ''), user.diet_type)]
print(f"4. Diet ({user.diet_type}): {len(diet_matches)}/{len(activity_matches)} plans")
print()

if len(diet_matches) == 0:
    print("⚠️ NO MATCHES FOUND!")
    print()
    print("DEBUGGING - Show sample plans to find mismatch:")
    print("-"*80)
    
    # Show first 5 plans
    for i, plan in enumerate(recommender.index['plans'][:5]):
        print(f"\nPlan {i+1}: {plan.get('filename', 'N/A')[:60]}")
        print(f"  Gender: {plan.get('gender', 'N/A')}")
        print(f"  BMI: {plan.get('bmi_category', 'N/A')}")
        print(f"  Activity: {plan.get('activity', 'N/A')}")
        print(f"  Diet: {plan.get('diet_type', 'N/A')}")
    
    print()
    print("CHECKING FOR UNDERWEIGHT + MALE + LIGHT + VEGETARIAN PLANS:")
    print("-"*80)
    underweight_male = [p for p in recommender.index['plans'] 
                        if p.get('gender', '').lower() == 'male' 
                        and p.get('bmi_category', '').lower() == 'underweight']
    print(f"Male + Underweight plans: {len(underweight_male)}")
    
    if underweight_male:
        print("\nSample Male + Underweight plans:")
        for i, plan in enumerate(underweight_male[:5]):
            print(f"  {i+1}. {plan.get('filename', 'N/A')[:70]}")
            print(f"     Activity: {plan.get('activity', 'N/A')}, Diet: {plan.get('diet_type', 'N/A')}")

else:
    print(f"✅ FOUND {len(diet_matches)} MATCHING PLANS!")
    print()
    
    # Get recommendations
    recommendations = recommender.recommend(user, top_k=10)
    
    print(f"TOP {len(recommendations)} RECOMMENDATIONS:")
    print("="*80)
    for i, plan in enumerate(recommendations, 1):
        age_info = plan.get('age_info', {})
        adj_nutrition = plan.get('adjusted_nutrition', {})
        
        print(f"\n{i}. {plan['filename'][:70]}")
        print(f"   Category: {plan.get('category', 'N/A')}")
        print(f"   Region: {plan.get('region', 'N/A')}")
        print(f"   Score: {plan['recommendation_score']:.1f}")
        print(f"   Age Range: {age_info.get('age_min', 'N/A')}-{age_info.get('age_max', 'N/A')}")
        print(f"   Calories: {adj_nutrition.get('calories_min', 0)}-{adj_nutrition.get('calories_max', 0)} kcal")
        
        if adj_nutrition.get('age_adjusted'):
            adj = adj_nutrition.get('age_adjustment_calories', 0)
            print(f"   ✅ Age Adjusted: {'+' if adj > 0 else ''}{adj} kcal")

print()
print("="*80)
