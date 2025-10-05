#!/bin/bash

# Test Reddit API Script
# Usage: ./test_reddit.sh

# Set your Reddit API credentials here
export REDDIT_CLIENT_ID="Ao_QStxK9p0cS5875yH6Ag"
export REDDIT_CLIENT_SECRET="-Y65zQvx1EBPy9rIzUX0_TYRi5Z_Yw"
export REDDIT_USER_AGENT="Brand Monitor Test Script v1.0"

echo "🧪 Testing Reddit API"
echo "===================="
echo ""

# Check if credentials are set
if [ "$REDDIT_CLIENT_ID" = "your_client_id_here" ]; then
    echo "❌ Please set your Reddit API credentials in this script"
    echo ""
    echo "To get Reddit API credentials:"
    echo "1. Go to https://www.reddit.com/prefs/apps"
    echo "2. Click 'create app' or 'create another app'"
    echo "3. Select 'script' as app type"
    echo "4. Fill in the form:"
    echo "   - name: Brand Monitor"
    echo "   - redirect uri: http://localhost:8080"
    echo "5. Copy the client ID and secret to this script"
    echo ""
    exit 1
fi

# Install PRAW if not already installed
echo "📦 Checking dependencies..."
pip install -q praw

echo ""
echo "🔍 Running tests..."
echo ""

# Test 1: Search for Tesla mentions (last 30 days, 20 posts)
echo "Test 1: Tesla mentions"
python3 test_reddit.py --brand "Tesla" --limit 20 --days 30 --sort new --quiet

echo ""
echo "---"
echo ""

# Test 2: Search for Apple mentions (last 7 days, 10 posts, save to file)
echo "Test 2: Apple mentions (saving to JSON)"
python3 test_reddit.py --brand "Apple" --limit 10 --days 7 --sort hot --save --quiet

echo ""
echo "---"
echo ""

# Test 3: Show detailed output for a brand
echo "Test 3: Nike mentions (detailed output)"
python3 test_reddit.py --brand "Nike" --limit 5 --days 30 --sort top

echo ""
echo "✅ All tests completed!"

