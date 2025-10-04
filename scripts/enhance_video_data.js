const fs = require('fs');
const path = require('path');

const YOUTUBE_API_KEY = 'AIzaSyA3yx9tfApYSRNOzk4odRWgulWQVz28eVQ';

async function getVideoDetails(videoId) {
  const baseUrl = 'https://www.googleapis.com/youtube/v3/videos';
  const params = new URLSearchParams({
    part: 'statistics,snippet',
    id: videoId,
    key: YOUTUBE_API_KEY
  });

  try {
    const response = await fetch(`${baseUrl}?${params}`);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(`YouTube API Error: ${data.error?.message || 'Unknown error'}`);
    }
    
    if (data.items && data.items.length > 0) {
      const video = data.items[0];
      return {
        viewCount: parseInt(video.statistics.viewCount) || 0,
        likeCount: parseInt(video.statistics.likeCount) || 0,
        commentCount: parseInt(video.statistics.commentCount) || 0,
        duration: video.contentDetails?.duration || null,
        publishedAt: video.snippet.publishedAt,
        title: video.snippet.title,
        description: video.snippet.description
      };
    }
    
    return null;
  } catch (error) {
    console.error(`Error fetching video details for ${videoId}:`, error);
    return null;
  }
}

async function enhanceVideoData() {
  console.log('Starting to enhance video data with views, comments, and likes...');
  
  // Read the parsed videos data
  const videosFile = 'parse_youtube_zara.json';
  const videosPath = path.join(__dirname, '..', videosFile);
  
  if (!fs.existsSync(videosPath)) {
    throw new Error(`Videos file not found: ${videosPath}. Please run parse_youtube_videos.js first.`);
  }

  // Read subscriber data
  const subscriberFile = 'youtube_subscriber_counts.json';
  const subscriberPath = path.join(__dirname, '..', subscriberFile);
  
  let subscriberData = {};
  if (fs.existsSync(subscriberPath)) {
    subscriberData = JSON.parse(fs.readFileSync(subscriberPath, 'utf8'));
    console.log(`Loaded subscriber data for ${Object.keys(subscriberData).length} channels`);
  } else {
    console.log('No subscriber data found. Run fetch_subscriber_counts.js first for complete data.');
  }

  const videos = JSON.parse(fs.readFileSync(videosPath, 'utf8'));
  console.log(`Loaded ${videos.length} videos to enhance`);

  // Setup real-time saving
  const outputFile = 'youtube_enhanced_data.json';
  const outputPath = path.join(__dirname, '..', outputFile);
  const progressFile = 'youtube_enhance_progress.json';
  const progressPath = path.join(__dirname, '..', progressFile);

  // Load existing progress if available
  let enhancedVideos = [];
  let startIndex = 0;
  
  if (fs.existsSync(outputPath)) {
    try {
      enhancedVideos = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
      console.log(`Resuming from existing data: ${enhancedVideos.length} videos already processed`);
    } catch (error) {
      console.log('Could not load existing data, starting fresh');
      enhancedVideos = [];
    }
  }

  if (fs.existsSync(progressPath)) {
    try {
      const progress = JSON.parse(fs.readFileSync(progressPath, 'utf8'));
      startIndex = progress.lastProcessedIndex + 1;
      console.log(`Resuming from index: ${startIndex}`);
    } catch (error) {
      console.log('Could not load progress, starting from beginning');
      startIndex = 0;
    }
  }

  let processedCount = enhancedVideos.length;
  let successCount = enhancedVideos.filter(v => !v.error).length;

  // Helper function to save progress in real-time
  const saveProgress = async (index, enhancedVideo) => {
    try {
      // Add the new video to the array
      enhancedVideos.push(enhancedVideo);
      
      // Save the enhanced data
      fs.writeFileSync(outputPath, JSON.stringify(enhancedVideos, null, 2));
      
      // Save progress tracking
      const progress = {
        lastProcessedIndex: index,
        totalProcessed: enhancedVideos.length,
        successCount: enhancedVideos.filter(v => !v.error).length,
        timestamp: new Date().toISOString()
      };
      fs.writeFileSync(progressPath, JSON.stringify(progress, null, 2));
      
    } catch (error) {
      console.error('Error saving progress:', error);
    }
  };

  // Process videos starting from the last processed index
  for (let i = startIndex; i < videos.length; i++) {
    const video = videos[i];
    
    try {
      console.log(`[${i + 1}/${videos.length}] Enhancing video: ${video.title} (${video.videoId})`);
      
      const videoDetails = await getVideoDetails(video.videoId);
      
      let enhancedVideo;
      
      if (videoDetails) {
        // Get subscriber count for this author
        const authorData = subscriberData[video.author] || {};
        
        enhancedVideo = {
          id: video.id,
          title: video.title,
          content: video.content,
          author: video.author,
          date: video.date,
          platform: video.platform,
          url: video.url,
          thumbnail: video.thumbnail,
          videoId: video.videoId,
          channelId: video.channelId,
          
          // Enhanced data
          viewCount: videoDetails.viewCount,
          likeCount: videoDetails.likeCount,
          commentCount: videoDetails.commentCount,
          duration: videoDetails.duration,
          
          // Author data
          subscriberCount: authorData.subscriberCount || 0,
          channelTitle: authorData.channelTitle || video.author,
          
          // Sentiment analysis (placeholder - you can add real sentiment analysis here)
          sentiment: 'neutral', // Default, can be enhanced with actual sentiment analysis
          sentiment_scores: {
            positive: 0.3,
            negative: 0.3,
            neutral: 0.4
          },
          category: 'fashion', // Default category
          rating: null // YouTube doesn't use star ratings
        };
        
        successCount++;
        console.log(`✓ ${video.title}: ${videoDetails.viewCount.toLocaleString()} views, ${videoDetails.likeCount.toLocaleString()} likes`);
      } else {
        console.log(`✗ Failed to enhance: ${video.title}`);
        // Still add the video with basic data
        enhancedVideo = {
          ...video,
          viewCount: 0,
          likeCount: 0,
          commentCount: 0,
          subscriberCount: subscriberData[video.author]?.subscriberCount || 0,
          sentiment: 'neutral',
          sentiment_scores: { positive: 0.3, negative: 0.3, neutral: 0.4 },
          category: 'fashion',
          rating: null,
          error: 'Failed to fetch video details'
        };
      }
      
      // Save progress in real-time
      await saveProgress(i, enhancedVideo);
      processedCount++;
      
      // Add delay to respect API rate limits
      await new Promise(resolve => setTimeout(resolve, 1200));
      
    } catch (error) {
      console.error(`Error processing ${video.title}:`, error);
      // Add video with basic data even if enhancement fails
      const enhancedVideo = {
        ...video,
        viewCount: 0,
        likeCount: 0,
        commentCount: 0,
        subscriberCount: subscriberData[video.author]?.subscriberCount || 0,
        sentiment: 'neutral',
        sentiment_scores: { positive: 0.3, negative: 0.3, neutral: 0.4 },
        category: 'fashion',
        rating: null,
        error: error.message
      };
      
      // Save progress even for failed videos
      await saveProgress(i, enhancedVideo);
      processedCount++;
    }
  }

  // Clean up progress file since we're done
  if (fs.existsSync(progressPath)) {
    fs.unlinkSync(progressPath);
    console.log('Progress file cleaned up');
  }

  console.log(`✅ Enhancement complete! Enhanced data saved to: ${outputPath}`);

  // Create final summary
  const summary = {
    totalVideos: videos.length,
    processedVideos: processedCount,
    successfulEnhancements: successCount,
    failedEnhancements: processedCount - successCount,
    timestamp: new Date().toISOString(),
    totalViews: enhancedVideos.reduce((sum, video) => sum + (video.viewCount || 0), 0),
    totalLikes: enhancedVideos.reduce((sum, video) => sum + (video.likeCount || 0), 0),
    totalComments: enhancedVideos.reduce((sum, video) => sum + (video.commentCount || 0), 0),
    topVideos: enhancedVideos
      .filter(video => video.viewCount > 0)
      .sort((a, b) => b.viewCount - a.viewCount)
      .slice(0, 10)
      .map(video => ({
        title: video.title,
        author: video.author,
        viewCount: video.viewCount,
        likeCount: video.likeCount
      }))
  };

  const summaryFile = 'youtube_enhanced_summary.json';
  const summaryPath = path.join(__dirname, '..', summaryFile);
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
  console.log(`📊 Summary saved to: ${summaryPath}`);

  return enhancedVideos;
}

// Run the script
if (require.main === module) {
  enhanceVideoData()
    .then(videos => {
      console.log(`Successfully enhanced ${videos.length} videos`);
      process.exit(0);
    })
    .catch(error => {
      console.error('Script failed:', error);
      process.exit(1);
    });
}

module.exports = { enhanceVideoData };
