import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

export default function ProgressSteps({ currentStep, totalSteps, stepLabels }) {
  return (
    <div className="flex items-center justify-center w-full max-w-2xl mx-auto mb-12">
      {Array.from({ length: totalSteps }, (_, i) => (
        <React.Fragment key={i}>
          <div className="flex flex-col items-center">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ 
                scale: currentStep === i + 1 ? 1.1 : 1,
                backgroundColor: i + 1 <= currentStep ? '#000' : '#e5e7eb'
              }}
              className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300
                ${i + 1 < currentStep ? 'bg-black text-white' : 
                  i + 1 === currentStep ? 'bg-black text-white ring-4 ring-gray-200' : 
                  'bg-gray-200 text-gray-500'}`}
            >
              {i + 1 < currentStep ? (
                <Check className="w-5 h-5" />
              ) : (
                i + 1
              )}
            </motion.div>
            <span className={`mt-2 text-xs font-medium hidden md:block ${
              i + 1 <= currentStep ? 'text-black' : 'text-gray-400'
            }`}>
              {stepLabels[i]}
            </span>
          </div>
          {i < totalSteps - 1 && (
            <div className="flex-1 h-0.5 mx-2 md:mx-4">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: i + 1 < currentStep ? '100%' : '0%' }}
                transition={{ duration: 0.4 }}
                className="h-full bg-black"
                style={{ 
                  width: i + 1 < currentStep ? '100%' : '0%',
                  backgroundColor: i + 1 < currentStep ? '#000' : '#e5e7eb'
                }}
              />
              <div className="h-full bg-gray-200 -mt-0.5" />
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}