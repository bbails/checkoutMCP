#!/bin/bash

# Test script for MCP API Server
# Tests the FastAPI HTTP wrapper for MCP server

API_URL="http://localhost:8001"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  MCP API Server Test Suite${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Test 1: Health check
echo -e "${BLUE}[Test 1] Health Check${NC}"
curl -s $API_URL/health | jq '.'
echo ""

# Test 2: MCP Initialize
echo -e "${BLUE}[Test 2] MCP Initialize${NC}"
curl -s -X POST $API_URL/mcp/initialize | jq '.'
echo ""

# Test 3: List MCP Tools
echo -e "${BLUE}[Test 3] List MCP Tools${NC}"
curl -s $API_URL/mcp/tools/list | jq '.tools[] | {name: .name, description: .description}'
echo ""

# Test 4: Call MCP Tool - Tokenize
echo -e "${BLUE}[Test 4] Call MCP Tool - Tokenize Card${NC}"
TOKEN_RESULT=$(curl -s -X POST $API_URL/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tokenize_payment_card",
    "arguments": {
      "card_number": "4532015112830366",
      "card_holder": "John Doe",
      "expiry_month": 12,
      "expiry_year": 2025,
      "cvv": "123",
      "customer_email": "john@example.com",
      "billing_street": "123 Main St",
      "billing_city": "New York",
      "billing_state": "NY",
      "billing_zip": "10001"
    }
  }')

echo "$TOKEN_RESULT" | jq '.'
TOKEN=$(echo "$TOKEN_RESULT" | jq -r '.content[0].text' | jq -r '.token')
echo -e "\n${GREEN}✓ Token: $TOKEN${NC}\n"

# Test 5: Direct API - Process Payment
echo -e "${BLUE}[Test 5] Direct API - Process Payment${NC}"
curl -s -X POST "$API_URL/tools/process-payment?token=$TOKEN&amount=99.99&customer_id=cust_test&description=Test+payment" | jq '.'
echo ""

# Test 6: Direct API - Get Customer Transactions
echo -e "${BLUE}[Test 6] Direct API - Get Customer Transactions${NC}"
curl -s "$API_URL/tools/customer/cust_test/transactions" | jq '.'
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All Tests Completed!${NC}"
echo -e "${GREEN}========================================${NC}"
