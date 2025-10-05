'use client';

import { motion } from 'framer-motion';
import { ThumbsUp, ThumbsDown, MessageCircle, Calendar, User, FileText, Loader2, Bot, Copy, Check, ChevronDown, ChevronUp, CheckCircle, XCircle } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function CommentCard({ comment, index = 0 }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDraft, setGeneratedDraft] = useState(null);
  const [actionItems, setActionItems] = useState([]);
  const [isCopied, setIsCopied] = useState(false);
  const [isResponseCollapsed, setIsResponseCollapsed] = useState(false);
  const [isActionItemsCollapsed, setIsActionItemsCollapsed] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
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

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  // Local storage functions
  const getStorageKey = (commentId) => `comment_${commentId}`;

  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem(getStorageKey(comment.id));
      if (stored) {
        const data = JSON.parse(stored);
        if (data.generatedDraft) setGeneratedDraft(data.generatedDraft);
        if (data.actionItems) setActionItems(data.actionItems);
        if (data.isCompleted !== undefined) setIsCompleted(data.isCompleted);
      }
    } catch (error) {
      console.error('Failed to load from localStorage:', error);
    }
  };

  const saveToStorage = (draft, items, completed) => {
    try {
      const data = {
        generatedDraft: draft,
        actionItems: items,
        isCompleted: completed
      };
      localStorage.setItem(getStorageKey(comment.id), JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  };

  // Load data from localStorage on component mount
  useEffect(() => {
    loadFromStorage();
  }, [comment.id]);

  // Save to localStorage whenever data changes
  useEffect(() => {
    if (generatedDraft || actionItems.length > 0) {
      saveToStorage(generatedDraft, actionItems, isCompleted);
    }
  }, [generatedDraft, actionItems, isCompleted, comment.id]);

  const handleCompletedToggle = () => {
    const newCompleted = !isCompleted;
    setIsCompleted(newCompleted);
    saveToStorage(generatedDraft, actionItems, newCompleted);
  };

  const handleGenerateDraft = async () => {
    setIsGenerating(true);
    try {
      const getPlatformStyle = (platform) => {
        const styles = {
          'Instagram': 'casual, trendy, with emojis, friendly yet professional',
          'App Store': 'official, polite, professional, formal tone',
          'Play Store': 'official, polite, professional, formal tone',
          'Reddit': 'casual, friendly, smart, conversational',
          'Trustpilot': 'professional, polite, customer-focused',
          'YouTube': 'engaging, friendly, professional',
          'Facebook': 'warm, friendly, community-focused',
          'Twitter': 'concise, professional, engaging'
        };
        return styles[platform] || 'professional, polite, helpful';
      };

      const platformStyle = getPlatformStyle(comment.platform);
      const sentimentContext = comment.sentiment === 'negative' ? 'This is a negative comment that needs careful, empathetic handling.' : 
                              comment.sentiment === 'positive' ? 'This is a positive comment that should be acknowledged warmly.' : 
                              'This is a neutral comment that needs helpful response.';

      const payload = {
        message: `Напиши природну, людяну відповідь від служби підтримки на цей ${comment.sentiment} коментар з ${comment.platform}.

Стиль платформи: ${platformStyle}
Контекст: ${sentimentContext}

Коментар: "${comment.content}"
${comment.category ? `Категорія: ${comment.category}` : ''}
${comment.rating ? `Рейтинг: ${comment.rating}/5` : ''}

ВАЖЛИВО - відповідь має бути:
- Написана українською мовою
- Природною та живою, як справжня людина
- Без шаблонних фраз та корпоративного жаргону
- З конкретними деталями та особистим підходом
- Відповідно до стилю платформи
- Щирою та емпатичною
- З практичними порадами або рішеннями
- Без зайвих формальностей

Приклади природних фраз:
- "Розумію вашу фрустрацію..."
- "Дякую, що поділилися досвідом!"
- "Це дійсно важлива інформація для нас"
- "Давайте разом це вирішимо"
- "Ваш відгук допоможе нам стати кращими"

Уникай: "Дякуємо за звернення", "Ми цінуємо ваш відгук", "Наша команда працює над цим" - це звучить як бот.

ДОДАТКОВО - створи список дій для команди підтримки у форматі JSON:
{
  "response": "твоя відповідь клієнту",
  "action_items": [
    "конкретна дія 1",
    "конкретна дія 2",
    "конкретна дія 3"
  ]
}

Приклади дій:
- "перевірити обліковий запис користувача"
- "зв'язатися зі службою підтримки"
- "перевірити статус замовлення"
- "оновити інформацію в системі"
- "направити до відповідного відділу"
- "зафіксувати проблему в базі даних"`

      };

      const response = await fetch('http://10.8.0.5:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Handle different response structures from the chat API
      let draftText = '';
      let extractedActionItems = [];
      
      const extractJsonFromText = (text) => {
        // Look for JSON object in the text
        const jsonMatch = text.match(/\{[\s\S]*"response"[\s\S]*"action_items"[\s\S]*\}/);
        if (jsonMatch) {
          try {
            const parsedJson = JSON.parse(jsonMatch[0]);
            if (parsedJson.response && parsedJson.action_items) {
              return {
                response: parsedJson.response,
                actionItems: parsedJson.action_items
              };
            }
          } catch (error) {
            console.log('Failed to parse JSON from text:', error);
          }
        }
        return null;
      };
      
      if (data.answer) {
        const extracted = extractJsonFromText(data.answer);
        if (extracted) {
          draftText = extracted.response;
          extractedActionItems = extracted.actionItems;
        } else {
          // Try to parse the entire answer as JSON
          try {
            const parsedAnswer = JSON.parse(data.answer);
            if (parsedAnswer.response && parsedAnswer.action_items) {
              draftText = parsedAnswer.response;
              extractedActionItems = parsedAnswer.action_items;
            } else {
              draftText = data.answer;
            }
          } catch {
            draftText = data.answer;
          }
        }
      } else if (data.response) {
        const extracted = extractJsonFromText(data.response);
        if (extracted) {
          draftText = extracted.response;
          extractedActionItems = extracted.actionItems;
        } else {
          draftText = data.response;
        }
      } else if (data.message && data.message.answer) {
        const extracted = extractJsonFromText(data.message.answer);
        if (extracted) {
          draftText = extracted.response;
          extractedActionItems = extracted.actionItems;
        } else {
          // Try to parse the entire message answer as JSON
          try {
            const parsedAnswer = JSON.parse(data.message.answer);
            if (parsedAnswer.response && parsedAnswer.action_items) {
              draftText = parsedAnswer.response;
              extractedActionItems = parsedAnswer.action_items;
            } else {
              draftText = data.message.answer;
            }
          } catch {
            draftText = data.message.answer;
          }
        }
      } else if (data.content) {
        const extracted = extractJsonFromText(data.content);
        if (extracted) {
          draftText = extracted.response;
          extractedActionItems = extracted.actionItems;
        } else {
          draftText = data.content;
        }
      } else if (typeof data === 'string') {
        const extracted = extractJsonFromText(data);
        if (extracted) {
          draftText = extracted.response;
          extractedActionItems = extracted.actionItems;
        } else {
          // Try to parse the entire string as JSON
          try {
            const parsedData = JSON.parse(data);
            if (parsedData.response && parsedData.action_items) {
              draftText = parsedData.response;
              extractedActionItems = parsedData.action_items;
            } else {
              draftText = data;
            }
          } catch {
            draftText = data;
          }
        }
      } else {
        draftText = JSON.stringify(data);
      }
      
      setGeneratedDraft(draftText);
      setActionItems(extractedActionItems);
      
      // Auto-copy to clipboard
      await copyToClipboard(draftText);
    } catch (error) {
      console.error('Error generating draft:', error);
      alert('Error generating draft: ' + error.message);
    } finally {
      setIsGenerating(false);
    }
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

      {/* Generated Draft Display */}
      {generatedDraft && (
        <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsResponseCollapsed(!isResponseCollapsed)}
                className="flex items-center gap-1 text-sm font-medium text-green-800 hover:text-green-900"
              >
                Generated Response Draft
                {isResponseCollapsed ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronUp className="h-4 w-4" />
                )}
              </motion.button>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => copyToClipboard(generatedDraft)}
              className={`flex items-center gap-1 px-2 py-1 rounded-md text-xs font-normal transition-colors ${
                isCopied
                  ? 'bg-green-100 text-green-700'
                  : 'bg-green-100 text-green-600 hover:bg-green-200'
              }`}
            >
              {isCopied ? (
                <>
                  <Check className="h-3 w-3" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  Copy
                </>
              )}
            </motion.button>
          </div>
          {!isResponseCollapsed && (
            <p className="text-sm text-green-700 leading-relaxed whitespace-pre-wrap">
              {typeof generatedDraft === 'string' ? generatedDraft : JSON.stringify(generatedDraft)}
            </p>
          )}
        </div>
      )}

      {/* Action Items Display */}
      {actionItems && actionItems.length > 0 && (
        <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsActionItemsCollapsed(!isActionItemsCollapsed)}
              className="flex items-center gap-1 text-sm font-medium text-blue-800 hover:text-blue-900"
            >
              Action Items for Support Team
              {isActionItemsCollapsed ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronUp className="h-4 w-4" />
              )}
            </motion.button>
            <div className="flex items-center gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleCompletedToggle}
                className={`flex items-center gap-1 px-2 py-1 rounded-md text-xs font-normal transition-colors ${
                  isCompleted
                    ? 'bg-green-100 text-green-700 hover:bg-green-200'
                    : 'bg-red-100 text-red-700 hover:bg-red-200'
                }`}
              >
                {isCompleted ? (
                  <>
                    <CheckCircle className="h-3 w-3" />
                    Completed
                  </>
                ) : (
                  <>
                    <XCircle className="h-3 w-3" />
                    Not Completed
                  </>
                )}
              </motion.button>
            </div>
          </div>
          {!isActionItemsCollapsed && (
            <ul className="space-y-1">
              {actionItems.map((item, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-blue-700">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
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
          ) : (
            // Other platforms - show only categories
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
      
      {/* AI Generate Draft Button */}
      <div className="mt-2 flex justify-end">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleGenerateDraft}
          disabled={isGenerating}
          className={`flex items-center gap-1 px-2 py-1 rounded-md text-xs font-normal transition-colors ${
            isGenerating
              ? 'bg-purple-100 text-purple-400 cursor-not-allowed'
              : 'bg-purple-50 text-purple-600 hover:bg-purple-100 hover:text-purple-700 border border-purple-200'
          }`}
        >
          {isGenerating ? (
            <>
              <Loader2 className="h-3 w-3 animate-spin" />
              AI Generating...
            </>
          ) : (
            <>
              <Bot className="h-3 w-3" />
              AI Draft
            </>
          )}
        </motion.button>
      </div>
    </motion.div>
  );
}
