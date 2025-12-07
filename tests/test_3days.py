"""Test Llama 3 meal plan generation for 3 days"""
import sys
sys.path.insert(0, 'd:\\Documents\\Diet plan')

from service.llama_service import LlamaService
import json

# Sample profile
profile = {
    "age": 25,
    "gender": "male",
    "current_weight": 75,
    "target_weight": 70,
    "goal": "weight loss",
    "diet_type": "vegetarian",
    "allergies": ["peanuts"]
}

print("=" * 70)
print("Testing Llama 3 Meal Plan Generation - 3 Days (Vegetarian)")
print("=" * 70)
print(f"\n📋 Profile:")
print(f"  Age: {profile['age']}, Gender: {profile['gender']}")
print(f"  Weight: {profile['current_weight']}kg → {profile['target_weight']}kg")
print(f"  Goal: {profile['goal']}")
print(f"  Diet: {profile['diet_type'].upper()}")
print(f"  Allergies: {', '.join(profile['allergies'])}")

# Create service
llama = LlamaService()

# Generate plan
print("\n" + "=" * 70)
print("🚀 Starting generation...")
print("This will take approximately 5 minutes (3 days × 100 seconds each)")
print("=" * 70)

try:
    result = llama.generate_meal_plan(profile, days=3)
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS!")
    print("=" * 70)
    
    # Check structure
    if "meal_plan" in result:
        days_generated = len(result["meal_plan"])
        print(f"\n📅 Days generated: {days_generated}")
        print(f"📋 Day keys: {list(result['meal_plan'].keys())}")
        
        # Show ALL days in detail
        for day_key in sorted(result["meal_plan"].keys()):
            day_data = result["meal_plan"][day_key]
            day_num = day_key.split("_")[1]
            
            print(f"\n{'=' * 70}")
            print(f"📖 DAY {day_num} - FULL DETAILS")
            print(f"{'=' * 70}")
            
            # Show all meals
            for meal_type in ["breakfast", "lunch", "dinner", "snack_1", "snack_2"]:
                meal = day_data.get(meal_type, {})
                meal_name = meal_type.replace("_", " ").title()
                
                print(f"\n🍽️  {meal_name}:")
                print(f"   Name: {meal.get('name', 'N/A')}")
                print(f"   Ingredients: {', '.join(meal.get('ingredients', []))}")
                print(f"   Calories: {meal.get('calories', 'N/A')} kcal")
                print(f"   Protein: {meal.get('protein', 'MISSING')}g | Carbs: {meal.get('carbs', 'MISSING')}g | Fats: {meal.get('fats', 'MISSING')}g")
                print(f"   Instructions: {meal.get('instructions', 'N/A')}")
            
            # Daily totals for this day
            day_calories = sum([
                day_data.get(m, {}).get('calories', 0) 
                for m in ["breakfast", "lunch", "dinner", "snack_1", "snack_2"]
            ])
            day_protein = sum([
                day_data.get(m, {}).get('protein', 0) 
                for m in ["breakfast", "lunch", "dinner", "snack_1", "snack_2"]
            ])
            day_carbs = sum([
                day_data.get(m, {}).get('carbs', 0) 
                for m in ["breakfast", "lunch", "dinner", "snack_1", "snack_2"]
            ])
            day_fats = sum([
                day_data.get(m, {}).get('fats', 0) 
                for m in ["breakfast", "lunch", "dinner", "snack_1", "snack_2"]
            ])
            
            print(f"\n📊 Day {day_num} Totals:")
            print(f"   Total Calories: {day_calories} kcal")
            print(f"   Total Protein: {day_protein}g | Carbs: {day_carbs}g | Fats: {day_fats}g")
        
        # Overall summary
        print(f"\n{'=' * 70}")
        print(f"📊 OVERALL SUMMARY")
        print(f"{'=' * 70}")
        print(f"Safety Check: {result.get('safety_check', 'N/A')}")
        print(f"Rationale: {result.get('rationale', 'N/A')}")
        
        # Save to file for inspection
        with open('test_3day_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full result saved to: test_3day_result.json")
        
    else:
        print("\n❌ Result missing 'meal_plan' key")
        print(f"Result keys: {result.keys()}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
