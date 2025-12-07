"""
Test script to see RAW Llama 3 output for meal generation
This will show exactly what Llama generates before any parsing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.llama_service import LlamaService
import json
import time

def test_raw_output():
    print("=" * 80)
    print("🔬 RAW LLAMA 3 OUTPUT TEST - See exactly what AI generates")
    print("=" * 80)
    
    llama = LlamaService()
    
    profile = {
        "age": 25,
        "gender": "male",
        "current_weight": 75,
        "target_weight": 70,
        "goal": "weight loss",
        "diet_type": "vegetarian",
        "dietary_preferences": ["vegetarian"],
        "allergies": ["peanuts"],
        "height": 175,
        "activity_level": "moderate"
    }
    
    print("\n📋 Profile:")
    print(f"  {profile['age']}yr {profile['gender']}, {profile['current_weight']}kg → {profile['target_weight']}kg")
    print(f"  {profile['diet_type'].upper()}, allergies: {', '.join(profile['allergies'])}")
    
    # Test Day 1 generation with verbose prompt
    print("\n" + "=" * 80)
    print("🚀 Generating DAY 1 - Watching raw Llama output...")
    print("=" * 80)
    
    start = time.time()
    
    # Call the internal method to see raw response
    prompt = f"""You are a professional nutritionist creating a personalized diet plan.

Profile:
- Age: {profile['age']}, Gender: {profile['gender']}
- Current Weight: {profile['current_weight']}kg, Target: {profile['target_weight']}kg
- Goal: {profile['goal']}
- Diet: STRICTLY VEGETARIAN (NO meat, fish, chicken, eggs)
- Allergies: {', '.join(profile['allergies'])}
- Activity: {profile.get('activity_level', 'moderate')}

Create ONE day of meals with 5 meals (breakfast, lunch, dinner, snack_1, snack_2).

Requirements:
1. VEGETARIAN ONLY - Use paneer, tofu, lentils, chickpeas, beans, yogurt
2. NO {', '.join(profile['allergies'])} - STRICT ALLERGY SAFETY
3. Make meals INTERESTING, FLAVORFUL, and DIVERSE
4. Use Indian, Mediterranean, Asian cuisine variety
5. Include spices, herbs, and different cooking methods
6. Provide specific measurements and detailed cooking instructions

Return JSON ONLY (no other text):
{{
  "day_1": {{
    "breakfast": {{
      "name": "Meal name",
      "ingredients": ["ingredient1", "ingredient2"],
      "calories": 350,
      "protein": 15,
      "carbs": 45,
      "fats": 10,
      "instructions": "Detailed step-by-step cooking instructions"
    }},
    "lunch": {{ ... same structure ... }},
    "dinner": {{ ... same structure ... }},
    "snack_1": {{ ... same structure ... }},
    "snack_2": {{ ... same structure ... }}
  }}
}}

Example vegetarian meals:
- Breakfast: Masala oats with nuts, Paneer bhurji, Greek yogurt parfait
- Lunch: Palak paneer with roti, Dal makhani with rice, Chickpea curry
- Dinner: Grilled tofu tikka, Vegetable biryani, Lentil soup with quinoa
- Snacks: Roasted chickpeas, Fruit smoothie, Hummus with veggies

RESPOND WITH JSON ONLY - START WITH {{ and END WITH }}"""

    print("\n📤 Sending prompt to Llama 3...")
    print(f"📏 Prompt length: {len(prompt)} characters")
    
    raw_response = llama._call_ollama(prompt, temperature=0.8, max_tokens=-1)
    
    elapsed = time.time() - start
    print(f"\n⏱️  Generation time: {elapsed:.1f} seconds")
    print(f"📏 Raw response length: {len(raw_response)} characters")
    
    print("\n" + "=" * 80)
    print("📄 RAW LLAMA 3 OUTPUT (exactly as received):")
    print("=" * 80)
    print(raw_response)
    print("=" * 80)
    
    # Try to parse it
    print("\n🔍 Attempting to parse JSON...")
    try:
        # Try direct parse
        parsed = json.loads(raw_response)
        print("✅ Direct JSON parse successful!")
        print("\n📊 Parsed structure:")
        print(json.dumps(parsed, indent=2))
        
        # Save to file
        with open("llama_raw_output_day1.json", "w") as f:
            json.dump({
                "raw_response": raw_response,
                "parsed_data": parsed,
                "generation_time": elapsed,
                "profile": profile
            }, f, indent=2)
        print("\n💾 Saved to: llama_raw_output_day1.json")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse failed: {e}")
        print("\n🔧 Trying to extract JSON...")
        
        # Try to find JSON in response
        start_idx = raw_response.find('{')
        end_idx = raw_response.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            json_part = raw_response[start_idx:end_idx+1]
            print(f"\n📦 Extracted JSON part ({len(json_part)} chars):")
            print(json_part)
            
            try:
                parsed = json.loads(json_part)
                print("\n✅ Extracted JSON parsed successfully!")
                print(json.dumps(parsed, indent=2))
                
                with open("llama_raw_output_day1.json", "w") as f:
                    json.dump({
                        "raw_response": raw_response,
                        "extracted_json": json_part,
                        "parsed_data": parsed,
                        "generation_time": elapsed,
                        "profile": profile
                    }, f, indent=2)
                print("\n💾 Saved to: llama_raw_output_day1.json")
                
            except json.JSONDecodeError as e2:
                print(f"❌ Still failed: {e2}")
                
                with open("llama_raw_output_day1_failed.txt", "w") as f:
                    f.write(f"Generation time: {elapsed:.1f}s\n")
                    f.write(f"Response length: {len(raw_response)} chars\n")
                    f.write(f"\n{'='*80}\n")
                    f.write("RAW RESPONSE:\n")
                    f.write(f"{'='*80}\n")
                    f.write(raw_response)
                print("\n💾 Saved failed output to: llama_raw_output_day1_failed.txt")
        else:
            print("❌ No JSON found in response")
            with open("llama_raw_output_day1_failed.txt", "w") as f:
                f.write(raw_response)
            print("💾 Saved to: llama_raw_output_day1_failed.txt")

if __name__ == "__main__":
    test_raw_output()
