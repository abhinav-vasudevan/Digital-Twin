import React from 'react';
import { Link } from 'react-router-dom';
import { createPageUrl } from '@/utils';
import { Home, Calendar, MessageSquare, User } from 'lucide-react';

const navItems = [
  { icon: Home, label: 'Home', page: 'Dashboard' },
  { icon: Calendar, label: 'Plan', page: 'MealPlan' },
  { icon: MessageSquare, label: 'Feedback', page: 'DailyFeedback' },
  { icon: User, label: 'Profile', page: 'Profile' }
];

export default function Layout({ children, currentPageName }) {
  const hideNav = ['Onboarding', 'GeneratePlan'].includes(currentPageName);

  return (
    <div className="min-h-screen bg-gray-50">
      <style>{`
        :root {
          --background: 0 0% 100%;
          --foreground: 0 0% 3.9%;
          --card: 0 0% 100%;
          --card-foreground: 0 0% 3.9%;
          --popover: 0 0% 100%;
          --popover-foreground: 0 0% 3.9%;
          --primary: 0 0% 9%;
          --primary-foreground: 0 0% 98%;
          --secondary: 0 0% 96.1%;
          --secondary-foreground: 0 0% 9%;
          --muted: 0 0% 96.1%;
          --muted-foreground: 0 0% 45.1%;
          --accent: 0 0% 96.1%;
          --accent-foreground: 0 0% 9%;
          --destructive: 0 84.2% 60.2%;
          --destructive-foreground: 0 0% 98%;
          --border: 0 0% 89.8%;
          --input: 0 0% 89.8%;
          --ring: 0 0% 3.9%;
          --radius: 0.75rem;
        }
        
        * {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        body {
          background-color: #f9fafb;
        }
      `}</style>
      
      <main className={hideNav ? '' : 'pb-20'}>
        {children}
      </main>

      {/* Bottom Navigation */}
      {!hideNav && (
        <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 z-50">
          <div className="max-w-2xl mx-auto">
            <div className="flex items-center justify-around py-2">
              {navItems.map(item => {
                const Icon = item.icon;
                const isActive = currentPageName === item.page;
                return (
                  <Link
                    key={item.page}
                    to={createPageUrl(item.page)}
                    className={`flex flex-col items-center py-2 px-4 transition-colors ${
                      isActive ? 'text-black' : 'text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    <Icon className={`w-5 h-5 ${isActive ? 'stroke-[2.5]' : ''}`} />
                    <span className="text-xs mt-1 font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
          {/* Safe area for mobile */}
          <div className="h-safe-area-inset-bottom bg-white" />
        </nav>
      )}
    </div>
  );
}