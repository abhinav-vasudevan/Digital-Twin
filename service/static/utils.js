// Utility Functions for Diet Plan App

// Date Formatting
function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en', { 
    weekday: 'long', 
    month: 'long', 
    day: 'numeric' 
  });
}

function formatShortDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en', { 
    month: 'short', 
    day: 'numeric' 
  });
}

function getTodayDate() {
  return new Date().toISOString().split('T')[0];
}

function addDays(dateStr, days) {
  const date = new Date(dateStr);
  date.setDate(date.getDate() + days);
  return date.toISOString().split('T')[0];
}

function daysBetween(date1, date2) {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  return Math.floor((d2 - d1) / (1000 * 60 * 60 * 24));
}

// BMR/TDEE Calculations (Mifflin-St Jeor Equation)
function calculateBMR(weight, height, age, gender) {
  // weight in kg, height in cm, age in years
  let bmr;
  if (gender === 'male') {
    bmr = 10 * weight + 6.25 * height - 5 * age + 5;
  } else {
    bmr = 10 * weight + 6.25 * height - 5 * age - 161;
  }
  return Math.round(bmr);
}

function calculateTDEE(bmr, activityLevel) {
  const activityMultipliers = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    active: 1.725,
    very_active: 1.9
  };
  return Math.round(bmr * (activityMultipliers[activityLevel] || 1.2));
}

function calculateBMI(weight, height) {
  // weight in kg, height in cm
  return ((weight / ((height / 100) ** 2))).toFixed(1);
}

function calculateDailyCalories(tdee, currentWeight, targetWeight) {
  if (targetWeight < currentWeight) {
    return Math.round(tdee - 500); // Weight loss: 500 cal deficit
  } else if (targetWeight > currentWeight) {
    return Math.round(tdee + 300); // Weight gain: 300 cal surplus
  }
  return tdee; // Maintenance
}

function calculateMacros(dailyCalories, proteinPercent = 0.30, carbsPercent = 0.40, fatsPercent = 0.30) {
  return {
    protein: Math.round((dailyCalories * proteinPercent) / 4), // 4 cal per gram
    carbs: Math.round((dailyCalories * carbsPercent) / 4),
    fats: Math.round((dailyCalories * fatsPercent) / 9) // 9 cal per gram
  };
}

// Local Storage Helpers
function saveToStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error('Error saving to storage:', error);
    return false;
  }
}

function getFromStorage(key, defaultValue = null) {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error('Error reading from storage:', error);
    return defaultValue;
  }
}

function removeFromStorage(key) {
  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error('Error removing from storage:', error);
    return false;
  }
}

// API Helpers
async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(endpoint, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
}

// Number Formatting
function formatNumber(num, decimals = 0) {
  return Number(num).toFixed(decimals);
}

function formatPercent(value, total) {
  if (total === 0) return 0;
  return Math.min(Math.round((value / total) * 100), 100);
}

// String Helpers
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatLabel(str) {
  return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Time of Day
function getTimeOfDay() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Morning';
  if (hour < 18) return 'Afternoon';
  return 'Evening';
}

// Export for use in modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    formatDate,
    formatShortDate,
    getTodayDate,
    addDays,
    daysBetween,
    calculateBMR,
    calculateTDEE,
    calculateBMI,
    calculateDailyCalories,
    calculateMacros,
    saveToStorage,
    getFromStorage,
    removeFromStorage,
    apiRequest,
    formatNumber,
    formatPercent,
    capitalize,
    formatLabel,
    getTimeOfDay
  };
}
