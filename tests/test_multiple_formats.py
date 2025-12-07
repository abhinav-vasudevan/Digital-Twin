import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from service.pdf_parser import CompletePDFParser
import random
import glob

# Get random PDFs from database
pdf_files = glob.glob(r"D:\Documents\Diet plan\outputs\raw\**\*.txt", recursive=True)
test_samples = random.sample(pdf_files, min(5, len(pdf_files)))

parser = CompletePDFParser()

print("=" * 80)
print("TESTING PDF PARSER WITH MULTIPLE FORMAT VARIATIONS")
print("=" * 80)

for pdf_file in test_samples:
    result = parser.parse_complete_pdf(pdf_file)
    
    filename = os.path.basename(pdf_file)
    print(f"\n📄 {filename}")
    print(f"   Meals found: {len(result.get('meals', []))}")
    
    if len(result.get('meals', [])) == 0:
        print(f"   ⚠️ WARNING: No meals extracted!")
        # Show first 500 chars to diagnose
        with open(pdf_file, 'r', encoding='utf-8') as f:
            preview = f.read()[:500]
            print(f"   Preview: {preview[:200]}...")
    else:
        for meal in result.get('meals', []):
            options_count = len(meal.get('options', []))
            print(f"      ✓ {meal['meal_type']}: {options_count} option(s)")

print("\n" + "=" * 80)
print("✅ Test complete!")
print("=" * 80)
