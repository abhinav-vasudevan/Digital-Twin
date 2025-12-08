import React from 'react';
import { motion } from 'framer-motion';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function BasicInfoStep({ data, onChange }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-8"
    >
      <div className="text-center mb-10">
        <h2 className="text-3xl font-light tracking-tight text-black mb-2">Tell us about yourself</h2>
        <p className="text-gray-500">Basic information to personalize your nutrition plan</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label className="text-sm font-medium text-gray-700">Age</Label>
          <Input
            type="number"
            placeholder="Enter your age"
            value={data.age || ''}
            onChange={(e) => onChange({ ...data, age: parseInt(e.target.value) || '' })}
            className="h-12 bg-gray-50 border-gray-200 focus:border-black focus:ring-black transition-all"
          />
        </div>

        <div className="space-y-2">
          <Label className="text-sm font-medium text-gray-700">Gender</Label>
          <Select value={data.gender || ''} onValueChange={(v) => onChange({ ...data, gender: v })}>
            <SelectTrigger className="h-12 bg-gray-50 border-gray-200 focus:ring-black">
              <SelectValue placeholder="Select gender" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="male">Male</SelectItem>
              <SelectItem value="female">Female</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label className="text-sm font-medium text-gray-700">Height (cm)</Label>
          <Input
            type="number"
            placeholder="e.g., 170"
            value={data.height || ''}
            onChange={(e) => onChange({ ...data, height: parseFloat(e.target.value) || '' })}
            className="h-12 bg-gray-50 border-gray-200 focus:border-black focus:ring-black transition-all"
          />
        </div>

        <div className="space-y-2">
          <Label className="text-sm font-medium text-gray-700">Weight (kg)</Label>
          <Input
            type="number"
            placeholder="e.g., 65"
            value={data.weight || ''}
            onChange={(e) => onChange({ ...data, weight: parseFloat(e.target.value) || '' })}
            className="h-12 bg-gray-50 border-gray-200 focus:border-black focus:ring-black transition-all"
          />
        </div>

        <div className="space-y-2">
          <Label className="text-sm font-medium text-gray-700">Target Weight (kg)</Label>
          <Input
            type="number"
            placeholder="Your goal weight"
            value={data.target_weight || ''}
            onChange={(e) => onChange({ ...data, target_weight: parseFloat(e.target.value) || '' })}
            className="h-12 bg-gray-50 border-gray-200 focus:border-black focus:ring-black transition-all"
          />
        </div>

        <div className="space-y-2">
          <Label className="text-sm font-medium text-gray-700">Activity Level</Label>
          <Select value={data.activity_level || ''} onValueChange={(v) => onChange({ ...data, activity_level: v })}>
            <SelectTrigger className="h-12 bg-gray-50 border-gray-200 focus:ring-black">
              <SelectValue placeholder="Select activity level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="sedentary">Sedentary (desk job)</SelectItem>
              <SelectItem value="light">Light (1-2 days/week)</SelectItem>
              <SelectItem value="moderate">Moderate (3-5 days/week)</SelectItem>
              <SelectItem value="active">Active (6-7 days/week)</SelectItem>
              <SelectItem value="very_active">Very Active (intense)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </motion.div>
  );
}