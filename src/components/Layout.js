'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, FileText, Home, Smartphone, Apple, MessageSquare, Bug } from 'lucide-react';
import Header from './Header';
import Issues from './Issues';

export default function Layout({ children }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dataSources, setDataSources] = useState({
    playStore: true,
    appStore: true,
    threads: false
  });

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'issues', label: 'Issues', icon: Bug },
    { id: 'resources', label: 'Resources', icon: FileText },
  ];

  const dataSourceOptions = [
    { id: 'playStore', label: 'Play Store', icon: Smartphone },
    { id: 'appStore', label: 'App Store', icon: Apple },
    { id: 'threads', label: 'Threads', icon: MessageSquare },
  ];

  const handleDataSourceChange = (sourceId) => {
    setDataSources(prev => ({
      ...prev,
      [sourceId]: !prev[sourceId]
    }));
  };

  const handleApplyChanges = () => {
    console.log('Applied data sources:', dataSources);
    // Here you would typically make an API call to update the data sources
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
            {activeTab === 'issues' && <Issues />}
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
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleApplyChanges}
                className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
              >
                Apply Changes
              </motion.button>

              {/* Status Info */}
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs text-blue-800">
                  <strong>Active Sources:</strong> {Object.values(dataSources).filter(Boolean).length} of {dataSourceOptions.length}
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
