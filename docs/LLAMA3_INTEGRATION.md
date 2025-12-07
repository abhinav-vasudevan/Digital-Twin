# Llama 3 AI Integration for Digital Twin Nutrition System

## Overview
The Digital Twin Nutrition system now uses **Llama 3** via **Ollama** for production-level, intelligent diet planning. This integration provides:

✅ **Personalized meal plans** based on comprehensive user profiles  
✅ **Allergy-safe recommendations** with multi-layer validation  
✅ **Daily feedback analysis** to adapt plans in real-time  
✅ **Intelligent meal alternatives** when users need variety  
✅ **Local, private AI** - no external API calls or data sharing

## Features

### 1. Smart Meal Planning
- **7-14 day personalized plans** generated from user profile
- Considers: age, weight, goals, activity level, health conditions
- Respects: dietary preferences (veg/non-veg/vegan), allergies, cuisine preferences
- Includes: detailed ingredients, portions, calories, macros, cooking instructions

### 2. Allergy Safety System
- **Pre-validation**: Checks ingredients against allergy list
- **Post-validation**: Scans AI-generated plans for allergen mentions
- **Safety fallback**: Provides safe basic plan if allergens detected
- **User warnings**: Alerts on potential cross-contamination

### 3. Daily Feedback Processing
- Analyzes: mood, energy, digestion, sleep, symptoms, adherence
- Provides: actionable insights, motivational messages
- Suggests: specific meal modifications to improve outcomes
- Tracks: patterns over time for continuous improvement

### 4. Meal Alternatives
- Generates 3+ alternatives for any meal
- Maintains similar calorie and macro profiles
- Respects all dietary restrictions and allergies
- Provides rationale for why each alternative is suitable

## Architecture

```
┌─────────────────┐
│  FastAPI App    │ ← User requests
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ llama_service.py│ ← AI integration layer
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Ollama API      │ ← localhost:11434
│ (Llama 3)       │
└─────────────────┘
```

### Key Components

**`service/llama_service.py`**
- `LlamaService` class: Handles all Ollama interactions
- `generate_meal_plan()`: Creates 7-day intelligent meal plans
- `analyze_feedback()`: Processes daily user feedback
- `get_meal_alternatives()`: Generates safe meal swaps
- `_validate_allergen_safety()`: Multi-layer allergen checking

**`service/api.py`** (Updated endpoints)
- `POST /api/meal-plan/generate`: AI-powered meal planning
- `POST /api/meal-plan/swap`: Intelligent meal alternatives
- `POST /api/daily-log/feedback`: Feedback analysis with insights

## Installation & Setup

### Prerequisites
1. **Ollama installed** on your system
2. **Llama 3 model** pulled to Ollama

### Setup Steps

```powershell
# 1. Install Ollama (if not already installed)
# Download from: https://ollama.ai/

# 2. Pull Llama 3 model
ollama pull llama3

# 3. Verify Ollama is running
ollama list

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Start the application
uvicorn service.api:app --reload
```

### Verify Integration

```powershell
# Check if Ollama is accessible
curl http://localhost:11434/api/tags

# Test the application
curl http://localhost:8000/ping
```

## Usage

### Generate AI Meal Plan

```javascript
// Frontend call
const response = await fetch('/api/meal-plan/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ /* empty or additional preferences */ })
});

const data = await response.json();
// Returns: { status, plans[], ai_rationale }
```

### Submit Daily Feedback

```javascript
const feedback = {
  mood: "good",
  energy_level: 7,
  digestion: "comfortable",
  sleep_quality: "good",
  symptoms: [],
  water_intake: 8,
  weight: 70.5,
  notes: "Felt great today!",
  adherence: "yes",
  satisfaction: 5
};

const response = await fetch('/api/daily-log/feedback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(feedback)
});

const result = await response.json();
// Returns: { ai_insight, motivation, went_well[], needs_improvement[], suggested_changes }
```

### Swap a Meal

```javascript
const swapRequest = {
  date: "2024-01-15",
  meal_type: "dinner",
  reason: "Don't like fish"
};

const response = await fetch('/api/meal-plan/swap', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(swapRequest)
});

const result = await response.json();
// Returns: { status, meal, alternatives[] }
```

## Allergy Safety

### How It Works

1. **User Profile**: Allergies stored in profile (e.g., `"allergies": ["peanuts", "dairy"]`)
2. **AI Prompt**: Allergies included in prompt with ⚠️ emphasis
3. **Response Parsing**: AI generates JSON with meal details
4. **Safety Validation**: `_validate_allergen_safety()` scans all ingredients
5. **Fallback**: If allergens detected, safe basic plan is used

### Example Validation

```python
# User has peanut allergy
profile = {"allergies": ["peanuts"]}

# AI generates meal plan
meal_plan = llama.generate_meal_plan(profile, days=7)

# Validation checks
if not llama._validate_allergen_safety(meal_plan, ["peanuts"]):
    # REJECTED - falls back to safe plan
    meal_plan = llama._create_safe_fallback_plan(profile)
```

### Safety Guarantees

