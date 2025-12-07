from service.pdf_parser import parse_pdf_complete

test_file = r"d:\Documents\Diet plan\outputs\raw\1\SKIN DETOX\skin detox male north indian non veg sedentary overweight.txt"

data = parse_pdf_complete(test_file)
meals = data['meals']

for meal in meals:
    print(f"\n{meal['meal_type']}: {len(meal['options'])} options")
    for i, opt in enumerate(meal['options'][:5], 1):  # Show first 5
        print(f"  {i}. {opt['name'][:60]}")
