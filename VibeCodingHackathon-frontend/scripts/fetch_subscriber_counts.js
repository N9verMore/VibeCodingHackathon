const fs = require('fs');
const path = require('path');

const YOUTUBE_API_KEY = 'AIzaSyA3yx9tfApYSRNOzk4odRWgulWQVz28eVQ';

async function getChannelDetails(channelId) {
  const baseUrl = 'https://www.googleapis.com/youtube/v3/channels';
  const params = new URLSearchParams({
    part: 'statistics,snippet',
    id: channelId,
    key: YOUTUBE_API_KEY
  });

  try {
    const response = await fetch(`${baseUrl}?${params}`);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(`YouTube API Error: ${data.error?.message || 'Unknown error'}`);
    }
    
    if (data.items && data.items.length > 0) {
      const channel = data.items[0];
      return {
        channelId: channel.id,
        title: channel.snippet.title,
        subscriberCount: parseInt(channel.statistics.subscriberCount) || 0,
        videoCount: parseInt(channel.statistics.videoCount) || 0,
        viewCount: parseInt(channel.statistics.viewCount) || 0
      };
    }
    
    return null;
  } catch (error) {
    console.error(`Error fetching channel details for ${channelId}:`, error);
    return null;
  }
}

async function fetchSubscriberCounts() {
  console.log('Starting to fetch subscriber counts for unique authors...');
  
  // Read the parsed videos data
  const inputFile = 'parse_youtube_zara.json';
  const inputPath = path.join(__dirname, '..', inputFile);
  
  if (!fs.existsSync(inputPath)) {
    throw new Error(`Input file not found: ${inputPath}. Please run parse_youtube_videos.js first.`);
  }

  const videos = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  console.log(`Loaded ${videos.length} videos`);

  // Get unique channel IDs and authors
  const uniqueChannels = new Map();
  videos.forEach(video => {
    if (video.channelId && video.author) {
      uniqueChannels.set(video.channelId, {
        channelId: video.channelId,
        author: video.author
      });
    }
  });

  console.log(`Found ${uniqueChannels.size} unique channels`);

  const subscriberData = {};
  let processedCount = 0;

  for (const [channelId, channelInfo] of uniqueChannels) {
    try {
      console.log(`Fetching subscriber count for: ${channelInfo.author} (${channelId})`);
      
      const channelDetails = await getChannelDetails(channelId);
      
      if (channelDetails) {
        subscriberData[channelInfo.author] = {
          channelId: channelDetails.channelId,
          channelTitle: channelDetails.title,
          subscriberCount: channelDetails.subscriberCount,
          videoCount: channelDetails.videoCount,
          viewCount: channelDetails.viewCount
        };
        
        console.log(`✓ ${channelInfo.author}: ${channelDetails.subscriberCount.toLocaleString()} subscribers`);
      } else {
        console.log(`✗ Failed to fetch data for: ${channelInfo.author}`);
        subscriberData[channelInfo.author] = {
          channelId: channelId,
          subscriberCount: 0,
          error: 'Failed to fetch channel details'
        };
      }
      
      processedCount++;
      
      // Add delay to respect API rate limits (100 requests per 100 seconds)
      await new Promise(resolve => setTimeout(resolve, 1200));
      
    } catch (error) {
      console.error(`Error processing ${channelInfo.author}:`, error);
      subscriberData[channelInfo.author] = {
        channelId: channelId,
        subscriberCount: 0,
        error: error.message
      };
      processedCount++;
    }
  }

  // Save subscriber data
  const outputFile = 'youtube_subscriber_counts.json';
  const outputPath = path.join(__dirname, '..', outputFile);
  
  fs.writeFileSync(outputPath, JSON.stringify(subscriberData, null, 2));
  console.log(`Subscriber data saved to: ${outputPath}`);

  // Create summary
  const summary = {
    totalChannels: uniqueChannels.size,
    processedChannels: processedCount,
    successfulFetches: Object.values(subscriberData).filter(data => !data.error).length,
    failedFetches: Object.values(subscriberData).filter(data => data.error).length,
    timestamp: new Date().toISOString(),
    topChannels: Object.entries(subscriberData)
      .filter(([_, data]) => !data.error)
      .sort(([_, a], [__, b]) => b.subscriberCount - a.subscriberCount)
      .slice(0, 10)
      .map(([author, data]) => ({
        author,
        subscriberCount: data.subscriberCount
      }))
  };

  const summaryFile = 'youtube_subscriber_summary.json';
  const summaryPath = path.join(__dirname, '..', summaryFile);
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
  console.log(`Summary saved to: ${summaryPath}`);

  return subscriberData;
}

// Run the script
if (require.main === module) {
  fetchSubscriberCounts()
    .then(data => {
      console.log(`Successfully fetched subscriber counts for ${Object.keys(data).length} channels`);
      process.exit(0);
    })
    .catch(error => {
      console.error('Script failed:', error);
      process.exit(1);
    });
}

module.exports = { fetchSubscriberCounts };
