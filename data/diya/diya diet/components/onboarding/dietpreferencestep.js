import React from 'react';
import { motion } from 'framer-motion';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';

const regions = [
  { id: 'north_indian', label: 'North Indian', desc: 'Roti, Dal, Paneer dishes' },
  { id: 'south_indian', label: 'South Indian', desc: 'Rice, Sambar, Dosa' },
  { id: 'east_indian', label: 'East Indian', desc: 'Fish, Rice, Sweets' },
  { id: 'west_indian', label: 'West Indian', desc: 'Dhokla, Thepla, Curry' },
  { id: 'mixed', label: 'Mixed/Pan Indian', desc: 'Variety from all regions' },
];

const dietTypes = [
  { id: 'vegetarian', label: 'Vegetarian', icon: '🥬' },
  { id: 'non_vegetarian', label: 'Non-Vegetarian', icon: '🍗' },
  { id: 'eggetarian', label: 'Eggetarian', icon: '🥚' },
  { id: 'vegan', label: 'Vegan', icon: '🌱' },
];

const commonAllergies = [
  'Dairy', 'Gluten', 'Nuts', 'Peanuts', 'Soy', 'Eggs', 'Shellfish', 'Fish', 'Sesame', 'Mustard'
];

export default function DietPreferencesStep({ data, onChange }) {
  const toggleAllergy = (allergy) => {
    const current = data.allergies || [];
    const updated = current.includes(allergy)
      ? current.filter(a => a !== allergy)
      : [...current, allergy];
    onChange({ ...data, allergies: updated });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-10"
    >
      <div className="text-center mb-10">
        <h2 className="text-3xl font-light tracking-tight text-black mb-2">Your food preferences</h2>
        <p className="text-gray-500">Help us curate meals you'll love</p>
      </div>

      {/* Region Selection */}
      <div className="space-y-4">
        <Label className="text-sm font-medium text-gray-700">Preferred Cuisine Region</Label>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {regions.map((region) => (
            <motion.button
              key={region.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onChange({ ...data, region: region.id })}
              className={`p-4 rounded-xl border-2 text-left transition-all duration-200
                ${data.region === region.id 
                  ? 'border-black bg-black text-white' 
                  : 'border-gray-200 hover:border-gray-400 bg-white'}`}
            >
              <div className="font-medium">{region.label}</div>
              <div className={`text-sm ${data.region === region.id ? 'text-gray-300' : 'text-gray-500'}`}>
                {region.desc}
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Diet Type */}
      <div className="space-y-4">
        <Label className="text-sm font-medium text-gray-700">Diet Type</Label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {dietTypes.map((diet) => (
            <motion.button
              key={diet.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onChange({ ...data, diet_type: diet.id })}
              className={`p-4 rounded-xl border-2 text-center transition-all duration-200
                ${data.diet_type === diet.id 
                  ? 'border-black bg-black text-white' 
                  : 'border-gray-200 hover:border-gray-400 bg-white'}`}
            >
              <div className="text-2xl mb-2">{diet.icon}</div>
              <div className="font-medium text-sm">{diet.label}</div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Allergies */}
      <div className="space-y-4">
        <Label className="text-sm font-medium text-gray-700">Food Allergies</Label>
        <div className="flex flex-wrap gap-2">
          {commonAllergies.map((allergy) => (
            <motion.button
              key={allergy}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => toggleAllergy(allergy)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
                ${(data.allergies || []).includes(allergy)
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              {allergy}
            </motion.button>
          ))}
        </div>
      </div>
    </motion.div>
  );
}