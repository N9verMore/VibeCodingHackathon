/**
 * Example usage of App Store Reviews TypeScript interfaces
 * 
 * This file demonstrates how to use the interfaces with the Liven app data
 */

import { AppReviewsData, Review, App, ExportMetadata } from './index';

// Example: Loading and processing Liven app reviews
async function loadLivenReviews(): Promise<AppReviewsData> {
  // This would typically come from your API or file system
  const response = await fetch('/api/reviews?appId=6450840109&country=us');
  const data: AppReviewsData = await response.json();
  
  return data;
}

// Example: Processing reviews data
function analyzeReviews(reviewsData: AppReviewsData) {
  const { app, reviews, exportInfo } = reviewsData;
  
  console.log(`Analyzing ${app.title} by ${app.developer}`);
  console.log(`Overall rating: ${app.rating} (${app.ratingCount} total ratings)`);
  console.log(`Export contains ${reviews.length} reviews from ${exportInfo.country}`);
  
  // Calculate rating distribution
  const ratingDistribution = reviews.reduce((acc, review) => {
    const rating = review.rating;
    acc[rating] = (acc[rating] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  console.log('Rating distribution:', ratingDistribution);
  
  // Find most recent reviews
  const recentReviews = reviews
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, 5);
  
  console.log('Most recent reviews:');
  recentReviews.forEach(review => {
    console.log(`- ${review.rating}⭐ ${review.title} by ${review.author}`);
  });
}

// Example: Filtering and searching reviews
function searchReviews(reviews: Review[], searchTerm: string): Review[] {
  const term = searchTerm.toLowerCase();
  
  return reviews.filter(review => 
    review.title.toLowerCase().includes(term) ||
    review.content.toLowerCase().includes(term) ||
    review.author.toLowerCase().includes(term)
  );
}

function getReviewsByRating(reviews: Review[], minRating: number): Review[] {
  return reviews.filter(review => parseInt(review.rating) >= minRating);
}

// Example: Type-safe review processing
function processReview(review: Review): {
  sentiment: 'positive' | 'negative' | 'neutral';
  wordCount: number;
  hasEmoji: boolean;
} {
  const rating = parseInt(review.rating);
  const content = review.content.toLowerCase();
  
  // Simple sentiment analysis based on rating
  let sentiment: 'positive' | 'negative' | 'neutral';
  if (rating >= 4) {
    sentiment = 'positive';
  } else if (rating <= 2) {
    sentiment = 'negative';
  } else {
    sentiment = 'neutral';
  }
  
  // Count words
  const wordCount = review.content.split(/\s+/).length;
  
  // Check for emojis (simple regex)
  const hasEmoji = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]/u.test(review.content);
  
  return { sentiment, wordCount, hasEmoji };
}

// Example: Working with app metadata
function getAppSummary(app: App): string {
  return `${app.title} by ${app.developer}
Category: ${app.category}
Rating: ${app.rating}/5 (${app.ratingCount.toLocaleString()} ratings)
Price: ${app.price}
URL: ${app.appUrl}`;
}

// Example: Export metadata analysis
function getExportSummary(exportInfo: ExportMetadata): string {
  const exportDate = new Date(exportInfo.exportDate);
  const successRate = (exportInfo.exportedReviews / exportInfo.totalReviews * 100).toFixed(1);
  
  return `Export Summary:
- App ID: ${exportInfo.appId}
- Country: ${exportInfo.country.toUpperCase()}
- Date: ${exportDate.toLocaleDateString()}
- Reviews: ${exportInfo.exportedReviews}/${exportInfo.totalReviews} (${successRate}% success)`;
}

// Example: Complete workflow
async function main() {
  try {
    // Load reviews data
    const reviewsData = await loadLivenReviews();
    
    // Analyze the data
    analyzeReviews(reviewsData);
    
    // Search for specific reviews
    const bugReports = searchReviews(reviewsData.reviews, 'bug');
    console.log(`Found ${bugReports.length} reviews mentioning bugs`);
    
    // Get high-rated reviews
    const highRated = getReviewsByRating(reviewsData.reviews, 4);
    console.log(`Found ${highRated.length} high-rated reviews (4+ stars)`);
    
    // Process individual reviews
    const processedReviews = reviewsData.reviews.map(processReview);
    const positiveReviews = processedReviews.filter(p => p.sentiment === 'positive');
    console.log(`Found ${positiveReviews.length} positive reviews`);
    
    // Display summaries
    console.log('\nApp Summary:');
    console.log(getAppSummary(reviewsData.app));
    
    console.log('\nExport Summary:');
    console.log(getExportSummary(reviewsData.exportInfo));
    
  } catch (error) {
    console.error('Error processing reviews:', error);
  }
}

// Export for use in other modules
export {
  loadLivenReviews,
  analyzeReviews,
  searchReviews,
  getReviewsByRating,
  processReview,
  getAppSummary,
  getExportSummary
};
