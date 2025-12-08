import React, { useEffect } from 'react';
import { base44 } from '@/api/base44Client';
import { useQuery } from '@tanstack/react-query';
import { createPageUrl } from '@/utils';
import { Loader2 } from 'lucide-react';

export default function Home() {
  const { data: user, isLoading: loadingUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => base44.auth.me()
  });

  const { data: profiles, isLoading: loadingProfile } = useQuery({
    queryKey: ['userProfile'],
    queryFn: () => base44.entities.UserProfile.filter({ created_by: user?.email }),
    enabled: !!user?.email
  });

  useEffect(() => {
    if (!loadingUser && !loadingProfile && user) {
      const profile = profiles?.[0];
      if (profile?.onboarding_complete) {
        window.location.href = createPageUrl('Dashboard');
      } else {
        window.location.href = createPageUrl('Onboarding');
      }
    }
  }, [user, profiles, loadingUser, loadingProfile]);

  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-black rounded-2xl flex items-center justify-center mx-auto mb-6">
          <Loader2 className="w-8 h-8 text-white animate-spin" />
        </div>
        <h1 className="text-2xl font-light text-black mb-2">nutriAI</h1>
        <p className="text-gray-500">Loading your nutrition system...</p>
      </div>
    </div>
  );
}