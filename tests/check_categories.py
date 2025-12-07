import json

# Load the index
with open('outputs/pdf_index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# User's required categories
user_categories = [
    'acne and oily skin',
    'high protein high fiber',
    'typ -1 DM and wt loss',
    'protein rich balanced diet',
    'anti aging /sundamage/ fine lines',
    'edema',
    'anti inflamatory',
    'weight loss',
    'weight loss + pcos',
    'Gas + bloating',
    'insulin resistance + obesity',
    'hair loss and hair thining',
    'skin health diet plan',
    'wt gain for underweight and malnutrition',
    'probiotic rich diet',
    'gut detox diet',
    'liver detox',
    'digestive detox /gut clensing',
    'ayurvedic detox diet',
    'skin detox'
]

# Index categories
index_categories = data['metadata']['category']

print("="*70)
print("CATEGORY COVERAGE CHECK")
print("="*70)
print(f"\nTotal categories in index: {len(index_categories)}")
print(f"Total user requirements: {len(user_categories)}\n")

print("INDEX CATEGORIES:")
for cat, count in sorted(index_categories.items()):
    print(f"  ✓ {cat}: {count} plans")

print("\n" + "="*70)
print("CHECKING USER REQUIREMENTS:")
print("="*70)

found = []
missing = []

# Check each user category
for user_cat in user_categories:
    user_cat_normalized = user_cat.lower().strip()
    
    # Try to find matching category
    matched = False
    for idx_cat in index_categories.keys():
        idx_cat_normalized = idx_cat.lower().replace('_', ' ')
        
        # Check if user category is subset of index category or vice versa
        if user_cat_normalized.replace('/', '').replace('+', '').strip() in idx_cat_normalized:
            found.append((user_cat, idx_cat, index_categories[idx_cat]))
            matched = True
            break
        elif idx_cat_normalized in user_cat_normalized.replace('/', '').replace('+', '').strip():
            found.append((user_cat, idx_cat, index_categories[idx_cat]))
            matched = True
            break
        # Manual mappings for special cases
        elif 'acne' in user_cat_normalized and 'skin_health' in idx_cat:
            found.append((user_cat, idx_cat, index_categories[idx_cat]))
            matched = True
            break
        elif 'typ -1 dm' in user_cat_normalized and 'diabetes' in idx_cat:
            found.append((user_cat, idx_cat, index_categories[idx_cat]))
            matched = True
            break
        elif 'insulin resistance' in user_cat_normalized and 'weight_loss' in idx_cat:
            # May need special handling
            pass
        elif 'digestive detox' in user_cat_normalized and 'gut_cleanse' in idx_cat:
            found.append((user_cat, idx_cat, index_categories[idx_cat]))
            matched = True
            break
    
    if not matched:
        missing.append(user_cat)

print(f"\n✓ FOUND ({len(found)}):")
for user_cat, idx_cat, count in sorted(found):
    print(f"  ✓ '{user_cat}' → {idx_cat} ({count} plans)")

print(f"\n✗ MISSING ({len(missing)}):")
for cat in sorted(missing):
    print(f"  ✗ '{cat}' - NO MATCHING CATEGORY")

print("\n" + "="*70)
print(f"COVERAGE: {len(found)}/{len(user_categories)} = {len(found)/len(user_categories)*100:.1f}%")
print("="*70)
