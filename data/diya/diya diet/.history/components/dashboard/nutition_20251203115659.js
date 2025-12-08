import React from 'react';
import { motion } from 'framer-motion';

export default function NutritionRing({ 
  consumed, 
  target, 
  label, 
  unit = 'g',
  color = 'black',
  size = 'default'
}) {
  const percentage = Math.min((consumed / target) * 100, 100);
  const strokeWidth = size === 'large' ? 8 : 6;
  const radius = size === 'large' ? 45 : 35;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const colorClasses = {
    black: 'stroke-black',
    blue: 'stroke-blue-500',
    amber: 'stroke-amber-500',
    green: 'stroke-green-500',
    purple: 'stroke-purple-500'
  };

  return (
    <div className="flex flex-col items-center">
      <div className={`relative ${size === 'large' ? 'w-24 h-24' : 'w-20 h-20'}`}>
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            fill="none"
            className="stroke-gray-100"
            strokeWidth={strokeWidth}
          />
          <motion.circle
            cx="50%"
            cy="50%"
            r={radius}
            fill="none"
            className={colorClasses[color]}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1, ease: "easeOut" }}
            style={{
              strokeDasharray: circumference,
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-bold ${size === 'large' ? 'text-lg' : 'text-sm'}`}>
            {Math.round(percentage)}%
          </span>
        </div>
      </div>
      <div className="text-center mt-2">
        <div className="text-xs text-gray-500">{label}</div>
        <div className="text-xs font-medium">
          {consumed}/{target}{unit}
        </div>
      </div>
    </div>
  );
}