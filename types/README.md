# App Store Reviews - TypeScript Interfaces

This directory contains TypeScript interfaces for App Store review data structures, based on Apple's iTunes API and RSS feeds.

## Quick Start

```typescript
import { AppReviewsData, Review, App } from './types';

// Use the main interface for complete app review data
const reviewsData: AppReviewsData = await fetchAppReviews('6450840109');

// Access individual components
const app: App = reviewsData.app;
const reviews: Review[] = reviewsData.reviews;
const firstReview: Review = reviews[0];
```

## Interfaces

### `AppReviewsData`
Main interface containing complete app review export data.

```typescript
interface AppReviewsData {
  app: App;           // App information
  reviews: Review[];  // Array of reviews
  exportInfo: ExportMetadata; // Export metadata
}
```

### `App`
App information from iTunes API.

```typescript
interface App {
  id: number;         // App Store ID (e.g., 6450840109)
  title: string;      // App name (e.g., "Liven: Discover yourself")
  developer: string;  // Developer name (e.g., "Chesmint limited")
  rating: string;     // Average rating (e.g., "4.41493")
  ratingCount: number; // Total ratings (e.g., 25035)
  price: string;      // Price display (e.g., "Free")
  category: string;   // Category (e.g., "Health & Fitness")
  description: string; // Full description
  appUrl: string;     // App Store URL
  iconUrl: string;    // Icon image URL
}
```

### `Review`
Individual review data from RSS feed.

```typescript
interface Review {
  author: string;     // Reviewer name
  rating: string;     // Rating 1-5 (as string)
  title: string;      // Review title
  content: string;    // Review content
  date: string;       // ISO date string
  version: string;    // App version
  country?: string;   // Optional country code
}
```

### `ExportMetadata`
Export process information.

```typescript
interface ExportMetadata {
  totalReviews: number;    // Reviews found
  exportedReviews: number; // Reviews exported
  exportDate: string;      // Export timestamp
  country: string;         // Country code
  appId: string;          // App ID
}
```

## Example Data

Based on Liven app (ID: 6450840109):

```json
{
  "app": {
    "id": 6450840109,
    "title": "Liven: Discover yourself",
    "developer": "Chesmint limited",
    "rating": "4.41493",
    "ratingCount": 25035,
    "price": "Free",
    "category": "Health & Fitness"
  },
  "reviews": [
    {
      "author": "katanitaadl20375",
      "rating": "1",
      "title": "App would not load",
      "content": "I paid the 20 dollars for the app...",
      "date": "2025-10-02T19:08:57-07:00",
      "version": "1.77.0"
    }
  ],
  "exportInfo": {
    "totalReviews": 49,
    "exportedReviews": 49,
    "exportDate": "2025-10-04T11:04:49.224Z",
    "country": "us",
    "appId": "6450840109"
  }
}
```

## Usage Examples

### Basic Usage
```typescript
import { AppReviewsData } from './types';

async function processReviews() {
  const data: AppReviewsData = await fetchReviews('6450840109');
  
  console.log(`App: ${data.app.title}`);
  console.log(`Rating: ${data.app.rating} (${data.app.ratingCount} reviews)`);
  console.log(`Found ${data.reviews.length} reviews`);
}
```

### Filtering Reviews
```typescript
import { Review } from './types';

function getHighRatedReviews(reviews: Review[]): Review[] {
  return reviews.filter(review => parseInt(review.rating) >= 4);
}

function getRecentReviews(reviews: Review[]): Review[] {
  const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
  return reviews.filter(review => new Date(review.date) > oneWeekAgo);
}
```

### Type Guards
```typescript
import { isAppStoreReview, isAppStoreApp } from './types/app-store-reviews';

function validateReviewData(data: any): data is AppReviewsData {
  return isAppStoreApp(data.app) && 
         Array.isArray(data.reviews) && 
         data.reviews.every(isAppStoreReview);
}
```

## API Endpoints

- **Single App Reviews**: `/api/reviews?appId=6450840109&country=us`
- **Export Script**: `node export-reviews.js 6450840109 us 100`

## Notes

- Ratings are strings from the API (e.g., "4.41493")
- Dates are ISO strings from RSS feeds
- Country codes: us, gb, ca, au, de, fr, jp
- RSS feeds typically return ~49 reviews per request
- Use multiple countries to get more reviews
