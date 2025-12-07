import json

with open('outputs/pdf_index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

cat_sum = sum(data['metadata']['category'].values())
print(f"Plans with category: {cat_sum} / {data['metadata']['total_plans']}")
print(f"Missing: {data['metadata']['total_plans'] - cat_sum}")

# Show breakdown
print("\nCategory breakdown:")
for cat, count in sorted(data['metadata']['category'].items()):
    print(f"  {cat}: {count}")
