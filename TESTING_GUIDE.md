# 🧪 Testing Guide - Verify Dietary Preferences Work

## ✅ How to Test the Fixes

### **Test 1: Vegetarian Diet (No Nuts)**

1. **Go to Onboarding:** http://localhost:8000/onboarding

2. **Step 1 - Basic Info:**
   - Age: 28
   - Gender: Female
   - Height: 165 cm
   - Weight: 65 kg
   - Target Weight: 60 kg

3. **Step 2 - Diet Preferences:**
   - Region: North Indian
   - **Diet Type: Click 🥬 Vegetarian**
   - **Allergies: Type "nuts, dairy"**

4. **Step 3 - Health Goals:**
   - Activity: Moderate
   - Medical Conditions: (leave blank or add PCOS)
   - Goals: Select "Weight Loss" + "Improve Skin"

5. **Click "Complete Profile"** → **Generate Plan**

6. **Expected Results:**
   - ✅ Breakfast: "Oats with Fruits and Seeds" (NO almonds)
   - ✅ Lunch: "Paneer Tikka Salad" OR "Chickpea Salad Bowl" (NO chicken)
   - ✅ Evening Snack: "Roasted Chickpeas" (NOT "Nuts and Seeds Mix")
   - ✅ Dinner: "Dal Khichdi Bowl" (NO fish/meat)
   - ❌ Should NOT see: Chicken, Fish, Almonds, Greek Yogurt

---

### **Test 2: Non-Vegetarian Diet (No Allergies)**

1. **Delete old data:**
   - Delete `service/data/profile.json`
   - Delete `service/data/meal_plans.json`

2. **Start Fresh:** Go to http://localhost:8000/onboarding

3. **Step 2 - Diet Preferences:**
   - **Diet Type: Click 🍗 Non-Vegetarian**
   - **Allergies: (leave blank)**

4. **Complete profile and generate plan**

5. **Expected Results:**
   - ✅ Lunch: "Grilled Chicken Salad"
   - ✅ Dinner: "Grilled Fish with Brown Rice"
   - ✅ Evening Snack: "Mixed Nuts and Seeds" (nuts allowed)
   - ✅ Should see protein-rich meals with chicken/fish

---

### **Test 3: Vegan Diet**

1. **Delete old data again**

2. **Step 2 - Diet Preferences:**
   - **Diet Type: Click 🌱 Vegan**
   - Allergies: (leave blank)

3. **Expected Results:**
   - ✅ Lunch: "Chickpea Salad Bowl" (NO paneer, NO chicken)
   - ✅ Snack: "Fruit Bowl" (NO Greek yogurt)
   - ✅ Dinner: "Quinoa Buddha Bowl" (with tofu, NO dairy)
   - ❌ Should NOT see: Any dairy, eggs, meat, fish

---

### **Test 4: Meal Swapping Respects Diet**

1. **Go to any meal detail page**

2. **Click "Swap Meal" button**

3. **Expected:**
   - If you're vegetarian → Should swap to another veg meal
   - If you're non-veg → May include chicken/fish options
   - Allergies should still be respected in swapped meals

---

## 🔍 How to Check Meal Ingredients

### View Meal Details:
1. Go to Dashboard
2. Click on any meal card
3. Check the "Ingredients" section
4. Verify NO allergens are listed

### Check All 14 Days:
1. Go to Meal Plan page
2. Click through each day
3. Verify all meals follow your diet type

---

## 📊 What Changed in the Code

### Before (Hardcoded):
```python
"lunch": {
    "name": "Grilled Chicken Salad",  # ❌ Always this
    "ingredients": ["Chicken breast", ...]  # ❌ Ignores diet
}
```

### After (Dynamic):
```python
if diet_type == "vegetarian":
    lunch = {
        "name": "Paneer Tikka Salad",  # ✅ Veg option
        "ingredients": ["Paneer", ...]  # ✅ No meat
    }
else:
    lunch = {
        "name": "Grilled Chicken Salad",  # ✅ Only if non-veg
        "ingredients": ["Chicken", ...]
    }
```

