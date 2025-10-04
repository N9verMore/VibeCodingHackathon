#!/bin/bash
#
# Manual Review Collection Trigger
# 
# Provides interactive menu for triggering review collection
# via AWS Lambda direct invoke.
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
LAMBDA_FUNCTION="serpapi-collector-lambda"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Review Collector - Manual Trigger${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to collect reviews
collect_reviews() {
    local source=$1
    local app_id=$2
    local brand=$3
    local limit=${4:-100}
    
    echo -e "${YELLOW}Collecting reviews...${NC}"
    echo -e "  Source: ${source}"
    echo -e "  App ID: ${app_id}"
    echo -e "  Brand: ${brand}"
    echo -e "  Limit: ${limit}"
    echo ""
    
    # Create payload
    payload=$(cat <<EOF
{
    "source": "${source}",
    "app_identifier": "${app_id}",
    "brand": "${brand}",
    "limit": ${limit}
}
EOF
)
    
    # Invoke Lambda
    aws lambda invoke \
        --function-name "${LAMBDA_FUNCTION}" \
        --region "${REGION}" \
        --payload "${payload}" \
        --cli-binary-format raw-in-base64-out \
        /tmp/review-collector-response.json \
        > /dev/null
    
    # Check response
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Lambda invoked successfully${NC}"
        echo ""
        echo -e "${BLUE}Response:${NC}"
        cat /tmp/review-collector-response.json | jq '.'
        
        # Extract statistics
        saved=$(cat /tmp/review-collector-response.json | jq -r '.body' | jq -r '.statistics.saved // 0')
        if [ "$saved" != "null" ] && [ "$saved" != "0" ]; then
            echo ""
            echo -e "${GREEN}✓ Collected ${saved} reviews successfully!${NC}"
        fi
    else
        echo -e "${RED}✗ Lambda invocation failed${NC}"
        exit 1
    fi
}

# Menu
echo "Select app to collect reviews:"
echo ""
echo "1) Telegram (App Store)"
echo "2) WhatsApp (Google Play)"  
echo "3) Instagram (App Store)"
echo "4) Custom app"
echo "5) Exit"
echo ""
read -p "Choose option (1-5): " option

case $option in
    1)
        echo ""
        collect_reviews "appstore" "544007664" "telegram" 50
        ;;
    2)
        echo ""
        collect_reviews "googleplay" "com.whatsapp" "whatsapp" 50
        ;;
    3)
        echo ""
        collect_reviews "appstore" "389801252" "instagram" 50
        ;;
    4)
        echo ""
        read -p "Source (appstore/googleplay/trustpilot): " source
        read -p "App Identifier: " app_id
        read -p "Brand: " brand
        read -p "Limit (default 100): " limit
        echo ""
        collect_reviews "$source" "$app_id" "$brand" "${limit:-100}"
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Done!${NC}"
echo -e "${BLUE}========================================${NC}"

