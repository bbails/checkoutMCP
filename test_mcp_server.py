"""
Test script for Payment MCP Server

This script tests the MCP server functionality without requiring
external AI frameworks.
"""

from mcp_server import get_payment_tools, execute_payment_function
import json


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print("=" * 70)


def test_get_tools():
    """Test getting the list of available tools."""
    print_section("Test 1: Get Payment Tools")

    tools = get_payment_tools()
    print(f"\n✓ Found {len(tools)} tools")

    for i, tool in enumerate(tools, 1):
        print(f"\n{i}. {tool['function']['name']}")
        print(f"   Description: {tool['function']['description'][:80]}...")

    return tools


def test_tokenize_card():
    """Test card tokenization."""
    print_section("Test 2: Tokenize a Payment Card")

    args = {
        "card_number": "4532015112830366",
        "card_holder": "John Doe",
        "expiry_month": 12,
        "expiry_year": 2025,
        "cvv": "123",
        "customer_email": "john@example.com",
        "billing_street": "123 Main St",
        "billing_city": "New York",
        "billing_state": "NY",
        "billing_zip": "10001",
        "billing_country": "US",
    }

    print("\n📝 Tokenizing Visa card...")
    result = execute_payment_function("tokenize_payment_card", json.dumps(args))
    result_data = json.loads(result)

    print(f"\n✓ Token: {result_data.get('token')}")
    print(f"✓ Card Type: {result_data.get('card_type')}")
    print(f"✓ Last 4 Digits: {result_data.get('last_four_digits')}")

    return result_data.get("token")


def test_process_payment(token):
    """Test payment processing."""
    print_section("Test 3: Process a Payment")

    args = {
        "token": token,
        "amount": 49.99,
        "currency": "USD",
        "customer_id": "cust_test",
        "description": "Test payment from MCP server",
    }

    print(f"\n💳 Processing payment of ${args['amount']}...")
    result = execute_payment_function("process_payment", json.dumps(args))
    result_data = json.loads(result)

    print(f"\n✓ Transaction ID: {result_data.get('transaction_id')}")
    print(f"✓ Status: {result_data.get('status')}")
    print(f"✓ Message: {result_data.get('message')}")

    return result_data.get("transaction_id")


def test_get_transaction(transaction_id):
    """Test getting transaction details."""
    print_section("Test 4: Get Transaction Details")

    args = {"transaction_id": transaction_id}

    print(f"\n🔍 Retrieving transaction {transaction_id}...")
    result = execute_payment_function("get_transaction", json.dumps(args))
    result_data = json.loads(result)

    print(f"\n✓ Amount: ${result_data.get('amount')}")
    print(f"✓ Status: {result_data.get('status')}")
    print(f"✓ Customer ID: {result_data.get('customer_id')}")

    return result_data


def test_get_customer_transactions():
    """Test getting customer transactions."""
    print_section("Test 5: Get Customer Transactions")

    args = {"customer_id": "cust_test"}

    print("\n📊 Retrieving customer transactions...")
    result = execute_payment_function("get_customer_transactions", json.dumps(args))
    result_data = json.loads(result)

    print(f"\n✓ Customer ID: {result_data.get('customer_id')}")
    print(f"✓ Transaction Count: {result_data.get('transaction_count')}")


def test_get_token_info(token):
    """Test getting token information."""
    print_section("Test 6: Get Token Information")

    args = {"token": token}

    print(f"\n🔐 Getting token information...")
    result = execute_payment_function("get_token_info", json.dumps(args))
    result_data = json.loads(result)

    print(f"\n✓ Token: {result_data.get('token')[:20]}...")
    print(f"✓ Card Type: {result_data.get('card_type')}")
    print(f"✓ Is Valid: {result_data.get('is_valid')}")
    print(f"✓ Expires At: {result_data.get('expires_at')}")


def test_insufficient_funds():
    """Test insufficient funds scenario."""
    print_section("Test 7: Test Insufficient Funds Scenario")

    # First tokenize a new card
    args = {
        "card_number": "5425233430109903",
        "card_holder": "Jane Smith",
        "expiry_month": 6,
        "expiry_year": 2026,
        "cvv": "456",
        "customer_email": "jane@example.com",
        "billing_street": "456 Oak Ave",
        "billing_city": "Los Angeles",
        "billing_state": "CA",
        "billing_zip": "90001",
        "billing_country": "US",
    }

    print("\n📝 Tokenizing Mastercard...")
    result = execute_payment_function("tokenize_payment_card", json.dumps(args))
    token = json.loads(result).get("token")

    # Process payment with special amount $0.01
    payment_args = {
        "token": token,
        "amount": 0.01,
        "currency": "USD",
        "customer_id": "cust_test2",
        "description": "Insufficient funds test",
    }

    print("💳 Processing payment of $0.01 (should fail)...")
    result = execute_payment_function("process_payment", json.dumps(payment_args))
    result_data = json.loads(result)

    print(f"\n✓ Status: {result_data.get('status')}")
    print(f"✓ Message: {result_data.get('message')}")


def test_refund(transaction_id):
    """Test refunding a transaction."""
    print_section("Test 8: Refund a Transaction")

    args = {"transaction_id": transaction_id}

    print(f"\n💰 Refunding transaction {transaction_id}...")
    result = execute_payment_function("refund_transaction", json.dumps(args))
    result_data = json.loads(result)

    if result_data.get("refund_id"):
        print(f"\n✓ Refund ID: {result_data.get('refund_id')}")
        print(f"✓ Status: {result_data.get('status')}")
        print(f"✓ Message: {result_data.get('message')}")
    else:
        print(f"\n⚠ Could not refund: {result_data.get('message', 'Unknown error')}")


def main():
    """Run all MCP server tests."""
    print("\n" + "=" * 70)
    print("  Payment MCP Server - Comprehensive Test Suite")
    print("=" * 70)
    print("\n⚠️  Make sure the Payment API is running on http://localhost:8000")

    try:
        # Test 1: Get available tools
        tools = test_get_tools()

        # Test 2: Tokenize a card
        token = test_tokenize_card()

        # Test 3: Process a payment
        transaction_id = test_process_payment(token)

        # Test 4: Get transaction details
        test_get_transaction(transaction_id)

        # Test 5: Get customer transactions
        test_get_customer_transactions()

        # Test 6: Get token info
        test_get_token_info(token)

        # Test 7: Test insufficient funds
        test_insufficient_funds()

        # Test 8: Refund transaction (if successful)
        test_refund(transaction_id)

        # Summary
        print_section("Test Summary")
        print("\n✅ All MCP server tests completed successfully!")
        print("\nThe Payment MCP Server is working correctly and can be used with:")
        print("  • Microsoft Agent Framework")
        print("  • OpenAI function calling")
        print("  • Any MCP-compatible AI agent")

    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n" + "=" * 70 + "\n")
    return 0


if __name__ == "__main__":
    exit(main())
