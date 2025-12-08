import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { base44 } from '@/api/base44Client';
import { useQuery } from '@tanstack/react-query';
import { format, addDays, isSameDay } from 'date-fns';
import { Link } from 'react-router-dom';
import { createPageUrl } from '@/utils';
import { ArrowLeft, ChevronLeft, ChevronRight, Calendar, Flame } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';

const mealOrder = ['breakfast', 'mid_morning_snack', 'lunch', 'evening_snack', 'dinner'];
const mealLabels = {
  breakfast: 'Breakfast',
  mid_morning_snack: 'Snack',
  lunch: 'Lunch',
  evening_snack: 'Tea Time',
  dinner: 'Dinner'
};

const mealIcons = {
  breakfast: '🍳',
  mid_morning_snack: '🍎',
  lunch: '🍛',
  evening_snack: '☕',
  dinner: '🥗'
};

export default function MealPlan() {
  const [selectedDate, setSelectedDate] = useState(new Date());

  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => base44.auth.me()
  });

  const { data: profiles } = useQuery({
    queryKey: ['userProfile'],
    queryFn: () => base44.entities.UserProfile.filter({ created_by: user?.email }),
    enabled: !!user?.email
  });

  const { data: plans } = useQuery({
    queryKey: ['mealPlans'],
    queryFn: () => base44.entities.MealPlan.filter({ user_email: user?.email }),
    enabled: !!user?.email
  });

  const profile = profiles?.[0];
  const selectedPlan = plans?.find(p => p.date === format(selectedDate, 'yyyy-MM-dd'));

  // Generate dates array
  const dates = [];
  const startDate = profile?.plan_start_date ? new Date(profile.plan_start_date) : new Date();
  for (let i = 0; i < 14; i++) {
    dates.push(addDays(startDate, i));
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link to={createPageUrl('Dashboard')}>
              <Button variant="ghost" size="icon">
                <ArrowLeft className="w-5 h-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-xl font-semibold">14-Day Meal Plan</h1>
              <p className="text-sm text-gray-500">Cycle {profile?.current_plan_cycle || 1}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Date Selector */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <ScrollArea className="w-full whitespace-nowrap">
            <div className="flex gap-2">
              {dates.map((date, i) => {
                const isSelected = isSameDay(date, selectedDate);
                const isToday = isSameDay(date, new Date());
                return (
                  <motion.button
                    key={i}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setSelectedDate(date)}
                    className={`flex-shrink-0 px-4 py-3 rounded-xl text-center transition-all
                      ${isSelected 
                        ? 'bg-black text-white' 
                        : isToday 
                          ? 'bg-gray-100 text-black border-2 border-black' 
                          : 'bg-gray-50 text-gray-700 hover:bg-gray-100'}`}
                  >
                    <div className="text-[10px] font-medium uppercase tracking-wide opacity-70">
                      {format(date, 'EEE')}
                    </div>
                    <div className="text-lg font-bold mt-1">{format(date, 'd')}</div>
                    <div className="text-[10px] mt-1">Day {i + 1}</div>
                  </motion.button>
                );
              })}
            </div>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 py-6">
        <AnimatePresence mode="wait">
          {selectedPlan ? (
            <motion.div
              key={selectedPlan.date}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {/* Daily Summary */}
              <Card className="p-4 bg-white border-0 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-gray-400" />
                    <span className="font-medium">{format(selectedDate, 'MMMM d, yyyy')}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Flame className="w-4 h-4 text-orange-500" />
                    <span className="font-bold">{selectedPlan.total_calories}</span>
                    <span className="text-gray-500">kcal</span>
                  </div>
                </div>
                <div className="flex items-center justify-center gap-6 mt-4 pt-4 border-t border-gray-100">
                  <div className="text-center">
                    <div className="text-sm font-bold text-blue-600">{selectedPlan.total_protein}g</div>
                    <div className="text-xs text-gray-500">Protein</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-bold text-amber-600">{selectedPlan.total_carbs}g</div>
                    <div className="text-xs text-gray-500">Carbs</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-bold text-green-600">{selectedPlan.total_fats}g</div>
                    <div className="text-xs text-gray-500">Fats</div>
                  </div>
                </div>
              </Card>

              {/* Meals */}
              {mealOrder.map((mealType) => {
                const meal = selectedPlan[mealType];
                if (!meal) return null;
                
                return (
                  <Link 
                    key={mealType}
                    to={createPageUrl(`MealDetail?date=${selectedPlan.date}&meal=${mealType}`)}
                  >
                    <Card className="p-4 bg-white border-0 shadow-sm hover:shadow-md transition-all">
                      <div className="flex items-start gap-4">
                        <div className="text-3xl">{mealIcons[mealType]}</div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                              {mealLabels[mealType]}
                            </span>
                            {meal.time && (
                              <span className="text-xs text-gray-400">• {meal.time}</span>
                            )}
                          </div>
                          <h3 className="font-semibold text-black">{meal.name}</h3>
                          {meal.description && (
                            <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                              {meal.description}
                            </p>
                          )}
                          <div className="flex items-center gap-4 mt-3 text-xs">
                            <span className="font-semibold">{meal.calories} kcal</span>
                            <span className="text-blue-600">P: {meal.protein}g</span>
                            <span className="text-amber-600">C: {meal.carbs}g</span>
                            <span className="text-green-600">F: {meal.fats}g</span>
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-gray-300" />
                      </div>
                    </Card>
                  </Link>
                );
              })}
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <div className="text-4xl mb-4">📅</div>
              <h3 className="text-lg font-medium text-gray-700">No plan for this day</h3>
              <p className="text-sm text-gray-500 mt-1">Select a day within your cycle</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}