import json
from service.pdf_recommender import PDFRecommender, UserProfile

with open('service/data/profile.json', 'r') as f:
    profile = json.load(f)

# Calculate BMI category (goal-aware)
def get_bmi_category(bmi, goal=None):
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
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

recommender = PDFRecommender()

# Get all filtered plans (before scoring)
filtered = recommender.filter_by_hard_constraints(user)
print(f"Total filtered plans: {len(filtered)}\n")

# Score each plan
scored_plans = []
for plan in filtered:
    score = recommender.score_plan(plan, user)
    scored_plans.append({
        'filename': plan['filename'][:70],
        'category': plan.get('category'),
        'region': plan.get('region'),
        'diet': plan.get('diet_type'),
        'score': score
    })

# Sort by score
scored_plans.sort(key=lambda x: x['score'], reverse=True)

print("TOP 10 SCORED PLANS:")
print("="*80)
for i, p in enumerate(scored_plans[:10], 1):
    print(f"\n{i}. {p['filename']}")
    print(f"   Category: {p['category']}, Region: {p['region']}, Diet: {p['diet']}")
    print(f"   Score: {p['score']}")

print("\n" + "="*80)
print("SCORE BREAKDOWN:")
print("="*80)
print("Category match (weight_gain): +1000")
print("Exact diet match (vegetarian): +100")
print("Region match (south_indian): +10")
print("Age match: +10 or +5")
print("\nExpected top score for weight_gain + south_indian + vegetarian: 1110")
