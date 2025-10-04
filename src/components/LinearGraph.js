'use client';

import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const normalizeDate = (dateString) => {
  if (!dateString) return null;
  
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return null;
  
  return date;
};

const formatDateForDisplay = (dateString) => {
  const date = normalizeDate(dateString);
  if (!date) return 'Invalid Date';
  
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

export default function LinearGraph({ chartData, dateFilter, DATE_FILTERS }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="bg-white border border-gray-200 rounded-lg p-6 shadow-md"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-black">Mentions Over Time</h2>
        <div className="text-right">
          <span className="text-sm text-gray-600">
            {DATE_FILTERS.find(f => f.value === dateFilter)?.label}
          </span>
          {chartData.length > 0 && (
            <div className="text-xs text-gray-500 mt-1">
              {formatDateForDisplay(chartData[chartData.length - 1]?.date)} - {formatDateForDisplay(chartData[0]?.date)}
            </div>
          )}
        </div>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="positiveGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="negativeGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="neutralGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6b7280" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#6b7280" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="date" 
              stroke="#666"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => {
                const date = normalizeDate(value);
                if (!date) return '';
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
              }}
            />
            <YAxis 
              stroke="#666"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              width={40}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
              labelFormatter={(value) => {
                const date = normalizeDate(value);
                if (!date) return value;
                return formatDateForDisplay(value);
              }}
            />
            <Area
              type="monotone"
              dataKey="positive"
              stroke="#10b981"
              strokeWidth={2}
              fill="url(#positiveGradient)"
              name="Positive Mentions"
            />
            <Area
              type="monotone"
              dataKey="negative"
              stroke="#ef4444"
              strokeWidth={2}
              fill="url(#negativeGradient)"
              name="Negative Mentions"
            />
            <Area
              type="monotone"
              dataKey="neutral"
              stroke="#6b7280"
              strokeWidth={2}
              fill="url(#neutralGradient)"
              name="Neutral Mentions"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
