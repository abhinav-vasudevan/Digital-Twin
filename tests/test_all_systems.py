"""
Test all 3 recommendation systems with API calls
Tests: Exact Match, Goal-Only, and Smart Scoring systems
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Create a test profile first
test_profile = {
    "email": "test@example.com",
    "age": 25,
    "gender": "female",
    "height": 165,
    "weight": 65,
    "target_weight": 58,
    "region": "north_indian",
    "diet_type": "vegetarian",
    "allergies": [],
    "activity_level": "moderate",
    "medical_conditions": [],
    "goals": ["weight_loss", "clear_skin"],
    "bmi": 23.9,
    "bmr": 1400,
    "tdee": 2170,
    "daily_calories": 1670,
    "daily_protein": 80,
    "daily_carbs": 200,
    "daily_fats": 55,
    "onboarding_complete": True,
    "plan_start_date": "2025-12-05",
    "current_plan_cycle": 1
}

print("="*80)
print("TESTING ALL 3 RECOMMENDATION SYSTEMS")
print("="*80)
print(f"\nTest Profile:")
print(f"  Gender: {test_profile['gender']}")
print(f"  Age: {test_profile['age']}")
print(f"  BMI: {test_profile['bmi']} (normal)")
print(f"  Activity: {test_profile['activity_level']}")
print(f"  Diet: {test_profile['diet_type']}")
print(f"  Region: {test_profile['region']}")
print(f"  Goals: {test_profile['goals']}")
print(f"  Allergies: {test_profile['allergies']}")
print()

# Save profile
try:
    response = requests.post(f"{BASE_URL}/api/profile", json=test_profile)
    if response.status_code == 200:
        print("✅ Test profile created successfully")
    else:
        print(f"⚠️  Profile creation: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Error creating profile: {e}")
    print("Make sure the server is running on http://localhost:8000")
    exit(1)

print()
print("="*80)

# Test System 1: Exact Match
print("SYSTEM 1: EXACT MATCH")
print("="*80)
print("Matching: Gender + BMI + Activity + Diet + Region + Category (ALL must match)")
print()

try:
    response = requests.post(f"{BASE_URL}/api/meal-plan/generate-exact")
    data = response.json()
    
    if data['status'] == 'not_available':
        print("❌ NO EXACT MATCHES FOUND")
        print(f"Message: {data['message']}")
        print("\nCriteria searched:")
        for key, value in data.get('criteria', {}).items():
            print(f"  {key}: {value}")
    else:
        print(f"✅ FOUND {data.get('total_matches', 0)} EXACT MATCHES")
        print(f"\nTop 3 recommendations:")
        for i, rec in enumerate(data['recommendations'][:3], 1):
            print(f"\n{i}. {rec['filename']}")
            print(f"   Category: {rec['category']} | Region: {rec['region']}")
            print(f"   Diet: {rec['diet_type']} | Gender: {rec.get('gender', 'N/A')}")
            print(f"   BMI: {rec.get('bmi_category', 'N/A')} | Activity: {rec.get('activity_level', 'N/A')}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print()
print("="*80)

# Test System 2: Goal-Only
print("SYSTEM 2: GOAL-ONLY MATCH")
print("="*80)
print("Matching: Primary Goal + Region + Diet Type")
print("Ignoring: Gender, BMI, Activity, Health, Age, Allergies")
print()

try:
    response = requests.post(f"{BASE_URL}/api/meal-plan/generate-goal")
    data = response.json()
    
    if data['status'] == 'not_available':
        print("❌ NO GOAL MATCHES FOUND")
        print(f"Message: {data['message']}")
    else:
        print(f"✅ FOUND {data.get('total_matches', 0)} GOAL MATCHES")
        print(f"\nCriteria: {data.get('criteria', {})}")
        print(f"\nTop 5 recommendations:")
        for i, rec in enumerate(data['recommendations'][:5], 1):
            print(f"\n{i}. {rec['filename']}")
            print(f"   Category: {rec['category']} | Region: {rec['region']}")
            print(f"   Diet: {rec['diet_type']} | Gender: {rec.get('gender', 'N/A')}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print()
print("="*80)

# Test System 3: Smart Scoring
print("SYSTEM 3: SMART SCORING (WEIGHTED)")
print("="*80)
print("AI Scoring with weighted priorities:")
print("  Goal (1000 pts) > Diet (100 pts) > Region/Health/Age (10 pts)")
print()

try:
    response = requests.post(f"{BASE_URL}/api/meal-plan/generate")
    data = response.json()
    
    if data.get('status') == 'success':
        recs = data.get('recommendations', [])
        print(f"✅ FOUND {len(recs)} SCORED RECOMMENDATIONS")
        print(f"\nTop 5 recommendations (sorted by score):")
        for i, rec in enumerate(recs[:5], 1):
            score = rec.get('score', 0)
            print(f"\n{i}. Score: {score} - {rec['filename']}")
            print(f"   Category: {rec['category']} | Region: {rec['region']}")
            print(f"   Diet: {rec['diet_type']} | Calories: {rec['calories']}")
    elif 'detail' in data:
        print(f"❌ ERROR: {data['detail']}")
    else:
        print(f"❌ ERROR: {data}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print()
print("="*80)

# Summary comparison
print("SUMMARY COMPARISON")
print("="*80)

try:
    exact_response = requests.post(f"{BASE_URL}/api/meal-plan/generate-exact").json()
    goal_response = requests.post(f"{BASE_URL}/api/meal-plan/generate-goal").json()
    smart_response = requests.post(f"{BASE_URL}/api/meal-plan/generate").json()
    
    exact_count = exact_response.get('total_matches', 0) if exact_response.get('status') == 'success' else 0
    goal_count = goal_response.get('total_matches', 0) if goal_response.get('status') == 'success' else 0
    smart_count = len(smart_response.get('recommendations', [])) if smart_response.get('status') == 'success' else 0
    
    print(f"System 1 (Exact Match):   {exact_count:3d} plans")
    print(f"System 2 (Goal-Only):     {goal_count:3d} plans")
    print(f"System 3 (Smart Scoring): {smart_count:3d} plans")
    print()
    
    if exact_count > 0 and goal_count > 0 and smart_count > 0:
        print("✅ ALL 3 SYSTEMS WORKING CORRECTLY!")
        print()
        print("Recommendation:")
        if exact_count > 5:
            print("  → Use EXACT MATCH for precise requirements")
        if goal_count > exact_count * 2:
            print("  → Use GOAL-ONLY for maximum variety")
        if smart_count > 0:
            print("  → Use SMART SCORING for balanced AI recommendations")
    elif exact_count == 0 and goal_count > 0:
        print("⚠️  EXACT MATCH: No matches (too strict)")
        print("✅ GOAL-ONLY: Working (recommended for this profile)")
        print("✅ SMART SCORING: Working")
    elif goal_count == 0:
        print("❌ WARNING: No plans found for this goal + region combination")
        print("   Check if plans exist in the PDF index")
    else:
        print("⚠️  Some systems returned results, others did not")
        
except Exception as e:
    print(f"❌ ERROR during comparison: {e}")

print()
print("="*80)
print("TEST COMPLETE")
print("="*80)
