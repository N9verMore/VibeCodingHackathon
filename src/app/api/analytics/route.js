import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Generate sample analytics data
    const analytics = {
      positiveMentions: 1247,
      negativeMentions: 89,
      totalMentions: 1336,
      positiveChange: 12.5,
      negativeChange: -8.3,
      totalChange: 15.2,
      chartData: generateChartData()
    };

    return NextResponse.json(analytics);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch analytics data' },
      { status: 500 }
    );
  }
}

function generateChartData() {
  const data = [];
  const today = new Date();
  
  // Generate data for the last 30 days
  for (let i = 29; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    // Generate realistic-looking data with some randomness
    const basePositive = 40 + Math.random() * 20;
    const baseNegative = 5 + Math.random() * 10;
    
    // Add some trend and seasonality
    const trend = Math.sin((29 - i) * 0.2) * 5;
    const positive = Math.max(0, Math.round(basePositive + trend + (Math.random() - 0.5) * 10));
    const negative = Math.max(0, Math.round(baseNegative - trend * 0.3 + (Math.random() - 0.5) * 5));
    
    data.push({
      date: date.toISOString().split('T')[0],
      positive,
      negative,
      total: positive + negative
    });
  }
  
  return data;
}
