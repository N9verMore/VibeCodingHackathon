const BACKEND_URL = 'http://10.8.0.5:8000/api/statistics';

export const DATE_FILTERS = [
  { label: 'Last 24 Hours', value: '24h', days: 1 },
  { label: '7 Days', value: '7d', days: 7 },
  { label: '1 Month', value: '1m', days: 30 },
  { label: '3 Months', value: '3m', days: 90 },
  { label: '6 Months', value: '6m', days: 180 },
  { label: '1 Year', value: '1y', days: 365 },
  { label: 'All Time', value: 'all', days: null }
];

export const calculateDateRange = (days) => {
  const now = new Date();
  const dateTo = new Date(now);
  dateTo.setHours(23, 59, 59, 999); // End of today
  
  const dateFrom = new Date(now);
  dateFrom.setDate(dateFrom.getDate() - parseInt(days));
  dateFrom.setHours(0, 0, 0, 0); // Start of the day
  
  // Format dates as YYYY-MM-DD without timezone
  const formatDateOnly = (date) => {
    return date.toISOString().split('T')[0];
  };
  
  return {
    dateFrom: formatDateOnly(dateFrom),
    dateTo: formatDateOnly(dateTo)
  };
};

export const transformExternalAPIData = (apiData) => {
  return {
    positiveMentions: apiData.sentiment_distribution?.positive || 0,
    negativeMentions: apiData.sentiment_distribution?.negative || 0,
    neutralMentions: apiData.sentiment_distribution?.neutral || 0,
    totalMentions: apiData.total_mentions || 0,
    averageRating: apiData.average_rating || 0,
    reputationScore: apiData.reputation_score?.overall_score || 0,
    reputationTrend: apiData.reputation_score?.trend || 'stable',
    riskLevel: apiData.reputation_score?.risk_level || 'low',
    platformDistribution: apiData.platform_distribution || {},
    topCategories: apiData.top_categories || [],
    chartData: transformTimelineData(apiData.timeline_data || []),
    lastUpdated: apiData.reputation_score?.last_updated || new Date().toISOString()
  };
};

export const transformTimelineData = (timelineData) => {
  return timelineData.map(item => ({
    date: item.date,
    positive: item.positive,
    negative: item.negative,
    neutral: item.neutral,
    total: item.positive + item.negative + item.neutral
  }));
};

export const mapFrontendToBackendPlatforms = (frontendSources) => {
  const sourceMap = {
    playStore: 'google_play',
    appStore: 'app_store',
    threads: 'threads',
    trustpilot: 'trustpilot',
    news: 'news',
    instagram: 'instagram'
  };
  
  return Object.entries(frontendSources)
    .filter(([_, isSelected]) => isSelected)
    .map(([source, _]) => sourceMap[source] || source);
};

export const fetchStatistics = async (options = {}) => {
  const {
    platforms = {},
    dateFilter = 'all',
    brandName = '',
    customDateRange = null
  } = options;

  try {
    // Map frontend platform names to backend platform names
    const selectedSources = mapFrontendToBackendPlatforms(platforms);
    
    // If no sources are selected, return empty analytics
    if (selectedSources.length === 0) {
      return {
        positiveMentions: 0,
        negativeMentions: 0,
        neutralMentions: 0,
        totalMentions: 0,
        averageRating: 0,
        reputationScore: 0,
        reputationTrend: 'stable',
        riskLevel: 'low',
        platformDistribution: {},
        topCategories: [],
        chartData: [],
        lastUpdated: new Date().toISOString()
      };
    }
    
    // Build request body for backend API
    const requestBody = {
      platforms: selectedSources
    };
    
    // Handle date filtering
    if (dateFilter !== 'all') {
      const filter = DATE_FILTERS.find(f => f.value === dateFilter);
      if (filter) {
        const { dateFrom, dateTo } = calculateDateRange(filter.days);
        requestBody.date_from = dateFrom;
        requestBody.date_to = dateTo;
      }
    }
    
    // Handle custom date range
    if (customDateRange) {
      requestBody.date_from = customDateRange.dateFrom;
      requestBody.date_to = customDateRange.dateTo;
    }
    
    // Add brand name (always include it, even if empty)
    requestBody.brand_name = brandName ? brandName.trim() : '';
    
    const response = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
      next: { revalidate: 60 }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const apiData = await response.json();
    
    // Check if the response contains an error
    if (apiData.error) {
      throw new Error(apiData.message || 'Failed to fetch analytics data');
    }
    
    // Transform backend API data to frontend format
    return transformExternalAPIData(apiData);
    
  } catch (error) {
    console.error('Failed to fetch statistics:', error);
    throw error;
  }
};
