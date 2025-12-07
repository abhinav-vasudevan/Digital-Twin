"""
Comprehensive PDF Parser for Diet Plans
Extracts ALL food-related content from PDF text files
"""
from typing import Dict, List, Any, Optional
import re


class CompletePDFParser:
    """Parse complete food-related content from diet plan PDFs"""
    
    def __init__(self):
        # Meal patterns - sorted by length (longest first) to avoid partial matches
        # e.g., "Mid-Morning Snack" must be checked before "Mid-Morning"
        meal_patterns_unsorted = [
            "Early Morning (On Waking)",
            "Early Morning (on Waking)",
            "Early Morning",
            "Pre-Workout (Heavy Training Fuel)",
            "Pre-Workout (Heavy Training – Fat Loss Focus)",
            "Pre-Workout (Heavy Training Fuel – Controlled Calories)",
            "Pre-Workout",
            "Pre-Yoga / Light Activity",
            "Pre-Activity",
            "Pre-Breakfast",
            "Breakfast (Post-Workout)",
            "Breakfast (Post-Yoga / Morning Meal)",
            "Breakfast (High-Calorie)",
            "Breakfast",
            "Mid-Morning Snack",
            "Mid-Morning",
            "Lunch (High-Calorie Balanced Meals)",
            "Lunch",
            "Evening Snack",
            "Evening",
            "Dinner",
            "Bedtime Snack",
            "Bedtime"
        ]
        self.meal_patterns = sorted(meal_patterns_unsorted, key=len, reverse=True)
    
    def parse_complete_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract ALL food-related information from PDF
        Returns complete structured data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read file: {e}"}
        
        result = {
            "title": self._extract_title(content),
            "profile_summary": self._extract_profile_summary(content),
            "overall_nutrition": self._extract_overall_nutrition(content),
            "key_micronutrients": self._extract_micronutrients(content),
            "meals": self._extract_all_meals(content),
            "dietary_context": self._extract_dietary_context(content),
            "rationale": self._extract_rationale(content),
            "source_references": self._extract_references(content)
        }
        
        return result
    
    def _extract_title(self, content: str) -> str:
        """Extract diet plan title from first line"""
        lines = content.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 10 and not line.startswith('Client'):
                return line
        return "Diet Plan"
    
    def _extract_profile_summary(self, content: str) -> str:
        """Extract brief profile summary (diet type, region, activity) - NO personal data"""
        lines = content.split('\n')
        for i, line in enumerate(lines[:10]):
            # Look for lines with | separators that have diet/region info
            if '|' in line and any(word in line.lower() for word in ['vegetarian', 'veg', 'indian', 'active', 'sedentary']):
                # Remove personal identifiers like names
                parts = [p.strip() for p in line.split('|')]
                # Filter out personal data, keep only diet-related descriptors
                filtered = []
                for part in parts:
                    if not any(skip in part.lower() for skip in ['name:', 'age:', 'height:', 'weight:', 'bmi:']):
                        filtered.append(part)
                return ' | '.join(filtered)
        return ""
    
    def _extract_overall_nutrition(self, content: str) -> Dict[str, str]:
        """Extract overall daily nutritional ranges"""
        nutrition = {}
        
        # Find the "Overall" nutrition section
        patterns = {
            'calories': r'Calories?:?\s*(\d+[-–]\d+)\s*kcal',
            'protein': r'Protein:?\s*(\d+[-–]\d+)\s*g',
            'carbohydrates': r'Carbohydrate?s?:?\s*(\d+[-–]\d+)\s*g',
            'fat': r'Fat:?\s*(\d+[-–]\d+)\s*g',
            'fiber': r'Fiber:?\s*(\d+[-–]\d+)\s*g'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                nutrition[key] = match.group(1)
        
        return nutrition
    
    def _extract_micronutrients(self, content: str) -> List[str]:
        """Extract key micronutrients list"""
        # Look for "Key Micronutrients:" section
        match = re.search(r'Key Micronutrients?:([^\n]+)', content, re.IGNORECASE)
        if match:
            nutrients_text = match.group(1)
            # Split by comma and clean up
            nutrients = [n.strip() for n in nutrients_text.split(',')]
            return nutrients
        return []
    
    def _extract_all_meals(self, content: str) -> List[Dict[str, Any]]:
        """Extract ALL meal types with ALL options and complete details"""
        meals = []
        
        for meal_type in self.meal_patterns:
            meal_data = self._extract_meal_section(content, meal_type)
            if meal_data:
                meals.append(meal_data)
        
        return meals
    
    def _extract_meal_section(self, content: str, meal_type: str) -> Optional[Dict[str, Any]]:
        """Extract one meal type with all its options"""
        # Try multiple patterns to find meal section - MUST match at start of line
        # Use \b word boundary or $ end-of-line to prevent partial matches
        patterns = [
            f"^Meal Type: {re.escape(meal_type)}(?:\n|$)",  # "Meal Type: Breakfast\n" - exact match
            f"^{re.escape(meal_type)} Options(?:\n|$|:)",   # "Breakfast Options"
            f"^{re.escape(meal_type)} \\([^)]*\\)",         # "Breakfast (8:00 AM)"
            f"^{re.escape(meal_type)}:(?:\n|$| )",         # "Breakfast:"
            f"^{re.escape(meal_type)}$"                     # Standalone "Breakfast"
        ]
        
        section_start = -1
        matched_pattern = None
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                section_start = match.start()
                matched_pattern = pattern
                break
        
        if section_start == -1:
            # print(f"DEBUG: No match found for meal_type '{meal_type}'")
            return None
        
        # print(f"DEBUG: Found '{meal_type}' at position {section_start}")
        
        # Find section end (next meal type or end of content)
        section_end = len(content)
        for next_meal in self.meal_patterns:
            if next_meal == meal_type:
                continue
            # Look for next meal pattern - must match at the start of a line
            for pattern in [
                f"^Meal Type: {next_meal}",    # "Meal Type: Lunch"
                f"^{next_meal} Options",        # "Lunch Options"
                f"^{next_meal} \\([^)]*\\)",   # "Lunch (1:00 PM)"
                f"^{next_meal}:",               # "Lunch:"
                f"^{next_meal}$"                # Standalone "Lunch"
            ]:
                match = re.search(pattern, content[section_start + 10:], re.MULTILINE | re.IGNORECASE)
                if match:
                    potential_end = section_start + 10 + match.start()
                    if potential_end < section_end:
                        section_end = potential_end
        
        # Also check for "Dietary & Cultural Context" which marks end of meals
        context_match = re.search(r'Dietary & Cultural Context', content[section_start:], re.IGNORECASE)
        if context_match:
            potential_end = section_start + context_match.start()
            if potential_end < section_end:
                section_end = potential_end
        
        section_text = content[section_start:section_end]
        
        # Extract all options in this section
        options = self._extract_options_from_section(section_text)
        
        if not options:
            return None
        
        return {
            "meal_type": meal_type,
            "options": options
        }
    
    def _extract_options_from_section(self, section_text: str) -> List[Dict[str, Any]]:
        """Extract all meal options from a section with complete details"""
        options = []
        
        # Find all "Option X" markers - handle various dashes and formatting
        # Match: "Option 1:", "Option 1 -", "Option -1", "Option 1 –" (em-dash), "Option 1—"
        # Also: "Option -1 Dish – Name"
        option_matches = list(re.finditer(r'Option\s*[:\-–—]?\s*(\d+)\s*(?:Dish\s*)?[:\-–—]\s*(.+?)(?=\n)', section_text, re.IGNORECASE))
        
        # If no "Option X" pattern, try "Dish:" or "Dish Name:" pattern (single-dish format)
        if not option_matches:
            # Try "Dish Name:" first, then "Dish:"
            dish_match = re.search(r'Dish\s*Name:\s*(.+?)(?=\n)', section_text, re.IGNORECASE)
            if not dish_match:
                dish_match = re.search(r'Dish:\s*(.+?)(?=\n)', section_text, re.IGNORECASE)
            
            if dish_match:
                # print(f"DEBUG: Found dish name: '{dish_match.group(1)}'")
                option_data = self._parse_single_option(section_text, 0, len(section_text), dish_match.group(1))
                if option_data:
                    # print(f"DEBUG: option_data is valid, adding to options")
                    option_data['option_number'] = '1'  # Single dish = Option 1
                    options.append(option_data)
                # else:
                #     print(f"DEBUG: option_data is None!")
            # else:
            #     print(f"DEBUG: No 'Dish Name:' found in section")
            #     print(f"DEBUG: Section text preview: {section_text[:300]}")
            return options
        
        # Parse each option
        for i, match in enumerate(option_matches):
            option_num = match.group(1)
            option_name = match.group(2).strip()
            
            # Find start and end of this option's content
            option_start = match.start()
            option_end = option_matches[i + 1].start() if i + 1 < len(option_matches) else len(section_text)
            
            option_text = section_text[option_start:option_end]
            
            option_data = self._parse_single_option(option_text, option_start, option_end, option_name)
            if option_data:
                option_data['option_number'] = option_num
                options.append(option_data)
        
        return options
    
    def _parse_single_option(self, option_text: str, start: int, end: int, name: str) -> Optional[Dict[str, Any]]:
        """Parse complete details for one meal option"""
        data = {
            "name": name,
            "ingredients": "",
            "serving": "",
            "time": "",
            "method": "",
            "nutrition": {}
        }
        
        # Extract ingredients - only capture until next line (not DOTALL)
        # "Ingredients:", "Ingredients with Quantities & Units:", "Ingredients with Quantities:"
        ing_match = re.search(r'Ingredients?(?:\s+with\s+Quantities(?:\s*&\s*Units)?)?:\s*(.+?)$', option_text, re.IGNORECASE | re.MULTILINE)
        if ing_match:
            data["ingredients"] = ing_match.group(1).strip()
        
        # Extract serving size - handle "Servings:" and "Serving Size:"
        serving_match = re.search(r'Servings?(?:\s+Size)?:\s*(.+?)$', option_text, re.IGNORECASE | re.MULTILINE)
        if serving_match:
            data["serving"] = serving_match.group(1).strip()
        
        # Extract prep/cooking time - handle "Time:", "Prep Time:", "Preparation Time:"
        time_match = re.search(r'(?:Preparation\s+|Prep\s+)?Time:\s*(.+?)$', option_text, re.IGNORECASE | re.MULTILINE)
        if time_match:
            data["time"] = time_match.group(1).strip()
        
        # Extract cooking method - handle "Method:", "Method of Cooking:", "Cooking Method:"
        method_match = re.search(r'(?:Cooking\s+)?Method(?:\s+of\s+Cooking)?:\s*(.+?)$', option_text, re.IGNORECASE | re.MULTILINE)
        if method_match:
            data["method"] = method_match.group(1).strip()
        
        # Extract nutritive values - handle both formats
        # Format 1: "280 kcal, 22 g protein, 25 g carbs, 8 g fat"
        # Format 2: "Calories: 280 kcal | Protein: 22 g"
        nutr_match = re.search(r'Nutritive Values?:\s*(.+?)(?=\n\n|Option \d|Meal Type:|$)', option_text, re.IGNORECASE | re.DOTALL)
        if nutr_match:
            nutr_text = nutr_match.group(1).strip()
            
            # Parse nutrition values
            calories_match = re.search(r'(\d+)\s*kcal', nutr_text)
            if calories_match:
                data["nutrition"]["calories"] = calories_match.group(1)
            
            protein_match = re.search(r'(\d+)\s*g protein', nutr_text)
            if protein_match:
                data["nutrition"]["protein"] = protein_match.group(1)
            
            carbs_match = re.search(r'(\d+)\s*g carb', nutr_text)
            if carbs_match:
                data["nutrition"]["carbs"] = carbs_match.group(1)
            
            fat_match = re.search(r'(\d+(?:\.\d+)?)\s*g fat', nutr_text)
            if fat_match:
                data["nutrition"]["fat"] = fat_match.group(1)
            
            fiber_match = re.search(r'(\d+)\s*g fiber', nutr_text)
            if fiber_match:
                data["nutrition"]["fiber"] = fiber_match.group(1)
        
        # Return if we have at least a name
        # (Some PDFs have per-option nutrition, some only have daily totals)
        if data["name"]:
            return data
        
        return None
    
    def _extract_dietary_context(self, content: str) -> Dict[str, Any]:
        """Extract dietary & cultural context including allergens"""
        context = {
            "allergens": [],
            "diet_type": "",
            "cultural_preference": "",
            "tags": []
        }
        
        # Find "Dietary & Cultural Context" section
        section_match = re.search(r'Dietary & Cultural Context(.+?)(?=Annotations|Rationale|Source|$)', content, re.IGNORECASE | re.DOTALL)
        if section_match:
            section_text = section_match.group(1)
            
            # Extract allergens
            allergen_match = re.search(r'Allergens?:\s*(.+?)(?=\n(?:Diet|Cultural)|\n\n|$)', section_text, re.IGNORECASE)
            if allergen_match:
                allergens_text = allergen_match.group(1)
                context["allergens"] = [a.strip() for a in allergens_text.split(',')]
            
            # Extract diet type
            diet_match = re.search(r'Diet Type:\s*(.+?)(?=\n(?:Cultural)|\n\n|$)', section_text, re.IGNORECASE)
            if diet_match:
                context["diet_type"] = diet_match.group(1).strip()
            
            # Extract cultural preference
            cultural_match = re.search(r'Cultural Preference:\s*(.+?)(?=\n\n|$)', section_text, re.IGNORECASE)
            if cultural_match:
                context["cultural_preference"] = cultural_match.group(1).strip()
        
        # Extract tags from Annotations section
        tags_match = re.search(r'Annotations.*?tags?\)?:?\s*(.+?)(?=\n\n|Rationale|Source|$)', content, re.IGNORECASE | re.DOTALL)
        if tags_match:
            tags_text = tags_match.group(1)
            context["tags"] = [t.strip() for t in tags_text.split(',')]
        
        return context
    
    def _extract_rationale(self, content: str) -> Dict[str, Any]:
        """Extract rationale & food alternatives"""
        rationale = {
            "description": "",
            "substitutions": []
        }
        
        # Find "Rationale & Alternatives" section
        section_match = re.search(r'Rationale & Alternatives?(.+?)(?=Source References|$)', content, re.IGNORECASE | re.DOTALL)
        if section_match:
            section_text = section_match.group(1).strip()
            
            # Split into lines
            lines = [line.strip() for line in section_text.split('\n') if line.strip()]
            
            # First few lines are usually description, rest are substitutions
            description_lines = []
            substitution_lines = []
            
            for line in lines:
                # If line contains "→" or "can be replaced", it's a substitution
                if '→' in line or 'can be replaced' in line.lower() or 'substitut' in line.lower():
                    substitution_lines.append(line)
                else:
                    description_lines.append(line)
            
            rationale["description"] = ' '.join(description_lines)
            rationale["substitutions"] = substitution_lines
        
        return rationale
    
    def _extract_references(self, content: str) -> List[str]:
        """Extract source references"""
        references = []
        
        # Find "Source References" section
        section_match = re.search(r'Source References?(.+?)$', content, re.IGNORECASE | re.DOTALL)
        if section_match:
            section_text = section_match.group(1).strip()
            
            # Split into lines and clean
            lines = [line.strip() for line in section_text.split('\n') if line.strip()]
            # Remove bullets and numbers
            references = [re.sub(r'^[•\-\d.]+\s*', '', line) for line in lines]
        
        return references


# Convenience function for API use
def parse_pdf_complete(file_path: str) -> Dict[str, Any]:
    """Parse complete food information from PDF"""
    parser = CompletePDFParser()
    return parser.parse_complete_pdf(file_path)
