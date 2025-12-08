import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { base44 } from '@/api/base44Client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format, differenceInDays } from 'date-fns';
import { Link } from 'react-router-dom';
import { createPageUrl } from '@/utils';
import { 
  Calendar, Scale, Target, TrendingUp, ChevronRight, 
  Flame, Droplets, MessageSquare, Settings
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

import TodayMealCard from '@/components/dashboard/TodayMealCard';
import NutritionRing from '@/components/dashboard/NutritionRing';
import WeekProgress from '@/components/dashboard/WeekProgress';

export default function Dashboard() {
  const today = format(new Date(), 'yyyy-MM-dd');
  const queryClient = useQueryClient();

  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => base44.auth.me()
  });

  const { data: profiles } = useQuery({
    queryKey: ['userProfile'],
    queryFn: () => base44.entities.UserProfile.filter({ created_by: user?.email }),
    enabled: !!user?.email
  });

  const { data: todayPlan } = useQuery({
    queryKey: ['todayPlan', today],
    queryFn: () => base44.entities.MealPlan.filter({ 
      user_email: user?.email, 
      date: today 
    }),
    enabled: !!user?.email
  });

  const { data: logs } = useQuery({
    queryKey: ['logs'],
    queryFn: () => base44.entities.DailyLog.filter({ user_email: user?.email }),
    enabled: !!user?.email
  });

  const { data: todayLog } = useQuery({
    queryKey: ['todayLog', today],
    queryFn: () => base44.entities.DailyLog.filter({ 
      user_email: user?.email, 
      date: today 
    }),
    enabled: !!user?.email
  });

  const profile = profiles?.[0];
  const meal = todayPlan?.[0];
  const log = todayLog?.[0];

  const currentDay = useMemo(() => {
    if (!profile?.plan_start_date) return 1;
    return differenceInDays(new Date(), new Date(profile.plan_start_date)) + 1;
  }, [profile]);

  const mealsEaten = log?.meals_eaten || {};
  const consumedCalories = useMemo(() => {
    if (!meal || !mealsEaten) return 0;
    let total = 0;
    if (mealsEaten.breakfast) total += meal.breakfast?.calories || 0;
    if (mealsEaten.mid_morning_snack) total += meal.mid_morning_snack?.calories || 0;
    if (mealsEaten.lunch) total += meal.lunch?.calories || 0;
    if (mealsEaten.evening_snack) total += meal.evening_snack?.calories || 0;
    if (mealsEaten.dinner) total += meal.dinner?.calories || 0;
    return total;
  }, [meal, mealsEaten]);

  const consumedProtein = useMemo(() => {
    if (!meal || !mealsEaten) return 0;
    let total = 0;
    if (mealsEaten.breakfast) total += meal.breakfast?.protein || 0;
    if (mealsEaten.mid_morning_snack) total += meal.mid_morning_snack?.protein || 0;
    if (mealsEaten.lunch) total += meal.lunch?.protein || 0;
    if (mealsEaten.evening_snack) total += meal.evening_snack?.protein || 0;
    if (mealsEaten.dinner) total += meal.dinner?.protein || 0;
    return total;
  }, [meal, mealsEaten]);

  const updateLogMutation = useMutation({
    mutationFn: async ({ mealType, eaten }) => {
      const newMealsEaten = { ...mealsEaten, [mealType]: eaten };
      
      if (log) {
        await base44.entities.DailyLog.update(log.id, { meals_eaten: newMealsEaten });
      } else {
        await base44.entities.DailyLog.create({
          user_email: user.email,
          date: today,
          meals_eaten: newMealsEaten
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todayLog'] });
      queryClient.invalidateQueries({ queryKey: ['logs'] });
    }
  });

  if (!profile?.onboarding_complete) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="text-center">
          <h2 className="text-2xl font-light mb-4">Welcome to nutriAI</h2>
          <p className="text-gray-500 mb-6">Let's set up your personalized nutrition plan</p>
          <Link to={createPageUrl('Onboarding')}>
            <Button className="bg-black hover:bg-gray-800">Get Started</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (!meal) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="text-center">
          <h2 className="text-2xl font-light mb-4">No meal plan found</h2>
          <p className="text-gray-500 mb-6">Let's generate your personalized plan</p>
          <Link to={createPageUrl('GeneratePlan')}>
            <Button className="bg-black hover:bg-gray-800">Generate Plan</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-2xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">{format(new Date(), 'EEEE, MMMM d')}</p>
              <h1 className="text-2xl font-semibold text-black">
                Day {currentDay} of 14
              </h1>
            </div>
            <Link to={createPageUrl('Profile')}>
              <Button variant="ghost" size="icon" className="rounded-full">
                <Settings className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Progress Rings */}
        <Card className="p-6 bg-white border-0 shadow-sm">
          <div className="flex items-center justify-around">
            <NutritionRing
              consumed={consumedCalories}
              target={profile.daily_calories || 2000}
              label="Calories"
              unit="kcal"
              color="black"
              size="large"
            />
            <NutritionRing
              consumed={consumedProtein}
              target={profile.daily_protein || 60}
              label="Protein"
              unit="g"
              color="blue"
            />
            <NutritionRing
              consumed={log?.water_intake || 0}
              target={8}
              label="Water"
              unit=" glasses"
              color="green"
            />
          </div>
        </Card>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-3">
          <Card className="p-4 bg-white border-0 shadow-sm text-center">
            <Scale className="w-5 h-5 mx-auto text-gray-400 mb-2" />
            <div className="text-lg font-bold">{profile.weight} kg</div>
            <div className="text-xs text-gray-500">Current</div>
          </Card>
          <Card className="p-4 bg-white border-0 shadow-sm text-center">
            <Target className="w-5 h-5 mx-auto text-gray-400 mb-2" />
            <div className="text-lg font-bold">{profile.target_weight} kg</div>
            <div className="text-xs text-gray-500">Target</div>
          </Card>
          <Card className="p-4 bg-white border-0 shadow-sm text-center">
            <Flame className="w-5 h-5 mx-auto text-gray-400 mb-2" />
            <div className="text-lg font-bold">{profile.daily_calories}</div>
            <div className="text-xs text-gray-500">Daily Goal</div>
          </Card>
        </div>

        {/* Today's Meals */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Today's Meals</h2>
            <Link to={createPageUrl('MealPlan')}>
              <Button variant="ghost" size="sm" className="text-gray-500">
                View All <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
          </div>

          {['breakfast', 'mid_morning_snack', 'lunch', 'evening_snack', 'dinner'].map(mealType => (
            <TodayMealCard
              key={mealType}
              mealType={mealType}
              meal={meal[mealType]}
              isCompleted={mealsEaten[mealType]}
              onView={() => window.location.href = createPageUrl(`MealDetail?date=${today}&meal=${mealType}`)}
              onMarkComplete={() => updateLogMutation.mutate({ 
                mealType, 
                eaten: !mealsEaten[mealType] 
              })}
            />
          ))}
        </div>

        {/* Week Progress */}
        <Card className="p-6 bg-white border-0 shadow-sm">
          <WeekProgress
            startDate={profile.plan_start_date}
            currentDay={currentDay}
            logs={logs}
          />
        </Card>

        {/* Daily Feedback CTA */}
        <Link to={createPageUrl('DailyFeedback')}>
          <Card className="p-6 bg-black text-white border-0 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center">
                  <MessageSquare className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold">Log Today's Feedback</h3>
                  <p className="text-sm text-gray-300">Help AI optimize your meals</p>
                </div>
              </div>
              <ChevronRight className="w-5 h-5" />
            </div>
          </Card>
        </Link>
      </div>
    </div>
  );
}