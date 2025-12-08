import React from 'react';
import { motion } from 'framer-motion';
import { Clock, ChevronRight, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

const mealIcons = {
  breakfast: '🍳',
  mid_morning_snack: '🍎',
  lunch: '🍛',
  evening_snack: '☕',
  dinner: '🥗'
};

const mealLabels = {
  breakfast: 'Breakfast',
  mid_morning_snack: 'Mid-morning Snack',
  lunch: 'Lunch',
  evening_snack: 'Evening Snack',
  dinner: 'Dinner'
};

export default function TodayMealCard({ mealType, meal, isCompleted, onView, onMarkComplete }) {
  if (!meal) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`p-4 rounded-2xl border transition-all duration-200
        ${isCompleted 
          ? 'bg-gray-50 border-gray-200 opacity-60' 
          : 'bg-white border-gray-100 hover:border-gray-300 hover:shadow-sm'}`}
    >
      <div className="flex items-start gap-4">
        <div className={`text-3xl ${isCompleted ? 'grayscale' : ''}`}>
          {mealIcons[mealType]}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              {mealLabels[mealType]}
            </span>
            {meal.time && (
              <span className="flex items-center text-xs text-gray-400">
                <Clock className="w-3 h-3 mr-1" />
                {meal.time}
              </span>
            )}
          </div>
          
          <h3 className={`font-semibold text-black mb-1 ${isCompleted ? 'line-through' : ''}`}>
            {meal.name}
          </h3>
          
          {meal.description && (
            <p className="text-sm text-gray-500 line-clamp-1 mb-2">
              {meal.description}
            </p>
          )}
          
          <div className="flex items-center gap-3 text-xs">
            <span className="text-gray-600">
              <span className="font-semibold text-black">{meal.calories}</span> kcal
            </span>
            <span className="text-blue-600">
              P: {meal.protein}g
            </span>
            <span className="text-amber-600">
              C: {meal.carbs}g
            </span>
            <span className="text-green-600">
              F: {meal.fats}g
            </span>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onView}
            className="text-gray-500 hover:text-black"
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onMarkComplete}
            className={isCompleted ? 'text-green-600' : 'text-gray-400 hover:text-green-600'}
          >
            <Check className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </motion.div>
  );
}