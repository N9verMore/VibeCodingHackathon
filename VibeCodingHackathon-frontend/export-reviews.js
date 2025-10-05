const fs = require('fs');
const path = require('path');

async function exportReviews(appId, country = 'us', maxReviews = 100) {
  try {
    console.log(`Fetching reviews for app ID: ${appId} from ${country} App Store...`);
    
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

    const exportData = {
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
      reviews: reviews.slice(0, maxReviews),
      exportInfo: {
        totalReviews: reviews.length,
        exportedReviews: Math.min(reviews.length, maxReviews),
        exportDate: new Date().toISOString(),
        country: country,
        appId: appId
      }
    };

    const filename = `reviews_${appId}_${country}_${new Date().toISOString().split('T')[0]}.json`;
    const filepath = path.join(__dirname, filename);
    
    fs.writeFileSync(filepath, JSON.stringify(exportData, null, 2));
    
    console.log(`✅ Successfully exported ${exportData.exportInfo.exportedReviews} reviews to: ${filename}`);
    console.log(`📱 App: ${app.trackName} by ${app.artistName}`);
    console.log(`⭐ Rating: ${exportData.app.rating} (${exportData.app.ratingCount.toLocaleString()} ratings)`);
    console.log(`📁 File size: ${(fs.statSync(filepath).size / 1024).toFixed(2)} KB`);
    
    return filepath;
    
  } catch (error) {
    console.error('❌ Error exporting reviews:', error.message);
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

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node export-reviews.js <appId> [country] [maxReviews]');
    console.log('');
    console.log('Examples:');
    console.log('  node export-reviews.js 389801252');
    console.log('  node export-reviews.js 389801252 us 100');
    console.log('  node export-reviews.js 6450840109 gb 50');
    console.log('');
    console.log('Popular App IDs:');
    console.log('  389801252 - Instagram');
    console.log('  310633997 - WhatsApp');
    console.log('  544007664 - YouTube');
    console.log('  6450840109 - Liven: Discover yourself');
    process.exit(1);
  }

  const appId = args[0];
  const country = args[1] || 'us';
  const maxReviews = parseInt(args[2]) || 100;

  try {
    await exportReviews(appId, country, maxReviews);
  } catch (error) {
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { exportReviews };
