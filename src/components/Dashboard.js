'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, MessageSquare, AlertTriangle, RefreshCw, Calendar } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import CommentsFeed from './CommentsFeed';

const DATE_FILTERS = [
  { label: 'Last 24 Hours', value: '24h', days: 1 },
  { label: '7 Days', value: '7d', days: 7 },
  { label: '1 Month', value: '1m', days: 30 },
  { label: '3 Months', value: '3m', days: 90 },
  { label: '6 Months', value: '6m', days: 180 },
  { label: '1 Year', value: '1y', days: 365 },
  { label: 'All Time', value: 'all', days: null }
];

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

export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateFilter, setDateFilter] = useState('7d');

  useEffect(() => {
    fetchAnalytics();
  }, [dateFilter]);

  // Listen for data refresh events
  useEffect(() => {
    const handleDataRefresh = () => {
      fetchAnalytics();
    };

    window.addEventListener('dataRefreshed', handleDataRefresh);
    return () => window.removeEventListener('dataRefreshed', handleDataRefresh);
  }, []);

  const fetchAnalytics = async () => {
    try {
      const params = new URLSearchParams();
      if (dateFilter !== 'all') {
        const filter = DATE_FILTERS.find(f => f.value === dateFilter);
        if (filter) {
          params.append('days', filter.days.toString());
        }
      }
      
      const response = await fetch(`/api/analytics?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Check if the response contains an error
      if (data.error) {
        throw new Error(data.message || 'Failed to fetch analytics data');
      }
      
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      // Set analytics to null to show error state
      setAnalytics(null);
    } finally {
      setLoading(false);
    }
  };

  const filterChartData = (data) => {
    if (!data || dateFilter === 'all') return data;
    
    const filter = DATE_FILTERS.find(f => f.value === dateFilter);
    if (!filter) return data;
    
    // Get the most recent date from the data to use as reference point
    const allDates = data.map(item => normalizeDate(item.date)).filter(date => date !== null);
    if (allDates.length === 0) return data;
    
    const mostRecentDate = new Date(Math.max(...allDates));
    const cutoffDate = new Date(mostRecentDate);
    cutoffDate.setDate(cutoffDate.getDate() - filter.days);
    
    return data.filter(item => {
      const itemDate = normalizeDate(item.date);
      if (!itemDate) return false;
      return itemDate >= cutoffDate;
    });
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Analytics</h2>
          <p className="text-gray-600 mb-4">
            There was an error fetching analytics data from the server.
          </p>
          <button
            onClick={fetchAnalytics}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const chartData = filterChartData(analytics?.chartData || []);

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-black">Dashboard</h1>
          <div className="flex items-center gap-4">
            {/* Date Filter */}
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-600" />
              <select
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                {DATE_FILTERS.map((filter) => (
                  <option key={filter.value} value={filter.value}>
                    {filter.label}
                  </option>
                ))}
              </select>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={fetchAnalytics}
              disabled={loading}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                loading 
                  ? 'bg-gray-400 text-white cursor-not-allowed' 
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Loading...' : 'Refresh Analytics'}
            </motion.button>
          </div>
        </div>

        {/* Analytics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* Positive Mentions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-white border border-gray-200 rounded-lg p-6 shadow-md"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Positive Mentions</p>
                <p className="text-2xl font-bold text-black">{analytics?.positiveMentions || 0}</p>
                <div className="flex items-center mt-2">
                  <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                  <span className="text-sm text-green-600">
                    +{analytics?.positiveChange || 0}% 
                  </span>
                </div>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <MessageSquare className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </motion.div>

          {/* Negative Mentions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white border border-gray-200 rounded-lg p-6 shadow-md"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Negative Mentions</p>
                <p className="text-2xl font-bold text-black">{analytics?.negativeMentions || 0}</p>
                <div className="flex items-center mt-2">
                  <TrendingDown className="h-4 w-4 text-red-600 mr-1" />
                  <span className="text-sm text-red-600">
                    +{analytics?.negativeChange || 0}%
                  </span>
                </div>
              </div>
              <div className="p-3 bg-red-100 rounded-full">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </motion.div>

          {/* Neutral Mentions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="bg-white border border-gray-200 rounded-lg p-6 shadow-md"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Neutral Mentions</p>
                <p className="text-2xl font-bold text-black">{analytics?.neutralMentions || 0}</p>
                <div className="flex items-center mt-2">
                  <MessageSquare className="h-4 w-4 text-gray-600 mr-1" />
                  <span className="text-sm text-gray-600">
                    Neutral sentiment
                  </span>
                </div>
              </div>
              <div className="p-3 bg-gray-100 rounded-full">
                <MessageSquare className="h-6 w-6 text-gray-600" />
              </div>
            </div>
          </motion.div>

          {/* Reputation Score */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="bg-white border border-gray-200 rounded-lg p-6 shadow-md"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Reputation Score</p>
                <p className="text-2xl font-bold text-black">{analytics?.reputationScore || 0}</p>
                <div className="flex items-center mt-2">
                  <span className={`text-sm font-medium ${
                    analytics?.reputationTrend === 'up' ? 'text-green-600' : 
                    analytics?.reputationTrend === 'down' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {analytics?.reputationTrend === 'up' ? '↗' : 
                     analytics?.reputationTrend === 'down' ? '↘' : '→'} {analytics?.reputationTrend || 'stable'}
                  </span>
                </div>
              </div>
              <div className={`p-3 rounded-full ${
                analytics?.riskLevel === 'high' ? 'bg-red-100' :
                analytics?.riskLevel === 'medium' ? 'bg-yellow-100' : 'bg-green-100'
              }`}>
                <AlertTriangle className={`h-6 w-6 ${
                  analytics?.riskLevel === 'high' ? 'text-red-600' :
                  analytics?.riskLevel === 'medium' ? 'text-yellow-600' : 'text-green-600'
                }`} />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Chart */}
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

        {/* Comments Feed */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-8"
        >
          <CommentsFeed title="Recent Comments" limit={6} />
        </motion.div>
      </motion.div>
    </div>
  );
}
