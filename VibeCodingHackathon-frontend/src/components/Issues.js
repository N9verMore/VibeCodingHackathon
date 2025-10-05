'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bug, AlertTriangle, Clock, TrendingUp, Filter, Search, BarChart3 } from 'lucide-react';
import { fetchStatistics } from '../lib/statistics';

export default function Issues() {
  const [issues, setIssues] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [dataSources, setDataSources] = useState({
    playStore: true,
    appStore: true,
    threads: false,
    trustpilot: false,
    news: true
  });

  useEffect(() => {
    fetchIssues();
  }, [dataSources]);

  // Listen for data source updates from Layout
  useEffect(() => {
    const handleDataSourceUpdate = (event) => {
      setDataSources(event.detail);
    };

    window.addEventListener('dataSourceUpdated', handleDataSourceUpdate);
    
    return () => {
      window.removeEventListener('dataSourceUpdated', handleDataSourceUpdate);
    };
  }, []);

  const fetchIssues = async () => {
    try {
      const analytics = await fetchStatistics({
        platforms: dataSources
      });
      
      // Transform API data to match our frontend structure
      const transformedIssues = {
        categories: analytics.topCategories?.map((category, index) => ({
          id: category.category,
          name: formatCategoryName(category.category),
          count: category.count,
          color: getCategoryColor(index),
        })) || [],
        recentIssues: [] // You can fetch recent issues from a separate endpoint if available
      };
      
      setIssues(transformedIssues);
    } catch (error) {
      console.error('Failed to fetch issues:', error);
      // If API fails, show empty state instead of mock data
      setIssues({ categories: [], recentIssues: [] });
    } finally {
      setLoading(false);
    }
  };

  // Helper function to format category names
  const formatCategoryName = (category) => {
    return category
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Helper function to assign colors to categories
  const getCategoryColor = (index) => {
    const colors = ['red', 'orange', 'yellow', 'purple', 'blue', 'green'];
    return colors[index % colors.length];
  };

  const getColorClasses = (color) => {
    const colors = {
      red: 'bg-red-100 text-red-800 border-red-200',
      orange: 'bg-orange-100 text-orange-800 border-orange-200',
      yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      purple: 'bg-purple-100 text-purple-800 border-purple-200',
      blue: 'bg-blue-100 text-blue-800 border-blue-200',
      green: 'bg-green-100 text-green-800 border-green-200'
    };
    return colors[color] || colors.blue;
  };

  const getSeverityColor = (severity) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    };
    return colors[severity] || colors.medium;
  };

  const filteredIssues = issues?.recentIssues.filter(issue => {
    const matchesCategory = selectedCategory === 'all' || issue.category === selectedCategory;
    const matchesSearch = issue.title.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  }) || [];

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
          <div className="h-96 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-black">Posts & Feedback</h1>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search posts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white text-sm w-64"
              />
            </div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white text-sm"
            >
              <option value="all">All Categories</option>
              {issues?.categories.map(category => (
                <option key={category.id} value={category.id}>{category.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Category Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {issues?.categories.map((category, index) => (
            <motion.div
              key={category.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white border border-gray-200 rounded-lg p-6 shadow-md cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => setSelectedCategory(category.id)}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-full ${getColorClasses(category.color).split(' ')[0]}`}>
                  <Bug className={`h-6 w-6 ${getColorClasses(category.color).split(' ')[1]}`} />
                </div>
                <div className="flex items-center gap-1 text-sm">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span className="text-green-600 font-medium">{category.trend}</span>
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{category.name}</h3>
              <p className="text-3xl font-bold text-gray-900 mb-2">{category.count}</p>
              <p className="text-sm text-gray-500">Total posts</p>
            </motion.div>
          ))}
        </div>

        {/* Recent Posts Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="bg-white border border-gray-200 rounded-lg shadow-md"
        >
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Recent Posts</h2>
            <p className="text-sm text-gray-500 mt-1">Latest feedback and posts across all sources</p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredIssues.map((issue) => (
                  <tr key={issue.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{issue.title}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getColorClasses(issues.categories.find(c => c.id === issue.category)?.color)}`}>
                        {issues.categories.find(c => c.id === issue.category)?.name}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(issue.severity)}`}>
                        {issue.severity.charAt(0).toUpperCase() + issue.severity.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {issue.source}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(issue.date).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
