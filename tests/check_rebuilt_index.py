import json

with open('outputs/pdf_index.json', encoding='utf-8') as f:
    idx = json.load(f)

print("Categories in metadata:", idx['metadata'].get('category', {}))
print(f"\nTotal plans: {len(idx['plans'])}")

# Check first 10 plans
print("\nFirst 10 plans - checking diet_type:")
for i, p in enumerate(idx['plans'][:10], 1):
    print(f"\n{i}. {p['filename'][:70]}")
    print(f"   Diet: {p.get('diet_type', 'MISSING')}")
    print(f"   Category: {p.get('category', 'MISSING')}")
    print(f"   Region: {p.get('region', 'MISSING')}")
    print(f"   BMI: {p.get('bmi_category', 'MISSING')}")
