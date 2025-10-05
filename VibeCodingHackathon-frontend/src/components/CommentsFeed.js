'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Filter, MessageSquare } from 'lucide-react';
import CommentCard from './CommentCard';

export default function CommentsFeed({ title = "Recent Comments", filterBy = null, limit = 50 }) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [dataSources, setDataSources] = useState({
    playStore: true,
    appStore: true,
    trustpilot: true
  });
  const [brandName, setBrandName] = useState('');

  useEffect(() => {
    fetchComments();
  }, [filterBy, filter, dataSources, brandName]);

  // Listen for data source updates from Layout
  useEffect(() => {
    const handleDataSourceUpdate = (event) => {
      if (event.detail.dataSources) {
        setDataSources(event.detail.dataSources);
      }
      if (event.detail.brandName !== undefined) {
        setBrandName(event.detail.brandName);
      }
    };

    window.addEventListener('dataSourceUpdated', handleDataSourceUpdate);
    
    return () => {
      window.removeEventListener('dataSourceUpdated', handleDataSourceUpdate);
    };
  }, []);

  const fetchComments = async () => {
    try {
      // Check if any data sources are selected
      const selectedSources = Object.entries(dataSources)
        .filter(([_, isSelected]) => isSelected)
        .map(([source, _]) => {
          // Map frontend source names to API platform names
          const sourceMap = {
            playStore: 'google_play',
            appStore: 'app_store',
            trustpilot: 'trustpilot'
          };
          return sourceMap[source] || source;
        });
      
      // If no sources are selected, show empty state
      if (selectedSources.length === 0) {
        setComments([]);
        return;
      }
      
      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      params.append('platforms', JSON.stringify(selectedSources));
      
      // Add brand name if provided
      if (brandName && brandName.trim()) {
        params.append('brandName', brandName.trim());
      }
      
      if (filter !== 'all') {
        params.append('sentiment', filter);
      }
      
      // Use the new comments API endpoint
      const response = await fetch(`/api/comments?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const apiData = await response.json();
      
      // Check if the response contains an error
      if (apiData.error) {
        throw new Error(apiData.message || 'Failed to fetch comments data');
      }
      
      // Transform API data and categorize posts by highest sentiment score
      const transformedComments = apiData.map(comment => {
        // Determine sentiment based on highest score
        const sentimentScores = {
          positive: comment.sentiment_scores?.positive || 0,
          negative: comment.sentiment_scores?.negative || 0,
          neutral: comment.sentiment_scores?.neutral || 0
        };
        
        // Find the sentiment with the highest score
        const dominantSentiment = Object.keys(sentimentScores).reduce((a, b) => 
          sentimentScores[a] > sentimentScores[b] ? a : b
        );

        return {
          id: comment.id,
          title: comment.title || comment.content?.substring(0, 50) + '...',
          content: comment.content,
          description: comment.description, // Extracted "Опис:" field
          author: comment.author || 'Anonymous',
          platform: mapPlatformName(comment.platform),
          sentiment: dominantSentiment,
          publishDate: comment.date || comment.publish_date || comment.created_at,
          likes: comment.likes || 0,
          replies: comment.replies || 0,
          rating: comment.rating || null,
          sentimentScores: sentimentScores,
          thumbnail: comment.thumbnail || null,
          url: comment.url || null,
          category: comment.category, // Pass through category information
          severity: comment.severity // Pass through severity information
        };
      });

      // Filter comments based on filterBy (for issue-specific feeds)
      let filteredComments = transformedComments;
      
      if (filterBy) {
        filteredComments = transformedComments.filter(comment => 
          comment.title.toLowerCase().includes(filterBy.toLowerCase()) ||
          comment.content.toLowerCase().includes(filterBy.toLowerCase())
        );
      }

      // Apply sentiment filter
      if (filter !== 'all') {
        filteredComments = filteredComments.filter(comment => comment.sentiment === filter);
      }

      // Sort by date (most recent first) and limit
      filteredComments = filteredComments
        .sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate))
        .slice(0, limit);

      setComments(filteredComments);
    } catch (error) {
      console.error('Failed to fetch comments:', error);
      // If API fails, show empty state instead of mock data
      setComments([]);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to map platform names
  const mapPlatformName = (platform) => {
    const platformMap = {
      'app_store': 'App Store',
      'google_play': 'Play Store',
      'reddit': 'Reddit',
      'trustpilot': 'Trustpilot',
      'quora': 'Quora',
      'twitter': 'Twitter',
      'facebook': 'Facebook',
      'instagram': 'Instagram',
      'youtube': 'YouTube'
    };
    return platformMap[platform] || platform;
  };

  const handleRefresh = () => {
    setLoading(true);
    fetchComments();
  };

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-md">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white border border-gray-200 rounded-lg p-6 shadow-md"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <MessageSquare className="h-5 w-5 text-gray-600" />
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
            {comments.length}
          </span>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Filter Dropdown */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-1 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            <option value="all">All Sentiments</option>
            <option value="positive">Positive</option>
            <option value="negative">Negative</option>
          </select>
          
          {/* Refresh Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleRefresh}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
          </motion.button>
        </div>
      </div>

      {/* Comments List */}
      {comments.length > 0 ? (
        <div className="space-y-4">
          {comments.map((comment, index) => (
            <CommentCard key={comment.id} comment={comment} index={index} />
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <MessageSquare className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No comments found</p>
          {filterBy && (
            <p className="text-sm text-gray-400 mt-2">
              No comments related to "{filterBy}"
            </p>
          )}
        </div>
      )}
    </motion.div>
  );
}
