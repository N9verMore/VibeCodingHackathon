/**
 * Parses comment text to extract additional fields like "Опис:" (Description)
 * 
 * Example usage:
 * Input: "Zara schuldet mir bereits mehr als 500€ Diese Betrüger!!!!! Опис: Проблеми з отриманням рахунків після повернення товару."
 * Output: {
 *   content: "Zara schuldet mir bereits mehr als 500€ Diese Betrüger!!!!!",
 *   description: "Проблеми з отриманням рахунків після повернення товару.",
 *   originalText: "Zara schuldet mir bereits mehr als 500€ Diese Betrüger!!!!! Опис: Проблеми з отриманням рахунків після повернення товару."
 * }
 * 
 * @param {string} text - The original comment text
 * @returns {object} - Object with parsed content and extracted fields
 */
function parseCommentText(text) {
  if (!text || typeof text !== 'string') {
    return {
      content: text || '',
      description: null,
      originalText: text || ''
    };
  }

  // Pattern to match "Опис:" followed by text until end of string
  const opisPattern = /\s*Опис:\s*(.+)$/i;
  const match = text.match(opisPattern);

  if (match) {
    // Extract the description part
    const description = match[1].trim();
    
    // Remove the "Опис:" part from the original text to get clean content
    const content = text.replace(opisPattern, '').trim();
    
    return {
      content: content,
      description: description,
      originalText: text
    };
  }

  // No "Опис:" field found, return original text as content
  return {
    content: text,
    description: null,
    originalText: text
  };
}

/**
 * Enhanced parser that can handle multiple additional fields
 * @param {string} text - The original comment text
 * @returns {object} - Object with parsed content and extracted fields
 */
function parseCommentTextAdvanced(text) {
  if (!text || typeof text !== 'string') {
    return {
      content: text || '',
      additionalFields: {},
      originalText: text || ''
    };
  }

  const additionalFields = {};
  let cleanContent = text;

  // Pattern for "Опис:" (Description in Ukrainian)
  const opisPattern = /\s*Опис:\s*(.+?)(?=\s*[А-ЯЁ][а-яё]+:|$)/i;
  const opisMatch = text.match(opisPattern);
  
  if (opisMatch) {
    additionalFields.description = opisMatch[1].trim();
    cleanContent = cleanContent.replace(opisPattern, '').trim();
  }

  // Pattern for other potential fields (can be extended)
  const otherFieldPatterns = [
    { key: 'category', pattern: /\s*Категорія:\s*(.+?)(?=\s*[А-ЯЁ][а-яё]+:|$)/i },
    { key: 'priority', pattern: /\s*Пріоритет:\s*(.+?)(?=\s*[А-ЯЁ][а-яё]+:|$)/i },
    { key: 'status', pattern: /\s*Статус:\s*(.+?)(?=\s*[А-ЯЁ][а-яё]+:|$)/i }
  ];

  otherFieldPatterns.forEach(({ key, pattern }) => {
    const match = text.match(pattern);
    if (match) {
      additionalFields[key] = match[1].trim();
      cleanContent = cleanContent.replace(pattern, '').trim();
    }
  });

  return {
    content: cleanContent,
    additionalFields: additionalFields,
    originalText: text
  };
}

module.exports = {
  parseCommentText,
  parseCommentTextAdvanced
};
