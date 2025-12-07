"""
Build searchable PDF index from extracted content.
Parses filenames for metadata and extracts meal structures.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFIndexBuilder:
    """Builds searchable index from extracted PDF content."""
    
    # Metadata extraction patterns
    GENDER_PATTERN = r'\b(male|female|m|f)\b'
    REGION_PATTERN = r'\b(north\s*indian?|south\s*indian?|indian?)\b'
    ACTIVITY_PATTERN = r'\b(sedentary|light|moderate|heavy|high)\b'
    BMI_PATTERN = r'\b(underweight|normal|overweight|obese)\b'
    DIET_PATTERN = r'\b(veg|vegetarian|vegeterian|non[-\s]?veg|non[-\s]?vegetarian|vegan|eggetarian|eggeterian|eggeter)\b'
    
    # Category keywords mapping - order matters, check specific ones first
    # ALL LOWERCASE for case-insensitive matching
    CATEGORY_KEYWORDS = {
        # Specific detox types
        'gut_cleanse_digestive_detox': ['gut cleanse digestive detox', 'digestive detox', 'gut clensing'],
        'gut_detox': ['gut detox diet', 'gut detox'],
        'liver_detox': ['liver detox'],
        'skin_detox': ['skin detox'],
        'ayurvedic_detox': ['ayurvedic detox', 'ayurvedic', 'panchakarma'],
        
        # Hair and skin
        'hair_loss': ['hair loss', 'hair thinning', 'hair thining'],
        'skin_health': ['skin health', 'acne and oily skin', 'acne', 'oily skin'],
        'anti_aging': ['anti aging', 'sundamage', 'sun damage', 'fine lines'],
        
        # Weight and diet types
        'weight_gain': ['wt gain for underweight and malnutrition', 'weight gain', 'malnutrition', 'underweight n'],
        'weight_loss_pcos': ['weight loss + pcos', 'wt loss + pcod', 'pcos + weight', 'pcod'],
        'weight_loss_diabetes': ['typ 1 dm and wt loss', 'weight loss+ typ', 'diabetes & weight', 'type 1 diabetes'],
        'weight_loss': ['weight loss only'],
        
        # Health conditions
        'gas_bloating': ['gas + bloating', 'gas & bloating', 'bloating'],
        'anti_inflammatory': ['anti inflamatory', 'anti inflammatory', 'edema'],
        'probiotic': ['probiotic rich diet', 'probiotic'],
        'insulin_resistance': ['insulin resistance', 'obesity'],
        
        # Protein diets
        'high_protein_high_fiber': ['high protein high fiber'],
        'high_protein_balanced': ['protein rich balanced diet', 'protein balanced'],
    }
    
    def __init__(self, raw_dir: str = "outputs/raw", output_file: str = "outputs/pdf_index.json"):
        self.raw_dir = Path(raw_dir)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
    def extract_metadata_from_filename(self, filename: str, folder_path: str) -> Dict[str, Any]:
        """Extract metadata from filename and folder structure."""
        # Convert to lowercase for case-insensitive matching
        filename_lower = filename.lower()
        folder_lower = folder_path.lower()
        combined = f"{folder_lower} {filename_lower}".replace('_', ' ').replace('-', ' ')
        
        metadata = {
            'filename': filename,
            'folder': folder_path,
        }
        
        # Extract gender
        gender_match = re.search(self.GENDER_PATTERN, combined, re.IGNORECASE)
        if gender_match:
            gender = gender_match.group(1).lower()
            metadata['gender'] = 'male' if gender in ['male', 'm'] else 'female'
        
        # Extract region
        region_match = re.search(self.REGION_PATTERN, combined, re.IGNORECASE)
        if region_match:
            region = region_match.group(1).lower()
            if 'north' in region:
                metadata['region'] = 'north_indian'
            elif 'south' in region:
                metadata['region'] = 'south_indian'
            else:
                metadata['region'] = 'indian'
        
        # Extract activity level
        activity_match = re.search(self.ACTIVITY_PATTERN, combined, re.IGNORECASE)
        if activity_match:
            activity = activity_match.group(1).lower()
            # Normalize activity levels
            if activity in ['sedentary']:
                metadata['activity'] = 'sedentary'
            elif activity in ['light']:
                metadata['activity'] = 'light'
            elif activity in ['moderate']:
                metadata['activity'] = 'moderate'
            elif activity in ['heavy', 'high']:
                metadata['activity'] = 'heavy'
        
        # Extract BMI category
        bmi_match = re.search(self.BMI_PATTERN, combined, re.IGNORECASE)
        if bmi_match:
            metadata['bmi_category'] = bmi_match.group(1).lower()
        
        # Extract diet type (handle typos like "vegeterian" and "eggeter")
        # Order matters: check vegan first, then egg, then non-veg, then veg
        diet_match = re.search(self.DIET_PATTERN, combined, re.IGNORECASE)
        if diet_match:
            diet = diet_match.group(1).lower()
            # Check in order of specificity
            if 'vegan' in diet:
                metadata['diet_type'] = 'vegan'
            elif 'egg' in diet:  # eggetarian or eggeter
                metadata['diet_type'] = 'eggetarian'
            elif 'non' in diet:  # non-veg or non vegetarian
                metadata['diet_type'] = 'non_veg'
            elif 'veg' in diet or 'veg' in diet:  # catches veg, vegetarian, vegeterian
                metadata['diet_type'] = 'vegetarian'
            else:
                metadata['diet_type'] = 'vegetarian'
        
        # Detect category from folder and filename
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                metadata['category'] = category
                break
        
        return metadata
    
    def extract_age_info(self, content: str) -> Dict[str, Any]:
        """Extract age information from content."""
        age_info = {}
        
        # Pattern 1: Age range like "Age: 30-40 years" or "Age: 30–40 years"
        age_range_pattern = r'Age[:\s]*(\d+)\s*[-–]\s*(\d+)\s*years?'
        age_range_match = re.search(age_range_pattern, content, re.IGNORECASE)
        
        if age_range_match:
            age_info['age_min'] = int(age_range_match.group(1))
            age_info['age_max'] = int(age_range_match.group(2))
            age_info['age_avg'] = (age_info['age_min'] + age_info['age_max']) // 2
        else:
            # Pattern 2: Single age like "Age: 30 years"
            age_single_pattern = r'Age[:\s]*(\d+)\s*years?'
            age_single_match = re.search(age_single_pattern, content, re.IGNORECASE)
            
            if age_single_match:
                age = int(age_single_match.group(1))
                age_info['age_min'] = age
                age_info['age_max'] = age
                age_info['age_avg'] = age
        
        return age_info
    
    def extract_nutrition_info(self, content: str) -> Dict[str, Any]:
        """Extract nutrition information from content."""
        nutrition = {}
        
        # Extract daily calorie range
        calorie_pattern = r'(?:calories?|kcal)[:\s]*(\d+)\s*[-–]\s*(\d+)'
        cal_match = re.search(calorie_pattern, content, re.IGNORECASE)
        if cal_match:
            nutrition['calories_min'] = int(cal_match.group(1))
            nutrition['calories_max'] = int(cal_match.group(2))
        
        # Extract protein range
        protein_pattern = r'protein[:\s]*(\d+)\s*[-–]\s*(\d+)\s*g'
        prot_match = re.search(protein_pattern, content, re.IGNORECASE)
        if prot_match:
            nutrition['protein_min'] = int(prot_match.group(1))
            nutrition['protein_max'] = int(prot_match.group(2))
        
        # Extract carbs range
        carb_pattern = r'carbohydrate[s]?[:\s]*(\d+)\s*[-–]\s*(\d+)\s*g'
        carb_match = re.search(carb_pattern, content, re.IGNORECASE)
        if carb_match:
            nutrition['carbs_min'] = int(carb_match.group(1))
            nutrition['carbs_max'] = int(carb_match.group(2))
        
        # Extract fat range
        fat_pattern = r'fat[:\s]*(\d+)\s*[-–]\s*(\d+)\s*g'
        fat_match = re.search(fat_pattern, content, re.IGNORECASE)
        if fat_match:
            nutrition['fat_min'] = int(fat_match.group(1))
            nutrition['fat_max'] = int(fat_match.group(2))
        
        # Extract fiber range
        fiber_pattern = r'fiber[:\s]*(\d+)\s*[-–]\s*(\d+)\s*g'
        fiber_match = re.search(fiber_pattern, content, re.IGNORECASE)
        if fiber_match:
            nutrition['fiber_min'] = int(fiber_match.group(1))
            nutrition['fiber_max'] = int(fiber_match.group(2))
        
        return nutrition
    
    def extract_meals(self, content: str) -> List[Dict[str, Any]]:
        """Extract meal structures from content."""
        meals = []
        
        # Meal time patterns
        meal_times = [
            'early morning', 'pre-breakfast', 'breakfast', 
            'mid-morning', 'mid morning', 'lunch', 
            'evening snack', 'evening', 'dinner', 'bedtime', 'post-dinner'
        ]
        
        for meal_time in meal_times:
            # Find meal time section
            pattern = rf'{meal_time}[:\s]*\(?(\d{{1,2}}[:\.]?\d{{0,2}}\s*(?:am|pm)?)\)?'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                meals.append({
                    'meal_time': meal_time.title().replace('-', ' '),
                    'time': match.group(1) if match.lastindex >= 1 else None
                })
        
        return meals
    
    def extract_ingredients(self, content: str) -> List[str]:
        """Extract common ingredients mentioned in the plan."""
        # Common Indian ingredients
        ingredient_keywords = [
            'rice', 'wheat', 'roti', 'chapati', 'dal', 'lentil', 'moong', 'chana',
            'paneer', 'tofu', 'milk', 'curd', 'yogurt', 'buttermilk',
            'oats', 'quinoa', 'ragi', 'jowar', 'bajra', 'dalia',
            'ghee', 'oil', 'butter',
            'vegetables', 'spinach', 'broccoli', 'carrot', 'tomato', 'onion',
            'fruits', 'apple', 'banana', 'papaya', 'orange', 'pomegranate',
            'almonds', 'walnuts', 'cashews', 'dates', 'raisins',
            'ginger', 'turmeric', 'cumin', 'coriander', 'ajwain',
            'chicken', 'fish', 'egg', 'meat'
        ]
        
        found_ingredients = []
        content_lower = content.lower()
        
        for ingredient in ingredient_keywords:
            if ingredient in content_lower:
                found_ingredients.append(ingredient)
        
        return found_ingredients
    
    def process_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Process a single extracted text file."""
        try:
            # Read content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Get relative path for folder structure
            rel_path = file_path.relative_to(self.raw_dir)
            folder_path = str(rel_path.parent)
            
            # Extract metadata
            metadata = self.extract_metadata_from_filename(file_path.stem, folder_path)
            
            # Extract age info
            age_info = self.extract_age_info(content)
            
            # Extract nutrition info
            nutrition = self.extract_nutrition_info(content)
            
            # Extract meal structure
            meals = self.extract_meals(content)
            
            # Extract ingredients
            ingredients = self.extract_ingredients(content)
            
            # Build index entry
            entry = {
                'file_path': str(file_path),
                'relative_path': str(rel_path),
                **metadata,
                'age_info': age_info,
                'nutrition': nutrition,
                'meals': meals,
                'ingredients': ingredients,
                'content_preview': content[:500],  # First 500 chars for preview
            }
            
            return entry
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None
    
    def build_index(self) -> Dict[str, Any]:
        """Build complete index from all extracted files."""
        logger.info(f"Building index from {self.raw_dir}")
        
        index = {
            'metadata': {
                'total_plans': 0,
                'by_gender': {},
                'by_region': {},
                'by_activity': {},
                'by_bmi': {},
                'by_diet': {},
                'by_category': {},
                'category': {},  # Add this for consistency
            },
            'plans': []
        }
        
        # Find all .txt files
        txt_files = list(self.raw_dir.rglob("*.txt"))
        logger.info(f"Found {len(txt_files)} files to process")
        
        # Process each file
        for i, file_path in enumerate(txt_files, 1):
            if i % 50 == 0:
                logger.info(f"Processing {i}/{len(txt_files)}")
            
            entry = self.process_file(file_path)
            if entry:
                index['plans'].append(entry)
                
                # Update metadata counts
                index['metadata']['total_plans'] += 1
                
                # Count by attributes
                for key in ['gender', 'region', 'activity', 'bmi_category', 'diet_type', 'category']:
                    if key in entry:
                        value = entry[key]
                        meta_key = key if key == 'category' else f"by_{key.split('_')[0]}"
                        if value not in index['metadata'][meta_key]:
                            index['metadata'][meta_key][value] = 0
                        index['metadata'][meta_key][value] += 1
        
        logger.info(f"Index built with {index['metadata']['total_plans']} plans")
        return index
    
    def save_index(self, index: Dict[str, Any]):
        """Save index to JSON file."""
        logger.info(f"Saving index to {self.output_file}")
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Index saved successfully")
    
    def run(self):
        """Main execution method."""
        logger.info("Starting PDF index builder")
        
        # Build index
        index = self.build_index()
        
        # Save index
        self.save_index(index)
        
        # Print summary
        print("\n" + "="*60)
        print("PDF INDEX BUILD SUMMARY")
        print("="*60)
        print(f"Total Plans: {index['metadata']['total_plans']}")
        print(f"\nBy Gender: {index['metadata']['by_gender']}")
        print(f"By Region: {index['metadata']['by_region']}")
        print(f"By Activity: {index['metadata']['by_activity']}")
        print(f"By BMI: {index['metadata']['by_bmi']}")
        print(f"By Diet: {index['metadata']['by_diet']}")
        print(f"By Category: {index['metadata']['by_category']}")
        print("="*60)
        
        logger.info("PDF index builder completed")


if __name__ == "__main__":
    builder = PDFIndexBuilder()
    builder.run()
