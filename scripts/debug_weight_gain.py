import json

with open('outputs/pdf_index.json', encoding='utf-8') as f:
    idx = json.load(f)

# User profile
user = {
    'gender': 'male',
    'bmi_category': 'normal',
    'activity': 'light',
    'diet': 'vegetarian',
    'region': 'south_indian',
    'goal': 'weight_gain'
}

# All weight gain plans
wg_plans = [p for p in idx['plans'] if p.get('category') == 'weight_gain']
print(f"Total weight_gain plans: {len(wg_plans)}")

# Filter step by step
print("\nFILTERING WEIGHT GAIN PLANS:")
print("="*80)

# Gender
gender_match = [p for p in wg_plans if p.get('gender') == user['gender']]
print(f"1. Gender (male): {len(gender_match)}/{len(wg_plans)}")

# BMI
bmi_match = [p for p in gender_match if p.get('bmi_category') == user['bmi_category']]
print(f"2. BMI (normal): {len(bmi_match)}/{len(gender_match)}")
print(f"   ❌ PROBLEM: Weight gain plans are for 'underweight', not 'normal'")

# Show BMI distribution
print(f"\n   BMI categories in male weight_gain plans:")
bmis = {}
for p in gender_match:
    bmi = p.get('bmi_category', 'N/A')
    bmis[bmi] = bmis.get(bmi, 0) + 1
for bmi, count in bmis.items():
    print(f"      {bmi}: {count} plans")

# Activity (if BMI matched)
if bmi_match:
    activity_match = [p for p in bmi_match if 'light' in p.get('activity', '').lower()]
    print(f"3. Activity (light): {len(activity_match)}/{len(bmi_match)}")
else:
    print(f"3. Activity: Can't check (no BMI matches)")

# Check what user's actual BMI should be
print("\n" + "="*80)
print("USER BMI ANALYSIS:")
print("="*80)
weight = 60
height = 178
bmi = weight / ((height/100)**2)
print(f"Weight: {weight} kg")
print(f"Height: {height} cm")
print(f"Calculated BMI: {bmi:.1f}")
print(f"Current category in profile.json: 'normal' (18.5-24.9)")
print(f"Actual category: {'underweight' if bmi < 18.5 else 'normal'}")
print(f"\n⚠️ BMI {bmi:.1f} is BORDERLINE - just above 18.5 threshold!")
print(f"   For weight_gain goal, user should be categorized as 'underweight'")

print("\n" + "="*80)
print("SOLUTION:")
print("="*80)
print("The profile.json has bmi: 18.9 which is being categorized as 'normal'")
print("But weight_gain plans are designed for 'underweight' users.")
print("\nOptions:")
print("1. Change BMI threshold: 18.5-19.5 → 'underweight' for weight gain goals")
print("2. User's actual BMI 18.9 should map to 'underweight' in the context")
print("3. Remove BMI as hard constraint (match only: gender, activity, diet, region, category)")
