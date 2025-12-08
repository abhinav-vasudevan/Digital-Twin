import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { base44 } from '@/api/base44Client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format, differenceInDays } from 'date-fns';
import { Link } from 'react-router-dom';
import { createPageUrl } from '@/utils';
import { 
  ArrowLeft, User, Scale, Target, Flame, Activity,
  RefreshCw, LogOut, Loader2, TrendingDown, TrendingUp, Calendar
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

export default function Profile() {
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

  const { data: logs } = useQuery({
    queryKey: ['allLogs'],
    queryFn: () => base44.entities.DailyLog.filter({ user_email: user?.email }, '-date'),
    enabled: !!user?.email
  });

  const profile = profiles?.[0];
  const weightLogs = logs?.filter(l => l.weight).sort((a, b) => new Date(b.date) - new Date(a.date)) || [];
  const latestWeight = weightLogs[0]?.weight || profile?.weight;

  const cycleDay = profile?.plan_start_date 
    ? differenceInDays(new Date(), new Date(profile.plan_start_date)) + 1
    : 1;
  const cycleProgress = Math.min((cycleDay / 14) * 100, 100);
  const daysRemaining = Math.max(14 - cycleDay, 0);

  const regeneratePlanMutation = useMutation({
    mutationFn: async () => {
      if (profile) {
        await base44.entities.UserProfile.update(profile.id, {
          current_plan_cycle: (profile.current_plan_cycle || 1) + 1,
          plan_start_date: new Date().toISOString().split('T')[0]
        });
      }
      window.location.href = createPageUrl('GeneratePlan');
    }
  });

  const handleLogout = () => {
    base44.auth.logout('/');
  };

  if (!profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin" />
      </div>
    );
  }

  const bmiStatus = profile.bmi < 18.5 ? 'Underweight' 
    : profile.bmi < 25 ? 'Normal' 
    : profile.bmi < 30 ? 'Overweight' : 'Obese';

  const weightDiff = latestWeight - profile.target_weight;
  const progressToGoal = profile.weight !== profile.target_weight
    ? Math.abs((profile.weight - latestWeight) / (profile.weight - profile.target_weight)) * 100
    : 100;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link to={createPageUrl('Dashboard')}>
              <Button variant="ghost" size="icon">
                <ArrowLeft className="w-5 h-5" />
              </Button>
            </Link>
            <h1 className="text-xl font-semibold">Profile</h1>
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-4">
        {/* User Info */}
        <Card className="p-6 bg-white border-0 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">{user?.full_name || 'User'}</h2>
              <p className="text-gray-500 text-sm">{user?.email}</p>
              <div className="flex gap-2 mt-2">
                <Badge variant="secondary">{profile.diet_type?.replace('_', ' ')}</Badge>
                <Badge variant="secondary">{profile.region?.replace('_', ' ')}</Badge>
              </div>
            </div>
          </div>
        </Card>

        {/* Cycle Progress */}
        <Card className="p-6 bg-black text-white border-0 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              <span className="font-medium">Cycle {profile.current_plan_cycle || 1}</span>
            </div>
            <span className="text-sm text-gray-300">{daysRemaining} days remaining</span>
          </div>
          <Progress value={cycleProgress} className="h-2 bg-white/20" />
          <div className="flex justify-between mt-2 text-sm text-gray-300">
            <span>Day {cycleDay}</span>
            <span>Day 14</span>
          </div>
        </Card>

        {/* Body Stats */}
        <div className="grid grid-cols-2 gap-3">
          <Card className="p-4 bg-white border-0 shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 mb-2">
              <Scale className="w-4 h-4" />
              <span className="text-sm">Current</span>
            </div>
            <div className="text-2xl font-bold">{latestWeight} kg</div>
            {weightDiff !== 0 && (
              <div className={`flex items-center gap-1 text-sm mt-1 ${
                weightDiff > 0 ? 'text-blue-600' : 'text-green-600'
              }`}>
                {weightDiff > 0 ? (
                  <>
                    <TrendingDown className="w-4 h-4" />
                    {Math.abs(weightDiff).toFixed(1)} kg to go
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-4 h-4" />
                    {Math.abs(weightDiff).toFixed(1)} kg gained
                  </>
                )}
              </div>
            )}
          </Card>

          <Card className="p-4 bg-white border-0 shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 mb-2">
              <Target className="w-4 h-4" />
              <span className="text-sm">Target</span>
            </div>
            <div className="text-2xl font-bold">{profile.target_weight} kg</div>
            <Progress value={Math.min(progressToGoal, 100)} className="h-1 mt-2" />
          </Card>
        </div>

        {/* Metabolic Profile */}
        <Card className="p-6 bg-white border-0 shadow-sm">
          <h3 className="font-semibold mb-4">Metabolic Profile</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-500">BMI</div>
              <div className="font-bold text-lg">{profile.bmi}</div>
              <div className="text-xs text-gray-400">{bmiStatus}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">BMR</div>
              <div className="font-bold text-lg">{profile.bmr} kcal</div>
              <div className="text-xs text-gray-400">at rest</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">TDEE</div>
              <div className="font-bold text-lg">{profile.tdee} kcal</div>
              <div className="text-xs text-gray-400">total daily burn</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Daily Target</div>
              <div className="font-bold text-lg">{profile.daily_calories} kcal</div>
              <div className="text-xs text-gray-400">for your goals</div>
            </div>
          </div>
        </Card>

        {/* Daily Targets */}
        <Card className="p-6 bg-white border-0 shadow-sm">
          <h3 className="font-semibold mb-4">Daily Macro Targets</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Protein</span>
                <span className="font-bold">{profile.daily_protein}g</span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 w-full rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Carbs</span>
                <span className="font-bold">{profile.daily_carbs}g</span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-amber-500 w-full rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Fats</span>
                <span className="font-bold">{profile.daily_fats}g</span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-green-500 w-full rounded-full" />
              </div>
            </div>
          </div>
        </Card>

        {/* Goals & Conditions */}
        <Card className="p-6 bg-white border-0 shadow-sm">
          <h3 className="font-semibold mb-4">Health Profile</h3>
          
          <div className="mb-4">
            <div className="text-sm text-gray-500 mb-2">Goals</div>
            <div className="flex flex-wrap gap-2">
              {(profile.goals || []).map(goal => (
                <Badge key={goal} variant="secondary" className="bg-black text-white">
                  {goal.replace(/_/g, ' ')}
                </Badge>
              ))}
            </div>
          </div>

          {(profile.medical_conditions || []).length > 0 && (
            <div className="mb-4">
              <div className="text-sm text-gray-500 mb-2">Medical Conditions</div>
              <div className="flex flex-wrap gap-2">
                {profile.medical_conditions.map(condition => (
                  <Badge key={condition} variant="outline">
                    {condition}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {(profile.allergies || []).length > 0 && (
            <div>
              <div className="text-sm text-gray-500 mb-2">Allergies</div>
              <div className="flex flex-wrap gap-2">
                {profile.allergies.map(allergy => (
                  <Badge key={allergy} variant="destructive" className="bg-red-100 text-red-700">
                    {allergy}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </Card>

        {/* Actions */}
        <div className="space-y-3 pt-4">
          <Button
            variant="outline"
            className="w-full h-12"
            onClick={() => regeneratePlanMutation.mutate()}
            disabled={regeneratePlanMutation.isPending}
          >
            {regeneratePlanMutation.isPending ? (
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="w-5 h-5 mr-2" />
            )}
            Generate New 14-Day Plan
          </Button>

          <Link to={createPageUrl('Onboarding')}>
            <Button variant="outline" className="w-full h-12">
              Update Profile
            </Button>
          </Link>

          <Button
            variant="ghost"
            className="w-full h-12 text-red-600 hover:text-red-700 hover:bg-red-50"
            onClick={handleLogout}
          >
            <LogOut className="w-5 h-5 mr-2" />
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
}