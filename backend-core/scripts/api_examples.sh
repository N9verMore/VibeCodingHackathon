#!/bin/bash
# API Examples для BrandPulse
# Використання: bash scripts/api_examples.sh

API_URL="http://localhost:8000"

echo "🚀 BrandPulse API Examples"
echo "================================"

# 1. Health Check
echo -e "\n1️⃣ Health Check"
curl -s $API_URL/ | jq '.'

# 2. Get Statistics
echo -e "\n2️⃣ Get Statistics"
curl -s $API_URL/api/statistics | jq '.total_mentions, .sentiment_distribution, .reputation_score.overall_score'

# 3. Get Reputation Score
echo -e "\n3️⃣ Reputation Score"
curl -s $API_URL/api/reputation-score | jq '.'

# 4. Check Crisis
echo -e "\n4️⃣ Crisis Detection"
curl -s $API_URL/api/crisis/check | jq '.'

# 5. Add Comment
echo -e "\n5️⃣ Add Comment"
curl -s -X POST $API_URL/api/comments \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Чудова якість продукту!",
    "timestamp": "2025-10-04T15:00:00",
    "rating": 5.0,
    "platform": "trustpilot",
    "sentiment": "positive",
    "category": "quality",
    "llm_description": "Користувач хвалить якість"
  }' | jq '.'

# 6. Search Comments
echo -e "\n6️⃣ Search Comments"
curl -s "$API_URL/api/search/comments?query=якість&limit=5" | jq '.results | length'

# 7. Chat Query
echo -e "\n7️⃣ Chat with AI"
curl -s -X POST $API_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Які найпоширеніші проблеми з брендом?"
  }' | jq '.answer'

echo -e "\n================================"
echo "✅ All examples completed!"
