'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, FileText, Home, Smartphone, Apple, MessageSquare, Bug, Star, Bot, Brain, Newspaper, Tag, Instagram } from 'lucide-react';
import Header from './Header';
import Issues from './Issues';
import AIChat from './AIChat';
import AIInsights from './AIInsights';
import { fetchStatistics } from '../lib/statistics';

export default function Layout({ children }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dataSources, setDataSources] = useState({
    playStore: true,
    appStore: true,
    trustpilot: true,
    news: true,
    instagram: true
  });
  const [isLoading, setIsLoading] = useState(false);
  const [brandName, setBrandName] = useState('flo');
  const [analytics, setAnalytics] = useState(null);
  
  // Track initial values to detect changes
  const [initialDataSources, setInitialDataSources] = useState({
    playStore: true,
    appStore: true,
    trustpilot: true,
    news: true,
    instagram: true
  });
  const [initialBrandName, setInitialBrandName] = useState('flo');

  // Fetch initial analytics data on mount
  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  // Check if there are any changes from initial state
  const hasChanges = () => {
    const dataSourcesChanged = JSON.stringify(dataSources) !== JSON.stringify(initialDataSources);
    const brandNameChanged = brandName !== initialBrandName;
    return dataSourcesChanged || brandNameChanged;
  };

  const fetchAnalyticsData = async () => {
    try {
      const analyticsData = await fetchStatistics({
        platforms: dataSources,
        brandName: brandName
      });
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Failed to fetch analytics for tags:', error);
      setAnalytics(null);
    }
  };

  const formatCategoryName = (category) => {
    if (!category) return 'Uncategorized';
    return category.charAt(0).toUpperCase() + category.slice(1);
  };

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'posts', label: 'Posts', icon: MessageSquare },
    { id: 'chat', label: 'AI Chat', icon: Bot },
    { id: 'insights', label: 'AI Insights', icon: Brain },
    { id: 'resources', label: 'Resources', icon: FileText },
  ];

  const dataSourceOptions = [
    { id: 'playStore', label: 'Play Store', icon: Smartphone },
    { id: 'appStore', label: 'App Store', icon: Apple },
    { id: 'trustpilot', label: 'Trustpilot', icon: Star },
    { id: 'news', label: 'News', icon: Newspaper },
    { id: 'instagram', label: 'Instagram', icon: Instagram },
  ];

  const handleDataSourceChange = (sourceId) => {
    setDataSources(prev => {
      const newDataSources = {
        ...prev,
        [sourceId]: !prev[sourceId]
      };
      
      return newDataSources;
    });
  };

  const handleBrandNameChange = (value) => {
    setBrandName(value);
  };

  const handleApplyChanges = async () => {
    setIsLoading(true);
    try {
      console.log('Applied data sources:', dataSources);
      
      // Update initial values to current values
      setInitialDataSources({ ...dataSources });
      setInitialBrandName(brandName);
      
      // Dispatch event to update dashboard with new settings
      window.dispatchEvent(new CustomEvent('dataSourceUpdated', {
        detail: { dataSources, brandName }
      }));
      
      // Fetch analytics data with new settings
      await fetchAnalyticsData();
      
      // Trigger data refresh event for dashboard and comments
      window.dispatchEvent(new CustomEvent('dataRefreshed'));
      
      console.log('Settings applied successfully');
      
    } catch (error) {
      console.error('Error applying changes:', error);
      alert('Error applying changes: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Navigation Panel - Black - Full Height */}
      <motion.div 
        initial={{ x: -250 }}
        animate={{ x: 0 }}
        className="w-64 bg-black text-white flex flex-col"
      >
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold text-white">Reputation Guardian</h1>
        </div>
        
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      activeTab === item.id
                        ? 'bg-green-100 text-green-800 border border-green-200'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    <Icon size={20} />
                    {item.label}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
      </motion.div>

      {/* Main Content Area with Header */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />
        
        {/* Main Content - Light Blue Background */}
        <div className="flex-1 flex overflow-hidden">
          <main className="flex-1 overflow-auto bg-blue-50">
            {activeTab === 'dashboard' && children}
            {activeTab === 'posts' && <Issues />}
            {activeTab === 'chat' && (
              <div className="h-full">
                <AIChat />
              </div>
            )}
            {activeTab === 'insights' && (
              <div className="p-8">
                <h1 className="text-3xl font-bold text-black mb-8">AI Insights</h1>
                <AIInsights />
              </div>
            )}
            {activeTab === 'resources' && (
              <div className="p-8">
                <h1 className="text-3xl font-bold text-black mb-8">Resources</h1>
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-md">
                  <p className="text-gray-500">Resources content coming soon...</p>
                </div>
              </div>
            )}
          </main>
          
          {/* Right Panel - Data Sources */}
          <motion.div 
            initial={{ x: 300 }}
            animate={{ x: 0 }}
            className="w-80 bg-gray-50 border-l border-gray-200"
          >
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Data Sources</h2>
              
              {/* Brand Name Input */}
              <div className="mb-6">
                <label htmlFor="brandName" className="block text-sm font-medium text-gray-700 mb-2">
                  Brand Name (Keyword)
                </label>
                <input
                  id="brandName"
                  type="text"
                  value={brandName}
                  onChange={(e) => handleBrandNameChange(e.target.value)}
                  placeholder="Enter brand name to search..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
              
              {/* Data Source Checkboxes */}
              <div className="space-y-4 mb-6">
                {dataSourceOptions.map((option) => {
                  const Icon = option.icon;
                  const isChecked = dataSources[option.id];
                  
                  return (
                    <motion.label
                      key={option.id}
                      whileHover={{ scale: 1.02 }}
                      className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                        isChecked 
                          ? 'bg-green-50 border border-green-200' 
                          : 'bg-white border border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => handleDataSourceChange(option.id)}
                        className="w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500 focus:ring-2"
                      />
                      <Icon className={`h-5 w-5 ${isChecked ? 'text-green-600' : 'text-gray-400'}`} />
                      <span className={`text-sm font-medium ${isChecked ? 'text-green-900' : 'text-gray-700'}`}>
                        {option.label}
                      </span>
                    </motion.label>
                  );
                })}
              </div>

              {/* Apply Button */}
              <motion.button
                whileHover={{ scale: (isLoading || !hasChanges()) ? 1 : 1.02 }}
                whileTap={{ scale: (isLoading || !hasChanges()) ? 1 : 0.98 }}
                onClick={handleApplyChanges}
                disabled={isLoading || !hasChanges()}
                className={`w-full py-3 px-4 rounded-lg font-medium focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors ${
                  isLoading || !hasChanges()
                    ? 'bg-gray-400 text-white cursor-not-allowed' 
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {isLoading ? 'Applying Changes...' : 'Apply Changes'}
              </motion.button>


              {/* Tags Section */}
              {analytics && analytics.topCategories && analytics.topCategories.length > 0 && (
                <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <Tag className="h-4 w-4 text-gray-600" />
                    <h3 className="text-sm font-semibold text-gray-900">Top Tags</h3>
                  </div>
                  <div className="space-y-2">
                    {analytics.topCategories.slice(0, 8).map((category, index) => {
                      const totalCount = analytics.topCategories.reduce((sum, cat) => sum + cat.count, 0);
                      const percentage = totalCount > 0 ? (category.count / totalCount) * 100 : 0;
                      
                      return (
                        <div key={index} className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-700 truncate flex-1">
                              {formatCategoryName(category.category)}
                            </span>
                            <div className="flex items-center gap-1 ml-2">
                              <span className="text-xs font-medium text-gray-500">
                                {category.count}
                              </span>
                              <span className="text-xs text-gray-400">
                                ({percentage.toFixed(1)}%)
                              </span>
                            </div>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div 
                              className="bg-green-500 h-1.5 rounded-full transition-all duration-300"
                              style={{ width: `${percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  {analytics.topCategories.length > 8 && (
                    <p className="text-xs text-gray-500 mt-2">
                      +{analytics.topCategories.length - 8} more tags
                    </p>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
