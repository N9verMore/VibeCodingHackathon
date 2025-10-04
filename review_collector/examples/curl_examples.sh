#!/bin/bash
###############################################################################
# cURL Examples for Review Collector API
#
# This file contains ready-to-use curl commands for testing the API.
# Replace YOUR_API_URL with your actual API Gateway endpoint.
###############################################################################

# Base URL (update with your actual endpoint)
API_URL="https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod"

echo "=========================================="
echo "Review Collector API - cURL Examples"
echo "=========================================="
echo ""

# Example 1: Trustpilot (DataForSEO)
echo "1. Trustpilot - Zara (40 reviews)"
echo "-----------------------------------"
cat << 'EOF'
curl -X POST "${API_URL}/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "trustpilot",
    "app_identifier": "www.zara.com",
    "brand": "zara",
    "limit": 40
  }'
EOF
echo ""
echo ""

# Example 2: Trustpilot - Tesla
echo "2. Trustpilot - Tesla (20 reviews)"
echo "-----------------------------------"
cat << 'EOF'
curl -X POST "${API_URL}/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "trustpilot",
    "app_identifier": "www.tesla.com",
    "brand": "tesla",
    "limit": 20
  }'
EOF
echo ""
echo ""

# Example 3: Trustpilot - Booking.com
echo "3. Trustpilot - Booking.com (50 reviews)"
echo "-----------------------------------------"
cat << 'EOF'
curl -X POST "${API_URL}/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "trustpilot",
    "app_identifier": "www.booking.com",
    "brand": "booking",
    "limit": 50
  }'
EOF
echo ""
echo ""

# Example 4: App Store (SerpAPI)
echo "4. App Store - Telegram (100 reviews)"
echo "--------------------------------------"
cat << 'EOF'
curl -X POST "${API_URL}/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 100
  }'
EOF
echo ""
echo ""

# Example 5: Google Play (SerpAPI)
echo "5. Google Play - Telegram (100 reviews)"
echo "----------------------------------------"
cat << 'EOF'
curl -X POST "${API_URL}/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "googleplay",
    "app_identifier": "org.telegram.messenger",
    "brand": "telegram",
    "limit": 100
  }'
EOF
echo ""
echo ""

# Example 6: Pretty output with jq
echo "6. With pretty JSON output (requires jq)"
echo "-----------------------------------------"
cat << 'EOF'
curl -X POST "${API_URL}/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "trustpilot",
    "app_identifier": "www.zara.com",
    "brand": "zara",
    "limit": 10
  }' | jq
EOF
echo ""
echo ""

# Example 7: Save response to file
echo "7. Save response to file"
echo "------------------------"
cat << 'EOF'
curl -X POST "${API_URL}/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "trustpilot",
    "app_identifier": "www.nike.com",
    "brand": "nike",
    "limit": 20
  }' -o response.json

cat response.json | jq
EOF
echo ""
echo ""

echo "=========================================="
echo "💡 Tips:"
echo "=========================================="
echo "1. Replace \${API_URL} with your actual endpoint"
echo "2. Install jq for pretty JSON output: brew install jq"
echo "3. Trustpilot requests take 5-15 seconds (async)"
echo "4. App Store/Google Play requests take 1-2 seconds"
echo ""

