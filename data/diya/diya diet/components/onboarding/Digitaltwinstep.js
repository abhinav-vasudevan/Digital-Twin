import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Flame, Target, Scale, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function DigitalTwinStep({ data }) {
  const [animatedBMI, setAnimatedBMI] = useState(0);
  const [animatedBMR, setAnimatedBMR] = useState(0);
  const [animatedTDEE, setAnimatedTDEE] = useState(0);
  const [animatedCalories, setAnimatedCalories] = useState(0);

  // Calculate metrics
  const calculateMetrics = () => {
    const height = data.height / 100; // convert to meters
    const bmi = data.weight / (height * height);
    
    // Mifflin-St Jeor Equation for BMR
    let bmr;
    if (data.gender === 'male') {
      bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age + 5;
    } else {
      bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age - 161;
    }

    // Activity multipliers
    const activityMultipliers = {
      sedentary: 1.2,
      light: 1.375,
      moderate: 1.55,
      active: 1.725,
      very_active: 1.9
    };

    const tdee = bmr * (activityMultipliers[data.activity_level] || 1.2);

    // Adjust calories based on goals
    let dailyCalories = tdee;
    if ((data.goals || []).includes('weight_loss')) {
      dailyCalories = tdee - 500; // 500 calorie deficit
    } else if ((data.goals || []).includes('weight_gain') || (data.goals || []).includes('muscle_building')) {
      dailyCalories = tdee + 300; // 300 calorie surplus
    }

    return {
      bmi: Math.round(bmi * 10) / 10,
      bmr: Math.round(bmr),
      tdee: Math.round(tdee),
      dailyCalories: Math.round(dailyCalories),
      protein: Math.round(data.weight * 1.6), // ICMR recommendation
      carbs: Math.round((dailyCalories * 0.5) / 4),
      fats: Math.round((dailyCalories * 0.25) / 9)
    };
  };

  const metrics = calculateMetrics();

  useEffect(() => {
    const duration = 1500;
    const steps = 60;
    const interval = duration / steps;

    let step = 0;
    const timer = setInterval(() => {
      step++;
      const progress = step / steps;
      setAnimatedBMI(metrics.bmi * progress);
      setAnimatedBMR(metrics.bmr * progress);
      setAnimatedTDEE(metrics.tdee * progress);
      setAnimatedCalories(metrics.dailyCalories * progress);
      if (step >= steps) clearInterval(timer);
    }, interval);

    return () => clearInterval(timer);
  }, [metrics.bmi, metrics.bmr, metrics.tdee, metrics.dailyCalories]);

  const getBMIStatus = (bmi) => {
    if (bmi < 18.5) return { label: 'Underweight', color: 'text-blue-500', bg: 'bg-blue-50' };
    if (bmi < 25) return { label: 'Normal', color: 'text-green-500', bg: 'bg-green-50' };
    if (bmi < 30) return { label: 'Overweight', color: 'text-yellow-500', bg: 'bg-yellow-50' };
    return { label: 'Obese', color: 'text-red-500', bg: 'bg-red-50' };
  };

  const bmiStatus = getBMIStatus(metrics.bmi);
  const weightDiff = data.target_weight ? data.weight - data.target_weight : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-8"
    >
      <div className="text-center mb-10">
        <h2 className="text-3xl font-light tracking-tight text-black mb-2">Your Digital Twin</h2>
        <p className="text-gray-500">AI-calculated metabolism profile based on ICMR/WHO guidelines</p>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className={`p-6 rounded-2xl ${bmiStatus.bg} border border-gray-100`}
        >
          <Scale className={`w-6 h-6 ${bmiStatus.color} mb-3`} />
          <div className="text-3xl font-bold text-black">{animatedBMI.toFixed(1)}</div>
          <div className="text-sm text-gray-600">BMI</div>
          <div className={`text-xs font-medium ${bmiStatus.color} mt-1`}>{bmiStatus.label}</div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="p-6 rounded-2xl bg-gray-50 border border-gray-100"
        >
          <Flame className="w-6 h-6 text-orange-500 mb-3" />
          <div className="text-3xl font-bold text-black">{Math.round(animatedBMR)}</div>
          <div className="text-sm text-gray-600">BMR</div>
          <div className="text-xs text-gray-500 mt-1">kcal/day at rest</div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="p-6 rounded-2xl bg-gray-50 border border-gray-100"
        >
          <Activity className="w-6 h-6 text-purple-500 mb-3" />
          <div className="text-3xl font-bold text-black">{Math.round(animatedTDEE)}</div>
          <div className="text-sm text-gray-600">TDEE</div>
          <div className="text-xs text-gray-500 mt-1">total daily burn</div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="p-6 rounded-2xl bg-black text-white"
        >
          <Target className="w-6 h-6 text-white mb-3" />
          <div className="text-3xl font-bold">{Math.round(animatedCalories)}</div>
          <div className="text-sm text-gray-300">Daily Target</div>
          <div className="text-xs text-gray-400 mt-1">kcal/day</div>
        </motion.div>
      </div>

      {/* Macros */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="p-6 rounded-2xl border border-gray-200 bg-white"
      >
        <h3 className="text-lg font-semibold mb-4">Daily Macro Targets</h3>
        <div className="grid grid-cols-3 gap-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Protein</span>
              <span className="text-sm font-bold">{metrics.protein}g</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: '100%' }}
                transition={{ delay: 0.6, duration: 0.8 }}
                className="h-full bg-blue-500 rounded-full"
              />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Carbs</span>
              <span className="text-sm font-bold">{metrics.carbs}g</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: '100%' }}
                transition={{ delay: 0.7, duration: 0.8 }}
                className="h-full bg-amber-500 rounded-full"
              />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Fats</span>
              <span className="text-sm font-bold">{metrics.fats}g</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: '100%' }}
                transition={{ delay: 0.8, duration: 0.8 }}
                className="h-full bg-green-500 rounded-full"
              />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Weight Journey */}
      {data.target_weight && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="p-6 rounded-2xl border border-gray-200 bg-white"
        >
          <h3 className="text-lg font-semibold mb-4">Your Journey</h3>
          <div className="flex items-center justify-between">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{data.weight} kg</div>
              <div className="text-sm text-gray-500">Current</div>
            </div>
            <div className="flex-1 mx-6 h-1 bg-gray-100 rounded-full relative">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: '50%' }}
                transition={{ delay: 0.8, duration: 1 }}
                className="absolute top-0 left-0 h-full bg-gradient-to-r from-gray-900 to-gray-400 rounded-full"
              />
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-black rounded-full border-4 border-white shadow-lg" />
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{data.target_weight} kg</div>
              <div className="text-sm text-gray-500">Target</div>
            </div>
          </div>
          <div className="text-center mt-4">
            <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium
              ${weightDiff > 0 ? 'bg-blue-50 text-blue-700' : weightDiff < 0 ? 'bg-green-50 text-green-700' : 'bg-gray-50 text-gray-700'}`}>
              {weightDiff > 0 ? <TrendingDown className="w-4 h-4" /> : weightDiff < 0 ? <TrendingUp className="w-4 h-4" /> : <Minus className="w-4 h-4" />}
              {Math.abs(weightDiff)} kg to {weightDiff > 0 ? 'lose' : weightDiff < 0 ? 'gain' : 'maintain'}
            </span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}