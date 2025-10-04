const fs = require('fs');
const path = require('path');

const YOUTUBE_API_KEY = 'AIzaSyA3yx9tfApYSRNOzk4odRWgulWQVz28eVQ';
const QUERY = 'zara';
const MAX_RESULTS = 50; // YouTube API limit per request
const MAX_PAGES = 10; // Maximum pages to fetch

async function searchYouTubeVideos(query, pageToken = null) {
  const baseUrl = 'https://www.googleapis.com/youtube/v3/search';
  const params = new URLSearchParams({
    part: 'snippet',
    q: `#${query}`,
    type: 'video',
    maxResults: MAX_RESULTS,
    order: 'relevance',
    key: YOUTUBE_API_KEY
  });

  if (pageToken) {
    params.append('pageToken', pageToken);
  }

  try {
    const response = await fetch(`${baseUrl}?${params}`);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(`YouTube API Error: ${data.error?.message || 'Unknown error'}`);
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching YouTube data:', error);
    throw error;
  }
}

async function parseYouTubeVideos() {
  console.log(`Starting to parse YouTube videos for hashtag: #${QUERY}`);
  
  let allVideos = [];
  let nextPageToken = null;
  let pageCount = 0;

  try {
    do {
      pageCount++;
      console.log(`Fetching page ${pageCount}...`);
      
      const data = await searchYouTubeVideos(QUERY, nextPageToken);
      
      if (data.items && data.items.length > 0) {
        const videos = data.items.map(item => ({
          id: `youtube_${item.id.videoId}`,
          title: item.snippet.title,
          content: item.snippet.description || 'YouTube video content',
          author: item.snippet.channelTitle,
          date: item.snippet.publishedAt,
          platform: 'youtube',
          url: `https://youtube.com/watch?v=${item.id.videoId}`,
          thumbnail: item.snippet.thumbnails.high?.url || item.snippet.thumbnails.default?.url,
          videoId: item.id.videoId,
          channelId: item.snippet.channelId,
          publishedAt: item.snippet.publishedAt,
          description: item.snippet.description
        }));
        
        allVideos.push(...videos);
        console.log(`Found ${videos.length} videos on page ${pageCount}`);
      }
      
      nextPageToken = data.nextPageToken;
      
      // Add delay to respect API rate limits
      if (nextPageToken && pageCount < MAX_PAGES) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
    } while (nextPageToken && pageCount < MAX_PAGES);

    // Remove duplicates based on videoId
    const uniqueVideos = allVideos.filter((video, index, self) => 
      index === self.findIndex(v => v.videoId === video.videoId)
    );

    console.log(`Total unique videos found: ${uniqueVideos.length}`);

    // Save to JSON file
    const outputFile = `parse_youtube_${QUERY}.json`;
    const outputPath = path.join(__dirname, '..', outputFile);
    
    fs.writeFileSync(outputPath, JSON.stringify(uniqueVideos, null, 2));
    console.log(`Data saved to: ${outputPath}`);

    // Also save a summary
    const summary = {
      query: QUERY,
      totalVideos: uniqueVideos.length,
      pagesFetched: pageCount,
      timestamp: new Date().toISOString(),
      uniqueAuthors: [...new Set(uniqueVideos.map(v => v.author))].length
    };

    const summaryFile = `parse_youtube_${QUERY}_summary.json`;
    const summaryPath = path.join(__dirname, '..', summaryFile);
    fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
    console.log(`Summary saved to: ${summaryPath}`);

    return uniqueVideos;

  } catch (error) {
    console.error('Error parsing YouTube videos:', error);
    throw error;
  }
}

// Run the script
if (require.main === module) {
  parseYouTubeVideos()
    .then(videos => {
      console.log(`Successfully parsed ${videos.length} YouTube videos`);
      process.exit(0);
    })
    .catch(error => {
      console.error('Script failed:', error);
      process.exit(1);
    });
}

module.exports = { parseYouTubeVideos };
