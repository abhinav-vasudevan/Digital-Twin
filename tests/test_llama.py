import requests
import json
import time

print("Testing Llama 3 with BATCH approach (3 days at a time)...")
print("=" * 60)

def test_ollama_batch(start_day, end_day):
    """Test generating a batch of days"""
    num_days = end_day - start_day + 1
    print(f"\n📋 Testing batch: days {start_day}-{end_day} ({num_days} days)")
    
    prompt = f"""Generate a {num_days}-day meal plan in JSON format for days {start_day} to {end_day}.

Return ONLY valid JSON (no extra text):
{{
  "meal_plan": {{
    "day_{start_day}": {{
      "breakfast": {{"name": "Oatmeal with Banana", "ingredients": ["250g oats", "100g banana", "15g honey"], "calories": 350, "protein_g": 10, "carbs_g": 60, "fats_g": 8, "instructions": "Cook oats, top with banana"}},
      "lunch": {{"name": "Chicken Wrap", "ingredients": ["1 tortilla", "100g chicken", "50g lettuce"], "calories": 450, "protein_g": 30, "carbs_g": 45, "fats_g": 15, "instructions": "Wrap ingredients"}},
      "dinner": {{"name": "Rice Bowl", "ingredients": ["200g rice", "100g vegetables"], "calories": 500, "protein_g": 15, "carbs_g": 80, "fats_g": 12, "instructions": "Cook rice, mix vegetables"}},
      "snack_1": {{"name": "Apple", "ingredients": ["1 apple"], "calories": 80, "protein_g": 0, "carbs_g": 20, "fats_g": 0, "instructions": "Wash and eat"}},
      "snack_2": {{"name": "Almonds", "ingredients": ["30g almonds"], "calories": 170, "protein_g": 6, "carbs_g": 6, "fats_g": 15, "instructions": "Portion and eat"}}
    }}{"," if num_days > 1 else ""}
    {"day_" + str(start_day+1) + ": {...}," if num_days > 1 else ""}
    {"day_" + str(start_day+2) + ": {...}" if num_days > 2 else ""}
  }}
}}"""
    
    start_time = time.time()
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3',
                'prompt': prompt,
                'stream': False,
                'options': {
                    'num_predict': -1,
                    'temperature': 0.3
                }
            },
            timeout=120
        )
        
        elapsed = time.time() - start_time
        result = response.json()
        llama_response = result.get('response', '')
        
        print(f"  ⏱️  Time taken: {elapsed:.1f} seconds")
        print(f"  📏 Response length: {len(llama_response)} characters")
        print(f"  🔚 Has closing brace: {'}' in llama_response[-50:]}")
        
        # Try to parse JSON
        json_start = llama_response.find('{')
        json_end = llama_response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = llama_response[json_start:json_end]
            meal_plan = json.loads(json_str)
            
            days_generated = len(meal_plan.get('meal_plan', {}))
            print(f"  ✅ SUCCESS! Parsed {days_generated} days")
            print(f"  📅 Day keys: {list(meal_plan.get('meal_plan', {}).keys())}")
            
            return meal_plan.get('meal_plan', {})
        else:
            print(f"  ❌ No JSON object found")
            print(f"  First 200 chars: {llama_response[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"  ❌ TIMEOUT after {elapsed:.1f} seconds")
        return None
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON Parse Error: {e}")
        print(f"  Context: ...{llama_response[max(0, e.pos-100):e.pos+100]}...")
        return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

# Test strategy: Generate ONE day at a time
print("\n🚀 Starting single-day generation test...")
all_days = {}

for day_num in range(1, 4):  # Test first 3 days
    batch = test_ollama_batch(day_num, day_num)
    if batch:
        all_days.update(batch)
    else:
        print(f"\n❌ Day {day_num} failed, stopping test")
        exit(1)

# Final result
print("\n" + "=" * 60)
print(f"🎉 COMPLETE SUCCESS! Generated {len(all_days)} days total")
print(f"📅 All day keys: {sorted(all_days.keys())}")
print("\n✅ Batch approach works! Ready to integrate into website.")
