const fs = require('fs');
const path = require('path');

async function exportLivenReviews(appId = '6450840109', targetReviews = 100) {
  const countries = ['us', 'gb', 'ca', 'au', 'de', 'fr'];
  const allReviews = [];
  const appDetails = {};
  
  console.log(`🚀 Fetching Liven app reviews (ID: ${appId})...`);
  console.log(`🎯 Target: ${targetReviews} reviews`);
  console.log('');

  for (let i = 0; i < countries.length && allReviews.length < targetReviews; i++) {
    const country = countries[i];
    console.log(`[${i + 1}/${countries.length}] Fetching from ${country.toUpperCase()} App Store...`);
    
    try {
      const result = await fetchAppReviews(appId, country);
      
      if (result.app && !appDetails.id) {
        appDetails.id = result.app.id;
        appDetails.title = result.app.title;
        appDetails.developer = result.app.developer;
        appDetails.rating = result.app.rating;
        appDetails.ratingCount = result.app.ratingCount;
        appDetails.price = result.app.price;
        appDetails.category = result.app.category;
        appDetails.description = result.app.description;
        appDetails.appUrl = result.app.appUrl;
        appDetails.iconUrl = result.app.iconUrl;
      }
      
      const newReviews = result.reviews.filter(review => 
        !allReviews.some(existing => 
          existing.author === review.author && 
          existing.content === review.content &&
          existing.date === review.date
        )
      );
      
      allReviews.push(...newReviews.map(review => ({
        ...review,
        country: country
      })));
      
      console.log(`✅ Added ${newReviews.length} new reviews (Total: ${allReviews.length})`);
      
    } catch (error) {
      console.log(`❌ Failed to fetch from ${country}: ${error.message}`);
    }
    
    console.log('');
  }

  const finalReviews = allReviews.slice(0, targetReviews);
  
  const exportData = {
    app: appDetails,
    reviews: finalReviews,
    exportInfo: {
      totalReviewsFound: allReviews.length,
      exportedReviews: finalReviews.length,
      targetReviews: targetReviews,
      exportDate: new Date().toISOString(),
      countriesChecked: countries.slice(0, Math.min(countries.length, Math.ceil(finalReviews.length / 49)))
    }
  };

  const filename = `liven_${targetReviews}_reviews_${new Date().toISOString().split('T')[0]}.json`;
  const filepath = path.join(__dirname, filename);
  
  fs.writeFileSync(filepath, JSON.stringify(exportData, null, 2));
  
  console.log('🎉 Export completed!');
  console.log(`📁 File: ${filename}`);
  console.log(`📱 App: ${appDetails.title} by ${appDetails.developer}`);
  console.log(`⭐ Rating: ${appDetails.rating} (${appDetails.ratingCount?.toLocaleString()} ratings)`);
  console.log(`📊 Reviews found: ${allReviews.length}`);
  console.log(`📊 Reviews exported: ${finalReviews.length}`);
  console.log(`💾 File size: ${(fs.statSync(filepath).size / 1024).toFixed(2)} KB`);
  
  return filepath;
}

async function fetchAppReviews(appId, country = 'us') {
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
    reviews: reviews
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
  const targetReviews = parseInt(args[0]) || 100;
  
  try {
    await exportLivenReviews('6450840109', targetReviews);
  } catch (error) {
    console.error('Export failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { exportLivenReviews };
