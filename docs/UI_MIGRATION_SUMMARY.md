# Diet Plan UI Migration - Diya Design System Implementation

## ✅ Completed Implementation

Successfully migrated the Diya UI design system to your existing diet plan project. The new implementation features a modern, clean interface with comprehensive meal planning, tracking, and profile management capabilities.

## 🎨 New Pages Created

### 1. **Layout Template** (`layout.html`)
- Bottom navigation with Home, Plan, and Profile tabs
- Clean, modern design with proper routing
- Responsive mobile-first design
- SVG icons matching Diya's aesthetic

### 2. **Onboarding Flow** (`onboarding.html`)
- 4-step wizard: Basics → Preferences → Goals → Digital Twin
- Progress indicators showing current step
- Real-time BMR/TDEE/BMI calculations
- Macro targets preview (protein, carbs, fats)
- Form validation and error handling
- Saves complete user profile to backend

### 3. **Dashboard** (`dashboard.html`)
- Welcome header with current cycle info (Day X/14)
- **3 Nutrition Rings**: Calories, Protein, Water (animated SVG circles)
- Quick stats: Current weight, Target weight, Progress
- **Today's Meals**: All 5 meals with completion checkboxes
  - Breakfast, Mid-morning Snack, Lunch, Evening Snack, Dinner
  - Meal icons, names, descriptions, macros
  - Mark as eaten functionality
- **14-Day Progress Calendar**: Grid view showing completed/today/upcoming days
- Daily feedback CTA

### 4. **Meal Plan Calendar** (`meal-plan.html`)
- **Horizontal date scroll**: 14-day picker with today indicator
- Selected day header with total macros
- Meal cards grid for the selected date
- Each meal card shows:
  - Icon, meal type label, name
  - Description, calories, protein, carbs, fats
  - Link to detail view

### 5. **Meal Detail** (`meal-detail.html`)
- Large nutrition grid: Calories, Protein, Carbs, Fats
- Meal description and recommended time
- **Ingredients**: Badge list of all ingredients
- **Recipe**: Step-by-step cooking instructions
- Allergy safe notice (if user has allergies)
- **Swap Meal** button: Generate alternative
- **Mark as Eaten** button: Track completion

### 6. **Profile Page** (`profile.html`)
- User info card with avatar, name, email, diet/region badges
- **Cycle Progress**: Current cycle, days remaining, progress bar
- **Body Stats**: Current weight, target weight, progress indicator
- **Metabolic Profile**: BMI, BMR, TDEE, Daily Calories with status
- **Daily Macro Targets**: Protein, Carbs, Fats with progress bars
- **Health Profile**: Goals, Medical conditions, Allergies as badges
- **Generate New 14-Day Plan** button
- Update Profile link

### 7. **Generate Plan** (`generate-plan.html`)
- Animated AI generation flow
- 4 steps with icons and descriptions:
  - Analyzing Metabolism 🧬
  - Simulating Strategies 🔄
  - Curating Meals 🍽️
  - Finalizing Plan ✅
- Progress bar with percentage
- Redirects to Dashboard when complete

## 🎨 Design System (styles.css)

### Color Palette (Light Theme)
```css
--bg: #f8f9fa          /* Light gray background */
--bg-soft: #ffffff     /* White cards */
--text: #000000        /* Black text */
--text-muted: #6b7280  /* Gray text */
--primary: #000000     /* Black primary */
--accent-blue: #3b82f6
--accent-amber: #f59e0b
--accent-green: #10b981
--accent-cyan: #06b6d4
--accent-red: #ef4444
```

### Components
- **Cards**: Rounded corners (16px), subtle shadows, white background
- **Buttons**: Primary (black), Secondary (outlined), Icon buttons
- **Badges**: Black, Outline, Red variants for different contexts
- **Progress Bars**: Animated, color-coded for different metrics
- **Nutrition Rings**: SVG circles with animated stroke-dashoffset
- **Calendar Grid**: 7-column responsive layout
- **Form Controls**: Clean inputs with focus states
- **Navigation**: Fixed bottom nav with active states

### Responsive Design
- Mobile-first approach
- Breakpoints at 640px
- Single column on mobile
- Touch-friendly tap targets
- Horizontal scrolling for date picker

## 🔧 Backend Updates (api.py)

### New Routes

#### Page Routes
- `GET /` - Root redirects to onboarding or dashboard
- `GET /onboarding` - Onboarding wizard
- `GET /dashboard` - Main dashboard
- `GET /meal-plan` - 14-day calendar view
- `GET /meal-detail` - Individual meal details
- `GET /profile` - User profile page
- `GET /generate-plan` - AI generation animation

#### API Endpoints
- `GET /api/profile` - Get user profile
- `POST /api/profile` - Create/update profile
- `POST /api/profile/new-cycle` - Start new 14-day cycle
- `GET /api/meal-plan?date=YYYY-MM-DD` - Get meals for date
- `POST /api/meal-plan/generate` - Generate 14-day plan
- `POST /api/meal-plan/swap` - Swap a meal with alternative
- `GET /api/daily-log?date=YYYY-MM-DD` - Get daily log
- `POST /api/daily-log/meal` - Toggle meal completion
- `POST /api/daily-log/water` - Update water intake

