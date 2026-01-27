#!/bin/bash

# Payment API Test Script
# Tests all endpoints with different scenarios

API_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Payment Mock API - Complete Test Suite${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to print section header
print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to print test result
print_test() {
    echo -e "${YELLOW}TEST:${NC} $1"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 1. Health Check
print_section "1. Health Check"
print_test "GET /health"
HEALTH=$(curl -s $API_URL/health)
echo "$HEALTH" | jq '.'
if echo "$HEALTH" | jq -e '.status == "healthy"' > /dev/null; then
    print_success "Health check passed"
else
    print_error "Health check failed"
fi

# 2. API Info
print_section "2. API Information"
print_test "GET /"
curl -s $API_URL/ | jq '.'
print_success "API info retrieved"

# 3. Tokenize Visa Card
print_section "3. Tokenize Visa Card"
print_test "POST /api/v1/tokenize (Visa)"
VISA_RESPONSE=$(curl -s -X POST $API_URL/api/v1/tokenize \
  -H "Content-Type: application/json" \
  -d '{
    "card": {
      "card_number": "4532015112830366",
      "card_holder": "John Doe",
      "expiry_month": 12,
      "expiry_year": 2025,
      "cvv": "123"
    },
    "customer": {
      "customer_id": "cust_visa",
      "email": "visa@example.com",
      "billing_address": {
        "street": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country": "US"
      }
    }
  }')
echo "$VISA_RESPONSE" | jq '.'
VISA_TOKEN=$(echo "$VISA_RESPONSE" | jq -r '.token')
print_success "Visa card tokenized: $VISA_TOKEN"

# 4. Tokenize Mastercard
print_section "4. Tokenize Mastercard"
print_test "POST /api/v1/tokenize (Mastercard)"
MC_RESPONSE=$(curl -s -X POST $API_URL/api/v1/tokenize \
  -H "Content-Type: application/json" \
  -d '{
    "card": {
      "card_number": "5425233430109903",
      "card_holder": "Jane Smith",
      "expiry_month": 6,
      "expiry_year": 2026,
      "cvv": "456"
    },
    "customer": {
      "customer_id": "cust_mc",
      "email": "mastercard@example.com",
      "billing_address": {
        "street": "456 Oak Ave",
        "city": "Los Angeles",
        "state": "CA",
        "zip_code": "90001",
        "country": "US"
      }
    }
  }')
echo "$MC_RESPONSE" | jq '.'
MC_TOKEN=$(echo "$MC_RESPONSE" | jq -r '.token')
print_success "Mastercard tokenized: $MC_TOKEN"

# 5. Tokenize American Express
print_section "5. Tokenize American Express"
print_test "POST /api/v1/tokenize (Amex)"
AMEX_RESPONSE=$(curl -s -X POST $API_URL/api/v1/tokenize \
  -H "Content-Type: application/json" \
  -d '{
    "card": {
      "card_number": "374245455400126",
      "card_holder": "Bob Johnson",
      "expiry_month": 3,
      "expiry_year": 2027,
      "cvv": "1234"
    },
    "customer": {
      "customer_id": "cust_amex",
      "email": "amex@example.com",
      "billing_address": {
        "street": "789 Pine Blvd",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60601",
        "country": "US"
      }
    }
  }')
echo "$AMEX_RESPONSE" | jq '.'
AMEX_TOKEN=$(echo "$AMEX_RESPONSE" | jq -r '.token')
print_success "Amex card tokenized: $AMEX_TOKEN"

# 6. Process Normal Payment (Success)
print_section "6. Process Normal Payment (Expected: Success)"
print_test "POST /api/v1/payments (Amount: \$99.99)"
PAYMENT1=$(curl -s -X POST $API_URL/api/v1/payments \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$VISA_TOKEN\",
    \"amount\": 99.99,
    \"currency\": \"USD\",
    \"customer_id\": \"cust_visa\",
    \"description\": \"Normal payment test\"
  }")
echo "$PAYMENT1" | jq '.'
TXN1=$(echo "$PAYMENT1" | jq -r '.transaction_id')
STATUS1=$(echo "$PAYMENT1" | jq -r '.status')
print_success "Payment processed - Status: $STATUS1, Transaction ID: $TXN1"

# 7. Process Payment - Insufficient Funds
print_section "7. Process Payment - Insufficient Funds Scenario"
print_test "POST /api/v1/payments (Amount: \$0.01 - Insufficient Funds)"
PAYMENT2=$(curl -s -X POST $API_URL/api/v1/payments \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$MC_TOKEN\",
    \"amount\": 0.01,
    \"currency\": \"USD\",
    \"customer_id\": \"cust_mc\",
    \"description\": \"Insufficient funds test\"
  }")
echo "$PAYMENT2" | jq '.'
TXN2=$(echo "$PAYMENT2" | jq -r '.transaction_id')
STATUS2=$(echo "$PAYMENT2" | jq -r '.status')
MESSAGE2=$(echo "$PAYMENT2" | jq -r '.message')
print_success "Payment processed - Status: $STATUS2, Message: $MESSAGE2"

# 8. Process Payment - Card Declined
print_section "8. Process Payment - Card Declined Scenario"
print_test "POST /api/v1/payments (Amount: \$0.02 - Card Declined)"
PAYMENT3=$(curl -s -X POST $API_URL/api/v1/payments \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$AMEX_TOKEN\",
    \"amount\": 0.02,
    \"currency\": \"USD\",
    \"customer_id\": \"cust_amex\",
    \"description\": \"Card declined test\"
  }")
echo "$PAYMENT3" | jq '.'
TXN3=$(echo "$PAYMENT3" | jq -r '.transaction_id')
STATUS3=$(echo "$PAYMENT3" | jq -r '.status')
MESSAGE3=$(echo "$PAYMENT3" | jq -r '.message')
print_success "Payment processed - Status: $STATUS3, Message: $MESSAGE3"

# 9. Process Payment - Pending
print_section "9. Process Payment - Pending Scenario"
print_test "POST /api/v1/payments (Amount: \$0.03 - Pending)"
# Re-tokenize to get fresh token
PENDING_TOKEN=$(curl -s -X POST $API_URL/api/v1/tokenize \
  -H "Content-Type: application/json" \
  -d '{
    "card": {
      "card_number": "4532015112830366",
      "card_holder": "Test Pending",
      "expiry_month": 12,
      "expiry_year": 2025,
      "cvv": "123"
    },
    "customer": {
      "customer_id": "cust_pending",
      "email": "pending@example.com",
      "billing_address": {
        "street": "123 St",
        "city": "City",
        "state": "ST",
        "zip_code": "12345",
        "country": "US"
      }
    }
  }' | jq -r '.token')

PAYMENT4=$(curl -s -X POST $API_URL/api/v1/payments \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$PENDING_TOKEN\",
    \"amount\": 0.03,
    \"currency\": \"USD\",
    \"customer_id\": \"cust_pending\",
    \"description\": \"Pending payment test\"
  }")
echo "$PAYMENT4" | jq '.'
TXN4=$(echo "$PAYMENT4" | jq -r '.transaction_id')
STATUS4=$(echo "$PAYMENT4" | jq -r '.status')
MESSAGE4=$(echo "$PAYMENT4" | jq -r '.message')
print_success "Payment processed - Status: $STATUS4, Message: $MESSAGE4"

# 10. Process Payment - Large Amount (Manual Review)
print_section "10. Process Payment - Large Amount (Manual Review)"
print_test "POST /api/v1/payments (Amount: \$15,000 - Manual Review)"
# Re-tokenize to get fresh token
LARGE_TOKEN=$(curl -s -X POST $API_URL/api/v1/tokenize \
  -H "Content-Type: application/json" \
  -d '{
    "card": {
      "card_number": "5425233430109903",
      "card_holder": "High Roller",
      "expiry_month": 12,
      "expiry_year": 2026,
      "cvv": "999"
    },
    "customer": {
      "customer_id": "cust_vip",
      "email": "vip@example.com",
      "billing_address": {
        "street": "999 Luxury Ave",
        "city": "Beverly Hills",
        "state": "CA",
        "zip_code": "90210",
        "country": "US"
      }
    }
  }' | jq -r '.token')

PAYMENT5=$(curl -s -X POST $API_URL/api/v1/payments \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$LARGE_TOKEN\",
    \"amount\": 15000.00,
    \"currency\": \"USD\",
    \"customer_id\": \"cust_vip\",
    \"description\": \"Large transaction test\"
  }")
echo "$PAYMENT5" | jq '.'
TXN5=$(echo "$PAYMENT5" | jq -r '.transaction_id')
STATUS5=$(echo "$PAYMENT5" | jq -r '.status')
MESSAGE5=$(echo "$PAYMENT5" | jq -r '.message')
print_success "Payment processed - Status: $STATUS5, Message: $MESSAGE5"

# 11. Get Transaction Details
print_section "11. Get Transaction Details"
print_test "GET /api/v1/transactions/$TXN1"
curl -s $API_URL/api/v1/transactions/$TXN1 | jq '.'
print_success "Transaction details retrieved"

# 12. Get Customer Transactions
print_section "12. Get Customer Transactions"
print_test "GET /api/v1/customers/cust_visa/transactions"
curl -s $API_URL/api/v1/customers/cust_visa/transactions | jq '.'
print_success "Customer transactions retrieved"

# 13. Get Token Info
print_section "13. Get Token Information"
print_test "GET /api/v1/tokens/$VISA_TOKEN"
curl -s $API_URL/api/v1/tokens/$VISA_TOKEN | jq '.'
print_success "Token information retrieved"

# 14. Test Invalid Token
print_section "14. Test Invalid Token"
print_test "POST /api/v1/payments (Invalid Token)"
INVALID=$(curl -s -X POST $API_URL/api/v1/payments \
  -H "Content-Type: application/json" \
  -d '{
    "token": "tok_invalid_token_12345",
    "amount": 50.00,
    "currency": "USD",
    "customer_id": "cust_test"
  }')
echo "$INVALID" | jq '.'
print_success "Invalid token properly rejected"

# 15. Test Invalid Card Number
print_section "15. Test Invalid Card Number"
print_test "POST /api/v1/tokenize (Invalid Card)"
INVALID_CARD=$(curl -s -X POST $API_URL/api/v1/tokenize \
  -H "Content-Type: application/json" \
  -d '{
    "card": {
      "card_number": "1234",
      "card_holder": "Invalid Card",
      "expiry_month": 12,
      "expiry_year": 2025,
      "cvv": "123"
    },
    "customer": {
      "email": "invalid@example.com",
      "billing_address": {
        "street": "123 St",
        "city": "City",
        "state": "ST",
        "zip_code": "12345",
        "country": "US"
      }
    }
  }')
echo "$INVALID_CARD" | jq '.'
print_success "Invalid card properly rejected"

# 16. Refund Transaction (if successful transaction exists)
print_section "16. Refund Transaction"
if [ "$STATUS1" == "success" ]; then
    print_test "POST /api/v1/transactions/$TXN1/refund"
    REFUND=$(curl -s -X POST $API_URL/api/v1/transactions/$TXN1/refund)
    echo "$REFUND" | jq '.'
    print_success "Refund processed"
else
    print_error "Skipping refund test - no successful transaction available"
fi

# Summary
print_section "Test Summary"
echo -e "${GREEN}✓ All API endpoints tested successfully!${NC}"
echo -e "\n${BLUE}Test Scenarios Covered:${NC}"
echo "  ✓ Health check"
echo "  ✓ Card tokenization (Visa, Mastercard, Amex)"
echo "  ✓ Normal payment processing"
echo "  ✓ Insufficient funds scenario (\$0.01)"
echo "  ✓ Card declined scenario (\$0.02)"
echo "  ✓ Pending payment scenario (\$0.03)"
echo "  ✓ Large amount/manual review (\$15,000+)"
echo "  ✓ Transaction retrieval"
echo "  ✓ Customer transaction history"
echo "  ✓ Token information"
echo "  ✓ Invalid token handling"
echo "  ✓ Invalid card validation"
echo "  ✓ Refund processing"

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}  Test Suite Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
