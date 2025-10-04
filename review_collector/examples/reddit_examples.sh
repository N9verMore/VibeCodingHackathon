#!/bin/bash

# Reddit Collector API Examples
# Demonstrates various ways to collect Reddit posts

# Set your API Gateway URL
API_URL="${API_URL:-https://your-api-id.execute-api.us-east-1.amazonaws.com/prod}"

echo "🧪 Reddit Collector API Examples"
echo "================================="
echo ""
echo "API URL: $API_URL"
echo ""

# Example 1: Basic Reddit collection
echo "📌 Example 1: Collect Reddit posts for Flo app"
echo "---"
curl -X POST "$API_URL/collect-reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Flo",
    "keywords": "Flo app",
    "limit": 50,
    "days_back": 30
  }'
echo ""
echo ""

# Example 2: Custom keywords
echo "📌 Example 2: Collect with custom keywords"
echo "---"
curl -X POST "$API_URL/collect-reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Flo",
    "keywords": "Flo Health",
    "limit": 100,
    "days_back": 30,
    "sort": "relevance"
  }'
echo ""
echo ""

# Example 3: Short time range
echo "📌 Example 3: Collect recent posts (last 7 days)"
echo "---"
curl -X POST "$API_URL/collect-reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Flo",
    "keywords": "Flo app",
    "limit": 20,
    "days_back": 7,
    "sort": "new"
  }'
echo ""
echo ""

# Example 4: Top posts
echo "📌 Example 4: Collect top-rated posts"
echo "---"
curl -X POST "$API_URL/collect-reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Flo",
    "keywords": "Flo app",
    "limit": 30,
    "days_back": 30,
    "sort": "top"
  }'
echo ""
echo ""

# Example 5: With job_id (for orchestration)
echo "📌 Example 5: Collect with job_id"
echo "---"
curl -X POST "$API_URL/collect-reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Flo",
    "keywords": "Flo app",
    "limit": 50,
    "days_back": 30,
    "job_id": "job_20251005_test123"
  }'
echo ""
echo ""

# Example 6: Different brand (Nike)
echo "📌 Example 6: Collect for different brand (Nike)"
echo "---"
curl -X POST "$API_URL/collect-reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Nike",
    "keywords": "Nike",
    "limit": 50,
    "days_back": 30,
    "sort": "hot"
  }'
echo ""
echo ""

echo "✅ Examples completed!"
echo ""
echo "📝 Notes:"
echo "- 'keywords' field is used for searching Reddit"
echo "- 'brand' field is used for storage in DynamoDB"
echo "- All Reddit posts have rating=-1 (no star rating)"
echo "- Posts are stored in ReviewsTableV2 with source='reddit'"

