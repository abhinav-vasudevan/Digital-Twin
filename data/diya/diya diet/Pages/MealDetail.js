import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { base44 } from '@/api/base44Client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';
import { createPageUrl } from '@/utils';
import { 
  ArrowLeft, Clock, Flame, RefreshCw, Check, 
  ChefHat, ShoppingBag, AlertCircle, Loader2 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const mealLabels = {
  breakfast: 'Breakfast',
  mid_morning_snack: 'Mid-morning Snack',
  lunch: 'Lunch',
  evening_snack: 'Evening Snack',
  dinner: 'Dinner'
};

const mealIcons = {
  breakfast: '🍳',
  mid_morning_snack: '🍎',
  lunch: '🍛',
  evening_snack: '☕',
  dinner: '🥗'
};

export default function MealDetail() {
  const urlParams = new URLSearchParams(window.location.search);
  const date = urlParams.get('date');
  const mealType = urlParams.get('meal');
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

  const { data: plans } = useQuery({
    queryKey: ['mealPlan', date],
    queryFn: () => base44.entities.MealPlan.filter({ 
      user_email: user?.email, 
      date 
    }),
    enabled: !!user?.email && !!date
  });

  const { data: todayLog } = useQuery({
    queryKey: ['todayLog', date],
    queryFn: () => base44.entities.DailyLog.filter({ 
      user_email: user?.email, 
      date 
    }),
    enabled: !!user?.email && !!date
  });

  const profile = profiles?.[0];
  const plan = plans?.[0];
  const meal = plan?.[mealType];
  const log = todayLog?.[0];
  const isEaten = log?.meals_eaten?.[mealType];

  const markEatenMutation = useMutation({
    mutationFn: async () => {
      const newMealsEaten = { ...(log?.meals_eaten || {}), [mealType]: !isEaten };
      
      if (log) {
        await base44.entities.DailyLog.update(log.id, { meals_eaten: newMealsEaten });
      } else {
        await base44.entities.DailyLog.create({
          user_email: user.email,
          date,
          meals_eaten: newMealsEaten
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todayLog'] });
    }
  });

  const swapMealMutation = useMutation({
    mutationFn: async () => {
      const prompt = `Generate an alternative ${mealType} meal for a ${profile.diet_type} ${profile.region?.replace('_', ' ')} diet.
      Current meal: ${meal.name}
      Allergies to avoid: ${(profile.allergies || []).join(', ') || 'None'}
      Medical conditions: ${(profile.medical_conditions || []).join(', ') || 'None'}
      Target calories: approximately ${meal.calories} kcal
      Target protein: approximately ${meal.protein}g
      
      Provide a different but equally nutritious alternative.`;

      const response = await base44.integrations.Core.InvokeLLM({
        prompt,
        response_json_schema: {
          type: "object",
          properties: {
            name: { type: "string" },
            description: { type: "string" },
            calories: { type: "number" },
            protein: { type: "number" },
            carbs: { type: "number" },
            fats: { type: "number" },
            ingredients: { type: "array", items: { type: "string" } },
            recipe: { type: "string" },
            time: { type: "string" }
          }
        }
      });

      await base44.entities.MealPlan.update(plan.id, {
        [mealType]: response,
        is_adjusted: true,
        adjustment_reason: 'Meal swapped by user'
      });

      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mealPlan'] });
    }
  });

  if (!meal) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🍽️</div>
          <p className="text-gray-500">Meal not found</p>
          <Link to={createPageUrl('Dashboard')}>
            <Button className="mt-4" variant="outline">Go Back</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link to={createPageUrl('MealPlan')}>
              <Button variant="ghost" size="icon">
                <ArrowLeft className="w-5 h-5" />
              </Button>
            </Link>
            <div className="flex-1">
              <p className="text-sm text-gray-500">{mealLabels[mealType]}</p>
              <h1 className="text-xl font-semibold">{meal.name}</h1>
            </div>
            <span className="text-3xl">{mealIcons[mealType]}</span>
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-4">
        {/* Nutrition Card */}
        <Card className="p-6 bg-white border-0 shadow-sm">
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-black">{meal.calories}</div>
              <div className="text-xs text-gray-500">Calories</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">{meal.protein}g</div>
              <div className="text-xs text-gray-500">Protein</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-amber-600">{meal.carbs}g</div>
              <div className="text-xs text-gray-500">Carbs</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{meal.fats}g</div>
              <div className="text-xs text-gray-500">Fats</div>
            </div>
          </div>

          {meal.time && (
            <div className="flex items-center justify-center gap-2 mt-4 pt-4 border-t border-gray-100">
              <Clock className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">Recommended time: {meal.time}</span>
            </div>
          )}
        </Card>

        {/* Description */}
        {meal.description && (
          <Card className="p-6 bg-white border-0 shadow-sm">
            <h3 className="font-semibold mb-2">About this meal</h3>
            <p className="text-gray-600">{meal.description}</p>
          </Card>
        )}

        {/* Ingredients */}
        {meal.ingredients && meal.ingredients.length > 0 && (
          <Card className="p-6 bg-white border-0 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <ShoppingBag className="w-5 h-5 text-gray-400" />
              <h3 className="font-semibold">Ingredients</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {meal.ingredients.map((ingredient, i) => (
                <Badge key={i} variant="secondary" className="bg-gray-100 text-gray-700">
                  {ingredient}
                </Badge>
              ))}
            </div>
          </Card>
        )}

        {/* Recipe */}
        {meal.recipe && (
          <Card className="p-6 bg-white border-0 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <ChefHat className="w-5 h-5 text-gray-400" />
              <h3 className="font-semibold">Recipe</h3>
            </div>
            <p className="text-gray-600 whitespace-pre-wrap">{meal.recipe}</p>
          </Card>
        )}

        {/* Allergy Notice */}
        {profile?.allergies?.length > 0 && (
          <Card className="p-4 bg-amber-50 border border-amber-200">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-medium text-amber-800">Allergy Safe</h4>
                <p className="text-sm text-amber-700">
                  This meal has been crafted avoiding: {profile.allergies.join(', ')}
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3 pt-4">
          <Button
            variant="outline"
            className="h-14"
            onClick={() => swapMealMutation.mutate()}
            disabled={swapMealMutation.isPending}
          >
            {swapMealMutation.isPending ? (
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="w-5 h-5 mr-2" />
            )}
            Swap Meal
          </Button>

          <Button
            className={`h-14 ${isEaten ? 'bg-green-600 hover:bg-green-700' : 'bg-black hover:bg-gray-800'}`}
            onClick={() => markEatenMutation.mutate()}
            disabled={markEatenMutation.isPending}
          >
            <Check className="w-5 h-5 mr-2" />
            {isEaten ? 'Marked as Eaten' : 'Mark as Eaten'}
          </Button>
        </div>
      </div>
    </div>
  );
}