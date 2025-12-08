import React from 'react';
import { motion } from 'framer-motion';
import { format, addDays, isSameDay, isAfter, isBefore } from 'date-fns';

export default function WeekProgress({ startDate, currentDay, logs }) {
  const today = new Date();
  const days = [];

  for (let i = 0; i < 14; i++) {
    const date = addDays(new Date(startDate), i);
    const dayLog = logs?.find(l => l.date === format(date, 'yyyy-MM-dd'));
    const isToday = isSameDay(date, today);
    const isPast = isBefore(date, today) && !isToday;
    const isFuture = isAfter(date, today);
    
    let status = 'upcoming';
    if (isToday) status = 'today';
    else if (isPast && dayLog) status = 'completed';
    else if (isPast && !dayLog) status = 'missed';

    days.push({
      date,
      dayNumber: i + 1,
      status,
      log: dayLog
    });
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-black text-white';
      case 'today': return 'bg-white border-2 border-black text-black';
      case 'missed': return 'bg-red-100 text-red-600';
      default: return 'bg-gray-100 text-gray-400';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">14-Day Cycle Progress</h3>
        <span className="text-sm text-gray-500">Day {currentDay}/14</span>
      </div>
      
      <div className="grid grid-cols-7 gap-2">
        {days.slice(0, 7).map((day, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            className="text-center"
          >
            <div className="text-[10px] text-gray-400 mb-1">
              {format(day.date, 'EEE')}
            </div>
            <div className={`w-8 h-8 mx-auto rounded-full flex items-center justify-center text-xs font-medium
              ${getStatusColor(day.status)}`}>
              {day.dayNumber}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-2">
        {days.slice(7, 14).map((day, i) => (
          <motion.div
            key={i + 7}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: (i + 7) * 0.05 }}
            className="text-center"
          >
            <div className="text-[10px] text-gray-400 mb-1">
              {format(day.date, 'EEE')}
            </div>
            <div className={`w-8 h-8 mx-auto rounded-full flex items-center justify-center text-xs font-medium
              ${getStatusColor(day.status)}`}>
              {day.dayNumber}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="flex items-center justify-center gap-4 text-xs text-gray-500 pt-2">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-black" /> Completed
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full border-2 border-black" /> Today
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-gray-100" /> Upcoming
        </span>
      </div>
    </div>
  );
}