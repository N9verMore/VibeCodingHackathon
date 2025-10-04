'use client';

import { useState } from 'react';
import AppDetails from './components/AppDetails';

export default function Home() {
  const [appId, setAppId] = useState('');
  const [country, setCountry] = useState('us');
  const [appData, setAppData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!appId.trim()) return;

    setLoading(true);
    setError('');
    setAppData(null);

    try {
      const response = await fetch(`/api/reviews?appId=${encodeURIComponent(appId)}&country=${country}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch app data');
      }

      setAppData(data.app);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            App Store Reviews Parser
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Enter an App ID to get real reviews from the App Store
          </p>
        </header>

        <div className="max-w-2xl mx-auto mb-8">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="flex gap-4">
              <input
                type="text"
                value={appId}
                onChange={(e) => setAppId(e.target.value)}
                placeholder="Enter App ID (e.g., 6450840109)"
                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                disabled={loading}
              />
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                disabled={loading}
              >
                <option value="us">US</option>
                <option value="gb">UK</option>
                <option value="ca">Canada</option>
                <option value="au">Australia</option>
                <option value="de">Germany</option>
                <option value="fr">France</option>
                <option value="jp">Japan</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={loading || !appId.trim()}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Fetching...' : 'Get App Reviews'}
            </button>
          </form>
          
          <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
            <p><strong>Example App IDs:</strong></p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>6450840109 - Spotify</li>
              <li>389801252 - Instagram</li>
              <li>310633997 - WhatsApp</li>
              <li>544007664 - YouTube</li>
            </ul>
          </div>
        </div>

        {error && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          </div>
        )}

        {loading && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <p className="text-blue-800 dark:text-blue-200 text-center">
                Fetching app data and reviews for ID: {appId}...
              </p>
            </div>
          </div>
        )}

        {appData && <AppDetails app={appData} />}
      </div>
    </div>
  );
}
