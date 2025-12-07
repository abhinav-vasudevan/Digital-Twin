"""
Test the new PDF-based /api/meal-plan/generate endpoint
"""
import requests
import json
from pathlib import Path

# Create test profile
DATA_DIR = Path("service/data")
DATA_DIR.mkdir(exist_ok=True)

test_profile = {
    "name": "Test User",
    "age": 26,
    "sex": "Female",
    "height": 160,
    "weight": 78,
    "bmi": 30.5,
    "weight_class": "Obese",
    "activity": "Light Activity",
    "region": "North Indian",
    "diet_type": "Vegetarian",
    "goal": "Weight Loss",
    "conditions": ["PCOS"],
    "preferences": {
        "allergies": [],
        "dislikes": []
    },
    "plan_start_date": "2024-01-01"
}

# Save profile
profile_path = DATA_DIR / "profile.json"
profile_path.write_text(json.dumps(test_profile, indent=2))
print(f"✅ Created test profile at {profile_path}")

# Test data to send
test_data = {}

print("\n" + "="*80)
print("Testing /api/meal-plan/generate with PDF Recommender")
print("="*80)

# Make request
try:
    response = requests.post("http://localhost:8000/api/meal-plan/generate", json=test_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS! Got {len(result.get('recommendations', []))} recommendations")
        
        print("\nTOP 5 RECOMMENDATIONS:")
        for i, rec in enumerate(result.get('recommendations', [])[:5], 1):
            print(f"\n{i}. {rec.get('filename', 'N/A')[:70]}")
            print(f"   Category: {rec.get('category')}")
            print(f"   Score: {rec.get('score')}")
            print(f"   Age Range: {rec.get('age_range')}")
            print(f"   Calories: {rec.get('calories')} kcal")
            print(f"   Protein: {rec.get('protein')}")
            if rec.get('age_adjusted'):
                adj = rec.get('age_adjustment', 0)
                print(f"   ✅ Age Adjusted: {'+' if adj > 0 else ''}{adj} kcal")
    else:
        print(f"❌ ERROR: Status {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n⚠️ Server not running. Start with: python -m uvicorn service.api:app --reload")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*80)
print("NEXT STEPS:")
print("1. Start server: python -m uvicorn service.api:app --reload")
print("2. Open browser: http://localhost:8000/generate-plan")
print("3. Select 2-5 plans from recommendations")
print("4. System will generate 14-day rotation")
print("="*80)
