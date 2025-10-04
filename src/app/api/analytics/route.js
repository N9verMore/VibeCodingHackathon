import { NextResponse } from 'next/server';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const days = searchParams.get('days');
    
    // Build API URL with date filter if provided
    let apiUrl = 'http://10.8.0.5:8000/api/statistics';
    if (days) {
      apiUrl += `?days=${days}`;
    }
    
    // Fetch real analytics data from your API
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add cache control to prevent stale data
      next: { revalidate: 60 } // Revalidate every 60 seconds
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const apiData = await response.json();
    
    // Transform API data to match our frontend structure
    const analytics = {
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

    return NextResponse.json(analytics);
  } catch (error) {
    console.error('Error fetching analytics from API:', error);
    
    // Return error response instead of fallback data
    return NextResponse.json(
      { 
        error: 'Failed to fetch analytics data',
        message: error.message 
      },
      { status: 500 }
    );
  }
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

