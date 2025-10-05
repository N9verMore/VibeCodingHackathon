const CHAT_API_URL = 'http://10.8.0.5:8000/api/chat';

export const sendChatMessage = async (message) => {
  try {
    if (!message || !message.trim()) {
      throw new Error('Message cannot be empty');
    }

    const response = await fetch(CHAT_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        message: message.trim() 
      }),
      next: { revalidate: 0 } // Don't cache chat responses
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Check if the response contains an error
    if (data.error) {
      throw new Error(data.message || 'Failed to get AI response');
    }

    return {
      success: true,
      insight: data.answer || data.insight || data.response || data.message || 'No response received',
      timestamp: new Date().toISOString()
    };

  } catch (error) {
    console.error('Failed to send chat message:', error);
    return {
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
};

export const generateInsight = async (context = '') => {
  const defaultMessage = context 
    ? `Based on the current analytics data, provide insights about: ${context}`
    : 'Provide insights about the current reputation and sentiment trends';

  return await sendChatMessage(defaultMessage);
};
