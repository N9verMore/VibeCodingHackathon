import { NextResponse } from 'next/server';
import xml2js from 'xml2js';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const appId = searchParams.get('appId');
    const country = searchParams.get('country') || 'us';
    
    if (!appId) {
      return NextResponse.json({ error: 'App ID is required' }, { status: 400 });
    }

    console.log(`Fetching reviews for app ID: ${appId} in country: ${country}`);
    
    const appData = await fetchAppStoreData(appId, country);
    
    return NextResponse.json({ app: appData });
  } catch (error) {
    console.error('Error fetching reviews:', error);
    return NextResponse.json({ 
      error: 'Failed to fetch reviews', 
      details: error.message 
    }, { status: 500 });
  }
}

async function fetchAppStoreData(appId, country) {
  try {
    const appInfoUrl = `https://itunes.apple.com/lookup?id=${appId}`;
    const reviewsUrl = `https://itunes.apple.com/${country}/rss/customerreviews/id=${appId}/json`;
    
    const [appInfoResponse, reviewsResponse] = await Promise.all([
      fetch(appInfoUrl),
      fetch(reviewsUrl)
    ]);

    if (!appInfoResponse.ok) {
      throw new Error(`Failed to fetch app info: ${appInfoResponse.status}`);
    }

    const appInfoData = await appInfoResponse.json();
    
    if (!appInfoData.results || appInfoData.results.length === 0) {
      throw new Error(`App with ID ${appId} not found`);
    }

    const app = appInfoData.results[0];
    
    let reviews = [];
    if (reviewsResponse.ok) {
      try {
        const reviewsData = await reviewsResponse.json();
        reviews = parseReviewsFromRSS(reviewsData);
      } catch (reviewsError) {
        console.warn('Failed to parse reviews, using empty array:', reviewsError.message);
        reviews = [];
      }
    } else {
      console.warn(`Failed to fetch reviews: ${reviewsResponse.status}`);
    }

    return {
      id: app.trackId,
      title: app.trackName,
      developer: app.artistName,
      rating: app.averageUserRating ? app.averageUserRating.toString() : 'N/A',
      ratingCount: app.userRatingCount || 0,
      price: app.price === 0 ? 'Free' : `$${app.price}`,
      category: app.primaryGenreName,
      description: app.description,
      appUrl: app.trackViewUrl,
      iconUrl: app.artworkUrl100,
      reviews: reviews
    };
    
  } catch (error) {
    console.error('Error in fetchAppStoreData:', error);
    throw error;
  }
}

function parseReviewsFromRSS(rssData) {
  try {
    if (!rssData.feed || !rssData.feed.entry) {
      return [];
    }

    const entries = Array.isArray(rssData.feed.entry) ? rssData.feed.entry : [rssData.feed.entry];
    
    return entries.map((entry, index) => {
      if (index === 0) return null;
      
      return {
        author: entry.author?.name?.label || entry.author?.label || 'Anonymous',
        rating: entry['im:rating']?.label || entry.rating?.label || 'N/A',
        title: entry.title?.label || 'No title',
        content: entry.content?.label || 'No content',
        date: entry.updated?.label || new Date().toISOString(),
        version: entry['im:version']?.label || entry.version?.label || 'N/A'
      };
    }).filter(review => review !== null);
    
  } catch (error) {
    console.error('Error parsing reviews from RSS:', error);
    return [];
  }
}
