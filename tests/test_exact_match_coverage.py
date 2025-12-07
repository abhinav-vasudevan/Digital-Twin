"""
Test ExactMatch PDF System - Goal Coverage Test
Tests 2 random PDFs for each goal category to verify complete content extraction
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'service'))

from pdf_parser import CompletePDFParser
import json
import random
from pathlib import Path

# Goal categories from ExactMatch system
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
    
    # Get all txt files recursively
    all_pdfs = list(base.glob("**/*.txt"))
    
    for pdf_path in all_pdfs:
        # Check if any keyword matches in the full path (case-insensitive)
        path_str = str(pdf_path).lower()
        
        for keyword in category_keywords:
            # Convert keyword to search patterns
            search_terms = keyword.lower().replace('_', ' ').split()
            
            # Check if all terms appear in the path
            if any(term in path_str for term in search_terms):
                pdf_files.append(pdf_path)
                break
    
    # Remove duplicates
    return list(set(pdf_files))

def analyze_pdf_content(pdf_path):
    """Analyze PDF and return detailed stats"""
    parser = CompletePDFParser()
    result = parser.parse_complete_pdf(str(pdf_path))
    
    if 'error' in result:
        return {
            'status': 'ERROR',
            'error': result['error'],
            'meals_found': 0,
            'total_options': 0
        }
    
    total_options = sum(len(meal.get('options', [])) for meal in result.get('meals', []))
    
    # Check if we have essential data
    has_title = bool(result.get('title'))
    has_nutrition = bool(result.get('overall_nutrition'))
    has_meals = len(result.get('meals', [])) > 0
    
    return {
        'status': 'SUCCESS' if has_meals else 'NO_MEALS',
        'meals_found': len(result.get('meals', [])),
        'total_options': total_options,
        'has_title': has_title,
        'has_nutrition': has_nutrition,
        'has_dietary_context': bool(result.get('dietary_context')),
        'meal_details': [
            {
                'type': meal['meal_type'],
                'options': len(meal.get('options', []))
            }
            for meal in result.get('meals', [])
        ]
    }

def main():
    base_path = r"D:\Documents\Diet plan\outputs\raw"
    
    print("=" * 100)
    print("EXACTMATCH PDF SYSTEM - GOAL COVERAGE TEST")
    print("Testing 2 random PDFs per goal category")
    print("=" * 100)
    
    results_summary = {
        'total_goals_tested': 0,
        'total_pdfs_tested': 0,
        'successful_extractions': 0,
        'failed_extractions': 0,
        'goals_with_issues': []
    }
    
    for goal, categories in GOAL_CATEGORIES.items():
        print(f"\n{'=' * 100}")
        print(f"[GOAL: {goal.upper()}]")
        print(f"   Categories: {', '.join(categories)}")
        print(f"{'=' * 100}")
        
        # Find all PDFs for this goal
        pdf_files = find_pdfs_by_category(base_path, categories)
        
        if not pdf_files:
            print(f"   [!] WARNING: No PDFs found for this goal!")
            results_summary['goals_with_issues'].append({
                'goal': goal,
                'issue': 'No PDFs found'
            })
            continue
        
        print(f"   Found {len(pdf_files)} PDFs matching this goal")
        
        # Test 2 random PDFs
        test_samples = random.sample(pdf_files, min(2, len(pdf_files)))
        
        goal_has_issues = False
        
        for i, pdf_path in enumerate(test_samples, 1):
            results_summary['total_pdfs_tested'] += 1
            
            filename = pdf_path.name
            print(f"\n   [PDF {i}/2]: {filename}")
            
            # Analyze the PDF
            analysis = analyze_pdf_content(pdf_path)
            
            if analysis['status'] == 'SUCCESS':
                results_summary['successful_extractions'] += 1
                print(f"      [OK] Status: {analysis['status']}")
                print(f"      [*] Meals found: {analysis['meals_found']}")
                print(f"      [*] Total options: {analysis['total_options']}")
                print(f"      [*] Has title: {analysis['has_title']}")
                print(f"      [*] Has nutrition: {analysis['has_nutrition']}")
                print(f"      [*] Has dietary context: {analysis['has_dietary_context']}")
                
                # Show meal breakdown
                print(f"      [*] Meal breakdown:")
                for meal in analysis['meal_details']:
                    print(f"         • {meal['type']}: {meal['options']} option(s)")
                
                # Warning if less than 5 meals (might be incomplete)
                if analysis['meals_found'] < 5:
                    print(f"      [!] WARNING: Only {analysis['meals_found']} meals found (expected 5-7)")
                    goal_has_issues = True
                
            else:
                results_summary['failed_extractions'] += 1
                goal_has_issues = True
                print(f"      [ERROR] Status: {analysis['status']}")
                if 'error' in analysis:
                    print(f"      [ERROR] Error: {analysis['error']}")
                print(f"      [*] Meals found: {analysis['meals_found']}")
                print(f"      [*] Total options: {analysis['total_options']}")
        
        if goal_has_issues:
            results_summary['goals_with_issues'].append({
                'goal': goal,
                'issue': 'Some PDFs had issues during extraction'
            })
        
        results_summary['total_goals_tested'] += 1
    
    # Final Summary
    print("\n" + "=" * 100)
    print("[FINAL SUMMARY]")
    print("=" * 100)
    print(f"[+] Goals tested: {results_summary['total_goals_tested']}/{len(GOAL_CATEGORIES)}")
    print(f"[+] PDFs tested: {results_summary['total_pdfs_tested']}")
    print(f"[+] Successful extractions: {results_summary['successful_extractions']}")
    print(f"[+] Failed extractions: {results_summary['failed_extractions']}")
    
    success_rate = (results_summary['successful_extractions'] / results_summary['total_pdfs_tested'] * 100) if results_summary['total_pdfs_tested'] > 0 else 0
    print(f"[+] Success rate: {success_rate:.1f}%")
    
    if results_summary['goals_with_issues']:
        print(f"\n[!] Goals with issues ({len(results_summary['goals_with_issues'])}):")
        for issue in results_summary['goals_with_issues']:
            print(f"   - {issue['goal']}: {issue['issue']}")
    else:
        print(f"\n[SUCCESS] All goals passed! ExactMatch system handles all goal categories successfully.")
    
    print("\n" + "=" * 100)
    
    # Return exit code
    return 0 if results_summary['failed_extractions'] == 0 else 1

if __name__ == "__main__":
    exit(main())
