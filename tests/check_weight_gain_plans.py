import json

with open('outputs/pdf_index.json', encoding='utf-8') as f:
    idx = json.load(f)

# Check weight_gain plans
wg_plans = [p for p in idx['plans'] if p.get('category') == 'weight_gain']
print(f"Total weight_gain plans: {len(wg_plans)}")

# Filter by male
male_wg = [p for p in wg_plans if p.get('gender') == 'male']
print(f"Male weight_gain: {len(male_wg)}")

# Filter by light activity
male_light_wg = [p for p in male_wg if 'light' in p.get('activity', '').lower()]
print(f"Male + light + weight_gain: {len(male_light_wg)}")

if male_light_wg:
    print("\nDiet types in male + light + weight_gain plans:")
    diets = {}
    for p in male_light_wg:
        diet = p.get('diet_type', 'N/A')
        diets[diet] = diets.get(diet, 0) + 1
    for diet, count in diets.items():
        print(f"  {diet}: {count} plans")
    
    print("\nBMI categories:")
    bmis = {}
    for p in male_light_wg:
        bmi = p.get('bmi_category', 'N/A')
        bmis[bmi] = bmis.get(bmi, 0) + 1
    for bmi, count in bmis.items():
        print(f"  {bmi}: {count} plans")
    
    print("\nRegions:")
    regions = {}
    for p in male_light_wg:
        region = p.get('region', 'N/A')
        regions[region] = regions.get(region, 0) + 1
    for region, count in regions.items():
        print(f"  {region}: {count} plans")
    
    print("\nSample plans:")
    for i, p in enumerate(male_light_wg[:5], 1):
        print(f"{i}. {p['filename'][:70]}")
        print(f"   Diet: {p.get('diet_type')}, BMI: {p.get('bmi_category')}, Region: {p.get('region')}")
