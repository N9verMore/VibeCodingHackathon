const fs = require('fs');
const path = require('path');

async function exportMultipleAppsReviews(appIds, country = 'us', maxReviewsPerApp = 50) {
  const allReviews = [];
  const appDetails = [];
  
  console.log(`🚀 Starting export for ${appIds.length} apps...`);
  console.log(`📱 Country: ${country.toUpperCase()}`);
  console.log(`📊 Max reviews per app: ${maxReviewsPerApp}`);
  console.log('');

  for (let i = 0; i < appIds.length; i++) {
    const appId = appIds[i];
    console.log(`[${i + 1}/${appIds.length}] Processing app ID: ${appId}`);
    
    try {
      const result = await exportReviews(appId, country, maxReviewsPerApp);
      
      appDetails.push(result.app);
      allReviews.push(...result.reviews.map(review => ({
        ...review,
        appId: appId,
        appName: result.app.title
      })));
      
      console.log(`✅ Added ${result.reviews.length} reviews from ${result.app.title}`);
      
    } catch (error) {
      console.log(`❌ Failed to fetch reviews for app ${appId}: ${error.message}`);
    }
    
    console.log('');
  }

  const exportData = {
    summary: {
      totalApps: appIds.length,
      successfulApps: appDetails.length,
      totalReviews: allReviews.length,
      exportDate: new Date().toISOString(),
      country: country
    },
    apps: appDetails,
    reviews: allReviews
  };

  const filename = `multiple_reviews_${country}_${new Date().toISOString().split('T')[0]}.json`;
  const filepath = path.join(__dirname, filename);
  
  fs.writeFileSync(filepath, JSON.stringify(exportData, null, 2));
  
  console.log('🎉 Export completed!');
  console.log(`📁 File: ${filename}`);
  console.log(`📊 Total reviews: ${allReviews.length}`);
  console.log(`📱 Apps processed: ${appDetails.length}/${appIds.length}`);
  console.log(`💾 File size: ${(fs.statSync(filepath).size / 1024).toFixed(2)} KB`);
  
  return filepath;
}

async function exportReviews(appId, country = 'us', maxReviews = 100) {
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
      console.warn('Failed to parse reviews:', reviewsError.message);
      reviews = [];
    }
  } else {
    console.warn(`Failed to fetch reviews: ${reviewsResponse.status}`);
  }

  return {
    app: {
      id: app.trackId,
      title: app.trackName,
      developer: app.artistName,
      rating: app.averageUserRating ? app.averageUserRating.toString() : 'N/A',
      ratingCount: app.userRatingCount || 0,
      price: app.price === 0 ? 'Free' : `$${app.price}`,
      category: app.primaryGenreName,
      description: app.description,
      appUrl: app.trackViewUrl,
      iconUrl: app.artworkUrl100
    },
    reviews: reviews.slice(0, maxReviews)
  };
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

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node export-multiple-reviews.js [country] [maxReviewsPerApp]');
    console.log('');
    console.log('Examples:');
    console.log('  node export-multiple-reviews.js');
    console.log('  node export-multiple-reviews.js us 50');
    console.log('  node export-multiple-reviews.js gb 30');
    console.log('');
    console.log('This will export reviews from popular apps:');
    console.log('  Instagram, WhatsApp, YouTube, Spotify, TikTok, etc.');
    process.exit(1);
  }

  const country = args[0] || 'us';
  const maxReviewsPerApp = parseInt(args[1]) || 50;

  const popularAppIds = [
    389801252, // Instagram
    310633997, // WhatsApp
    544007664, // YouTube
    835599320, // TikTok
    324684580, // Spotify
    284882215, // Facebook
    333903271, // Twitter/X
    284417350, // Snapchat
    310633997, // WhatsApp (duplicate for more reviews)
    389801252, // Instagram (duplicate for more reviews)
  ];

  try {
    await exportMultipleAppsReviews(popularAppIds, country, maxReviewsPerApp);
  } catch (error) {
    console.error('Export failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { exportMultipleAppsReviews };
