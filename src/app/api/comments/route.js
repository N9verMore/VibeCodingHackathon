import { NextResponse } from 'next/server';
const { parseCommentText } = require('../../../../lib/textParser.js');

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit')) || 50;
    const platform = searchParams.get('platform');
    const sentiment = searchParams.get('sentiment');
    const platforms = searchParams.get('platforms');
    const brandName = searchParams.get('brandName');
    // Build request body for external API
    const requestBody = {
      limit: limit
    };
    
    // Add platform filtering
    if (platforms) {
      try {
        requestBody.platforms = JSON.parse(platforms);
      } catch (error) {
        // If platforms is not valid JSON, treat as comma-separated string
        requestBody.platforms = platforms.split(',').map(p => p.trim());
      }
    } else if (platform) {
      requestBody.platforms = [platform];
    }
    
    // Add sentiment filtering
    if (sentiment && sentiment !== 'all') {
      requestBody.sentiment = sentiment;
    }
    
    // Add brand name filtering
    if (brandName && brandName.trim()) {
      requestBody.brand_name = brandName.trim();
    }
    
    // Call external API
    const response = await fetch('http://10.8.0.5:8000/api/reviews/filter', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });


    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const apiData = await response.json();
    
    // Extract comments array from the response structure
    let commentsArray = [];
    if (apiData.success && apiData.data && Array.isArray(apiData.data)) {
      commentsArray = apiData.data;
    } else if (Array.isArray(apiData)) {
      commentsArray = apiData;
    } else {
      console.error('Unexpected API response structure:', apiData);
      return NextResponse.json(
        { 
          error: 'Unexpected API response format',
          message: 'The external API returned data in an unexpected format'
        },
        { status: 500 }
      );
    }
    
    // Handle empty response
    if (!commentsArray || commentsArray.length === 0) {
      console.log('No comments found in API response');
      return NextResponse.json([]);
    }
    
    // Transform the API response to match our frontend format
    const transformedData = commentsArray.map(comment => {
      // Parse the text field to extract additional information
      const parsedText = parseCommentText(comment.text);
      
      return {
        id: comment.id,
        title: parsedText.content?.substring(0, 50) + '...' || 'Review',
        content: parsedText.content,
        description: parsedText.description, // Extracted "Опис:" field
        author: 'Anonymous', // API doesn't provide author info
        platform: comment.platform,
        sentiment: comment.sentiment,
        sentiment_scores: {
          positive: comment.sentiment === 'positive' ? 0.8 : 0.1,
          negative: comment.sentiment === 'negative' ? 0.8 : 0.1,
          neutral: comment.sentiment === 'neutral' ? 0.8 : 0.1
        },
        publish_date: comment.timestamp,
        likes: 0, // API doesn't provide likes
        replies: 0, // API doesn't provide replies
        rating: comment.rating,
        // Additional fields from API
        severity: comment.severity,
        category: comment.category,
        backlink: comment.backlink,
        // YouTube fields (not present in this API)
        viewCount: null,
        subscriberCount: null,
        thumbnail: null,
        url: comment.backlink,
        videoId: null
      };
    });
    
    return NextResponse.json(transformedData);
    
  } catch (error) {
    console.error('Error fetching comments:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch comments',
        message: error.message 
      },
      { status: 500 }
    );
  }
}
