import json

with open('outputs/pdf_index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find plans without categories
missing = []
for plan in data['plans']:
    if 'category' not in plan:
        missing.append({
            'folder': plan.get('folder', 'N/A'),
            'filename': plan.get('filename', 'N/A')
        })

print(f"Plans without category: {len(missing)}\n")

# Group by folder
from collections import defaultdict
by_folder = defaultdict(list)
for item in missing:
    by_folder[item['folder']].append(item['filename'])

for folder in sorted(by_folder.keys()):
    print(f"\n{folder}:")
    for filename in by_folder[folder][:3]:  # Show first 3 examples
        print(f"  - {filename}")
    if len(by_folder[folder]) > 3:
        print(f"  ... and {len(by_folder[folder]) - 3} more")
