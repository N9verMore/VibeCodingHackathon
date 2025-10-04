import ReviewCard from './ReviewCard';

export default function AppDetails({ app }) {
  if (!app) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-center">
          <p className="text-gray-500 dark:text-gray-400">No app data available.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-start gap-6">
            {app.iconUrl && (
              <img
                src={app.iconUrl}
                alt={`${app.title} icon`}
                className="w-20 h-20 rounded-lg shadow-sm"
              />
            )}
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {app.title}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 mb-3">
                by {app.developer}
              </p>
              
              <div className="flex flex-wrap gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-700 dark:text-gray-300">Rating:</span>
                  <div className="flex items-center">
                    <span className="text-yellow-400 text-lg">★</span>
                    <span className="ml-1 font-medium text-gray-900 dark:text-white">
                      {app.rating}
                    </span>
                    <span className="ml-1 text-gray-500 dark:text-gray-400">
                      ({app.ratingCount.toLocaleString()} ratings)
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-700 dark:text-gray-300">Price:</span>
                  <span className="text-gray-900 dark:text-white">{app.price}</span>
                </div>
                
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-700 dark:text-gray-300">Category:</span>
                  <span className="text-gray-900 dark:text-white">{app.category}</span>
                </div>
              </div>
              
              {app.appUrl && (
                <div className="mt-4">
                  <a
                    href={app.appUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    View on App Store
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {app.description && (
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Description
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              {app.description.length > 500 
                ? `${app.description.substring(0, 500)}...` 
                : app.description
              }
            </p>
          </div>
        )}
        
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Customer Reviews ({app.reviews?.length || 0})
          </h3>
          
          {app.reviews && app.reviews.length > 0 ? (
            <div className="space-y-4">
              {app.reviews.map((review, index) => (
                <ReviewCard key={index} review={review} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 dark:text-gray-400">
                No reviews available for this app.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
