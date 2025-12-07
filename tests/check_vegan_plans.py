import json

with open('outputs/pdf_index.json', encoding='utf-8') as f:
    data = json.load(f)

vegan_plans = [p for p in data['plans'] if p.get('diet_type') == 'vegan']

print(f"Total vegan plans: {len(vegan_plans)}")
print("\nFirst 10 vegan diet plans:\n")

for i, plan in enumerate(vegan_plans[:10], 1):
    print(f"{i}. {plan['filename']}")
    print(f"   Category: {plan.get('category', 'N/A')}")
    print(f"   Region: {plan.get('region', 'N/A')}")
    print(f"   Gender: {plan.get('gender', 'N/A')} | BMI: {plan.get('bmi_category', 'N/A')}")
    print()
