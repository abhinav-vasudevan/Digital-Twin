"""
Test Both Recommendation Systems
Case 1: Exact Match (all fields must match)
Case 2: Goal Only (only goal + region)
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from service.recommender_exact.exact_recommender import ExactMatchRecommender
from service.recommender_goal.goal_recommender import GoalOnlyRecommender

# Load test profile
profile_path = Path("service/data/profile.json")
with open(profile_path, 'r') as f:
    profile = json.load(f)

print("="*80)
print("TEST PROFILE")
print("="*80)
print(f"Gender: {profile.get('gender')}")
print(f"Age: {profile.get('age')}")
print(f"BMI: {profile.get('bmi')}")
print(f"Height: {profile.get('height')} cm")
print(f"Weight: {profile.get('weight')} kg → Target: {profile.get('target_weight')} kg")
print(f"Activity: {profile.get('activity_level')}")
print(f"Diet: {profile.get('diet_type')}")
print(f"Region: {profile.get('region')}")
print(f"Goals: {profile.get('goals')}")
print(f"Medical: {profile.get('medical_conditions')}")
print(f"Allergies: {profile.get('allergies')}")
print()

# ====================
# TEST CASE 1: EXACT MATCH
# ====================
print("="*80)
print("CASE 1: EXACT MATCH SYSTEM")
print("="*80)
print("Matching: Gender + BMI + Activity + Diet + Region + Category (ALL must match)")
print()

exact_recommender = ExactMatchRecommender()
exact_result = exact_recommender.recommend(profile, top_k=5)

if exact_result['status'] == 'not_available':
    print("❌ NO EXACT MATCHES FOUND")
    print(f"Message: {exact_result['message']}")
    print()
    print("Criteria searched:")
    for key, value in exact_result['criteria'].items():
        print(f"  {key}: {value}")
else:
    print(f"✅ FOUND {exact_result['total_matches']} EXACT MATCHES")
    print()
    print("Top recommendations:")
    for i, rec in enumerate(exact_result['recommendations'][:5], 1):
        print(f"\n{i}. {rec.get('filename', 'N/A')}")
        print(f"   Gender: {rec.get('gender')} | BMI: {rec.get('bmi_category')} | Activity: {rec.get('activity_level')}")
        print(f"   Diet: {rec.get('diet_type')} | Region: {rec.get('region')} | Category: {rec.get('category')}")

print()
print()

# ====================
# TEST CASE 2: GOAL ONLY
# ====================
print("="*80)
print("CASE 2: GOAL-ONLY MATCH SYSTEM")
print("="*80)
print("Matching: Primary Goal + Region ONLY")
print("Ignoring: Gender, BMI, Activity, Diet, Health, Age, Allergies")
print()

goal_recommender = GoalOnlyRecommender()
goal_result = goal_recommender.recommend(profile, top_k=10)

if goal_result['status'] == 'not_available':
    print("❌ NO GOAL MATCHES FOUND")
    print(f"Message: {goal_result['message']}")
    print()
    print("Criteria searched:")
    for key, value in goal_result['criteria'].items():
        print(f"  {key}: {value}")
else:
    print(f"✅ FOUND {goal_result['total_matches']} GOAL MATCHES")
    print()
    print("Criteria:")
    for key, value in goal_result['criteria'].items():
        print(f"  {key}: {value}")
    print()
    print("Top recommendations:")
    for i, rec in enumerate(goal_result['recommendations'][:10], 1):
        print(f"\n{i}. {rec.get('filename', 'N/A')}")
        print(f"   Gender: {rec.get('gender')} | BMI: {rec.get('bmi_category')} | Activity: {rec.get('activity_level')}")
        print(f"   Diet: {rec.get('diet_type')} | Region: {rec.get('region')} | Category: {rec.get('category')}")

print()
print()

# ====================
# COMPARISON
# ====================
print("="*80)
print("COMPARISON")
print("="*80)

if exact_result['status'] == 'success':
    exact_count = exact_result['total_matches']
else:
    exact_count = 0

if goal_result['status'] == 'success':
    goal_count = goal_result['total_matches']
else:
    goal_count = 0

print(f"Exact Match System:  {exact_count} plans")
print(f"Goal-Only System:    {goal_count} plans")
print(f"Difference:          {goal_count - exact_count} additional plans from relaxed matching")
print()

if exact_count > 0 and goal_count > 0:
    print("✅ Both systems working correctly!")
    print()
    print("USAGE GUIDANCE:")
    print("- Use EXACT MATCH when user wants strict adherence to all criteria")
    print("- Use GOAL-ONLY when user prioritizes goal achievement over other factors")
    print("- Goal-only system provides more variety and flexibility")
elif exact_count == 0 and goal_count > 0:
    print("⚠️  No exact matches, but goal-only system has recommendations")
    print("→ Suggest using goal-only system or adjusting profile criteria")
elif exact_count == 0 and goal_count == 0:
    print("❌ No plans found in either system")
    print("→ Check if plans exist for this goal + region combination")
else:
    print("✅ Exact matches found, goal-only provides additional options")
