"""
Comprehensive category coverage analysis
"""

# User's required categories
user_requirements = [
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

# Actual folders in the system
actual_folders = [
    'anti inflamatory',
    'ANTI-AGING ,SUN DAMAGE,FINE LINES DIET PLAN',
    'AYURVEDIC DETOX',
    'GAS + BLOATING',
    'GUT CLEANSE DIGESTIVE DETOX',
    'GUT DETOX DIET',
    'hair loss and hair thinning diet',
    'high protein balanced diet',
    'high protein high fiber',
    'LIVER DETOX',
    'PROBIOTIC RICH DIET',
    'SKIN DETOX',
    'SKIN HEALTH',
    'skin health diet plans',
    'weight gain for underweight n malnutrition',
    'weight loss + pcos',
    'WEIGHT LOSS ONLY',
    'weight loss+ typ 1 diabetes'
]

# Index categories (from our built index)
index_categories = {
    'anti_aging': 13,
    'anti_inflammatory': 20,
    'ayurvedic_detox': 32,
    'gas_bloating': 40,
    'gut_cleanse_digestive_detox': 35,
    'hair_loss': 18,
    'high_protein_balanced': 22,
    'high_protein_high_fiber': 39,
    'liver_detox': 20,
    'probiotic': 16,
    'skin_detox': 30,
    'skin_health': 65,
    'weight_gain': 39,
    'weight_loss': 16,
    'weight_loss_diabetes': 15,
    'weight_loss_pcos': 40
}

# Manual mapping
mappings = [
    ('acne and oily skin', 'SKIN HEALTH', 'skin_health', 65),
    ('high protein high fiber', 'high protein high fiber', 'high_protein_high_fiber', 39),
    ('typ -1 DM and wt loss', 'weight loss+ typ 1 diabetes', 'weight_loss_diabetes', 15),
    ('protein rich balanced diet', 'high protein balanced diet', 'high_protein_balanced', 22),
    ('anti aging /sundamage/ fine lines', 'ANTI-AGING ,SUN DAMAGE,FINE LINES DIET PLAN', 'anti_aging', 13),
    ('edema', None, None, 0),  # NOT FOUND
    ('anti inflamatory', 'anti inflamatory', 'anti_inflammatory', 20),
    ('weight loss', 'WEIGHT LOSS ONLY', 'weight_loss', 16),
    ('weight loss + pcos', 'weight loss + pcos', 'weight_loss_pcos', 40),
    ('Gas + bloating', 'GAS + BLOATING', 'gas_bloating', 40),
    ('insulin resistance + obesity', None, None, 0),  # NOT FOUND
    ('hair loss and hair thining', 'hair loss and hair thinning diet', 'hair_loss', 18),
    ('skin health diet plan', 'skin health diet plans', 'skin_health', 65),
    ('wt gain for underweight and malnutrition', 'weight gain for underweight n malnutrition', 'weight_gain', 39),
    ('probiotic rich diet', 'PROBIOTIC RICH DIET', 'probiotic', 16),
    ('gut detox diet', 'GUT DETOX DIET', None, 0),  # Folder exists but not in index!
    ('liver detox', 'LIVER DETOX', 'liver_detox', 20),
    ('digestive detox /gut clensing', 'GUT CLEANSE DIGESTIVE DETOX', 'gut_cleanse_digestive_detox', 35),
    ('ayurvedic detox diet', 'AYURVEDIC DETOX', 'ayurvedic_detox', 32),
    ('skin detox', 'SKIN DETOX', 'skin_detox', 30),
]

print("="*80)
print("COMPREHENSIVE CATEGORY COVERAGE ANALYSIS")
print("="*80)

print(f"\n{'USER REQUIREMENT':<40} {'STATUS':<10} {'PLANS':<10}")
print("-"*80)

covered_count = 0
missing_count = 0
folder_exists_but_not_indexed = 0

for user_req, folder, idx_cat, count in mappings:
    if folder and count > 0:
        status = "✓ FOUND"
        covered_count += 1
        print(f"{user_req:<40} {status:<10} {count:<10}")
    elif folder and count == 0:
        status = "⚠ FOLDER EXISTS, NOT INDEXED"
        folder_exists_but_not_indexed += 1
        print(f"{user_req:<40} {status:<10} {'-':<10}")
    else:
        status = "✗ MISSING"
        missing_count += 1
        print(f"{user_req:<40} {status:<10} {'-':<10}")

print("-"*80)
print(f"\nSUMMARY:")
print(f"  ✓ Covered: {covered_count}/{len(user_requirements)}")
print(f"  ⚠ Folder exists but not indexed: {folder_exists_but_not_indexed}")
print(f"  ✗ Missing completely: {missing_count}")
print(f"\nCoverage: {covered_count/len(user_requirements)*100:.1f}%")

print("\n" + "="*80)
print("MISSING CATEGORIES:")
print("="*80)

print("\n1. COMPLETELY MISSING (no folder, no plans):")
for user_req, folder, idx_cat, count in mappings:
    if not folder:
        print(f"   ✗ {user_req}")

print("\n2. FOLDER EXISTS BUT NOT INDEXED:")
for user_req, folder, idx_cat, count in mappings:
    if folder and count == 0:
        print(f"   ⚠ {user_req}")
        print(f"      Folder: '{folder}'")
        print(f"      Action needed: Check why PDFs from this folder weren't indexed")

print("\n" + "="*80)
