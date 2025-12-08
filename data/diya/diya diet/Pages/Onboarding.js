import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowLeft, ArrowRight, Loader2 } from 'lucide-react';
import { base44 } from '@/api/base44Client';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createPageUrl } from '@/utils';

import ProgressSteps from '@/components/onboarding/ProgressSteps';
import BasicInfoStep from '@/components/onboarding/BasicInfoStep';
import DietPreferencesStep from '@/components/onboarding/DietPreferencesStep';
import HealthGoalsStep from '@/components/onboarding/HealthGoalsStep';
import DigitalTwinStep from '@/components/onboarding/DigitalTwinStep';

const stepLabels = ['Basics', 'Preferences', 'Goals', 'Your Profile'];

export default function Onboarding() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    height: '',
    weight: '',
    target_weight: '',
    activity_level: 'moderate',
    region: 'north_indian',
    diet_type: 'vegetarian',
    allergies: [],
    medical_conditions: [],
    goals: [],
    notes: ''
  });

  const queryClient = useQueryClient();

  const calculateMetrics = (data) => {
    const height = data.height / 100;
    const bmi = data.weight / (height * height);
    
    let bmr;
    if (data.gender === 'male') {
      bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age + 5;
    } else {
      bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age - 161;
    }

    const activityMultipliers = {
      sedentary: 1.2,
      light: 1.375,
      moderate: 1.55,
      active: 1.725,
      very_active: 1.9
    };

    const tdee = bmr * (activityMultipliers[data.activity_level] || 1.2);
    let dailyCalories = tdee;
    if ((data.goals || []).includes('weight_loss')) {
      dailyCalories = tdee - 500;
    } else if ((data.goals || []).includes('weight_gain') || (data.goals || []).includes('muscle_building')) {
      dailyCalories = tdee + 300;
    }

    return {
      bmi: Math.round(bmi * 10) / 10,
      bmr: Math.round(bmr),
      tdee: Math.round(tdee),
      daily_calories: Math.round(dailyCalories),
      daily_protein: Math.round(data.weight * 1.6),
      daily_carbs: Math.round((dailyCalories * 0.5) / 4),
      daily_fats: Math.round((dailyCalories * 0.25) / 9)
    };
  };

  const createProfileMutation = useMutation({
    mutationFn: async (data) => {
      const metrics = calculateMetrics(data);
      const today = new Date().toISOString().split('T')[0];
      
      const profileData = {
        ...data,
        ...metrics,
        onboarding_complete: true,
        plan_start_date: today,
        current_plan_cycle: 1
      };

      const existingProfiles = await base44.entities.UserProfile.filter({ created_by: (await base44.auth.me()).email });
      if (existingProfiles.length > 0) {
        await base44.entities.UserProfile.update(existingProfiles[0].id, profileData);
      } else {
        await base44.entities.UserProfile.create(profileData);
      }

      return profileData;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userProfile'] });
      window.location.href = createPageUrl('GeneratePlan');
    }
  });

  const nextStep = () => {
    if (step < 4) setStep(step + 1);
    else createProfileMutation.mutate(formData);
  };

  const prevStep = () => {
    if (step > 1) setStep(step - 1);
  };

  const isStepValid = () => {
    switch (step) {
      case 1:
        return formData.age && formData.gender && formData.height && formData.weight && formData.activity_level;
      case 2:
        return formData.region && formData.diet_type;
      case 3:
        return (formData.goals || []).length > 0;
      case 4:
        return true;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-4 py-8 md:py-16">
        {/* Logo */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-2xl font-bold tracking-tight text-black">nutriAI</h1>
          <p className="text-gray-500 text-sm mt-1">Your personal nutrition system</p>
        </motion.div>

        {/* Progress Steps */}
        <ProgressSteps currentStep={step} totalSteps={4} stepLabels={stepLabels} />

        {/* Form Content */}
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 md:p-10">
          <AnimatePresence mode="wait">
            {step === 1 && (
              <BasicInfoStep 
                key="basic"
                data={formData} 
                onChange={setFormData} 
              />
            )}
            {step === 2 && (
              <DietPreferencesStep 
                key="diet"
                data={formData} 
                onChange={setFormData} 
              />
            )}
            {step === 3 && (
              <HealthGoalsStep 
                key="goals"
                data={formData} 
                onChange={setFormData} 
              />
            )}
            {step === 4 && (
              <DigitalTwinStep 
                key="twin"
                data={formData} 
              />
            )}
          </AnimatePresence>

          {/* Navigation */}
          <div className="flex items-center justify-between mt-10 pt-6 border-t border-gray-100">
            <Button
              variant="ghost"
              onClick={prevStep}
              disabled={step === 1}
              className="text-gray-600 hover:text-black"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>

            <Button
              onClick={nextStep}
              disabled={!isStepValid() || createProfileMutation.isPending}
              className="bg-black hover:bg-gray-800 text-white px-8 h-12"
            >
              {createProfileMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : step === 4 ? (
                'Generate My Plan'
              ) : (
                <>
                  Continue
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}