---

## 🐛 If You Still See Wrong Meals

### Possible Reasons:

1. **Old cached data:**
   - Delete `service/data/meal_plans.json`
   - Delete `service/data/profile.json`
   - Restart from onboarding

2. **Profile not saved correctly:**
   - Open `service/data/profile.json`
   - Check if `diet_type` and `allergies` are there
   - Should look like:
     ```json
     {
       "diet_type": "vegetarian",
       "allergies": ["nuts", "dairy"],
       ...
     }
     ```

3. **Server needs restart:**
   - The server should auto-reload
   - But if issues persist, manually restart

---

## 💡 Understanding the AI Insights

### Current State:
The "AI Insights" use **rule-based logic**, not actual AI:

```python
if energy_level < 3:
    insight = "Your energy is low. Add more protein."
elif digestion == "poor":
    insight = "Try more fiber and probiotics."
```

**This is:**
- ✅ **Fast** - Instant response
- ✅ **Reliable** - No API failures
- ✅ **Free** - No OpenAI costs
- ❌ **Not learning** - Same rules always
- ❌ **Not personalized** - Generic advice

### To Upgrade to Real AI:

You would need to:
1. Get OpenAI API key
2. Install `openai` library
3. Replace the function with actual LLM calls

**Cost:** ~$0.01-0.05 per insight (GPT-4)  
**Benefit:** Truly personalized, context-aware advice

---

## 🎯 Quick Verification Checklist

Test your profile and check these:

- [ ] Vegetarian profile → No chicken/fish/meat in ANY meal
- [ ] "Nut allergy" entered → No almonds/nuts in ANY meal
- [ ] "Dairy allergy" entered → No yogurt/milk/paneer
- [ ] Vegan diet → No dairy, eggs, or animal products
- [ ] Non-veg diet → Can see chicken/fish options
- [ ] Meal swapping → Alternative meals also respect diet
- [ ] All 14 days → Consistent dietary rules

---

## 📸 Expected Meal Examples

### Vegetarian Profile:
- **Breakfast:** Oats with fruits and chia seeds
- **Lunch:** Paneer tikka salad / Chickpea bowl
- **Snack:** Roasted chickpeas (if nut-free)
- **Dinner:** Dal khichdi / Quinoa bowl

### Non-Vegetarian Profile:
- **Breakfast:** Same (usually veg-friendly)
- **Lunch:** Grilled chicken salad
- **Snack:** Mixed nuts (if no allergy)
- **Dinner:** Grilled fish with rice

### Vegan Profile:
- **Breakfast:** Oats with plant milk
- **Lunch:** Chickpea salad bowl
- **Snack:** Fruit bowl (no yogurt)
- **Dinner:** Quinoa buddha bowl with tofu

---

## 🚀 Next Steps After Testing

Once you verify everything works:

1. **Add More Meal Variety:**
   - Expand the meal database
   - Add regional cuisines
   - Include more allergen-free options

2. **Connect the ML Recommender:**
   - Use your existing `Recommender` class
   - Load real meal templates
   - Generate category-specific plans (PCOS, diabetes, etc.)

3. **Upgrade to Real AI:**
   - Integrate OpenAI API
   - Generate personalized recipes
   - Smart ingredient substitutions

4. **Improve Allergy Detection:**
   - Add more allergen keywords
   - Support "gluten-free", "soy-free", etc.
   - Cross-contamination warnings

---

## 📝 Summary

**What's Fixed:**
- ✅ Diet type is now respected (veg/non-veg/vegan)
- ✅ Allergies are detected and excluded
- ✅ Meal alternatives respect preferences
- ✅ All 14 days follow the same rules

**What's Still Basic:**
- ⚠️ Limited meal variety (10-15 options)
- ⚠️ AI insights are rule-based, not LLM
- ⚠️ ML recommender not fully integrated

**Test Now:**
Delete old data, go through onboarding as vegetarian with nut allergy, and verify your meals are safe! 🎉
