export interface AppStoreReview {
  author: string;
  rating: string;
  title: string;
  content: string;
  date: string;
  version: string;
  country?: string;
  appId?: number;
  appName?: string;
}

export interface AppStoreApp {
  id: number;
  title: string;
  developer: string;
  rating: string;
  ratingCount: number;
  price: string;
  category: string;
  description: string;
  appUrl: string;
  iconUrl: string;
}

export interface ExportInfo {
  totalReviews: number;
  exportedReviews: number;
  exportDate: string;
  country: string;
  appId: string;
  targetReviews?: number;
  countriesChecked?: string[];
}

export interface AppStoreReviewsExport {
  app: AppStoreApp;
  reviews: AppStoreReview[];
  exportInfo: ExportInfo;
}

export interface MultiAppExportSummary {
  totalApps: number;
  successfulApps: number;
  totalReviews: number;
  exportDate: string;
  country: string;
}

export interface MultiAppReviewsExport {
  summary: MultiAppExportSummary;
  apps: AppStoreApp[];
  reviews: AppStoreReview[];
}

export interface iTunesLookupResponse {
  resultCount: number;
  results: iTunesAppResult[];
}

export interface iTunesAppResult {
  trackId: number;
  trackName: string;
  artistName: string;
  averageUserRating?: number;
  userRatingCount?: number;
  price: number;
  primaryGenreName: string;
  description: string;
  trackViewUrl: string;
  artworkUrl100: string;
}

export interface RSSFeedResponse {
  feed: RSSFeed;
}

export interface RSSFeed {
  entry: RSSFeedEntry[];
}

export interface RSSFeedEntry {
  author: {
    name: {
      label: string;
    };
  };
  'im:rating': {
    label: string;
  };
  title: {
    label: string;
  };
  content: {
    label: string;
  };
  updated: {
    label: string;
  };
  'im:version': {
    label: string;
  };
}

export type CountryCode = 'us' | 'gb' | 'ca' | 'au' | 'de' | 'fr' | 'jp';

export interface ExportOptions {
  appId: string;
  country?: CountryCode;
  maxReviews?: number;
  includeAppInfo?: boolean;
}

export interface AppStoreError {
  error: string;
  details?: string;
  appId?: string;
  country?: string;
}

export type ReviewRating = '1' | '2' | '3' | '4' | '5';

export type AppCategory = 
  | 'Health & Fitness'
  | 'Photo & Video'
  | 'Social Networking'
  | 'Entertainment'
  | 'Productivity'
  | 'Education'
  | 'Games'
  | 'Lifestyle'
  | 'Music'
  | 'News'
  | 'Sports'
  | 'Travel'
  | 'Utilities'
  | 'Weather'
  | 'Business'
  | 'Developer Tools'
  | 'Finance'
  | 'Food & Drink'
  | 'Medical'
  | 'Navigation'
  | 'Reference'
  | 'Shopping'
  | 'Stickers'
  | 'Books'
  | 'Catalogs'
  | 'Graphics & Design'
  | 'Magazines & Newspapers'
  | 'Newsstand'
  | 'Productivity'
  | 'Developer Tools'
  | string;

export const isValidRating = (rating: string): rating is ReviewRating => {
  return ['1', '2', '3', '4', '5'].includes(rating);
};

export const isValidCountryCode = (country: string): country is CountryCode => {
  return ['us', 'gb', 'ca', 'au', 'de', 'fr', 'jp'].includes(country);
};

export const isAppStoreReview = (obj: any): obj is AppStoreReview => {
  return (
    typeof obj === 'object' &&
    typeof obj.author === 'string' &&
    typeof obj.rating === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.content === 'string' &&
    typeof obj.date === 'string' &&
    typeof obj.version === 'string'
  );
};

export const isAppStoreApp = (obj: any): obj is AppStoreApp => {
  return (
    typeof obj === 'object' &&
    typeof obj.id === 'number' &&
    typeof obj.title === 'string' &&
    typeof obj.developer === 'string' &&
    typeof obj.rating === 'string' &&
    typeof obj.ratingCount === 'number' &&
    typeof obj.price === 'string' &&
    typeof obj.category === 'string' &&
    typeof obj.description === 'string' &&
    typeof obj.appUrl === 'string' &&
    typeof obj.iconUrl === 'string'
  );
};

export const isAppStoreReviewsExport = (obj: any): obj is AppStoreReviewsExport => {
  return (
    typeof obj === 'object' &&
    isAppStoreApp(obj.app) &&
    Array.isArray(obj.reviews) &&
    obj.reviews.every(isAppStoreReview) &&
    typeof obj.exportInfo === 'object'
  );
};
