#!/bin/bash

# News Collection Examples
# NewsAPI Integration

# Set your API endpoint
API_URL="https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-news"

echo "=========================================="
echo "NewsAPI Collection Examples"
echo "=========================================="
echo ""

# Example 1: Search news about Tesla
echo "1. Search news about Tesla (last 100 articles)..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Tesla",
    "limit": 100,
    "search_type": "everything",
    "language": "en"
  }'
echo -e "\n\n"

# Example 2: News about Apple from specific date range
echo "2. Apple news from Oct 1-4, 2025..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Apple",
    "limit": 50,
    "search_type": "everything",
    "from_date": "2025-10-01",
    "to_date": "2025-10-04",
    "language": "en"
  }'
echo -e "\n\n"

# Example 3: Top technology headlines in US
echo "3. Top technology headlines in US..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "technology",
    "limit": 20,
    "search_type": "top-headlines",
    "country": "us",
    "category": "technology"
  }'
echo -e "\n\n"

# Example 4: News from specific sources
echo "4. Tech news from BBC and CNN..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "artificial intelligence",
    "limit": 30,
    "search_type": "top-headlines",
    "sources": "bbc-news,cnn"
  }'
echo -e "\n\n"

# Example 5: AI/ML news
echo "5. Artificial Intelligence news..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "artificial intelligence",
    "limit": 100,
    "search_type": "everything",
    "language": "en"
  }'
echo -e "\n\n"

# Example 6: Cryptocurrency news
echo "6. Cryptocurrency news..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "cryptocurrency",
    "limit": 50,
    "search_type": "everything",
    "language": "en"
  }'
echo -e "\n\n"

# Example 7: Business headlines
echo "7. Top business headlines..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "business",
    "limit": 50,
    "search_type": "top-headlines",
    "country": "us",
    "category": "business"
  }'
echo -e "\n\n"

# Example 8: Electric vehicles news
echo "8. Electric vehicles news..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "electric vehicles",
    "limit": 75,
    "search_type": "everything",
    "language": "en",
    "from_date": "2025-09-01"
  }'
echo -e "\n\n"

echo "=========================================="
echo "Examples completed!"
echo "=========================================="

