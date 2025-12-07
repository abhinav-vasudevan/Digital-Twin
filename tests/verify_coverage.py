import json

with open('outputs/pdf_index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Your requirements
required_categories = {
    'acne and oily skin': 'skin_health',
    'high protein high fiber': 'high_protein_high_fiber',
    'typ -1 DM and wt loss': 'weight_loss_diabetes',
    'protein rich balanced diet': 'high_protein_balanced',
    'anti aging /sundamage/ fine lines': 'anti_aging',
    'edema': 'anti_inflammatory',
    'anti inflamatory': 'anti_inflammatory',
    'weight loss': 'weight_loss',
    'weight loss + pcos': 'weight_loss_pcos',
    'Gas + bloating': 'gas_bloating',
    'insulin resistance + obesity': 'insulin_resistance',
    'hair loss and hair thining': 'hair_loss',
    'skin health diet plan': 'skin_health',
    'wt gain for underweight and malnutrition': 'weight_gain',
    'probiotic rich diet': 'probiotic',
    'gut detox diet': 'gut_detox',
    'liver detox': 'liver_detox',
    'digestive detox /gut clensing': 'gut_cleanse_digestive_detox',
    'ayurvedic detox diet': 'ayurvedic_detox',
    'skin detox': 'skin_detox',
}

# Available categories
available = data['metadata']['category']

print("="*80)
print("CATEGORY COVERAGE ANALYSIS")
print("="*80)
print(f"\nTotal Plans Indexed: {data['metadata']['total_plans']}")
print(f"Total Categories: {len(available)}")
print()

# Check each requirement
print("YOUR REQUIREMENTS vs SYSTEM CATEGORIES:")
print("-"*80)

covered = []
missing = []

for req, expected_cat in required_categories.items():
    count = available.get(expected_cat, 0)
    status = "✅" if count > 0 else "❌"
    
    if count > 0:
        covered.append((req, expected_cat, count))
        print(f"{status} {req:45} -> {expected_cat:30} ({count} plans)")
    else:
        missing.append((req, expected_cat))
        print(f"{status} {req:45} -> {expected_cat:30} (MISSING)")

print()
print("="*80)
print(f"COVERAGE: {len(covered)}/{len(required_categories)} categories covered")
print("="*80)

if missing:
    print("\n⚠️  MISSING CATEGORIES:")
    for req, cat in missing:
        print(f"   - {req} (expected as '{cat}')")
else:
    print("\n✅ ALL CATEGORIES COVERED!")

print()
print("="*80)
print("FULL CATEGORY BREAKDOWN:")
print("="*80)
for cat, count in sorted(available.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cat:40} : {count:3} plans")
