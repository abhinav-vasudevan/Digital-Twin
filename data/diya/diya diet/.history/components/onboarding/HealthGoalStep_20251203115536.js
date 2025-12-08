import React from 'react';
import { motion } from 'framer-motion';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Target, Scale, Flame, Heart, Brain, Moon, Zap, Smile } from 'lucide-react';

const goals = [
  { id: 'weight_loss', label: 'Weight Loss', icon: Scale, desc: 'Lose weight healthily' },
  { id: 'weight_gain', label: 'Weight Gain', icon: Flame, desc: 'Build mass & muscle' },
  { id: 'maintain', label: 'Maintain Weight', icon: Target, desc: 'Stay at current weight' },
  { id: 'muscle_building', label: 'Build Muscle', icon: Zap, desc: 'Increase muscle mass' },
  { id: 'energy', label: 'More Energy', icon: Flame, desc: 'Boost daily energy' },
  { id: 'better_sleep', label: 'Better Sleep', icon: Moon, desc: 'Improve sleep quality' },
  { id: 'clear_skin', label: 'Clear Skin', icon: Smile, desc: 'Reduce acne & glow' },
  { id: 'gut_health', label: 'Gut Health', icon: Heart, desc: 'Improve digestion' },
];

const medicalConditions = [
  'Diabetes Type 1', 'Diabetes Type 2', 'Hypertension', 'PCOS', 'Thyroid', 
  'Heart Disease', 'Cholesterol', 'Fatty Liver', 'IBS', 'Celiac Disease', 'None'
];

export default function HealthGoalsStep({ data, onChange }) {
  const toggleGoal = (goalId) => {
    const current = data.goals || [];
    const updated = current.includes(goalId)
      ? current.filter(g => g !== goalId)
      : [...current, goalId];
    onChange({ ...data, goals: updated });
  };

  const toggleCondition = (condition) => {
    if (condition === 'None') {
      onChange({ ...data, medical_conditions: [] });
      return;
    }
    const current = data.medical_conditions || [];
    const updated = current.includes(condition)
      ? current.filter(c => c !== condition)
      : [...current, condition];
    onChange({ ...data, medical_conditions: updated });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-10"
    >
      <div className="text-center mb-10">
        <h2 className="text-3xl font-light tracking-tight text-black mb-2">Your health goals</h2>
        <p className="text-gray-500">What would you like to achieve?</p>
      </div>

      {/* Goals */}
      <div className="space-y-4">
        <Label className="text-sm font-medium text-gray-700">Select Your Goals (choose multiple)</Label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {goals.map((goal) => {
            const Icon = goal.icon;
            const isSelected = (data.goals || []).includes(goal.id);
            return (
              <motion.button
                key={goal.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => toggleGoal(goal.id)}
                className={`p-4 rounded-xl border-2 text-left transition-all duration-200
                  ${isSelected 
                    ? 'border-black bg-black text-white' 
                    : 'border-gray-200 hover:border-gray-400 bg-white'}`}
              >
                <Icon className={`w-5 h-5 mb-2 ${isSelected ? 'text-white' : 'text-gray-600'}`} />
                <div className="font-medium text-sm">{goal.label}</div>
                <div className={`text-xs ${isSelected ? 'text-gray-300' : 'text-gray-500'}`}>
                  {goal.desc}
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Medical Conditions */}
      <div className="space-y-4">
        <Label className="text-sm font-medium text-gray-700">Medical Conditions (if any)</Label>
        <div className="flex flex-wrap gap-2">
          {medicalConditions.map((condition) => (
            <motion.button
              key={condition}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => toggleCondition(condition)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
                ${(data.medical_conditions || []).includes(condition) || (condition === 'None' && (!data.medical_conditions || data.medical_conditions.length === 0))
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              {condition}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Additional Notes */}
      <div className="space-y-2">
        <Label className="text-sm font-medium text-gray-700">Any other health concerns?</Label>
        <Textarea
          placeholder="Tell us about any specific health concerns, dietary restrictions, or preferences..."
          value={data.notes || ''}
          onChange={(e) => onChange({ ...data, notes: e.target.value })}
          className="min-h-24 bg-gray-50 border-gray-200 focus:border-black focus:ring-black"
        />
      </div>
    </motion.div>
  );
}