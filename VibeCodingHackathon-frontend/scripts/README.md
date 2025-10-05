# YouTube Data Parser Scripts

This directory contains scripts to parse YouTube data for Zara-related videos and enhance the existing comment system with real YouTube metrics.

## Scripts Overview

### 1. `parse_youtube_videos.js`
- **Purpose**: Searches YouTube for videos with #zara hashtag
- **Output**: `parse_youtube_zara.json` - Raw video data
- **API Usage**: YouTube Search API
- **Rate Limit**: ~50 requests per minute

### 2. `fetch_subscriber_counts.js`
- **Purpose**: Fetches subscriber counts for unique channel authors
- **Input**: `parse_youtube_zara.json`
- **Output**: `youtube_subscriber_counts.json` - Author subscriber data
- **API Usage**: YouTube Channels API
- **Rate Limit**: ~100 requests per 100 seconds

### 3. `enhance_video_data.js`
- **Purpose**: Enhances video data with views, likes, comments
- **Input**: `parse_youtube_zara.json` + `youtube_subscriber_counts.json`
- **Output**: `youtube_enhanced_data.json` - Complete enhanced dataset
- **API Usage**: YouTube Videos API
- **Rate Limit**: ~100 requests per 100 seconds
- **Features**: 
  - ✅ **Real-time saving** - Data saved after each video
  - ✅ **Resume capability** - Can resume from interruption
  - ✅ **Progress tracking** - Tracks last processed index

### 4. `run_youtube_parser.js`
- **Purpose**: Master script that runs all three scripts in sequence
- **Usage**: `node scripts/run_youtube_parser.js`

## Usage

### Quick Start (Recommended)
```bash
# Run the complete pipeline
node scripts/run_youtube_parser.js
```

### Individual Scripts
```bash
# Step 1: Parse videos
node scripts/parse_youtube_videos.js

# Step 2: Fetch subscriber counts
node scripts/fetch_subscriber_counts.js

# Step 3: Enhance video data
node scripts/enhance_video_data.js
```

## Output Files

### Generated Files
- `parse_youtube_zara.json` - Raw video data from YouTube search
- `youtube_subscriber_counts.json` - Channel subscriber information
- `youtube_enhanced_data.json` - **Final enhanced dataset**
- `*_summary.json` - Statistics and summaries for each step

### Final Dataset Structure
```json
{
  "id": "youtube_Oi7aANyP7b4",
  "title": "Zara cotton dress review - not as good as you think!",
  "content": "YouTube video content",
  "author": "Jennifer Wang",
  "date": "2023-05-12T13:52:33Z",
  "platform": "youtube",
  "url": "https://youtube.com/watch?v=Oi7aANyP7b4",
  "thumbnail": "https://i.ytimg.com/vi/Oi7aANyP7b4/hqdefault.jpg",
  "videoId": "Oi7aANyP7b4",
  "viewCount": 125000,
  "likeCount": 2500,
  "commentCount": 150,
  "subscriberCount": 50000,
  "sentiment": "negative",
  "sentiment_scores": {
    "positive": 0.1,
    "negative": 0.7,
    "neutral": 0.2
  },
  "category": "fashion",
  "rating": null
}
```

## API Key Configuration

The scripts use the YouTube API key: `AIzaSyA3yx9tfApYSRNOzk4odRWgulWQVz28eVQ`

**Note**: This key has rate limits. For production use, consider:
- Using multiple API keys
- Implementing proper rate limiting
- Using YouTube Data API v3 quotas efficiently

## Rate Limiting

Each script includes built-in delays to respect YouTube API rate limits:
- Search API: 1 second delay between requests
- Channels/Videos API: 1.2 second delay between requests

## Error Handling

- Scripts continue processing even if individual requests fail
- Failed requests are logged with error details
- Partial data is saved even if some requests fail
- Summary files include success/failure statistics

## Real-Time Saving & Resume Capability

The `enhance_video_data.js` script includes advanced features to prevent data loss:

### ✅ **Real-Time Saving**
- Data is saved after each video is processed
- No data loss if connection is interrupted
- Progress is tracked in `youtube_enhance_progress.json`

### ✅ **Resume Capability**
- Script automatically resumes from last processed video
- Detects existing data and continues from where it left off
- No need to restart from beginning

### ✅ **Progress Tracking**
- Shows current progress: `[45/428] Enhancing video...`
- Tracks successful vs failed enhancements
- Progress file cleaned up when complete

### Usage Examples
```bash
# If interrupted, just run again - it will resume automatically
pnpm youtube:enhance

# Clean up progress files if needed
pnpm youtube:clean
```

## Integration with Frontend

The enhanced data can be used by updating the CommentsFeed component to use `youtube_enhanced_data.json` instead of the current `youtube_comments.json`.

## Monitoring

Each script generates summary files with:
- Total items processed
- Success/failure counts
- Top performers (most views, subscribers, etc.)
- Processing timestamps

## Troubleshooting

### Common Issues
1. **API Quota Exceeded**: Wait for quota reset or use multiple API keys
2. **Network Errors**: Scripts will retry and continue with remaining items
3. **Missing Files**: Run scripts in order or use the master script

### Logs
All scripts provide detailed console output showing:
- Progress indicators
- Success/failure status
- Error messages
- Final statistics
