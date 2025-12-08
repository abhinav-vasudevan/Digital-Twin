"""
Test Range Value Parsing
Shows how the system handles range inputs for age, height, weight
"""

def parse_range_value(value):
    """Parse range values like '70-72', '30-35', or single values"""
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        value = value.strip()
        if '-' in value or 'to' in value.lower():
            value = value.lower().replace('kg', '').replace('cm', '').replace('years', '').strip()
            
            if '-' in value:
                parts = value.split('-')
            else:
                parts = value.split('to')
            
            try:
                start = float(parts[0].strip())
                end = float(parts[1].strip())
                return (start + end) / 2
            except (ValueError, IndexError):
                pass
        
        try:
            cleaned = value.lower().replace('kg', '').replace('cm', '').replace('years', '').strip()
            return float(cleaned)
        except ValueError:
            pass
    
    return 0.0


# Test Cases
print("=" * 70)
print("TESTING RANGE VALUE PARSING")
print("=" * 70)

test_cases = [
    # Age ranges
    ("30-35 years", "Age range"),
    ("30-35", "Age range without unit"),
    ("32", "Single age"),
    (32, "Numeric age"),
    
    # Height ranges  
    ("160-165 cm", "Height range"),
    ("162 cm", "Single height"),
    ("162", "Height without unit"),
    
    # Weight ranges
    ("70-72 kg", "Weight range"),
    ("70 kg", "Single weight"),
    ("71", "Weight without unit"),
    
    # Edge cases
    ("25 to 30", "Using 'to' instead of dash"),
    ("25 TO 30 years", "Uppercase TO"),
]

print("\nTest Results:")
print("-" * 70)

for value, description in test_cases:
    result = parse_range_value(value)
    print(f"Input: {str(value):20s} | Result: {result:6.1f} | {description}")

print("\n" + "=" * 70)
print("EXAMPLE: Your User Profile")
print("=" * 70)

# Your example from the question
profile = {
    "age": "30-35 years",
    "gender": "Female",
    "height": "162 cm",
    "weight": "70-72 kg"
}

print("\nOriginal Profile:")
for key, value in profile.items():
    print(f"  {key}: {value}")

# Parse ranges
profile['age'] = parse_range_value(profile['age'])
profile['height'] = parse_range_value(profile['height'])
profile['weight'] = parse_range_value(profile['weight'])

print("\nParsed Profile (middle values):")
for key, value in profile.items():
    print(f"  {key}: {value}")

# Calculate BMI
height_m = profile['height'] / 100
bmi = profile['weight'] / (height_m ** 2)

print(f"\n✅ Calculated BMI: {bmi:.1f}")

if bmi < 18.5:
    category = "underweight"
elif bmi < 25:
    category = "normal"
elif bmi < 30:
    category = "overweight"
else:
    category = "obese"

print(f"✅ BMI Category: {category}")

print("\n" + "=" * 70)
print("HOW IT WORKS IN EXACT MATCH SYSTEM")
print("=" * 70)
print("""
1. User submits profile with ranges:
   Age: '30-35 years'
   Height: '162 cm' 
   Weight: '70-72 kg'

2. API parses ranges to middle values:
   Age: 32.5
   Height: 162.0
   Weight: 71.0

3. Calculates BMI from parsed values:
   BMI = 71 / (1.62^2) = 27.1

4. Determines BMI category:
   Category: 'overweight' (since 25 < 27.1 < 30)

5. Exact match searches for plans matching:
   ✓ Goal: weight_loss_only
   ✓ Region: north_indian
   ✓ Diet: vegetarian
   ✓ Gender: female
   ✓ BMI: overweight  ← Calculated from range
   ✓ Activity: light

6. Result: Found 1 plan matching ALL 6 factors!
""")
