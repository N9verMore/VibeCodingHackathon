import { NextResponse } from 'next/server';

export async function GET(request) {

}

function calculateDateRange(days) {
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
}

function transformExternalAPIData(apiData) {
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
}


function transformTimelineData(timelineData) {
  return timelineData.map(item => ({
    date: item.date,
    positive: item.positive,
    negative: item.negative,
    neutral: item.neutral,
    total: item.positive + item.negative + item.neutral
  }));
}

