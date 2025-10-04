/**
 * App Store Reviews - Complete TypeScript Interfaces
 * 
 * Цей файл містить всі необхідні TypeScript інтерфейси для роботи з даними відгуків App Store
 * Базуються на реальних даних з Apple iTunes API та RSS feeds
 * 
 * Використання:
 * import { AppReviewsData, Review, App } from './AppStoreReviewsInterfaces';
 */

// ============================================================================
// ОСНОВНІ ІНТЕРФЕЙСИ
// ============================================================================

/**
 * Інтерфейс для одного відгуку
 */
export interface Review {
  /** Ім'я автора відгуку */
  author: string;
  
  /** Рейтинг від 1 до 5 зірок (як рядок з API) */
  rating: string;
  
  /** Заголовок відгуку */
  title: string;
  
  /** Повний текст відгуку */
  content: string;
  
  /** Дата створення відгуку (ISO рядок) */
  date: string;
  
  /** Версія додатку, для якої написаний відгук */
  version: string;
  
  /** Опціонально: код країни (для експорту з різних країн) */
  country?: string;
  
  /** Опціонально: ID додатку (для мульти-додатків експорту) */
  appId?: number;
  
  /** Опціонально: назва додатку (для мульти-додатків експорту) */
  appName?: string;
}

/**
 * Інтерфейс для інформації про додаток
 */
export interface App {
  /** Унікальний ідентифікатор App Store */
  id: number;
  
  /** Назва додатку */
  title: string;
  
  /** Назва розробника/видавця */
  developer: string;
  
  /** Середній рейтинг користувачів (рядок з API) */
  rating: string;
  
  /** Загальна кількість оцінок користувачів */
  ratingCount: number;
  
  /** Рядок з ціною (наприклад, "Free", "$2.99") */
  price: string;
  
  /** Основна категорія додатку */
  category: string;
  
  /** Повний опис додатку */
  description: string;
  
  /** Пряме посилання на App Store */
  appUrl: string;
  
  /** URL іконки додатку */
  iconUrl: string;
}

/**
 * Інтерфейс для метаданих експорту
 */
export interface ExportMetadata {
  /** Загальна кількість знайдених відгуків */
  totalReviews: number;
  
  /** Кількість фактично експортованих відгуків */
  exportedReviews: number;
  
  /** Дата експорту (ISO рядок) */
  exportDate: string;
  
  /** Код країни для експорту */
  country: string;
  
  /** ID додатку, який було експортовано */
  appId: string;
  
  /** Опціонально: цільова кількість відгуків */
  targetReviews?: number;
  
  /** Опціонально: перевірені країни під час експорту */
  countriesChecked?: string[];
}

/**
 * Головний інтерфейс для експорту відгуків одного додатку
 */
export interface AppReviewsData {
  /** Інформація про додаток */
  app: App;
  
  /** Масив відгуків */
  reviews: Review[];
  
  /** Метадані експорту */
  exportInfo: ExportMetadata;
}

// ============================================================================
// ДОДАТКОВІ ІНТЕРФЕЙСИ ДЛЯ API
// ============================================================================

/**
 * Відповідь iTunes Lookup API
 */
export interface iTunesLookupResponse {
  resultCount: number;
  results: iTunesAppResult[];
}

/**
 * Результат пошуку додатку в iTunes API
 */
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

/**
 * Відповідь RSS feed для відгуків
 */
export interface RSSFeedResponse {
  feed: RSSFeed;
}

/**
 * RSS feed структура
 */
export interface RSSFeed {
  entry: RSSFeedEntry[];
}

/**
 * Запис RSS feed
 */
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

// ============================================================================
// УТИЛІТИ ТА ДОПОМІЖНІ ТИПИ
// ============================================================================

/**
 * Коди країн для App Store
 */
export type CountryCode = 'us' | 'gb' | 'ca' | 'au' | 'de' | 'fr' | 'jp';

/**
 * Опції для експорту
 */
export interface ExportOptions {
  /** ID додатку в App Store */
  appId: string;
  
  /** Код країни для регіону App Store */
  country?: CountryCode;
  
