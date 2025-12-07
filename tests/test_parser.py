import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from service.pdf_parser import CompletePDFParser

# Test with the 'Acne & Oily Skin' PDF
parser = CompletePDFParser()
test_file = r"D:\Documents\Diet plan\outputs\raw\1\skin health diet plans\acne and oily skin diet plan.txt"
result = parser.parse_complete_pdf(test_file)

if 'error' in result:
    print(f'ERROR: {result["error"]}')
else:
    print(f'Title: {result["title"]}')
    print(f'\nMeals found: {len(result["meals"])}')
    
    for meal in result['meals']:
        options_count = len(meal.get('options', []))
        print(f'  - {meal["meal_type"]}: {options_count} options')
        if options_count > 0:
            for opt in meal['options']:
                print(f'      Option {opt.get("option_number", "?")}: {opt["name"]}')
