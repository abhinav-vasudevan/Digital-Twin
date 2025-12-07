import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from service.pdf_parser import CompletePDFParser
from pathlib import Path

# Find the problematic PDF
pdf_files = list(Path(r"d:\Documents\Diet plan\outputs\raw").rglob("*Female _ Non-Veg _ South Indian _ Overweight _ Light Activity _ We*.txt"))

if pdf_files:
    test_file = pdf_files[0]
    print(f"Testing: {test_file.name}\n")
    
    parser = CompletePDFParser()
    result = parser.parse_complete_pdf(str(test_file))
    
    print(f"Meals found: {len(result.get('meals', []))}")
    for meal in result.get('meals', []):
        print(f"  - {meal['meal_type']}: {len(meal.get('options', []))} options")
else:
    print("PDF not found")
