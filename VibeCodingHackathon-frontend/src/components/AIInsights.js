'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain, TrendingUp, AlertTriangle, Lightbulb, RefreshCw, Loader2 } from 'lucide-react';
import { generateInsight } from '../lib/chat';
import { createMarkdownHTML } from '../lib/markdown';

export default function AIInsights({ analytics = null }) {
  const [insights, setInsights] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const generateInsights = async () => {
    setIsLoading(true);
    try {
      // Create context from current analytics
      let context = '';
      if (analytics) {
        context = `
          Current Analytics Summary:
          - Total Mentions: ${analytics.totalMentions}
          - Positive: ${analytics.positiveMentions} (${((analytics.positiveMentions / analytics.totalMentions) * 100).toFixed(1)}%)
          - Negative: ${analytics.negativeMentions} (${((analytics.negativeMentions / analytics.totalMentions) * 100).toFixed(1)}%)
          - Neutral: ${analytics.neutralMentions} (${((analytics.neutralMentions / analytics.totalMentions) * 100).toFixed(1)}%)
          - Average Rating: ${analytics.averageRating}
          - Reputation Score: ${analytics.reputationScore}
          - Risk Level: ${analytics.riskLevel}
          - Top Categories: ${analytics.topCategories?.map(c => c.category).join(', ') || 'None'}
        `;
      }

      const response = await generateInsight(context);
      
      if (response.success) {
        const newInsight = {
          id: Date.now(),
          content: response.insight,
          timestamp: response.timestamp,
          type: 'general'
        };
        
        setInsights(prev => [newInsight, ...prev.slice(0, 4)]); // Keep only 5 most recent
        setLastUpdated(new Date().toISOString());
      } else {
        throw new Error(response.error);
      }
    } catch (error) {
      console.error('Failed to generate insights:', error);
      const errorInsight = {
        id: Date.now(),
        content: `Failed to generate insights: ${error.message}`,
        timestamp: new Date().toISOString(),
        type: 'error'
      };
      setInsights(prev => [errorInsight, ...prev.slice(0, 4)]);
    } finally {
      setIsLoading(false);
    }
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'trend':
        return <TrendingUp className="h-5 w-5 text-blue-600" />;
      case 'alert':
        return <AlertTriangle className="h-5 w-5 text-orange-600" />;
      case 'tip':
        return <Lightbulb className="h-5 w-5 text-yellow-600" />;
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      default:
        return <Brain className="h-5 w-5 text-green-600" />;
    }
  };

  const getInsightColor = (type) => {
    switch (type) {
      case 'trend':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'alert':
        return 'bg-orange-50 border-orange-200 text-orange-800';
      case 'tip':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-green-50 border-green-200 text-green-800';
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-md">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-green-50 to-blue-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Brain className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">AI Insights</h2>
              <p className="text-sm text-gray-500">
                {lastUpdated ? `Last updated: ${formatTime(lastUpdated)}` : 'Click generate to get insights'}
              </p>
            </div>
          </div>
          <motion.button
            whileHover={{ scale: isLoading ? 1 : 1.05 }}
            whileTap={{ scale: isLoading ? 1 : 0.95 }}
            onClick={generateInsights}
            disabled={isLoading}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              isLoading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            {isLoading ? 'Generating...' : 'Generate Insights'}
          </motion.button>
        </div>
      </div>

      {/* Insights Content */}
      <div className="p-4">
        {insights.length === 0 ? (
          <div className="text-center py-8">
            <Brain className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No insights generated yet</p>
            <p className="text-sm text-gray-400">
              Click "Generate Insights" to get AI-powered analysis of your reputation data
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {insights.map((insight, index) => (
              <motion.div
                key={insight.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className={`p-4 rounded-lg border ${getInsightColor(insight.type)}`}
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {getInsightIcon(insight.type)}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm whitespace-pre-wrap leading-relaxed" dangerouslySetInnerHTML={createMarkdownHTML(insight.content)} />
                    <p className="text-xs opacity-75 mt-2">
                      {formatTime(insight.timestamp)}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
