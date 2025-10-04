'use client';

import { motion } from 'framer-motion';
import { ThumbsUp, ThumbsDown, MessageCircle, Calendar, User } from 'lucide-react';

export default function CommentCard({ comment, index = 0 }) {
  const getSentimentColor = (sentiment) => {
    if (sentiment === 'positive') {
      return 'bg-green-100 text-green-800 border-green-200';
    } else if (sentiment === 'negative') {
      return 'bg-red-100 text-red-800 border-red-200';
    } else {
      return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPlatformColor = (platform) => {
    const colors = {
      'App Store': 'bg-blue-100 text-blue-800',
      'Play Store': 'bg-green-100 text-green-800',
      'Trustpilot': 'bg-orange-100 text-orange-800',
      'Threads': 'bg-purple-100 text-purple-800',
      'Twitter': 'bg-sky-100 text-sky-800',
      'Facebook': 'bg-indigo-100 text-indigo-800',
      'Instagram': 'bg-pink-100 text-pink-800',
      'YouTube': 'bg-red-100 text-red-800'
    };
    return colors[platform] || 'bg-gray-100 text-gray-800';
  };

  const getCategoryColor = (category) => {
    // Color mapping for different comment categories
    const categoryColors = {
      'fashion': 'bg-pink-100 text-pink-800',
      'fragrance': 'bg-purple-100 text-purple-800',
      'quality': 'bg-blue-100 text-blue-800',
      'service': 'bg-green-100 text-green-800',
      'shipping': 'bg-yellow-100 text-yellow-800',
      'returns': 'bg-orange-100 text-orange-800',
      'pricing': 'bg-red-100 text-red-800',
      'app': 'bg-indigo-100 text-indigo-800',
      'website': 'bg-cyan-100 text-cyan-800',
      'customer_support': 'bg-teal-100 text-teal-800'
    };
    
    // Handle both string and array categories
    const categoryKey = Array.isArray(category) ? category[0] : category;
    return categoryColors[categoryKey] || 'bg-gray-100 text-gray-800';
  };

  const getSentimentIcon = (sentiment) => {
    if (sentiment === 'positive') {
      return ThumbsUp;
    } else if (sentiment === 'negative') {
      return ThumbsDown;
    } else {
      return MessageCircle;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
    return date.toLocaleDateString();
  };

  const renderStars = (rating) => {
    if (!rating) return null;
    
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <span key={i} className="text-yellow-400 text-sm">★</span>
      );
    }
    
    if (hasHalfStar) {
      stars.push(
        <span key="half" className="text-yellow-400 text-sm">☆</span>
      );
    }
    
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(
        <span key={`empty-${i}`} className="text-gray-300 text-sm">☆</span>
      );
    }
    
    return (
      <div className="flex items-center gap-1">
        {stars}
        <span className="text-xs text-gray-600 ml-1">({rating}/5)</span>
      </div>
    );
  };

  const isReviewPlatform = (platform) => {
    return ['Trustpilot', 'App Store', 'Play Store'].includes(platform);
  };

  const getReviewUrl = (comment) => {
    if (comment.platform === 'Trustpilot' && comment.url) {
      // Ensure Trustpilot URLs go to trustpilot.com
      return comment.url.replace(/trustpilot\.\w+/, 'trustpilot.com');
    }
    return comment.url;
  };

  const SentimentIcon = getSentimentIcon(comment.sentiment);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow relative"
    >
      {/* Severity indicator in top left corner */}
      {comment.severity && (
        <div className={`absolute top-2 left-2 px-2 py-1 rounded-full text-xs font-bold ${
          comment.severity === 'critical' ? 'bg-red-500 text-white' :
          comment.severity === 'high' ? 'bg-orange-500 text-white' :
          comment.severity === 'medium' ? 'bg-yellow-500 text-black' :
          'bg-green-500 text-white'
        }`}>
          {comment.severity.toUpperCase()}
        </div>
      )}
      
      {/* Header */}
      <div className={`flex items-start justify-between mb-3 ${comment.severity ? 'pt-6' : ''}`}>
        <div className="flex items-center gap-3">
          {comment.platform === 'YouTube' && comment.thumbnail ? (
            <div className="h-10 w-10 rounded-lg overflow-hidden flex-shrink-0">
              <img 
                src={comment.thumbnail} 
                alt={`${comment.author} video thumbnail`}
                className="h-full w-full object-cover"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div className="h-10 w-10 bg-gradient-to-br from-red-400 to-red-600 rounded-lg flex items-center justify-center" style={{display: 'none'}}>
                <User className="h-5 w-5 text-white" />
              </div>
            </div>
          ) : (
            <div className="h-10 w-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
              <User className="h-5 w-5 text-white" />
            </div>
          )}
          <div>
            <h4 className="font-semibold text-gray-900 text-sm">{comment.author}</h4>
            <div className="flex items-center gap-2 mt-1">
              <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getPlatformColor(comment.platform)}`}>
                {comment.platform}
              </span>
              <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full border ${getSentimentColor(comment.sentiment)}`}>
                <SentimentIcon className="h-3 w-3" />
                {comment.sentiment}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <Calendar className="h-3 w-3" />
          {formatDate(comment.publishDate)}
        </div>
      </div>

      {/* Content */}
      <div className="mb-3">
        <h3 className="font-medium text-gray-900 mb-2 text-sm">
          {(comment.platform === 'YouTube' || isReviewPlatform(comment.platform)) && comment.url ? (
            <a 
              href={getReviewUrl(comment)} 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-blue-600 transition-colors"
            >
              {comment.title}
            </a>
          ) : (
            comment.title
          )}
        </h3>
        <p className="text-gray-700 text-sm leading-relaxed line-clamp-3">
          {comment.content}
        </p>
        
        {/* Display extracted description if available */}
        {comment.description && (
          <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-md d-flex flex-row"><span className="text-xs text-blue-800 font-medium mb-1 mr-1">Summary:</span><span className="text-xs text-blue-700 leading-relaxed">{comment.description}</span></div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center pt-3 border-t border-gray-100">
        <div className="flex items-center gap-4 text-xs text-gray-500">
          {isReviewPlatform(comment.platform) ? (
            // Reviews go first - show category and other review-specific info
            <>
              {comment.category && (
                <div className="flex items-center gap-1 flex-wrap">
                  {Array.isArray(comment.category) ? (
                    comment.category.slice(0, 2).map((cat, idx) => (
                      <span
                        key={idx}
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(cat)}`}
                      >
                        {cat}
                      </span>
                    ))
                  ) : (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(comment.category)}`}>
                      {comment.category}
                    </span>
                  )}
                </div>
              )}
            </>
          ) : comment.platform === 'YouTube' ? (
            // YouTube content second
            <>
              <div className="flex items-center gap-1">
                <ThumbsUp className="h-3 w-3" />
                <span>{comment.likeCount ? comment.likeCount.toLocaleString() : 0}</span>
              </div>
              <div className="flex items-center gap-1">
                <MessageCircle className="h-3 w-3" />
                <span>{comment.commentCount ? comment.commentCount.toLocaleString() : 0}</span>
              </div>
              {comment.viewCount && (
                <div className="flex items-center gap-1">
                  <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                  <span>{comment.viewCount.toLocaleString()}</span>
                </div>
              )}
              {comment.category && (
                <div className="flex items-center gap-1 flex-wrap">
                  {Array.isArray(comment.category) ? (
                    comment.category.slice(0, 2).map((cat, idx) => (
                      <span
                        key={idx}
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(cat)}`}
                      >
                        {cat}
                      </span>
                    ))
                  ) : (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(comment.category)}`}>
                      {comment.category}
                    </span>
                  )}
                </div>
              )}
            </>
          ) : (
            // Other platforms last
            <>
              <div className="flex items-center gap-1">
                <ThumbsUp className="h-3 w-3" />
                <span>{comment.likes || 0}</span>
              </div>
              <div className="flex items-center gap-1">
                <MessageCircle className="h-3 w-3" />
                <span>{comment.replies || 0}</span>
              </div>
              {comment.category && (
                <div className="flex items-center gap-1 flex-wrap">
                  {Array.isArray(comment.category) ? (
                    comment.category.slice(0, 2).map((cat, idx) => (
                      <span
                        key={idx}
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(cat)}`}
                      >
                        {cat}
                      </span>
                    ))
                  ) : (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(comment.category)}`}>
                      {comment.category}
                    </span>
                  )}
                </div>
              )}
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          {comment.rating && isReviewPlatform(comment.platform) && renderStars(comment.rating)}
          {comment.rating && comment.platform === 'YouTube' && `⭐ ${comment.rating}/5`}
          {comment.platform === 'YouTube' && comment.subscriberCount && (
            <span className="text-xs text-gray-400">👥 {comment.subscriberCount.toLocaleString()}</span>
          )}
        </div>
      </div>
    </motion.div>
  );
}