  /** Максимальна кількість відгуків для експорту */
  maxReviews?: number;
  
  /** Чи включати інформацію про додаток */
  includeAppInfo?: boolean;
}

/**
 * Інтерфейс для обробки помилок
 */
export interface AppStoreError {
  error: string;
  details?: string;
  appId?: string;
  country?: string;
}

/**
 * Типи рейтингів
 */
export type ReviewRating = '1' | '2' | '3' | '4' | '5';

/**
 * Категорії додатків
 */
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
  | string; // Дозволяємо інші категорії

// ============================================================================
// TYPE GUARDS ДЛЯ ВАЛІДАЦІЇ
// ============================================================================

/**
 * Перевіряє чи є рядок валідним рейтингом
 */
export const isValidRating = (rating: string): rating is ReviewRating => {
  return ['1', '2', '3', '4', '5'].includes(rating);
};

/**
 * Перевіряє чи є рядок валідним кодом країни
 */
export const isValidCountryCode = (country: string): country is CountryCode => {
  return ['us', 'gb', 'ca', 'au', 'de', 'fr', 'jp'].includes(country);
};

/**
 * Type guard для перевірки відгуку
 */
export const isAppStoreReview = (obj: any): obj is Review => {
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

/**
 * Type guard для перевірки додатку
 */
export const isAppStoreApp = (obj: any): obj is App => {
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

/**
 * Type guard для перевірки повного експорту
 */
export const isAppStoreReviewsExport = (obj: any): obj is AppReviewsData => {
  return (
    typeof obj === 'object' &&
    isAppStoreApp(obj.app) &&
    Array.isArray(obj.reviews) &&
    obj.reviews.every(isAppStoreReview) &&
    typeof obj.exportInfo === 'object'
  );
};

// ============================================================================
// ПРИКЛАДИ ВИКОРИСТАННЯ
// ============================================================================

/**
 * Приклад використання основних інтерфейсів:
 * 
 * import { AppReviewsData, Review, App } from './AppStoreReviewsInterfaces';
 * 
 * // Завантаження даних
 * const reviewsData: AppReviewsData = await fetchAppReviews('6450840109');
 * 
 * // Робота з додатком
 * const app: App = reviewsData.app;
 * console.log(`App: ${app.title} by ${app.developer}`);
 * 
 * // Робота з відгуками
 * const reviews: Review[] = reviewsData.reviews;
 * const firstReview: Review = reviews[0];
 * console.log(`First review: ${firstReview.title} by ${firstReview.author}`);
 * 
 * // Фільтрація відгуків
 * const highRatedReviews = reviews.filter(review => parseInt(review.rating) >= 4);
 * 
 * // Валідація даних
 * if (isAppStoreReviewsExport(data)) {
 *   // data тепер типізований як AppReviewsData
 *   console.log(`Found ${data.reviews.length} reviews`);
 * }
 */

/**
 * Приклад структури даних (Liven app ID: 6450840109):
 * 
 * {
 *   "app": {
 *     "id": 6450840109,
 *     "title": "Liven: Discover yourself",
 *     "developer": "Chesmint limited",
 *     "rating": "4.41493",
 *     "ratingCount": 25035,
 *     "price": "Free",
 *     "category": "Health & Fitness",
 *     "description": "Liven is your self-discovery companion...",
 *     "appUrl": "https://apps.apple.com/us/app/liven-discover-yourself/id6450840109",
 *     "iconUrl": "https://is1-ssl.mzstatic.com/image/thumb/..."
 *   },
 *   "reviews": [
 *     {
 *       "author": "katanitaadl20375",
 *       "rating": "1",
 *       "title": "App would not load",
 *       "content": "I paid the 20 dollars for the app...",
 *       "date": "2025-10-02T19:08:57-07:00",
 *       "version": "1.77.0"
 *     }
 *   ],
 *   "exportInfo": {
 *     "totalReviews": 49,
 *     "exportedReviews": 49,
 *     "exportDate": "2025-10-04T11:04:49.224Z",
 *     "country": "us",
 *     "appId": "6450840109"
 *   }
 * }
 */
