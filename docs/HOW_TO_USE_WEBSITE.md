# How to Use the 3 Recommendation Systems on the Website

## Quick Start

1. **Start the server** (if not already running):
   ```bash
   cd "d:\Documents\Diet plan"
   .venv\Scripts\Activate.ps1
   python -m uvicorn service.api:app --reload --port 8000
   ```

2. **Complete your profile** (if you haven't):
   - Go to: `http://localhost:8000/onboarding`
   - Fill in all details (age, weight, goals, diet, region, etc.)

3. **Choose a recommendation system**:
   - Go to: `http://localhost:8000/choose-system`
   - Pick one of the 3 systems

---

## The 3 Systems Explained

### 🎯 System 1: Exact Match
**URL**: `http://localhost:8000/choose-system` → Click "Exact Match"

**What it does:**
- Matches ALL 6 criteria EXACTLY:
  - Gender
  - BMI Category
  - Activity Level
  - Diet Type
  - Region
  - Goal/Category

**When to use:**
- You want plans that match your profile perfectly
- You have strict dietary/activity requirements
- You prefer precision over variety

**Example result with your profile:**
- Found: **2 exact matches**
- Both are: male + underweight + light + vegetarian/eggetarian + south_indian + weight_gain

**Pros:** Highly personalized, very specific
**Cons:** May show "not available" if no exact match exists

---

### 🚀 System 2: Goal-Only Match (RECOMMENDED)
**URL**: `http://localhost:8000/choose-system` → Click "Goal-Only Match"

**What it does:**
- Matches ONLY 2 criteria:
  - Primary Goal (weight_gain, weight_loss, skin_health, etc.)
  - Region (south_indian, north_indian)
- **Ignores:** Gender, BMI, Activity, Diet, Health conditions, Age, Allergies

**When to use:**
- You want maximum variety
- Your primary focus is achieving your goal
- You're flexible about other details (can adapt diet type, activity, etc.)

**Example result with your profile:**
- Found: **22 matches**
- All are: weight_gain + south_indian (mixed genders, BMIs, activities, diets)

**Pros:** Lots of variety, rarely shows "not available"
**Cons:** Some plans may require adaptation (e.g., non-veg to vegetarian)

---

### ⚖️ System 3: Smart Scoring (Original)
**URL**: `http://localhost:8000/choose-system` → Click "Smart Scoring"

**What it does:**
- AI scores every plan with weighted priorities:
  - **Goal** (1000 points) - highest priority
  - **Diet Type** (100 points) - second priority
  - **Region, Health, Age** (10 points each) - lower priority
- Filters out incompatible plans (wrong gender/BMI/activity)
- Ranks results by score

**When to use:**
- You want a balanced approach
- You prefer AI to prioritize what matters most
- You want some flexibility but not complete relaxation

**Example result with your profile:**
- Found: Multiple plans ranked by score
- Higher scores mean better matches overall

**Pros:** Balanced, intelligent prioritization
**Cons:** More complex logic, results may vary

---

## Step-by-Step Usage

### Option A: Use the Visual Interface

1. Open browser: `http://localhost:8000/choose-system`

2. You'll see 3 cards:
   - **Exact Match** (left) - All criteria
   - **Goal-Only** (center, recommended) - Goal + Region only
   - **Smart Scoring** (right) - AI weighted

3. Click on any card

4. You'll be taken to the recommendations page

5. Select 2-5 plans (click cards to select)

6. Click "Select Plans" button

7. Done! Redirects to dashboard

### Option B: Direct URL Navigation

**For Exact Match:**
```
http://localhost:8000/choose-system
→ Click "Exact Match"
```

**For Goal-Only:**
```
http://localhost:8000/choose-system
→ Click "Goal-Only Match"
```

**For Smart Scoring:**
```
http://localhost:8000/choose-system
→ Click "Smart Scoring"
```

### Option C: Test via Browser Console

1. Go to: `http://localhost:8000/dashboard`
2. Press **F12** to open Developer Console
3. Run one of these:

**Test Exact Match:**
```javascript
fetch('/api/meal-plan/generate-exact', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
})
.then(r => r.json())
.then(data => console.log(data))
```

**Test Goal-Only:**
```javascript
fetch('/api/meal-plan/generate-goal', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
})
.then(r => r.json())
.then(data => console.log(data))
```

**Test Smart Scoring:**
```javascript
fetch('/api/meal-plan/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
})
.then(r => r.json())
.then(data => console.log(data))
```

---

## API Endpoints

### Exact Match System
```
POST /api/meal-plan/generate-exact
```
**Returns:**
- `status`: "success" or "not_available"
- `recommendations`: Array of plan objects
- `total_matches`: Number of exact matches
- `message`: Error message if not available
- `criteria`: What was searched (if not available)

### Goal-Only System
```
POST /api/meal-plan/generate-goal
```
**Returns:**
- `status`: "success" or "not_available"
- `recommendations`: Array of plan objects
- `total_matches`: Number of goal matches
- `criteria`: {goal, region}

### Smart Scoring System
```
POST /api/meal-plan/generate
```
**Returns:**
- `status`: "success"
- `recommendations`: Array of scored plan objects

---

## Comparison with Your Profile

**Your Profile:**
- Gender: male
- Age: 20
- BMI: 18.9 (underweight)
- Activity: light
- Diet: vegetarian
- Region: south_indian
- Goal: weight_gain

### Results:

| System | Matches Found | Example Plans |
|--------|--------------|---------------|
| **Exact Match** | 2 | male + underweight + light + vegetarian + south_indian + weight_gain |
| **Goal-Only** | 22 | All weight_gain + south_indian (any gender/BMI/diet/activity) |
| **Smart Scoring** | ~10-15 | Scored/ranked plans (goal=1000pts, diet=100pts, region=10pts) |

---

## Which System Should You Use?

### Choose **Exact Match** if:
- ✅ You have strict requirements (e.g., religious diet restrictions)
- ✅ You want plans made specifically for your profile
- ✅ You're okay with "not available" if nothing matches

### Choose **Goal-Only** if:
- ✅ You want maximum variety (recommended!)
- ✅ Your main focus is achieving your goal
- ✅ You can adapt plans (e.g., substitute ingredients)
- ✅ You want to see all available options

### Choose **Smart Scoring** if:
- ✅ You want AI to decide priorities
- ✅ You prefer a balanced approach
- ✅ You trust weighted scoring logic

---

## Troubleshooting

### "No plans found"
**Solution:**
1. Try Goal-Only system (most flexible)
2. Check your profile has valid data
3. Try a different region or goal

### "Allergen rejection"
**Current behavior:** Plans with your allergens get -1000 score (rejected)
**Workaround:** Remove allergens from profile temporarily (in `service/data/profile.json`)

### Can't select plans
**Requirement:** Must select 2-5 plans
**Fix:** Click on plan cards to toggle selection

### Page not loading
**Check:** Server is running on port 8000
```bash
python -m uvicorn service.api:app --reload --port 8000
```

---

## Quick Test Commands

**Test all 3 systems at once:**
```bash
python test_both_systems.py
```

**Check your profile:**
```powershell
Get-Content "service\data\profile.json" | ConvertFrom-Json
```

**Rebuild index if needed:**
```bash
python pipeline\build_pdf_index.py
```

---

## Summary

✅ **3 systems now available on the website**
✅ **Visual interface at** `/choose-system`
✅ **Recommendations page at** `/get-recommendations`
✅ **All tested and working**

**Start here:** `http://localhost:8000/choose-system`