### Data Storage
- JSON file-based storage in `service/data/`
- Files: `profile.json`, `meal_plans.json`, `daily_logs.json`
- Easily upgradeable to database (SQLite, PostgreSQL)

### Data Models

**UserProfile**:
- Personal: age, gender, height, weight, target_weight
- Diet: region, diet_type, allergies, medical_conditions, goals
- Metrics: bmi, bmr, tdee, daily_calories, daily_protein/carbs/fats
- State: onboarding_complete, plan_start_date, current_plan_cycle

**MealPlan**:
- Meta: date, day_number (1-14), cycle
- Meals: breakfast, mid_morning_snack, lunch, evening_snack, dinner
- Each meal: name, description, calories, protein, carbs, fats, ingredients[], recipe, time
- Totals: total_calories, total_protein, total_carbs, total_fats

**DailyLog**:
- date
- meals_eaten: {breakfast: true/false, ...}
- water_intake: number of glasses
- notes: string

## 📊 JavaScript Utilities (utils.js)

### Date Functions
- `formatDate()`, `formatShortDate()`, `getTodayDate()`
- `addDays()`, `daysBetween()`

### Calculations
- `calculateBMR()` - Mifflin-St Jeor equation
- `calculateTDEE()` - Activity multipliers
- `calculateBMI()` - Weight/height formula
- `calculateDailyCalories()` - Goal-adjusted TDEE
- `calculateMacros()` - 30/40/30 split

### Storage
- `saveToStorage()`, `getFromStorage()`, `removeFromStorage()`

### API
- `apiRequest()` - Fetch wrapper with error handling

## 🚀 How to Use

### 1. Start the Server
```powershell
cd "D:\Documents\Diet plan"
.\.venv\Scripts\Activate.ps1
python -m uvicorn service.api:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Access the Application
Open browser to: **http://localhost:8000**

### 3. First-Time Flow
1. **Onboarding**: Complete 4-step wizard
2. **Generate Plan**: Watch AI generate 14-day meal plan
3. **Dashboard**: View today's meals and progress
4. **Meal Plan**: Browse all 14 days
5. **Profile**: View metabolic profile and cycle progress

### 4. Daily Usage
- Open Dashboard to see today's meals
- Check off meals as you eat them
- View nutrition ring progress (calories, protein, water)
- Track 14-day progress in calendar
- Browse Meal Plan for upcoming days
- View Meal Details for recipes and ingredients
- Swap meals if you want alternatives

## ✨ Key Features Adopted from Diya

1. **Onboarding Wizard**: Multi-step profile creation with progress
2. **Digital Twin**: Real-time BMR/TDEE/macro calculations
3. **Nutrition Visualization**: Animated SVG rings for daily tracking
4. **14-Day Cycle**: Complete meal plan with day-by-day view
5. **Meal Tracking**: Mark meals as eaten, track completion
6. **Calendar View**: Visual 14-day progress indicator
7. **Meal Swapping**: AI-powered alternative generation (simplified)
8. **Profile Management**: Complete metabolic and health profile
9. **Responsive Design**: Mobile-first, touch-friendly
10. **Clean UI**: Modern, minimalist aesthetic with clear hierarchy

## 📝 Next Steps (Optional Enhancements)

### Immediate
- [ ] Connect to your existing recommendation engine
- [ ] Add real LLM integration for meal generation
- [ ] Implement database (SQLite or PostgreSQL)

### Advanced
- [ ] Daily feedback page with mood/energy/digestion tracking
- [ ] AI insights based on adherence patterns
- [ ] Weight logging and progress charts
- [ ] Grocery list generation from meal plans
- [ ] Recipe photos and nutrition labels
- [ ] Social features (share plans, recipes)
- [ ] Push notifications for meal times
- [ ] Export meal plans to PDF/calendar

## 🎯 Comparison: Before vs After

### Before
- Single-page form
- JSON output display
- Basic dark theme
- No meal tracking
- No progress visualization
- No user profiles

### After
- 7 dedicated pages with routing
- Complete onboarding flow
- Dashboard with nutrition rings
- 14-day meal calendar
- Detailed meal views with recipes
- Profile with cycle tracking
- Light, clean Diya-inspired design
- Mobile responsive
- Mark meals as eaten
- Progress calendars
- BMR/TDEE calculations

## 🔗 URLs

- **Homepage**: http://localhost:8000
- **Dashboard**: http://localhost:8000/dashboard
- **Meal Plan**: http://localhost:8000/meal-plan
- **Profile**: http://localhost:8000/profile
- **API Docs**: http://localhost:8000/docs

## 📦 Files Changed/Created

### Templates (7 new)
- ✅ `layout.html` - Base layout with navigation
- ✅ `onboarding.html` - 4-step wizard
- ✅ `dashboard.html` - Main view
- ✅ `meal-plan.html` - Calendar view
- ✅ `meal-detail.html` - Recipe details
- ✅ `profile.html` - User profile
- ✅ `generate-plan.html` - AI generation

### Static Files
- ✅ `styles.css` - Complete redesign (1000+ lines)
- ✅ `utils.js` - Helper functions

### Backend
- ✅ `api.py` - Updated with 10+ new routes
- ✅ `data/` - JSON storage directory (auto-created)

---

**Status**: ✅ Fully functional and ready to use!

**Server**: Running at http://localhost:8000

**Next**: Open browser and start onboarding flow!
