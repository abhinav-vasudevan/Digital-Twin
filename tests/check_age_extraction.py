import json

with open('outputs/pdf_index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check age extraction
print("AGE EXTRACTION VERIFICATION")
print("="*80)

plans_with_age = 0
age_examples = []

for plan in data['plans'][:20]:  # Check first 20
    age_info = plan.get('age_info', {})
    if age_info:
        plans_with_age += 1
        age_examples.append({
            'filename': plan['filename'][:60],
            'age_info': age_info
        })

print(f"Plans with age info: {plans_with_age}/{len(data['plans'])}")
print()

print("SAMPLE AGE EXTRACTIONS:")
print("-"*80)
for i, ex in enumerate(age_examples[:10], 1):
    print(f"{i}. {ex['filename']}")
    print(f"   Age: {ex['age_info']}")
    print()
