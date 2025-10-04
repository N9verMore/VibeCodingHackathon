import ReviewCard from './ReviewCard';

export default function ReviewList({ reviews }) {
  if (!reviews || reviews.length === 0) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-center">
          <p className="text-gray-500 dark:text-gray-400">No reviews found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Found {reviews.length} app{reviews.length !== 1 ? 's' : ''}
      </h2>
      
      <div className="space-y-6">
        {reviews.map((app, index) => (
          <div key={index} className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                    {app.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    by {app.developer}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-medium text-gray-900 dark:text-white">
                    {app.rating}
                  </div>
                  {app.appUrl !== '#' && (
                    <a
                      href={app.appUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                    >
                      View on App Store
                    </a>
                  )}
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Reviews ({app.reviews?.length || 0})
              </h4>
              
              {app.reviews && app.reviews.length > 0 ? (
                <div className="space-y-4">
                  {app.reviews.map((review, reviewIndex) => (
                    <ReviewCard key={reviewIndex} review={review} />
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 dark:text-gray-400 italic">
                  No reviews available for this app.
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