✅ Allergens ALWAYS included in AI prompts  
✅ Multi-layer validation (pre + post generation)  
✅ Automatic fallback if unsafe content detected  
✅ Clear warning logs when allergens found  

## Fallback Behavior

If Ollama is unavailable (e.g., on Render deployment), the system automatically falls back to:

1. **Basic rule-based meal plans** (safe, allergen-aware)
2. **Simple feedback insights** (pattern-based analysis)
3. **Template alternatives** (pre-defined safe options)

This ensures the app remains functional even without AI.

## Deployment Considerations

### Local Development (Full AI)
- Ollama runs locally
- Full Llama 3 capabilities
- Low latency, private
- No API costs

### Production on Render (Fallback Mode)
- Ollama NOT available on free tier
- Uses fallback functions
- Still safe and functional
- Limited intelligence

### Production with AI (Recommended)
- Self-hosted server with Ollama
- OR: Use paid Render plan with Docker
- OR: Separate AI service (API endpoint)

## Performance

### Typical Response Times
- **Meal plan generation**: 15-30 seconds (7 days)
- **Feedback analysis**: 3-5 seconds
- **Meal alternatives**: 5-10 seconds

### Optimization Tips
1. Use `temperature=0.3` for consistent meal plans
2. Limit `max_tokens` to reduce generation time
3. Cache common responses (future enhancement)
4. Pre-generate plans during off-peak hours

## Troubleshooting

### Issue: "Ollama not available"
**Solution**: 
```powershell
# Start Ollama service
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### Issue: Slow AI responses
**Solution**:
- Reduce `days` parameter (7 instead of 14)
- Lower `max_tokens` in prompts
- Use smaller model (llama3:8b instead of llama3:70b)

### Issue: Allergen detected in plan
**Solution**:
- Automatic fallback engaged
- Check logs for which allergen was detected
- Review user profile for correct allergy spelling

### Issue: JSON parse errors
**Solution**:
- AI response format improved with explicit JSON instructions
- Fallback plans used if parsing fails
- Check Ollama model version (update if old)

## Future Enhancements

🔮 **Planned Features**
- [ ] Multi-language meal plans (Hindi, Spanish, etc.)
- [ ] Recipe video generation links
- [ ] Grocery shopping list automation
- [ ] Nutrient deficiency predictions
- [ ] Social sharing of meal plans
- [ ] Integration with fitness trackers

## API Reference

### `LlamaService.generate_meal_plan(profile, days, current_feedback)`
Generates comprehensive meal plan with allergy safety.

**Parameters:**
- `profile` (Dict): User profile with allergies, goals, preferences
- `days` (int): Number of days (default: 7)
- `current_feedback` (List[Dict]): Recent feedback for context

**Returns:**
```python
{
  "meal_plan": {
    "day_1": {
      "breakfast": {...},
      "snack_1": {...},
      "lunch": {...},
      "snack_2": {...},
      "dinner": {...}
    },
    ...
  },
  "daily_totals": {"calories": 1800, "protein_g": 90, ...},
  "safety_check": "All meals verified allergen-free",
  "rationale": "Explanation of plan..."
}
```

### `LlamaService.analyze_feedback(profile, feedback, current_plan)`
Analyzes daily feedback and suggests improvements.

**Parameters:**
- `profile` (Dict): User profile
- `feedback` (Dict): Daily feedback data
- `current_plan` (Dict): Current meal plan

**Returns:**
```python
{
  "analysis": "Brief summary...",
  "went_well": ["Point 1", "Point 2"],
  "needs_improvement": ["Issue 1", "Issue 2"],
  "suggested_changes": {
    "breakfast": "suggestion or null",
    "lunch": "suggestion or null",
    ...
  },
  "motivation": "Encouraging message",
  "allergen_safety_confirmed": true
}
```

### `LlamaService.get_meal_alternatives(profile, original_meal, reason)`
Generates safe meal alternatives.

**Parameters:**
- `profile` (Dict): User profile with allergies
- `original_meal` (Dict): Meal to replace
- `reason` (str): Why alternatives needed

**Returns:**
```python
[
  {
    "name": "Alternative Meal",
    "ingredients": [...],
    "calories": 400,
    "protein_g": 25,
    "carbs_g": 45,
    "fats_g": 12,
    "instructions": "...",
    "why_better": "Reason..."
  },
  ... (2 more alternatives)
]
```

## Security & Privacy

✅ **All AI processing happens locally** - no data sent to external APIs  
✅ **No training on user data** - Llama 3 is pre-trained  
✅ **Allergy safety is paramount** - multi-layer validation  
✅ **Fallback always available** - system never fully fails  

## Contributing

To improve the AI integration:

1. Test with edge cases (rare allergies, extreme diets)
2. Improve prompt engineering in `llama_service.py`
3. Add more fallback templates for common scenarios
4. Optimize response parsing for faster results

## Support

For issues related to:
- **Ollama setup**: Visit [ollama.ai/docs](https://ollama.ai/docs)
- **AI integration**: Check logs in `service/llama_service.py`
- **API errors**: Review FastAPI logs with `--log-level debug`

---

**Built with ❤️ using Llama 3, Ollama, FastAPI, and Python**
