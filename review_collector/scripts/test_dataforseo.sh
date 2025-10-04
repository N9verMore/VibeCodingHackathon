#!/bin/bash
###############################################################################
# DataForSEO Trustpilot API Test Script
#
# Quick test script for DataForSEO integration.
# Tests fetching reviews from Trustpilot using DataForSEO API.
#
# Usage:
#   ./scripts/test_dataforseo.sh
#
# Environment Variables (optional):
#   DATAFORSEO_LOGIN    - DataForSEO login (default: mglushko@perfsys.com)
#   DATAFORSEO_PASSWORD - DataForSEO password (default: cd0bdc42c24cad76)
###############################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default credentials
DEFAULT_LOGIN="mglushko@perfsys.com"
DEFAULT_PASSWORD="cd0bdc42c24cad76"

# Use env vars or defaults
LOGIN="${DATAFORSEO_LOGIN:-$DEFAULT_LOGIN}"
PASSWORD="${DATAFORSEO_PASSWORD:-$DEFAULT_PASSWORD}"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  DataForSEO Trustpilot API Test${NC}"
echo -e "${BLUE}============================================================${NC}"

# Check if python script exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_SCRIPT="$SCRIPT_DIR/test_dataforseo.py"

if [ ! -f "$TEST_SCRIPT" ]; then
    echo -e "${RED}❌ Error: test_dataforseo.py not found${NC}"
    exit 1
fi

# Test cases
declare -a TEST_CASES=(
    "www.zara.com:zara:20"
    "www.tesla.com:tesla:10"
    "www.booking.com:booking:15"
)

echo ""
echo -e "${GREEN}🧪 Running test cases...${NC}"
echo ""

# Run tests
for test_case in "${TEST_CASES[@]}"; do
    IFS=':' read -r domain brand limit <<< "$test_case"
    
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Testing: ${domain} (${brand})${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    export DATAFORSEO_LOGIN="$LOGIN"
    export DATAFORSEO_PASSWORD="$PASSWORD"
    
    # Run test
    if python3 "$TEST_SCRIPT" \
        --domain "$domain" \
        --brand "$brand" \
        --limit "$limit"; then
        echo -e "${GREEN}✅ Test passed for ${domain}${NC}"
    else
        echo -e "${RED}❌ Test failed for ${domain}${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}Waiting 3 seconds before next test...${NC}"
    sleep 3
    echo ""
done

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}✅ All tests completed!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}💡 Tip: You can also run individual tests:${NC}"
echo -e "   python3 scripts/test_dataforseo.py --domain www.zara.com --brand zara --limit 40"
echo ""

