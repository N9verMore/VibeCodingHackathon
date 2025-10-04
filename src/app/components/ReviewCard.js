export default function ReviewCard({ review }) {
  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const renderStars = (rating) => {
    const numRating = parseInt(rating);
    if (isNaN(numRating)) return null;
    
    return (
      <div className="flex items-center">
        {[...Array(5)].map((_, i) => (
          <span
            key={i}
            className={`text-lg ${
              i < numRating 
                ? 'text-yellow-400' 
                : 'text-gray-300 dark:text-gray-600'
            }`}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h5 className="font-medium text-gray-900 dark:text-white">
              {review.author}
            </h5>
            {review.rating && review.rating !== 'N/A' && (
              <div className="flex items-center gap-1">
                {renderStars(review.rating)}
                <span className="text-sm text-gray-600 dark:text-gray-300 ml-1">
                  ({review.rating}/5)
                </span>
              </div>
            )}
          </div>
          
          {review.title && review.title !== 'No title' && (
            <h6 className="font-medium text-gray-800 dark:text-gray-200 mb-2">
              {review.title}
            </h6>
          )}
        </div>
        
        <div className="text-right">
          {review.date && (
            <span className="text-sm text-gray-500 dark:text-gray-400 block">
              {formatDate(review.date)}
            </span>
          )}
          {review.version && review.version !== 'N/A' && (
            <span className="text-xs text-gray-400 dark:text-gray-500">
              v{review.version}
            </span>
          )}
        </div>
      </div>
      
      <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
        {review.content}
      </p>
    </div>
  );
}
