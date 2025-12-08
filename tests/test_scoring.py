import json
from service.pdf_recommender import PDFRecommender, UserProfile

with open('service/data/profile.json', 'r') as f:
    profile = json.load(f)

# Calculate BMI category
def get_bmi_category(bmi):
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"

bmi = profile.get("bmi", 22)
bmi_category = get_bmi_category(bmi)

# Get goal from profile
goals = profile.get("goals", ["weight_loss_only"])
goal = goals[0] if isinstance(goals, list) else goals

user = UserProfile(
    gender=profile.get("gender", "male").lower(),
    age=profile.get("age", 20),
    height=profile.get("height", 178),
    weight=profile.get("weight", 60),
    bmi_category=bmi_category,
    activity_level=profile.get("activity_level", "light").lower().replace(" ", "_"),
    diet_type=profile.get("diet_type", "vegetarian").lower(),
    region=profile.get("region", "south_indian").lower().replace(" ", "_"),
    goal=goal,
    health_conditions=[],
    allergies=[]
)

recommender = PDFRecommender()

# Test HIERARCHICAL EXACT MATCH - goal first, then 5 other factors
print("="*80)
print("HIERARCHICAL EXACT MATCH TEST")
print("="*80)
print("Matching order:")
print(f"  1. GOAL: {user.goal}")
print(f"  2. Region: {user.region}")
print(f"  3. Diet: {user.diet_type}")
print(f"  4. Gender: {user.gender}")
print(f"  5. BMI: {user.bmi_category}")
print(f"  6. Activity: {user.activity_level}")
print("="*80 + "\n")

# Get exact matches
exact_matches = recommender.recommend(user, top_k=10)

if exact_matches:
    print(f"✓ Found {len(exact_matches)} EXACT MATCHES:\n")
    for i, plan in enumerate(exact_matches, 1):
        print(f"{i}. {plan['filename'][:80]}")
        print(f"   Category: {plan.get('category')}")
        print(f"   [Gender: {plan.get('gender')}, Diet: {plan.get('diet_type')}, "
              f"Region: {plan.get('region')}, BMI: {plan.get('bmi_category')}, "
              f"Activity: {plan.get('activity')}]")
        print()
else:
    print("❌ NO EXACT MATCHES FOUND")
    print("\nThis means no plans match ALL 6 factors exactly:")
    print(f"  1. goal → category mapping")
    print(f"  2. region={user.region}")
    print(f"  3. diet_type={user.diet_type}")
    print(f"  4. gender={user.gender}")
    print(f"  5. bmi_category={user.bmi_category}")
    print(f"  6. activity_level={user.activity_level}")
