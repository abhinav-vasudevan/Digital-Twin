import json

with open('outputs/pdf_index.json', encoding='utf-8') as f:
    idx = json.load(f)

# Manual filtering
plans = idx['plans']
plans = [p for p in plans if p.get('gender') == 'male']
plans = [p for p in plans if p.get('bmi_category') == 'underweight']
plans = [p for p in plans if 'light' in p.get('activity', '').lower()]
plans = [p for p in plans if p.get('diet_type') in [None, 'vegan', 'vegetarian']]

print(f"Found {len(plans)} plans matching: male + underweight + light + vegetarian")
print("\nChecking Region and Category:")
print("="*80)

for i, p in enumerate(plans, 1):
    print(f"\n{i}. {p['filename'][:70]}")
    print(f"   Region: {p.get('region', 'N/A')}")
    print(f"   Category: {p.get('category', 'N/A')}")
    print(f"   Diet: {p.get('diet_type', 'N/A')}")

print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)

regions = {}
categories = {}
for p in plans:
    region = p.get('region', 'N/A')
    category = p.get('category', 'N/A')
    regions[region] = regions.get(region, 0) + 1
    categories[category] = categories.get(category, 0) + 1

print("\nRegion distribution:")
for r, c in regions.items():
    print(f"  {r}: {c} plans")

print("\nCategory distribution:")
for cat, c in categories.items():
    print(f"  {cat}: {c} plans")

print("\n⚠️ USER WANTS:")
print("  Region: south_indian")
print("  Category: weight_gain")

# Check matches
matching = [p for p in plans if p.get('region') == 'south_indian' and p.get('category') == 'weight_gain']
print(f"\n✅ Plans matching ALL criteria: {len(matching)}")

if matching:
    for p in matching:
        print(f"  - {p['filename']}")
else:
    print("  ❌ NO EXACT MATCHES")
    print("\n  Closest matches (south_indian only):")
    south = [p for p in plans if p.get('region') == 'south_indian']
    if south:
        for p in south:
            print(f"    - {p['filename'][:70]}")
            print(f"      Category: {p.get('category')}")
    else:
        print("    None")
    
    print("\n  Closest matches (weight_gain only):")
    wg = [p for p in plans if p.get('category') == 'weight_gain']
    if wg:
        for p in wg:
            print(f"    - {p['filename'][:70]}")
            print(f"      Region: {p.get('region')}")
    else:
        print("    None")
