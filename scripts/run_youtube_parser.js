#!/usr/bin/env node

const { parseYouTubeVideos } = require('./parse_youtube_videos');
const { fetchSubscriberCounts } = require('./fetch_subscriber_counts');
const { enhanceVideoData } = require('./enhance_video_data');

async function runCompleteYouTubeParsing() {
  console.log('🚀 Starting complete YouTube data parsing pipeline...\n');
  
  try {
    // Step 1: Parse YouTube videos
    const videos = await parseYouTubeVideos();
    console.log(`✅ Found ${videos.length} unique videos\n`);
    
    // Step 2: Fetch subscriber counts
    console.log('👥 Step 2: Fetching subscriber counts for unique authors...');
    const subscriberData = await fetchSubscriberCounts();
    console.log(`✅ Fetched subscriber data for ${Object.keys(subscriberData).length} channels\n`);
    
    // Step 3: Enhance video data
    console.log('📊 Step 3: Enhancing video data with views, comments, and likes...');
    const enhancedVideos = await enhanceVideoData();
    console.log(`✅ Enhanced ${enhancedVideos.length} videos with detailed metrics\n`);
    
    console.log('🎉 Complete YouTube parsing pipeline finished successfully!');
    console.log('\n📁 Generated files:');
    console.log('  - parse_youtube_zara.json (raw video data)');
    console.log('  - youtube_subscriber_counts.json (subscriber data)');
    console.log('  - youtube_enhanced_data.json (final enhanced dataset)');
    console.log('  - Various summary files with statistics');
    
    return enhancedVideos;
    
  } catch (error) {
    console.error('❌ Pipeline failed:', error);
    throw error;
  }
}

// Run the complete pipeline
if (require.main === module) {
  runCompleteYouTubeParsing()
    .then(videos => {
      console.log(`\n🎯 Final result: ${videos.length} enhanced YouTube videos ready for use!`);
      process.exit(0);
    })
    .catch(error => {
      console.error('💥 Pipeline execution failed:', error);
      process.exit(1);
    });
}

module.exports = { runCompleteYouTubeParsing };
