import json

with open('outputs/pdf_index.json', encoding='utf-8') as f:
    idx = json.load(f)

# Check weight_gain plans
wg_plans = [p for p in idx['plans'] if 'weight gain' in p['filename'].lower() and p['gender']=='male'][:5]

print("CHECKING INGREDIENTS IN WEIGHT GAIN PLANS:")
print("="*80)
for i, p in enumerate(wg_plans, 1):
    print(f"\n{i}. {p['filename'][:70]}")
    ingredients = p.get('ingredients', [])
    print(f"   Ingredients: {ingredients[:15]}")
    
    # Check for nuts
    has_nuts = any('nut' in ing.lower() for ing in ingredients)
    print(f"   Contains nuts: {has_nuts}")
