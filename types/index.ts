/**
 * App Store Reviews - TypeScript Interfaces
 * 
 * Simple, focused interfaces for sharing with other engineers
 * Based on the Liven app (ID: 6450840109) review data structure
 */

export interface Review {
  /** Reviewer's display name */
  author: string;
  
  /** Rating from 1-5 stars (as string from API) */
  rating: string;
  
  /** Review title/subject */
  title: string;
  
  /** Full review content */
  content: string;
  
  /** ISO date string when review was posted */
  date: string;
  
  /** App version the review was written for */
  version: string;
  
  /** Optional: Country code (for multi-country exports) */
  country?: string;
}

export interface App {
  /** Unique App Store identifier */
  id: number;
  
  /** App display name */
  title: string;
  
  /** Developer/Publisher name */
  developer: string;
  
  /** Average user rating (string format from API) */
  rating: string;
  
  /** Total number of user ratings */
  ratingCount: number;
  
  /** Price display string (e.g., "Free", "$2.99") */
  price: string;
  
  /** Primary app category */
  category: string;
  
  /** Full app description */
  description: string;
  
  /** Direct App Store URL */
  appUrl: string;
  
  /** App icon image URL */
  iconUrl: string;
}

export interface ExportMetadata {
  /** Total reviews found during export */
  totalReviews: number;
  
  /** Number of reviews actually exported */
  exportedReviews: number;
  
  /** ISO date string when export was performed */
  exportDate: string;
  
  /** Country code for the export */
  country: string;
  
  /** App ID that was exported */
  appId: string;
}

export interface AppReviewsData {
  /** App information */
  app: App;
  
  /** Array of reviews */
  reviews: Review[];
  
  /** Export metadata */
  exportInfo: ExportMetadata;
}

// Example usage:
// const livenReviews: AppReviewsData = await fetchLivenReviews();
// const firstReview: Review = livenReviews.reviews[0];
// const appInfo: App = livenReviews.app;
