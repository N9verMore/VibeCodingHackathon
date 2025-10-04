export const formatMarkdown = (text) => {
  if (!text) return '';
  
  return text
    // Bold text: **text** -> <strong>text</strong>
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic text: *text* -> <em>text</em>
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Headers: # Header -> <h1>Header</h1>
    .replace(/^# (.*?)$/gm, '<h1 class="font-bold text-xl mt-4 mb-3">$1</h1>')
    // Subheaders: ## Subheader -> <h2>Subheader</h2>
    .replace(/^## (.*?)$/gm, '<h2 class="font-bold text-lg mt-3 mb-2">$1</h2>')
    // Sub-subheaders: ### Sub-subheader -> <h3>Sub-subheader</h3>
    .replace(/^### (.*?)$/gm, '<h3 class="font-bold text-base mt-2 mb-1">$1</h3>')
    // Lists: - item -> <li>item</li>
    .replace(/^- (.*?)$/gm, '<li class="ml-4">$1</li>')
    // Numbered lists: 1. item -> <li>item</li>
    .replace(/^\d+\. (.*?)$/gm, '<li class="ml-4">$1</li>')
    // Line breaks: \n\n -> <br><br>
    .replace(/\n\n/g, '<br><br>')
    // Single line breaks: \n -> <br>
    .replace(/\n/g, '<br>');
};

export const createMarkdownHTML = (text) => {
  return {
    __html: formatMarkdown(text)
  };
};
