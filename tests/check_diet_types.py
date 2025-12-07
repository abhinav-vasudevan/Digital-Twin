import json

with open('outputs/pdf_index.json', encoding='utf-8') as f:
    data = json.load(f)

# Check all diet types including None
diet_types = {}
for plan in data['plans']:
    dt = plan.get('diet_type')
    diet_types[dt] = diet_types.get(dt, 0) + 1

print("All diet types found in index:")
for diet, count in sorted(diet_types.items(), key=lambda x: (x[0] is None, x[0])):
    print(f"  {diet}: {count}")

print("\nChecking for 'egg' in filenames where diet_type is None:")
egg_files = [p for p in data['plans'] if p.get('diet_type') is None and 'egg' in p.get('filename', '').lower()]
print(f"Found {len(egg_files)} files with 'egg' in name but diet_type=None")
if egg_files:
    print("\nFirst 5 examples:")
    for i, p in enumerate(egg_files[:5], 1):
        print(f"{i}. {p['filename']}")
