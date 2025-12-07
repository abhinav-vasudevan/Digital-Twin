"""
DETAILED ExactMatch PDF System Test
Tests 2 PDFs per goal and shows sample extracted content
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.pdf_parser import CompletePDFParser
import random
from pathlib import Path

GOAL_CATEGORIES = {
    'weight_loss': ['weight_loss', 'weight_loss_pcos', 'weight_loss_diabetes'],
    'weight_gain': ['weight_gain', 'underweight', 'malnutrition'],
    'muscle_gain': ['muscle_gain', 'high_protein'],
    'gut_health': ['gut_health', 'gut_detox', 'gut_cleanse_digestive_detox', 'probiotic'],
    'skin_health': ['skin_health', 'skin_detox'],
    'liver_detox': ['liver_detox'],
    'clear_skin': ['skin_health', 'skin_detox'],
    'anti_aging': ['anti_aging'],
    'hair_health': ['hair_loss', 'hair_thinning']
}

def find_pdfs_by_category(base_path, category_keywords):
    """Find PDFs matching any of the category keywords"""
    pdf_files = []
    base = Path(base_path)
    all_pdfs = list(base.glob("**/*.txt"))
    
    for pdf_path in all_pdfs:
        path_str = str(pdf_path).lower()
        for keyword in category_keywords:
            search_terms = keyword.lower().replace('_', ' ').split()
            if any(term in path_str for term in search_terms):
                pdf_files.append(pdf_path)
                break
    
    return list(set(pdf_files))

def show_sample_content(result, max_options_to_show=2):
    """Show sample of extracted content"""
    print(f"\n      📋 Sample Content:")
    
    # Show title
    if result.get('title'):
        title = result['title'][:80] + "..." if len(result['title']) > 80 else result['title']
        print(f"         Title: {title}")
    
    # Show overall nutrition
    if result.get('overall_nutrition'):
        nutr = result['overall_nutrition']
        items = []
        for key in ['calories', 'protein', 'carbs', 'fat']:
            if key in nutr:
                items.append(f"{key.capitalize()}: {nutr[key]}")
        if items:
            print(f"         Overall Nutrition: {', '.join(items[:3])}")
    
    # Show first meal with options
    meals = result.get('meals', [])
    if meals:
        first_meal = meals[0]
        print(f"\n         Sample Meal: {first_meal['meal_type']}")
        
        options = first_meal.get('options', [])
        for i, opt in enumerate(options[:max_options_to_show]):
            opt_num = opt.get('option_number', '?')
            name = opt.get('name', 'No name')[:60]
            ingredients = opt.get('ingredients', '')[:80]
            
            print(f"           Option {opt_num}: {name}")
            if ingredients:
                print(f"              Ingredients: {ingredients}...")
            if opt.get('serving'):
                print(f"              Serving: {opt['serving']}")

def main():
    base_path = r"D:\Documents\Diet plan\outputs\raw"
    parser = CompletePDFParser()
    
    print("=" * 100)
    print("DETAILED EXACTMATCH PDF SYSTEM TEST")
    print("Testing 2 random PDFs per goal category with content samples")
    print("=" * 100)
    
    all_passed = True
    
    for goal, categories in GOAL_CATEGORIES.items():
        print(f"\n{'=' * 100}")
        print(f"🎯 {goal.upper()}")
        print(f"{'=' * 100}")
        
        pdf_files = find_pdfs_by_category(base_path, categories)
        
        if not pdf_files:
            print(f"⚠️  No PDFs found")
            continue
        
        test_samples = random.sample(pdf_files, min(2, len(pdf_files)))
        
        for i, pdf_path in enumerate(test_samples, 1):
            filename = pdf_path.name
            print(f"\n   Test {i}/2: {filename[:75]}")
            
            result = parser.parse_complete_pdf(str(pdf_path))
            
            if 'error' in result:
                print(f"      ❌ ERROR: {result['error']}")
                all_passed = False
                continue
            
            meals = result.get('meals', [])
            total_options = sum(len(m.get('options', [])) for m in meals)
            
            print(f"      ✅ Meals: {len(meals)} | Options: {total_options}")
            
            # Check completeness
            issues = []
            if len(meals) < 5:
                issues.append(f"Only {len(meals)} meals")
            if total_options == 0:
                issues.append("No options extracted")
            if not result.get('title'):
                issues.append("No title")
            
            if issues:
                print(f"      ⚠️  Issues: {', '.join(issues)}")
                all_passed = False
            
            # Show sample content
            show_sample_content(result)
    
    print("\n" + "=" * 100)
    if all_passed:
        print("🎉 SUCCESS: All PDFs extracted completely!")
    else:
        print("⚠️  Some PDFs had issues")
    print("=" * 100)

if __name__ == "__main__":
    main()
