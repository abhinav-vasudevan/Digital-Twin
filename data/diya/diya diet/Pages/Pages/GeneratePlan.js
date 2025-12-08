import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { base44 } from '@/api/base44Client';
import { useQuery } from '@tanstack/react-query';
import { Loader2, Sparkles, ChefHat, Brain, CheckCircle } from 'lucide-react';
import { createPageUrl } from '@/utils';

const generationSteps = [
  { icon: Brain, label: 'Analyzing your metabolism profile', duration: 2000 },
  { icon: Sparkles, label: 'Simulating diet strategies', duration: 2500 },
  { icon: ChefHat, label: 'Curating personalized meals', duration: 3000 },
  { icon: CheckCircle, label: 'Finalizing your 14-day plan', duration: 2000 },
];

export default function GeneratePlan() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isGenerating, setIsGenerating] = useState(true);

  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => base44.auth.me()
  });

  const { data: profiles } = useQuery({
    queryKey: ['userProfile'],
    queryFn: () => base44.entities.UserProfile.filter({ created_by: user?.email }),
    enabled: !!user?.email
  });

  const profile = profiles?.[0];

  useEffect(() => {
    if (!profile) return;

    const generatePlan = async () => {
      // Step through the animation
      for (let i = 0; i < generationSteps.length; i++) {
        setCurrentStep(i);
        await new Promise(resolve => setTimeout(resolve, generationSteps[i].duration));
      }

      // Generate the actual meal plan
      const today = new Date();
      const planDays = [];

      for (let day = 1; day <= 14; day++) {
        const date = new Date(today);
        date.setDate(date.getDate() + day - 1);
        planDays.push({
          day_number: day,
          date: date.toISOString().split('T')[0],
          profile
        });
      }

      // Generate meals using AI in batches
      const prompt = `Generate a 14-day Indian meal plan for a user with these details:
      - Region: ${profile.region?.replace('_', ' ')}
      - Diet: ${profile.diet_type?.replace('_', ' ')}
      - Allergies: ${(profile.allergies || []).join(', ') || 'None'}
      - Medical conditions: ${(profile.medical_conditions || []).join(', ') || 'None'}
      - Goals: ${(profile.goals || []).join(', ')}
      - Daily calories: ${profile.daily_calories} kcal
      - Daily protein: ${profile.daily_protein}g
      - Daily carbs: ${profile.daily_carbs}g
      - Daily fats: ${profile.daily_fats}g

      Follow ICMR/WHO guidelines. Include breakfast, mid-morning snack, lunch, evening snack, dinner.
      For each day, provide exact calories and macros for each meal.
      Use authentic Indian recipes appropriate for the region.
      Ensure variety across days and balanced nutrition.`;

      const response = await base44.integrations.Core.InvokeLLM({
        prompt,
        response_json_schema: {
          type: "object",
          properties: {
            days: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  day: { type: "number" },
                  breakfast: {
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
                  },
                  mid_morning_snack: {
                    type: "object",
                    properties: {
                      name: { type: "string" },
                      calories: { type: "number" },
                      protein: { type: "number" },
                      carbs: { type: "number" },
                      fats: { type: "number" }
                    }
                  },
                  lunch: {
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
                  },
                  evening_snack: {
                    type: "object",
                    properties: {
                      name: { type: "string" },
                      calories: { type: "number" },
                      protein: { type: "number" },
                      carbs: { type: "number" },
                      fats: { type: "number" }
                    }
                  },
                  dinner: {
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
                }
              }
            }
          }
        }
      });

      // Delete existing meal plans
      const existingPlans = await base44.entities.MealPlan.filter({ 
        user_email: user.email,
        cycle: profile.current_plan_cycle || 1
      });
      
      for (const plan of existingPlans) {
        await base44.entities.MealPlan.delete(plan.id);
      }

      // Save meal plans
      const mealPlans = response.days.map((dayData, index) => {
        const date = new Date(today);
        date.setDate(date.getDate() + index);
        
        const totalCalories = (dayData.breakfast?.calories || 0) + 
          (dayData.mid_morning_snack?.calories || 0) + 
          (dayData.lunch?.calories || 0) + 
          (dayData.evening_snack?.calories || 0) + 
          (dayData.dinner?.calories || 0);
        
        const totalProtein = (dayData.breakfast?.protein || 0) + 
          (dayData.mid_morning_snack?.protein || 0) + 
          (dayData.lunch?.protein || 0) + 
          (dayData.evening_snack?.protein || 0) + 
          (dayData.dinner?.protein || 0);

        const totalCarbs = (dayData.breakfast?.carbs || 0) + 
          (dayData.mid_morning_snack?.carbs || 0) + 
          (dayData.lunch?.carbs || 0) + 
          (dayData.evening_snack?.carbs || 0) + 
          (dayData.dinner?.carbs || 0);

        const totalFats = (dayData.breakfast?.fats || 0) + 
          (dayData.mid_morning_snack?.fats || 0) + 
          (dayData.lunch?.fats || 0) + 
          (dayData.evening_snack?.fats || 0) + 
          (dayData.dinner?.fats || 0);

        return {
          user_email: user.email,
          day_number: index + 1,
          date: date.toISOString().split('T')[0],
          cycle: profile.current_plan_cycle || 1,
          breakfast: dayData.breakfast,
          mid_morning_snack: dayData.mid_morning_snack,
          lunch: dayData.lunch,
          evening_snack: dayData.evening_snack,
          dinner: dayData.dinner,
          total_calories: totalCalories,
          total_protein: totalProtein,
          total_carbs: totalCarbs,
          total_fats: totalFats
        };
      });

      await base44.entities.MealPlan.bulkCreate(mealPlans);

      setIsGenerating(false);
      setTimeout(() => {
        window.location.href = createPageUrl('Dashboard');
      }, 1500);
    };

    generatePlan();
  }, [profile, user]);

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="max-w-lg w-full text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mb-12"
        >
          <div className="w-20 h-20 bg-black rounded-2xl flex items-center justify-center mx-auto mb-6">
            {isGenerating ? (
              <Loader2 className="w-10 h-10 text-white animate-spin" />
            ) : (
              <CheckCircle className="w-10 h-10 text-white" />
            )}
          </div>
          <h1 className="text-3xl font-light text-black mb-2">
            {isGenerating ? 'Creating Your Plan' : 'Plan Ready!'}
          </h1>
          <p className="text-gray-500">
            {isGenerating 
              ? 'Our AI is designing your personalized nutrition system'
              : 'Redirecting to your dashboard...'}
          </p>
        </motion.div>

        <div className="space-y-4">
          {generationSteps.map((step, index) => {
            const Icon = step.icon;
            const isActive = currentStep === index;
            const isComplete = currentStep > index || !isGenerating;
            
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.2 }}
                className={`flex items-center gap-4 p-4 rounded-xl transition-all duration-300
                  ${isActive ? 'bg-gray-50 border border-gray-200' : 
                    isComplete ? 'bg-gray-50/50' : 'opacity-50'}`}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all
                  ${isComplete ? 'bg-black text-white' : 
                    isActive ? 'bg-gray-200 text-gray-700' : 'bg-gray-100 text-gray-400'}`}>
                  {isComplete ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : isActive ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                <span className={`font-medium ${isComplete || isActive ? 'text-black' : 'text-gray-400'}`}>
                  {step.label}
                </span>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}