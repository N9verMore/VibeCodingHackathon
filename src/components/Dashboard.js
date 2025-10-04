'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Calendar, AlertTriangle } from 'lucide-react';
import CommentsFeed from './CommentsFeed';
import StatsCards from './StatsCards';
import LinearGraph from './LinearGraph';
import { fetchStatistics, DATE_FILTERS } from '../lib/statistics';


export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateFilter, setDateFilter] = useState('all');
  const [dataSources, setDataSources] = useState({
    playStore: true,
    appStore: true,
    trustpilot: true
  });
  const [brandName, setBrandName] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, [dateFilter, dataSources, brandName]);

  // Listen for data refresh events
  useEffect(() => {
    const handleDataRefresh = () => {
      fetchAnalytics();
    };

    const handleDataSourceUpdate = (event) => {
      if (event.detail.dataSources) {
        setDataSources(event.detail.dataSources);
      }
      if (event.detail.brandName !== undefined) {
        setBrandName(event.detail.brandName);
      }
    };

    window.addEventListener('dataRefreshed', handleDataRefresh);
    window.addEventListener('dataSourceUpdated', handleDataSourceUpdate);
    
    return () => {
      window.removeEventListener('dataRefreshed', handleDataRefresh);
      window.removeEventListener('dataSourceUpdated', handleDataSourceUpdate);
    };
  }, []);

  const fetchAnalytics = async () => {
    try {
      const analytics = await fetchStatistics({
        platforms: dataSources,
        dateFilter: dateFilter,
        brandName: brandName
      });
      setAnalytics(analytics);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      // Set analytics to null to show error state
      setAnalytics(null);
    } finally {
      setLoading(false);
    }
  };


  const normalizeDate = (dateString) => {
    if (!dateString) return null;
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return null;
    
    return date;
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
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-center py-12 mb-8">
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
          
          {/* Comments Feed - Show even when analytics fails */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <CommentsFeed title="Recent Comments" limit={50} />
          </motion.div>
        </motion.div>
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
        <StatsCards analytics={analytics} />

        {/* Chart */}
        <LinearGraph 
          chartData={chartData} 
          dateFilter={dateFilter} 
          DATE_FILTERS={DATE_FILTERS} 
        />

        {/* Comments Feed */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-8"
        >
          <CommentsFeed title="Recent Comments" limit={50} />
        </motion.div>
      </motion.div>
    </div>
  );
}
